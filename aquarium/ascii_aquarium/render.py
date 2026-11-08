"""Render the ocean as a self-contained animated SVG (CSS animations only), and an HTML page.

* The SVG works as a README image: GitHub keeps the SVG's own <style> and @keyframes when it
  is shown through <img>. Images are not interactive there, so it shows no text at all.
* The same SVG inlined in a web page (GitHub Pages) becomes interactive: hovering an animal
  pauses it and shows the project name, clicking opens the repository.

Each animal crosses the scene (one @keyframes per animal). Inside it, the swim cycle is a
stack of ASCII frames that cross-fade into each other, so wings and tails move smoothly.
"""
from __future__ import annotations

from html import escape

from .scene import CHAR_W, LINE_H, Config, Fish, rand

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"
DEEP_CENTRE, DEEP_EDGE = "#33414f", "#1a222b"   # deep blue, almost grey
LIGHT = "#a9c8e2"
SHADOW = "#06090d"


def _num(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".")


def _frame_keyframes(n: int, fade: float = 0.25) -> str:
    """Frame k is fully visible during its own slice and cross-fades with its neighbours."""
    slot = 100 / n
    return (f"@keyframes fr{n}{{0%{{opacity:0}}{_num(slot * fade)}%,{_num(slot)}%{{opacity:1}}"
            f"{_num(slot * (1 + fade))}%,100%{{opacity:0}}}}")


def _sprite(lines: list[str], fs: float) -> str:
    spans = "".join(
        f'<tspan x="0" y="{_num((k + 0.85) * LINE_H * fs)}">{escape(line.rstrip())}</tspan>'
        for k, line in enumerate(lines) if line.strip())
    return f'<text font-size="{_num(fs)}">{spans}</text>'


def _fish_svg(i: int, f: Fish, cfg: Config) -> tuple[str, str]:
    """Return (keyframes, element) for one animal."""
    w, h = f.width, f.height
    # One keyframe per path sample. The rotation pivots on the centre of the body:
    # translate(centre) rotate(heading) translate(-half size).
    steps = "".join(
        f"{_num(pct)}%{{transform:translate({_num(x + w / 2)}px,{_num(y + h / 2)}px) "
        f"rotate({_num(a)}deg) translate({_num(-w / 2)}px,{_num(-h / 2)}px)}}"
        for pct, x, y, a in f.path)
    keyframes = f"@keyframes s{i}{{{steps}}}"

    n, period = len(f.frames), f.spec.period
    frames = "".join(
        f'<g class="fr{" fr0" if k == 0 else ""}" style="animation-name:fr{n};'
        f'animation-duration:{_num(period)}s;animation-delay:{_num(k * period / n - period)}s">'
        f'{_sprite(fr, f.font_size)}</g>'
        for k, fr in enumerate(f.frames))
    # Shadow on the sea floor: the first frame, blurred and offset (blur hides the motion).
    depth = 8 + 10 * min(1.0, w / 300)
    shadow = (f'<g class="sh" transform="translate({_num(depth)},{_num(depth * 1.6)})" '
              f'filter="url(#soft)">{_sprite(f.frames[0], f.font_size)}</g>')

    name = escape(f.repo.name)
    pill_w = len(f.repo.name) * CHAR_W * 11 + 16
    label = (f'<g class="lbl" transform="translate({_num(w / 2 - pill_w / 2)},{_num(-22)})">'
             f'<rect width="{_num(pill_w)}" height="18" rx="9"/>'
             f'<text x="{_num(pill_w / 2)}" y="12.5" text-anchor="middle">{name}</text></g>')
    el = (f'<a href="{escape(f.repo.url or "#")}" target="_top">'
          f'<g class="f" style="animation-name:s{i};animation-duration:{_num(f.duration)}s;'
          f'animation-delay:{_num(f.delay)}s" transform="translate({_num(f.rest_x)},{_num(f.y0)})">'
          f'<title>{name}</title>'
          f'<g class="bob" style="animation-duration:{_num(f.bob_duration)}s">'
          f'{shadow}<g class="body">{frames}</g>'
          f'<rect class="hit" width="{_num(w)}" height="{_num(h)}"/>{label}</g></g></a>')
    return keyframes, el


