# Manuscript results

Reproducible numerical tables and figures supporting the manuscript are retained
here. The manuscript text and bibliography are edited separately in Overleaf.

## Tables

`tables/` contains:

- `publication_object_selection.csv`: full membership mask, with 220 primary and
  234 expanded-sample objects after evidence and identity exclusions.
- `identity_exclusion_sensitivity.csv`: comparisons before and after identity exclusions,
  holding the evidence policy fixed.
- `mass_offset_sensitivity.csv` and `mass_offset_object_sensitivity.csv`: coherent
  mass shifts of −0.5, −0.3, 0, +0.3 and +0.5 dex. These translate the same
  identifier-seeded reported-error draws; they do not infer calibration bias or
  marginalize over systematics. Missing-error objects retain unavailable probabilities.
- `target_robustness.csv`: the eight primary objects above the reference growth
  threshold, including source caveats and offset scenarios. The −1 and −2 dex
  values are directional scenarios, not inferred corrections.
- `source_inventory.csv`: 32 source families, with separate measurement,
  mass-eligible measurement and primary preferred-object counts.
- `matched_literature_comparison.csv`: four named Dayal matches with measurement
  and seed-start-time changes separated. This is not a full catalogue crossmatch.
- `external_direct_mass_comparison.csv`: A2744-QSO1's catalogue virial estimate
  and external dynamical estimate, with exact normal log-mass error propagation.
  The external estimate is not substituted into the canonical catalogue.
- `publication_baccus_revision_comparison.csv` and
  `publication_baccus_revision_summary.csv`: published-value substitutions after
  identity exclusions. Primary and expanded samples are nested, not independent.

Inputs and source locators are in [data/publication](../../data/publication/README.md).
Regenerate with `python -m src.internal.publication_selection --write` (notebook 01),
and verify with the same command without `--write` (notebook 04).

## Figures

`figures/` contains PNG and PDF exports. The six principal figures are generated
by `python -m src.internal.publication_figures`; verify them with `--verify`.
The seed-timing and optional early-start comparisons use
`src.internal.plot_seed_timing_comparison` and `src.internal.plot_early_start`.
Notebook 02 generates all eight pairs; notebook 03 compares them to the baseline.

Numerical publication plots use the conservative selection. The coverage panel
also accounts for excluded identities and objects without eligible masses.
The primary sample is nested within the expanded sample (called `exploratory`
in existing table fields). Objects without
reported mass errors are not treated as having certain masses.

Growth-track display selection uses seed masses 10², 10⁴ and 10⁵ solar masses,
the four stated constant efficiencies, and rates from 0.1 to 2.0 in steps of 0.1.
For each seed/efficiency, it selects two rates with the most primary objects
within 0.5 dex of either the B=1 or B=2 track (at least five objects), breaking
ties by median absolute residual and then rate. Bands connect the two fixed
merger multipliers; they are not credible intervals. No objects are removed to
optimize the display, and omitted curves are not ruled out by this selection.

The early-start comparison includes radiation for both starting redshifts,
30 and 3400. It uses H0 = 67.3 km/s/Mpc, Omega_m = 0.315,
Omega_r = Omega_m / 3401, and Omega_Lambda = 1 - Omega_m - Omega_r.
The main catalogue retains its matter-plus-Lambda approximation.
Run `python -m src.internal.check_early_start` to reproduce the supplement's
98.73 Myr time difference and 0.858 dex mass shift at efficiency 0.1 and
Eddington ratio 1, plus the main paper's cosmology-sensitivity comparison.
This calculation assumes an accretion history; it does not establish a
seed-formation mechanism or sufficient gas supply.
Full-catalogue figures remain in `results/v1/`, `results/v2/`, and `results/v3/`.
See the [reproduction guide](../../docs/guides/reproducibility.md) for comparison tolerances.
