"""Render the aquarium as a self-contained animated SVG (CSS animations only).

GitHub sanitises README HTML (no CSS, no JS), but an SVG loaded through <img>
keeps its internal <style> and @keyframes, so the tank animates on profile pages.
"""
from __future__ import annotations

import datetime as dt
from html import escape

from .scene import CHAR_W, LINE_H, SAND_H, Config, Fish, rand

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
WATER_TOP, WATER_BOTTOM = "#0e3a5c", "#061526"
WEED, SAND, UI = "#3fae78", "#c9b37e", "#8fb8d0"


def _num(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".")


def _fish_svg(i: int, f: Fish, cfg: Config) -> tuple[str, str, str]:
    """Return (gradient def, keyframes, element) for one fish."""
    w = f.width
    # Head-first stripes: on a right-facing fish the head is at x = w.
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
    y = _num(f.y)
    keyframes = (f"@keyframes s{i}{{from{{transform:translate({_num(start_x)}px,{y}px)}}"
                 f"to{{transform:translate({_num(end_x)}px,{y}px)}}}}")

    fs = f.font_size
    lines = "".join(
        f'<text y="{_num((k + 0.85) * LINE_H * fs)}" font-size="{_num(fs)}">{escape(line)}</text>'
        for k, line in enumerate(f.lines))
    label = ""
    if cfg.show_labels:
        star = f.repo.name.lower() in {h.lower() for h in cfg.highlight}
        label = (f'<text class="{"lbl hi" if star else "lbl"}" x="{_num(w / 2)}" y="{_num(f.height + 11)}" '
                 f'text-anchor="middle">{"★ " if star else ""}{escape(f.repo.name)}</text>')
    bob = "bobs" if f.species == "jellyfish" else "bob"
    langs = ", ".join(f"{k} {v / max(f.repo.code_bytes, 1):.0%}"
                      for k, v in sorted(f.repo.languages.items(), key=lambda kv: -kv[1])[:4])
    el = (f'<g class="f" style="animation-name:s{i};animation-duration:{_num(f.duration)}s;'
          f'animation-delay:{_num(f.delay)}s" transform="translate({_num(f.rest_x)},{y})">'
          f'<title>{escape(f.repo.name)} · {escape(f.species)} · {langs}</title>'
          f'<g class="{bob}" style="animation-duration:{_num(f.bob_duration)}s">'
          f'<g fill="url(#g{i})">{lines}</g>{label}</g></g>')
    return "".join(grad), keyframes, el


