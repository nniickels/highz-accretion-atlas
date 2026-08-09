# v1 Uncertainty Propagation

This document describes the v1 uncertainty-aware growth diagnostics generated
by `scripts/generate_v1_uncertainty_rankings.py`.

## Command

Run from the repository root after generating the processed catalogue, v1
evaluation CSVs, and point-estimate ranking table:

```powershell
python scripts/generate_v1_uncertainty_rankings.py
```

Optional deterministic controls:

```powershell
python scripts/generate_v1_uncertainty_rankings.py --n-samples 10000 --seed 20260808
```

The default run uses `10000` Monte Carlo samples per object and random seed
`20260808`.

## Sampling Model

For each v1 measurement row, the script samples `log_mbh_msun_std` using the
reported asymmetric errors:

- positive normal draws use `log_mbh_err_plus_std`
- negative normal draws use `log_mbh_err_minus_std`
- if only one side is available, it is used for both sides
- if neither side is available, the row is treated as a point estimate
- negative reported uncertainties are treated as invalid input

This is a split-normal approximation in log-mass space. It captures the reported
asymmetry without adding a heavy statistical dependency. It is not a full
posterior reconstruction.

The sampled distribution has 50% of draws on each side of the reported central
mass, so the median remains close to `log_mbh_msun_std` for large sample counts.
When the positive and negative errors differ, the mean can shift slightly and
the 16th/84th percentile distances need not be symmetric.

The output tables explicitly record the MBH uncertainty handling with:

- `log_mbh_err_plus_reported`
- `log_mbh_err_minus_reported`
- `log_mbh_sigma_plus_used`
- `log_mbh_sigma_minus_used`
- `mbh_uncertainty_mode`

Allowed `mbh_uncertainty_mode` values are:

- `asymmetric`: both sides are reported and differ
- `symmetric_reported`: both sides are reported and equal within numerical
  tolerance
- `symmetric_from_plus`: only the positive error is reported and reused for both
  sides
- `symmetric_from_minus`: only the negative error is reported and reused for
  both sides
- `point_estimate_no_reported_mbh_error`: neither side is reported, so the row
  is sampled as a deterministic point estimate

Each sampled mass distribution is evaluated under three systematic scenarios:

- `baseline`: reported black-hole mass
- `mbh_minus_0p3dex`: sampled mass shifted down by 0.3 dex
- `mbh_plus_0p3dex`: sampled mass shifted up by 0.3 dex

All v1 uncertainty diagnostics currently use:

- `z_seed = 30`
- `epsilon = 0.1`
- `merger_boost = 1`
- the same Planck-style cosmology used in `src.models`

## Outputs

| Output | Rows | Meaning |
| --- | --- | --- |
| `results/v1_uncertainty_required_fedd_summary.csv` | one row per object, scenario, and fixed seed mass | Required lifetime-average `f_Edd` percentiles and `P(required f_Edd > 1)`. |
| `results/v1_uncertainty_required_mseed_summary.csv` | one row per object, scenario, and fixed growth history | Required seed-mass percentiles in `log10(Msun)` and `Msun`, plus probabilities above `1e5` and `1e6 Msun`. |
| `results/v1_uncertainty_aware_ranking_table.csv` | one row per current v1 measurement/object | Point-estimate ranking table plus uncertainty percentiles, threshold probabilities, and uncertainty-aware ranks. |

Percentile summaries include 5th, 16th, 50th, 84th, and 95th percentiles.
Seed-mass summaries include both `required_log_mseed_*` and
`required_mseed_msun_*` percentile columns.

## Threshold Probabilities

The required-`f_Edd` summary includes:

- `p_required_fedd_gt1`
- `prob_required_fedd_gt_1`

The required-seed summary includes:

- `p_required_mseed_gt1e5`
- `p_required_mseed_gt1e6`
- `prob_required_mseed_gt_1e5`
- `prob_required_mseed_gt_1e6`

The `prob_*` names are the preferred reader-facing names. The shorter `p_*`
names are retained for backwards compatibility with earlier v1 outputs.

The uncertainty-aware ranking table exposes these probabilities in wide form.
Preferred examples are:

- `prob_required_fedd_seed1e2_gt_1_baseline`
- `prob_required_mseed_fedd0p3_gt_1e5_baseline`
- `prob_required_mseed_fedd0p3_gt_1e6_baseline`

Earlier-compatible aliases are also retained, for example:

- `p_req_fedd_seed1e2_gt1_baseline`
- `p_req_log_mseed_fedd0p3_gt1e5_baseline`
- `p_req_log_mseed_fedd0p3_gt1e6_baseline`

Scenario suffixes label the systematic mass-shift state. Statistical MBH
sampling is not blended across systematic scenarios: `baseline`,
`mbh_minus_0p3dex`, and `mbh_plus_0p3dex` are written as separate columns and
rows.

## Current v1 Ranking Impact

The uncertainty-aware ranking preserves the main high-leverage v1 group, but it
changes how confidently the objects should be described.

| Object | Quality | Uncertainty tier | Key probabilities under baseline |
| --- | --- | --- | --- |
| `GN-38509` | robust | `likely_high_pressure` | `prob_required_fedd_seed1e2_gt_1_baseline=0.85`; `prob_required_mseed_fedd0p3_gt_1e6_baseline=0.97`. |
| `GS-20057765` | tentative | `likely_high_pressure` | `prob_required_fedd_seed1e2_gt_1_baseline=0.98`; `prob_required_mseed_fedd0p3_gt_1e6_baseline=0.59`. |
| `GS-20030333` | tentative | `likely_high_pressure` | `prob_required_fedd_seed1e2_gt_1_baseline=0.91`; `prob_required_mseed_fedd0p3_gt_1e6_baseline=0.48`. |
| `GS-164055` | tentative | `likely_high_pressure` | `prob_required_fedd_seed1e2_gt_1_baseline=0.70`; `prob_required_mseed_fedd0p3_gt_1e6_baseline=0.52`. |
| `GN-4685` | tentative | `likely_high_pressure` | `prob_required_fedd_seed1e2_gt_1_baseline=0.58`; `prob_required_mseed_fedd0p3_gt_1e6_baseline=0.31`. |
| `GN-954` | robust | `possible_high_pressure` | `prob_required_fedd_seed1e2_gt_1_baseline=0.13`; `prob_required_mseed_fedd0p3_gt_1e6_baseline=0.36`. |

Interpretation:

- `GN-38509` remains the strongest robust v1 growth-pressure object.
- `GS-20057765` remains the strongest tentative high-redshift follow-up target.
- `GS-20030333` and `GS-164055` stay high leverage but are caveated by missing
  host stellar masses and tentative status.
- `GN-4685` stays in the likely high-pressure group probabilistically, but its
  point-estimate pressure is close to the threshold and remains
  systematics-sensitive.
- `GN-954` is better described as a robust comparison/systematics object than as
  a likely high-pressure object under the baseline uncertainty model.

These rankings remain triage products. High threshold probability means an
object is worth follow-up or modeling attention under stated assumptions; it
does not prove a formation channel.
