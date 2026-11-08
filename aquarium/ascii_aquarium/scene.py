"""Turn repositories into animals: species, size, colours, path and speed."""
from __future__ import annotations

import hashlib
import math
import tomllib
from dataclasses import dataclass, field

from .github import Repo
from .species import (DEFAULT_COMBOS, DEFAULT_LANGUAGE_SPECIES, FALLBACK_SPECIES, SPECIES,
                      Species, mirror)
from .sprite import frames as make_frames

CHAR_W = 0.6     # monospace glyph width, in em
LINE_H = 1.12    # line height, in em
TOP_MARGIN = 10
BOTTOM_MARGIN = 10


@dataclass
class Config:
    user: str
    exclude: list[str] = field(default_factory=list)
    include_forks: bool = False
    include_archived: bool = True
    max_fish: int = 18
    width: int = 1000
    height: int = 560
    font_size: float = 6.0       # px per character: smaller = finer drawings
    min_cols: int = 22           # sprite length (characters) of the smallest repo...
    max_cols: int = 58           # ...and of the largest
    frames: int = 12             # animation frames per swim cycle (cross-faded)
    fish_color: str = "#cfdbe6"  # one colour for every animal
    species: dict[str, str] = field(default_factory=dict)  # language -> species overrides
    # Bytes of these languages count less for size (notebooks embed outputs/images).
    size_weights: dict[str, float] = field(default_factory=lambda: {"Jupyter Notebook": 0.25})
    combos: list[dict] | None = None  # None -> DEFAULT_COMBOS; [] disables combination rules
    seed: str = "aquarium"
    # Interactive page (GitHub Pages): presentation shown over the ocean.
    page_title: str = ""
    page_html: str = ""          # HTML fragment placed over the background

    @classmethod
    def load(cls, path: str) -> "Config":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)

    def size_bytes(self, repo: Repo) -> int:
        return int(sum(n * self.size_weights.get(lang, 1.0) for lang, n in repo.languages.items()))

    def species_for(self, repo: Repo) -> str:
        """Combination rules first, then the main language, then the fallback."""
        total = repo.code_bytes or 1
        share = {lang: n / total for lang, n in repo.languages.items()}
        for rule in DEFAULT_COMBOS if self.combos is None else self.combos:
            floor = rule.get("min_share", 0.0)
            if all(any(alt in share and share[alt] >= floor for alt in group.split("|"))
                   for group in rule["all"]):
                return rule["species"]
        mapping = {**DEFAULT_LANGUAGE_SPECIES, **self.species}
        name = mapping.get(repo.primary_language or "", FALLBACK_SPECIES)
        return name if name in SPECIES else FALLBACK_SPECIES

    def cols_for(self, size_bytes: int) -> int:
        """Sprite length grows with log(code size): 1 kB -> min_cols, ~3 MB -> max_cols."""
        t = (math.log10(max(size_bytes, 1000)) - 3) / 3.5
        return round(self.min_cols + (self.max_cols - self.min_cols) * max(0.0, min(1.0, t)))


@dataclass
class Fish:
    repo: Repo
    species: str
    spec: Species
    mask: str
    facing_right: bool
    frames: list[list[str]]
    font_size: float
    y0: float = 0.0           # lane at the entry side
    y1: float = 0.0           # lane at the exit side (slightly diagonal crossing)
    angle: float = 0.0        # degrees, matches the diagonal
    rest_x: float = 0.0       # position used when animations are off
    duration: float = 30.0
    delay: float = 0.0
    bob_duration: float = 3.0

    @property
    def width(self) -> float:
        return max(len(l) for l in self.frames[0]) * CHAR_W * self.font_size

    @property
    def height(self) -> float:
        return len(self.frames[0]) * LINE_H * self.font_size


def rand(seed: str, *parts: object) -> float:
    """Deterministic float in [0, 1) so the tank looks the same between runs."""
    h = hashlib.sha256("|".join(map(str, (seed, *parts))).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2**64


def select(repos: list[Repo], cfg: Config) -> list[Repo]:
    excluded = {e.lower() for e in cfg.exclude} | {cfg.user.lower()}
    keep = [r for r in repos
            if r.name.lower() not in excluded
            and r.languages
            and (cfg.include_forks or not r.fork)
            and (cfg.include_archived or not r.archived)]
    keep.sort(key=cfg.size_bytes, reverse=True)
    return keep[:cfg.max_fish]


def build(repos: list[Repo], cfg: Config) -> list[Fish]:
    """Biggest first, so smaller animals are drawn on top of larger ones."""
    fish: list[Fish] = []
    for r in select(repos, cfg):
        name = cfg.species_for(r)
        spec = SPECIES[name]
        mask = spec.masks[int(rand(cfg.seed, r.name, "variant") * len(spec.masks))]
        cols = round(cfg.cols_for(cfg.size_bytes(r)) * spec.length)
        right = rand(cfg.seed, r.name, "dir") < 0.5
        fr = make_frames(mask, spec.motion, cols, cfg.frames, spec.texture)
        if not right:
            fr = [mirror(f) for f in fr]
        fish.append(Fish(repo=r, species=name, spec=spec, mask=mask, facing_right=right,
                         frames=fr, font_size=cfg.font_size))
    _layout(fish, cfg)
    return fish


def _layout(fish: list[Fish], cfg: Config) -> None:
    label = 0
    top, bottom = TOP_MARGIN, cfg.height - BOTTOM_MARGIN
    # Lanes in a deterministic shuffled order so big animals are not stacked together.
    order = sorted(fish, key=lambda f: rand(cfg.seed, f.repo.name, "lane"))
    n = max(len(order), 1)
    for i, f in enumerate(order):
        span = bottom - top - f.height - label
        centre = top + (i + 0.5) * (bottom - top) / n - (f.height + label) / 2
        f.y0 = max(top, min(top + span, centre))
        drift = (rand(cfg.seed, f.repo.name, "drift") - 0.5) * 0.16 * cfg.width
        f.y1 = max(top, min(top + span, f.y0 + drift))
        dx = cfg.width + f.width + 120
        a = math.degrees(math.atan2(f.y1 - f.y0, dx))
        f.angle = round(a if f.facing_right else -a, 2)

        speed = 30.0 * f.spec.speed * (0.8 + 0.4 * rand(cfg.seed, f.repo.name, "speed"))
        speed *= 1.25 - 0.5 * min(1.0, f.width / 300)  # big animals cruise slower
        f.duration = round(dx / speed, 2)
        # Golden-ratio phases: neighbouring lanes start far apart horizontally.
        phase = (i * 0.618034 + 0.1 * rand(cfg.seed, f.repo.name, "phase")) % 1.0
        f.delay = -round(phase * f.duration, 2)
        f.rest_x = round(rand(cfg.seed, f.repo.name, "rest") * (cfg.width - f.width), 1)
        f.bob_duration = round(3 + 3 * rand(cfg.seed, f.repo.name, "bob"), 2)


__all__ = ["Config", "Fish", "build", "select", "rand",
           "CHAR_W", "LINE_H", "TOP_MARGIN", "BOTTOM_MARGIN"]
