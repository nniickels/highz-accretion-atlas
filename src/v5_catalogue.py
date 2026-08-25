"""Build the non-breaking v5 BLAGN measurement-version release."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from src.identity import (
    apply_reviewed_identity_overrides, candidate_matches, require_unambiguous_candidates,
    stable_object_id,
)
from src.object_taxonomy import TAXONOMY_FIELDS, add_blagn_taxonomy, validate_taxonomy
from src.standardize_data import CANONICAL_RAW_FIELDS, standardize_dataframe


CATALOGUE_RELEASE = "v5-blagn"
HARIKANE_SOURCE_KEY = "harikane23_nirspec_blagn"
HARIKANE_MASS_METHOD = "single-epoch-virial-halpha-greeneho2005"
HARIKANE_PAPER_VERSION = "The Astrophysical Journal 959:39 (2023); arXiv:2303.11946v3"
HARIKANE_ARCHIVE_SHA256 = "02c2951b4594234f8cc015fc811f1ed438d35997249138af4d756d02d44ca4b4"

NATIVE_NUMERIC_FIELDS = [
    "ra_deg", "dec_deg", "redshift", "muv", "muv_err_plus", "muv_err_minus",
    "metallicity_12_logoh", "metallicity_err_plus", "metallicity_err_minus", "ebv_mag",
    "halpha_broad_snr", "delta_aic", "halpha_lum_broad_erg_s",
    "halpha_lum_broad_err_plus", "halpha_lum_broad_err_minus",
    "halpha_broad_to_narrow_ratio", "halpha_broad_to_narrow_err_plus",
    "halpha_broad_to_narrow_err_minus", "halpha_broad_fwhm_km_s",
    "halpha_broad_fwhm_err_plus", "halpha_broad_fwhm_err_minus",
    "mbh_msun", "mbh_err_plus_msun", "mbh_err_minus_msun",
    "log_mbh_msun", "log_mbh_err_plus", "log_mbh_err_minus",
    "lbol_erg_s", "lbol_err_plus_erg_s", "lbol_err_minus_erg_s",
    "log_lbol_erg_s", "log_lbol_err_plus", "log_lbol_err_minus",
    "edd_ratio_reported", "edd_ratio_err_plus", "edd_ratio_err_minus",
    "log_mstar_msun", "log_mstar_err_plus", "log_mstar_err_minus",
    "log_mstar_upper_limit_msun", "red_agn_flag", "compact_source_flag",
    "dual_agn_candidate_flag", "lrd_flag",
]

HARIKANE_EXTRA_FIELDS = [
    "published_ra", "published_dec", "field", "program", "muv", "muv_err_plus",
    "muv_err_minus", "metallicity_12_logoh", "metallicity_err_plus",
    "metallicity_err_minus", "ebv_mag", "halpha_broad_snr", "delta_aic",
    "halpha_lum_broad_erg_s", "halpha_lum_broad_err_plus",
    "halpha_lum_broad_err_minus", "halpha_broad_to_narrow_ratio",
    "halpha_broad_to_narrow_err_plus", "halpha_broad_to_narrow_err_minus",
    "halpha_broad_fwhm_km_s", "halpha_broad_fwhm_err_plus",
    "halpha_broad_fwhm_err_minus", "mbh_msun", "mbh_err_plus_msun",
    "mbh_err_minus_msun", "lbol_erg_s", "lbol_err_plus_erg_s",
    "lbol_err_minus_erg_s", "log_mstar_upper_limit_msun", "host_fit_model",
    "red_agn_flag", "compact_source_flag", "dual_agn_candidate_flag", "lrd_flag",
    "source_caveat_tags", "selection_channel", "broad_line_species",
    "log_mbh_systematic_dex", "mbh_systematic_kind", "mbh_systematic_applied_flag",
    "mbh_formal_uncertainty_kind", "dust_correction_applied_flag",
    "source_paper_version", "source_url", "source_doi", "source_archive_url",
    "source_archive_sha256", "extraction_date", "selection_criteria",
    "log_mstar_systematic_dex", "mstar_systematic_kind",
    "mstar_systematic_applied_flag",
]

EVIDENCE_STATUS_PRIORITY = {
    "secure_accreting_mbh": 0,
    "probable_accreting_mbh": 1,
    "candidate_accreting_mbh": 2,
    "disputed_accreting_mbh": 3,
}


def _require_columns(frame: pd.DataFrame, fields: Iterable[str], label: str) -> None:
    if missing := sorted(set(fields) - set(frame.columns)):
        raise ValueError(f"{label} missing columns: {missing}")


def validate_harikane_raw(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate all ten authoritative final-sample rows and transformations."""
    required = {
        "measurement_id", "object_id", "published_ra", "published_dec", "field",
        "survey", "program", "host_fit_model", "source_caveat_tags", *NATIVE_NUMERIC_FIELDS,
    }
    _require_columns(raw, required, "Harikane raw table")
    if len(raw) != 10 or not raw["measurement_id"].is_unique:
        raise ValueError("Harikane final sample must contain 10 unique measurement rows")
    result = raw.copy()
    for field in NATIVE_NUMERIC_FIELDS:
        result[field] = pd.to_numeric(result[field], errors="coerce")
    required_numeric = [
        "ra_deg", "dec_deg", "redshift", "halpha_broad_snr", "delta_aic",
        "halpha_lum_broad_erg_s", "halpha_broad_fwhm_km_s", "mbh_msun",
        "log_mbh_msun", "lbol_erg_s", "log_lbol_erg_s", "edd_ratio_reported",
    ]
    if result[required_numeric].isna().any().any():
        raise ValueError("Harikane published final-sample numeric fields cannot be missing")
    if not result["redshift"].between(4.015, 6.936).all():
        raise ValueError("Harikane redshift range must be 4.015--6.936")
    if not result["halpha_broad_snr"].gt(5).all() or not result["delta_aic"].gt(20).all():
        raise ValueError("Harikane rows must satisfy the published S/N and Delta-AIC cuts")
    if not result["halpha_broad_fwhm_km_s"].gt(1000).all():
        raise ValueError("Harikane rows must satisfy broad Halpha FWHM >1000 km/s")
    if not np.allclose(result["log_mbh_msun"], np.log10(result["mbh_msun"]), atol=5e-8):
        raise ValueError("Harikane log MBH transformation disagrees with the published linear value")
    if not np.allclose(result["log_lbol_erg_s"], np.log10(result["lbol_erg_s"]), atol=5e-8):
        raise ValueError("Harikane log Lbol transformation disagrees with the published linear value")
    if int(result["log_mstar_msun"].notna().sum()) != 6 or int(result["log_mstar_upper_limit_msun"].notna().sum()) != 4:
        raise ValueError("Harikane host table must retain six measurements and four upper limits")
    if result.loc[result["log_mstar_upper_limit_msun"].notna(), "log_mstar_msun"].notna().any():
        raise ValueError("Host upper limits must not populate the canonical Mstar measurement")
    for field in ["red_agn_flag", "compact_source_flag", "dual_agn_candidate_flag"]:
        if not result[field].dropna().isin([0, 1]).all():
            raise ValueError(f"{field} must contain only 0/1")
    if result["lrd_flag"].notna().any():
        raise ValueError("Harikane does not publish an object-level LRD marker")
    anchors = result.set_index("object_id")
    if not np.isclose(anchors.loc["CEERS-02782", "mbh_msun"], 4.2e7):
        raise ValueError("Harikane CEERS-02782 MBH anchor mismatch")
    if not np.isclose(anchors.loc["CEERS-00717", "halpha_broad_fwhm_km_s"], 6279):
        raise ValueError("Harikane CEERS-00717 FWHM anchor mismatch")
    return result


