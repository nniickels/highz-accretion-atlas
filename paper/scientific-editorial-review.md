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
