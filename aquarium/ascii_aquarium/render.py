"""Render the ocean as a self-contained animated SVG (CSS animations only).

GitHub sanitises README HTML (no CSS, no JS), but an SVG loaded through <img>
keeps its internal <style> and @keyframes, so the scene animates on profile pages.

Each animal is a group that crosses the scene (one @keyframes per animal). Inside it,
the swim cycle is a stack of ASCII frames shown one at a time (frame k is visible
during the k-th slice of the cycle), so the wings flap and the tails sway.
"""
from __future__ import annotations

import datetime as dt
from html import escape

from .scene import CHAR_W, LINE_H, Config, Fish, rand

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
DEEP_TOP, DEEP_BOTTOM = "#2b3743", "#1b232c"   # deep blue, almost grey
RIPPLE, PLANKTON, UI = "#9fb3c6", "#c3cfdb", "#93a6b8"


def _num(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".")


def _frame_keyframes(n: int) -> str:
    on = 100 / n
    return (f"@keyframes fr{n}{{0%,{_num(on)}%{{opacity:1}}"
            f"{_num(on + 0.01)}%,100%{{opacity:0}}}}")


def _sprite(lines: list[str], fs: float) -> str:
    spans = "".join(
        f'<tspan x="0" y="{_num((k + 0.85) * LINE_H * fs)}">{escape(line.rstrip())}</tspan>'
        for k, line in enumerate(lines) if line.strip())
    return f'<text font-size="{_num(fs)}">{spans}</text>'


def _fish_svg(i: int, f: Fish, cfg: Config) -> tuple[str, str, str]:
    """Return (gradient def, keyframes, element) for one animal."""
    w, h = f.width, f.height
    # Head-first colour bands: on a right-facing animal the head is at x = w.
    stops = []
    for start, end, color in f.stripes:
        a, b = (1 - end, 1 - start) if f.facing_right else (start, end)
        stops.append((a, b, color))
    stops.sort()
    grad = [f'<linearGradient id="g{i}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{_num(w)}" y2="0">']
    for a, b, color in stops:
        grad.append(f'<stop offset="{_num(a)}" stop-color="{color}"/><stop offset="{_num(b)}" stop-color="{color}"/>')
    grad.append("</linearGradient>")

    start_x, end_x = (-w - 60, cfg.width + 60) if f.facing_right else (cfg.width + 60, -w - 60)
    keyframes = (f"@keyframes s{i}{{from{{transform:translate({_num(start_x)}px,{_num(f.y0)}px)}}"
                 f"to{{transform:translate({_num(end_x)}px,{_num(f.y1)}px)}}}}")

    n, period = len(f.frames), f.spec.period
    frames = "".join(
        f'<g class="fr{" fr0" if k == 0 else ""}" style="animation-name:fr{n};'
        f'animation-duration:{_num(period)}s;animation-delay:{_num(k * period / n - period)}s">'
        f'{_sprite(fr, f.font_size)}</g>'
        for k, fr in enumerate(f.frames))
    label = ""
    if cfg.show_labels:
        star = f.repo.name.lower() in {x.lower() for x in cfg.highlight}
        label = (f'<text class="{"lbl hi" if star else "lbl"}" x="{_num(w / 2)}" y="{_num(h + 9)}" '
                 f'text-anchor="middle">{"★ " if star else ""}{escape(f.repo.name)}</text>')
    langs = ", ".join(f"{k} {v / max(f.repo.code_bytes, 1):.0%}"
                      for k, v in sorted(f.repo.languages.items(), key=lambda kv: -kv[1])[:4])
    el = (f'<g class="f" style="animation-name:s{i};animation-duration:{_num(f.duration)}s;'
          f'animation-delay:{_num(f.delay)}s" transform="translate({_num(f.rest_x)},{_num(f.y0)})">'
          f'<title>{escape(f.repo.name)} · {escape(f.species)} · {escape(langs)}</title>'
          f'<g class="bob" style="animation-duration:{_num(f.bob_duration)}s">'
          f'<g transform="rotate({_num(f.angle)} {_num(w / 2)} {_num(h / 2)})">'
          f'<g fill="url(#g{i})">{frames}</g></g>{label}</g></g>')
    return "".join(grad), keyframes, el


