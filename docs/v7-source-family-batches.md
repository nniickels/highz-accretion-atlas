# v7 source-family batch ingestion

The catalogue now admits independently audited sources in coherent evidence-
family batches. Row count is not the limiting factor: selection functions,
mass methods, identity resolution, and evidence semantics are. A batch may
contain several papers or one large homogeneous survey, but it must represent
one evidence family and pass a common release gate.

The executable foundation is `src/v7_batch.py`. Each source adapter returns a
`SourceAdmissionBundle` containing its validated measurement rows and optional
long-form observables. The generic assembler then requires:

1. one nonblank and unique `source_key` per bundle;
2. one coherent `evidence_family` across the batch;
3. unique measurement and observable identifiers;
4. source-local observable foreign keys;
5. the canonical v7 admission and standardized-compatibility contracts;
6. coordinate/redshift candidate searches against the prior release and
   between new sources; and
7. explicit review before any candidate identity can enter a frozen release.

Source-specific code remains responsible for authoritative extraction,
scientific interpretation, stable physical-object and host-system assignment,
and any reviewed identity decision. The generic assembler never promotes a
coordinate match into scientific identity automatically.

`data/source_family_registry.csv` records released and selected batches and is
validated by `load_source_family_registry` in `src/v7_batch.py`. A source moves
through `selected_pending_source_audit`, `extracted`, `admitted`, and
`released_catalogue_layer`; status cannot substitute for the corresponding raw
file, validator, tests, and manifest.

## Released first larger batch: XQR-30

The first post-v7.0 batch is the luminous-quasar comparison family represented
by Mazzucchelli et al. (2023), XQR-30, A&A 676 A71,
DOI `10.1051/0004-6361/202346317`, arXiv `2306.16474v1`.

The primary paper reports a homogeneous table for 42 luminous quasars at
`z>6`, based on high-S/N VLT/X-shooter spectra. Its table includes redshift,
C IV and Mg II FWHM, C IV blueshift, 1350/3000-A luminosities, bolometric
luminosity, C IV- and Mg II-based virial masses, and the corresponding
Eddington ratios. This is large enough to exercise batch ingestion while
remaining a single, clearly separated selection and mass-comparability family.

Admission decisions to freeze during the source audit:

- use `object_class=luminous_quasar_comparison` and keep this stratum separate
  from faint JWST candidate populations;
- use the paper's Mg II estimate as the canonical row-level mass when
  available, because the paper uses Mg II for its principal comparison;
- retain C IV mass, corrected width, blueshift, and Eddington ratio as explicit
  alternate source observables rather than silently discarding them;
- store the quoted approximately `0.55 dex` Mg II scaling-relation systematic
  separately from table-fit uncertainties;
- preserve telluric-absorption and low-S/N caveats named by the paper;
- review the 23 objects with earlier literature measurements as measurement
  versions of existing physical objects where applicable;
- treat the lensed quasar J0439+1634 with explicit magnification provenance,
  rather than inheriting the paper's demographic exclusion as missing data;
- audit aliases and coordinates from an authoritative companion table before
  assigning physical-object IDs; and
- generate catalogue products and source/class strata only. Do not pool this
  luminous comparison family into v7 growth rankings or demographics.

XQR-30 passed this gate in catalogue-only v7.1. The complete 42-row mass table,
42-row companion coordinate table, source-archive hashes, seven telluric
caveats, one CIV low-S/N caveat, lensing treatment, 23-record external-
literature identity audit, source validator, regression tests, and immutable
v7.1 manifest are checked in. See `docs/xqr30-extraction-notes.md`.

No subsequent family may be appended directly to the v7.1 filenames. It must
receive a new release prefix and repeat the same source-audit and identity gate.

Primary source: <https://arxiv.org/abs/2306.16474v1>.

## Released second larger batch: GNIRS-50

Shen et al. (2019) passed the same gate in catalogue-only v7.2. The complete
50-row sample and 50-row spectral catalogue are machine-readable through CDS.
The release preserves 29 MgII fiducial masses, 20 CIV-only fiducial masses, one
explicitly massless object, 629 available source observables, eight BAL flags,
and four radio-loud flags. Six identities shared with XQR-30 are reviewed and
merged without discarding either measurement. See
`docs/shen19-gnirs50-extraction-notes.md`.

The larger 50-row admission demonstrates that batch size can increase once a
source has complete authoritative tables. It does not relax the source gate:
SHELLQs XVII was evaluated but deferred because its public archive lacks the
131-row object-level measurement table needed for reproducible admission.
