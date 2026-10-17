# Manuscript results

These tables and figures support the manuscript's 223-object primary and
238-object expanded samples. The expanded sample contains every primary object;
existing table fields call it `exploratory`.

## Tables

| File in `tables/` | Contents |
| --- | --- |
| `publication_object_selection.csv` | Sample membership after evidence and identity exclusions. |
| `identity_exclusion_sensitivity.csv` | Effect of identity exclusions with the evidence rules held fixed. |
| `mass_offset_sensitivity.csv`, `mass_offset_object_sensitivity.csv` | Results after uniform mass shifts of −0.5, −0.3, 0, +0.3, and +0.5 dex. |
| `target_robustness.csv` | Eleven primary objects above the reference threshold, with source caveats and mass-shift tests. |
| `source_inventory.csv` | Counts of measurements, eligible mass measurements, and adopted primary objects for 37 source families. |
| `matched_literature_comparison.csv` | Four named Dayal matches, separating measurement changes from starting-time changes. |
| `external_direct_mass_comparison.csv` | A2744-QSO1 virial and dynamical masses with normal log-mass error propagation. |
| `publication_baccus_revision_comparison.csv`, `publication_baccus_revision_summary.csv` | Effect of substituting published Baccus values after identity exclusions. |
| `calibration_sensitivity.csv` | Separate two-object test of added calibration scatter. |

A dex is a unit of base-10 logarithm; a 0.5-dex mass change is a factor of about
3.2. Mass-shift tests reuse the same object-specific random draws. They test
assumed biases rather than measure them. The −1 and −2 dex tests in
`target_robustness.csv` are also assumed shifts. Objects without reported mass
errors have no probability estimates. The external dynamical mass does not
replace the catalogue value, and the four Dayal matches are not a full crossmatch.

## Generate and verify

From the repository root, after [setup](../../README.md#getting-started):

```bash
.venv/bin/python -m src.internal.publication_selection --write
.venv/bin/python -m src.internal.publication_selection
.venv/bin/python -m src.internal.publication_figures
.venv/bin/python -m src.internal.publication_figures --verify
```

The first pair writes and checks tables; the second exports and checks the six
principal PNG/PDF figure pairs. The [publication inputs](../../data/publication/README.md)
record sample rules and source locations. Notebooks 01 and 02 generate tables
and figures; notebooks 03 and 04 compare and verify outputs. The two additional
figure pairs use `src.internal.plot_seed_timing_comparison` and
`src.internal.plot_early_start`. See the [reproduction guide](../../docs/guides/reproducibility.md)
for the independent baseline and comparison tolerances.

## Figure interpretation

Numerical plots use the publication samples. The coverage panel also shows
excluded identities and objects without eligible masses.

The growth-track display uses seed masses of 10², 10⁴, and 10⁵ solar masses,
four fixed efficiencies, and Eddington ratios from 0.1 to 2.0 in steps of 0.1.
For each seed/efficiency pair, it selects two ratios whose tracks pass within
0.5 dex of the most primary objects, requiring at least five objects. It uses
merger multipliers B=1 and B=2, with ties settled by median absolute residual
and then ratio. Bands connect those fixed multipliers; they are not uncertainty
intervals. Objects are not removed to improve the display, and omitted tracks
are not excluded physical histories.

The early-start comparison includes radiation in cosmic ages for both starting
redshifts, 30 and 3400. It uses H0=67.3 km/s/Mpc, Omega_m=0.315,
Omega_r=Omega_m/3401, and Omega_Lambda=1−Omega_m−Omega_r. H0 is the Hubble constant; the Omega values are the density fractions of matter,
radiation, and dark energy. The main catalogue retains the matter-plus-Lambda
approximation. Run
`.venv/bin/python -m src.internal.check_early_start` to check the 98.73 Myr time
difference, 0.858 dex mass shift at efficiency 0.1 and Eddington ratio 1, and
cosmology sensitivity. This comparison assumes growth and available gas; it does
not establish seed formation.

## Calibration test

`calibration_sensitivity.csv` adds independent Gaussian scatter of 0.5 dex to
the symmetric reported log-mass errors for RUBIES-EGS-55604 and
J0910_2028_12910. It gives exact probabilities at mass offsets 0 and −0.5 dex.
This is an assumption test for two objects, not a change to catalogue masses
or a common error model for the sample. It is generated and verified with the
other publication tables. Full assumptions and checks are in the
[reproduction guide](../../docs/guides/reproducibility.md#apss-calibration-sensitivity).

## Manuscript files

The public [draft PDF](../../paper/early_giants_draft.pdf) and
[Overleaf ZIP](../../paper/early_giants_overleaf.zip) are in `paper/`.
The original local source, `paper/main.tex`, is excluded from Git. Compiling that
source and running `src.internal.package_overleaf` updates the public package;
its `--verify` mode checks the package without local sources or LaTeX.
The [Ap&SS submission package](../../paper/apss/README.md) is tracked separately.
Analysis regeneration does not edit manuscript prose or compile PDFs.