def _ripples(cfg: Config) -> str:
    """Light rippling on the surface: sparse '~' marks that drift and fade."""
    out = []
    for k in range(34):
        x = rand(cfg.seed, "rip", k) * cfg.width
        y = 30 + rand(cfg.seed, "ripy", k) * (cfg.height - 50)
        glyph = ["~", "~ ~", "~~", " ~  ~", "~ ~~"][int(rand(cfg.seed, "ripg", k) * 5)]
        dur = 7 + 7 * rand(cfg.seed, "ripd", k)
        out.append(f'<text class="rip" x="{_num(x)}" y="{_num(y)}" style="animation-duration:{_num(dur)}s;'
                   f'animation-delay:-{_num(dur * rand(cfg.seed, "ripp", k))}s">{glyph}</text>')
    return f'<g fill="{RIPPLE}" font-size="11">{"".join(out)}</g>'


def _plankton(cfg: Config) -> str:
    out = []
    for k in range(40):
        x = rand(cfg.seed, "pl", k) * cfg.width
        y = rand(cfg.seed, "ply", k) * cfg.height
        glyph = ".,·'"[int(rand(cfg.seed, "plg", k) * 4)]
        dur = 16 + 18 * rand(cfg.seed, "pld", k)
        out.append(f'<text class="pl" x="{_num(x)}" y="{_num(y)}" style="animation-duration:{_num(dur)}s;'
                   f'animation-delay:-{_num(dur * rand(cfg.seed, "plp", k))}s">{glyph}</text>')
    return f'<g fill="{PLANKTON}" font-size="9">{"".join(out)}</g>'


def render(fish: list[Fish], cfg: Config, today: dt.date | None = None) -> str:
    W, H = cfg.width, cfg.height
    today = today or dt.date.today()
    defs, keyframes, bodies = [], [], []
    for i, f in enumerate(fish):
        d, k, b = _fish_svg(i, f, cfg)
        defs.append(d)
        keyframes.append(k)
        bodies.append(b)
    frame_kf = "".join(_frame_keyframes(n) for n in sorted({len(f.frames) for f in fish}))
    title = escape(cfg.title or f"~/{cfg.user}/ocean $ ls repos | swim")
    legend = "1 animal = 1 repo · species = languages · colours = language mix · size = code size"

    style = f"""
text{{font-family:{FONT};white-space:pre}}
.f{{animation-timing-function:linear;animation-iteration-count:infinite}}
.fr{{opacity:0;animation-timing-function:linear;animation-iteration-count:infinite}}
.bob{{animation:bob 4s ease-in-out infinite}}
.lbl{{font-size:9px;fill:#d3dde6;opacity:.45}}
.hi{{fill:#f2d58c;opacity:.95;font-weight:bold}}
.rip{{opacity:0;animation:rip 10s ease-in-out infinite}}
.pl{{opacity:.35;animation:pl 20s linear infinite}}
@keyframes bob{{0%,100%{{transform:translateY(-2px)}}50%{{transform:translateY(2px)}}}}
@keyframes rip{{0%,100%{{opacity:0;transform:translateX(0)}}50%{{opacity:.13;transform:translateX(14px)}}}}
@keyframes pl{{0%{{transform:translate(0,0)}}50%{{transform:translate(9px,-6px)}}100%{{transform:translate(0,0)}}}}
{frame_kf}
{"".join(keyframes)}
@media (prefers-reduced-motion:reduce){{.f,.fr,.bob,.rip,.pl{{animation:none}}.fr0{{opacity:1}}}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" xml:space="preserve" role="img" aria-label="ASCII ocean: each animal is one of {escape(cfg.user)}'s GitHub repositories">
<title>{escape(cfg.user)}'s repository ocean</title>
<defs>
<linearGradient id="deep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{DEEP_TOP}"/><stop offset="1" stop-color="{DEEP_BOTTOM}"/></linearGradient>
<radialGradient id="vignette" cx=".5" cy=".45" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></radialGradient>
<clipPath id="tank"><rect width="{W}" height="{H}" rx="10"/></clipPath>
{"".join(defs)}
</defs>
<style>{style}</style>
<g clip-path="url(#tank)">
<rect width="{W}" height="{H}" fill="url(#deep)"/>
{_plankton(cfg)}
{_ripples(cfg)}
{"".join(bodies)}
<rect width="{W}" height="{H}" fill="url(#vignette)"/>
</g>
<g font-size="12" fill="{UI}"><text x="14" y="22">{title}</text>
<text x="{W - 14}" y="22" text-anchor="end" opacity=".75" font-size="10">{escape(legend)}</text>
<text x="{W - 14}" y="{H - 8}" text-anchor="end" opacity=".6" font-size="9">{len(fish)} repos · fed {today.isoformat()}</text></g>
</svg>
"""
