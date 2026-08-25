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
  - `docs/getting-started.md` (modified)
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
  - `data/processed/v1_processed.csv` (modified)
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
  - `docs/catalogue-schema.md` (modified)
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
  - `data/processed/v1_processed.csv` (modified)
  - `data/sources.md` (modified)
  - `src/standardize_data.py` (modified)
  - `scripts/generate_v1_rankings.py` (modified)
  - `scripts/generate_v1_uncertainty_rankings.py` (modified)
  - `scripts/v1_evaluate.ipynb` (modified)
  - `results/v1_evaluation_table.csv` (modified)
  - `results/v1_required_fedd_by_seed_mass.csv` (modified)
  - `results/v1_required_mseed_by_growth_assumption.csv` (modified)
  - `results/v1_object_ranking_table.csv` (modified)
  - `results/v1_uncertainty_required_fedd_summary.csv` (modified)
  - `results/v1_uncertainty_required_mseed_summary.csv` (modified)
  - `results/v1_uncertainty_aware_ranking_table.csv` (modified)
  - `results/v1_main_text_figures/v1_main_text_pressure_vs_confidence.png` (modified)
  - `tests/test_v1_pipeline.py` (modified)
  - `docs/catalogue-schema.md` (modified)
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
  - `docs/getting-started.md` (modified)
  - `docs/release-versioning.md` (added)
  - `.codex_tmp/catalogue-expansion-guide.md` (modified)
  - `.codex_tmp/observational-atlas-roadmap.md` (modified)
  - `.codex_tmp/research-grade-observational-atlas-roadmap-detailed.md` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.tex` (modified)
  - `.codex_tmp/highz_accretion_atlas_status.pdf` (modified)
  - `data/crossmatch/measurement_object_links.csv` -> `data/crossmatch/v3_measurement_object_links.csv` (renamed)
  - `data/processed/expanded_blagn_measurements.csv` -> `data/processed/v3_blagn_measurements.csv` (renamed and release metadata updated)
  - `data/processed/expanded_blagn_objects.csv` -> `data/processed/v3_blagn_objects.csv` (renamed and release metadata updated)
  - `docs/expanded-blagn-catalogue-schema.md` -> `docs/v3-blagn-catalogue-schema.md` (renamed and modified)
  - `docs/expanded-blagn-science-workflow.md` -> `docs/v3-blagn-science-workflow.md` (renamed and modified)
  - `docs/v1-figure-inventory.md` -> `docs/v2-figure-inventory.md` (renamed and modified)
  - `docs/v1-ranking-metrics.md` -> `docs/v2-ranking-metrics.md` (renamed and modified)
  - `docs/v1-uncertainty-propagation.md` -> `docs/v2-uncertainty-propagation.md` (renamed and modified)
  - `docs/v2-candidate-black-hole-papers.md` -> `docs/catalogue-expansion-candidates-legacy.md` (renamed and marked as a legacy planning memo)
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
  - `results/v1_object_ranking_table.csv` -> `results/v2_object_ranking_table.csv` (renamed and release metadata updated)
  - `results/v1_uncertainty_aware_ranking_table.csv` -> `results/v2_uncertainty_aware_ranking_table.csv` (renamed and release metadata updated)
  - `results/v1_uncertainty_required_fedd_summary.csv` -> `results/v2_uncertainty_required_fedd_summary.csv` (renamed and release metadata updated)
  - `results/v1_uncertainty_required_mseed_summary.csv` -> `results/v2_uncertainty_required_mseed_summary.csv` (renamed and release metadata updated)
  - `results/v1_main_text_figures/v1_main_text_mbh_redshift_growth_overview.png` -> `results/v2_main_text_figures/v2_main_text_mbh_redshift_growth_overview.png` (renamed)
  - `results/v1_main_text_figures/v1_main_text_pressure_vs_confidence.png` -> `results/v2_main_text_figures/v2_main_text_pressure_vs_confidence.png` (renamed)
  - `results/v1_main_text_figures/v1_main_text_ranked_required_fedd.png` -> `results/v2_main_text_figures/v2_main_text_ranked_required_fedd.png` (renamed)
  - `results/v1_main_text_figures/v1_main_text_ranked_required_seed_mass.png` -> `results/v2_main_text_figures/v2_main_text_ranked_required_seed_mass.png` (renamed)
  - `results/v1_main_text_figures/v1_main_text_spotlight_seed_redshift_maps.png` -> `results/v2_main_text_figures/v2_main_text_spotlight_seed_redshift_maps.png` (renamed)
  - `results/v1_main_text_figures/v1_main_text_uncertainty_forest.png` -> `results/v2_main_text_figures/v2_main_text_uncertainty_forest.png` (renamed)
  - `results/expanded_blagn_catalogue_summary.csv` -> `results/v3_blagn_catalogue_summary.csv` (renamed)
  - `results/expanded_blagn_growth_summary.csv` -> `results/v3_blagn_growth_summary.csv` (renamed)
  - `results/expanded_blagn_measurement_evaluation.csv` -> `results/v3_blagn_measurement_evaluation.csv` (renamed)
  - `results/expanded_blagn_measurement_point_ranking.csv` -> `results/v3_blagn_measurement_point_ranking.csv` (renamed)
  - `results/expanded_blagn_measurement_uncertainty_fedd.csv` -> `results/v3_blagn_measurement_uncertainty_fedd.csv` (renamed)
  - `results/expanded_blagn_measurement_uncertainty_mseed.csv` -> `results/v3_blagn_measurement_uncertainty_mseed.csv` (renamed)
  - `results/expanded_blagn_measurement_uncertainty_ranking.csv` -> `results/v3_blagn_measurement_uncertainty_ranking.csv` (renamed)
  - `results/expanded_blagn_physical_object_evaluation.csv` -> `results/v3_blagn_physical_object_evaluation.csv` (renamed)
  - `results/expanded_blagn_physical_object_point_ranking.csv` -> `results/v3_blagn_physical_object_point_ranking.csv` (renamed)
  - `results/expanded_blagn_physical_object_uncertainty_fedd.csv` -> `results/v3_blagn_physical_object_uncertainty_fedd.csv` (renamed)
  - `results/expanded_blagn_physical_object_uncertainty_mseed.csv` -> `results/v3_blagn_physical_object_uncertainty_mseed.csv` (renamed)
  - `results/expanded_blagn_physical_object_uncertainty_ranking.csv` -> `results/v3_blagn_physical_object_uncertainty_ranking.csv` (renamed)
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
  - `data/processed/v4_blagn_measurements.csv` (added)
  - `data/processed/v4_blagn_objects.csv` (added)
  - `data/crossmatch/v4_measurement_object_links.csv` (added)
  - `data/crossmatch/v4_object_aliases.csv` (added)
  - `data/crossmatch/v4_reviewed_match_candidates.csv` (added)
  - `docs/getting-started.md` (modified)
  - `docs/release-versioning.md` (modified)
  - `docs/v3-blagn-catalogue-schema.md` (modified)
  - `docs/v3-blagn-science-workflow.md` (modified)
  - `docs/matthee23-eiger-fresco-extraction-notes.md` (added)
  - `docs/lin24-aspire-extraction-notes.md` (added)
  - `docs/v4-blagn-catalogue-schema.md` (added)
  - `docs/v4-blagn-science-workflow.md` (added)
  - `scripts/generate_v3_final_figures.py` (added)
  - `scripts/process_v4_blagn.py` (added)
  - `scripts/generate_v4_blagn_science.py` (added)
  - `src/identity.py` (added)
  - `src/v4_catalogue.py` (added)
  - `src/v4_science.py` (added)
  - `tests/test_v4_blagn_pipeline.py` (added)
  - `tests/test_v4_blagn_science.py` (added)
  - `results/v3_main_text_figures/v3_main_text_mbh_redshift_growth_overview.png` (added)
  - `results/v3_main_text_figures/v3_main_text_ranked_required_fedd.png` (added)
  - `results/v3_main_text_figures/v3_main_text_uncertainty_forest.png` (added)
  - `results/v3_main_text_figures/v3_main_text_source_stratified_coverage.png` (added)
  - `results/v4_blagn_catalogue_summary.csv` (added)
  - `results/v4_blagn_growth_summary.csv` (added)
  - `results/v4_blagn_measurement_evaluation.csv` (added)
  - `results/v4_blagn_measurement_point_ranking.csv` (added)
  - `results/v4_blagn_measurement_uncertainty_fedd.csv` (added)
  - `results/v4_blagn_measurement_uncertainty_mseed.csv` (added)
  - `results/v4_blagn_measurement_uncertainty_ranking.csv` (added)
  - `results/v4_blagn_physical_object_evaluation.csv` (added)
  - `results/v4_blagn_physical_object_point_ranking.csv` (added)
  - `results/v4_blagn_physical_object_uncertainty_fedd.csv` (added)
  - `results/v4_blagn_physical_object_uncertainty_mseed.csv` (added)
  - `results/v4_blagn_physical_object_uncertainty_ranking.csv` (added)
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
  - `docs/getting-started.md` (modified)
  - `docs/release-versioning.md` (modified)
  - `docs/v4-blagn-catalogue-schema.md` (modified)
  - `docs/v4-blagn-science-workflow.md` (modified)
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
  - `data/crossmatch/v4_reviewed_identity_overrides.csv` (added)
  - `data/crossmatch/v4_reviewed_match_candidates.csv` (modified)
  - `data/processed/v4_blagn_objects.csv` (modified)
  - `docs/getting-started.md` (modified)
  - `docs/release-versioning.md` (modified)
  - `docs/v2-figure-inventory.md` (modified)
  - `docs/v4-blagn-catalogue-schema.md` (modified)
  - `docs/v4-blagn-science-workflow.md` (modified)
  - `results/v4_blagn_alternate_measurement_sensitivity.csv` (added)
  - `results/v4_blagn_catalogue_summary.csv` (modified)
  - `results/v4_blagn_measurement_point_ranking.csv` (modified)
  - `results/v4_blagn_measurement_uncertainty_ranking.csv` (modified)
  - `results/v4_blagn_physical_object_point_ranking.csv` (modified)
  - `results/v4_blagn_physical_object_uncertainty_ranking.csv` (modified)
  - `results/v4_main_text_figures/v4_main_text_mbh_redshift_growth_overview.png` (added)
  - `results/v4_main_text_figures/v4_main_text_ranked_required_fedd.png` (added)
  - `results/v4_main_text_figures/v4_main_text_uncertainty_forest.png` (added)
  - `results/v4_main_text_figures/v4_main_text_source_stratified_coverage.png` (added)
  - `results/v4_main_text_figures/v4_main_text_measurement_choice_sensitivity.png` (added)
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
  - `data/crossmatch/v4_reviewed_identity_overrides.csv` (modified)
  - `data/crossmatch/v4_reviewed_match_candidates.csv` (metadata column added)
  - `data/mass_method_registry.csv` (added)
  - `data/sources.md` (modified)
  - `docs/getting-started.md` (modified)
  - `docs/model-menu.md` (modified)
  - `docs/release-versioning.md` (modified)
  - `docs/v4-blagn-catalogue-schema.md` (modified)
  - `docs/v4-blagn-science-workflow.md` (modified)
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
  - `data/processed/v5_blagn_measurements.csv` (added)
  - `data/processed/v5_blagn_objects.csv` (added)
  - `data/crossmatch/v5_measurement_object_links.csv` (added)
  - `data/crossmatch/v5_object_aliases.csv` (added)
  - `data/crossmatch/v5_reviewed_identity_overrides.csv` (added)
  - `data/crossmatch/v5_reviewed_match_candidates.csv` (added)
  - `data/mass_method_registry.csv` (modified)
  - `data/sources.md` (modified)
  - `docs/getting-started.md` (modified)
  - `docs/release-versioning.md` (modified)
  - `docs/v2-figure-inventory.md` (modified)
  - `docs/harikane23-nirspec-extraction-notes.md` (added)
  - `docs/object-taxonomy.md` (added)
  - `docs/v5-blagn-catalogue-schema.md` (added)
  - `docs/v5-blagn-science-workflow.md` (added)
  - `docs/v5-manuscript-claim-audit.md` (added)
  - `scripts/process_v5_blagn.py` (added)
  - `scripts/generate_v5_blagn_science.py` (added)
  - `src/object_taxonomy.py` (added)
  - `src/v5_catalogue.py` (added)
  - `src/v5_science.py` (added)
  - `tests/test_v5_blagn_pipeline.py` (added)
  - `tests/test_v5_blagn_science.py` (added)
  - 13 `results/v5_blagn_*.csv` science products (added)
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
- **Status:** Complete and verified locally; changes are uncommitted.
