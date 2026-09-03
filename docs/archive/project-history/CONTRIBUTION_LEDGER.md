# Codex Contribution Ledger

Purpose: maintain an append-only chronological record of Codex contributions to this repository so work can be audited and summarized later.

## Maintenance rule

For every future Codex contribution that changes repository files:

1. Append a dated entry to this ledger in the same contribution, before handoff. Include the ledger itself in the entry's file list when it is changed. Read-only reviews that do not change repository files do not require an entry.
2. Use every field in the template below: objective, files changed, contribution, scientific/technical effect, validation, and status. If validation was not run, write `Not run` and give the reason rather than omitting the field.
3. Under **Files changed**, list every affected repository-relative path on its own bullet and label it `(added)`, `(modified)`, `(deleted)`, or `(renamed from `old/path`)`. Reconcile the list with `git diff --name-status` for uncommitted work or Git history for committed work.
4. State whether the work is committed or uncommitted in **Status**. For committed work, include the abbreviated commit hash and subject.
5. Preserve the chronological record. Existing entries may be edited only to correct factual errors, omissions, or formatting needed to meet this audit standard.
6. Update `.codex_tmp/highz_accretion_atlas_status.tex` when the contribution changes an overall method, major capability, result, limitation, figure, or roadmap stage.
7. Recompile and visually verify `.codex_tmp/highz_accretion_atlas_status.pdf` whenever the LaTeX paper changes.
8. Minor mechanical changes may be recorded in the ledger without receiving detailed paper coverage; the paper should summarize major steps and durable results rather than every edit.

## Entry template

```markdown
### YYYY-MM-DD - Short title

- **Objective:** What the contribution was intended to accomplish.
- **Files changed:**
  - `path/to/file` (added)
  - `path/to/other-file` (modified)
- **Contribution:** What was implemented or changed.
- **Scientific/technical effect:** Effect on the science, data, software, workflow, or documentation; explicitly state when there was no scientific effect.
- **Validation:** Checks performed and their outcomes, or `Not run` with a reason.
- **Status:** Complete or in progress; committed in `abcdef0` (`commit subject`) or verified locally and uncommitted.
```

## Chronological entries

### 2026-08-12 - Uncertainty-aware main-text figure

- **Objective:** Turn the Monte Carlo uncertainty products into a compact, publication-style visualization.
- **Files changed:**
  - `scripts/generate_v1_final_figures.py` (modified)
  - `results/v1_main_text_figures/v1_main_text_uncertainty_forest.png` (added)
  - `docs/guides/getting-started.md` (modified)
  - `docs/v1-figure-inventory.md` (modified)
- **Contribution:** Added a two-panel uncertainty forest plot ordered by the uncertainty-aware pressure rank. The plot shows baseline 5th--95th and 16th--84th percentile intervals, Monte Carlo medians, original point estimates, separate `MBH +/- 0.3 dex` systematic medians, robust/tentative measurement status, physical thresholds, and per-object threshold probabilities. Integrated the output into the existing final-figure generator and documented the new product.
- **Scientific/technical effect:** Made Monte Carlo threshold probabilities and interval/systematic comparisons available as a main-text visual; no source catalogue or numerical result tables changed.
- **Validation:** Generated and visually inspected the PNG; confirmed all 23 objects and both probability columns were legible; ran the full 23-test regression suite successfully; checked the patch with `git diff --check`.
- **Status:** Complete and present in repository commit `15a1b3f` (`Document monte carlo sample results`).

### 2026-08-13 - Project-status paper and contribution ledger

- **Objective:** Document the completed project, current scientific interpretation, repository workflow, limitations, and future research goals in a concise paper with figures.
- **Files changed:**
  - `.codex_tmp/highz_accretion_atlas_status.tex` (added)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (added)
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (added)
- **Contribution:** Added a LaTeX project-status manuscript organized chronologically from data provenance through standardization, physical modeling, scenario evaluation, ranking, Monte Carlo uncertainty propagation, current findings, validation, limitations, and the staged research roadmap. Embedded the mass--redshift overview, uncertainty forest plot, pressure-versus-confidence plot, and seed-redshift spotlight maps. Established this ledger as the ongoing record for future Codex work.
- **Scientific/technical effect:** Created durable project-state documentation and an audit trail; no analysis inputs or outputs changed.
- **Validation:** LaTeX compilation and PDF rendering/visual inspection completed; final page count, embedded figures, text extraction, and layout were checked. No source or result tables were altered by the documentation build.
- **Status:** Complete and present in repository commit `33b9337` (`documentation`).

### 2026-08-15 - Correct tentative broad-Hbeta evidence and virial-mass metadata

- **Objective:** Correct the first must-address scientific metadata issue by distinguishing the four high-redshift tentative broad-Hbeta candidates from the robust broad-Halpha sample and carrying that distinction through the analysis products.
- **Files changed:**
  - `data/raw/v1_raw.csv` (modified)
  - `data/processed/v1/v1_processed.csv` (modified)
  - `data/sources.md` (modified)
  - `src/standardize_data.py` (modified)
  - `scripts/generate_v1_rankings.py` (modified)
  - `scripts/generate_v1_uncertainty_rankings.py` (modified)
  - `scripts/v1_evaluate.ipynb` (modified)
  - `results/v1_object_ranking_table.csv` (modified)
  - `results/v1_uncertainty_aware_ranking_table.csv` (modified)
  - `results/v1_uncertainty_required_fedd_summary.csv` (modified)
  - `results/v1_uncertainty_required_mseed_summary.csv` (modified)
  - `tests/test_v1_pipeline.py` (modified)
  - `docs/archive/legacy/catalogue-schema.md` (modified)
  - `docs/v1-ranking-metrics.md` (modified)
  - `docs/v1-uncertainty-propagation.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (modified)
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
- **Contribution:** Corrected GS-20057765, GS-20030333, GS-164055, and GN-4685 from single-epoch broad-Halpha to broad-Hbeta virial-mass metadata. Added a controlled `detection_evidence` field, mapped it deterministically to `quality_flag`, and propagated the evidence and mass method through point and uncertainty products. The four candidates are now consistently represented as stack-supported tentative broad-Hbeta measurements with low confidence and explicit caveats that their individual broad-component detections are not formally significant. No getting-started or reproduction-guide material was changed.
- **Scientific/technical effect:** The physical-pressure and uncertainty-pressure rank order is unchanged, but the evidential status and follow-up interpretation of the four tentative high-redshift candidates are now explicit and source-consistent.
- **Validation:** Re-ran the complete processing, point-ranking, and 10,000-sample uncertainty pipeline with seed `20260808`; all pipeline sanity checks passed and regenerated hashes were unchanged. All 24 regression tests passed. Exact-four-object invariants, evidence-to-quality mapping, confidence tiers, caveat tags, and unchanged rank mappings were checked directly. `git diff --check` passed. The status PDF was recompiled, rendered, and visually inspected after this entry was added.
- **Status:** Complete and present in repository commit `11b6d93` (`fix data source tag`).

### 2026-08-15 - Standardize contribution-ledger requirements

- **Objective:** Make the contribution ledger consistently identify every changed file and provide enough status and validation detail for future auditing.
- **Files changed:**
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
- **Contribution:** Added a mandatory entry format and reusable template, including per-file change types, validation reporting, and commit state. Reconciled the existing entries with Git history and normalized them to the same format.
- **Scientific/technical effect:** No scientific methods, source data, analysis code, or results changed; this improves auditability and future ledger compliance.
- **Validation:** Checked all three committed historical entries and their file lists against Git history for commits `15a1b3f`, `33b9337`, and `11b6d93`; reviewed the current worktree file list for this uncommitted entry; and ran `git diff --check`.
- **Status:** Complete and present in repository commit `35aeab7` (`data flag update`).

### 2026-08-15 - Restore adopted host masses and flag an inconsistent Eddington ratio

- **Objective:** Resolve the two remaining must-address scientific catalogue issues: omitted source-adopted host stellar masses for three objects and the internally inconsistent published Eddington-ratio triplet for GN-11836.
- **Files changed:**
  - `data/raw/v1_raw.csv` (modified)
  - `data/processed/v1/v1_processed.csv` (modified)
  - `data/sources.md` (modified)
  - `src/standardize_data.py` (modified)
  - `scripts/generate_v1_rankings.py` (modified)
  - `scripts/generate_v1_uncertainty_rankings.py` (modified)
  - `scripts/v1_evaluate.ipynb` (modified)
  - `results/releases/v1/tables/v1_evaluation_table.csv` (modified)
  - `results/releases/v1/tables/v1_required_fedd_by_seed_mass.csv` (modified)
  - `results/releases/v1/tables/v1_required_mseed_by_growth_assumption.csv` (modified)
  - `results/v1_object_ranking_table.csv` (modified)
  - `results/v1_uncertainty_required_fedd_summary.csv` (modified)
  - `results/v1_uncertainty_required_mseed_summary.csv` (modified)
  - `results/v1_uncertainty_aware_ranking_table.csv` (modified)
  - `results/v1_main_text_figures/v1_main_text_pressure_vs_confidence.png` (modified)
  - `tests/test_v1_pipeline.py` (modified)
  - `docs/archive/legacy/catalogue-schema.md` (modified)
  - `docs/v1-ranking-metrics.md` (modified)
  - `docs/v1-uncertainty-propagation.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (modified)
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
- **Contribution:** Restored the paper's adopted CIGALE host-mass measurements for GS-200679 (`8.53 +/- 0.13`), GS-20030333 (`8.61 +/- 0.20`), and GS-164055 (`7.99 +/- 0.23`). Added deterministic Eddington-ratio cross-check fields derived from reported black-hole mass and bolometric luminosity, a `0.3 dex` consistency tolerance, validation of ratio/uncertainty domains, and downstream consistency caveats. Preserved the published GN-11836 values verbatim while flagging their inconsistency, lowering the object's ranking confidence to medium, and assigning source clarification as its follow-up category. Regenerated all affected point-estimate, uncertainty, figure, and status-paper products. No getting-started or reproduction-guide material was changed.
- **Scientific/technical effect:** The number of active processed objects lacking a host mass fell from four to one. The restored black-hole-to-host mass ratios are `-2.34` for GS-200679, `-1.19` for GS-20030333, and `-0.36` for GS-164055. For GN-11836, the reported `log(M_BH/M_sun)=6.06` and `log(L_bol/[erg s^-1])=44.11` imply `lambda_Edd=0.890491`, rather than the reported `0.11`, a residual of `-0.908237 dex`; the catalogue now exposes this discrepancy without substituting an undocumented value. Point and uncertainty pressure ranks remain unchanged.
- **Validation:** Checked the source values and host-mass selection against Tables 2 and 5 of the published catalogue paper. Re-ran standardization, the 8,832-row evaluation grid, both 2,208-row derived scenario tables, point rankings, and the full 10,000-sample uncertainty pipeline with seed `20260808`; all built-in sanity checks passed. All 25 regression tests passed. Confirmed exactly one remaining active missing host mass and exactly one Eddington-ratio inconsistency. Rebuilt and inspected the affected main-text figure. Recompiled the 10-page status PDF and visually inspected every page. `git diff --check` passed.
- **Status:** Complete and present in repository commit `35aeab7` (`data flag update`).

### 2026-08-15 - Preserve source-consistency priority in uncertainty ranking

- **Objective:** Prevent a point-ranking source-consistency priority from falling through to generic context in the uncertainty-aware follow-up classification.
- **Files changed:**
  - `scripts/generate_v1_uncertainty_rankings.py` (modified)
  - `tests/test_v1_pipeline.py` (modified)
  - `docs/v1-uncertainty-propagation.md` (modified)
  - `results/v1_uncertainty_aware_ranking_table.csv` (modified)
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
- **Contribution:** Added explicit `D_source_consistency` handling to the uncertainty follow-up categorizer and a source-specific reason that retains the standard quality, baseline-assumption, and measurement-tier context. Added a production sanity invariant and regression assertions for GN-11836. Regenerated the uncertainty-aware ranking and documented the behavior.
- **Scientific/technical effect:** GN-11836 now remains `D_source_consistency` in both `followup_priority_category` and `uncertainty_followup_category`, rather than being relabeled `F_context`. Its uncertainty follow-up reason carries the `-0.91 dex` Eddington-ratio residual and source-clarification requirement. Numerical uncertainty products, pressure tiers, scores, probabilities, and rank order are unchanged.
- **Validation:** All 25 regression tests passed. Re-ran the full 10,000-sample uncertainty pipeline with seed `20260808`; all nine built-in sanity checks passed, including the new `source_consistency_followup_preserved` invariant. Confirmed the GN-11836 row has matching source-consistency categories and the specific clarification reason. Confirmed uncertainty rank mappings are unchanged and ran `git diff --check`.
- **Status:** Complete and present in repository commit `35aeab7` (`data flag update`).

### 2026-08-17 - Harden source-consistency ranking and validation

- **Objective:** Fix the two dormant uncertainty-ranking defects identified during the repository-wide review: source-consistency priorities could be overwritten by derived pressure or host-ratio categories, and the production verifier incorrectly required at least one source inconsistency to exist.
- **Files changed:**
  - `scripts/generate_v1_uncertainty_rankings.py` (modified)
  - `tests/test_v1_pipeline.py` (modified)
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
- **Contribution:** Moved `D_source_consistency` to the first branch of the uncertainty follow-up categorizer so values awaiting source clarification remain quarantined regardless of their derived growth-pressure or host-ratio tiers. Changed the verification invariant to treat a catalogue with no source inconsistencies as valid while still requiring every inconsistency that does exist to preserve its category. Added regression cases that combine source inconsistency with likely high pressure and an extreme host ratio, and that verify a synthetic clean catalogue containing no source inconsistencies.
- **Scientific/technical effect:** Future source-inconsistent rows cannot be promoted to a physical-pressure or host-tension category before their inputs are clarified, and valid clean catalogues no longer fail production verification. Current v1 uncertainty probabilities, scores, categories, ranks, and result tables are unchanged.
- **Validation:** Re-ran the deterministic 10,000-sample uncertainty pipeline with seed `20260808`; all nine production sanity checks passed and Git showed no changes to the three regenerated uncertainty result tables. All 27 regression tests passed, including both new synthetic edge cases. `git diff --check` passed.
- **Status:** Complete and present in repository commit `15aea4a` (`fix consistencies`).

