#!/usr/bin/env python3
"""Verify codes.js against the data files.

Every flag in a data/<view>.json must have a code; codes and flags must be
unique. Codes for retired structures stay reserved and are listed.
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

# The link builder reads the data files at runtime, so the data files are the
# authoritative list of what can be assigned.
used = set()
for p in sorted((ROOT / "data").glob("*.json")):
    for s in json.loads(p.read_text())["structures"]:
        used.add(s["flag"])
        if s["flag"] not in flags: problems.append(f"{p.name}: flag has no code: {s['flag']}")
retired = [flags[f] for f in flags if f not in used]   # codes stay reserved after a structure is retired

print(f"{len(codes)} codes · {len(used)} flags in use across "
      f"{sum(1 for _ in (ROOT / 'data').glob('*.json'))} data files")
if retired: print(f"  retired codes (kept reserved): {', '.join(sorted(retired, key=lambda c: (c[0], int(c[1:]))))}")
for m in problems: print("  !!", m)
sys.exit(1 if problems else 0)
