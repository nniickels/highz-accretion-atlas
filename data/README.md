# Data

This folder holds catalogue tables, their source measurements, and the records
used to check them. Calculated growth rates and figures are in [results/](../results/README.md).

## Start here

- [v3 object table](processed/v3/v3_accreting_objects.csv): one preferred
  measurement per stored object, with 343 object records.
- [v3 measurement table](processed/v3/v3_accreting_measurements.csv): all 355
  literature measurements, including alternatives for the same object.

The catalogue records 342 host systems. Three identity groups remain unresolved,
so the object count is provisional. See the [identity audit](../docs/source-notes/redshift-identity-audit.md).

## Folder guide

| Folder | Contents |
| --- | --- |
| [processed/](#processed-catalogues) | Standardized measurement, object, host, observable, and subgroup tables. |
| [raw/](raw/README.md) | Original source tables and manual extractions. |
| [assembly/](#assembly-inputs) | Inputs used to combine source records and apply reviewed identity decisions. |
| [crossmatch/](#identity-links) | Links between measurements, objects, and hosts, with aliases and match reviews. |
| [validation/](validation/README.md) | Independent expected values, source locators, and conversion checks. |
| [publication/](publication/README.md) | Rules and comparison inputs for the primary and expanded samples. |
| [scenarios/](scenarios/) | Settings for the v3 growth comparisons and four-target v4 analysis. |
| [manifests/](#file-manifests) | File lists and hashes for data, results, and source records. |

## Processed catalogues

`processed/v1/`, `v2/`, and `v3/` use the same table structure. Their sizes and
scope are listed in the [main README](../README.md#dataset-versions).
Choose one version for an analysis; concatenating versions counts shared
records repeatedly.

A measurement is a record from the literature. An object groups measurements
assigned to the same accreting system. A host groups systems assigned to the
same host galaxy. Distinct objects can share a host. Observable tables retain
individual reported quantities; strata tables summarize catalogue subgroups.

Use `measurement_id`, `physical_object_id`, and `host_system_id` to join tables.
Display names can differ between sources. Retained legacy tables support
regression checks and do not define additional public versions.

## Columns, units, and missing values

The object table combines the preferred measurement with identity and history
columns. The measurement table retains alternatives. A field ending in `_std`
is the standardized value; source-native alternatives and observables retain
their published units and interpretation. Standardization does not make mass
estimators interchangeable or remove their source assumptions.

| Field or field group | Meaning and units |
| --- | --- |
| `measurement_id`, `physical_object_id`, `host_system_id` | Stable join keys for a measurement, accreting system, and host. |
| `object_id`, `published_aliases`, `available_object_ids` | Source display names and aliases; not safe cross-source join keys. |
| `catalogue_release`, `project_version` | Recorded catalogue/version labels; use the folder's public v1–v3 scope. |
| `ra_deg`, `dec_deg` | Adopted sky coordinates in degrees. Check source metadata for frame and coordinate role; a host centroid need not locate the nucleus. |
| `published_ra`, `published_dec`, `coordinate_source_*` | Original coordinate representation and its separate source/version provenance. |
| `redshift`, `redshift_err`, `redshift_kind` | Dimensionless adopted redshift, reported error, and spectroscopic/photometric type. `zphot` and `program_redshift` preserve source-specific alternatives. |
| `cosmic_time_gyr` | Cosmic age in Gyr under the baseline catalogue cosmology. The v3 minimum-seed and v4 tables calculate radiation-inclusive ages separately. |
| `log_mbh_msun_std`, `log_mstar_msun_std` | Base-10 logarithms of black-hole and host stellar masses in solar masses. |
| `log_lbol_erg_s_std` | Base-10 logarithm of bolometric luminosity in erg/s. |
| `log_mbh_mstar_ratio` | Base-10 logarithm of the black-hole/stellar-mass ratio. |
| `log_*_err_plus_std`, `log_*_err_minus_std`, legacy `log_*_err_plus`/`log_*_err_minus` | Positive upper/lower error magnitudes in dex about the corresponding logarithmic value. They can include source-defined calibration terms. |
| `log_mbh_mstar_ratio_err` | Error in the logarithmic mass ratio, in dex. |
| `mbh_msun`, `mbh_err_plus_msun`, `mbh_err_minus_msun` | Source-native linear black-hole mass and errors in solar masses. |
| `lbol_erg_s`, `lbol_err_*_erg_s`, `lbol_1e44_erg_s`, `lbol_1e44_err_*` | Linear luminosities/errors in erg/s or units of 10^44 erg/s, respectively. |
| `edd_ratio_std`, `edd_ratio_err_std`, `edd_ratio_from_mbh_lbol` | Dimensionless reported ratio/error and the independent consistency value computed from mass and luminosity. |
| `log_edd_ratio_published`, `edd_ratio_log_residual_dex`, `edd_ratio_consistency_flag` | Source log10 ratio, logarithmic consistency residual in dex, and assessment of the source triplet. These are not required growth rates. |
| `mbh_method`, `mstar_method`, `lbol_method`, `edd_ratio_method`, `*_interpretation_tag` | Estimator and interpretation metadata; consult the source and mass-method registry. |
| `log_mbh_systematic_dex`, `log_mstar_systematic_dex`, `*_systematic_kind`, `*_systematic_applied_flag` | Additional method scales in dex, their interpretation, and whether applied. A recorded scale is not automatically added to reported errors. |
| `mbh_formal_uncertainty_kind`, `mbh_statistical_uncertainty_kind` | Source-defined error semantics. The historical word `statistical` does not guarantee purely statistical errors. |
| `lensing_mu`, `lensing_mu_err`, `lensing_status`, `lensing_mass_correction_status`, `lensing_provenance` | Dimensionless magnification/error and whether/how the adopted mass was corrected. Do not demagnify a source-corrected mass again. |
| `object_class`, `spectroscopic_type`, `evidence_status`, `evidence_status_basis`, `detection_evidence`, `quality_flag` | Independent class, spectrum and evidence assessments with source-specific explanations. |
| `selection_channel`, `selection_channels`, `selection_criteria`, `phenotype_tags`, `lrd_flag`, `lrd_definition` | Selection and phenotype metadata. LRD is a phenotype, not a mass method or secure-evidence label. |
| `growth_ranking_eligible_flag`, `growth_ranking_eligibility_reason` | Whether a supported mass can enter numerical growth diagnostics and why. |
| `primary_mass_comparison_flag`, `primary_mass_comparison_reason`, `mass_comparability_group` | Method-comparability assessment; it does not alone establish primary evidence or publication membership. |
| `primary_growth_ranking_flag`, `primary_growth_ranking_reason`, `conditional_mass_flag`, `conditional_mass_reason` | Primary growth eligibility and conditional-mass interpretation. Apply the separate publication mask for manuscript use. |
| `preferred_measurement_flag`, `preferred_measurement_reason`, `match_method`, `match_reference`, `identity_resolution_status` | Assembly decisions and reasons. A resolved assembly label does not override unresolved cases in the independent identity audit. |
| `scientific_identity_status`, `scientific_identity_issue_group` | Independent audit status: `unresolved` or `no_open_issue_recorded`, with the open group where applicable. The latter is not proof of uniqueness. |
| `host_system_assignment_status`, `host_system_source_id`, `host_property_scope`, `host_fit_model`, `log_mstar_upper_limit_msun` | Host assignment, fit, scope and logarithmic mass limit. A shared host mass must not be counted once per nucleus. |
| `n_measurements`, `available_measurement_ids`, `available_source_keys`, `all_measurement_evidence_statuses`, `all_measurement_evidence_status_bases`, `object_evidence_aggregation_policy` | Object-level measurement history and aggregation policy; list fields use semicolons. |
| `source_key`, `source_table`, `source_paper_version`, `source_url`, `source_doi`, `source_archive_url`, `source_archive_sha256`, `extraction_date`, `extraction_date_status` | Source identifiers, locations, exact versions, payload hashes and date completeness. |
| `survey`, `program`, `field`, `thrils_id`, `ceers_photometry_id`, `notes`, `source_caveat_tags` | Survey context, source-specific identifiers and caveats. |
| `halpha_flux_*_1e18_erg_s_cm2`, `halpha_broad_flux_dustcorr_1e18` and flux error companions | Halpha fluxes in 10^-18 erg/s/cm². Total, narrow, broad and dust-corrected quantities are distinct. |
| `halpha_lum_*_1e42`, `halpha_lum_*_erg_s` and luminosity error companions | Halpha luminosities in 10^42 erg/s or erg/s, as named. |
| `halpha_*fwhm*`, `halpha_broad_to_total_ratio`, `halpha_broad_to_narrow_ratio` and error companions | Line widths/errors in km/s and dimensionless component ratios/errors. Instrument correction is recorded separately. |
| `halpha_ew_rest_angstrom`, `halpha_ew_err_*` | Rest-frame equivalent width/errors in Å. |
| `photometry_band`, `photometry_mag`, `photometry_mag_err_*`, `f200w_mag`, `f200w_err_*`, `muv`, `muv_err_*`, `delta_m_lw` | Published photometric band, magnitudes/errors, UV absolute magnitude, and source-defined long-wavelength colour. Consult source photometry conventions. |
| `beta_uv`, `beta_opt` and error companions | Dimensionless source continuum slopes. |
| `metallicity_12_logoh`, `metallicity_err_*`, `ebv_mag`, `av_mag` | Published 12+log10(O/H), its quoted errors, colour excess E(B−V), and extinction A_V in magnitudes. |
| `broad_line_species`, `fwhm_instrument_corrected_flag`, `dust_correction_applied_flag`, `halpha_absorption_fit_flag`, `halpha_broad_snr`, `delta_aic` | Line identity, correction/fit status, dimensionless signal-to-noise and fit-comparison statistic. |
| `agn_contam_flag`, `red_agn_flag`, `compact_source_flag`, `dual_agn_candidate_flag`, `robust_candidate_flag`, `oiii_outflow_detected_flag`, `halpha_three_component_fit_flag` | Source-specific interpretation/fit flags; absent values do not establish a negative result. |
| `missing_mstar_flag`, `missing_lbol_flag`, `missing_edd_ratio_flag`, `missing_lensing_flag`, `missing_optional_fields` | Explicit missingness metadata; consult the corresponding value and source. |

Blank numeric cells are missing, never zero. Processed boolean flags use
`True`/`False` or a blank for unknown; `quality_flag` and
`edd_ratio_consistency_flag` are categorical labels. Raw inputs retain legacy
0/1 representations. Do not use `astype(bool)` on string columns. Text tokens
such as `not_reported`, `not_applicable`, and `not_recorded_in_frozen_v1_source_layer`
describe different provenance states. Missing mass errors imply no uncertainty
probability, not a perfectly known mass.

Preferred-measurement reasons describe the alternatives retained in each version.
Source extraction inputs preserve the original selection reasons.

Ratio consistency is assessed wherever finite mass, luminosity, and a positive
reported Eddington ratio exist, using a 0.3-dex tolerance. Other rows are marked
`not_evaluable`. These diagnostics do not alter required growth rates.
The original JADES rows use the registry's verified v2 archive link and hash;
their original extraction date remains explicitly unknown.

For a log mass L with lower/upper errors d−/d+, the linear interval is
[10^(L−d−), 10^(L+d+)] solar masses. Error magnitudes in dex are not logarithms
of linear error bars. Limits and contextual proxy estimates remain distinct
from eligible canonical point masses.

The long-form `v3_source_observables.csv` uses `observable_name`, `value`,
`err_plus`, `err_minus`, `censoring`, `unit`, `uncertainty_kind` and
`source_location`, linked by `measurement_id`. Read its explicit `unit` and
`censoring` columns before combining quantities from different sources.

## Example: select the manuscript sample

From the repository root, using the pinned environment:

```python
import pandas as pd

objects = pd.read_csv("data/processed/v3/v3_accreting_objects.csv")
selection = pd.read_csv("results/v3/selected_samples/tables/publication_object_selection.csv")
joined = objects.merge(selection[["physical_object_id", "publication_primary_flag"]],
                       on="physical_object_id", validate="one_to_one")
primary = joined.loc[joined["publication_primary_flag"].eq(True)]
print(primary[["physical_object_id", "redshift", "log_mbh_msun_std"]].head())
```

This uses the reviewed [publication mask](publication/README.md#sample-selection).
For a different analysis, choose and document the appropriate evidence, identity
and method criteria using the [schema guide](../docs/reference/catalogue-schema.md).

## Assembly inputs

`assembly/blagn_foundation_measurements.csv` holds the corrected broad-line
AGN measurements used before Ren and the v3 expansion sources are added.
Here AGN means active galactic nucleus. Files ending in
`_identity_overrides.csv` record reviewed decisions about source matches;
other assembly inputs record reconciled duplicate pairs.

These files are fixed inputs to the catalogue builder. Generated tables go to
`processed/` and `crossmatch/`. The [versioning guide](../docs/guides/versioning.md)
defines which source types enter each version.

## Identity links

`crossmatch/v1/`, `v2/`, and `v3/` contain measurement-to-object and object-to-host
links, aliases, and match reviews. Use these links to inspect how records were
grouped. Historical filenames in retained review inputs do not identify new
catalogue versions. Open identity questions are documented in the identity audit.

## File manifests

`manifests/v1-dataset-manifest.json`, `v2-dataset-manifest.json`, and
`v3-dataset-manifest.json` list the generated files and their SHA-256 checksums.
Each includes shared plots referenced from earlier versions.
`source-provenance-manifest.json` records source and validation files.
The v3 manifest also checks code, settings, and sample-rule hashes for the
[extended result tables](../docs/reference/catalogue-results.md).
Checksums detect file changes; they do not establish scientific correctness.

The [reproduction guide](../docs/guides/reproducibility.md) gives verification
commands for checking files and reproducing results.
Publication results are compared separately against an independent baseline.

## Registries and review records

| File | Purpose |
| --- | --- |
| [sources.md](sources.md) | Source bibliography, extraction methods, and limitations. |
| [source_provenance_registry.csv](source_provenance_registry.csv) | Publication versions, source locations, archive hashes, and verification dates. |
| [source_family_registry.csv](source_family_registry.csv) | How each study or related survey group enters the catalogue. |
| [mass_method_registry.csv](mass_method_registry.csv) | Mass estimators, calibration references, and method uncertainties. |
| [selection_function_registry.csv](selection_function_registry.csv) | Survey selection, completeness information, and limits on population inference. |
| [manual_extraction_audit.csv](manual_extraction_audit.csv) | Extracted-file hashes, row counts, source locations, and remaining checks. |
| [poster_inputs.json](poster_inputs.json) | Reviewed scientific inputs for poster figures and claims. |
| [poster_exports.json](poster_exports.json) | Reviewed PowerPoint/PDF pairs and their hashes. |

See [setup](../README.md#getting-started) before running the workflows.

## Reporting data errors

Report a suspected error with the object or measurement ID, affected field,
source DOI and version, table or passage, and published value. Distinguish
measurements, limits, and missing values.
