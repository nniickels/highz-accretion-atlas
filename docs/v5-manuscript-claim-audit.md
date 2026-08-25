# v5 manuscript claim audit

Audit date: 2026-08-25. Scope: the living status manuscript, current catalogue,
science tables, source registry, extraction notes, and roadmaps.

| Claim | Repository evidence | Status |
| --- | --- | --- |
| v5 has 106 measurements / 99 physical objects | processed v5 tables and regression tests | verified |
| Primary evidence-supported ranks contain 105 measurements / 98 physical objects; the alternative-interpretation candidate remains exploratory | processed v5 rankings and regression tests | verified |
| Object-level LRD state is 53 positive / 19 explicit negative / 27 not reported | processed v5 object catalogue and summary tests | verified |
| Harikane contributes ten rows, five matched and five new objects | raw table, reviewed candidates, links | verified |
| CEERS-2782 has three retained measurements but one object-level row | v5 links and object table | verified |
| Baseline uses `z_seed=30`, `epsilon=0.1`, `merger_boost=1` | v5 evaluations and model tests | verified |
| Statistical and fixed systematic shifts are separate | v5 uncertainty metadata/tests | verified |
| No numeric Harikane virial systematic is assumed | mass registry, raw metadata, scenario inventory | verified |
| CEERS-00717 enters point rank 4 and uncertainty rank 5 | v5 object ranking products | verified |
| Full diagnostic counts are 106/99 and primary evidence-supported counts are 105/98 | rankings and paper-facing comparison | verified |
| The primary point top five are GN-38509, GS-20057765, CEERS-00717, GOODS-N-9771, and GS-164055 | paper-facing comparison | verified |
| Two-state duty-cycle products use a 100-Msun seed, burst fEdd 1/2/3, zero quiescent rate, and the baseline cosmology/growth assumptions | accretion-history products and model tests | verified |
| Reported current fEdd is equivalent to a lifetime-average history | explicitly prohibited by output metadata and workflow documentation | rejected claim |
| GN-11836's published current fEdd may be used in a current-to-required ratio despite its source-table inconsistency | published value is retained, but the accretion-history comparison eligibility flag is false and ratio is missing | rejected claim |
| Fixed-burst duty-cycle ordering is independent of required-average-fEdd ordering | for fixed burst and zero quiescent rate, duty cycle is a monotonic rescaling | rejected claim |
| Four v5 paper figures describe the current sample without replacing frozen v4 figures | v5 generator, separate figure manifest/verifier, figure inventory, and visual inspection | verified |
| Both release manifests require exact artifact membership in addition to matching hashes | release verifiers and maintenance regression tests | verified |
| Mixed-source summaries support demographics | explicitly prohibited by summary metadata | rejected claim |
| Rankings prove a unique seed channel | explicitly prohibited by project framing | rejected claim |

The current claims are internally reproducible. The primary-source citation
check is recorded in `docs/v5-manuscript-citation-audit.md`. Figure/table numbers
must still be refreshed if a later release supersedes v5. No demographic
conclusion should be drawn from the combined row counts.