### 2026-08-17 - Normalize v1/v2/v3 release naming

- **Objective:** Make repository filenames and embedded metadata follow the actual project chronology: v1 pilot catalogue/evaluation, v2 analysis on the frozen v1 catalogue, and v3 JADES + Taylor CEERS/RUBIES expansion.
- **Files changed:**
  - `README.md` (modified)
  - `docs/guides/getting-started.md` (modified)
  - `docs/guides/release-versioning.md` (added)
  - `.codex_tmp/catalogue-expansion-guide.md` (modified)
  - `.codex_tmp/observational-atlas-roadmap.md` (modified)
  - `.codex_tmp/research-grade-observational-atlas-roadmap-detailed.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (modified)
  - `data/crossmatch/measurement_object_links.csv` -> `data/crossmatch/v3/v3_measurement_object_links.csv` (renamed)
  - `data/processed/expanded_blagn_measurements.csv` -> `data/processed/v3/v3_blagn_measurements.csv` (renamed and release metadata updated)
  - `data/processed/expanded_blagn_objects.csv` -> `data/processed/v3/v3_blagn_objects.csv` (renamed and release metadata updated)
  - `docs/expanded-blagn-catalogue-schema.md` -> `docs/archive/releases/v3/v3-blagn-catalogue-schema.md` (renamed and modified)
  - `docs/expanded-blagn-science-workflow.md` -> `docs/archive/releases/v3/v3-blagn-science-workflow.md` (renamed and modified)
  - `docs/v1-figure-inventory.md` -> `docs/archive/releases/v2/v2-figure-inventory.md` (renamed and modified)
  - `docs/v1-ranking-metrics.md` -> `docs/archive/releases/v2/v2-ranking-metrics.md` (renamed and modified)
  - `docs/v1-uncertainty-propagation.md` -> `docs/archive/releases/v2/v2-uncertainty-propagation.md` (renamed and modified)
  - `docs/v2-candidate-black-hole-papers.md` -> `docs/archive/legacy/catalogue-expansion-candidates-legacy.md` (renamed and marked as a legacy planning memo)
  - `scripts/generate_v1_rankings.py` -> `scripts/generate_v2_rankings.py` (renamed and modified)
  - `scripts/generate_v1_uncertainty_rankings.py` -> `scripts/generate_v2_uncertainty_rankings.py` (renamed and modified)
  - `scripts/generate_v1_final_figures.py` -> `scripts/generate_v2_final_figures.py` (renamed and modified)
  - `scripts/process_expanded_blagn.py` -> `scripts/process_v3_blagn.py` (renamed and modified)
  - `scripts/generate_expanded_blagn_science.py` -> `scripts/generate_v3_blagn_science.py` (renamed and modified)
  - `src/expanded_catalogue.py` -> `src/v3_catalogue.py` (renamed and modified)
  - `src/expanded_science.py` -> `src/v3_science.py` (renamed and modified)
  - `tests/test_v1_pipeline.py` -> `tests/test_v1_v2_pipeline.py` (renamed and modified)
  - `tests/test_expanded_blagn_pipeline.py` -> `tests/test_v3_blagn_pipeline.py` (renamed and modified)
  - `tests/test_expanded_blagn_science.py` -> `tests/test_v3_blagn_science.py` (renamed and modified)
  - `results/v1_object_ranking_table.csv` -> `results/releases/v2/tables/v2_object_ranking_table.csv` (renamed and release metadata updated)
  - `results/v1_uncertainty_aware_ranking_table.csv` -> `results/releases/v2/tables/v2_uncertainty_aware_ranking_table.csv` (renamed and release metadata updated)
  - `results/v1_uncertainty_required_fedd_summary.csv` -> `results/releases/v2/tables/v2_uncertainty_required_fedd_summary.csv` (renamed and release metadata updated)
  - `results/v1_uncertainty_required_mseed_summary.csv` -> `results/releases/v2/tables/v2_uncertainty_required_mseed_summary.csv` (renamed and release metadata updated)
  - `results/v1_main_text_figures/v1_main_text_mbh_redshift_growth_overview.png` -> `results/releases/v2/figures/main_text/v2_main_text_mbh_redshift_growth_overview.png` (renamed)
  - `results/v1_main_text_figures/v1_main_text_pressure_vs_confidence.png` -> `results/releases/v2/figures/main_text/v2_main_text_pressure_vs_confidence.png` (renamed)
  - `results/v1_main_text_figures/v1_main_text_ranked_required_fedd.png` -> `results/releases/v2/figures/main_text/v2_main_text_ranked_required_fedd.png` (renamed)
  - `results/v1_main_text_figures/v1_main_text_ranked_required_seed_mass.png` -> `results/releases/v2/figures/main_text/v2_main_text_ranked_required_seed_mass.png` (renamed)
  - `results/v1_main_text_figures/v1_main_text_spotlight_seed_redshift_maps.png` -> `results/releases/v2/figures/main_text/v2_main_text_spotlight_seed_redshift_maps.png` (renamed)
  - `results/v1_main_text_figures/v1_main_text_uncertainty_forest.png` -> `results/releases/v2/figures/main_text/v2_main_text_uncertainty_forest.png` (renamed)
  - `results/expanded_blagn_catalogue_summary.csv` -> `results/releases/v3/tables/v3_blagn_catalogue_summary.csv` (renamed)
  - `results/expanded_blagn_growth_summary.csv` -> `results/releases/v3/tables/v3_blagn_growth_summary.csv` (renamed)
  - `results/expanded_blagn_measurement_evaluation.csv` -> `results/releases/v3/tables/v3_blagn_measurement_evaluation.csv` (renamed)
  - `results/expanded_blagn_measurement_point_ranking.csv` -> `results/releases/v3/tables/v3_blagn_measurement_point_ranking.csv` (renamed)
  - `results/expanded_blagn_measurement_uncertainty_fedd.csv` -> `results/releases/v3/tables/v3_blagn_measurement_uncertainty_fedd.csv` (renamed)
  - `results/expanded_blagn_measurement_uncertainty_mseed.csv` -> `results/releases/v3/tables/v3_blagn_measurement_uncertainty_mseed.csv` (renamed)
  - `results/expanded_blagn_measurement_uncertainty_ranking.csv` -> `results/releases/v3/tables/v3_blagn_measurement_uncertainty_ranking.csv` (renamed)
  - `results/expanded_blagn_physical_object_evaluation.csv` -> `results/releases/v3/tables/v3_blagn_physical_object_evaluation.csv` (renamed)
  - `results/expanded_blagn_physical_object_point_ranking.csv` -> `results/releases/v3/tables/v3_blagn_physical_object_point_ranking.csv` (renamed)
  - `results/expanded_blagn_physical_object_uncertainty_fedd.csv` -> `results/releases/v3/tables/v3_blagn_physical_object_uncertainty_fedd.csv` (renamed)
  - `results/expanded_blagn_physical_object_uncertainty_mseed.csv` -> `results/releases/v3/tables/v3_blagn_physical_object_uncertainty_mseed.csv` (renamed)
  - `results/expanded_blagn_physical_object_uncertainty_ranking.csv` -> `results/releases/v3/tables/v3_blagn_physical_object_uncertainty_ranking.csv` (renamed)
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
- **Contribution:** Added a canonical release-version map and renamed release-specific code, tests, documentation, processed catalogues, rankings, summaries, and v2 figure prototypes. Added `analysis_release=v2` and `input_catalogue_release=v1` to v2 tables, standardized Taylor rows as `project_version=v3`, retained `catalogue_release=v3-blagn`, and updated every live reference. Source-specific raw extractions remain descriptively named because their paper/arXiv versions are separate provenance dimensions. Updated the roadmaps and status paper to the completed v3 state.
- **Scientific/technical effect:** No v1 source or processed data changed, no object was added or removed, and no growth assumptions or rank calculations changed. The current release is now unambiguously v3: 60 measurements representing 59 physical objects at `z>=4`; v2 remains the reproducible pre-expansion analysis of the 23-row v1 catalogue.
- **Validation:** Rebuilt the v3 processed catalogue (63 Taylor source rows; 37 Taylor measurements / 36 Taylor objects at `z>=4`; 60 combined measurements / 59 physical objects), regenerated all v2 and v3 CSV products with 10,000 samples and seed `20260808`, and passed all 53 regression tests. Confirmed the v1 raw and processed SHA-256 anchors remain byte-identical, checked live references for retired names, rebuilt the 10-page status PDF, rendered every page, and visually verified layout and legibility. `git diff --check` passed.
- **Status:** Complete and present in repository commit `2c438d1` (`update consistencies`).

### 2026-08-22 - Complete v3 figures and add the v4 same-class BLAGN expansion

- **Objective:** Apply roadmap changes 1--4: repository release hygiene, the
  frozen-v3 main-text figure set and living status paper, generalized
  measurement/physical-object identity handling, and authoritative Matthee
  EIGER/FRESCO plus Lin ASPIRE broad-Halpha ingestion and science products.
- **Files changed:**
  - `.gitignore` (added)
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
  - `.codex_tmp/catalogue-expansion-guide.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (modified)
  - `.codex_tmp/observational-atlas-roadmap.md` (modified)
  - `.codex_tmp/research-grade-observational-atlas-roadmap-detailed.md` (modified)
  - `.codex_tmp/matplotlib/fontlist-v3.11.0.json` (deleted generated cache)
  - `README.md` (modified)
  - `data/sources.md` (modified)
  - `data/raw/matthee23_eiger_fresco_blagn_tables1_3.csv` (added)
  - `data/raw/lin24_aspire_blagn_tables1_3.csv` (added)
  - `data/processed/v4/v4_blagn_measurements.csv` (added)
  - `data/processed/v4/v4_blagn_objects.csv` (added)
  - `data/crossmatch/v4/v4_measurement_object_links.csv` (added)
  - `data/crossmatch/v4/v4_object_aliases.csv` (added)
  - `data/crossmatch/v4/v4_reviewed_match_candidates.csv` (added)
  - `docs/guides/getting-started.md` (modified)
  - `docs/guides/release-versioning.md` (modified)
  - `docs/archive/releases/v3/v3-blagn-catalogue-schema.md` (modified)
  - `docs/archive/releases/v3/v3-blagn-science-workflow.md` (modified)
  - `docs/source-notes/matthee23-eiger-fresco-extraction-notes.md` (added)
  - `docs/source-notes/lin24-aspire-extraction-notes.md` (added)
  - `docs/archive/releases/v4/v4-blagn-catalogue-schema.md` (added)
  - `docs/archive/releases/v4/v4-blagn-science-workflow.md` (added)
  - `scripts/generate_v3_final_figures.py` (added)
  - `scripts/process_v4_blagn.py` (added)
  - `scripts/generate_v4_blagn_science.py` (added)
  - `src/identity.py` (added)
  - `src/v4_catalogue.py` (added)
  - `src/v4_science.py` (added)
  - `tests/test_v4_blagn_pipeline.py` (added)
  - `tests/test_v4_blagn_science.py` (added)
  - `results/releases/v3/figures/main_text/v3_main_text_mbh_redshift_growth_overview.png` (added)
  - `results/releases/v3/figures/main_text/v3_main_text_ranked_required_fedd.png` (added)
  - `results/releases/v3/figures/main_text/v3_main_text_uncertainty_forest.png` (added)
  - `results/releases/v3/figures/main_text/v3_main_text_source_stratified_coverage.png` (added)
  - `results/releases/v4/tables/v4_blagn_catalogue_summary.csv` (added)
  - `results/releases/v4/tables/v4_blagn_growth_summary.csv` (added)
  - `results/releases/v4/tables/v4_blagn_measurement_evaluation.csv` (added)
  - `results/releases/v4/tables/v4_blagn_measurement_point_ranking.csv` (added)
  - `results/releases/v4/tables/v4_blagn_measurement_uncertainty_fedd.csv` (added)
  - `results/releases/v4/tables/v4_blagn_measurement_uncertainty_mseed.csv` (added)
  - `results/releases/v4/tables/v4_blagn_measurement_uncertainty_ranking.csv` (added)
  - `results/releases/v4/tables/v4_blagn_physical_object_evaluation.csv` (added)
  - `results/releases/v4/tables/v4_blagn_physical_object_point_ranking.csv` (added)
  - `results/releases/v4/tables/v4_blagn_physical_object_uncertainty_fedd.csv` (added)
  - `results/releases/v4/tables/v4_blagn_physical_object_uncertainty_mseed.csv` (added)
  - `results/releases/v4/tables/v4_blagn_physical_object_uncertainty_ranking.csv` (added)
  - `scripts/.ipynb_checkpoints/v1_evaluate-checkpoint.ipynb` (deleted generated checkpoint)
  - `scripts/__pycache__/generate_catalogue.cpython-312.pyc` (deleted generated cache)
  - `scripts/__pycache__/generate_v1_rankings.cpython-312.pyc` (deleted generated cache)
  - `scripts/__pycache__/generate_v1_uncertainty_rankings.cpython-312.pyc` (deleted generated cache)
  - `scripts/__pycache__/process_data.cpython-312.pyc` (deleted generated cache)
  - `src/__pycache__/__init__.cpython-312.pyc` (deleted generated cache)
  - `src/__pycache__/models.cpython-312.pyc` (deleted generated cache)
  - `src/__pycache__/scoring.cpython-312.pyc` (deleted generated cache)
  - `src/__pycache__/standardize_data.cpython-312.pyc` (deleted generated cache)
  - `tests/__pycache__/test_v1_pipeline.cpython-312.pyc` (deleted generated cache)
