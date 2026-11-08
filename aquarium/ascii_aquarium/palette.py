"""Language colours (GitHub linguist values), brightened to read on dark water."""
from __future__ import annotations

LINGUIST: dict[str, str] = {
    "Python": "#3572A5",
    "Jupyter Notebook": "#DA5B0B",
    "TypeScript": "#3178C6",
    "JavaScript": "#F1E05A",
    "HTML": "#E34C26",
    "CSS": "#663399",
    "SCSS": "#C6538C",
    "Vue": "#41B883",
    "Shell": "#89E051",
    "PowerShell": "#012456",
    "Batchfile": "#C1F12E",
    "Makefile": "#427819",
    "Dockerfile": "#384D54",
    "HCL": "#844FBA",
    "C": "#555555",
    "C++": "#F34B7D",
    "Rust": "#DEA584",
    "Go": "#00ADD8",
    "Java": "#B07219",
    "SQL": "#E38C00",
    "PLpgSQL": "#336790",
    "R": "#198CE7",
    "Julia": "#A270BA",
    "TeX": "#3D6117",
    "Cython": "#FEDF5B",
    "MQL5": "#4A76B8",
    "MQL4": "#62A8D6",
}
DEFAULT = "#9CCFD8"


def _rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def _hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(max(0.0, min(1.0, c)) * 255):02x}" for c in rgb)


def luminance(hex_color: str) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in _rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def readable(hex_color: str, min_luminance: float = 0.28) -> str:
    """Mix a colour towards white until it stands out on a dark-blue background."""
    rgb = _rgb(hex_color)
    for _ in range(20):
        if luminance(_hex(rgb)) >= min_luminance:
            break
        rgb = tuple(c + (1 - c) * 0.12 for c in rgb)  # type: ignore[assignment]
    return _hex(rgb)


def language_color(language: str) -> str:
    return readable(LINGUIST.get(language, DEFAULT))
