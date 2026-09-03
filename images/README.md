# Specimen plates

Photographs of a preserved sheep brain, dissected for the lab practicum.

Photographed by FlowingMind. Licensed CC BY 4.0 — see [`LICENSE`](LICENSE).

---

## `clean/` — unlabeled plates

What the interactive atlas needs. Labels are rendered as live HTML on top of these, which is
what makes them independently filterable.

| File | View | Dimensions |
|---|---|---|
| `midsagittal.jpg` | Midsagittal section | 2000 × 1500 |

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

## Producing clean plates

To build an atlas for any view in `labeled/`, an unlabeled version has to exist first.

**If layered source files survive** (Keynote, PowerPoint, Illustrator, Photoshop), hide the
label layer and re-export. Minutes per plate.

**If the labels were flattened**, it's manual cleanup — clone/heal over the text and leader
lines. Watch for ghosting, which reads badly under an HTML label sitting on top.

Either way:

- **Format** JPEG. These are photographs; PNG buys nothing here.
- **Width** 1500–2000 px. The atlas scales down cleanly; it can't invent detail.
- **File size** Under ~800 KB, so the survey stays responsive on classroom wifi.
- **Background** Leave the white surround. The atlas places labels in that margin.

Save to `clean/` with a name matching the view.

---

## Attribution

  Sheep brain specimen photographs by FlowingMind, licensed CC BY 4.0.
  Source: https://github.com/torryscott/lamina
