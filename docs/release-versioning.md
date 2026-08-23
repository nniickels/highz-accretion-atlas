# Release Versioning and Filename Map

Project release numbers identify reproducible catalogue or science milestones.
They do not identify the version of a source paper. The current catalogue and
science release is **v4**; v3 remains frozen as the JADES + Taylor comparison
release and figure set.

| Release | Scope | Inputs | Canonical outputs |
| --- | --- | --- | --- |
| v1 | Pilot JADES broad-line AGN catalogue and baseline growth evaluation | `data/raw/v1_raw.csv` | `data/processed/v1_processed.csv`, `results/v1_evaluation_table.csv`, other `results/v1_*` exploratory products |
| v2 | Ranking, asymmetric-error propagation, and final-style prototypes for the frozen v1 catalogue | v1 processed and evaluation products | `results/v2_object_ranking_table.csv`, `results/v2_uncertainty_*.csv`, `results/v2_main_text_figures/` |
| v3 | Combined JADES + Taylor CEERS/RUBIES BLAGN catalogue, with separate measurement and physical-object views | frozen v1 catalogue plus the Taylor source extraction and crossmatch | `data/processed/v3_blagn_*.csv`, `results/v3_blagn_*.csv` |
| v4 | Generalized identity layer plus Matthee EIGER/FRESCO and Lin ASPIRE BLAGN | frozen v3 catalogue plus two source-native extractions | `data/processed/v4_blagn_*.csv`, `results/v4_blagn_*.csv` |

This means v2 is an **analysis release**, not a second catalogue extraction.
The later combined products extend earlier releases, but do not overwrite or
invalidate v1, v2, or v3 artifacts.

## Naming Rules

- Put the project release prefix first on processed data, generated results,
  release-specific scripts, tests, and documentation.
- Keep immutable source-specific raw extractions descriptive, for example
  `taylor24_ceers_rubies_blagn_table1.csv`. Their provenance columns record the
  paper version, DOI, archive URL, extraction date, and checksum.
- Use `project_version` for the standardization release (`v1`, `v3`, or `v4`)
  and `catalogue_release` for the named combined catalogue.
- Use `analysis_release` and `input_catalogue_release` on v2 result tables so a
  filename cannot be mistaken for the catalogue version it evaluates.
- Treat an arXiv suffix such as `v2` in `2409.06772v2` only as a source-paper
  version. It has no relationship to project release v2.
- Do not rename a frozen artifact in place in a later scientific release.
  Generate a new release-prefixed product and retain regression coverage of the
  earlier artifact.

## Current Dependency Map

```text
v1 raw JADES -> v1 processed -> v1 baseline evaluation
                                  |
                                  +-> v2 ranking / uncertainty / figures
                                  |
Taylor raw + crossmatch ----------+-> v3 measurement catalogue
                                       -> v3 physical-object catalogue
                                       -> v3 evaluation / rankings / summaries
                                                   |
Matthee + ASPIRE raw + identity metadata ---------+-> v4 measurement catalogue
                                                       -> v4 physical-object catalogue
                                                       -> v4 evaluation / rankings / summaries
```

The v3 measurement view retains all 60 `z >= 4` literature measurements. The
physical-object view has 59 rows because CEERS-2782 and RUBIES-EGS-50052 are two
measurements of one physical object. The preferred-measurement rule is stored in
`data/crossmatch/v3_measurement_object_links.csv` rather than encoded by deleting
either measurement.

The v4 identity layer preserves those assignments and adds one verified
cross-paper link: Matthee `GOODS-S-13971` is JADES `GS-204851`. The prior-release
JADES measurement remains the default for continuity, while both measurements
remain independently rankable in the measurement view.

The current science tables are v4 products. The latest release-specific
main-text figures remain the frozen v3 set in `results/v3_main_text_figures/`;
there is not yet a v4 figure directory. This is an explicit roadmap gap, not a
filename mismatch.

## Rename Map

| Previous name | Current name |
| --- | --- |
| `scripts/generate_v1_rankings.py` | `scripts/generate_v2_rankings.py` |
| `scripts/generate_v1_uncertainty_rankings.py` | `scripts/generate_v2_uncertainty_rankings.py` |
| `scripts/generate_v1_final_figures.py` | `scripts/generate_v2_final_figures.py` |
| `results/v1_object_ranking_table.csv` | `results/v2_object_ranking_table.csv` |
| `results/v1_uncertainty_*.csv` | `results/v2_uncertainty_*.csv` |
| `results/v1_main_text_figures/v1_main_text_*.png` | `results/v2_main_text_figures/v2_main_text_*.png` |
| `scripts/process_expanded_blagn.py` | `scripts/process_v3_blagn.py` |
| `scripts/generate_expanded_blagn_science.py` | `scripts/generate_v3_blagn_science.py` |
| `src/expanded_catalogue.py` | `src/v3_catalogue.py` |
| `src/expanded_science.py` | `src/v3_science.py` |
| `data/processed/expanded_blagn_*.csv` | `data/processed/v3_blagn_*.csv` |
| `results/expanded_blagn_*.csv` | `results/v3_blagn_*.csv` |

All code, documentation, tests, and status-report references use the current
names. The old paths are intentionally not maintained as duplicate aliases,
which prevents two filenames from appearing to identify different releases
when they contain the same artifact.
