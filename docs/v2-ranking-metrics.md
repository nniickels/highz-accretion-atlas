# v2 Object-Ranking Metrics (v1 Catalogue)

This document defines the v2 ranking design, evaluated on the frozen v1
catalogue, and the
implemented `results/v2_object_ranking_table.csv` table.

## Ranking Philosophy

The atlas ranking should answer two different questions without mixing them:

1. **Physical growth pressure:** how demanding is it to grow the reported black
   hole mass by the observed redshift under transparent seed, accretion,
   efficiency, and merger assumptions?
2. **Measurement confidence and caveats:** how much should the row be trusted
   as an observational constraint, and which follow-up measurement would most
   change the interpretation?

The v2 table should therefore keep physical metrics, robustness metrics, and
measurement-quality fields as separate columns. A tentative object can have high
physical leverage, but it should not be described with the same confidence as a
robust object. Conversely, a robust object with moderate growth pressure can be
valuable as a comparison anchor.

The v2 ranking is measurement-level because the v1 catalogue has one row per
source-paper measurement. The v3 workflow adds separate measurement- and
physical-object-level rankings through stable `physical_object_id` values.

## Baseline Assumptions

Unless a column name states otherwise, v2 ranking metrics use:

- `z_seed = 30`
- `epsilon = 0.1`
- `merger_boost = 1`
- catalogue baseline `log_mbh_msun_std`
- Planck-style flat Lambda-CDM cosmology already used by `src.models`

The baseline assumptions are a reference frame, not a claim that every object
followed this exact history.

The implemented baseline ranking columns are selected from the existing result
tables with these filters:

- `results/v1_required_fedd_by_seed_mass.csv`:
  `interpretation_variant=baseline`,
  `fedd_requirement_config=eps0p1_no_merger_boost`, and
  `seed_mass_assumption` in `seed_1e2_msun`, `seed_1e4_msun`, and
  `seed_1e5_msun`.
- `results/v1_required_mseed_by_growth_assumption.csv`:
  `interpretation_variant=baseline` and `growth_config` in
  `fedd0p3_eps0p1_no_merger_boost` and
  `fedd1_eps0p1_no_merger_boost`.
- The simple robustness columns use the same baseline efficiency and merger
  assumptions, but with `interpretation_variant` equal to
  `mbh_minus_0p3dex` or `mbh_plus_0p3dex`.

## Required f_Edd Metrics

These columns measure the lifetime-average Eddington fraction needed to grow
from fixed seed masses to the reported black-hole mass.

| Column | Units | Definition | Interpretation |
| --- | --- | --- | --- |
| `req_fedd_seed1e2_z30_eps0p1_b1` | dimensionless | Required average `f_Edd` for `log10(M_seed/Msun)=2`. | Light-seed pressure metric. Values `> 1` are challenging for this exact fixed-seed scenario unless average accretion or other assumptions change. |
| `req_fedd_seed1e4_z30_eps0p1_b1` | dimensionless | Required average `f_Edd` for `log10(M_seed/Msun)=4`. | Intermediate/nominal heavy-seed-scale pressure metric. |
| `req_fedd_seed1e5_z30_eps0p1_b1` | dimensionless | Required average `f_Edd` for `log10(M_seed/Msun)=5`. | Nominal heavy-seed-scale pressure metric, not evidence that such a seed occurred. |
| `req_fedd_seed1e2_label` | none | Threshold label for the light-seed requirement. | Suggested labels: `sub_eddington`, `eddington_like`, `super_eddington`, `extreme`. |
| `req_fedd_seed1e4_label` | none | Threshold label for the `1e4 Msun` seed requirement. | Same labels. |
| `req_fedd_seed1e5_label` | none | Threshold label for the `1e5 Msun` seed requirement. | Same labels. |

Suggested v1 point-estimate thresholds:

- `sub_eddington`: `req_fedd < 0.3`
- `eddington_like`: `0.3 <= req_fedd <= 1.0`
- `super_eddington`: `1.0 < req_fedd <= 2.0`
- `extreme`: `req_fedd > 2.0`

The uncertainty-aware ranking table adds scenario-suffixed summaries, including:

- `req_fedd_seed1e2_p16_baseline`, `req_fedd_seed1e2_p50_baseline`,
  `req_fedd_seed1e2_p84_baseline`
- `prob_required_fedd_seed1e2_gt_1_baseline`
- analogous columns for `1e4` and `1e5 Msun` seeds
- analogous columns for `mbh_minus_0p3dex` and `mbh_plus_0p3dex`