def _light(cfg: Config) -> str:
    """Soft patches of surface light drifting over the scene."""
    out = []
    for k in range(7):
        cx = rand(cfg.seed, "lx", k) * cfg.width
        cy = rand(cfg.seed, "ly", k) * cfg.height
        rx = 140 + 160 * rand(cfg.seed, "lr", k)
        dur = 18 + 14 * rand(cfg.seed, "ld", k)
        out.append(f'<ellipse class="lp" cx="{_num(cx)}" cy="{_num(cy)}" rx="{_num(rx)}" ry="{_num(rx * 0.6)}" '
                   f'style="animation-duration:{_num(dur)}s;animation-delay:-{_num(dur * rand(cfg.seed, "lp", k))}s"/>')
    return f'<g fill="url(#glow)">{"".join(out)}</g>'


def _schools(cfg: Config) -> tuple[str, str]:
    """Distant schools of tiny fish, deep and dim, for depth."""
    kf, out = [], []
    for k in range(4):
        right = rand(cfg.seed, "sd", k) < 0.5
        y = 40 + rand(cfg.seed, "sy", k) * (cfg.height - 120)
        a, b = (-160, cfg.width + 40) if right else (cfg.width + 40, -160)
        dur = 70 + 50 * rand(cfg.seed, "sv", k)
        kf.append(f"@keyframes sc{k}{{from{{transform:translate({a}px,{_num(y)}px)}}"
                  f"to{{transform:translate({b}px,{_num(y + 30)}px)}}}}")
        glyph = ">" if right else "<"
        members = "".join(
            f'<text x="{_num(rand(cfg.seed, "mx", k, j) * 110)}" y="{_num(rand(cfg.seed, "my", k, j) * 50)}" '
            f'class="m" style="animation-delay:-{_num(3 * rand(cfg.seed, "mw", k, j))}s">{glyph}</text>'
            for j in range(9 + int(7 * rand(cfg.seed, "sn", k))))
        out.append(f'<g class="sc" style="animation-name:sc{k};animation-duration:{_num(dur)}s;'
                   f'animation-delay:-{_num(dur * rand(cfg.seed, "sp", k))}s">{members}</g>')
    return "".join(kf), f'<g fill="{cfg.fish_color}" font-size="8" opacity=".22">{"".join(out)}</g>'


def _plankton(cfg: Config) -> str:
    out = []
    for k in range(60):
        x = rand(cfg.seed, "pl", k) * cfg.width
        y = rand(cfg.seed, "ply", k) * cfg.height
        r = 0.5 + 1.1 * rand(cfg.seed, "plr", k)
        dur = 16 + 18 * rand(cfg.seed, "pld", k)
        out.append(f'<circle class="pl" cx="{_num(x)}" cy="{_num(y)}" r="{_num(r)}" style="animation-duration:'
                   f'{_num(dur)}s;animation-delay:-{_num(dur * rand(cfg.seed, "plp", k))}s"/>')
    return f'<g fill="#d6e2ec">{"".join(out)}</g>'


