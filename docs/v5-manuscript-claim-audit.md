# v5 manuscript claim audit

Audit date: 2026-08-23. Scope: the living status manuscript, current catalogue,
science tables, source registry, extraction notes, and roadmaps.

| Claim | Repository evidence | Status |
| --- | --- | --- |
| v5 has 106 measurements / 99 physical objects | processed v5 tables and regression tests | verified |
| Harikane contributes ten rows, five matched and five new objects | raw table, reviewed candidates, links | verified |
| CEERS-2782 has three retained measurements but one object-level row | v5 links and object table | verified |
| Baseline uses `z_seed=30`, `epsilon=0.1`, `merger_boost=1` | v5 evaluations and model tests | verified |
| Statistical and fixed systematic shifts are separate | v5 uncertainty metadata/tests | verified |
| No numeric Harikane virial systematic is assumed | mass registry, raw metadata, scenario inventory | verified |
| CEERS-00717 enters point rank 4 and uncertainty rank 5 | v5 object ranking products | verified |
| Mixed-source summaries support demographics | explicitly prohibited by summary metadata | rejected claim |
| Rankings prove a unique seed channel | explicitly prohibited by project framing | rejected claim |

The current claims are internally reproducible. Before submission, every
literature statement still requires a final citation-by-citation check against
the published primary version, and figure/table numbers must be refreshed if a
later release supersedes v5. No demographic conclusion should be drawn from the
combined row counts.
