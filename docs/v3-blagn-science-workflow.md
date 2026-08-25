# v3 Expanded BLAGN Science Workflow

This workflow evaluates the combined JADES and Taylor CEERS/RUBIES broad-line
catalogue without modifying frozen v1 inputs/baselines or v2 rankings/figures.
The products are observational-triage and growth-pressure summaries under
explicit assumptions. They do not prove a black-hole seed channel.

## Reproduction

Run from the repository root:

```powershell
python -m scripts.process_v3_blagn
python -m scripts.generate_v3_blagn_science --n-samples 10000 --seed 20260808
$env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests
```

The first command rebuilds the separate v3 measurement and physical-object
catalogues. The second writes only files beginning with `v3_blagn_` in
`results/`. It does not regenerate science figures.

## Product inventory

| Product | Measurement view | Physical-object view |
| --- | --- | --- |
| Point evaluation | `v3_blagn_measurement_evaluation.csv` | `v3_blagn_physical_object_evaluation.csv` |
| Point ranking | `v3_blagn_measurement_point_ranking.csv` | `v3_blagn_physical_object_point_ranking.csv` |
| Uncertainty required fEdd | `v3_blagn_measurement_uncertainty_fedd.csv` | `v3_blagn_physical_object_uncertainty_fedd.csv` |
| Uncertainty required seed | `v3_blagn_measurement_uncertainty_mseed.csv` | `v3_blagn_physical_object_uncertainty_mseed.csv` |
| Uncertainty ranking | `v3_blagn_measurement_uncertainty_ranking.csv` | `v3_blagn_physical_object_uncertainty_ranking.csv` |

Two long-form descriptive summaries are also written:

- `v3_blagn_catalogue_summary.csv`
- `v3_blagn_growth_summary.csv`

The catalogue summary separates measurement and physical-object counts and
provides source, survey, field, survey/field, and LRD-phenotype strata. Overall
mixed-source rows are explicitly marked descriptive-only because JADES and
CEERS/RUBIES do not share one selection function or completeness model.
Physical-object source/survey/field strata follow the preferred measurement's
metadata; `n_measurements_represented` can include linked alternate observations
from another program, as for CEERS-2782/RUBIES-EGS-50052.

## Measurement and object views

The measurement view retains all 60 measurements at `z >= 4`. The object view
contains 59 physical objects and selects exactly one preferred measurement
per object using `data/crossmatch/v3_measurement_object_links.csv`.

CEERS-2782 and RUBIES-EGS-50052 remain separate literature measurements but map
to `HZA-CEERS-2782`. The object view uses RUBIES-EGS-50052 because Taylor et al.
adopt its higher-S/N spectrum; the CEERS observation has severe spatially
dependent slit loss. The selected row retains the paper's possible-outflow
caveat. `n_measurements`, `available_measurement_ids`, and the preference reason
make this choice auditable.

## Growth assumptions and systematic scenarios

The point and uncertainty products retain the v1 baseline:

- seed redshift `z_seed=30`
- radiative efficiency `epsilon=0.1`
- merger boost `1` (no merger mass boost)
- the flat Planck-style cosmology in `src.models`
- fixed seed masses of `1e2`, `1e4`, and `1e5 Msun`
- fixed lifetime-average accretion histories `fEdd=0.3` and `fEdd=1`

Scenarios are separate rows and columns:

| Scenario | Scope | Meaning |
| --- | --- | --- |
| `baseline` | all sources | Reported MBH |
| `mbh_minus_0p3dex`, `mbh_plus_0p3dex` | all sources | Existing atlas comparison shifts |
| `taylor_virial_minus_0p5dex`, `taylor_virial_plus_0p5dex` | Taylor only | Sensitivity to the paper's approximate 0.5 dex virial-calibration systematic |

The Taylor shifts are sensitivity bounds, not an added Gaussian error. Each
uncertainty scenario first samples the reported asymmetric statistical MBH
errors with the established equal-side two-piece normal approximation (the
legacy machine-readable label is `split-normal-in-log-mbh`) and then applies
one fixed shift.
Columns explicitly record that statistical and systematic terms were not
combined. The deterministic seed is resolved per measurement ID, so a preferred
measurement has identical draws in the measurement and physical-object views.

## Missing diagnostics and ranking semantics

Taylor Table 1 does not publish Mstar, Lbol, or Eddington ratio. These are marked
`unavailable_not_published_in_taylor_table1` and are not used to reduce
measurement confidence, growth pressure, or follow-up priority. Host-ratio and
current-accretion diagnostics remain unavailable rather than inferred.

Growth-pressure ranks use only redshift, MBH, and the stated analytic growth
assumptions. Measurement confidence is separate and responds to evidence or
interpretive caveats, including tentative stack-supported JADES detections,
source-value inconsistencies, possible outflow contamination, alternative
non-AGN broadening, and severe slit loss. This prevents missing optional
quantities from masquerading as poor measurements.

`rank_growth_pressure` orders point-estimate pressure.
`rank_uncertainty_pressure` combines baseline threshold probabilities with the
point score. `rank_followup_priority` keeps measurement caveats visible. None of
these ranks is a posterior probability for a formation channel.

## Current release anchors

- 60 measurement ranks and 59 physical-object ranks.
- Point evaluations: 254 measurement rows and 249 physical-object rows.
- Uncertainty required-fEdd summaries: 762 measurement rows and 747 object rows.
- Uncertainty required-seed summaries: 508 measurement rows and 498 object rows.
- Every uncertainty row uses 10,000 draws with seed 20260808 in the committed
  release.
- The first three physical-object point and uncertainty ranks are GN-38509,
  GS-20057765, and RUBIES-EGS-49140. The third object remains explicitly
  caveated because the source discusses an alternative compact-galaxy broadening
  interpretation; its baseline high-pressure label is not robust to the Taylor
  `-0.5 dex` sensitivity.

## Descriptive coverage comparison

The 23-object v1 sample spans `z=4.133-8.913` and
`log(MBH/Msun)=6.06-8.57`. The 36 Taylor physical objects retained at `z >= 4`
span `z=4.000-6.778` and `log(MBH/Msun)=6.43-8.30`. The combined object view has
59 objects, retains the v1 extrema, and substantially fills the intermediate
`z~4-6.8` mass-redshift plane.

Four Taylor objects enter the top ten point and uncertainty rankings. The two
highest-ranked v1 objects remain first and second. Taylor adds one baseline-high
object, RUBIES-EGS-49140, plus several possible-pressure comparison targets.
These counts are descriptive: source- and LRD-stratified rows must not be read as
population fractions without source-specific completeness and selection models.
