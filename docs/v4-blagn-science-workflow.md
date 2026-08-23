# v4 BLAGN science workflow

The v4 science products evaluate both all 96 measurements and the 94-row
physical-object view. Baseline assumptions remain z_seed=30, epsilon=0.1,
merger_boost=1, and the repository cosmology. Rankings are observational triage
and growth-pressure summaries, not evidence for a unique seed channel.

## Catalogue views

The measurement view preserves and ranks all 96 literature measurements. The
physical-object view ranks 94 defaults chosen by the explicit link-table rules
documented in `docs/v4-blagn-catalogue-schema.md`. It never counts
CEERS-2782/RUBIES-EGS-50052 or GS-204851/GOODS-S-13971 as two physical black
holes. Alternative measurements remain available in the measurement view. The
separate alternate-measurement sensitivity product substitutes each of the two
nondefault measurements one at a time, recomputes the full object ranking, and
leaves release defaults unchanged.

## Uncertainty and systematic scenarios

Reported asymmetric MBH errors are sampled with the same deterministic
split-normal method and random seed used in v2/v3. Global +/-0.3 dex comparisons
remain. Taylor, Matthee, and ASPIRE each receive separately named +/-0.5 dex
Reines-calibration scenarios. Statistical and systematic uncertainties are
never silently combined.

Scenario scopes are explicit:

- `baseline`: reported MBH with no systematic shift;
- `mbh_minus_0p3dex` and `mbh_plus_0p3dex`: common comparison scenarios applied
  to all sources;
- Taylor, Matthee, and ASPIRE virial `+/-0.5 dex` scenarios: applied only to the
  named source and labelled independently from the common comparison.

The default run uses 10,000 draws per measurement and seed `20260808`.

## Output inventory

| Product | Measurement rows | Physical-object rows |
| --- | ---: | ---: |
| Evaluation | `v4_blagn_measurement_evaluation.csv` (434) | `v4_blagn_physical_object_evaluation.csv` (424) |
| Point ranking | `v4_blagn_measurement_point_ranking.csv` (96) | `v4_blagn_physical_object_point_ranking.csv` (94) |
| Uncertainty required fEdd | `v4_blagn_measurement_uncertainty_fedd.csv` (1302) | `v4_blagn_physical_object_uncertainty_fedd.csv` (1272) |
| Uncertainty required seed | `v4_blagn_measurement_uncertainty_mseed.csv` (868) | `v4_blagn_physical_object_uncertainty_mseed.csv` (848) |
| Uncertainty ranking | `v4_blagn_measurement_uncertainty_ranking.csv` (96) | `v4_blagn_physical_object_uncertainty_ranking.csv` (94) |

The remaining products are `v4_blagn_catalogue_summary.csv` and
`v4_blagn_growth_summary.csv`, each with 107 rows, plus the two-row
`v4_blagn_alternate_measurement_sensitivity.csv`. Evaluation and uncertainty
tables are long-form scenario products, so their row counts are larger than the
catalogue and differ by view/source scope.

## Interpretation and missing diagnostics

Products are stratified by source, survey/field, and LRD phenotype. Overall
rows are descriptive only: JADES, CEERS/RUBIES, EIGER/FRESCO, and ASPIRE have
different selection functions and are not pooled for demographic inference.
Missing Mstar or a source-reported Eddington ratio is marked unavailable and is
not a ranking penalty.

`edd_ratio_from_mbh_lbol` is a comparison derived from two published
quantities. It does not populate the source-reported Eddington-ratio field.
Similarly, `quality_flag=robust` describes broad-line detection confidence.
The ranking exposes that as `detection_confidence_tier` and independently
records `mass_measurement_reliability_tier`. Absorption, line-model, and
contamination caveats affect the latter and follow-up category; the universal
tracked virial systematic remains a separate scenario rather than a confidence
penalty.

## Reproduction and verification

Run:

```powershell
python -m scripts.process_v4_blagn
python -m scripts.generate_v4_blagn_science --n-samples 10000 --seed 20260808
python -m scripts.generate_v4_final_figures
```

The output names begin `v4_blagn_` and leave all v1--v3 artifacts unchanged.
The generator verifies catalogue/evaluation row counts, unique ranking IDs,
release metadata, and the requested Monte Carlo sample count before reporting
success. Run the full v1--v4 regression suite separately with:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests
```

The five v4 figures under `results/v4_main_text_figures/` include mass-redshift,
ranked-growth, uncertainty, source-coverage, and duplicate-measurement
sensitivity views. The four files under `results/v3_main_text_figures/` remain
intentional frozen-v3 comparisons.
