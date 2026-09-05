#!/usr/bin/env python3
"""
Generate the two Qualtrics QSF variants from one canonical survey file.

  lamina.qsf                  images served from GitHub Pages (portable — what
                              adopters import; works on import with no uploads)
  lamina-qualtrics-hosted.qsf images served from your own Qualtrics graphics
                              library (no external dependency during a graded
                              assessment)

Both are otherwise byte-identical. Only <img src> values differ.

Usage:
    python3 scripts/build-variants.py

Reads scripts/image-map.json for the plate -> URL mapping.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAP_FILE = ROOT / "scripts" / "image-map.json"
CANONICAL = ROOT / "qualtrics" / "lamina.qsf"
HOSTED_OUT = ROOT / "qualtrics" / "lamina-qualtrics-hosted.qsf"


def load_map():
    cfg = json.loads(MAP_FILE.read_text())
    pages_base = cfg["pages_base"].rstrip("/")
    q_base = cfg["qualtrics_base"]

    pages_url, qualtrics_url = {}, {}
    for name, meta in cfg["plates"].items():
        pages_url[name] = f"{pages_base}/{meta['repo_path']}"
        im = meta.get("qualtrics_im")
        qualtrics_url[name] = f"{q_base}{im}" if im else None
    return pages_url, qualtrics_url


def swap_images(qsf_text, replacements):
    """Replace image URLs inside the QSF's JSON-encoded question text."""
    out = qsf_text
    for old, new in replacements.items():
        # URLs live inside JSON strings, so slashes are escaped as \/
        for a, b in ((old, new), (old.replace("/", "\\/"), new.replace("/", "\\/"))):
            out = out.replace(a, b)
    return out


def main():
    if not CANONICAL.exists():
        sys.exit(f"Canonical survey not found: {CANONICAL}")

    pages_url, qualtrics_url = load_map()
    text = CANONICAL.read_text()

    replacements = {}
    skipped = []
    for name, p_url in pages_url.items():
        q_url = qualtrics_url.get(name)
        if not q_url:
            skipped.append(name)
            continue
        replacements[p_url] = q_url

    if not replacements:
        sys.exit("No plates have a qualtrics_im set in scripts/image-map.json — nothing to build.")

    hosted = swap_images(text, replacements)

    # Sanity check: the output must still be valid JSON
    try:
        json.loads(hosted)
    except json.JSONDecodeError as e:
        sys.exit(f"Generated variant is not valid JSON: {e}")

    HOSTED_OUT.write_text(hosted)

    print(f"Wrote {HOSTED_OUT.relative_to(ROOT)}")
    for p_url, q_url in replacements.items():
        print(f"  {p_url}")
        print(f"    -> {q_url}")
    if skipped:
        print("\nSkipped (no qualtrics_im set):")
        for name in skipped:
            print(f"  {name}")


if __name__ == "__main__":
    main()
