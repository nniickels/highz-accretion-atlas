# Manuscript shortening — 11 September 2026

The main draft was shortened from 22 to 19 pages, including appendices and
references. The separate supplement is four pages.

- Moved the complete compatibility grid, spin/efficiency prescription and
  early-start/primordial-seed illustration to `supplementary_material.tex`.
- Moved the catalogue navigation score to `docs/guides/catalogue-navigation-score.md`.
- Moved detailed source admission, preferred-measurement and classification
  accounting to `docs/source-notes/manuscript-catalogue-bookkeeping.md`.
  Retained the source inventory, sample counts and unresolved identity exclusions
  in the manuscript.
- Consolidated repeated statements about mass errors, scenario probabilities,
  sample selection and fixed catalogue membership.
- Retained Table 1 and its calibration notes and mass margins, the uncertainty
  and efficiency-boundary figures, both controlled measurement comparisons,
  numerical results and scientific qualifications.
- Updated bibliography generation and checks for the two-document organization.
  Corrected the table-validation parser to ignore calibration footnote markers
  when comparing object names; numerical checks remain in place.

Both PDFs compile without LaTeX warnings or unresolved references. The final
layouts were inspected. No catalogue data, model calculations or numerical
figure/table outputs were changed.

Validation: all 99 unit tests pass. The main and supplementary Overleaf sources
were checked against the local sources after expanding generated table fragments
and adjusting figure paths for the existing Overleaf project layout.

## Compatibility appendix restored

Following review of the plot's role, the compatibility grid and its efficiency
prescription and seed-range methods were returned to Appendix C. The main text
briefly directs readers there. The early-start/primordial-seed illustration
remains in the supplement. The resulting manuscript has 21 pages and the
supplement has two. Numerical results and plot files are unchanged.

Both PDFs compile without warnings; the restored appendix and supplementary
figure layout were inspected. All 11 repository-layout tests pass, including
figure availability and separate citation/bibliography checks for both documents.
Both Overleaf sources were compared with their prepared local equivalents.
