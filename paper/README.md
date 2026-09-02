# Paper package

`highz_accretion_atlas_v3.tex` is the final manuscript source. It references
the canonical v3 figures in `results/v3/figures/`.

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error highz_accretion_atlas_v3.tex
pdflatex -interaction=nonstopmode -halt-on-error highz_accretion_atlas_v3.tex
```

Tectonic is an equivalent local option when `pdflatex` is unavailable:

```bash
tectonic --keep-logs highz_accretion_atlas_v3.tex
```

The final compiled manuscript is `highz_accretion_atlas_v3.pdf`. LaTeX
intermediate files are ignored.
