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