def standardize_harikane(raw: pd.DataFrame) -> pd.DataFrame:
    validated = validate_harikane_raw(raw)
    canonical = pd.DataFrame(index=validated.index, columns=CANONICAL_RAW_FIELDS)
    for field in [
        "measurement_id", "object_id", "ra_deg", "dec_deg", "redshift", "survey",
        "log_mbh_msun", "log_mbh_err_plus", "log_mbh_err_minus",
        "log_mstar_msun", "log_mstar_err_plus", "log_mstar_err_minus",
        "log_lbol_erg_s", "log_lbol_err_plus", "log_lbol_err_minus",
        "edd_ratio_reported", "edd_ratio_err_plus", "edd_ratio_err_minus",
    ]:
        canonical[field] = validated[field]
    canonical["redshift_kind"] = "spec"
    canonical["object_class"] = "broad-line-agn"
    canonical["mbh_method"] = HARIKANE_MASS_METHOD
    canonical["detection_evidence"] = "individual_robust"
    canonical["mstar_method"] = np.where(
        canonical["log_mstar_msun"].notna(), "prospector-after-agn-host-image-decomposition", "",
    )
    canonical["lbol_method"] = "halpha-multicalibration-best-estimate-harikane2023"
    canonical["agn_contam_flag"] = 1
    canonical["source_key"] = HARIKANE_SOURCE_KEY
    canonical["source_table"] = "Tables 1-3"
    canonical["notes"] = "Extinction-corrected broad-Halpha Greene & Ho (2005) mass; source gives no numeric virial-calibration systematic."
    standardized = standardize_dataframe(
        canonical, project_version="v5", mbh_tag=HARIKANE_MASS_METHOD,
        lbol_tag="halpha-multicalibration-best-estimate-harikane2023", min_redshift=4.0,
    )
    extras = validated.copy()
    extras["selection_channel"] = "broad-halpha"
    extras["broad_line_species"] = "Halpha"
    extras["log_mbh_systematic_dex"] = np.nan
    extras["mbh_systematic_kind"] = "not numerically specified by Harikane et al. (2023)"
    extras["mbh_systematic_applied_flag"] = False
    extras["mbh_formal_uncertainty_kind"] = "log transform of published asymmetric linear MBH errors"
    extras["dust_correction_applied_flag"] = True
    extras["source_paper_version"] = HARIKANE_PAPER_VERSION
    extras["source_url"] = "https://doi.org/10.3847/1538-4357/ad029e"
    extras["source_doi"] = "10.3847/1538-4357/ad029e"
    extras["source_archive_url"] = "https://arxiv.org/e-print/2303.11946v3"
    extras["source_archive_sha256"] = HARIKANE_ARCHIVE_SHA256
    extras["extraction_date"] = "2026-08-23"
    extras["selection_criteria"] = "NIRSpec parent sample at zspec 3.8-8.9; permitted broad Halpha FWHM >1000 km/s and S/N >5; narrow forbidden lines; outflow-component veto; final rows have Delta AIC >20"
    extras["log_mstar_systematic_dex"] = 0.2
    extras["mstar_systematic_kind"] = "typical systematic from fixed SED-fitting prior; Harikane et al. (2023) Section 4.3"
    extras["mstar_systematic_applied_flag"] = False
    return standardized.merge(
        extras[["measurement_id", *HARIKANE_EXTRA_FIELDS]], on="measurement_id", validate="one_to_one",
    )


