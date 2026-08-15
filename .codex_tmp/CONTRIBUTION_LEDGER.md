# Codex Contribution Ledger

Purpose: maintain an append-only chronological record of Codex contributions to this repository so work can be audited and summarized later.

## Maintenance rule

For every future Codex contribution that changes repository files:

1. Append a dated entry to this ledger; do not replace prior history except to correct a factual error.
2. Record the objective, files changed, scientific or technical effect, validation performed, and current status.
3. Update `.codex_tmp/highz_accretion_atlas_status.tex` when the contribution changes an overall method, major capability, result, limitation, figure, or roadmap stage.
4. Recompile and visually verify `.codex_tmp/highz_accretion_atlas_status.pdf` whenever the LaTeX paper changes.
5. Minor mechanical changes may be recorded in the ledger without receiving detailed paper coverage; the paper should summarize major steps and durable results rather than every edit.

## Chronological entries

### 2026-08-12 - Uncertainty-aware main-text figure

- **Objective:** Turn the Monte Carlo uncertainty products into a compact, publication-style visualization.
- **Files changed:**
  - `scripts/generate_v1_final_figures.py`
  - `results/v1_main_text_figures/v1_main_text_uncertainty_forest.png`
  - `docs/getting-started.md`
  - `docs/v1-figure-inventory.md`
- **Contribution:** Added a two-panel uncertainty forest plot ordered by the uncertainty-aware pressure rank. The plot shows baseline 5th--95th and 16th--84th percentile intervals, Monte Carlo medians, original point estimates, separate `MBH +/- 0.3 dex` systematic medians, robust/tentative measurement status, physical thresholds, and per-object threshold probabilities. Integrated the output into the existing final-figure generator and documented the new product.
- **Validation:** Generated and visually inspected the PNG; confirmed all 23 objects and both probability columns were legible; ran the full 23-test regression suite successfully; checked the patch with `git diff --check`.
- **Status:** Complete and present in repository commit `15a1b3f` (`Document monte carlo sample results`).

### 2026-08-13 - Project-status paper and contribution ledger

- **Objective:** Document the completed project, current scientific interpretation, repository workflow, limitations, and future research goals in a concise paper with figures.
- **Files added:**
  - `.codex_tmp/highz_accretion_atlas_status.tex`
  - `.codex_tmp/highz_accretion_atlas_status.pdf`
  - `.codex_tmp/CONTRIBUTION_LEDGER.md`
- **Contribution:** Added a LaTeX project-status manuscript organized chronologically from data provenance through standardization, physical modeling, scenario evaluation, ranking, Monte Carlo uncertainty propagation, current findings, validation, limitations, and the staged research roadmap. Embedded the mass--redshift overview, uncertainty forest plot, pressure-versus-confidence plot, and seed-redshift spotlight maps. Established this ledger as the ongoing record for future Codex work.
- **Validation:** LaTeX compilation and PDF rendering/visual inspection completed; final page count, embedded figures, text extraction, and layout were checked. No source or result tables were altered by the documentation build.
- **Status:** Complete as of the latest successful PDF quality check recorded in this session.

### 2026-08-15 - Correct tentative broad-Hbeta evidence and virial-mass metadata

- **Objective:** Correct the first must-address scientific metadata issue by distinguishing the four high-redshift tentative broad-Hbeta candidates from the robust broad-Halpha sample and carrying that distinction through the analysis products.
- **Files changed:**
  - `data/raw/v1_raw.csv`
  - `data/processed/v1_processed.csv`
  - `data/sources.md`
  - `src/standardize_data.py`
  - `scripts/generate_v1_rankings.py`
  - `scripts/generate_v1_uncertainty_rankings.py`
  - `scripts/v1_evaluate.ipynb`
  - `results/v1_object_ranking_table.csv`
  - `results/v1_uncertainty_aware_ranking_table.csv`
  - `results/v1_uncertainty_required_fedd_summary.csv`
  - `results/v1_uncertainty_required_mseed_summary.csv`
  - `tests/test_v1_pipeline.py`
  - `docs/catalogue-schema.md`
  - `docs/v1-ranking-metrics.md`
  - `docs/v1-uncertainty-propagation.md`
  - `.codex_tmp/highz_accretion_atlas_status.tex`
  - `.codex_tmp/highz_accretion_atlas_status.pdf`
  - `.codex_tmp/CONTRIBUTION_LEDGER.md`
- **Contribution:** Corrected GS-20057765, GS-20030333, GS-164055, and GN-4685 from single-epoch broad-Halpha to broad-Hbeta virial-mass metadata. Added a controlled `detection_evidence` field, mapped it deterministically to `quality_flag`, and propagated the evidence and mass method through point and uncertainty products. The four candidates are now consistently represented as stack-supported tentative broad-Hbeta measurements with low confidence and explicit caveats that their individual broad-component detections are not formally significant. No getting-started or reproduction-guide material was changed.
- **Scientific effect:** The physical-pressure and uncertainty-pressure rank order is unchanged, but the evidential status and follow-up interpretation of the four tentative high-redshift candidates are now explicit and source-consistent.
- **Validation:** Re-ran the complete processing, point-ranking, and 10,000-sample uncertainty pipeline with seed `20260808`; all pipeline sanity checks passed and regenerated hashes were unchanged. All 24 regression tests passed. Exact-four-object invariants, evidence-to-quality mapping, confidence tiers, caveat tags, and unchanged rank mappings were checked directly. `git diff --check` passed. The status PDF was recompiled, rendered, and visually inspected after this entry was added.
- **Status:** Complete and verified locally; changes are not yet committed.
