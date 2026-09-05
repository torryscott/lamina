#!/usr/bin/env python3
"""Recover the Coronal F plate from the teaching-atlas PDF.

Every other plate comes from a PNG master with the background already removed.
Coronal F has no master, but the atlas PDF embeds the original photograph
underneath its printed labels, so the unlabeled image can be pulled straight
out. The photo sits on a dark dissection surface, so the specimen is segmented
by color rather than by an alpha channel.

The photograph is tilted. `--rotate` sets how far it is turned before trimming,
in degrees clockwise. 5.0 reproduces the orientation of the printed plate;
larger values straighten the slice further. Marker positions are stored as
points in the original photograph and mapped through the same rotation, so the
three structures stay on the anatomy at any angle and the image is only ever
resampled once.

    python3 scripts/extract-coronal-f.py "/path/to/Coronal (Frontal) Sheep Brain Atlas.pdf"
    python3 scripts/extract-coronal-f.py "…/atlas.pdf" --rotate 7.5
"""
import argparse, io, json, math, pathlib, sys
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARGIN, MAX_DIM, QUALITY = 0.16, 2000, 88      # matches prepare-plates.py
DEFAULT_ROTATE = 5.0                            # the printed plate's orientation

# Where each structure sits in the original photograph, in its own pixels.
# Read from the printed plate at 5 degrees, then carried back to the source
# frame so any rotation can be applied without re-reading the atlas.
ANCHORS = {
    "inc_cor_superior_colliculus":       (1214.1, 1520.7),
    "inc_cor_coronal_cerebral_aqueduct": (1532.9, 2038.9),
    "inc_cor_tegmentum":                 (1491.7, 2396.9),
}
STRUCTURES = [
    ("inc_cor_superior_colliculus", "Superior Colliculus", "Gray Matter",
     "The rostral pair of swellings on the roof of the midbrain, involved in visual reflexes and orienting.",
     ["superior colliculi", "rostral colliculus", "optic tectum"], (0.22, 0.06)),
    ("inc_cor_coronal_cerebral_aqueduct", "Cerebral Aqueduct", "a Cavity",
     "The narrow channel through the midbrain connecting the third and fourth ventricles.",
     ["aqueduct", "aqueduct of sylvius"], (0.80, 0.94)),
    ("inc_cor_tegmentum", "Tegmentum", "Gray Matter",
     "The core of the midbrain beneath the colliculi, carrying cranial nerve nuclei and ascending and descending tracts.",
     ["midbrain tegmentum"], (0.22, 0.94)),
]


def specimen_mask(im):
    """The slice is warm and bright; the page paints pure white around it."""
    a = np.asarray(im).astype(int)
    R, B = a[..., 0], a[..., 2]
    m = (R > 140) & (R > B + 10) & (a.min(2) < 246)
    m = ndimage.binary_opening(ndimage.binary_closing(m, np.ones((9, 9))), np.ones((15, 15)))
    lab, n = ndimage.label(m)
    if not n:
        sys.exit("no specimen found in the embedded photograph")
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    return ndimage.binary_fill_holes(lab == int(np.argmax(sizes)) + 1)


def geometry(im, mask, rotate):
    """Trim/pad/scale numbers for this rotation, plus a source-pixel -> fraction map."""
    W, H = im.size
    rot = Image.fromarray((mask * 255).astype(np.uint8)).rotate(
        -rotate, resample=Image.NEAREST, expand=True, fillcolor=0)
    Wp, Hp = rot.size
    ys, xs = np.nonzero(np.asarray(rot) > 127)
    x0, y0 = int(xs.min()), int(ys.min())
    cw, ch = int(xs.max()) - x0 + 1, int(ys.max()) - y0 + 1
    pad = int(max(cw, ch) * MARGIN)
    pw, ph = cw + 2 * pad, ch + 2 * pad
    s = MAX_DIM / max(pw, ph) if max(pw, ph) > MAX_DIM else 1.0
    fw, fh = round(pw * s), round(ph * s)
    phi = math.radians(-rotate)
    cx, cy, cxp, cyp = W / 2, H / 2, Wp / 2, Hp / 2

    def to_fraction(px, py):
        dx, dy = px - cx, py - cy
        rx = cxp + dx * math.cos(phi) + dy * math.sin(phi)
        ry = cyp - dx * math.sin(phi) + dy * math.cos(phi)
        return round((rx - x0 + pad) * s / fw, 4), round((ry - y0 + pad) * s / fh, 4)

    return dict(crop=(x0, y0, cw, ch), pad=pad, scale=s, size=(fw, fh), to_fraction=to_fraction)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="the coronal atlas PDF")
    ap.add_argument("--page", type=int, default=6, help="1-based page holding plate F")
    ap.add_argument("--rotate", type=float, default=DEFAULT_ROTATE,
                    help="degrees clockwise before trimming (default %(default)s)")
    args = ap.parse_args()

    try:
        import fitz                      # PyMuPDF
    except ImportError:
        sys.exit("PyMuPDF is needed:  pip install pymupdf")

    doc = fitz.open(args.pdf)
    images = doc[args.page - 1].get_images(full=True)
    if not images:
        sys.exit(f"page {args.page} embeds no image")
    im = Image.open(io.BytesIO(doc.extract_image(images[0][0])["image"])).convert("RGB")
    doc.close()

    mask = specimen_mask(im)
    geo = geometry(im, mask, args.rotate)

    # Feather the cut edge so the specimen does not look scissored.
    soft = np.clip((ndimage.gaussian_filter(mask.astype(float), 1.5) - 0.35) / 0.35, 0, 1)
    flat = np.asarray(im).astype(float) * soft[..., None] + 255.0 * (1 - soft[..., None])
    img = Image.fromarray(flat.round().astype(np.uint8)).rotate(
        -args.rotate, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))
    x0, y0, cw, ch = geo["crop"]
    img = img.crop((x0, y0, x0 + cw, y0 + ch))
    pad = geo["pad"]
    canvas = Image.new("RGB", (cw + pad * 2, ch + pad * 2), "white")
    canvas.paste(img, (pad, pad))
    if geo["scale"] != 1.0:
        canvas = canvas.resize(geo["size"], Image.LANCZOS)

    dst = ROOT / "images" / "clean" / "coronal-f.jpg"
    canvas.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    print(f"{dst.relative_to(ROOT)}  {canvas.size[0]}x{canvas.size[1]}  "
          f"{dst.stat().st_size // 1024} KB  at {args.rotate:+.1f} degrees")

    # Markers follow the same rotation. Label pills keep whatever the data file
    # already has, since they sit in the margin rather than on the anatomy.
    data_path = ROOT / "data" / "coronal-f.json"
    existing = {}
    if data_path.exists():
        existing = {s["flag"]: s for s in json.loads(data_path.read_text())["structures"]}
    out = []
    for flag, name, matter, about, accept, default_label in STRUCTURES:
        tx, ty = geo["to_fraction"](*ANCHORS[flag])
        prev = existing.get(flag, {})
        label = prev.get("label", {"x": default_label[0], "y": default_label[1]})
        out.append({"flag": flag, "name": name, "matter": matter, "about": about,
                    "accept": list(accept), "target": {"x": tx, "y": ty}, "label": label})
        print(f"   {name:<20} ({tx}, {ty})")
    data_path.write_text(json.dumps(
        {"view": "coronal-f", "label": "Coronal F", "image": "images/clean/coronal-f.jpg",
         "structures": out}, indent=2, ensure_ascii=False) + "\n")
    print(f"{data_path.relative_to(ROOT)}  {len(out)} structures")


if __name__ == "__main__":
    main()
