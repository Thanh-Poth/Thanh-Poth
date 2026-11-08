"""Turn repositories into fish: species, size, colours, lane and speed."""
from __future__ import annotations

import hashlib
import math
import tomllib
from dataclasses import dataclass, field

from .github import Repo
from .palette import language_color
from .species import (BOTTOM_DWELLERS, DEFAULT_COMBOS, DEFAULT_LANGUAGE_SPECIES, DRIFTERS, FALLBACK_SPECIES,
                      SIZES, art)

CHAR_W = 0.6     # monospace glyph width, in em
LINE_H = 1.12    # line height, in em
TOP_MARGIN = 46  # room for the title bar
SAND_H = 46


@dataclass
class Config:
    user: str
    exclude: list[str] = field(default_factory=list)
    include_forks: bool = False
    include_archived: bool = True
    max_fish: int = 18
    width: int = 1000
    height: int = 520
    # code bytes thresholds: < small -> S, < large -> M, else L
    small_bytes: int = 15_000
    large_bytes: int = 250_000
    species: dict[str, str] = field(default_factory=dict)  # language -> species overrides
    # Bytes of these languages count less for size (notebooks embed outputs/images).
    size_weights: dict[str, float] = field(default_factory=lambda: {"Jupyter Notebook": 0.25})
    combos: list[dict] | None = None  # None -> DEFAULT_COMBOS; [] disables combination rules
    title: str = ""
    show_labels: bool = True
    highlight: list[str] = field(default_factory=list)  # repos with a starred, brighter label
    seed: str = "aquarium"

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
            if all(any(share.get(alt, -1) >= floor and alt in share for alt in group.split("|"))
                   for group in rule["all"]):
                return rule["species"]
        mapping = {**DEFAULT_LANGUAGE_SPECIES, **self.species}
        return mapping.get(repo.primary_language or "", FALLBACK_SPECIES)


@dataclass
class Fish:
    repo: Repo
    species: str
    size: str
    facing_right: bool
    lines: list[str]
    font_size: float
    stripes: list[tuple[float, float, str]]  # (start offset, end offset, colour), head first
    y: float = 0.0
    rest_x: float = 0.0
    duration: float = 30.0
    delay: float = 0.0
    bob_duration: float = 3.0

    @property
    def width(self) -> float:
        return max(len(l) for l in self.lines) * CHAR_W * self.font_size

    @property
    def height(self) -> float:
        return len(self.lines) * LINE_H * self.font_size


def rand(seed: str, *parts: object) -> float:
    """Deterministic float in [0, 1) so the tank looks the same between runs."""
    h = hashlib.sha256("|".join(map(str, (seed, *parts))).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2**64


def size_tier(code_bytes: int, cfg: Config) -> str:
    if code_bytes < cfg.small_bytes:
        return "S"
    if code_bytes < cfg.large_bytes:
        return "M"
    return "L"


def font_size(code_bytes: int) -> float:
    """Continuous scaling inside a tier: 1 kB -> 13px, 100 kB -> ~18px, 1 MB -> ~21px."""
    return max(13.0, min(24.0, 13 + 2.6 * (math.log10(max(code_bytes, 1000)) - 3)))


def stripes(languages: dict[str, int], max_colors: int = 4) -> list[tuple[float, float, str]]:
    """Colour bands proportional to each language's share of the code."""
    total = sum(languages.values()) or 1
    ranked = sorted(languages.items(), key=lambda kv: kv[1], reverse=True)
    head, tail = ranked[:max_colors], ranked[max_colors:]
    if tail and head:
        name, n = head[-1]
        head[-1] = (name, n + sum(b for _, b in tail))
    bands, pos = [], 0.0
    for name, n in head:
        share = n / total
        bands.append((pos, pos + share, language_color(name)))
        pos += share
    return bands or [(0.0, 1.0, language_color(""))]


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
    fish: list[Fish] = []
    for r in select(repos, cfg):
        species = cfg.species_for(r)
        n = cfg.size_bytes(r)
        size = size_tier(n, cfg)
        right = rand(cfg.seed, r.name, "dir") < 0.5
        fish.append(Fish(
            repo=r, species=species, size=size, facing_right=right,
            lines=art(species, size, right), font_size=font_size(n),
            stripes=stripes(r.languages),
        ))
    _layout(fish, cfg)
    return fish


def _layout(fish: list[Fish], cfg: Config) -> None:
    sand_top = cfg.height - SAND_H
    label = 14 if cfg.show_labels else 0
    swimmers = [f for f in fish if f.species not in BOTTOM_DWELLERS]
    # Shuffle lanes deterministically so big fish are not all stacked together.
    swimmers.sort(key=lambda f: rand(cfg.seed, f.repo.name, "lane"))
    band_top, band_bottom = TOP_MARGIN, sand_top - 10
    n = max(len(swimmers), 1)
    for i, f in enumerate(swimmers):
        centre = band_top + (i + 0.5) * (band_bottom - band_top) / n
        y = centre - (f.height + label) / 2
        f.y = max(band_top, min(band_bottom - f.height - label, y))
    for f in fish:
        if f.species in BOTTOM_DWELLERS:
            f.y = sand_top - f.height - label + 8

    # Golden-ratio phases: neighbouring lanes start far apart horizontally.
    order = {id(f): i for i, f in enumerate(swimmers)}
    for f in fish:
        u = rand(cfg.seed, f.repo.name, "speed")
        speed = {"S": 46.0, "M": 32.0, "L": 22.0}[f.size] * (0.8 + 0.4 * u)
        if f.species in DRIFTERS:
            speed *= 0.45
        if f.species in BOTTOM_DWELLERS:
            speed *= 0.6
        distance = cfg.width + f.width + 120
        f.duration = round(distance / speed, 2)
        k = order.get(id(f), len(order) + fish.index(f))
        phase = (k * 0.618034 + 0.1 * rand(cfg.seed, f.repo.name, "phase")) % 1.0
        f.delay = -round(phase * f.duration, 2)
        f.rest_x = round(rand(cfg.seed, f.repo.name, "rest") * (cfg.width - f.width), 1)
        f.bob_duration = round(2.4 + 2.4 * rand(cfg.seed, f.repo.name, "bob"), 2)


__all__ = ["Config", "Fish", "build", "select", "size_tier", "stripes", "rand", "SIZES",
           "CHAR_W", "LINE_H", "SAND_H", "TOP_MARGIN"]
