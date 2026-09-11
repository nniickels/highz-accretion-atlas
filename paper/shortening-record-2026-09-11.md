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

## Repetition and procedural-detail edits

Removed the five agreed repeated qualifications in the offset methods,
mass-scale results, discussion and compatibility appendix/caption. Preserved
qualifications in the abstract, Table 1 notes and conclusions.

Moved the Baccus central-mass change count/range and coordinate-validation counts
to `docs/source-notes/manuscript-catalogue-bookkeeping.md`. Moved the compatibility
code-key explanation and detailed notebook verification description to
`docs/guides/reproducibility.md`, referenced by the shortened data statement.
The catalogue baseline identifier and analysis-input paths are retained.

Table 6 and its generated inputs are unchanged pending discussion of its role.
The manuscript compiles without warnings and all 11 repository-layout checks
pass. The prepared Overleaf main source matches the local manuscript.

## Table 6 reduced to mass-estimator caveats

Removed the proposed-observation column while preserving all twelve object-specific
caveats. Updated the table generator so regeneration retains the two-column format.
Replaced claims about an observing programme in the introduction, table references
and conclusion. Section 5.2 now briefly discusses scattering in COSMOS3D-13852,
confirmation of the broad Hβ component in CEERS-1019, and independent calibration
for J0910_2028_12910 in relation to its 0.330-dex threshold margin.

No numerical results changed. All 99 tests and the publication-generation checks
pass. The final PDF compiles without warnings; the table and discussion layout
were inspected. The Overleaf source matches the prepared local manuscript.

## Two-object parameter-map comparison

Added Appendix D and Figure 7 comparing UNCOVER-20466 and GN-z11 in seed mass
and starting redshift, with common axes and colour scale. The figure uses the
catalogue central masses, efficiency 0.1 and no merger boost, over starting
redshifts 11–30. Its caption states sample membership and the absence of mass-error
propagation. The complete galleries remain online catalogue products.

Notebook 02 regenerates the new figure. All 99 tests pass. A direct growth
inversion check across both plotted parameter domains recovers the adopted
masses, and the required rates decrease with seed mass and earlier starting
redshift. The local manuscript compiles without warnings and the figure and
compiled page were inspected. Overleaf propagation is pending upload of the
new PDF; the extension denied file access and the native picker did not complete.
