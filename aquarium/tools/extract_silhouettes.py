"""Dev tool: cut the silhouettes out of assets/silhouettes.png into ascii_aquarium/silhouettes.txt.

Needs Pillow, NumPy and SciPy (only for this step, the library itself has no dependencies):

    python tools/extract_silhouettes.py [--preview preview.png]

Each silhouette is rotated so its head points RIGHT, cropped, resized so its long side is
RES pixels, and stored as run-length rows: "@name width height" then one line per row,
alternating empty/filled run lengths (starting with empty).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "silhouettes.png"
OUT = ROOT / "ascii_aquarium" / "silhouettes.txt"
RES = 200
MIN_AREA = 500

# Components are found top-to-bottom, left-to-right by scipy; identify them by the
# image position of their bounding-box centre, then rotate (degrees, counter-clockwise).
SHAPES = {
    # name:        (centre x, centre y, rotation)
    "hammerhead": (272, 145, 125),
    "ray1": (86, 89, 70),
    "shark": (88, 329, 58),
    "ray2": (297, 365, 118),
    "ray3": (86, 555, 60),
    "turtle": (285, 626, 100),
}


def components(gray: np.ndarray) -> list[tuple[tuple[float, float], np.ndarray]]:
    lab, _ = ndimage.label(gray < 110)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        m = lab[sl] == i
        if m.sum() < MIN_AREA:
            continue
        cy = (sl[0].start + sl[0].stop) / 2
        cx = (sl[1].start + sl[1].stop) / 2
        out.append(((cx, cy), ndimage.binary_fill_holes(m)))
    return out


def normalise(mask: np.ndarray, angle: float) -> np.ndarray:
    img = Image.fromarray((mask * 255).astype("uint8"))
    img = img.rotate(angle, expand=True, resample=Image.BICUBIC)
    a = np.asarray(img) > 127
    ys, xs = np.nonzero(a)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape
    scale = RES / max(h, w)
    img = Image.fromarray((a * 255).astype("uint8")).resize(
        (max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    return np.asarray(img) > 110


def rle(row: np.ndarray) -> str:
    runs, current, n = [], False, 0
    for v in row:
        if bool(v) == current:
            n += 1
        else:
            runs.append(n)
            current, n = bool(v), 1
    runs.append(n)
    return ",".join(map(str, runs))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--preview", help="write a contact sheet of the normalised shapes")
    args = p.parse_args()

    gray = np.asarray(Image.open(SRC).convert("L"))
    comps = components(gray)
    blocks, masks = [], []
    for name, (x, y, angle) in SHAPES.items():
        _, mask = min(comps, key=lambda c: (c[0][0] - x) ** 2 + (c[0][1] - y) ** 2)
        m = normalise(mask, angle)
        masks.append(m)
        blocks.append(f"@{name} {m.shape[1]} {m.shape[0]}\n" + "\n".join(rle(r) for r in m))
    OUT.write_text("\n".join(blocks) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(blocks)} silhouettes)")

    if args.preview:
        sheet = Image.new("L", (len(masks) * (RES + 20), RES + 20), 255)
        for k, m in enumerate(masks):
            sheet.paste(Image.fromarray(((~m) * 255).astype("uint8")), (k * (RES + 20) + 10, 10))
        sheet.save(args.preview)


if __name__ == "__main__":
    main()