def render(fish: list[Fish], cfg: Config, fade_edges: bool = True, page: bool = False) -> str:
    """The animated SVG. fade_edges blends it into the README page instead of a framed box."""
    W, H = cfg.width, cfg.height
    keyframes, bodies = [], []
    for i, f in enumerate(fish):
        k, b = _fish_svg(i, f, cfg)
        keyframes.append(k)
        bodies.append(b)
    frame_kf = "".join(_frame_keyframes(n) for n in sorted({len(f.frames) for f in fish}))
    school_kf, schools = _schools(cfg)

    style = f"""
text{{font-family:{FONT};white-space:pre}}
.f{{animation-timing-function:linear;animation-iteration-count:infinite;cursor:pointer}}
.f:hover{{animation-play-state:paused}}
.fr{{opacity:0;animation-timing-function:linear;animation-iteration-count:infinite}}
.body{{fill:{cfg.fish_color}}}
.sh{{fill:{SHADOW};opacity:.55}}
.hit{{fill:none;pointer-events:all}}
.lbl{{opacity:0;transition:opacity .25s;pointer-events:none}}
.lbl rect{{fill:#0f151c;fill-opacity:.85;stroke:{cfg.fish_color};stroke-opacity:.35}}
.lbl text{{fill:#e8eff5;font-size:11px}}
.f:hover .lbl{{opacity:1}}
.f:hover .body{{fill:#ffffff}}
.bob{{animation:bob 4s ease-in-out infinite}}
.lp{{opacity:.08;animation:lp 24s ease-in-out infinite alternate}}
.pl{{opacity:.28;animation:pl 20s ease-in-out infinite}}
.sc{{animation-timing-function:linear;animation-iteration-count:infinite}}
.m{{animation:m 3s ease-in-out infinite}}
@keyframes bob{{0%,100%{{transform:translateY(-2px)}}50%{{transform:translateY(2px)}}}}
@keyframes lp{{from{{transform:translate(-30px,-10px);opacity:.04}}to{{transform:translate(40px,20px);opacity:.11}}}}
@keyframes pl{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(10px,-7px)}}}}
@keyframes m{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(3px,2px)}}}}
{frame_kf}
{school_kf}
{"".join(keyframes)}
@media (prefers-reduced-motion:reduce){{.f,.fr,.bob,.lp,.pl,.sc,.m{{animation:none}}.fr0{{opacity:1}}}}
"""
    fade_defs = fade_open = fade_close = ""
    if fade_edges:
        fade_defs = """
<linearGradient id="fv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/><stop offset=".14" stop-color="#fff"/><stop offset=".86" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
<linearGradient id="fh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000"/><stop offset=".06" stop-color="#fff"/><stop offset=".94" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>"""
        fade_defs += (f'<mask id="mv"><rect width="{W}" height="{H}" fill="url(#fv)"/></mask>'
                      f'<mask id="mh"><rect width="{W}" height="{H}" fill="url(#fh)"/></mask>')
        fade_open, fade_close = '<g mask="url(#mh)"><g mask="url(#mv)">', "</g></g>"
    aspect = ' preserveAspectRatio="xMidYMid slice"' if page else ""
    size = 'width="100%" height="100%"' if page else f'width="{W}" height="{H}"'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" {size}{aspect} xml:space="preserve" role="img" aria-label="Animated ASCII ocean: each animal is one of {escape(cfg.user)}'s GitHub repositories">
<defs>
<radialGradient id="deep" cx=".5" cy=".4" r=".8"><stop offset="0" stop-color="{DEEP_CENTRE}"/><stop offset="1" stop-color="{DEEP_EDGE}"/></radialGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{LIGHT}"/><stop offset="1" stop-color="{LIGHT}" stop-opacity="0"/></radialGradient>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3.5"/></filter>{fade_defs}
</defs>
<style>{style}</style>
{fade_open}
<rect width="{W}" height="{H}" fill="url(#deep)"/>
{_plankton(cfg)}
{schools}
{_light(cfg)}
{"".join(bodies)}
{fade_close}
</svg>
"""


def render_page(fish: list[Fish], cfg: Config) -> str:
    """Full-screen interactive page: the ocean as a real background, the presentation on top."""
    svg = render(fish, cfg, fade_edges=False, page=True)
    title = escape(cfg.page_title or f"{cfg.user} · ocean")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
:root{{color-scheme:dark}}
html,body{{margin:0;height:100%;background:{DEEP_EDGE};color:#e6edf3;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}}
#ocean{{position:fixed;inset:0;z-index:0}}
main{{position:relative;z-index:1;min-height:100%;display:flex;align-items:center;justify-content:center;
  padding:16px;box-sizing:border-box;pointer-events:none}}
.card{{pointer-events:auto;max-width:640px;padding:28px 32px;border-radius:16px;line-height:1.55;
  background:rgba(16,22,29,.62);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);
  border:1px solid rgba(207,219,230,.14);box-shadow:0 20px 60px rgba(0,0,0,.35)}}
.card h1{{margin:0 0 4px;font-size:1.7rem}}
.card a{{color:#9ecbff}}
.card p{{margin:.6em 0}}
</style>
</head>
<body>
<div id="ocean">{svg}</div>
<main><div class="card">{cfg.page_html}</div></main>
</body>
</html>
"""