## Required Seed-Mass Metrics

These columns measure the seed mass needed under fixed growth histories.

| Column | Units | Definition | Interpretation |
| --- | --- | --- | --- |
| `req_log_mseed_fedd0p3_z30_eps0p1_b1` | log10(Msun) | Required seed mass for `f_Edd=0.3`. | Gentle-growth pressure. Values above 6 exceed the nominal heavy-seed-scale reference band used in v1. |
| `req_mseed_fedd0p3_msun` | Msun | Linear version of the same metric. | Human-readable table value. |
| `req_mseed_fedd0p3_label` | none | Seed-scale label for `f_Edd=0.3`. | Suggested labels below. |
| `req_log_mseed_fedd1_z30_eps0p1_b1` | log10(Msun) | Required seed mass for `f_Edd=1`. | Eddington-limited growth reference. |
| `req_mseed_fedd1_msun` | Msun | Linear version of the same metric. | Human-readable table value. |
| `req_mseed_fedd1_label` | none | Seed-scale label for `f_Edd=1`. | Suggested labels below. |

Suggested seed-scale labels:

- `below_light_seed_scale`: `req_log_mseed < 1`
- `light_seed_scale`: `1 <= req_log_mseed <= 2`
- `intermediate_seed_scale`: `2 < req_log_mseed < 4`
- `heavy_seed_scale`: `4 <= req_log_mseed <= 6`
- `above_heavy_seed_scale`: `req_log_mseed > 6`

The uncertainty-aware ranking table adds scenario-suffixed summaries, including:

- `req_log_mseed_fedd0p3_p16_baseline`,
  `req_log_mseed_fedd0p3_p50_baseline`,
  `req_log_mseed_fedd0p3_p84_baseline`
- `prob_required_mseed_fedd0p3_gt_1e5_baseline`
- `prob_required_mseed_fedd0p3_gt_1e6_baseline`
- analogous columns for `f_Edd=1`
- analogous columns for `mbh_minus_0p3dex` and `mbh_plus_0p3dex`

## MBH/Mstar Tension

Host-mass tension is physically useful, but it is not the same quantity as
growth pressure. It should be carried as its own axis.

| Column | Units | Definition | Interpretation |
| --- | --- | --- | --- |
| `log_mbh_mstar_ratio` | dex | `log10(M_BH/Mstar)`. | Larger values are more black-hole dominated. |
| `mbh_mstar_ratio` | dimensionless | `10**log_mbh_mstar_ratio`. | Human-readable ratio. |
| `mbh_mstar_tension_label` | none | Threshold label for host-ratio tension. | Suggested labels below. |
| `missing_mstar_flag` | boolean | Existing catalogue missingness flag. | Missing host mass should not drop the object from growth-pressure ranking. |

Suggested host-ratio labels:

- `not_available`: host mass missing
- `low_or_typical`: `log_mbh_mstar_ratio < -2`
- `elevated`: `-2 <= log_mbh_mstar_ratio < -1`
- `extreme`: `log_mbh_mstar_ratio >= -1`

These thresholds are for atlas triage only. They should not be presented as a
calibrated evolutionary relation without a separate comparison model.

## Robustness and Caveat Fields

Robustness columns should describe whether the physical ranking survives simple
measurement-systematic changes. They should not overwrite the baseline values.

| Column | Units | Definition |
| --- | --- | --- |
| `req_fedd_seed1e2_mbh_minus0p3` | dimensionless | Light-seed required `f_Edd` after shifting `log_mbh` down by 0.3 dex. |
| `req_fedd_seed1e2_mbh_plus0p3` | dimensionless | Light-seed required `f_Edd` after shifting `log_mbh` up by 0.3 dex. |
| `req_log_mseed_fedd0p3_mbh_minus0p3` | log10(Msun) | Gentle-growth required seed after shifting `log_mbh` down by 0.3 dex. |
| `req_log_mseed_fedd0p3_mbh_plus0p3` | log10(Msun) | Gentle-growth required seed after shifting `log_mbh` up by 0.3 dex. |
| `light_seed_superedd_robust_mbh_minus0p3` | boolean | True if `req_fedd_seed1e2_mbh_minus0p3 > 1`. |
| `gentle_growth_above_heavy_robust_mbh_minus0p3` | boolean | True if `req_log_mseed_fedd0p3_mbh_minus0p3 > 6`. |
| `growth_pressure_robustness_label` | none | `robust_high`, `baseline_high_only`, `systematics_sensitive`, or `low`. |
| `quality_flag` | none | Existing catalogue flag, e.g. `robust` or `tentative`. |
| `detection_evidence` | none | Structured evidence class; `stack_supported_tentative_hbeta` distinguishes the four high-redshift candidates whose individual broad-H-beta detections are not formally significant. |
| `measurement_confidence_tier` | none | Derived tier: `high`, `medium`, or `low`. |
| `edd_ratio_consistency_flag` | none | Cross-check of the reported ratio against the value implied by tabulated MBH and Lbol. |
| `caveat_tags` | none | Semicolon-separated tags such as `tentative`, `missing_mstar`, `agn_contam_mstar`, `published_edd_ratio_inconsistent_with_mbh_lbol`, `missing_lensing`, `single_source_measurement`. |
| `primary_caveat` | none | Short human-readable caveat for table display. |
| `most_needed_followup` | none | The observation or analysis most likely to change the ranking. |

