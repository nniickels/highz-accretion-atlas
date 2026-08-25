# v5 BLAGN catalogue and taxonomy schema

v5 adds the ten-row Harikane et al. (2023) measurement layer to frozen v4. It
contains 106 literature measurements representing 99 physical objects at
`z>=4`. No v1--v4 artifact is overwritten.

| Product | Rows | Purpose |
| --- | ---: | --- |
| `data/raw/harikane23_nirspec_blagn_tables1_3.csv` | 10 | Immutable source-table extraction |
| `data/processed/v5_blagn_measurements.csv` | 106 | Every literature measurement |
| `data/processed/v5_blagn_objects.csv` | 99 | One reproducible default measurement per object |
| `data/crossmatch/v5_measurement_object_links.csv` | 106 | Measurement/object links and default rules |
| `data/crossmatch/v5_object_aliases.csv` | 106 | Source aliases and coordinates |
| `data/crossmatch/v5_reviewed_match_candidates.csv` | 6 | Reviewed threshold candidates |
| `data/crossmatch/v5_reviewed_identity_overrides.csv` | 6 | Explicit accepted identity decisions |

Five Harikane measurements match five existing physical objects; five are new.
The six candidate rows arise because CEERS-02782 is independently close to two
already linked Taylor measurements. Every physical object has exactly one
preferred measurement. Prior-release preferences are retained, while all
alternates remain rankable and enter the alternate-measurement sensitivity
product.

## Orthogonal taxonomy

v5 adds fields that prepare the atlas for later heterogeneous evidence without
pooling unlike classes:

- `evidence_status`: strength of the accreting massive-black-hole evidence;
- `evidence_status_basis`: controlled reason for the assigned evidence status;
- `spectroscopic_type`: Type 1 broad-line, Type 2 narrow-line, ambiguous, or unknown;
- `selection_channels`: the observation that selected the measurement;
- `phenotype_tags`: independent descriptors such as `lrd`, `red_agn`, or `compact_source`;
- `lensing_status`: whether lensing metadata are present;
- `growth_ranking_eligible_flag`: whether a sufficiently supported MBH exists for growth diagnostics.
- `primary_growth_ranking_flag`: whether the row belongs to the secure/probable
  primary ordering rather than the preserved exploratory candidate layer.

All v5 rows remain `object_class=broad-line-agn`,
`spectroscopic_type=type1_broad_line`, and growth-ranking eligible. Evidence
status is nevertheless caveat-aware: robust detection is not automatically a
secure physical interpretation. LRD is never used as the object class. Blank
LRD state means the source did not provide a row-level designation; it does not
mean non-LRD.

At physical-object level, `phenotype_tags` is the union across every linked
measurement. `preferred_measurement_phenotype_tags` preserves the default
measurement alone, while `phenotype_evidence_measurement_ids` and
`phenotype_evidence_source_keys` make the union auditable.

Physical-object `evidence_status` is likewise the most conservative status
among linked measurements. Preferred-measurement evidence and the linked
measurement/source support for the aggregate status are retained separately.

Object-level LRD status is explicitly three-state: `true` if any linked
measurement reports LRD, `false` only if at least one linked measurement
provides a designation and none reports LRD, and blank if no linked source
provides a designation. The current object view therefore contains 53 LRDs, 19
explicit non-LRDs, and 27 objects with no reported designation.

Harikane's typical `0.2 dex` stellar-mass systematic from the fixed SED-fitting
prior is stored separately in `log_mstar_systematic_dex` and is not combined
with the published statistical uncertainty or used in growth rankings.

The taxonomy is scaffolding, not permission to pool future X-ray, narrow-line,
photometric, lensed, or disputed candidates. Those additions require
class-specific evidence and mass-method rules and should begin in v6.
