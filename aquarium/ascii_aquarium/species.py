"""Species catalogue: which silhouette, how it swims, and which languages it stands for.

Silhouettes come from assets/silhouettes.png (top-down view) and are extracted by
tools/extract_silhouettes.py into silhouettes.txt.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Species:
    masks: tuple[str, ...]   # silhouette variants (picked per repo)
    motion: str              # "flap", "sway" or "paddle" (see sprite.MOTIONS)
    period: float            # seconds per swim cycle (wing beat, tail beat...)
    texture: str             # interior fill; "row1|row2" for a 2-D pattern
    speed: float             # crossing speed multiplier
    length: float            # sprite length multiplier (rays have a long tail)


SPECIES: dict[str, Species] = {
    "ray": Species(("ray1", "ray2", "ray3"), "flap", 2.6, ":", 0.85, 1.35),
    "hammerhead": Species(("hammerhead",), "sway", 1.8, "=", 1.0, 1.15),
    "shark": Species(("shark",), "sway", 1.4, "#", 1.2, 1.0),
    "turtle": Species(("turtle",), "paddle", 3.4, r"\_/ |/ \_", 0.55, 0.85),
}

# Combination rules, checked in order before the main-language table.
# Each rule: every group must be present with at least `min_share` of the code;
# a group is "A|B" = A or B.
DEFAULT_COMBOS: list[dict] = [
    {"all": ["Python", "JavaScript|TypeScript"], "species": "hammerhead", "min_share": 0.10},
    {"all": ["Python", "Dockerfile"], "species": "hammerhead", "min_share": 0.0},
]

# Primary GitHub language -> species. Unknown languages become turtles.
DEFAULT_LANGUAGE_SPECIES: dict[str, str] = {
    "Python": "ray",
    "R": "ray",
    "Julia": "ray",
    "Jupyter Notebook": "turtle",
    "TypeScript": "shark",
    "JavaScript": "shark",
    "C": "shark",
    "C++": "shark",
    "Rust": "shark",
    "Go": "shark",
    "Java": "shark",
    "Dockerfile": "hammerhead",
    "HCL": "hammerhead",
    "Shell": "hammerhead",
}
FALLBACK_SPECIES = "turtle"

_MIRROR = str.maketrans({
    "(": ")", ")": "(", "<": ">", ">": "<", "/": "\\", "\\": "/",
    "[": "]", "]": "[", "{": "}", "}": "{", "`": "'", "'": "`",
})


def mirror(lines: list[str]) -> list[str]:
    """Flip a right-facing sprite so it faces left (keeps the bounding box)."""
    width = max((len(line) for line in lines), default=0)
    return [line.ljust(width)[::-1].translate(_MIRROR) for line in lines]