Suggested `measurement_confidence_tier`:

- `high`: `quality_flag=robust` and no central mass/luminosity field missing
- `medium`: robust but missing a key secondary field, or tentative with strong
  source-paper support
- `low`: tentative/candidate status plus major missingness or method caveats

The `stack_supported_tentative_hbeta` evidence class always maps to `low`
measurement confidence, even when host mass, bolometric luminosity, and an
Eddington ratio are available.

A robust row with `edd_ratio_consistency_flag=inconsistent` maps to `medium`
confidence. Its published values remain unchanged, but comparisons involving
the reported Eddington ratio require source verification.

For v1, all rows have missing lensing information because no lensing correction
is reported. This should be carried as a caveat tag but not treated as a severe
penalty unless a source is known or suspected to be lensed.

## Physical Pressure and Follow-Up Logic

The table should expose both a physical pressure tier and a follow-up priority
category.

Suggested `physical_growth_pressure_tier`:

- `high`: any of the following is true:
  - `req_fedd_seed1e2_z30_eps0p1_b1 > 1`
  - `req_log_mseed_fedd0p3_z30_eps0p1_b1 > 6`
  - `req_fedd_seed1e4_z30_eps0p1_b1 > 0.8` at `z > 7`
- `medium`: any of the following is true:
  - `0.7 < req_fedd_seed1e2_z30_eps0p1_b1 <= 1`
  - `5 < req_log_mseed_fedd0p3_z30_eps0p1_b1 <= 6`
  - `redshift > 7` with `req_fedd_seed1e2_z30_eps0p1_b1 > 0.8`
- `low`: otherwise

Implemented `followup_priority_category`:

- `A_robust_high_pressure`: high physical pressure and high measurement
  confidence. These are the strongest main-text ranking candidates under the
  stated assumptions.
- `B_tentative_high_pressure`: high physical pressure but tentative or
  caveated. These are high-value follow-up targets, not high-confidence claims.
- `C_host_ratio_tension`: extreme `M_BH/Mstar` tension, regardless of whether
  the growth-pressure tier is high.
- `D_source_consistency`: a published measurement triplet fails an internal
  consistency cross-check and requires source clarification.
- `D_systematics_leverage`: interpretation changes strongly under `MBH +/- 0.3`
  dex or host-contamination variants.
- `E_comparison_anchor`: robust objects with moderate pressure that contextualize
  the high-pressure cases.

If a numeric score is useful for sorting, use separate scores rather than one
opaque number:

- `physical_pressure_score_0_100`
- `measurement_confidence_score_0_100`
- `followup_value_score_0_100`

The follow-up value score may increase for uncertain but high-leverage objects,
because the point of follow-up is to resolve leverage. The measurement
confidence score should not be hidden inside the physical pressure score.

The implemented `rank_physical_pressure` is sorted by
`physical_pressure_score_0_100`, with `redshift` and `log_mbh_msun` used only as
tie-breakers. The pressure score is built from required-parameter metrics:

- light-seed pressure:
  `(req_fedd_seed1e2_z30_eps0p1_b1 - 0.3) / 1.2`, clipped to `[0, 1]`
- gentle-growth seed pressure:
  `(req_log_mseed_fedd0p3_z30_eps0p1_b1 - 4.0) / 2.8`, clipped to `[0, 1]`
- `1e4 Msun` seed pressure:
  `(req_fedd_seed1e4_z30_eps0p1_b1 - 0.3) / 0.7`, clipped to `[0, 1]`
