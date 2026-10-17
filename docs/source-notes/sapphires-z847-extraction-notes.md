# SAPPHIRES z=8.47 source extraction

Primary source: Fudamoto et al., [arXiv:2503.15597v1](https://arxiv.org/html/2503.15597v1), submitted 19 March 2025. Retrieved/reviewed 17 October 2026 against the 3 September 2026 cutoff. The retrieved arXiv history lists only v1; no later version or journal reference was identified. All SAPPHIRES values below use that version. No processed catalogue has been changed.

## Scope and complete screen

Tables 1 and 2 describe the same ten spectroscopic/tentative objects; Table B1 adds seven photometric candidates. Appendix A presents spectra/cutouts of the spectroscopic sample rather than additional objects. Section IV.2 applies LRD color/morphology selection to both samples and identifies only ID-8760. Hβ in ordinary member galaxies is not independent evidence for accretion.

| IDs | Outcome | Reason |
| --- | --- | --- |
| 8760 | Propose one new v3 candidate/context object | LRD colors, marginal compactness and tentative broad Hβ; no published BH mass |
| 1967, 1988 | Exclude | Close galaxy pair; no source AGN evidence |
| 17832, 17882 | Exclude | Close galaxy pair; no source AGN evidence |
| 17929, 18743, 19406 | Exclude | Member galaxies; no source AGN evidence |
| 21284 | Exclude | Member with spectral contamination; no source AGN evidence |
| 16702 | Exclude | Tentative spectroscopic member; no source AGN evidence |
| 2508, 6385, 8764, 15524, 16324, 23481, 25528 | Exclude | Photometric candidates; none passes source LRD screen; no other source accretion evidence |

This is 17 individually identified objects, one admission proposal and 16 exclusions. The initial photometric search finds 17 candidates, of which four are already confirmed members and five have discordant spectroscopic redshifts (6.29–8.15); the paper does not identify those five rejected sources individually. The remaining eight are 16702 and the seven Table B1 candidates. Do not invent identities for the unnamed rejected sources or count the initial search as 17 additional galaxies. The six other z>8 galaxies mentioned in the wider EDR sample are not individually tabulated here. Neither unlisted group is an AGN sample.

MACS0416-Y1, MACS0416-JD (z=8.34) and f090d_018 (z=8.49) are external large-scale-structure comparisons in V.2.2, not additional SAPPHIRES AGN identifications. The paper's inconsistent approximate structure separations are not used for identity. ID-25528 has a separate bright foreground contaminant discussed in III.2; it must not be assumed to be ID-8760's neighbour.

## ID-8760 measurements and interpretation

Table 1 gives RA=63.9573331 deg, Dec=-24.1674685 deg and zspec=8.479, without redshift errors or an explicit coordinate frame. Preserve the decimal coordinates; do not assert a source-stated ICRS frame. Hβ FWHM is 1010±190 km/s; [O III] FWHM is 110±70 km/s. Fluxes are 32.4±5.0 and 17.7±2.5, respectively, in 10^-19 erg/s/cm². The table's last flux header says [O II]5007, but III.3 identifies the measured line as [O III]5008: retain that header in the source cells and map the observable to [O III] with this documented typo correction. Quoted line errors have no explicitly identified confidence convention in the measurement passage; do not silently label them posterior percentiles.

III.3 fits one Gaussian per line convolved with a modeled NIRCam R/C grism LSF, separately for each dispersion direction. Thus the reported width is from an LSF-aware forward fit: do not subtract instrumental resolution again. ID-8760 is explicitly exempted from tying Hβ width to [O III]. The paper does not provide a separate spatial/morphology broadening correction or a resolved broad+narrow Hβ decomposition. The fitted total Hβ flux is not automatically a broad-component virial luminosity.

IV.2 reports a **peak** Hβ significance of 2.5σ, distinct from integrated flux/error. F444W aperture flux ratio (0.4/0.2 arcsec diameter) is 1.58±0.04, exceeding Greene's 1.5 threshold; the authors attribute elevated large-aperture flux to a projected foreground neighbour and cite an alternative 1.7 criterion. Retain candidate status even though some source passages call it confirmed. Table 2 suppresses stellar mass, dust attenuation and SFR because galaxy-only SED fitting is unreliable for this object. Do not revive commented-out TeX estimates. The isolated prose ID-8740 and pair ID-1963 conflict with repeated table IDs 8760 and 1967; treat as apparent typographical variants, not new objects or independently secure aliases.

No BH mass, BH mass error, bolometric luminosity, Eddington ratio or calibrated BH-mass recipe is published for ID-8760. Halo masses in V.1 and stellar masses in Tables 2/B1 are not BH masses. Width alone cannot supply a catalogue mass. Leave all canonical mass and mass-error fields missing, with method `not_published`; no numerical growth calculations are supported.

Section II says cluster magnification in this parallel field is negligible (mu approximately <=1.1). Store this bound and source assessment, not an invented object-level mu=1.1 or a zero-error mu=1. No lensing or dust correction is applied to these source-native values. This does not establish that the unidentified foreground galaxy has no local lensing effect.

## Identity review

The source-specific crossmatch CSV scans every available coordinate in both v2/v3 measurement tables using great-circle distance, without a redshift prefilter. All 17 have zero matches within 2 arcsec. The closest existing measurement to 8760 is J0430M1445BHAE1_lin24, about 36059.61 arcsec away. Alias scans of both version tables and alias tables identify no SAPPHIRES/8760/MACS0416 counterpart. Rows without catalogue coordinates cannot be excluded by positional matching; no name evidence links them here.

The separately retained MACS0416 context crossmatch checks all four MACS0416 rows in the existing pinned Baccus published Table 1: 4750_50001, 4750_60009, 4750_60003 and 4750_22011. They are 378–440 arcsec away, at z=4.7079–5.9631; they cannot be the immediate foreground contaminant or ID-8760. They were not admitted to v2/v3 because of missing source-published lensing corrections.

For MACS0416-Y1, the concurrent source extraction retains host astrometry from Tamura v2 (04:16:09.415, -24:05:35.54) and z=8.312 from Takechi v1. The host is 379.30 arcsec from ID-8760 with delta-z=0.167. They are distinct systems; Y1's proposed broad-line measurement must not be attached to ID-8760. This supporting cross-check does not modify the other extraction's files or its membership proposal.

Figure 3 marks ID-8760's immediate foreground neighbour but supplies no catalogue ID, coordinate pair or redshift. Its individual identity remains **unresolved**; no forced alias, host merge or neighbour admission is justified. The nearby photometric ID-8764 is ~54.6 arcsec away and zphot=8.46, not an identification of that neighbour. Lack of a precise neighbour identity does not supply an alternative BH mass. The no-mass candidate can be retained with an explicit contamination caveat; integration should preserve the unresolved-neighbour flag rather than claim a completed neighbour identity audit.

## Proposed canonical mapping and registry information

Propose source key `fudamoto25_sapphires_z847`, measurement ID `SAPPHIRES8760_fudamoto25`, object display ID `SAPPHIRES-ID-8760`, physical ID `HZA-SAPPHIRES-ID-8760`, host ID `HZS-SAPPHIRES-ID-8760`. Only this new measurement is proposed, so it is preferred for its new object. Proposed placement is **v3 only**, with v1/v2 unchanged: the source is an overdensity/heterogeneous candidate study without supported single-epoch BH masses, not a comparable Balmer mass family. The presence of Hβ does not change the source-family placement.

Use object_class `broad_line_agn`, evidence_status `candidate`, spectroscopic_type `type1_broad_line_candidate`, phenotype `lrd`, selection channels `broad_hbeta;photometric_lrd`, and mass-comparability `no_numeric_mass` (integration must map these proposals to existing controlled values). Evidence basis must mention low peak significance and contaminated marginal compactness. Set growth and primary-growth flags false; manuscript-primary and expanded numerical-growth eligibility false. Reason: no published supported BH mass. Candidate inclusion in contextual discussion is separate from numerical manuscript membership.

Source registry proposal: arXiv DOI 10.48550/arXiv.2503.15597, exact version v1, source-native Table 1/Sections II, III.3, IV.2; retrieval date 2026-10-17. Manifest records SHA-256 for the retrieved archive, its retained `sample631.tex` member, HTML payload and retained evidence extract/version history. There is no source mass-method calibration to register. Selection is NIRCam WFSS [O III] member identification plus LRD screen in the parallel field, not a complete AGN selection function; no population weights or fractions are supported.

## Files and checks

Produced source-specific files:

- `data/raw/sapphires_z847_v1_member_screen.csv`: all 17 source rows, original table cells and explicit outcomes.
- `data/raw/sapphires_z847_v1_agn_candidate.csv`: one proposed candidate with measurements, missingness, caveats and eligibility.
- `data/validation/source_inputs/sapphires_z847_v1_main.tex`: exact source member, including tables and explanatory context.
- `data/validation/source_inputs/sapphires_z847_v1_extract.html`: retained table/evidence elements.
- `data/validation/source_inputs/sapphires_z847_version_history.html`: retrieved version-history element.
- `data/validation/sapphires_z847_source_manifest.json`: URLs, dates, payload/member hashes.
- `data/validation/sapphires_z847_expected_values.json`: independent Table 1/prose anchors and complete table-ID expectations.
- `data/validation/sapphires_z847_catalogue_crossmatch.csv`: 34 nearest-neighbour screens across both versions.
- `data/validation/sapphires_z847_macs0416_context_crossmatch.csv`: four Baccus sources plus Y1.

Anchors were transcribed from the TeX table/prose independently of the HTML-to-CSV screen. Checks compare ID sets, candidate values, missing mass and false inference flags, hash integrity and 34 no-close-match outcomes. The integration session must register these source-specific anchors and wire the one-row adapter; no shared registry, manifest, generated output, staging or commit is part of this extraction. The only unresolved scientific identity is the unnamed foreground contaminant. No usable BH mass is blocked on transcription; none is published in the pinned source.

## Reviewed canonical admission

Admitted 17 October 2026 at the unchanged 3 September 2026 cutoff.
Final measurement `SAPPHIRES8760_fudamoto25`, physical object `HZA-SAPPHIRES-ID-8760`, host `HZS-SAPPHIRES-ID-8760`.
Membership: **v3 context only; no numerical growth or numerical manuscript membership**. Adopted semantics: mass and both errors remain missing; foreground contaminant identity unresolved.
Each family contributes one new physical object and one preferred measurement;
model alternatives do not add measurements or objects. The source-level screen
and exclusions above remain the scientific provenance for that decision.
The three older unresolved catalogue identity groups remain excluded from
manuscript inference. Canonical values are built by
`src/internal/october2026_additions.py`, with independent source-native fixtures
registered in the complete mass/error and redshift/coordinate checks.
