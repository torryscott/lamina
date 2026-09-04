# Conventions

Technical reference for editing the survey directly — whether through the Qualtrics UI or by
modifying the QSF as JSON. If you're only importing and running the module, the
[README](../README.md) is enough.

---

## Flag naming

```
inc_<view>_<structure>
```

- `inc_` — prefix identifying a structure-inclusion flag. The atlas and link builder both
  filter on this prefix, so don't use it for anything else.
- `<view>` — the anatomical view or sub-view the block belongs to.
- `<structure>` — the structure name, lowercased, non-alphanumerics collapsed to underscores.

### Short codes

Each flag also has a permanent short code in `codes.js`: view letter + number (`D1`,
`L4`, `C12`). Student links use codes — `?off=D1.M3` hides those structures —
and the pages still honour `inc_<flag>=0`. Rules:

- A code is assigned once and never changed or reused, even if the structure is removed.
- A new structure takes the next number in its view's run, wherever it sits in the list.
- Run `python3 scripts/check-codes.py` after touching `codes.js`, the builder, or a data file.

Letters: `D` dorsal · `L` lateral · `V` ventral · `P` posterior · `C` coronal · `M` midsagittal.

### View prefixes

| Prefix | View | Flags | Quiz branch |
|---|---|---:|---|
| `mid` | Midsagittal | 30 | Midsagittal |
| `cor` | Coronal | 30 | Coronal |
| `dorsal` | Dorsal surface | 11 | Gross |
| `lat` | Lateral surface | 16 | Gross |
| `vent` | Ventral surface | 16 | Gross |
| `post` | Posterior / internal | 6 | Gross |
| `dosal` | *(typo — see below)* | 1 | Gross |

110 flags total. The Gross branch aggregates dorsal, lateral, ventral, and posterior.

### The `dosal` typo

One block is named `Dosal - 8 Block (Dorsomedian Fissure)` with the flag
`inc_dosal_dorsomedian_fissure` — a misspelling that predates this system. It's preserved
deliberately: renaming it means changing the flag in the QSF, the link builder, and the
capture tool simultaneously, and any instructor link containing the old flag silently breaks.

If you fix it, fix it in all three places at once and treat it as a breaking change.

---

## Block naming

```
<View> - <N> Block (<Structure>)
```

Examples: `Mid - 22 Block (Central Sulcus)`, `Cor - 29 Block (Massa Intermedia)`.

Numbers are sequential within a view prefix, with gaps where blocks were removed over time.
They carry no meaning beyond ordering in the editor — the flag is what actually identifies
a block.

Two blocks break the pattern for historical reasons: `Coronal - Cerebral Aqueduct` and
the `Dosal - 8` block above.

---

## Block anatomy

Six elements per block, always in this order:

| # | Element | Type / Selector | Export tag |
|---|---|---|---|
| 1 | Pic | `DB` / `GRB` / `WOTXB` | `<View> - <N> Pic` |
| 2 | Ans | `TE` / `SL` | `<View> - <N> Ans` |
| 3 | Timer | `Timing` / `D` | `<View> - <N> Timer` |
| 4 | Page break | — | — |
| 5 | Pic (reveal) | `DB` / `GRB` / `WOTXB` | default `Q<n>` |
| 6 | Feedback | `DB` / `TB` | default `Q<n>` |

The **Feedback** question pipes the student's response from the Ans question:

```html
<strong>Your Answer:</strong>&nbsp;${q://QID87/ChoiceTextEntryValue}
<div><strong>Correct Answer: </strong>Thalamus</div>
<button onclick="alert('…explanation…')">What is the Thalamus?</button>
```

The `QID87` reference must point at that block's own Ans question. If you duplicate a block
in the Qualtrics UI, **check this** — a stale reference shows the wrong answer back to students.

---

## Display logic

Every question in a structure block carries the same rule: show unless the flag is explicitly
`0`. In the QSF that's:

```json
"DisplayLogic": {
  "0": {
    "0": {
      "LogicType": "EmbeddedField",
      "LeftOperand": "inc_mid_thalamus",
      "Operator": "NotEqualTo",
      "RightOperand": "0",
      "Type": "Expression"
    },
    "Type": "If"
  },
  "Type": "BooleanExpression",
  "inPage": false
}
```

### Why `NotEqualTo 0` and not `EqualTo 1`

Two failed approaches preceded this one, and both are easy to repeat:

1. **Declaring flags in Survey Flow with a default value of `1`.** A Survey Flow embedded-data
   element that sets a constant *overwrites* the URL parameter, so `?inc_x=0` had no effect.
2. **Declaring them with an empty value.** Same problem — the flow element still ran after the
   URL was parsed and blanked the field.

The fix was to remove the Survey Flow declarations entirely and invert the comparison. Qualtrics
populates embedded data from URL parameters automatically when a field is referenced in logic,
so an unset flag is simply absent — which is *not equal to* `0`, so the block shows.

**Do not add these flags to Survey Flow.** It breaks the whole mechanism.

### Block-level logic doesn't work here

Logic sits on all five questions individually, not on the block. Block-level Display Logic
doesn't round-trip reliably through QSF import.

---

## Matter-type vocabulary

The Ans question includes a hint about tissue type. Values in use:

- `Gray Matter`
- `White Matter`
- `Gray Matter (Not a Lobe)` — for gyri and cortical regions
- `a Lobe`
- `a Groove` — sulci and fissures
- `a Cavity` — ventricles and cisterns
- `spongy tissue` — choroid plexus

Some carry an extra prompt, e.g. `Gray Matter (Be specific. What part of the cerebellum is it?)`.

