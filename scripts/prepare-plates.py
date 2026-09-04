#!/usr/bin/env python3
"""
Turn background-removed specimen PNGs into atlas-ready JPEG plates.

The source PNGs carry an alpha channel with the background already masked out.
This script flattens that alpha onto white, trims to the specimen, adds a
uniform margin for label pills to sit in, and downscales to a sane web size.

Usage:
    python3 scripts/prepare-plates.py [--margin 0.16] [--max-dim 2000] [--quality 88]
"""

import argparse
import pathlib
import sys

try:
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit("Pillow and NumPy are required:  python3 -m pip install Pillow numpy")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "images" / "clean"

# Source filename -> canonical plate name (matches images/labeled/)
# NOTE: midsagittal is deliberately excluded. Its 25 marker coordinates were
# placed against the original plate, which frames the specimen edge-to-edge.
# Regenerating it here would reframe the specimen and misalign every label.
# Re-enable only if you also re-place the markers in the capture tool.
PLATES = {
    # Coronal A-E come from PNG masters named to match the printed plates.
    # Coronal F has no master: it is recovered from the atlas PDF by
    # scripts/extract-coronal-f.py, which writes images/clean/coronal-f.jpg
    # directly. Running this script does not touch that plate.
    "Coronal A.png":                "coronal-a",
    "Coronal B.png":                "coronal-b",
    "Coronal C.png":                "coronal-c",
    "Coronal D.png":                "coronal-d",
    "Coronal E.png":                "coronal-e",
    "Gross Dorsal View.png":        "dorsal",
    "Gross Lateral View.png":       "lateral",
    "Gross Posterior Internal.png": "posterior-internal",
    "Gross Ventral View.png":       "ventral",
    "Pulled Back Lateral View.png": "pulled-back-lateral",
    # "Midsagittal.png":            "midsagittal",   # see note below
}

# Degrees clockwise to rotate a plate after trimming. The dorsal photograph
# was taken rostral-up; the teaching atlas shows it rostral-right, so the
# plate is rotated to match. Coordinates in data/<view>.json are in the
# rotated frame — changing a rotation means re-placing that view's markers.
ROTATE = {
    "dorsal": 90,
}


def prepare(src: pathlib.Path, dst: pathlib.Path, margin: float, max_dim: int, quality: int,
            rotate: int = 0):
    im = Image.open(src)

    # Masters come two ways: with the background cut to transparency, or with it
    # already painted white. Trim to whichever marks the specimen.
    if "A" in im.getbands() and im.getchannel("A").getextrema()[0] < 255:
        im = im.convert("RGBA")
        bbox = im.getchannel("A").getbbox()
        if bbox is None:
            raise ValueError("image is fully transparent")
    else:
        im = im.convert("RGB")
        a = np.asarray(im).astype(int)
        content = ~((a > 244).all(2))
        cols = np.nonzero(content.any(0))[0]
        rows = np.nonzero(content.any(1))[0]
        if not len(cols) or not len(rows):
            raise ValueError("image is entirely background")
        bbox = (int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1)
        im = im.convert("RGBA")
    im = im.crop(bbox)

    # Uniform margin, sized off the long edge so plates look consistent
    pad = int(max(im.size) * margin)
    canvas = Image.new("RGB", (im.width + pad * 2, im.height + pad * 2), "white")
    canvas.paste(im, (pad, pad), im)          # alpha as the paste mask

    # Rotate after padding so the margin stays uniform. PIL's transpose
    # constants are counter-clockwise, hence the mapping.
    if rotate:
        canvas = canvas.transpose({90: Image.ROTATE_270, 180: Image.ROTATE_180, 270: Image.ROTATE_90}[rotate])

    # Downscale to the target long edge
    long_edge = max(canvas.size)
    if long_edge > max_dim:
        s = max_dim / long_edge
        canvas = canvas.resize(
            (round(canvas.width * s), round(canvas.height * s)),
            Image.LANCZOS,
        )

    canvas.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
    return canvas.size, dst.stat().st_size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--margin", type=float, default=0.16,
                    help="margin as a fraction of the long edge (default 0.16)")
    ap.add_argument("--max-dim", type=int, default=2000)
    ap.add_argument("--quality", type=int, default=88)
    ap.add_argument("--only", nargs="*", metavar="NAME",
                    help="regenerate only these plates (e.g. --only dorsal)")
    args = ap.parse_args()

    total_in = total_out = 0
    missing = []

    print(f"{'PLATE':<22} {'DIMENSIONS':<13} {'SIZE':>8}")
    print("-" * 46)

    for filename, name in PLATES.items():
        src = SRC / filename
        if args.only and name not in args.only:
            continue
        if not src.exists():
            missing.append(filename)
            continue
        dst = SRC / f"{name}.jpg"
        size, nbytes = prepare(src, dst, args.margin, args.max_dim, args.quality,
                               rotate=ROTATE.get(name, 0))
        total_in += src.stat().st_size
        total_out += nbytes
        print(f"{name:<22} {size[0]}x{size[1]:<8} {nbytes // 1024:>6} KB")

    print("-" * 46)
    print(f"{len(PLATES) - len(missing)} plates   "
          f"{total_in / 1e6:.1f} MB PNG -> {total_out / 1e6:.1f} MB JPEG")

    if missing:
        print("\nNot found:")
        for m in missing:
            print(f"  {m}")


if __name__ == "__main__":
    main()
