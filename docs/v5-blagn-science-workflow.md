# v5 BLAGN science workflow

v5 applies the verified v4 growth mathematics to 106 measurements and 99
physical objects. It preserves `z_seed=30`, `epsilon=0.1`, `merger_boost=1`, and
the repository cosmology. Products are observational-triage and growth-pressure
rankings, not proof of a seed or accretion channel.

Run:

```powershell
python -m scripts.process_v5_blagn
python -m scripts.generate_v5_blagn_science --n-samples 10000 --seed 20260808
```

The science command writes 16 `results/releases/v5/tables/v5_blagn_*.csv` files: measurement- and
physical-object evaluations, point rankings, required-fEdd and required-seed
Monte Carlo summaries, uncertainty rankings, stratified catalogue and growth
summaries, alternate-measurement sensitivity, two accretion-history tables, and
a paper-facing full-versus-primary physical-object ranking comparison.

Evaluation, point-ranking, uncertainty-summary, and uncertainty-ranking rows
carry the v5 evidence, type, selection, phenotype, lensing, and eligibility
metadata. Summary products add object-class, evidence-status,
spectroscopic-type, and eligibility strata. The workflow fails rather than
ranking any row whose `growth_ranking_eligible_flag` is false.

The complete diagnostic rankings preserve all 106 measurements and 99 objects.
`rank_primary_growth_pressure` and `rank_primary_uncertainty_pressure` cover
the evidence-supported subset of 105 measurements and 98 objects. The single
alternative-interpretation candidate remains visible with its full growth
diagnostics but has a blank primary rank. This keeps physical growth pressure
separate from confidence in the accreting-black-hole interpretation.

The object view prevents physical double-counting. In particular,
CEERS-2782/RUBIES-EGS-50052/Harikane CEERS-02782 are three measurements of one
black hole. Seven nonpreferred measurements are tested one at a time without
changing the release defaults.

## Uncertainty and scenario policy

Reported asymmetric statistical MBH errors are sampled in log mass with the
project's established equal-side two-piece normal approximation (retained in
machine-readable products under the legacy label `split-normal-in-log-mbh`). A
standard-normal draw selects the reported upper or lower scale by sign, so each
side has 50% probability; this is not the normalized split-normal distribution
whose side weights depend on the two scales, nor a reconstruction of a source
posterior. The statistical draws are not silently combined with fixed shifts. Every row
has baseline and global `MBH +/-0.3 dex` comparisons. Taylor, Matthee, and
ASPIRE retain their separately labelled source-specific `+/-0.5 dex` virial
sensitivities. Harikane receives no source-specific scenario because its paper
does not state a numeric calibration systematic.

Missing host mass, luminosity, or Eddington-ratio diagnostics are labelled
unavailable and are not scoring penalties. Summary tables are stratified by
source, survey, field, survey/field, and LRD phenotype; overall mixed-selection
rows are descriptive and explicitly disallow demographic inference.
Physical-object LRD summaries preserve positive, explicit-negative, and
not-reported states; absence of a published designation is never counted as
non-LRD.

## Accretion-history extension

`v5_blagn_measurement_accretion_history.csv` has 318 rows (106 measurements by
three burst scenarios), and `v5_blagn_physical_object_accretion_history.csv`
has 297 rows (99 objects by three scenarios). Each uses a 100-Msun seed,
`z_seed=30`, `epsilon=0.1`, `merger_boost=1`, zero quiescent accretion, and
burst `f_Edd=1,2,3`. Required duty-cycle intervals propagate only the reported
asymmetric statistical MBH errors. No fixed mass systematic is silently folded
into them. A required duty cycle above one is retained and labels that fixed
burst scenario insufficient.

Reported `edd_ratio_std` values are copied only when published and are labelled
current/instantaneous measurements. Their ratio to the required lifetime mean
is a descriptive comparison, not an inferred historical duty cycle. Missing
ratios remain missing and do not affect ranking. The published GN-11836 value
is retained, along with its `-0.908 dex` source-table residual, but its
`current_to_required_fedd_ratio` is blank because the source-table consistency
check fails. `current_fedd_comparison_eligible_flag` and
`current_fedd_comparison_status` make that exclusion machine-readable.

For fixed `f_Edd,burst` and zero quiescent rate, required duty cycle is a
monotonic rescaling of required lifetime-average `f_Edd`. It therefore does not
define an independent scientific rank. The evidence-supported growth-pressure
rank remains canonical; duty cycle supplies an interpretable fixed-scenario
axis and feasibility threshold.

For paper use, `v5_blagn_primary_ranking_comparison.csv` is the canonical bridge
between the complete 99-object exploratory diagnostic ranking and the 98-object
primary evidence-supported ranking. Main-text rank claims should use the
primary columns; the complete ordering belongs in an exploratory or appendix
context. Four deliberate v5 figures now live under
`results/releases/v5/figures/main_text/` and are mapped in
`docs/v5-figure-inventory.md`. Frozen v4 figures remain unchanged.

Verify every checked-in v5 catalogue and science CSV, including a complete
in-memory reconstruction, without writing artifacts:

```powershell
python -m scripts.verify_v5_release --reproduce
```

Committed artifact integrity remains byte-exact through the manifest. Rebuilt
CSV structure and nonnumeric content are exact; floating-point comparison uses
`rtol=1e-13` and `atol=1e-14` for cross-platform final-bit stability. The
legacy `separation_arcsec` calculation alone uses `atol=1e-4` arcsec to cover
documented `arccos` cancellation differences between platform math libraries;
this is 5,000 times smaller than the 0.5-arcsec candidate-match threshold.

## Scientific change from v4

Harikane adds five new physical objects and five independent measurements of
known CEERS objects. The redshift ceiling remains set by JADES, while Harikane
adds a high-FWHM `z=6.936` object (CEERS-00717) that enters complete
point-estimate growth-pressure rank 4 and complete uncertainty-aware rank 5.
The prior v4 top three remain the same only in the complete exploratory
ordering; candidate RUBIES-EGS-49140 has no primary rank. This is a leverage
change within a heterogeneous-selection atlas, not a revised population-frequency
claim.
