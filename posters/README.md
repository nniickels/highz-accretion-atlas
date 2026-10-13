# CUPC poster sources and reproduction

The editable text/layout sources and delivered decks are tracked at the repository root:

- `CUPC_Poster_portrait_36x48.pptx`: the current single-slide portrait poster.
- `CUPC_Poster.pptx`: the landscape deck; slide 2 contains the current poster and slide 1 is retained as the older version.

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

`inputs.json` pins the reviewed scientific inputs by SHA-256. Rendering stops
if an input changes. Review the corresponding poster numbers and conclusions
before deliberately updating this separate poster manifest. Do not refresh the
canonical analysis manifests to make a poster build pass.

## Landscape layout

```bash
.venv/bin/python posters/build_landscape.py --output /tmp/cupc-landscape-rebuilt.pptx
```

Choose an unused output path. The builder reads the committed portrait deck for
current text, equation, styles and plot assets, and the committed landscape deck
for its slide 1 and header artwork placements. It reflows slide 2 and regenerates
its shorter uncertainty canvas from the pinned inputs. Text and native-equation
checks reject accidental content loss. It leaves both source decks untouched.

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
