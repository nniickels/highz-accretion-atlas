# Release Versioning and Filename Map

Project release numbers identify reproducible catalogue or science milestones.
They do not identify the version of a source paper. The current catalogue layer
is **v7.1** and the current completed science release is **v6**. v4.0.1 remains
the frozen reproducibility anchor for the preceding Matthee/ASPIRE release; v3
remains the JADES + Taylor comparison.

| Release | Scope | Inputs | Canonical outputs |
| --- | --- | --- | --- |
| v1 | Pilot JADES broad-line AGN catalogue and baseline growth evaluation | `data/raw/v1_raw.csv` | `data/processed/v1_processed.csv`, `results/v1_evaluation_table.csv`, other `results/v1_*` exploratory products |
| v2 | Ranking, asymmetric-error propagation, and final-style prototypes for the frozen v1 catalogue | v1 processed and evaluation products | `results/v2_object_ranking_table.csv`, `results/v2_uncertainty_*.csv`, `results/v2_main_text_figures/` |
| v3 | Combined JADES + Taylor CEERS/RUBIES BLAGN catalogue, with separate measurement and physical-object views | frozen v1 catalogue plus the Taylor source extraction and crossmatch | `data/processed/v3_blagn_*.csv`, `results/v3_blagn_*.csv` |
| v4 | Generalized identity plus Matthee EIGER/FRESCO and Lin ASPIRE BLAGN, corrected confidence semantics, duplicate sensitivity, and final figures | frozen v3 catalogue plus two source-native extractions | `data/processed/v4_blagn_*.csv`, `results/v4_blagn_*.csv`, `results/v4_main_text_figures/` |
| v5 | Harikane NIRSpec BLAGN measurement-version layer, orthogonal taxonomy, accretion-history science extension, and current paper figures | frozen v4 catalogue plus Harikane Tables 1--3 | `data/processed/v5_blagn_*.csv`, `results/v5_blagn_*.csv`, `results/v5_main_text_figures/` |
| v6 | Final same-class BLAGN consolidation with the Davis/THRILS deep-spectroscopy sample | frozen v5 plus Davis Appendix Table 5 and Hutchison Table 3 coordinates | `data/processed/v6_blagn_*.csv`, `results/v6_blagn_*.csv` |
| v7.0 catalogue (frozen) | First heterogeneous evidence-class catalogue layer | frozen v6 plus Ren et al. rows admitted by the multi-class contract | 119 measurements / 112 objects / 111 host systems; catalogue products only |
| v7.1 catalogue (current) | Luminous-quasar comparison extension | frozen v7.0 plus the complete 42-object XQR-30 source family | 161 measurements / 154 objects / 153 host systems; catalogue products only |
| class-aware science (planned) | Heterogeneous atlas analysis | a verified heterogeneous catalogue layer | rankings and figures that keep evidence and mass-comparability strata explicit |

This means v2 is an **analysis release**, not a second catalogue extraction.
The later combined products extend earlier releases, but do not overwrite or
invalidate v1, v2, or v3 artifacts.

Patch tags such as `v4.0.1` do not advance the catalogue chronology. The
`v4-blagn` tag remains the frozen science anchor; `releases/v4.0.1-manifest.json`
records hashes for its catalogue and science CSVs, exact Monte Carlo controls,
and expected counts.

The v5 CSVs are independently covered by `releases/v5-manifest.json`
and `python -m scripts.verify_v5_release --reproduce`; this reproducibility gate
does not require a release tag. Both v4.0.1 and v5 verifiers require exact
manifest membership as well as matching hashes, so omitted or unexpected
release artifacts fail verification.

The current v6 CSVs are covered by `releases/v6-manifest.json` and
`python -m scripts.verify_v6_release --reproduce`. v6 does not regenerate a
figure set; the deliberate v5 figures remain the latest paper-facing images.

The catalogue-only v7 files are covered by
`releases/v7-catalogue-manifest.json` and
`python -m scripts.verify_v7_catalogue --reproduce`. This manifest deliberately
contains no science ranking, uncertainty, or figure artifact.

The XQR-30 extension is independently covered by
`releases/v7.1-catalogue-manifest.json` and
`python -m scripts.verify_v7_1_catalogue --reproduce`. Its `v7_1_` filenames do
not replace the frozen v7.0 artifacts.

The four canonical rendered v5 PNGs are independently hash-anchored by
`releases/v5-figures-manifest.json` and checked with
`python -m scripts.verify_v5_figures`. Keeping the figure boundary separate
preserves strict cross-platform CSV reconstruction while acknowledging that
rendered bytes can depend on platform font and graphics libraries.

The installable package version follows the current implemented science
milestone (`6.0.0`). That version is not a source-paper version, a catalogue
label (`v6-blagn`), or a promise that every historical artifact was regenerated.

## Naming Rules

- Put the project release prefix first on processed data, generated results,
  release-specific scripts, tests, and documentation.
- Keep immutable source-specific raw extractions descriptive, for example
  `taylor24_ceers_rubies_blagn_table1.csv`. Their provenance columns record the
  paper version, DOI, archive URL, extraction date, and checksum.
- Use `project_version` for the row's standardization release (`v1`, `v3`, `v4`, `v5`, `v6`, or `v7`)
  and `catalogue_release` for the named combined catalogue. v7.1 rows introduced
  by XQR-30 use `project_version=v7.1`; inherited rows retain their introduction
  version.
- Use `analysis_release` and `input_catalogue_release` on v2 result tables so a
  filename cannot be mistaken for the catalogue version it evaluates.
- Treat an arXiv suffix such as `v2` in `2409.06772v2` only as a source-paper
  version. It has no relationship to project release v2.
- Do not rename a frozen artifact in place in a later scientific release.
  Generate a new release-prefixed product and retain regression coverage of the
  earlier artifact.
- Use a patch tag for infrastructure or documentation maintenance that leaves
  the scientific release invariant. Confirm that invariance with a checked-in
  hash manifest and in-memory reproduction. Manifest integrity remains
  byte-exact; cross-platform reconstruction compares structure and nonnumeric
  values exactly and floating-point values at documented tight tolerance.

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
                                                       -> v4 evaluation / rankings / summaries / figures
                                                                  |
Harikane raw + reviewed identity decisions -----------------------+-> v5 measurement catalogue
                                                                      -> v5 physical-object catalogue
                                                                      -> v5 evaluation / rankings / summaries
                                                                      -> v5 two-state duty-cycle diagnostics
                                                                      -> v5 paper-facing figures
                                                                                 |
THRILS Table 5 + programme coordinates -----------------------------------------+-> v6 measurement catalogue
                                                                                     -> v6 physical-object catalogue
                                                                                     -> v6 evaluations / rankings / summaries
                                                                                               |
Ren Tables 1--2 + v7 admission gate ----------------------------------------------------------+-> v7 measurement catalogue
                                                                                                  -> v7 physical-object catalogue
                                                                                                  -> v7 host-system / observable / strata products
                                                                                                              |
XQR-30 mass table + companion coordinates ---------------------------------------------------------------+-> v7.1 catalogue / identity / observable / strata products
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

The current science tables remain v6 products. The current catalogue layer is
v7.1 and has no heterogeneous science tables yet. The paper-facing
`v6_blagn_primary_ranking_comparison.csv` distinguishes the complete 112/105
exploratory diagnostic population from the 111/104 primary evidence-supported
population. Deliberate current figures live under
`results/v5_main_text_figures/`; the frozen v4 set remains unchanged as the
previous-release record.

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
