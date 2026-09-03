# Specimen plates

Photographs of a preserved sheep brain, dissected for the lab practicum.

Photographed by FlowingMind. Licensed CC BY 4.0 — see [`LICENSE`](LICENSE).

---

## `clean/` — atlas plates

Specimen on white with margin for label pills. These are what the interactive atlas renders;
labels are drawn as live HTML on top, which is what makes them independently filterable.

| File | View | Dimensions |
|---|---|---|
| `midsagittal.jpg` | Midsagittal section | 2000 × 1257 |
| `dorsal.jpg` | Dorsal surface | 1512 × 2000 |
| `lateral.jpg` | Lateral surface | 2000 × 1423 |
| `ventral.jpg` | Ventral surface | 2000 × 1419 |
| `posterior-internal.jpg` | Posterior, internal | 2000 × 1850 |
| `coronal-a.jpg` … `coronal-f.jpg` | Coronal series, rostral → caudal | ~2000 × 1450–1540 |

**Still needed:** `pulled-back-lateral.jpg` — the lateral view with the cerebellum retracted,
covering the geniculate nuclei, brachium, and middle cerebellar peduncle (quiz blocks Lat 12–16).
A labeled version exists in `labeled/`; the clean master hasn't been produced yet.

### Regenerating

Masters are PNGs with the background masked out via alpha. They're kept locally rather than
committed — 47 MB against 1.9 MB for the derived JPEGs. To rebuild the plates from them:

```bash
python3 scripts/prepare-plates.py
```

The script flattens alpha onto white, trims to the specimen, adds a 16% margin, and downscales
to a 2000 px long edge. Adjust with `--margin`, `--max-dim`, and `--quality`.

## `labeled/` — original plates

Labels are burned into the pixels, so these can't drive the dynamic atlas. Kept as reference
for what each view is supposed to show, and as a fallback if clean versions never materialize.

| File | View | Structures labeled |
|---|---|---|
| `dorsal.jpg` | Dorsal surface | 12 |
| `lateral.jpg` | Lateral surface | 11 |
| `ventral.jpg` | Ventral surface | 16 |
| `posterior-internal.jpg` | Posterior, internal | 3 |
| `pulled-back-lateral.jpg` | Lateral, cerebellum retracted | 5 |
| `coronal-a.jpg` … `coronal-f.jpg` | Coronal series, rostral → caudal | 3–10 each |

---

## Attribution

  Sheep brain specimen photographs by FlowingMind, licensed CC BY 4.0.
  Source: https://github.com/torryscott/lamina