def _seaweed(cfg: Config) -> str:
    sand_top = cfg.height - SAND_H
    out = []
    n = max(4, cfg.width // 130)
    for k in range(n):
        x = (k + 0.3 + 0.4 * rand(cfg.seed, "weed", k)) * cfg.width / n
        height = 4 + int(6 * rand(cfg.seed, "weedh", k))
        fs = 14
        lines = "".join(
            f'<text x="{_num(x + (4 if j % 2 else 0))}" y="{_num(sand_top + 10 - (height - j) * fs * 0.95)}">'
            f'{")" if j % 2 else "("}</text>'
            for j in range(height))
        dur = 3.5 + 2 * rand(cfg.seed, "weeds", k)
        out.append(f'<g class="weed" style="animation-duration:{_num(dur)}s;'
                   f'animation-delay:-{_num(dur * rand(cfg.seed, "weedd", k))}s">{lines}</g>')
    return f'<g fill="{WEED}" font-size="14" opacity=".75">{"".join(out)}</g>'


def _bubbles(cfg: Config) -> tuple[str, str]:
    rise = cfg.height - SAND_H - 20
    kf = (f"@keyframes rise{{0%{{transform:translateY(0);opacity:0}}10%{{opacity:.75}}"
          f"85%{{opacity:.5}}100%{{transform:translateY(-{rise}px);opacity:0}}}}")
    out = []
    for k in range(22):
        x = rand(cfg.seed, "bub", k) * cfg.width
        glyph = "oO.°o"[int(rand(cfg.seed, "bubg", k) * 5)]
        dur = 6 + 8 * rand(cfg.seed, "bubd", k)
        delay = dur * rand(cfg.seed, "bubp", k)
        out.append(f'<text class="bub" x="{_num(x)}" y="{cfg.height - SAND_H}" '
                   f'style="animation-duration:{_num(dur)}s;animation-delay:-{_num(delay)}s">{glyph}</text>')
    return kf, f'<g fill="#cfe8f5" font-size="11">{"".join(out)}</g>'


def _sand(cfg: Config) -> str:
    sand_top = cfg.height - SAND_H
    cols = int(cfg.width / (CHAR_W * 11)) + 2
    rows = []
    for r in range(3):
        chars = "".join(" .,:'`_~."[int(rand(cfg.seed, "sand", r, c) * 9)] for c in range(cols))
        rows.append(f'<text x="0" y="{sand_top + 16 + r * 12}">{escape(chars)}</text>')
    return (f'<rect y="{sand_top}" width="{cfg.width}" height="{SAND_H}" fill="url(#sandg)"/>'
            f'<g fill="{SAND}" font-size="11" opacity=".35">{"".join(rows)}</g>')


def _rays(cfg: Config) -> str:
    out = []
    for k in range(4):
        x = (k + 0.2 + 0.6 * rand(cfg.seed, "ray", k)) * cfg.width / 4
        w = 40 + 50 * rand(cfg.seed, "rayw", k)
        bottom = cfg.height - SAND_H
        out.append(f'<polygon class="ray" style="animation-delay:-{k * 2}s" '
                   f'points="{_num(x)},0 {_num(x + w)},0 {_num(x + w * 2.2 - 60)},{bottom} {_num(x + w * 1.2 - 60)},{bottom}"/>')
    return f'<g fill="#bfe6ff">{"".join(out)}</g>'


def render(fish: list[Fish], cfg: Config, today: dt.date | None = None) -> str:
    W, H = cfg.width, cfg.height
    today = today or dt.date.today()
    defs, keyframes, bodies = [], [], []
    for i, f in enumerate(fish):
        d, k, b = _fish_svg(i, f, cfg)
        defs.append(d)
        keyframes.append(k)
        bodies.append(b)
    bub_kf, bubbles = _bubbles(cfg)
    title = escape(cfg.title or f"~/{cfg.user}/aquarium $ ls repos | swim")
    legend = "1 fish = 1 repo · species = main language · colours = language mix · size = code size"

    style = f"""
text{{font-family:{FONT};white-space:pre}}
.f{{animation-timing-function:linear;animation-iteration-count:infinite}}
.bob,.bobs{{animation-name:bob;animation-timing-function:ease-in-out;animation-iteration-count:infinite}}
.bobs{{animation-name:bobs}}
.lbl{{font-size:10px;fill:#d7ecf7;opacity:.5}}
.hi{{fill:#ffe08a;opacity:.95;font-weight:bold}}
.bub{{animation-name:rise;animation-timing-function:linear;animation-iteration-count:infinite;opacity:0}}
.weed{{transform-box:fill-box;transform-origin:50% 100%;animation:sway 4s ease-in-out infinite alternate}}
.ray{{opacity:.05;animation:ray 7s ease-in-out infinite alternate}}
@keyframes bob{{0%,100%{{transform:translateY(-3px)}}50%{{transform:translateY(3px)}}}}
@keyframes bobs{{0%,100%{{transform:translateY(-10px)}}50%{{transform:translateY(10px)}}}}
@keyframes sway{{from{{transform:skewX(-9deg)}}to{{transform:skewX(9deg)}}}}
@keyframes ray{{from{{opacity:.02}}to{{opacity:.08}}}}
{bub_kf}
{"".join(keyframes)}
@media (prefers-reduced-motion:reduce){{.f,.bob,.bobs,.bub,.weed,.ray{{animation:none}}.bub{{opacity:.4}}}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" xml:space="preserve" role="img" aria-label="ASCII aquarium: each fish is one of {escape(cfg.user)}'s GitHub repositories">
<title>{escape(cfg.user)}'s repository aquarium</title>
<defs>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WATER_TOP}"/><stop offset="1" stop-color="{WATER_BOTTOM}"/></linearGradient>
<linearGradient id="sandg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a3322"/><stop offset="1" stop-color="#1c1810"/></linearGradient>
<clipPath id="tank"><rect width="{W}" height="{H}" rx="10"/></clipPath>
{"".join(defs)}
</defs>
<style>{style}</style>
<g clip-path="url(#tank)">
<rect width="{W}" height="{H}" fill="url(#water)"/>
{_rays(cfg)}
{_seaweed(cfg)}
{"".join(bodies)}
{bubbles}
{_sand(cfg)}
</g>
<g font-size="12" fill="{UI}"><text x="14" y="22">{title}</text>
<text x="{W - 14}" y="22" text-anchor="end" opacity=".75" font-size="10">{escape(legend)}</text>
<text x="{W - 14}" y="{H - 8}" text-anchor="end" opacity=".6" font-size="9">{len(fish)} repos · fed {today.isoformat()}</text></g>
</svg>
"""