- **Contribution:** Transcribed all 20 Matthee Tables 1--3 rows and all 16 Lin
  Tables 1--3 rows from authoritative arXiv source archives, with coordinates,
  redshifts, line measurements, formal asymmetric errors, source-native
  luminosities, Reines et al. (2013) mass-method metadata, separate 0.5 dex
  calibration systematics, LRD provenance, absorption-fit flags, and row
  caveats. Added reusable coordinate/redshift candidate matching, stable
  physical-object IDs, aliases, explicit ambiguity rejection, and a
  prior-release preference-continuity rule. Added v4 measurement/object
  evaluation, point-ranking, Monte Carlo ranking, and stratified-summary
  products while leaving v1--v3 artifacts separate. Added four frozen-v3
  main-text figures and updated the status paper, release map, run guide,
  schemas, source registry, and roadmaps. Removed tracked generated caches and
  added ignore rules preventing recurrence.
- **Scientific/technical effect:** v4 contains 96 measurements representing 94
  physical objects at `z >= 4` and is now the current catalogue and science
  release. The 36 new literature rows add 35 physical
  objects because Matthee GOODS-S-13971 is linked to JADES GS-204851; both
  measurements remain present and the prior JADES default is retained. The
  earlier CEERS-2782/RUBIES-EGS-50052 pair remains one physical object. Baseline
  assumptions remain `z_seed=30`, `epsilon=0.1`, `merger_boost=1`, with reported
  asymmetric statistical errors, global +/-0.3 dex comparisons, and separately
  labelled Taylor/Matthee/ASPIRE +/-0.5 dex calibration sensitivities. The mass
  and redshift extrema are unchanged from v3, but coverage is denser at
  `z approximately 4.2--5.5`; Matthee GOODS-N-9771 enters the object-level
  uncertainty-pressure ranking at rank 4. Overall source/LRD summaries remain
  descriptive because the surveys have unlike selection functions.
- **Validation:** Verified the source archives as Matthee arXiv `2306.05448v3`
  (SHA-256 `b3e6f5385e694d92a7456f81eb123a305468baf743cebc7aeea820befb9b1190`)
  and Lin arXiv `2407.17570v1` (SHA-256
  `fc1c4d96e4a568b09b3caefa0fdde1c7fabe8decad71fb6423ff37c912b024cd`).
  Compared the new CSVs against the authoritative TeX tables, imported both
  into a spreadsheet QA workbook, scanned for formula errors, rendered sample
  ranges, and visually inspected them. Regenerated 96 measurement and 94
  physical-object rows, all v4 science products with 10,000 Monte Carlo draws
  and seed `20260808`, and restored v2's canonical 10,000-draw products after
  the test fixture. All 70 regression tests passed. Frozen v3 catalogue hashes
  remain `7df69c0a...1b76` (measurements) and `5c67d8a8...2126` (objects).
  Recompiled the 12-page status PDF and visually inspected every rendered page.
  `git diff --check` passed.
- **Status:** Complete and present in repository commit `da28d37` (`documentation consistency`).

### 2026-08-22 - Reconcile current v4 documentation

- **Objective:** Correct the remaining documentation inconsistencies identified
  in the post-v4 review without changing code, catalogue rows, rankings, or
  generated science products.
- **Files changed:**
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
  - `.codex_tmp/catalogue-expansion-guide.md` (modified)
  - `.codex_tmp/research-grade-observational-atlas-roadmap-detailed.md` (modified)
  - `README.md` (modified)
  - `data/sources.md` (modified)
  - `docs/guides/getting-started.md` (modified)
  - `docs/guides/release-versioning.md` (modified)
  - `docs/archive/releases/v4/v4-blagn-catalogue-schema.md` (modified)
  - `docs/archive/releases/v4/v4-blagn-science-workflow.md` (modified)
- **Contribution:** Made v4 the primary onboarding and minimal-reproduction
  path; updated the verification-suite description from v1--v3 to v1--v4;
  corrected the pre-implementation Matthee and ASPIRE source descriptions;
  distinguished completed, historical, and immediate-next roadmap material;
  and documented that v4 science tables are current while the latest
  release-specific figures remain frozen v3 products. Expanded the v4 schema
  with exact raw/processed/crossmatch inventories, identity/default rules,
  matching thresholds, field groups, missingness policy, LRD evidence
  provenance, quality semantics, and validation anchors. Expanded the v4
  science guide with catalogue-view rules, scenario scopes, exact output row
  counts, missing-diagnostic interpretation, and verification commands.
- **Scientific/technical effect:** Documentation now matches the implemented
  source selections and data semantics. In particular, Matthee is described as
  line-selected rather than compact/red preselected; ASPIRE no longer claims a
  tabulated source-reported Eddington ratio or dust correction; Matthee's LRD
  status is explicitly paper-level; and `robust` is identified as broad-line
  detection confidence rather than a guarantee that absorption, contamination,
  or virial-mass caveats are absent. No scientific value, identity assignment,
  rank, or release artifact changed.
- **Validation:** Confirmed every exact repository path referenced by the core
  documentation exists. Compared all documented v4 row counts against the
  current CSVs: 96 measurements, 94 objects, 96 links, 96 aliases, one reviewed
  candidate and the 12 products that existed at that contribution all matched;
  the corrected v4 freeze subsequently added a thirteenth sensitivity product.
  Searched for the stale source/release phrases corrected here and found
  no live occurrences. `git diff --check` passed. Regression tests were not
  rerun because this contribution changes documentation only.
- **Status:** Complete and present in repository commit `da28d37` (`documentation consistency`).

### 2026-08-22 - Correct and freeze the v4 BLAGN release

- **Objective:** Apply the post-review fixes in order: separate detection
  confidence from mass/line-model reliability, require explicit reviewed
  identity decisions with pairwise new-source matching, preserve phenotype
  source attribution, quantify both duplicate-measurement choices, complete
  v4 figures/manuscript documentation, and freeze the corrected release.
- **Files changed:**
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (modified)
  - `.codex_tmp/observational-atlas-roadmap.md` (modified)
  - `.codex_tmp/research-grade-observational-atlas-roadmap-detailed.md` (modified)
  - `README.md` (modified)
  - `data/crossmatch/v4/v4_reviewed_identity_overrides.csv` (added)
  - `data/crossmatch/v4/v4_reviewed_match_candidates.csv` (modified)
  - `data/processed/v4/v4_blagn_objects.csv` (modified)
  - `docs/guides/getting-started.md` (modified)
  - `docs/guides/release-versioning.md` (modified)
  - `docs/archive/releases/v2/v2-figure-inventory.md` (modified)
  - `docs/archive/releases/v4/v4-blagn-catalogue-schema.md` (modified)
  - `docs/archive/releases/v4/v4-blagn-science-workflow.md` (modified)
  - `results/releases/v4/tables/v4_blagn_alternate_measurement_sensitivity.csv` (added)
  - `results/releases/v4/tables/v4_blagn_catalogue_summary.csv` (modified)
  - `results/releases/v4/tables/v4_blagn_measurement_point_ranking.csv` (modified)
  - `results/releases/v4/tables/v4_blagn_measurement_uncertainty_ranking.csv` (modified)
  - `results/releases/v4/tables/v4_blagn_physical_object_point_ranking.csv` (modified)
  - `results/releases/v4/tables/v4_blagn_physical_object_uncertainty_ranking.csv` (modified)
  - `results/releases/v4/figures/main_text/v4_main_text_mbh_redshift_growth_overview.png` (added)
  - `results/releases/v4/figures/main_text/v4_main_text_ranked_required_fedd.png` (added)
  - `results/releases/v4/figures/main_text/v4_main_text_uncertainty_forest.png` (added)
  - `results/releases/v4/figures/main_text/v4_main_text_source_stratified_coverage.png` (added)
  - `results/releases/v4/figures/main_text/v4_main_text_measurement_choice_sensitivity.png` (added)
  - `scripts/generate_v4_blagn_science.py` (modified)
  - `scripts/generate_v4_final_figures.py` (added)
  - `scripts/process_v4_blagn.py` (modified)
  - `src/identity.py` (modified)
  - `src/v4_catalogue.py` (modified)
  - `src/v4_science.py` (modified)
  - `tests/test_v4_blagn_pipeline.py` (modified)
  - `tests/test_v4_blagn_science.py` (modified)
- **Contribution:** Added independent `detection_confidence_*` and
  `mass_measurement_reliability_*` fields and recalculated v4-only follow-up
  categories/ranks so absorption, alternative-interpretation, and contamination
  caveats no longer fall through as uniformly high-reliability measurements.
  Added prior-release and same-release cross-source candidate generation plus a
  mandatory accepted/rejected override registry; the sole current candidate
  remains GOODS-S-13971 = GS-204851. Added preferred-measurement LRD state and
  measurement/source evidence fields so source summaries do not silently
  attribute another paper's phenotype. Added a two-row, one-object-at-a-time
  sensitivity product for both multiply measured objects. Added five v4
  publication-style figures and consolidated the living status manuscript and
  release documentation. No Harikane rows were ingested into this freeze.
- **Scientific/technical effect:** The catalogue remains 96 measurements / 94
  physical objects, with unchanged default measurements and source counts.
  GN-38509 and GS-20057765 remain growth-pressure ranks 1 and 2. RUBIES-EGS-49140
  and GOODS-N-9771 remain ranks 3 and 4 but now carry explicit interpretive or
  line-model reliability caveats while retaining high detection confidence.
  Replacing the default RUBIES-EGS-50052 with CEERS-2782 changes the object's
  mass by -0.42 dex and growth-pressure rank 28 to 46; replacing JADES GS-204851
  with Matthee GOODS-S-13971 changes the mass by -0.19 dex and rank 17 to 22.
  These substitutions are sensitivities only and do not change the release
  defaults. Mixed-selection summaries remain descriptive, not demographic.
- **Validation:** Rebuilt v4 catalogue products, all 13 v4 science tables with
  10,000 Monte Carlo draws and seed `20260808`, and all five v4 figures. All 74
  regression tests passed. Confirmed the frozen-v3 SHA-256 anchors remain
  `7df69c0a...1b76` and `5c67d8a8...2126`, restored the canonical v2 10,000-draw
  outputs after test fixtures, and ran `git diff --check`. Recompiled the
  14-page status PDF without TeX warnings, rendered every page, and visually
  inspected the complete document and all five standalone v4 figures.
- **Status:** Complete in repository commit `371c08f` (`Correct and freeze v4
  BLAGN release`) and frozen by annotated tag `v4-blagn`.

### 2026-08-23 - Harden and reproduce the v4.0.1 maintenance release

- **Objective:** Resolve the five remaining post-freeze maintenance issues and
  complete the recommended reproducibility gate without changing v4 science.
- **Files changed:**
  - `.github/workflows/ci.yml` (added)
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (rebuilt)
  - `.codex_tmp/observational-atlas-roadmap.md` (modified)
  - `.codex_tmp/research-grade-observational-atlas-roadmap-detailed.md` (modified)
  - `README.md` (modified)
  - `pyproject.toml` (added)
  - `requirements-lock.txt` (added)
  - `releases/v4.0.1-manifest.json` (added)
  - `data/crossmatch/v4/v4_reviewed_identity_overrides.csv` (modified)
  - `data/crossmatch/v4/v4_reviewed_match_candidates.csv` (metadata column added)
  - `data/mass_method_registry.csv` (added)
  - `data/sources.md` (modified)
  - `docs/guides/getting-started.md` (modified)
  - `docs/reference/model-menu.md` (modified)
  - `docs/guides/release-versioning.md` (modified)
  - `docs/archive/releases/v4/v4-blagn-catalogue-schema.md` (modified)
  - `docs/archive/releases/v4/v4-blagn-science-workflow.md` (modified)
  - `scripts/generate_v2_uncertainty_rankings.py` (modified)
  - `scripts/verify_v4_release.py` (added)
  - `src/identity.py` (modified)
  - `src/mass_systematics.py` (added)
  - `src/v4_catalogue.py` (modified)
  - `tests/test_maintenance_release.py` (added)
  - `tests/test_v4_blagn_pipeline.py` (modified)
- **Contribution:** Pinned the Python 3.12 runtime dependencies; added CI, a
  SHA-256 release manifest, and a write-free full v4 in-memory reproduction
  command. Hardened future physical-ID allocation against normalized-token
  collisions and added documented manual identity assertions outside numerical
  candidate thresholds while retaining mandatory review metadata. Added a
  source/method virial registry covering every v4 pair. Primary JADES Section 4
  supports Reines & Volonteri (2015) Halpha with a 0.3 dex calibration
  uncertainty and Vestergaard & Peterson (2006) Hbeta without a source-stated
  numeric systematic; the latter remains blank. Corrected historical ledger
  commit statuses, superseded 12-product wording, current model-menu status,
  maintenance/science release mapping, and the v2 verifier's misleading
  in-memory `Wrote` messages.
- **Scientific/technical effect:** Existing v1--v4 measurements, physical IDs,
  preferred measurements, science values, Monte Carlo settings, ranks, and
  figures are unchanged. The sole reviewed candidate gains
  `match_origin=threshold_candidate`; method metadata are descriptive and are
  not silently combined with statistical errors or used to create new
  scenarios. `v4-blagn` remains the science tag and `v4.0.1` is a maintenance
  tag.
- **Validation:** All 79 regression tests passed. Verified all 18 manifest
  hashes and reproduced the five catalogue/identity plus 13 science CSVs in
  memory at 10,000 draws and seed `20260808`, without writing them. Confirmed
  96 measurements, 94 physical objects, unchanged frozen science hashes, and a
  clean `git diff --check`. Rebuilt the 14-page status PDF without TeX warnings,
  rendered every page, and visually verified the complete document.
