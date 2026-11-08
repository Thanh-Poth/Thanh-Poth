"""Rasterise the silhouettes into animated ASCII frames.

The silhouettes (seen from above, head pointing right) are stored as run-length masks
in ``silhouettes.txt``. For each animation frame the mask is deformed (wing flap, tail
sway, flipper paddle), then every character cell is sampled: cells fully inside get the
species texture, cells on the outline get a character that follows the edge direction.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

CHAR_ASPECT = 1.12 / 0.6  # character cell height / width
SUB_X, SUB_Y = 4, 6       # samples per cell


@dataclass(frozen=True)
class Mask:
    name: str
    w: int
    h: int
    rows: tuple[tuple[bool, ...], ...]
    yc: float  # body axis (centre of mass row)

    def at(self, x: float, y: float) -> bool:
        xi, yi = int(x), int(y)
        if 0 <= xi < self.w and 0 <= yi < self.h:
            return self.rows[yi][xi]
        return False


def _decode(line: str, width: int) -> tuple[bool, ...]:
    row: list[bool] = []
    filled = False
    for n in map(int, line.split(",")):
        row.extend([filled] * n)
        filled = not filled
    return tuple(row[:width] + [False] * (width - len(row)))


@lru_cache(maxsize=1)
def masks() -> dict[str, Mask]:
    text = (Path(__file__).with_name("silhouettes.txt")).read_text(encoding="utf-8")
    out: dict[str, Mask] = {}
    for block in text.split("@")[1:]:
        head, *lines = block.strip().splitlines()
        name, w, h = head.split()
        rows = tuple(_decode(l, int(w)) for l in lines)
        mass = [(y, sum(r)) for y, r in enumerate(rows)]
        total = sum(n for _, n in mass) or 1
        out[name] = Mask(name, int(w), len(rows), rows, sum(y * n for y, n in mass) / total)
    return out


# --- motions: (mask, x, y, t in [0,1)) -> source point ------------------------------

def flap(m: Mask, x: float, y: float, t: float) -> tuple[float, float]:
    """Manta ray: the wings fold towards the body and back (span shrinks seen from above)."""
    s = 1 - 0.32 * (1 - math.cos(2 * math.pi * t)) / 2
    body = 0.10 * m.h
    d = y - m.yc
    if abs(d) <= body:
        return x, y
    k = (abs(d) - body) / (m.h / 2)
    return x - 0.05 * m.w * (1 - s) / 0.32 * k, m.yc + math.copysign(body + (abs(d) - body) / s, d)


def sway(m: Mask, x: float, y: float, t: float) -> tuple[float, float]:
    """Sharks: a travelling wave, still head, swinging tail."""
    u = (m.w - x) / m.w  # 0 at the head, 1 at the tail
    return x, y - 0.075 * m.w * u * u * math.sin(2 * math.pi * t + 2.6 * u)


def paddle(m: Mask, x: float, y: float, t: float) -> tuple[float, float]:
    """Sea turtle: front flippers sweep back and forth, rear flippers follow gently."""
    shell = 0.24 * m.h
    d = abs(y - m.yc)
    if d <= shell:
        return x, y
    k = min(1.0, (d - shell) / (m.h / 2 - shell))
    a = 0.09 * m.w * math.sin(2 * math.pi * t)
    return (x - a * k, y) if x > 0.45 * m.w else (x + 0.4 * a * k, y)


MOTIONS = {"flap": flap, "sway": sway, "paddle": paddle}
PAD = {"flap": 0.0, "sway": 0.075, "paddle": 0.0}  # vertical room needed, x mask width


# --- rasteriser -----------------------------------------------------------------------

def _edge_char(samples: list[list[bool]]) -> str:
    cov = sum(map(sum, samples)) / (SUB_X * SUB_Y)
    cols = [any(samples[j][i] for j in range(SUB_Y)) for i in range(SUB_X)]
    rows = [any(r) for r in samples]
    if cov <= 0.3:
        if sum(cols) >= 3 and sum(rows) <= 3:
            return "-"
        if sum(rows) >= 4 and sum(cols) <= 2:
            return "|"
    half_x, half_y = SUB_X // 2, SUB_Y // 2
    left = sum(r[i] for r in samples for i in range(half_x))
    right = sum(r[i] for r in samples for i in range(half_x, SUB_X))
    top = sum(map(sum, samples[:half_y]))
    bottom = sum(map(sum, samples[half_y:]))
    n = SUB_X * SUB_Y / 2
    gx, gy = (right - left) / n, (bottom - top) / n
    if abs(gx) < 0.15 and abs(gy) < 0.15:
        return "." if cov < 0.5 else "o"
    if abs(gy) > 2 * abs(gx):
        return ("_" if cov < 0.5 else "-") if gy > 0 else "-"
    if abs(gx) > 2 * abs(gy):
        return "(" if gx > 0 else ")"
    return "/" if gx * gy > 0 else "\\"


def rasterise(m: Mask, motion: str, t: float, cols: int,
              texture: str = ":", seed_row: int = 0) -> list[str]:
    move = MOTIONS[motion]
    pad = PAD[motion] * m.w
    canvas_h = m.h + 2 * pad
    cell_w = m.w / cols
    cell_h = cell_w * CHAR_ASPECT
    n_rows = max(1, math.ceil(canvas_h / cell_h))
    off_y = (n_rows * cell_h - canvas_h) / 2 + pad  # centre the mask vertically

    grid: list[list[list[list[bool]]]] = []
    for r in range(n_rows):
        line = []
        for c in range(cols):
            cell = []
            for j in range(SUB_Y):
                y = (r + (j + 0.5) / SUB_Y) * cell_h - off_y
                sub = []
                for i in range(SUB_X):
                    x = (c + (i + 0.5) / SUB_X) * cell_w
                    sx, sy = move(m, x, y, t)
                    sub.append(m.at(sx, sy))
                cell.append(sub)
            line.append(cell)
        grid.append(line)

    out = []
    for r, line in enumerate(grid):
        chars = []
        for c, cell in enumerate(line):
            filled = sum(map(sum, cell))
            if filled == 0:
                chars.append(" ")
            elif filled == SUB_X * SUB_Y:
                chars.append(texture_char(texture, r + seed_row, c))
            else:
                chars.append(_edge_char(cell))
        out.append("".join(chars).rstrip())
    return out


def texture_char(texture: str, r: int, c: int) -> str:
    """Interior fill. A texture with several rows ("ab|cd") repeats as a 2-D pattern."""
    rows = texture.split("|")
    row = rows[r % len(rows)]
    return row[c % len(row)]


def frames(mask_name: str, motion: str, cols: int, n: int, texture: str) -> list[list[str]]:
    """n frames of one swim cycle, all padded to the same width and height."""
    m = masks()[mask_name]
    raw = [rasterise(m, motion, k / n, cols, texture) for k in range(n)]
    # Drop only the rows that are empty in every frame, so the sprite never jumps.
    used = [r for r in range(len(raw[0])) if any(f[r].strip() for f in raw)]
    lo, hi = (used[0], used[-1] + 1) if used else (0, 0)
    width = max((len(l) for f in raw for l in f), default=0)
    return [[l.ljust(width) for l in f[lo:hi]] for f in raw]