def build_v5_catalogues(
    v4_measurements: pd.DataFrame,
    harikane_raw: pd.DataFrame,
    identity_overrides: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return v5 measurements, objects, links, aliases, and reviewed candidates."""
    inherited_link_columns = [
        "measurement_id", "physical_object_id", "preferred_measurement_flag",
        "preferred_measurement_reason", "match_method", "match_reference",
    ]
    _require_columns(v4_measurements, inherited_link_columns, "v4 measurements")
    new = standardize_harikane(harikane_raw)
    candidates = candidate_matches(new, v4_measurements)
    require_unambiguous_candidates(candidates, new["measurement_id"])
    candidates, accepted_map = apply_reviewed_identity_overrides(
        candidates, identity_overrides,
        known_measurement_ids=pd.concat([v4_measurements["measurement_id"], new["measurement_id"]]),
    )
    expected_overlaps = {
        "CEERS01244_harikane23": "HZA-CEERS-1244", "CEERS00746_harikane23": "HZA-CEERS-746",
        "CEERS00672_harikane23": "HZA-CEERS-672", "CEERS02782_harikane23": "HZA-CEERS-2782",
        "CEERS00397_harikane23": "HZA-CEERS-397",
    }
    if len(candidates) != 6 or any(accepted_map.get(key) != value for key, value in expected_overlaps.items()):
        raise ValueError("Harikane reviewed overlap set does not match the five verified physical objects")

    inherited = v4_measurements[inherited_link_columns].copy()
    reserved = set(inherited["physical_object_id"].astype(str))
    link_rows = []
    for _, row in new.iterrows():
        measurement_id = str(row["measurement_id"])
        if measurement_id in accepted_map:
            physical_id = accepted_map[measurement_id]
            preferred = False
            reason = "prior-release preferred measurement retained for longitudinal reproducibility"
            method = "coordinate-redshift match; manually reviewed"
            reference = "0.5 arcsec and delta-z 0.01 candidate thresholds"
        else:
            physical_id = stable_object_id(
                str(row["object_id"]), source_key=HARIKANE_SOURCE_KEY, reserved_ids=reserved,
            )
            reserved.add(physical_id)
            preferred = True
            reason = "only catalogue measurement in this release"
            method = "singleton assignment after coordinate-redshift search"
            reference = "no candidate within 0.5 arcsec and delta-z 0.01"
        link_rows.append({
            "measurement_id": measurement_id, "physical_object_id": physical_id,
            "preferred_measurement_flag": preferred, "preferred_measurement_reason": reason,
            "match_method": method, "match_reference": reference,
        })
    links = pd.concat([inherited, pd.DataFrame(link_rows)], ignore_index=True)

    release_columns = list(dict.fromkeys([*v4_measurements.columns, *new.columns]))
    measurements = pd.DataFrame.from_records([
        *v4_measurements.reindex(columns=release_columns).to_dict("records"),
        *new.reindex(columns=release_columns).to_dict("records"),
    ], columns=release_columns)
    measurements = measurements.drop(
        columns=[column for column in inherited_link_columns[1:] if column in measurements], errors="ignore",
    ).merge(links, on="measurement_id", validate="one_to_one")
    measurements["catalogue_release"] = CATALOGUE_RELEASE
    measurements = add_blagn_taxonomy(measurements)
    preferred_counts = measurements.groupby("physical_object_id")["preferred_measurement_flag"].sum()
    if len(measurements) != 106 or measurements["physical_object_id"].nunique() != 99 or not preferred_counts.eq(1).all():
        raise ValueError("v5 must contain 106 measurements, 99 objects, and one default per object")

    grouped = measurements.groupby("physical_object_id", sort=False)
    aggregates = grouped.agg(
        n_measurements=("measurement_id", "size"),
        available_measurement_ids=("measurement_id", lambda values: ";".join(values.astype(str))),
        available_object_ids=("object_id", lambda values: ";".join(values.astype(str))),
        lrd_reported_by_any_measurement=("lrd_flag", lambda values: any(pd.notna(v) and bool(v) for v in values)),
        lrd_designation_reported_by_any_measurement=("lrd_flag", lambda values: values.notna().any()),
    ).reset_index()
    lrd_rows = measurements[measurements["lrd_flag"].fillna(False).astype(bool)]
    lrd_ids = lrd_rows.groupby("physical_object_id")["measurement_id"].agg(lambda values: ";".join(values.astype(str)))
    lrd_sources = lrd_rows.groupby("physical_object_id")["source_key"].agg(lambda values: ";".join(dict.fromkeys(values.astype(str))))
    aggregates["lrd_evidence_measurement_ids"] = aggregates["physical_object_id"].map(lrd_ids)
    aggregates["lrd_evidence_source_keys"] = aggregates["physical_object_id"].map(lrd_sources)
    phenotype_rows = measurements[
        measurements["phenotype_tags"].fillna("").astype(str).str.strip().ne("")
    ]
    phenotype_ids = phenotype_rows.groupby("physical_object_id")["measurement_id"].agg(
        lambda values: ";".join(values.astype(str))
    )
    phenotype_sources = phenotype_rows.groupby("physical_object_id")["source_key"].agg(
        lambda values: ";".join(dict.fromkeys(values.astype(str)))
    )
    phenotype_union = grouped["phenotype_tags"].agg(
        lambda values: ";".join(dict.fromkeys(
            tag
            for value in values.dropna().astype(str)
            for tag in value.split(";")
            if tag
        ))
    )
    aggregates["phenotype_evidence_measurement_ids"] = aggregates["physical_object_id"].map(phenotype_ids)
    aggregates["phenotype_evidence_source_keys"] = aggregates["physical_object_id"].map(phenotype_sources)
    aggregates["all_measurements_phenotype_tags"] = aggregates["physical_object_id"].map(phenotype_union)
    evidence_priority = measurements["evidence_status"].map(EVIDENCE_STATUS_PRIORITY)
    worst_priority = evidence_priority.groupby(measurements["physical_object_id"]).max()
    worst_status = worst_priority.map({value: key for key, value in EVIDENCE_STATUS_PRIORITY.items()})
    evidence_rows = measurements[
        evidence_priority.eq(measurements["physical_object_id"].map(worst_priority))
    ]
    evidence_ids = evidence_rows.groupby("physical_object_id")["measurement_id"].agg(
        lambda values: ";".join(values.astype(str))
    )
    evidence_sources = evidence_rows.groupby("physical_object_id")["source_key"].agg(
        lambda values: ";".join(dict.fromkeys(values.astype(str)))
    )
    evidence_bases = evidence_rows.groupby("physical_object_id")["evidence_status_basis"].agg(
        lambda values: ";".join(dict.fromkeys(values.astype(str)))
    )
    aggregates["all_measurements_evidence_status"] = aggregates["physical_object_id"].map(worst_status)
    aggregates["evidence_status_measurement_ids"] = aggregates["physical_object_id"].map(evidence_ids)
    aggregates["evidence_status_source_keys"] = aggregates["physical_object_id"].map(evidence_sources)
    aggregates["all_measurements_evidence_status_basis"] = aggregates["physical_object_id"].map(evidence_bases)
    objects = measurements[measurements["preferred_measurement_flag"]].copy()
    objects["preferred_measurement_lrd_flag"] = objects["lrd_flag"]
    objects["preferred_measurement_phenotype_tags"] = objects["phenotype_tags"]
    objects["preferred_measurement_evidence_status"] = objects["evidence_status"]
    objects["preferred_measurement_evidence_status_basis"] = objects["evidence_status_basis"]
    objects = objects.merge(aggregates, on="physical_object_id", validate="one_to_one")
    objects["lrd_flag"] = objects.apply(
        lambda row: (
            bool(row["lrd_reported_by_any_measurement"])
            if bool(row["lrd_designation_reported_by_any_measurement"])
            else np.nan
        ),
        axis=1,
    )
    objects["phenotype_tags"] = objects["all_measurements_phenotype_tags"].fillna("")
    objects["evidence_status"] = objects["all_measurements_evidence_status"]
    objects["evidence_status_basis"] = objects["all_measurements_evidence_status_basis"]
    objects["growth_ranking_eligible_flag"] = (
        pd.to_numeric(objects["log_mbh_msun_std"], errors="coerce").notna()
        & ~objects["evidence_status"].eq("disputed_accreting_mbh")
    )
    objects["primary_growth_ranking_flag"] = (
        objects["growth_ranking_eligible_flag"]
        & objects["evidence_status"].isin({"secure_accreting_mbh", "probable_accreting_mbh"})
    )
    validate_taxonomy(objects)

    aliases = measurements[[
        "physical_object_id", "measurement_id", "object_id", "source_key", "ra_deg", "dec_deg", "redshift",
    ]].copy()
    aliases["alias_kind"] = "source_object_id"
    aliases["catalogue_release"] = CATALOGUE_RELEASE
    front = ["catalogue_release", "physical_object_id", "measurement_id", "object_id"]
    measurements = measurements[front + [column for column in measurements if column not in front]]
    object_meta = ["n_measurements", "available_measurement_ids", "available_object_ids"]
    objects = objects[front + object_meta + [column for column in objects if column not in front + object_meta]]
    return (
        measurements.sort_values(["source_key", "redshift", "measurement_id"], ascending=[True, False, True]).reset_index(drop=True),
        objects.sort_values(["source_key", "redshift", "physical_object_id"], ascending=[True, False, True]).reset_index(drop=True),
        links.sort_values("measurement_id").reset_index(drop=True),
        aliases.sort_values(["physical_object_id", "measurement_id"]).reset_index(drop=True),
        candidates.sort_values(["measurement_id", "candidate_measurement_id"]).reset_index(drop=True),
    )
