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

The science command writes 13 `results/v5_blagn_*.csv` files: measurement- and
physical-object evaluations, point rankings, required-fEdd and required-seed
Monte Carlo summaries, uncertainty rankings, stratified catalogue and growth
summaries, and alternate-measurement sensitivity.

The object view prevents physical double-counting. In particular,
CEERS-2782/RUBIES-EGS-50052/Harikane CEERS-02782 are three measurements of one
black hole. Seven nonpreferred measurements are tested one at a time without
changing the release defaults.

## Uncertainty and scenario policy

Reported asymmetric statistical MBH errors are sampled with a split-normal
model in log mass. They are not silently combined with fixed shifts. Every row
has baseline and global `MBH +/-0.3 dex` comparisons. Taylor, Matthee, and
ASPIRE retain their separately labelled source-specific `+/-0.5 dex` virial
sensitivities. Harikane receives no source-specific scenario because its paper
does not state a numeric calibration systematic.

Missing host mass, luminosity, or Eddington-ratio diagnostics are labelled
unavailable and are not scoring penalties. Summary tables are stratified by
source, survey, field, survey/field, and LRD phenotype; overall mixed-selection
rows are descriptive and explicitly disallow demographic inference.

## Scientific change from v4

Harikane adds five new physical objects and five independent measurements of
known CEERS objects. The redshift ceiling remains set by JADES, while Harikane
adds a high-FWHM `z=6.936` object (CEERS-00717) that enters point-estimate
growth-pressure rank 4 and uncertainty-aware rank 5. The prior v4 top three
physical objects remain the same. This is a leverage change within a
heterogeneous-selection atlas, not a revised population-frequency claim.
