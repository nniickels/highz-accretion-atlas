# Focused scientific and editorial pass

Baseline reviewed: commit `8334746`. This is a code/data/source-supported review,
not external peer review or an exhaustive re-extraction of the literature.

## Verified and corrected

- Recomputed all displayed class/evidence counts, mass/redshift ranges, required
  f_Edd distribution summaries, primary-subset counts, uncertainty counts and
  follow-up categories from canonical v3 tables. Existing headline values agree.
- Checked the retained growth law against Equation 1 of [Dayal (2024)](https://research.rug.nl/files/1151545270/aa51481-24.pdf).
  The atlas's starting redshift and flat cosmology are its stated choices;
  it is not an exact rerun of that paper's parameter choices.
- Added the missing cosmic-age equation and numerical cosmology, explicit
  luminosity-based f_Edd definition, and clarified averaging/duty-cycle semantics.
- Defined the primary subset, distinguished GN-z11's UV estimator, and added
  227-object primary counts (12 point, eight p16, six P>=0.95), alongside the
  unchanged exploratory headline (14 point, ten p16, eight P>=0.95).
- Added an independently checked efficiency sensitivity: epsilon=1-sqrt(8/9)
  yields scaling 0.54594 and maximum required f_Edd=0.793, with no point estimate
  above unity. This prevents a model-independent super-Eddington interpretation.
- Specified compatibility intervals, inclusive boundaries, overgrowth meaning,
  and the limited meaning of the PBH-labelled scenario.
- Clarified fixed-redshift error sampling, deterministic random streams and
  Monte Carlo precision; checked units and captions. Corrected the introductory
  wavelength/age description, stated the membership cutoff, and removed awkward
  or overbroad language.
- Added a citation to the [pinned A2744-QSO1 direct-mass preprint](https://arxiv.org/abs/2508.21748v2)
  for the already documented deferred measurement. No new measurement is admitted.

- Added the original [Kerr orbit reference](https://adsabs.harvard.edu/pdf/1972ApJ...178..347B), checked its ISCO limits, and stated the zero-torque/photon-capture assumptions. The supercritical efficiency remains explicitly an illustrative luminosity ansatz.

## Remaining scientific work

Extend independent redshift and identity validation first, then other non-mass
fields used for scientific claims. A full calibration-aware posterior treatment
and population selection model remain separate research extensions. Source
transcription checks cannot establish whether the underlying mass estimators are
valid for every object. External subject-matter review remains recommended.

The catalogue, baseline science outputs and figure data are unchanged. New tests
check the added subset and efficiency claims; the draft PDF is rebuilt and
visually reviewed. Journal selection, affiliations, funding acknowledgements and
a permanent release/archive identifier still need author input before submission.

## Subsequent identity audit

The [5 September audit](../docs/source-notes/redshift-identity-audit.md) supersedes
the earlier redshift/identity coverage assessment: all central redshifts and
available coordinates are checked, but three scientific identity groups remain
open. Unique-object counts and affected interpretations require reconciliation.

## Correction and interpretation update — 7 September 2026

Two supported mass-free duplicates were merged while retaining all 350 source
measurements. The current catalogue has 338 object records (237 numerical,
101 mass-free), with three identity groups still open. Numerical growth and
uncertainty results remain unchanged. Counts, affected figures, manifests,
uncertainty-model metadata, and draft prose were updated together. The discussion
now distinguishes the early-redshift tail, algebraic efficiency sensitivity,
physical growth feasibility, and the catalogue's contribution. The limitations
list the outstanding identities and exact source-audit scope; the conclusion
prioritizes their resolution before optional demographic extensions.


## Conservative manuscript scope — 7 September 2026

The remaining identity dependency is addressed by excluding all six affected
records from manuscript inference, retaining all source data and unresolved
audit dispositions. The 224/234 primary/exploratory samples preserve all tested
threshold counts and top-five rankings; the primary reference median becomes
0.578. Reproducible masks, before/after summaries, and mutation tests ensure
these exclusions cannot silently lose a group or readmit an affected object.
The full-catalogue identity gate still fails; only the conservative manuscript
exclusion check passes. Unique-object census finalization remains separate.

## Mass-scale sensitivity and presentation — 7 September 2026

The five manuscript figures now use the conservative 224/234 selection. A fixed
virial-mass offset experiment translates the original reported-error draws by
-0.5, -0.3, 0, +0.3 and +0.5 dex; this is a coherent stress test, not added
independent scatter or a systematic-marginalized posterior. At the extremes,
primary point/p16/P>=0.95 counts become 6/4/3 and 19/16/13, versus 12/8/6 at
zero offset. The analysis is integrated into publication-product generation and
verification, with object-level outputs and regression checks for zero-offset
recovery, the analytic mass response, and missing-error handling.

The draft foregrounds these conditional results; class, provenance and release
bookkeeping is consolidated in appendices. The figure-path documentation is
corrected. Source-specific mass calibration and external scientific review
remain beyond this stress test.

## Source-aware manuscript revision — 7 September 2026

Implemented the manuscript assessment against catalogue baseline
`a40a0d28c6c8d0b7e0c98aea089629903c34f7be`:

- Reframed the title, abstract, introduction and conclusions around named
  observational tests, with the full twelve-object primary threshold set.
- Added generated source/mass/error/offset tables and source-linked caveats with
  proposed observations. UNCOVER-20466, COSMOS3D-13852 and RUBIES-EGS-55604 retain
  P>=0.95 after -0.5 dex. This is explicitly not estimator-independent robustness:
  the source-motivated -1/-2 dex COSMOS-3D check gives 1.115/0.916, and the
  narrow formal error on J0910_2028_12910 excludes its larger calibration scale.
- Added a controlled four-object comparison with Dayal (2024), Table 1 in
  arXiv:2407.07162v2. With the atlas cosmology fixed, it separates adopted
  mass/redshift changes from seeding at 25 versus 30. It is not a complete
  crossmatch or a reconstruction of the earlier population calculation.
- Evaluated the pinned A2744-QSO1 MOKA3D estimate (arXiv:2508.21748v2, p. 3 and
  Methods p. 11) as an external comparison, with exact normal error propagation.
  **Correction to the preliminary review expectation:** the 7.7 +/- 0.3 dex
  estimate gives f=0.9996 (rounded 1.000), interval 0.947--1.052 and conditional
  P=0.497. It is borderline, not securely below the threshold. The adopted 7.3
  +/- 0.2 dex virial estimate gives 0.929 and interval 0.895--0.964. No catalogue
  row or headline sample count is changed by this external comparison.
- Replaced crowded uncertainty and alternate-measurement scatterplots with
  named interval and paired-value plots; added fixed-efficiency seed boundaries.
  Moved the full compatibility grid and Kerr algebra to the appendix, renamed
  the broad mass interval, and cited the motivation for logarithmic luminosity
  growth while preserving the distinction from a physical wind/slim-disk model.
- Added a generated 32-family inventory and a repository/version availability
  statement; removed artifact-count prose and shortened internal version history.
  No permanent archival DOI is claimed.

The new comparisons and their LaTeX fragments are generated and verified by the
existing notebook publication-selection entry points. External inputs and
editorial assessments are explicit in `paper/review_inputs.json`. New tests
check named survivors, source-count units, controlled comparison differences,
and the borderline direct-mass result; manuscript structural tests now read
included table fragments rather than requiring the obsolete five-row layout.

Validation: all 87 unit tests pass; publication selection and generated-table
verification pass; all six manuscript figures reproduce within the declared
pixel tolerance; v1/v2/v3 manifests, CSV reproduction and shared analysis
contracts pass. The rebuilt 21-page PDF has no LaTeX layout/citation warnings
and all pages were visually inspected, including a second inspection after
final flow adjustments. The pre-existing open identity gate remains explicitly
reported and is not treated as resolved by this revision.

## Joint revision sensitivity and presentation — 7 September 2026

Applied the published Baccus redshift/mass/error substitutions after all
manuscript identity exclusions, separately for primary and exploratory samples.
The 44 position-confirmed exact matches remain. Of five unmatched frozen records,
one is already identity-excluded; retaining or omitting the other four yields
224/220 primary and 234/230 exploratory objects. Recomputed quoted-error results
preserve primary 12/8/6 and exploratory 14/10/8 threshold counts and each sample's
top-five ordering. Generated per-object CSVs, six-scenario summary and LaTeX
rows are integrated into the publication generation and verification entry points.
This closes the previously separate-test limitation without changing canonical
catalogue membership or claiming identity resolution.

Moved the detailed catalogue accounting table to the source appendix, removed
the repeated discussion of mass-free evidence, and condensed repeated inference
caveats while retaining their full methodological definitions and limitations.
The new combined-test table keeps the sensitivity result explicit in the text.

Validation: all 93 unit tests pass, including the joint-sample regression and
analytic revised-mass check. Publication CSVs and generated TeX fragments verify;
v1/v2/v3 catalogue/science reproduction, manifests and inventory checks pass.
The revised 21-page PDF compiles without warnings and was visually inspected.