- a small redshift tie-breaking bonus:
  `8 * clip((redshift - 6.0) / 4.0, 0, 1)`

`feasibility_score`, seed-model compatibility scores, and compatibility heatmap
quantities are not used for `rank_physical_pressure`.

## Proposed v1 Ranking Table Schema

The proposed output file is `results/v2_object_ranking_table.csv`.

| Column | Units | Source or derivation |
| --- | --- | --- |
| `rank_physical_pressure` | none | Sort rank by physical pressure metrics. |
| `rank_followup_priority` | none | Sort rank by follow-up value class/score. |
| `measurement_id` | none | From processed catalogue. |
| `physical_object_id` | none | Reserved for v4; blank or same as `object_id` in v1. |
| `object_id` | none | From processed catalogue. |
| `redshift` | none | From processed catalogue. |
| `cosmic_time_gyr` | Gyr | From processed catalogue. |
| `delta_t_z30_gyr` | Gyr | Existing result-table `delta_t_gyr` for `z_seed=30`. |
| `survey` | none | From processed catalogue. |
| `object_class` | none | From processed catalogue. |
| `quality_flag` | none | From processed catalogue. |
| `detection_evidence` | none | Controlled source-evidence class from the processed catalogue. |
| `source_key` | none | From processed catalogue. |
| `log_mbh_msun` | log10(Msun) | Baseline `log_mbh_msun_std`. |
| `log_mbh_err_plus` | dex | From processed catalogue. |
| `log_mbh_err_minus` | dex | From processed catalogue. |
| `mbh_method` | none | From processed catalogue. |
| `log_mstar_msun` | log10(Msun) | From processed catalogue. |
| `log_mstar_err_plus` | dex | From processed catalogue. |
| `log_mstar_err_minus` | dex | From processed catalogue. |
| `mstar_method` | none | From processed catalogue. |
| `edd_ratio_reported` | dimensionless | From processed catalogue. |
| `edd_ratio_from_mbh_lbol` | dimensionless | Cross-check derived from tabulated MBH and Lbol. |
| `edd_ratio_log_residual_dex` | dex | Reported-to-derived Eddington-ratio residual. |
| `edd_ratio_consistency_flag` | none | `consistent`, `inconsistent`, or `not_evaluable`. |
| `log_mbh_mstar_ratio` | dex | From processed catalogue. |
| `mbh_mstar_ratio` | dimensionless | Derived. |
| `mbh_mstar_tension_label` | none | Derived. |
| `req_fedd_seed1e2_z30_eps0p1_b1` | dimensionless | Required-`f_Edd` table. |
| `req_fedd_seed1e4_z30_eps0p1_b1` | dimensionless | Required-`f_Edd` table. |
| `req_fedd_seed1e5_z30_eps0p1_b1` | dimensionless | Required-`f_Edd` table. |
| `req_fedd_seed1e2_label` | none | Derived threshold label. |
| `req_fedd_seed1e4_label` | none | Derived threshold label. |
| `req_fedd_seed1e5_label` | none | Derived threshold label. |
| `req_log_mseed_fedd0p3_z30_eps0p1_b1` | log10(Msun) | Required-seed table. |
| `req_mseed_fedd0p3_msun` | Msun | Derived from log seed mass. |
| `req_mseed_fedd0p3_label` | none | Derived threshold label. |
| `req_log_mseed_fedd1_z30_eps0p1_b1` | log10(Msun) | Required-seed table. |
| `req_mseed_fedd1_msun` | Msun | Derived from log seed mass. |
| `req_mseed_fedd1_label` | none | Derived threshold label. |
| `req_fedd_seed1e2_mbh_minus0p3` | dimensionless | Systematic variant. |
| `req_fedd_seed1e2_mbh_plus0p3` | dimensionless | Systematic variant. |
| `req_log_mseed_fedd0p3_mbh_minus0p3` | log10(Msun) | Systematic variant. |
| `req_log_mseed_fedd0p3_mbh_plus0p3` | log10(Msun) | Systematic variant. |
| `light_seed_superedd_robust_mbh_minus0p3` | boolean | Derived. |
| `gentle_growth_above_heavy_robust_mbh_minus0p3` | boolean | Derived. |
| `physical_growth_pressure_tier` | none | Derived. |
| `growth_pressure_robustness_label` | none | Derived. |
| `measurement_confidence_tier` | none | Derived. |
| `caveat_tags` | none | Derived from flags/methods/notes. |
| `primary_caveat` | none | Short display string. |
| `most_needed_followup` | none | Short display string. |
| `followup_priority_category` | none | Derived. |
| `physical_pressure_score_0_100` | score | Derived, optional. |
| `measurement_confidence_score_0_100` | score | Derived, optional. |
| `followup_value_score_0_100` | score | Derived, optional. |
| `ranking_note` | none | One-sentence object note. |

