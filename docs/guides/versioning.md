# Dataset versioning

v1–v3 are nested catalogue versions. They describe source additions, not code
milestones or package releases. Counts are in the
[main README](../../README.md#dataset-versions); the
[literature scope](../reference/literature-scope.md) defines the cutoff,
exclusions, and membership history.

| Version | Membership |
| --- | --- |
| v1 | Original Juodžbalis JADES broad-line AGN sample. |
| v2 | v1 plus comparable JWST broad-line source families with published numerical masses. Source-specific calibrations are preserved. |
| v3 | v2 plus heterogeneous X-ray, narrow-line, high-ionization, infrared, photometric, and broad-line candidates. Missing and conditional masses remain explicit. |
| v4 | Separate four-target growth analysis using v3 measurements and publication sample rules; no additional catalogue rows. |

Source-level assignment governs membership: a heterogeneous source belongs to
v3 even when individual rows resemble v2 objects. The
[source bibliography](../../data/sources.md) identifies the included families.

All three catalogues use the shared baseline analysis and applicable corrections.
v3 also has the [extended result tables](../reference/catalogue-results.md).
Unchanged plots are shared across versions; each visual-coverage table records
the retained paths and missing-mass reasons.

The 29 October 2026 metadata correction standardizes nullable boolean flags
before object and stratum aggregation. Literal false values no longer inflate
little-red-dot counts. Adoption explanations also reflect retained alternatives.
These corrections change neither catalogue membership nor adopted masses,
redshifts, or manuscript growth results. The updated
[follow-up policy](../reference/science-policy.md#samples-identities-and-ranks)
withholds numerical follow-up ranks for unresolved identities.

v4 has separate settings, outputs, and verification under `results/v4/`.
It does not introduce `data/processed/v4`. See the
[v4 methods](../reference/pbh-growth-v4.md) and
[output guide](../../results/v4/README.md).
