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