Where a structure appears in several views, the matter type stays consistent across all of them.

---

## Survey Flow

```
Intro
└─ Branch: which view?
   ├─ Gross Neuroanatomy
   │  ├─ Branch: Atlas  → atlas block
   │  └─ Branch: Quiz   → BlockRandomizer (50 of 50)
   ├─ Coronal Neuroanatomy
   │  ├─ Branch: Atlas  → atlas block
   │  └─ Branch: Quiz   → BlockRandomizer (30 of 30)
   └─ Midsagittal Neuroanatomy
      ├─ Branch: Atlas  → atlas block
      └─ Branch: Quiz   → BlockRandomizer (30 of 30)
```

Each randomizer's `SubSet` equals its total block count, so every block is presented in random
order rather than a random sample. **When you add a block, increment `SubSet` too** — otherwise
the new block is only sometimes shown.

Blocks whose flag is `0` still get selected by the randomizer; their questions just render
nothing. The effective quiz length shrinks accordingly.

---

## Atlas embedding

Each atlas lives in a Descriptive Text question and needs two pieces in two different editors:

| Piece | Where | Notes |
|---|---|---|
| HTML + CSS | Question content → `<>` source view | Everything scoped under `.smcm-atlas-mid` |
| JavaScript | Question gear → *Edit Question JavaScript* | `Qualtrics.SurveyEngine.addOnReady(...)` |

**The Rich Content Editor strips `<script>` tags on paste.** That's why the JavaScript is
separate. If you paste HTML into the JavaScript editor you get `Unexpected token <`.

In the QSF these are `Payload.QuestionText` and `Payload.QuestionJS`. Both round-trip through
export/import, so a QSF can ship a working atlas with no manual pasting — which is how
`lamina.qsf` is built.

### Scoping

All CSS is prefixed with `.smcm-atlas-mid` and element IDs with `smcm` to avoid colliding with
Qualtrics' own styles. Keep that convention if you add views — an unscoped `button` or `img`
rule will leak into the rest of the survey page.

### Responsive behavior

- Label and dot sizes scale from a `--iw` custom property that JavaScript sets to the image's
  rendered width, so labels stay proportional at any display size.
- Below 720px, CSS forces hover-reveal behavior regardless of the selected mode — 25 labels on a
  phone-width image is unreadable otherwise.
- Don't try to widen the atlas past Qualtrics' question container with negative margins or
  viewport units. The editor preview pane is narrower than a real browser and it clips.
  A *View full image* link handles the need for a larger view.

---

## Atlas data format

```json
{
  "image":   { "filename": "midsagittal.jpg", "width": 2000, "height": 1500 },
  "markers": [
    {
      "flag":   "inc_mid_thalamus",
      "area":   "Thalamus",
      "text":   "Thalamus",
      "target": { "x": 0.3617, "y": 0.5241 },
      "label":  { "x": 0.3640, "y": 0.8002 }
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `flag` | Which `inc_*` flag controls visibility. Empty string = always visible. |
| `area` | Canonical structure name. |
| `text` | Display text on the label pill — may differ from `area` for disambiguation. |
| `target` | Dot position on the anatomy, as fractions of image width/height. |
| `label` | Label pill position, same coordinate space. |

Fractional coordinates mean the same data drives the atlas at any rendered size.

---

## Answer matching

Free-text answers are checked in two layers.

### Handled automatically

The normalizer folds variation nobody should have to enumerate:

| Variation | Example |
|---|---|
| Case and whitespace | `THIRD  Ventricle` |
| Articles and prepositions | `the third ventricle`, `aqueduct of Sylvius` |
| Punctuation | `chiasm.` |
| Ordinals — word, digit, Roman | `third` = `3rd` = `III` = `3` |
| English plurals | `bodies` = `body` |
| Latin plurals | `colliculi` = `colliculus`, `gyri` = `gyrus`, `nuclei` = `nucleus` |
| Word order | `third ventricle` = `ventricle III` |

Word order is handled by comparing the sorted token set as a fallback, which also
catches Latin-style inversions like `gyrus cinguli`.

### Listed per structure

Genuine synonyms — different established names for the same structure — go in an
`accept` array in the view's data file:

```json
{
  "name": "Cerebral Aqueduct",
  "accept": ["aqueduct of sylvius", "sylvian aqueduct",
             "mesencephalic aqueduct", "aqueduct"]
}
```

Entries are normalized the same way as student input, so `accept` only needs the
base form — no need to list `aqueducts` or `Aqueduct of Sylvius` separately.

**Veterinary nomenclature matters here.** Sheep anatomy often uses rostral/caudal
where human anatomy uses superior/inferior, so `rostral colliculus` is accepted for
Superior Colliculus and `caudal commissure` for Posterior Commissure.

### Deciding what to accept

This is a pedagogical call, not a technical one. Accepting `primary motor cortex`
for Precentral Gyrus is defensible — same tissue — but it changes what the question
tests. Review the `accept` lists rather than inheriting them.

The student-facing **Count mine as correct** button is the backstop: string matching
can't anticipate every acceptable answer, so the student can override a wrong verdict.
If a particular override keeps coming up, that's a signal to add the synonym.

### Checking for collisions

After editing `accept` lists, make sure no two structures can claim the same answer:

```js
// in the browser console on quiz.html
const d = await (await fetch('data/midsagittal.json')).json();
// ...compare normalized forms across all structures
```

The 25-structure midsagittal set currently resolves to 94 accepted strings with no
collisions and no false positives against near-miss pairs (superior vs. inferior
colliculus, pre- vs. postcentral gyrus, thalamus vs. hypothalamus).
