#!/usr/bin/env python3
"""Recover the Coronal F plate from the teaching-atlas PDF.

Every other plate comes from a PNG master with the background already removed.
Coronal F has no master, but the atlas PDF embeds the original photograph
underneath its printed labels, so the unlabelled image can be pulled straight
out. The photo sits on a dark dissection surface, so the specimen is
segmented by colour rather than by an alpha channel, and it is rotated 5
degrees to the orientation the printed plate uses.

    python3 scripts/extract-coronal-f.py "/path/to/Coronal (Frontal) Sheep Brain Atlas.pdf"
"""
import argparse, io, pathlib, sys
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARGIN, MAX_DIM, QUALITY, ROTATE = 0.16, 2000, 88, 5.0   # matches prepare-plates.py


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="the coronal atlas PDF")
    ap.add_argument("--page", type=int, default=6, help="1-based page holding plate F")
    args = ap.parse_args()

    try:
        import fitz                      # PyMuPDF
    except ImportError:
        sys.exit("PyMuPDF is needed:  pip install pymupdf")

    doc = fitz.open(args.pdf)
    page = doc[args.page - 1]
    images = page.get_images(full=True)
    if not images:
        sys.exit(f"page {args.page} embeds no image")
    raw = doc.extract_image(images[0][0])
    im = Image.open(io.BytesIO(raw["image"])).convert("RGB")
    doc.close()

    # Specimen: warm and bright, but not the pure white the page paints around it.
    a = np.asarray(im).astype(int)
    R, B = a[..., 0], a[..., 2]
    mask = (R > 140) & (R > B + 10) & (a.min(2) < 246)
    mask = ndimage.binary_opening(ndimage.binary_closing(mask, np.ones((9, 9))), np.ones((15, 15)))
    lab, n = ndimage.label(mask)
    if not n:
        sys.exit("no specimen found")
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    mask = ndimage.binary_fill_holes(lab == int(np.argmax(sizes)) + 1)

    soft = np.clip((ndimage.gaussian_filter(mask.astype(float), 1.5) - 0.35) / 0.35, 0, 1)
    flat = np.asarray(im).astype(float) * soft[..., None] + 255.0 * (1 - soft[..., None])
    img = Image.fromarray(flat.round().astype(np.uint8)).rotate(
        -ROTATE, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))
    rot = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).rotate(
        -ROTATE, resample=Image.NEAREST, expand=True, fillcolor=0)) > 127
    ys, xs = np.nonzero(rot)
    img = img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

    pad = int(max(img.size) * MARGIN)
    canvas = Image.new("RGB", (img.width + pad * 2, img.height + pad * 2), "white")
    canvas.paste(img, (pad, pad))
    if max(canvas.size) > MAX_DIM:
        s = MAX_DIM / max(canvas.size)
        canvas = canvas.resize((round(canvas.width * s), round(canvas.height * s)), Image.LANCZOS)

    dst = ROOT / "images" / "clean" / "coronal-f.jpg"
    canvas.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    print(f"{dst.relative_to(ROOT)}  {canvas.size[0]}x{canvas.size[1]}  {dst.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
