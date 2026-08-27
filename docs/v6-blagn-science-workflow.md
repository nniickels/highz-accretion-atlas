# v6 BLAGN science workflow

v6 evaluates 112 measurements and 105 physical objects without overwriting v5.
It retains the repository cosmology and baseline `z_seed=30`, `epsilon=0.1`,
and `merger_boost=1`. These are observational-triage and growth-pressure
products, not proof of a seed or accretion channel.

Run:

```powershell
python -m scripts.process_v6_blagn
python -m scripts.generate_v6_blagn_science --n-samples 10000 --seed 20260808
python -m scripts.verify_v6_release --reproduce
```

The science command writes 16 `results/releases/v6/tables/v6_blagn_*.csv` tables at measurement
and physical-object level: evaluations, point rankings, statistical-uncertainty
summaries and rankings, stratified summaries, measurement-choice sensitivity,
accretion-history diagnostics, and the full-versus-primary object comparison.
The complete ordering contains 112/105 rows; the evidence-supported primary
ordering contains 111/104 because the inherited Taylor alternative-interpretation
candidate remains exploratory.

Every row retains baseline and common `MBH +/-0.3 dex` comparisons. Taylor,
Matthee, ASPIRE, and THRILS also receive separately named source-specific
`+/-0.5 dex` virial-calibration sensitivities. Reported statistical MBH errors
are propagated independently using the established equal-side two-piece-normal
approximation. Fixed systematics are not silently combined with statistical
draws.

Unavailable Mstar, Lbol, Eddington ratio, and LRD diagnostics are labelled
unavailable and never penalized. Summaries remain stratified by source,
survey/field, phenotype, and catalogue view. Overall rows explicitly warn that
the constituent selection functions differ and cannot support pooled demographic
inference.

No v6 figure set is generated in this release step. The four v5 paper-facing
figures remain the latest deliberate rendered products until a separate v6
figure-selection review establishes that a new plot materially changes the
paper argument.

