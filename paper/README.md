# Manuscript draft

The `paper/` folder contains the current working manuscript draft and is kept
for reference while the catalogue and analysis continue to evolve.
`highz_accretion_atlas_v3.tex` is the editable LaTeX source. It references the
canonical v3 figures in `results/v3/figures/`.

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error highz_accretion_atlas_v3.tex
pdflatex -interaction=nonstopmode -halt-on-error highz_accretion_atlas_v3.tex
```

Tectonic is an equivalent local option when `pdflatex` is unavailable:

```bash
tectonic --keep-logs highz_accretion_atlas_v3.tex
```

The compiled draft is `highz_accretion_atlas_v3.pdf`. LaTeX intermediate files
are ignored.
