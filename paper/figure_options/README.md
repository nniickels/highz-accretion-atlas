# Growth-track layout options

Option C is adopted as the manuscript growth-track figure; A, B and D remain review alternatives. All use the conservative 224 primary plus 10 exploratory-only objects, not the broader full-catalogue atlas. Objects without eligible numerical masses and identity exclusions are not plotted. All displayed points lie within the axes. The complete original atlas remains in `results/v3/figures/`.

- **A — reference seed panels:** three nearby rates per seed, fixed efficiency 0.1 and B=1. Clearest comparison of rates at fixed seed mass.
- **B — minimal reference:** one nearby rate per seed. Simplest overview, but hides the range of possible histories.
- **C — full assumption efficiency panels:** four efficiency cases; two nearby rates per seed/efficiency, and B=1–2 bands. Recommended for comparing the fuller assumptions.
- **D — full assumption seed panels:** the same scenarios as C, grouped by seed mass; more information per panel.

The word “full” refers to varying seed mass, efficiency, rate and merger multiplier, not showing every original curve. These options use z_seed=30; they do not reproduce the supplementary z_seed=3400 extrapolation.

## Explicit display selection

Candidate seed masses: 10^2, 10^4, 10^5 solar masses. Candidate fixed efficiencies: 0.1 and the ideal Kerr values for spins -1, 0, +1. Candidate average luminosity-based Eddington ratios: 0.1 through 2.0 in steps of 0.1 (denser than the original 0.3, 1, 2 grid). All are constant-efficiency histories, including rates above one; no supercritical efficiency correction is applied in these growth tracks.

A nearby primary object has an absolute predicted-minus-observed log-mass difference <=0.5 dex at its observed redshift. This is an illustrative display tolerance, not an uncertainty interval or goodness-of-fit statistic. For C/D proximity is the smaller distance to B=1 or B=2; the filled band simply connects those fixed mass multipliers. It is not a credible interval. A/B score B=1 alone.

A retains the three candidate rates with the most nearby primary objects per seed; B takes the first. C/D retain two per seed/efficiency. At least five nearby primary objects are required. Ties use smaller median absolute residual, then smaller rate. The common sample at z~4–6 dominates this choice; it does not optimize the high-redshift tail. Excluding other tracks from a display is not evidence against their physical scenarios, and these cross-sectional data do not fit individual evolutionary histories. No data points are removed to make curves appear closer.

`track_selection.csv` records all 240 full-grid candidates, proximity counts, residuals and selection flags. `reference_selection.csv` records the displayed reference choices. Bands and exact rates are labelled in the figures.

Reproduce from the repository root:

```sh
MPLCONFIGDIR=/tmp/highz-mpl .venv/bin/python -m src.internal.growth_track_options
```

## Publication refinement

All four previews now extend from z=11.5 to z=3 so markers at z=4 are not clipped. No objects or selected scenarios changed. Six scientific targets are outlined: GN-z11 (exploratory), CEERS-1019, GS-20057765, UNCOVER-20466, COSMOS3D-13852 and RUBIES-EGS-55604. Full names appear once per multipanel figure, with the same targets highlighted in every panel; B names all six.

Option C uses legends outside the plotting area, shared axes and panel letters. Both 300-dpi PNG and vector SVG are supplied; option C is adopted in the manuscript and Overleaf. The second footer line has been removed; selection and band definitions are documented in the manuscript text and caption.