## Compatibility Is Not Physical Possibility

The existing compatibility summaries ask whether a fixed scenario lands inside a
seed-model mass interval or close to a target mass. That is useful for maps and
sample summaries, but it is not identical to physical possibility.

A scenario can fail compatibility in two opposite ways:

- **Undergrowth:** the scenario cannot produce enough mass by the observed
  redshift. This is a physical-pressure signal.
- **Overgrowth:** the scenario produces too much mass, or the required seed mass
  falls below the seed-model interval. This does not mean the object is
  impossible. It means that exact scenario would need less accretion, a smaller
  seed, a lower duty cycle, a later seed time, or another parameter change.

For object ranking, required-parameter metrics are therefore clearer than a
single compatibility score. Compatibility should be described as
`exact_scenario_compatibility`, while physical possibility should be discussed
through the required `f_Edd`, required seed mass, uncertainty, and caveat
columns.

Overgrowth cases must not be labelled as physically impossible. They indicate
that the exact fixed scenario is too massive for the reported object unless one
or more assumptions changes. Undergrowth cases are the compatibility failures
that map most directly onto growth pressure.

## Expected High-Leverage v1 Objects

The current v1 outputs identify the following high-leverage objects under the
baseline `z_seed=30`, `epsilon=0.1`, no-merger reference.

| Object | Status | Why it is high leverage | Main caveat |
| --- | --- | --- | --- |
| `GS-20057765` | tentative | Highest-redshift v1 object (`z=8.913`), strongest light-seed pressure (`req_fedd_seed1e2=1.355`), high `1e4 Msun` seed pressure (`0.847`), and extreme host ratio (`log_mbh_mstar_ratio=-0.07`). Gentle growth requires `req_log_mseed_fedd0p3=6.150`. | Tentative; host and BH inference need confirmation. |
| `GN-38509` | robust | Strongest robust growth-pressure object: massive BH (`log_mbh=8.57`) at `z=6.678`, light-seed requirement `1.065`, and gentle-growth seed requirement `6.719`. It remains high-pressure after `MBH - 0.3 dex` (`req_fedd_seed1e2=1.016`, `req_log_mseed_fedd0p3=6.419`). | Host ratio is extreme but less so than GS-20057765 (`log_mbh_mstar_ratio=-0.62`); the reported current `f_Edd=0.015` is not a lifetime average, so the contrast motivates accretion-history follow-up rather than a direct inconsistency claim. |
| `GS-20030333` | tentative | High-redshift pressure object (`z=7.891`) with `req_fedd_seed1e2=1.133` and `req_log_mseed_fedd0p3=5.985`; remains light-seed super-Eddington after `MBH - 0.3 dex` (`1.070`). | Tentative H-beta status; the restored CIGALE host mass gives an elevated host ratio (`log_mbh_mstar_ratio=-1.19`). |
| `GS-164055` | tentative | High-redshift pressure object (`z=7.397`) with `req_fedd_seed1e2=1.065` and `req_log_mseed_fedd0p3=6.044`; barely remains light-seed super-Eddington after `MBH - 0.3 dex` (`1.008`). | Tentative H-beta status; the restored CIGALE host mass gives an extreme host ratio (`log_mbh_mstar_ratio=-0.36`). |
| `GN-4685` | tentative | High-redshift comparison object (`z=7.415`) with baseline light-seed pressure just above Eddington (`1.017`) and heavy-seed-scale gentle-growth requirement (`5.779`). | Tentative; pressure is sensitive to a downward BH-mass shift (`req_fedd_seed1e2_mbh_minus0p3=0.960`); host ratio is not extreme (`-2.55`). |
| `GN-954` | robust | Robust high-redshift comparison object (`z=6.759`) with substantial but sub-Eddington light-seed pressure (`0.940`) and heavy-seed-scale gentle-growth requirement (`5.881`). | Not a super-Eddington light-seed case at baseline; host ratio is low/typical for this triage scheme (`-3.23`). |

Secondary v1 objects worth retaining in ranked tables include `GS-210600`,
`GS-10013704`, `GS-204851`, `GS-30148179`, and `GN-61888`, which provide robust
moderate-pressure comparison points.
