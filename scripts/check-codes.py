#!/usr/bin/env python3
"""Verify codes.js against the link builder and the data files.

Every flag the builder knows must have exactly one code; every flag in a
data/<view>.json must have a code; codes and flags must be unique.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
codes_js = (ROOT / "codes.js").read_text()
pairs = re.findall(r"^\s+([A-Z]+\d+):\s+'(inc_[a-z_]+)',", codes_js, re.M)
codes = dict(pairs)
flags = {f: c for c, f in pairs}
problems = []
if len(codes) != len(pairs): problems.append("duplicate code in codes.js")
if len(flags) != len(pairs): problems.append("one flag has two codes in codes.js")

b = (ROOT / "tools/link-builder.html").read_text()
i = b.index("const DATA = {"); j = b.index("\n};", i)
builder = re.findall(r'"flag":\s*"(inc_[a-z_]+)"', b[i:j])
for f in builder:
    if f not in flags: problems.append(f"builder flag has no code: {f}")
for f in flags:
    if f not in builder: problems.append(f"code {flags[f]} -> {f} is not in the builder")

for p in sorted((ROOT / "data").glob("*.json")):
    for s in json.loads(p.read_text())["structures"]:
        if s["flag"] not in flags: problems.append(f"{p.name}: flag has no code: {s['flag']}")

print(f"{len(codes)} codes · {len(builder)} builder flags · "
      f"{sum(1 for _ in (ROOT / 'data').glob('*.json'))} data files")
for m in problems: print("  !!", m)
sys.exit(1 if problems else 0)