- **Status:** Complete in the v4.0.1 maintenance commit and annotated tag
  `v4.0.1`; the `v4-blagn` science tag remains unchanged.

### 2026-08-23 - Add Harikane measurement versions and v5 taxonomy foundation

- **Objective:** Complete the next same-class measurement layer after v4,
  preserve every prior release, audit current manuscript claims, and establish
  class-aware metadata before any heterogeneous-candidate ingestion.
- **Files changed:**
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
  - `.codex_tmp/catalogue-expansion-guide.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (rebuilt)
  - `.codex_tmp/observational-atlas-roadmap.md` (modified)
  - `.codex_tmp/research-grade-observational-atlas-roadmap-detailed.md` (modified)
  - `README.md` (modified)
  - `data/raw/harikane23_nirspec_blagn_tables1_3.csv` (added)
  - `data/processed/v5/v5_blagn_measurements.csv` (added)
  - `data/processed/v5/v5_blagn_objects.csv` (added)
  - `data/crossmatch/v5/v5_measurement_object_links.csv` (added)
  - `data/crossmatch/v5/v5_object_aliases.csv` (added)
  - `data/crossmatch/v5/v5_reviewed_identity_overrides.csv` (added)
  - `data/crossmatch/v5/v5_reviewed_match_candidates.csv` (added)
  - `data/mass_method_registry.csv` (modified)
  - `data/sources.md` (modified)
  - `docs/guides/getting-started.md` (modified)
  - `docs/guides/release-versioning.md` (modified)
  - `docs/archive/releases/v2/v2-figure-inventory.md` (modified)
  - `docs/source-notes/harikane23-nirspec-extraction-notes.md` (added)
  - `docs/reference/object-taxonomy.md` (added)
  - `docs/archive/releases/v5/v5-blagn-catalogue-schema.md` (added)
  - `docs/archive/releases/v5/v5-blagn-science-workflow.md` (added)
  - `docs/archive/releases/v5/v5-manuscript-claim-audit.md` (added)
  - `scripts/process_v5_blagn.py` (added)
  - `scripts/generate_v5_blagn_science.py` (added)
  - `src/object_taxonomy.py` (added)
  - `src/v5_catalogue.py` (added)
  - `src/v5_science.py` (added)
  - `tests/test_v5_blagn_pipeline.py` (added)
  - `tests/test_v5_blagn_science.py` (added)
  - 13 `results/releases/v5/tables/v5_blagn_*.csv` science products (added)
- **Contribution:** Extracted all ten final-sample rows from the authoritative
  Harikane et al. (2023) ApJ/arXiv v3 Tables 1--3 source archive, preserving
  coordinates, selection diagnostics, broad-Halpha quantities, Greene & Ho
  (2005) masses, bolometric luminosities, Eddington ratios, host measurements
  and upper limits, phenotype descriptions, caveats, and provenance. Reviewed
  six coordinate/redshift candidates and linked five Harikane measurements to
  five existing CEERS physical objects; five new stable objects were allocated.
  Added orthogonal evidence/type/selection/phenotype/lensing/ranking axes and a
  non-breaking v5 science workflow. Harikane rows receive reported asymmetric
  statistical propagation and the common +/-0.3 dex comparison only; no
  numeric source-specific systematic or LRD marker was invented. Updated the
  roadmaps, release map, source registry, reproduction instructions, claim
  audit, and living manuscript. No release tag was created.
- **Scientific/technical effect:** v5 contains 106 measurements representing 99
  physical objects. CEERS-2782/RUBIES-EGS-50052/Harikane CEERS-02782 are three
  measurements of one physical object, with the prior RUBIES default retained.
  Five Harikane physical objects are new. The prior v4 point-ranking top three
  remain unchanged; Harikane CEERS-00717 enters point rank 4 and uncertainty
  rank 5. Overall mixed-selection summaries remain descriptive and explicitly
  prohibit demographic inference. Every v1--v4 artifact remains unchanged.
- **Validation:** Rebuilt five v5 catalogue/identity products and all 13 v5
  science tables with 10,000 Monte Carlo draws and seed `20260808`. Verified
  exact counts (464/439 evaluation, 1,392/1,317 required-fEdd, 928/878
  required-seed, and seven alternate-measurement rows), unique ranks, scenario
  separation, missingness behavior, identity linkage, and source provenance.
  All 93 regression tests passed. The v4.0.1 verifier reproduced all frozen v4
  products in memory and confirmed all 18 hashes. `git diff --check` passed.
  Rebuilt the 15-page status PDF without TeX warnings, rendered all pages, and
  visually inspected the full document.
- **Status:** Complete in commit `9a1fa3d` (`v5`) and pushed to `origin/main`.

### 2026-08-24 - Expand the status paper into a detailed repository tour

- **Objective:** Update the living status document so it gives a detailed,
  newcomer-oriented tour of the repository's important scientific, data,
  software, release, and validation components, with visual explanations.
- **Files changed:**
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (rebuilt)
- **Contribution:** Retitled and refreshed the report, added a one-way data-flow
  diagram, a full directory map, a measurement-versus-physical-object identity
  diagram, a module-by-module implementation tour, a reproducibility walkthrough,
  current repository scale and source-composition summaries, and a v5 top-five
  growth-pressure table. Preserved the chronological science narrative, existing
  release-specific figures, limitations, roadmap, and bibliography. Added running
  headers and consistent page numbering for navigation.
- **Scientific/technical effect:** No catalogue, identity, model, ranking, or
  result artifact changed. The documentation now makes the repository architecture,
  frozen-v4/current-v5 distinction, uncertainty policy, and release gates easier to
  audit; all scientific numbers are drawn from the current checked-in v5 tables and
  existing verified documentation.
- **Validation:** All 93 regression tests passed. The v4.0.1 verifier confirmed all
  18 frozen hashes and reproduced the frozen catalogue/science products in memory.
  Tectonic compiled the 19-page PDF without warnings. All pages were rendered to
  PNG, reviewed as contact sheets, and the dense directory, module, source-count,
  ranking, and dependency-map pages were inspected at full resolution with no
  clipping, overlap, or illegible content.
- **Status:** Complete in commit `184b4c8` (`v5 documentation`) and pushed to
  `origin/main`.

### 2026-08-24 - Restore the scientific status-manuscript direction

- **Objective:** Revise the status-paper update so it preserves the earlier
  scientific narrative and formatting rather than presenting a literal tour of
  repository directories and modules.
- **Files changed:**
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (rebuilt)
- **Contribution:** Removed the repository-at-a-glance section, architecture and
  identity boxes, directory/module catalogues, reproduction walkthrough, and
  navigation-specific header styling. Restored the original project-status title,
  abstract direction, section flow, typography, and page furniture. Retained only
  two concise current-v5 additions: the literature-source measurement/object
  composition and the present point-versus-uncertainty top-five ranking summary.
- **Scientific/technical effect:** The report again reads as a chronological
  scientific status manuscript while incorporating current v5 evidence. No data,
  identity, model, ranking, or other result artifact changed.
- **Validation:** All 93 regression tests passed, and the v4.0.1 verifier confirmed
  every frozen hash plus in-memory reproduction. Tectonic compiled the final
  15-page PDF without warnings. Every page was rendered and reviewed; the two new
  tables were additionally inspected at full resolution with no clipping, overlap,
  or legibility problems.
- **Status:** Complete in commit `184b4c8` (`v5 documentation`) and pushed to
  `origin/main`.

### 2026-08-24 - Complete the v5 evidence and reproducibility gate

- **Objective:** Resolve the remaining review findings with the smallest
  non-breaking v5-only changes before any heterogeneous v6 expansion.
- **Files changed:** v5 taxonomy/catalogue/science modules and tests; the v5
  processed catalogue and science CSVs; CI, source/schema/workflow/release
  documentation and roadmaps; `scripts/verify_v5_release.py`; and
  `releases/v5-manifest.json`.
- **Contribution:** Separated robust line detection from secure accreting-MBH
  interpretation with an auditable evidence basis; enforced growth eligibility;
  propagated taxonomy through evaluation and uncertainty products; added
  taxonomy summary strata; unioned phenotype evidence across linked
  measurements; recorded the Harikane `0.2 dex` host-mass systematic without
  applying it; corrected mixed-selection and roadmap language; and added an
  exact v5 hash/reproduction gate to CI.
- **Scientific/technical effect:** All 106 measurements and 99 physical objects
  remain eligible and retain identical numerical values and ranks. Evidence
  labels are now 96 secure, nine probable, and one candidate. No v1--v4
  artifact or figure changed.
- **Validation:** All 98 regression tests passed. Both the frozen v4.0.1 and
  current v5 verifiers reproduced all 18 artifacts in memory. Independent
  comparison against the prior v5 files confirmed unchanged IDs, ranks, and
  every common numerical ranking column to `1e-12`. `git diff --check` passed.
- **Status:** Complete in commit `184b4c8` (`v5 documentation`) and pushed to
  `origin/main`.

### 2026-08-24 - Make release reproduction cross-platform

- **Objective:** Correct the GitHub Actions failure caused by final-bit
  floating-point differences between macOS/ARM and Ubuntu/x86 without weakening
  frozen-artifact integrity checks.
- **Files changed:** `scripts/reproduction.py`, both release verifiers, the v4
  catalogue regression test, focused maintenance tests, and reproducibility
  documentation.
- **Contribution:** Retained byte-exact SHA-256 validation for checked-in
  artifacts while replacing platform-fragile generated-CSV string/hash
  comparisons with exact schema/order/text/boolean/missingness checks and
  floating comparison at `rtol=1e-13`, `atol=1e-14`.
- **Scientific/technical effect:** No catalogue, source extraction, identity,
  result CSV, manifest, rank, uncertainty value, or figure changed. A final-bit
  `numpy.log10` difference no longer causes a false CI failure, while meaningful
  numeric changes and any structural or nonnumeric change still fail.
- **Validation:** All 100 regression tests passed. Exact v4.0.1 and v5 manifest
  checks passed, and both releases reproduced all 18 artifacts in memory under
  the cross-platform comparison contract. `git diff --check` passed.
- **Status:** Complete across commits `f4ae2ac` (`reproducibility fixes`) and
  `e7ddfb0` (`reproducibility tests`), both pushed to `origin/main`.

### 2026-08-25 - Preserve three-state LRD and primary-ranking semantics

- **Objective:** Remove the remaining object-level phenotype ambiguity and
  make candidate participation in growth diagnostics explicit without deleting
  any literature measurement.
- **Files changed:** v5 taxonomy/catalogue/science modules, focused tests,
  current v5 processed and science CSVs, manifest, and concise taxonomy/workflow
  documentation.
- **Contribution:** Preserved LRD, explicit non-LRD, and not-reported states at
  physical-object level; conservatively aggregated linked-measurement evidence;
  retained all candidates in exploratory diagnostics while assigning primary
  ranks only to secure/probable evidence; and corrected committed ledger states.
- **Scientific/technical effect:** Catalogue membership, physical identities,
  growth calculations, and full diagnostic ranks remain unchanged. The primary
  evidence-supported population contains 105 measurements and 98 physical
  objects. Object-level LRD counts are 53 positive, 19 explicit negative, and
  27 not reported.
- **Validation:** All 105 regression tests passed. The frozen v4.0.1 and current
  v5 verifiers reproduced all 18 artifacts under the cross-platform comparison
  contract, and v5 manifest hashes match. Independent comparison with prior v5
  products confirmed unchanged IDs, full diagnostic ranks, and common numerical
  ranking fields to `1e-12`. `git diff --check` passed.
- **Status:** Complete in commit `d2b1731` (`fixing up`) and pushed to
  `origin/main`.

### 2026-08-25 - Consolidate paper-facing v5 and add accretion-history diagnostics

- **Objective:** Complete the documentation/primary-ranking cleanup and the
  first growth-history step before any heterogeneous v6 catalogue ingestion.
- **Files changed:** v5 science generator/module, shared growth model, focused
  tests, three new v5 result CSVs, v5 manifest, current workflow/versioning
  documentation and roadmaps, and the living status manuscript/PDF.
- **Contribution:** Added a canonical 99-object full-versus-primary paper table;
  implemented an effective two-state model with zero quiescent accretion and
  burst `f_Edd={1,2,3}`; propagated asymmetric statistical MBH errors into
  required-duty-cycle intervals and infeasibility probabilities; preserved
  current Eddington ratios as instantaneous comparison-only measurements; and
  made the manuscript's headline ranking primary-evidence-first.
- **Scientific/technical effect:** Catalogue membership and all v1--v4 artifacts
  remain unchanged. The full diagnostic population is 106 measurements / 99
  objects and the primary population is 105 / 98. The new history products have
  318 measurement rows and 297 object rows. At object level, the median required
  duty cycles for burst `f_Edd=1,2,3` are 0.574, 0.287, and 0.191; seven full
  diagnostic objects (six primary) exceed `D=1` for the unit-burst point
  scenario, explicitly marking that fixed scenario insufficient.
- **Validation:** All 108 regression tests passed. The frozen v4.0.1 and current
  v5 verifiers reproduced their complete artifact sets in memory, the updated
  v5 manifest hashes match, `git diff --check` passed, and the rebuilt 15-page
  status PDF was rendered and visually inspected. Hosted GitHub Actions run
  `32814549253` passed for the committed state.
- **Status:** Complete in commit `b73a241` (`v5 diagnostics`) and pushed to
  `origin/main`.

### 2026-08-25 - Complete the v5 science and manuscript consistency gate

- **Objective:** Resolve the remaining caveat-propagation, release-contract,
  figure-selection, chronology, citation, and documentation findings without
  changing v1--v4 artifacts or v5 catalogue membership/ranks.
- **Files changed:**
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
  - `.codex_tmp/catalogue-expansion-guide.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/observational-atlas-roadmap.md` (modified)
  - `.codex_tmp/research-grade-observational-atlas-roadmap-detailed.md` (modified)
  - `.github/workflows/ci.yml` (modified)
  - `README.md` (modified)
  - `docs/guides/getting-started.md` (modified)
  - `docs/reference/multiclass-eligibility-and-mass-comparability.md` (added)
  - `docs/guides/release-versioning.md` (modified)
  - `docs/archive/releases/v2/v2-uncertainty-propagation.md` (modified)
  - `docs/archive/releases/v3/v3-blagn-science-workflow.md` (modified)
  - `docs/archive/releases/v4/v4-blagn-science-workflow.md` (modified)
  - `docs/archive/releases/v5/v5-blagn-science-workflow.md` (modified)
  - `docs/archive/releases/v5/v5-figure-inventory.md` (added)
  - `docs/archive/releases/v5/v5-manuscript-citation-audit.md` (added)
  - `docs/archive/releases/v5/v5-manuscript-claim-audit.md` (modified)
  - `pyproject.toml` (modified)
  - `releases/v5-manifest.json` (modified)
  - `requirements-lock.txt` (modified)
  - `releases/v5-figures-manifest.json` (added)
  - `results/releases/v5/tables/v5_blagn_measurement_accretion_history.csv` (modified)
  - `results/releases/v5/tables/v5_blagn_physical_object_accretion_history.csv` (modified)
  - `results/releases/v5/tables/v5_blagn_primary_ranking_comparison.csv` (modified)
  - `results/releases/v5/figures/main_text/v5_appendix_measurement_choice_sensitivity.png` (added)
  - `results/releases/v5/figures/main_text/v5_main_text_accretion_history_diagnostics.png` (added)
  - `results/releases/v5/figures/main_text/v5_main_text_mbh_redshift_growth_overview.png` (added)
  - `results/releases/v5/figures/main_text/v5_main_text_primary_vs_full_ranking.png` (added)
  - `scripts/generate_v5_final_figures.py` (added)
  - `scripts/generate_v2_uncertainty_rankings.py` (modified)
  - `scripts/verify_v4_release.py` (modified)
  - `scripts/verify_v5_release.py` (modified)
  - `scripts/verify_v5_figures.py` (added)
  - `src/v5_science.py` (modified)
  - `tests/test_maintenance_release.py` (modified)
  - `tests/test_v5_blagn_science.py` (modified)
- **Contribution:** Retained GN-11836's published Eddington ratio while making
  its failed source-table consistency check an explicit exclusion from the
  current-to-required comparison; propagated method, evidence, systematic, and
  source caveats into accretion-history and paper-facing tables; required exact
  manifest membership; aligned package metadata with v5; generated a current
  three-main/one-appendix figure set; completed primary-source citation and
  multi-class admission contracts; and resolved chronology so v6 is the final
  same-class BLAGN consolidation and v7 is the first heterogeneous release.
  The canonical PNGs now have a separate exact-membership/hash manifest and CI
  gate. Documentation now identifies the asymmetric-error sampler precisely as
  an equal-side two-piece normal approximation while retaining the historical
  machine-readable label, and makes THRILS ingestion conditional on an
  authoritative object-level source table.
- **Scientific/technical effect:** Catalogue membership, physical identities,
  all complete and primary ranks, baseline mathematics, and every v1--v4
  artifact remain unchanged. Only the three v5 tables needing new caveat fields
  changed. Fixed-burst duty cycle is documented as a transformed view of the
  canonical required-average-growth ordering, not an independent rank.
- **Validation:** All 112 regression tests passed. Exact v4.0.1 and v5 CSV
  manifest membership/hashes and full in-memory reproduction passed; the new
  v5 figure manifest membership and hashes also passed. GN-11836 is present
  in both history views with `reported_current_fedd=0.11`, residual `-0.908 dex`,
  false comparison eligibility, and a missing ratio. All four PNGs were opened
  and visually inspected. The rebuilt 15-page status PDF was rendered and all
  pages were visually inspected without clipping or layout defects. PDF
  structure, `git diff --check`, and local documentation-link checks passed.
- **Status:** Complete and verified locally; changes are uncommitted.

## 2026-08-25 — v6 Davis/THRILS same-class consolidation

- **Objective:** Complete the final same-class BLAGN source gate and release
  without modifying any v1--v5 artifact.
- **Contribution:** Verified Davis et al. arXiv `2602.23310v1` Appendix Table 5
  as a complete seven-row source; joined primary-source coordinates by THRILS
  ID from Hutchison et al. arXiv `2512.12509v1`; retained the below-cut Taylor
  repeat in raw history; added six new `z >= 4` objects; generated separate v6
  catalogue, identity, evaluation, ranking, uncertainty, summary, and
  accretion-history products; added a separate THRILS `+/-0.5 dex` sensitivity;
  and added exact release-manifest/reproduction coverage.
- **Scientific/technical effect:** v6 contains 112 measurements / 105 physical
  objects and 111/104 primary-ranked rows. Unpublished LRD, host, luminosity,
  Eddington-ratio, absorption, and FWHM values remain missing. The source's
  approximately 0.5 dex virial scatter remains separate from formal errors.
  No v6 figures were generated and all earlier release defaults remain fixed.
- **Validation:** All 127 regression tests pass. Exact v4.0.1, v5, and v6
  manifest membership/hashes and full in-memory reproduction pass; canonical
  v5 figure hashes pass. The 15-page status PDF was rebuilt without TeX layout
  warnings, rendered page-by-page, and visually inspected without clipping or
  overlap. `git diff --check` passes.
- **Status:** Complete and verified locally; changes are uncommitted.

## 2026-08-25 — v7 heterogeneous admission schema gate

- **Objective:** Implement the source-independent v7 design gate after the
  read-only ALPINE--CRISTAL admission audit, without ingesting source rows or
  modifying frozen v1--v6 products.
- **Contribution:** Added controlled v7 object/evidence, spectroscopy,
  selection, phenotype, lensing, mass-comparability, conditional-mass, and
  ranking-eligibility validation; added measurement/physical-object/host-system
  identity and shared-host-property rules; added a long-form detection/limit
  observable validator; and added an explicit non-mutating adapter from frozen
  v5/v6 vocabulary. Updated forward-looking documentation and roadmaps to
  distinguish the completed gate from the still-pending source extraction.
- **Scientific/technical effect:** No catalogue row, physical identity, science
  result, figure, release manifest, or rank changed. The gate prevents candidate
  evidence from entering primary ranks, keeps conditional BLR masses explicit,
  leaves unpublished host/luminosity/Eddington diagnostics non-penalizing, and
  supports multiple candidate nuclei sharing one system-level host value.
- **Validation:** All 139 regression tests pass, including 12 synthetic v7 gate
  tests and exact frozen-manifest checks. Exact v4.0.1, v5, and v6 in-memory
  reproduction passes; canonical v5 figure membership and hashes pass.
  `git diff --check` passes.
- **Status:** Complete and verified locally; changes are uncommitted.

## 2026-08-25 — Ren ALPINE--CRISTAL--JWST source admission layer

- **Objective:** Extract and validate the first audited heterogeneous source
  without creating a combined v7 catalogue or science release.
- **Contribution:** Preserved all seven published Ren et al. Table 1 candidate
  rows and all 70 Table 2 line entries; represented twelve 3-sigma upper limits
  as censored values; mapped seven candidate nuclei to six host systems; kept
  the shared `DC_848185` host mass at system scope; attached source-specific
  evidence/outflow/three-component caveats; and passed the source layer through
  the v7 admission contract in memory. Added a coordinate/redshift audit against
  v6 and source-specific extraction documentation.
- **Scientific/technical effect:** `DC_536534` is the sole probable/primary
  source record. Six intermediate-width candidates retain conditional virial
  masses in the exploratory tier only. Reines et al. (2013) Halpha masses carry
  a separate `0.4 dex` sensitivity; no LRD label, Delta-BIC value, alternate
  host mass, or other unavailable value is inferred. No v1--v6 artifact, v7
  combined catalogue, rank, result, figure, or manifest changed.
- **Validation:** All 149 regression tests pass. Source-specific tests verify
  7/7/6 measurement/object/system counts, 70 line entries, 58 detections,
  twelve limits, identity, evidence, mass-systematic, host-scope, and
  primary-rank outcomes, plus zero v6 identity candidates. Exact v4.0.1, v5,
  and v6 in-memory reproduction passes; canonical v5 figure membership and
  hashes pass; `git diff --check` passes.
- **Status:** Complete and verified locally; changes are uncommitted.

## 2026-08-25 — v7 catalogue-only heterogeneous assembly

- **Objective:** Attach the admitted Ren source to frozen v6 through the v7
  contract without generating heterogeneous science rankings or figures.
- **Contribution:** Added a non-mutating v6 adapter and combined builder; wrote
  119 measurement, 112 physical-object, and 111 host-system rows; retained both
  identity edges; preserved v6 preferred measurements; added the 70-row Ren
  observable table and source/evidence/phenotype count strata; and added a
  catalogue-only hash/reproduction manifest. Added the Ren 0.4 dex method entry
  to the mass registry and synchronized the v7 documentation and roadmaps.
- **Scientific/technical effect:** All 119 measurements / 112 objects are
  exploratory growth-eligible. The primary tier contains 112 measurements /
  105 objects: `DC_536534` enters as probable evidence while six BLR-conditional
  Ren candidate masses remain exploratory only. `DC_848185_a` and `_b` remain
  two candidate nuclei sharing one host system and integrated host mass. No
  v1--v6 artifact, v7 science ranking, result table, or figure was overwritten.
- **Validation:** All 157 regression tests pass. Exact v4.0.1, v5, v6, and v7
  in-memory reproduction passes; canonical v5 figure membership and hashes
  pass; `git diff --check` passes.
- **Status:** Complete and verified locally; changes are uncommitted.

### 2026-08-25 - Harden v7 and add source-family batch ingestion

- **Objective:** Resolve the v7 schema, source-table foreign-key, manifest,
  dependency, and scaling findings; verify the catalogue from a clean checkout;
  and prepare the repository for larger coherent source-family additions without
  starting pooled heterogeneous science.
- **Files changed:**
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `README.md` (modified)
  - `data/processed/v7/v7_accreting_measurements.csv` (added)
  - `data/processed/v7/v7_accreting_objects.csv` (added)
  - `data/source_family_registry.csv` (added)
  - `docs/guides/getting-started.md` (modified)
  - `docs/guides/release-versioning.md` (modified)
  - `docs/source-notes/v7-admission-schema.md` (modified)
  - `docs/archive/releases/v7/v7-catalogue-schema.md` (added)
  - `docs/source-notes/v7-source-family-batches.md` (added)
  - `releases/v7-catalogue-manifest.json` (added)
  - `requirements-lock.txt` (modified)
  - `requirements-notebook-lock.txt` (added)
  - `scripts/verify_v7_catalogue.py` (added)
  - `src/v7_batch.py` (added)
  - `src/v7_catalogue.py` (added)
  - `src/v7_ren.py` (added)
  - `tests/test_v7_batch.py` (added)
  - `tests/test_v7_catalogue.py` (added)
  - `tests/test_v7_ren_admission.py` (added)
- **Contribution:** Routed the Ren source through the shared standardization
  layer, populated v7 and retained `*_std` uncertainty representations, set
  row-introduction versions and cosmic ages, and made compatibility equality an
  executable batch invariant. Strengthened Table 2 validation from independent
  set checks to the exact Table 1 measurement/object mapping. Added a generic
  one-family batch assembler with source-local observable validation, duplicate
  guards, and prior-release/within-batch identity-candidate gates. Extended the
  v7 verifier to enforce release metadata and all manifest counts. Split the
  optional notebook environment from the core CI lock. Added an executable
  source-family registry and selected XQR-30 as the next separately stratified
  42-quasar comparison batch, pending its complete source and identity audit.
- **Scientific/technical effect:** Published Ren values, v7 membership,
  physical identities, host assignments, evidence tiers, and 119/112/111
  measurement/object/host counts remain unchanged. The seven Ren rows now have
  complete shared-standardization metadata and cannot be silently lost by
  consumers of retained compatibility fields. Future larger additions must
  share an evidence family and cannot carry foreign observables or unresolved
  identity candidates into a release. No v7 science ranking or figure was
  generated, and no v1--v6 artifact changed.
- **Validation:** All 163 regression tests passed under isolated Python 3.12.14
  with the exact pinned core dependencies. Exact v4.0.1, v5, v6, and v7
  manifest membership/hashes and full in-memory reproduction passed; canonical
  v5 figure membership and hashes passed. The exact CI sequence, including all
  `--require-clean` gates, passed in a fresh committed temporary checkout and
  left it clean. All CSVs, JSON, and CI YAML parsed; `git diff --check` passed.
  The updated 15-page status PDF compiled without TeX layout warnings, all pages
  were rendered, and the full contact sheet plus the changed roadmap and
  conclusion pages were visually inspected without clipping or overlap.
- **Status:** Complete in commit `e82e82f` (`Freeze v7 catalogue and batch
  ingestion`); verified locally and not pushed.

### 2026-08-27 - Organize catalogue data and results by release

- **Objective:** Make the growing catalogue and results tree navigable while
  preserving every frozen artifact and its reproducibility contract.
- **Contribution:** Moved standardized catalogue tables to
  `data/processed/<release>/`, identity and crossmatch products to
  `data/crossmatch/<release>/`, and generated science artifacts to
  `results/releases/<release>/tables|figures|galleries`. Retained all original
  filenames, separated large per-object galleries from paper-facing figures,
  added data/results directory guides, regenerated the 269-artifact inventory,
  and updated every generator, verifier, test, manifest, and documentation
  reference to the canonical layout.
- **Scientific/technical effect:** No catalogue membership, value, preferred
  identity, ranking, figure content, or source artifact changed. Earlier
  releases remain available as frozen reproducibility snapshots rather than
  being deleted as superseded copies.
- **Validation:** All 211 regression tests pass. Every v4 through v7.4 release
  hash, exact-membership, and in-memory reproduction gate passes; canonical v5
  figure hashes and the v7.3 gallery dimensions, membership, and cross-inventory
  hashes pass. The results inventory still contains exactly 269 artifacts.
- **Status:** Complete and verified locally; commit and remote CI pending.

### 2026-08-27 - Complete v7.4 per-object growth collection

- **Objective:** Give every growth-eligible catalogue object the same complete
  visual diagnostic set and make unavailable cases auditable.
- **Contribution:** Generated parameter-map sheets, seed-redshift maps, and
  reference growth tracks for all 196 eligible objects; added six zoomable
  class grids, 288 class-specific compatibility rows, an all-object coverage
  audit, a 22-object unavailable audit, a 594-image gallery index, and a
  byte-exact 600-artifact release manifest. Expanded the global results index
  from 269 to 868 artifacts and added CI verification.
- **Scientific/technical effect:** Broad-line AGN and luminous-quasar results
  remain separate. Compatibility fractions are descriptive within class only;
  no pooled demographic fraction or missing-mass inference is allowed. The 22
  unavailable objects remain visible with explicit exclusion reasons.
- **Validation:** All 216 regression tests pass. Every v4 through v7.4
  catalogue/science reproduction gate passes, both organized-gallery gates
  pass, canonical v5 figure hashes pass, and `git diff --check` is clean.
- **Status:** Complete and verified locally; commit, push, clean-worktree
  verification, and remote CI pending.

### 2026-08-27 - Complete integrated v7.5 research release

- **Objective:** Complete the next four milestones: provenance/evidence-policy
  closure, current class-aware science, current figures/full-gallery coverage,
  and manuscript/publication packaging.
- **Contribution:** Added the complete 41-row Scholtz source-native table and
  proved the exact 21-row `z >= 4` subset; admitted the omitted
  JADES-NS-GS00099671 row without inventing a mass; introduced preferred-row
  object evidence aggregation with full status history; released the 234/219/218
  catalogue and eight current science tables; generated four visually inspected
  high-resolution figures; indexed all 219 objects against the complete inherited
  588-image/six-grid gallery; and added the authoritative seven-page manuscript,
  citation metadata, license, release notes, claim/citation audits, contribution
  guidance, CI gates, and catalogue/science/figure/publication manifests.
- **Scientific/technical effect:** Frozen v7.4 bytes remain unchanged. Growth
  eligibility stays at 209 measurements / 196 objects because the corrected
  source row has no canonical black-hole mass. The preferred secure JADES 8083
  row again controls its object status, raising the primary object count to 171,
  while its candidate alternate remains auditable. All 23 catalogue-only objects
  are explicit in current gallery coverage and all 48 excluded measurement/object
  rows are explicit in current science.
- **Validation:** All 231 regression tests pass. v7.4 catalogue and gallery
  gates still pass. All four v7.5 release gates pass with exact hashes and
  in-memory reproduction where applicable. The manuscript compiled without TeX
  layout warnings; all seven rendered pages and all four source figures were
  visually inspected. `git diff --check` passes.
- **Status:** Complete and verified locally; commit, clean-worktree verification,
  push, and remote CI pending.

### 2026-08-27 - Reconcile current documentation and publication provenance

- **Objective:** Correct every confirmed documentation inconsistency from the
  repository-wide audit without changing scientific catalogue or result data.
- **Files changed:**
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
  - `.codex_tmp/catalogue-expansion-guide.md` (modified)
  - `.codex_tmp/observational-atlas-roadmap.md` (modified)
  - `.codex_tmp/research-grade-observational-atlas-roadmap-detailed.md` (modified)
  - `.github/workflows/ci.yml` (modified)
  - `CHANGELOG.md` (modified)
  - `CONTRIBUTING.md` (modified)
  - `README.md` (modified)
  - `data/README.md` (modified)
  - `data/sources.md` (modified)
  - `docs/guides/getting-started.md` (modified)
  - `docs/reference/model-menu.md` (modified)
  - `docs/guides/release-versioning.md` (modified)
  - `docs/source-notes/uhz1-xray-evidence-history-extraction-notes.md` (modified)
  - `docs/archive/releases/v2/v2-ranking-metrics.md` (modified)
  - `docs/archive/releases/v2/v2-uncertainty-propagation.md` (modified)
  - `docs/archive/releases/v6/v6-blagn-science-workflow.md` (modified)
  - `docs/current/v7.5-citation-audit.md` (modified)
  - `docs/current/v7.5-release-notes.md` (modified)
  - `paper/README.md` (modified)
  - `paper/highz_accretion_atlas_v7_5.tex` (modified)
  - `paper/highz_accretion_atlas_v7_5.pdf` (modified)
  - `releases/v7.5-publication-manifest.json` (modified)
- **Contribution:** Reconciled frozen/current release terminology, corrected
  the data-directory map and project-version vocabulary, documented the frozen
  JADES provenance gap and current 21-row Scholtz correction, fixed the v7.5
  manifest count, completed contributor verification instructions, clarified
  raw-versus-processed provenance storage, separated background reading from
  catalogue sources, and marked superseded roadmap files as historical.
  Completed the publication citation trail with exact Zou, D'Odorico,
  Hutchison, Goulding, and JADES DR3 provenance; corrected Goulding's year and
  DOI; rebuilt and visually inspected the authoritative PDF; and refreshed its
  publication-manifest hashes.
- **Scientific/technical effect:** No catalogue membership, measurement value,
  identity decision, ranking, science table, or figure changed. Documentation
  now describes v7.5 as current and all preceding releases as frozen or
  historical, while accurately exposing unavailable frozen-v1 provenance.
- **Validation:** All 231 regression tests pass. All four v7.5 catalogue,
  science, figure/gallery, and publication gates pass. The TeX source compiled
  without layout warnings; all seven PDF pages were rendered and visually
  inspected with no clipping, overlap, broken citations, or unreadable content.
  `CITATION.cff` and the publication manifest parse successfully, every
  documented Python module resolves, targeted stale-language searches are
  empty, and `git diff --check` passes.
- **Status:** Complete and verified locally; uncommitted.

### 2026-09-02 - Rename and fully flatten map galleries

- **Objective:** Replace generic or class-nested gallery names with two direct,
  axis-named folders for every canonical dataset version.
- **Files changed:** Gallery products under `results/v1/`, `results/v2/`, and
  `results/v3/`; the visual-coverage tables, results inventory, dataset
  manifests, atlas generators, inventory and verification modules, repository
  tests, workflow notebook, README and current publication documentation,
  manuscript, and archived status document.
- **Contribution:** Each `gallery/` now contains exactly `fedd_mass_maps/` and
  `seedredshift_mass_maps/`. Object-class directories were removed. Individual
  filenames and coverage product kinds now use `fedd_mass_map` and
  `seedredshift_mass_map`; the combined gallery figure is now named
  `v*_all_object_fedd_mass_map_gallery.png`. Supporting modules were renamed to
  `src/internal/fedd_mass_maps.py` and
  `src/internal/seedredshift_mass_maps.py`.
- **Scientific/technical effect:** None. All 708 retained per-object images
  remain represented, with 46 panels in v1, 224 in v2, and 438 in v3. The
  change affects paths and labels, not catalogue membership, numerical values,
  model assumptions, rankings, or interpretations.
- **Validation:** The atlas notebook rebuilt all panels and regenerated the
  792-row result inventory plus the 84/262/476-artifact v1/v2/v3 manifests.
  The manuscript and status PDFs were rebuilt, rendered in full, and visually
  inspected without layout defects. Complete verification results are recorded
  in the final repository assessment for this change.
- **Recovery note:** Superseded paths and names remain recoverable from Git
  history.
- **Status:** Complete and verified locally; uncommitted.

### 2026-08-27 - Complete source-provenance improvements

- **Objective:** Convert the source-quality review's provenance recommendations
  into a controlled, verifiable supplement without rewriting frozen data.
- **Files added:** `data/source_provenance_registry.csv`,
  `releases/source-provenance-manifest.json`,
  `scripts/verify_source_provenance.py`, `src/source_provenance.py`, and
  `tests/test_source_provenance.py`.
- **Files updated:** `.github/workflows/ci.yml`, `CHANGELOG.md`,
  `CONTRIBUTING.md`, `README.md`, `data/README.md`, `data/sources.md`,
  `docs/guides/getting-started.md`, `docs/guides/release-versioning.md`, and
  `releases/v7.5-publication-manifest.json`.
- **Contribution:** Added 16 machine-readable records covering all 11 current
  source families plus the Hutchison and D'Odorico coordinate sources,
  Goulding context source, and JADES DR3 coordinate release. Separated source
  role, publication status, evidence status, paper DOI, and dataset DOI;
  scheduled reviews for Davis, Hutchison, and Zou; attached the Shen VizieR
  dataset DOI; and backfilled the exact current Juodžbalis v2 archive and DOI
  while preserving the unknown historical v1 extraction date.
- **Scientific/technical effect:** No raw or processed catalogue value,
  membership, identity decision, ranking, result, figure, or manuscript content
  changed. Candidate/disputed evidence remains distinct from publication
  maturity, including the Davis EELG-parent context and UHZ1 evidence history.
- **Validation:** All 237 regression tests pass. The source-provenance gate and
  all four v7.5 catalogue, science, figure/gallery, and publication gates pass;
  exact manifest hashes and in-memory reproductions are verified.
- **Status:** Complete and verified locally; uncommitted.

### 2026-08-27 - Finalize v7.5 repository navigation and release handoff

- **Objective:** Make the completed catalogue easy to enter and navigate, then
  prepare the full integrated state for its clean public release.
- **Files updated:** `README.md`, `data/README.md`, `CHANGELOG.md`,
  `.codex_tmp/CONTRIBUTION_LEDGER.md`, and the affected v7.5 publication
  manifest hash.
- **Contribution:** Added prominent links to the current object catalogue,
  schema, results inventory, manuscript draft, and source provenance. Added a
  table-by-table guide for all current processed and crossmatch products,
  including row counts, row meanings, stable relational keys, preferred-row
  semantics, and a tested minimal read example. Preserved all frozen release
  paths and artifacts.
- **Scientific/technical effect:** Navigation and release packaging only; no
  catalogue membership, value, identity decision, analysis result, figure, or
  manuscript claim changed.
- **Validation:** All 237 regression tests, source-provenance verification, and
  every release gate from v4 through v7.5 pass. All local Markdown links and
  release JSON files validate; the documented read example returns 219 objects
  and 196 growth-eligible objects; `git diff --check` passes.
- **Status:** Final integrated state prepared for commit, clean-worktree
  verification, tag finalization, push, and remote CI.

### 2026-09-01 - Organize active and archived documentation

- **Objective:** Declutter the top-level `docs/` directory and make current,
  reference, source, publication, and historical material easy to navigate.
- **Files changed:**
  - `.gitignore` (modified)
  - `README.md` (modified)
  - `data/README.md` (modified)
  - `data/sources.md` (modified)
  - `docs/README.md` (modified)
  - `docs/current/README.md` (added)
  - `docs/current/v7.5-catalogue-schema.md` (renamed from `docs/v7.5-catalogue-schema.md`)
  - `docs/current/v7.5-citation-audit.md` (renamed from `docs/v7.5-citation-audit.md`)
  - `docs/current/v7.5-claim-audit.md` (renamed from `docs/v7.5-claim-audit.md`)
  - `docs/current/v7.5-class-aware-science-workflow.md` (renamed from `docs/v7.5-class-aware-science-workflow.md`)
  - `docs/current/v7.5-release-notes.md` (renamed from `docs/v7.5-release-notes.md`)
  - `docs/guides/README.md` (added)
  - `docs/guides/getting-started.md` (renamed from `docs/getting-started.md`)
  - `docs/guides/release-versioning.md` (renamed from `docs/release-versioning.md`)
  - `docs/reference/README.md` (added)
  - `docs/reference/model-menu.md` (renamed from `docs/model-menu.md`)
  - `docs/reference/multiclass-eligibility-and-mass-comparability.md` (renamed from `docs/multiclass-eligibility-and-mass-comparability.md`)
  - `docs/reference/object-taxonomy.md` (renamed from `docs/object-taxonomy.md`)
  - `docs/source-notes/README.md` (added)
  - `docs/source-notes/davis26-thrils-extraction-notes.md` (renamed from `docs/davis26-thrils-extraction-notes.md`)
  - `docs/source-notes/harikane23-nirspec-extraction-notes.md` (renamed from `docs/harikane23-nirspec-extraction-notes.md`)
  - `docs/source-notes/lin24-aspire-extraction-notes.md` (renamed from `docs/lin24-aspire-extraction-notes.md`)
  - `docs/source-notes/matthee23-eiger-fresco-extraction-notes.md` (renamed from `docs/matthee23-eiger-fresco-extraction-notes.md`)
  - `docs/source-notes/ren25-alpine-cristal-jwst-extraction-notes.md` (renamed from `docs/ren25-alpine-cristal-jwst-extraction-notes.md`)
  - `docs/source-notes/scholtz25-jades-narrow-line-extraction-notes.md` (renamed from `docs/scholtz25-jades-narrow-line-extraction-notes.md`)
  - `docs/source-notes/shen19-gnirs50-extraction-notes.md` (renamed from `docs/shen19-gnirs50-extraction-notes.md`)
  - `docs/source-notes/taylor24-ceers-rubies-extraction-notes.md` (renamed from `docs/taylor24-ceers-rubies-extraction-notes.md`)
  - `docs/source-notes/uhz1-xray-evidence-history-extraction-notes.md` (renamed from `docs/uhz1-xray-evidence-history-extraction-notes.md`)
  - `docs/source-notes/v7-admission-schema.md` (renamed from `docs/v7-admission-schema.md`)
  - `docs/source-notes/v7-source-family-batches.md` (renamed from `docs/v7-source-family-batches.md`)
  - `docs/source-notes/xqr30-extraction-notes.md` (renamed from `docs/xqr30-extraction-notes.md`)
  - `docs/archive/README.md` (added)
  - `docs/archive/legacy/README.md` (added)
  - `docs/archive/legacy/catalogue-expansion-candidates-legacy.md` (renamed from `docs/catalogue-expansion-candidates-legacy.md`)
  - `docs/archive/legacy/catalogue-schema.md` (renamed from `docs/catalogue-schema.md`)
  - `docs/archive/releases/README.md` (added)
  - `docs/archive/releases/v2/v2-figure-inventory.md` (renamed from `docs/v2-figure-inventory.md`)
  - `docs/archive/releases/v2/v2-ranking-metrics.md` (renamed from `docs/v2-ranking-metrics.md`)
  - `docs/archive/releases/v2/v2-uncertainty-propagation.md` (renamed from `docs/v2-uncertainty-propagation.md`)
  - `docs/archive/releases/v3/v3-blagn-catalogue-schema.md` (renamed from `docs/v3-blagn-catalogue-schema.md`)
  - `docs/archive/releases/v3/v3-blagn-science-workflow.md` (renamed from `docs/v3-blagn-science-workflow.md`)
  - `docs/archive/releases/v4/v4-blagn-catalogue-schema.md` (renamed from `docs/v4-blagn-catalogue-schema.md`)
  - `docs/archive/releases/v4/v4-blagn-science-workflow.md` (renamed from `docs/v4-blagn-science-workflow.md`)
  - `docs/archive/releases/v5/v5-blagn-catalogue-schema.md` (renamed from `docs/v5-blagn-catalogue-schema.md`)
  - `docs/archive/releases/v5/v5-blagn-science-workflow.md` (renamed from `docs/v5-blagn-science-workflow.md`)
  - `docs/archive/releases/v5/v5-figure-inventory.md` (renamed from `docs/v5-figure-inventory.md`)
  - `docs/archive/releases/v5/v5-manuscript-citation-audit.md` (renamed from `docs/v5-manuscript-citation-audit.md`)
  - `docs/archive/releases/v5/v5-manuscript-claim-audit.md` (renamed from `docs/v5-manuscript-claim-audit.md`)
  - `docs/archive/releases/v6/v6-blagn-catalogue-schema.md` (renamed from `docs/v6-blagn-catalogue-schema.md`)
  - `docs/archive/releases/v6/v6-blagn-science-workflow.md` (renamed from `docs/v6-blagn-science-workflow.md`)
  - `docs/archive/releases/v7/v7-catalogue-schema.md` (renamed from `docs/v7-catalogue-schema.md`)
  - `docs/archive/releases/v7/v7.1-catalogue-schema.md` (renamed from `docs/v7.1-catalogue-schema.md`)
  - `docs/archive/releases/v7/v7.2-catalogue-schema.md` (renamed from `docs/v7.2-catalogue-schema.md`)
  - `docs/archive/releases/v7/v7.2-class-aware-science-workflow.md` (renamed from `docs/v7.2-class-aware-science-workflow.md`)
  - `docs/archive/releases/v7/v7.3-catalogue-schema.md` (renamed from `docs/v7.3-catalogue-schema.md`)
  - `docs/archive/releases/v7/v7.4-catalogue-schema.md` (renamed from `docs/v7.4-catalogue-schema.md`)
  - `docs/archive/project-history/README.md` (added; ignored local history)
  - `docs/archive/project-history/CONTRIBUTION_LEDGER.md` (renamed from `docs/archive/CONTRIBUTION_LEDGER.md`; ignored local history)
  - `docs/archive/project-history/catalogue-expansion-guide.md` (renamed from `docs/archive/catalogue-expansion-guide.md`; ignored local history)
  - `docs/archive/project-history/highz_accretion_atlas_status.pdf` (renamed from `docs/archive/highz_accretion_atlas_status.pdf`; ignored local history)
  - `docs/archive/project-history/highz_accretion_atlas_status.tex` (renamed from `docs/archive/highz_accretion_atlas_status.tex`; ignored local history)
  - `docs/archive/project-history/observational-atlas-roadmap.md` (renamed from `docs/archive/observational-atlas-roadmap.md`; ignored local history)
  - `docs/archive/project-history/research-grade-observational-atlas-roadmap-detailed.md` (renamed from `docs/archive/research-grade-observational-atlas-roadmap-detailed.md`; ignored local history)
  - `docs/publication/documentation/README.md` (modified)
  - `paper/README.md` (modified)
  - `releases/README.md` (modified)
  - `releases/v7.5-publication-manifest.json` (modified)
  - `scripts/README.md` (modified)
  - `scripts/verify_v7_5_publication.py` (modified)
- **Contribution:** Grouped active docs by role, archived all frozen v2–v7.4
  release contracts and legacy material, added navigation indexes at every
  major boundary, updated repository-wide references, and narrowed the archive
  ignore rule so versioned historical contracts remain available after clone.
- **Scientific/technical effect:** Navigation and packaging only. No catalogue,
  source data, scientific result, figure, or manuscript claim changed.
- **Validation:** All local Markdown links resolve; no stale pre-move primary,
  extraction-note, or frozen-release paths remain; the v7.5 publication gate
  passes with exact hashes; all 237 regression tests pass through `unittest`
  discovery; and `git diff --check` passes.
- **Status:** Complete and verified locally; uncommitted.

### 2026-09-02 - Migrate the public repository contract to v1/v2/v3 datasets

- **Objective:** Complete the repository migration from software-like v7.x
  public release naming to three nested scientific datasets, while preserving
  reproducibility, useful history, the restored narrative README, and the
  project record.
- **Files changed:** Public workflow notebooks under `scripts/`; Python
  implementation modules under `src/internal/`; canonical v1/v2/v3 processed,
  crossmatch, table, figure, gallery, and manifest products; archived v7.x
  manifests and release documentation; current workflow, literature-scope,
  publication, status, versioning, contribution, and repository navigation
  documentation; CI and regression contracts.
- **Contribution:** Established v1, v2, and v3 as the only public dataset
  versions; retained former `v7_*` modules only as internal compatibility and
  reconstruction history; converted the ordered public workflow to five clean
  Jupyter notebooks backed by testable `.py` modules; added exact SHA-256
  dataset manifests and in-memory catalogue/science reproduction checks;
  retained compact historical tables and immutable manifests while removing
  duplicated generated historical PNGs; declared a 27 August 2026 literature
  cutoff with considered/not-admitted records; restored the earlier README
  narrative and updated only the workflow and facts made inaccurate by the
  migration; regenerated the repository status report.
- **Scientific/technical effect:** Canonical membership is 23 measurements and
  23 objects in v1, 119 measurements and 112 objects in v2, and 234
  measurements and 219 objects in v3. The v3 atlas contains 196 numerical and
  23 explicit no-inference objects, with 219 parameter sheets and 219 growth
  panels. Dataset versions remain distinct from the deliberately unresolved
  software package version.
- **Validation:** Executed all five public notebooks end to end from clean
  copies. Rebuilt all catalogues, science tables, summary figures, 708
  per-object panels across v1/v2/v3, and three dataset manifests. Source
  provenance verification covers 16 records and all 11 final-v3 source
  families; exact CSV and manifest reproduction passes; all 183 regression
  tests pass; all five source notebooks validate with stable cell IDs and no
  stored outputs; the nine-page status PDF was rendered and visually inspected
  page by page.
- **Status:** Migration complete and verified locally; software-version policy
  intentionally held for a separate decision; uncommitted.

### 2026-09-02 - Complete the intended paper-product contract

- **Objective:** Produce the canonical products still promised by the README
  and identify the location of every intended main-text and supplement product
  directly in that section.
- **Files changed:** `README.md`; shared science and atlas generators under
  `src/`; v1/v2/v3 result tables, visual-coverage tables, seed-redshift
  galleries, result inventory, and dataset manifests; current atlas, claim,
  publication, manuscript, test, and status documentation.
- **Contribution:** Added one seed-mass/seed-redshift panel for every catalogue
  object in every dataset version (23 v1, 112 v2, 219 v3), using numerical
  baseline maps when a canonical mass exists and explicit no-inference panels
  otherwise. Added class-aware follow-up-priority matrices that include every
  object, rank only growth-eligible objects, and label global ordering as a
  navigation aid rather than cross-class demographic inference. Added one
  dedicated caveat-summary row per admitted source family. Annotated every
  README intended-product bullet with its canonical path.
- **Scientific/technical effect:** v3 visual coverage increases from 438 to 657
  per-object panels: 219 parameter maps, 219 growth tracks, and 219
  seed-redshift panels. The v3 follow-up matrix contains 219 objects, including
  196 ranked growth-eligible objects and 23 visibly unranked objects without a
  method-comparable canonical mass. The v3 caveat table covers all 11 admitted
  source families.
- **Validation:** All 185 regression tests pass. Exact v1/v2/v3 CSV
  reproduction, source provenance, strict dataset nesting, visual coverage,
  and SHA-256 manifest verification pass. The manifests cover 109 v1, 375 v2,
  and 698 v3 artifacts; the result inventory covers 1,226 retained artifacts.
  Representative numerical and no-inference seed-redshift panels were visually
  inspected, and the regenerated status PDF was rendered and checked.
- **Status:** Intended paper-product contract complete and verified locally;
  uncommitted.

### 2026-09-02 - Retire obsolete releases and reconcile the manuscript audit

- **Objective:** Finish the v1/v2/v3 migration by removing obsolete public
  release-era trees, retaining only the source-admission code and assembly
  inputs required for exact reconstruction, and checking every quantitative
  manuscript and status claim against regenerated products.
- **Files changed:** `README.md`, `CONTRIBUTING.md`, `CITATION.cff`,
  `pyproject.toml`, CI and dependency metadata; active documentation under
  `docs/current/`, `docs/guides/`, `docs/reference/`, `docs/source-notes/`, and
  `docs/publication/`; the manuscript under `paper/`; source and assembly
  registries under `data/`; canonical v1/v2/v3 processed, crossmatch, result,
  inventory, and manifest products; public notebooks under `scripts/`; Python
  modules under `src/`; tests under `tests/`; this ledger; and the dated status
  source and PDF. Obsolete v4-v7.x data, result, manifest, documentation,
  script, source, and test trees were removed from the repository.
- **Contribution:** Restructured the repository around `src/datasets.py` and
  `src/science.py`, five ordered public notebooks, canonical version-scoped
  outputs, and a small test suite focused on the surviving contract. Moved the
  required historical source-admission builders under
  `src/internal/compatibility/`; moved their frozen inputs under
  `data/assembly/`; removed the compatibility writer that could recreate a
  public v7 tree; normalized active audit labels and source-family metadata;
  and updated navigation, workflow, schema, publication, and provenance docs.
  Historical ledger text remains unchanged and this entry supersedes its old
  release-era counts where the canonical repository was intentionally pruned.
- **Scientific/technical effect:** Catalogue membership and numerical science
  are unchanged: v1/v2/v3 contain 23/112/219 objects, and v3 contains 234
  measurements, 218 hosts, 1,106 source-local observables, 196
  growth-eligible objects, 13 alternate-measurement comparisons, 219 follow-up
  rows with 196 ranked, 11 source-caveat rows, and 657 per-object panels. The
  manuscript, claim audit, and status report now state those verified values.
  The canonical result inventory contains 1,149 artifacts; manifests cover
  108 v1, 375 v2, and 696 v3 artifacts after obsolete duplicates and releases
  were removed.
- **Validation:** Executed all five public notebooks end to end into clean
  temporary copies, rebuilding all three catalogues, all shared science tables,
  paper figures, all-object products, result inventory, and manifests. All 24
  focused regression tests pass. Source provenance verifies 16 records and all
  11 v3 source families; the dataset verifier passes strict nesting, exact CSV
  reproduction, numerical/result contracts, and SHA-256 manifests. All local
  Markdown links resolve, `git diff --check` passes, and the nine-page status
  PDF was rendered and visually inspected page by page.
- **Recovery note:** Removed release-era material was first moved to
  `/private/tmp/highz-accretion-atlas-legacy-20260902`; it remains recoverable
  there until temporary storage is cleaned and remains recoverable from Git
  history thereafter.
- **Status:** Canonical v1/v2/v3 restructuring and claim reconciliation
  complete and verified locally; uncommitted.

### 2026-09-02 - Reconcile package metadata and active documentation

- **Objective:** Resolve the post-migration packaging omissions and correct the
  stale documentation identified by the final repository review.
- **Files changed:** `pyproject.toml`, `requirements-lock.txt`, `README.md`,
  `docs/README.md`, `docs/guides/getting-started.md`,
  `docs/current/v3-claim-audit.md`, `releases/README.md`, and this ledger.
- **Contribution:** Changed package discovery from an incomplete explicit list
  to the full `src.*` tree so the required internal compatibility builders are
  included; declared Pillow as a direct core dependency and ReportLab as a
  notebook/documentation dependency; added README, license, author, and
  repository metadata; documented that data and results require a complete
  source checkout; replaced obsolete release-history and manifest terminology;
  and made the Scholtz and JADES-NS-GS00099671 audit evidence descriptions match
  the builder assertions and exact-reproduction gate that actually enforce the
  claims. The intentionally held software version remains `0.0.0`.
- **Scientific/technical effect:** No catalogue membership, numerical result,
  source provenance, manuscript claim, or generated product changed.
- **Validation:** Built the `0.0.0` wheel without dependency resolution,
  confirmed that it contains and imports the complete `src.internal.compatibility`
  package outside the repository tree, and inspected its dependency and project
  metadata. All 24 focused regression tests pass. Source provenance verifies 16
  records and all 11 v3 source families; strict dataset nesting, manifests,
  result inventory, shared analysis, and exact CSV reproduction pass. All 51
  local Markdown documents have resolving local links, and `git diff --check`
  passes.
- **Status:** Documentation and metadata corrections complete and verified
  locally; uncommitted.

### 2026-09-02 - Harden CI, scientific claim tests, and manuscript delivery

- **Objective:** Complete the remaining post-migration maintenance work by
  strengthening automated validation, compiling the final manuscript, and
  removing obsolete configuration and local residue.
- **Files changed:** `.github/workflows/ci.yml`, `.gitignore`, `paper/README.md`,
  `paper/highz_accretion_atlas_v3.pdf`, `tests/README.md`,
  `tests/test_scientific_claims.py`, `docs/current/v3-claim-audit.md`,
  `docs/publication/README.md`, and this ledger.
- **Contribution:** Updated the official checkout and Python setup actions to
  their Node 24-compatible v7 releases. Extended CI to install the complete
  pinned notebook environment, build and import the wheel outside the source
  tree, execute all five public notebooks in an isolated checkout, and compile
  the manuscript with LaTeX. Added direct regression anchors for the Scholtz
  41/21 table counts, the JADES-NS-GS00099671 no-mass correction, the JADES 8083
  identity merge, J1148+5251's two leading ranks, the top-eight unit
  probabilities, primary-row counts, alternate comparisons, follow-up and
  caveat counts, and complete panel coverage. Compiled and indexed the final
  manuscript PDF, removed obsolete archive allow-list rules, and ignored only
  LaTeX intermediate files.
- **Scientific/technical effect:** No catalogue membership, source value,
  numerical result, or scientific interpretation changed. Existing manuscript
  claims now have explicit unit-level regression coverage in addition to exact
  end-to-end reproduction.
- **Validation:** All 31 tests pass, including the compiled-manuscript artifact
  check. Source provenance verifies 16 records and
  all 11 v3 source families; manifests, result inventory, strict dataset
  nesting, shared analysis, and exact CSV reproduction pass. The wheel builds
  and imports outside the repository. All five notebooks execute in order in an
  isolated copy and reproduce the checked-in processed data, crossmatches,
  results, and manifests byte for byte. Tectonic compiled the eight-page
  manuscript without warnings; every page was rendered and visually inspected.
- **Status:** CI, claim-test, manuscript, and cleanup hardening complete and
  verified locally; the updated remote CI will run after these changes are
  committed and pushed.

### 2026-09-02 - Remove the public contribution guide

- **Objective:** Remove GitHub's automatic repository-level Contributing tab.
- **Files changed:** `CONTRIBUTING.md` (removed) and this ledger.
- **Contribution:** Removed the root contribution guide so GitHub no longer
  promotes it as repository community documentation. The maintained setup,
  workflow, validation, and source-provenance guidance remains in the README,
  documentation guides, and test documentation.
- **Scientific/technical effect:** None; no source code, data, results, or
  scientific claims changed.
- **Validation:** Confirmed that active documentation does not link to the
  removed file; the complete repository validation suite is rerun with this
  change before publication.
- **Status:** Complete.

### 2026-09-02 - Flatten galleries and remove individual growth tracks

- **Objective:** Simplify every dataset gallery by removing the redundant
  `per_object/` directory and the unneeded individual growth-track products.
- **Files changed:**
  - `.gitattributes` (added)
  - `README.md`, `results/README.md`, `docs/current/v3-atlas.md`,
    `docs/current/v3-notes.md`, `docs/current/v3-claim-audit.md`, and
    `docs/publication/supplement/README.md` (modified)
  - `scripts/03_generate_atlas.ipynb` (modified)
  - `src/internal/atlas.py`, `src/internal/generate_atlas.py`,
    `src/internal/seed_redshift_gallery.py`,
    `src/internal/parameter_maps.py` (renamed from
    `src/internal/growth_visuals.py`),
    `src/internal/figures.py`, `src/internal/build_results_inventory.py`,
    `src/internal/verify_versions.py`, and `src/internal/build_status_pdf.py`
    (modified)
  - `tests/test_repository_layout.py` and `tests/test_scientific_claims.py`
    (modified)
  - `results/v1/gallery/`, `results/v2/gallery/`, and `results/v3/gallery/`
    (708 retained parameter/seed-redshift panels moved one level up; 354
    individual growth-track panels deleted)
  - `results/v1/tables/v1_growth_gallery_coverage.csv`,
    `results/v2/tables/v2_growth_gallery_coverage.csv`, and
    `results/v3/tables/v3_growth_gallery_coverage.csv` (deleted)
  - `results/v1/tables/v1_all_object_visual_coverage.csv`,
    `results/v2/tables/v2_all_object_visual_coverage.csv`,
    `results/v3/tables/v3_all_object_visual_coverage.csv`,
    `results/results_inventory.csv`, and all three dataset manifests under
    `releases/` (regenerated)
  - `paper/highz_accretion_atlas_v3.tex`,
    `paper/highz_accretion_atlas_v3.pdf`,
    `docs/archive/project-history/highz_accretion_atlas_status.tex`, and
    `docs/archive/project-history/highz_accretion_atlas_status.pdf` (modified)
- **Contribution:** Galleries now begin directly with object-class directories,
  each containing only `parameter_maps/` and `seed_redshift_maps/`. Removed the
  unused individual-track renderer and the redundant one-row-per-object growth
  gallery table. The all-object growth-track figure remains as the sole growth
  track visualization for each version. Canonical v3 gallery coverage is now
  438 panels rather than 657, and the result inventory contains 792 artifacts.
- **Scientific/technical effect:** No catalogue membership, source value,
  ranking, uncertainty result, or scientific interpretation changed. This is a
  product-layout reduction only.
- **Validation:** Executed the updated atlas notebook with full panel rebuilds
  for v1, v2, and v3, then executed the verification notebook. All 32 tests
  pass; provenance covers 16 records and all 11 final-v3 source families; all
  manifests, inventory rows, exact CSV reproduction, shared analysis, image
  resolution, and strict nested dataset contracts verify. Both PDFs were
  rebuilt, rendered in full, and visually inspected without layout defects.
  Binary asset attributes keep Git's text-whitespace checks scoped to text
  files.
- **Recovery note:** Deleted individual panels and obsolete coverage tables
  remain recoverable from Git history.
- **Status:** Complete and verified locally; uncommitted.

### 2026-09-02 - Add comprehensive v3 growth-track companion

- **Objective:** Preserve the full reference-line vocabulary of the historical
  v1 growth-track figure in a new v3 all-object product without replacing the
  simpler canonical overview.
- **Files changed:** Atlas generator and verifier, scientific regression tests,
  current and publication documentation, manuscript and status sources/PDFs,
  result inventory, v3 manifest, and
  `results/v3/figures/v3_all_object_growth_tracks_full_assumptions.png`.
- **Contribution:** Added a v3 companion containing 72 constant-efficiency
  curves: three seed masses (`10^2`, `10^4`, and `10^5 M_sun`) crossed with
  `f_Edd = 0.3, 1, 2`, four efficiencies (`0.100`, `0.038`, `0.057`, and
  `0.423`), and merger boosts of one and two. Colour, line style, width, and
  opacity preserve the historical v1 encoding. All 196 supported v3 objects
  remain plotted with uncertainties, and the lower strip retains all 23
  no-inference objects by class and redshift.
- **Scientific/technical effect:** Adds an assumption-comparison visualization;
  it does not change catalogue membership, numerical tables, rankings, model
  equations, or the simpler v3 growth-track figure.
- **Validation:** The public atlas notebook regenerated v1, v2, and v3 and the
  verification notebook passed all 33 tests. The 72-curve Cartesian product is
  regression-tested; the 4500-by-3750 PNG is resolution-checked; provenance,
  exact CSV reproduction, strict dataset nesting, the 793-row result inventory,
  and 84/262/477-artifact manifests verify. The figure and all 17 pages across
  the rebuilt manuscript and status PDFs were visually inspected without
  clipping, overlap, or illegible labels.
- **Status:** Complete and verified locally; included in the accompanying
  repository commit.

### 2026-09-02 - Simplify comprehensive growth-track title

- **Objective:** Use the concise requested title for the comprehensive v3
  all-object growth-track companion.
- **Files changed:** Atlas generator, regenerated companion PNG, result
  inventory, and v3 release manifest.
- **Contribution:** Changed the displayed title to exactly
  `v3: all-object growth tracks`. The full assumption grid remains documented
  by the figure legend and repository documentation.
- **Scientific/technical effect:** None. Curves, objects, uncertainties, axes,
  and numerical products are unchanged.
- **Validation:** Regenerated the 4500-by-3750 companion PNG, visually checked
  the title and layout, and rebuilt the result inventory and v3 manifest. All
  33 tests pass; provenance and all version, inventory, manifest, exact-CSV,
  and dataset-growth checks pass.
- **Status:** Complete and verified locally; included in the accompanying
  repository commit.

### 2026-09-02 - Add uncertainty-filtered v3 growth-track companion

- **Objective:** Provide a readable copy of the comprehensive 72-curve v3
  growth-track plot without the most uncertain luminous-quasar measurements,
  while preserving the complete plot as the canonical unfiltered reference.
- **Files changed:** Atlas generation and verification code, focused scientific
  regression tests, README/current documentation, manuscript and status-report
  sources/PDFs, result inventory, v3 manifest, the new filtered figure, and its
  exclusion audit table.
- **Contribution:** Added
  `v3_all_object_growth_tracks_full_assumptions_uncertainty_filtered.png`.
  The reproducible display filter excludes only growth-eligible luminous
  quasars whose maximum reported black-hole-mass uncertainty exceeds 0.5 dex.
  It removes seven GNIRS50 objects (J0300-2232, J0221-0802, J2307+0031,
  J0033-0125, J2356+0023, J1335+3533, and J2329-0403), leaving all other
  numerical objects and all 23 no-inference markers. The exact rows are stored
  in `v3_growth_track_uncertainty_filter.csv`.
- **Scientific/technical effect:** This is a visualization sensitivity product
  only. The canonical catalogue, unfiltered companion, model curves, rankings,
  and numerical science tables remain unchanged. The archived status source
  was also corrected to reference the flattened two-product gallery layout.
- **Validation:** The public atlas notebook rebuilt all v1/v2/v3 products and
  the public verification notebook passed. All 34 tests pass; provenance covers
  all 11 v3 source families; manifests contain 84/262/479 artifacts; the result
  inventory contains 795 artifacts; exact CSV reproduction, nesting, image
  resolution, and the explicit seven-object selection verify. Both nine-page
  PDFs were rebuilt and visually inspected without clipping or layout defects.
- **Status:** Complete and verified locally; included in the accompanying
  repository commit.

### 2026-09-02 - Raise filtered growth-track cutoff to 0.7 dex

- **Objective:** Revise the luminous-quasar uncertainty filter from 0.5 dex to
  the requested 0.7 dex threshold.
- **Contribution:** The filtered companion now excludes four rather than seven
  luminous quasars: J0300-2232, J0221-0802, J2307+0031, and J0033-0125. The
  selection remains strictly greater than the threshold, so a measurement at
  exactly 0.70 dex would remain included. Regenerated the audit CSV, figure,
  inventory, v3 manifest, current documentation, manuscript, and status report.
- **Scientific/technical effect:** Display-only selection change. The canonical
  catalogue, unfiltered figure, rankings, model curves, and science tables are
  unchanged.
- **Validation:** All 34 tests, provenance checks, version checks, manifest and
  inventory checks, exact CSV reproduction, and dataset nesting pass. Both
  nine-page PDFs and the revised 4500-by-3750 PNG were rebuilt and visually
  inspected without layout defects.
- **Status:** Complete and verified locally; included in the accompanying
  repository commit.

### 2026-09-02 - Reframe all growth-track axes to redshift 10--3

- **Objective:** Center the observed objects more effectively in every combined
  growth-track visualization without changing figure dimensions or plot
  margins.
- **Contribution:** Changed the shared reversed observed-redshift limits from
  12.2--3.8 to exactly 10--3 for the v1, v2, and v3 overview figures and both
  comprehensive v3 companions. Extended the model-curve grids to $z=3$ and
  updated the comprehensive figures' cosmic-age ticks to cover integer
  redshifts 10 through 3. Updated the current documentation, claim audit,
  manuscript, and archived status report.
- **Scientific/technical effect:** Visual framing only. Catalogue membership,
  object values, uncertainties, growth equations, assumptions, rankings, and
  plot dimensions/margins are unchanged.
- **Validation:** Regenerated and visually inspected all five growth-track
  figures. All 34 tests, provenance checks, version checks, manifests, result
  inventory, exact CSV reproduction, and dataset nesting pass. Both nine-page
  PDFs were rebuilt and their updated figure pages visually inspected without
  clipping or layout defects.
- **Status:** Complete and verified locally; included in the accompanying
  repository commit.

### 2026-09-02 - Increase growth-track class-color contrast

- **Objective:** Make the two numerical object classes easier to distinguish in
  every combined growth-track visualization.
- **Contribution:** Added a growth-track-specific class palette using purple
  (`#7B2CBF`) for broad-line AGN and red (`#D62728`) for luminous quasars.
  Applied it to points, uncertainties, legends, and applicable no-inference
  markers in the v1, v2, and v3 overviews and both comprehensive v3 companions.
  Other repository figures retain their existing class colors. Updated current
  documentation, claim audit, manuscript, and status report.
- **Scientific/technical effect:** Visual encoding only. Data, uncertainties,
  models, selections, rankings, axes, dimensions, and margins are unchanged.
- **Validation:** Regenerated and visually inspected all five growth-track
  figures. All 34 tests, provenance checks, version checks, manifests, result
  inventory, exact CSV reproduction, and dataset nesting pass. Both nine-page
  PDFs were rebuilt and the updated figure pages visually inspected without
  clipping or layout defects.
- **Status:** Complete and verified locally; included in the accompanying
  repository commit.
