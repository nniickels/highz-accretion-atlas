# Manuscript draft

**Conservative manuscript scope:** all six records linked to the three open
identity groups are excluded from manuscript inference. The primary sample has
224 objects; the exploratory numerical sample has 234. Headline threshold
counts and top-five ordering are unchanged in the tested scenarios.
This addresses the analysis dependency, not physical identity resolution or a
final unique-object census. The strict identity gate remains open.

The explicit policy is `identity_exclusions.json`. Reproduce the stored selection
and inclusion/exclusion sensitivity tables with:

```bash
.venv/bin/python -m src.internal.publication_selection --write
.venv/bin/python -m src.internal.publication_selection
```

The second command verifies without rewriting; it is also part of notebook 04.
The five manuscript figures in `paper/figures/` use the conservative publication
samples. Notebook 02 regenerates them and notebook 04 compares regenerated
pixels (maximum channel difference 3, identical dimensions). The original
full-catalogue figures remain in `results/v3/figures/`.


The `paper/` folder contains the current working manuscript draft and is kept
for reference while the catalogue and analysis continue to evolve.
`highz_accretion_atlas_v3.tex` is the editable LaTeX source. It references the
canonical v3 figures in `results/v3/figures/`.

```bash
cd paper
SOURCE_DATE_EPOCH=1788393600 pdflatex -interaction=nonstopmode -halt-on-error highz_accretion_atlas_v3.tex
SOURCE_DATE_EPOCH=1788393600 pdflatex -interaction=nonstopmode -halt-on-error highz_accretion_atlas_v3.tex
```

Tectonic is an equivalent local option when `pdflatex` is unavailable:

```bash
SOURCE_DATE_EPOCH=1788393600 tectonic --keep-logs highz_accretion_atlas_v3.tex
```

The compiled draft is `highz_accretion_atlas_v3.pdf`. LaTeX intermediate files
are ignored. The fixed epoch is 2026-09-03 00:00:00 UTC and makes repeat builds
with the same compiler byte-reproducible.

The [scientific/editorial pass record](scientific-editorial-review.md) lists
checked claims, corrections, and remaining submission work.
