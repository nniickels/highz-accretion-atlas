# CUPC poster sources and reproduction

The editable text/layout sources and delivered decks are tracked at the repository root:

- `CUPC_Poster_portrait_36x48.pptx`: the current single-slide portrait poster.
- `CUPC_Poster.pptx`: the current single-slide landscape poster.

The landscape deck is 48 × 36 inches. These files retain native text and the
Office math equation; scientific plots are embedded PNGs. PowerPoint is needed
for a final native export/print inspection. The portable rebuild does not need
Codex, Node.js, an artifact tool, temporary authoring directories, or absolute
machine paths.

## Scientific plot assets

Install `requirements/core.txt` under Python 3.12, then run from the repository root:

```bash
.venv/bin/python posters/render_figures.py --output-dir /tmp/cupc-portrait-figures
```

This regenerates the portrait plot assets from the publication selection,
v3 ranking/uncertainty tables, mass-offset sensitivity table, v4 seed-onset
inputs, and the repository growth law. It never writes analysis tables,
canonical manuscript/v4 figures, inventories, or manifests.

The input manifest also pins `external_direct_mass_comparison.csv`, which
supplies the independent A2744-QSO1 mass comparison and its uncertainty range.

`inputs.json` pins the reviewed scientific inputs by SHA-256. Code and non-CSV inputs remain byte-exact. A regenerated CSV with different
serialization is accepted only when `HIGHZ_BASELINE_ROOT` identifies an
independent baseline whose file matches the pinned hash, and the shared
scientific CSV comparison passes. Changed values, text, row/column membership,
a changed baseline, and self-comparison are rejected. Rendering stops if these
checks fail. Review the corresponding poster numbers and conclusions
before deliberately updating this separate poster manifest. Do not refresh the
canonical analysis manifests to make a poster build pass.

## Landscape layout

```bash
.venv/bin/python posters/build_landscape.py --output /tmp/cupc-landscape-rebuilt.pptx
```

Choose an unused output path. The builder reads the committed portrait deck for
current text, equation, styles and plot assets, and the committed landscape deck
for its header artwork placements. It reflows the final slide and regenerates
its shorter uncertainty canvas from the pinned inputs. Single-slide files and older multi-slide decks are supported without changing
the slide count. Text and native-equation checks reject accidental content loss. It leaves both source decks untouched.

The PPTX files are authoritative editable layout/text inputs, not outputs of the
00–04 science notebooks. This command reproduces the current landscape from
those inputs; it is not a text-to-poster generator for an arbitrary future
layout. New shapes or major copy changes require reviewing the placement map
and visually inspecting the rebuilt slide. Archive timestamps are fixed, but
PowerPoint metadata/XML serialization and platform font rendering mean that
byte-identical PPTX reproduction across editors/platforms is not promised.
The regression test checks content preservation and the plot pixels using the
same per-channel tolerance as the scientific image gate.

## Analysis reproduction stays separate

The poster workflow does not alter the scope or tolerances of notebooks 00–04,
publication figure verification, or v4 verification. Follow
[`docs/guides/reproducibility.md`](../docs/guides/reproducibility.md) for the
independent baseline/execution workflow. Temporary `.cupc-*` authoring folders
are ignored; the portable source scripts and finished posters are committed.

## Editorial conventions

Completed Methods actions use past tense; scientific definitions and general
limitations remain in present tense. Quantitative counts, model parameters,
ratios, percentages and ranges use numerals, including counts below 10. Large
quantities use thousands separators (for example, 3,400); years, catalogue
identifiers and scientific powers retain their conventional notation. Prose
uses “above 1” consistently for the growth threshold; mathematical comparisons
include a space after the relation sign.

The October 2026 CI notebook failure came from byte-exact poster input checks
after otherwise valid CSV regeneration. The poster guard now uses the existing
scientific comparison contract for CSVs against an independently pinned
baseline; no input hashes or comparison tolerances were relaxed or refreshed.

The current editions use the same Methods text, including the model-testing
step after the reference assumptions. Body text is 33 pt, section headings
50 pt, and captions 24 pt in each edition; mathematical subscripts use smaller
text deliberately. The portrait uncertainty canvas is 16 × 8.6 inches, with
24 pt labels, to provide space below the Results prose. The landscape canvas
remains 14.8 × 7.6 inches. These canvas choices are encoded in the renderer and
checked against the embedded plots by the regression suite.
