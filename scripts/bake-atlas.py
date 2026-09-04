#!/usr/bin/env python3
"""
Bake the interactive atlas into the Qualtrics survey file.

Qualtrics stores a question's markup in Payload.QuestionText and its
per-question script in Payload.QuestionJS. Both survive export/import, so a
QSF can ship a working atlas with no manual pasting.

This script copies the current embed sources into the survey, so the QSF never
drifts from the files under qualtrics/atlas-embeds/.

    python3 scripts/bake-atlas.py

Then regenerate the image-URL variant:

    python3 scripts/build-variants.py
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QSF = ROOT / "qualtrics" / "lamina.qsf"

# Which question holds which view's atlas
ATLASES = {
    "QID424": {
        "html": ROOT / "qualtrics" / "atlas-embeds" / "midsagittal.html",
        "js":   ROOT / "qualtrics" / "atlas-embeds" / "midsagittal.js",
        "desc": "Interactive Midsagittal Atlas",
    },
}


def load_html(path):
    """Embed markup, minus any inline <script> — the JS goes in QuestionJS."""
    html = path.read_text()
    html = re.sub(r"<script>.*?</script>", "", html, flags=re.S).strip()
    html = re.sub(r"\n{3,}", "\n\n", html)
    if "<script" in html:
        sys.exit(f"{path}: an inline <script> survived stripping")
    return html


def main():
    if not QSF.exists():
        sys.exit(f"survey not found: {QSF}")

    data = json.loads(QSF.read_text())
    by_qid = {
        e["PrimaryAttribute"]: e
        for e in data["SurveyElements"]
        if e.get("Element") == "SQ"
    }

    for qid, spec in ATLASES.items():
        el = by_qid.get(qid)
        if el is None:
            sys.exit(f"{qid} not found in {QSF.name}")
        for key in ("html", "js"):
            if not spec[key].exists():
                sys.exit(f"missing source: {spec[key]}")

        html = load_html(spec["html"])
        js = spec["js"].read_text().strip()
        if not js.startswith("Qualtrics.SurveyEngine"):
            sys.exit(f"{spec['js']}: expected a Qualtrics.SurveyEngine block")

        p = el["Payload"]
        p["QuestionText"] = html
        p["QuestionJS"] = js
        p["QuestionDescription"] = spec["desc"]
        el["SecondaryAttribute"] = spec["desc"]

        print(f"{qid}  <- {spec['html'].name} ({len(html):,} chars)"
              f" + {spec['js'].name} ({len(js):,} chars)")

    QSF.write_text(json.dumps(data))
    json.loads(QSF.read_text())          # parse-check what we just wrote
    print(f"\nWrote {QSF.relative_to(ROOT)}")
    print("Now run: python3 scripts/build-variants.py")


if __name__ == "__main__":
    main()
