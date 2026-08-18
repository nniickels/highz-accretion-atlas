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
- **Status:** Complete and verified locally; changes are not yet committed.

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
- **Status:** Complete and verified locally; changes are not yet committed.

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
- **Status:** Complete and verified locally; changes are not yet committed.

### 2026-08-17 - Harden source-consistency ranking and validation

- **Objective:** Fix the two dormant uncertainty-ranking defects identified during the repository-wide review: source-consistency priorities could be overwritten by derived pressure or host-ratio categories, and the production verifier incorrectly required at least one source inconsistency to exist.
- **Files changed:**
  - `scripts/generate_v1_uncertainty_rankings.py` (modified)
  - `tests/test_v1_pipeline.py` (modified)
  - `.codex_tmp/CONTRIBUTION_LEDGER.md` (modified)
- **Contribution:** Moved `D_source_consistency` to the first branch of the uncertainty follow-up categorizer so values awaiting source clarification remain quarantined regardless of their derived growth-pressure or host-ratio tiers. Changed the verification invariant to treat a catalogue with no source inconsistencies as valid while still requiring every inconsistency that does exist to preserve its category. Added regression cases that combine source inconsistency with likely high pressure and an extreme host ratio, and that verify a synthetic clean catalogue containing no source inconsistencies.
- **Scientific/technical effect:** Future source-inconsistent rows cannot be promoted to a physical-pressure or host-tension category before their inputs are clarified, and valid clean catalogues no longer fail production verification. Current v1 uncertainty probabilities, scores, categories, ranks, and result tables are unchanged.
- **Validation:** Re-ran the deterministic 10,000-sample uncertainty pipeline with seed `20260808`; all nine production sanity checks passed and Git showed no changes to the three regenerated uncertainty result tables. All 27 regression tests passed, including both new synthetic edge cases. `git diff --check` passed.
- **Status:** Complete and verified locally; changes are not yet committed.

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
- **Status:** Complete and verified locally; changes are not yet committed.
