# Manuscript draft

**Scientific hold:** the [identity audit](../docs/source-notes/redshift-identity-audit.md)
found three duplicate groups and two unresolved close-neighbour groups. Object
counts and affected summaries need reconciliation before submission.

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
