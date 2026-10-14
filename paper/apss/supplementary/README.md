# Supplementary calibration-scatter sensitivity

Early Giants: Black-Hole Growth Constraints from JWST
Nicole Jiang, University of Toronto
Correspondence: nicolejitong.jiang@mail.utoronto.ca

This archive reproduces the separate calibration test. It does not change the
catalogue, reference Monte Carlo results, or sample selection.

## Reproduce

Use Python 3.12 and pandas 2.2.3; `core.txt` records the full scientific runtime
pins used by the project. No project installation or random seed is needed.
From this directory:

```sh
python calibration_sensitivity.py --input target_robustness.csv --verify calibration_sensitivity.csv
python calibration_sensitivity.py --input target_robustness.csv --output regenerated.csv
```

The supplied input is the canonical `results/manuscript/tables/target_robustness.csv`
from repository commit 9584a7d05b597740434e3413514a12eb4811f6b6:
https://github.com/nniickels/highz-accretion-atlas
It identifies adopted measurements and their source keys. Source records are
in that revision's v3 object/measurement tables and provenance registry.
RUBIES-EGS-55604 uses RUBIESEGS55604_kocevski25; J0910_2028_12910 uses
J0910202812910_baccus26 (the frozen Baccus preprint measurement).

## Assumptions

Treat each separately reported 0.5-dex calibration scale as a Gaussian standard
deviation independent of the symmetric reported log-mass error. Add variances.
For a given offset, the probability is Phi((delta + offset) / sigma_total),
where delta is the downward log-mass shift that would bring the reference
required average Eddington ratio to unity, and Phi is the standard normal CDF.
The reference uses a 100-solar-mass seed, onset redshift 30, efficiency 0.1,
and no merger growth. Probabilities are computed analytically.

Only these two objects receive additional scatter. GN-38509 and ZS7 already
include calibration scatter in reported errors. Other unquantified biases
are not assigned artificial error distributions. The calculation makes no
assumption about correlations between objects and reports no joint probability.
