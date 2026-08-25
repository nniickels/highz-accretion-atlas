"""Build the non-breaking v6 THRILS broad-line-AGN release."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from src.identity import CANDIDATE_COLUMNS, candidate_matches, stable_object_id
from src.object_taxonomy import add_blagn_taxonomy, validate_taxonomy
from src.standardize_data import CANONICAL_RAW_FIELDS, standardize_dataframe
from src.v5_catalogue import EVIDENCE_STATUS_PRIORITY


CATALOGUE_RELEASE = "v6-blagn"
THRILS_SOURCE_KEY = "davis26_thrils_blagn"
THRILS_MASS_METHOD = "single-epoch-virial-halpha-reinesvolonteri2015"
THRILS_PAPER_VERSION = "arXiv:2602.23310v1 (submitted to ApJ; 2026-02-26)"
THRILS_ARCHIVE_SHA256 = "13274268d718138119dbbb818d58e3f5255ce0a34f80f9d8a7a0d0013f16153b"
THRILS_PROGRAM_VERSION = "arXiv:2512.12509v1 (2025-12-14)"
THRILS_PROGRAM_ARCHIVE_SHA256 = "584a56f5867e816c6220ea52f55fc0411f2fc745544ecccfb6ea4ad42c445fdc"

NUMERIC_FIELDS = [
    "thrils_id", "ceers_photometry_id", "ra_deg", "dec_deg", "redshift",
    "program_redshift", "zphot", "halpha_flux_broad_1e20_erg_s_cm2",
    "halpha_flux_broad_err_1e20", "halpha_flux_narrow_1e19_erg_s_cm2",
    "halpha_flux_narrow_err_1e19", "halpha_broad_fwhm_km_s",
    "halpha_broad_fwhm_err", "log_mbh_msun", "log_mbh_err", "lrd_flag",
]

THRILS_EXTRA_FIELDS = [
    "thrils_id", "ceers_photometry_id", "program_redshift", "zphot", "program",
    "field", "selection_channel", "broad_line_species",
    "halpha_flux_broad_1e18_erg_s_cm2", "halpha_flux_broad_err_plus",
    "halpha_flux_broad_err_minus", "halpha_flux_narrow_1e18_erg_s_cm2",
    "halpha_flux_narrow_err_plus", "halpha_flux_narrow_err_minus",
    "halpha_broad_fwhm_km_s", "halpha_broad_fwhm_err_plus",
    "halpha_broad_fwhm_err_minus", "fwhm_instrument_corrected_flag", "lrd_flag",
    "lrd_definition", "halpha_absorption_fit_flag", "log_mbh_systematic_dex",
    "mbh_systematic_kind", "mbh_systematic_applied_flag",
    "mbh_formal_uncertainty_kind", "dust_correction_applied_flag",
    "source_caveat_tags", "source_paper_version", "source_url", "source_doi",
    "source_archive_url", "source_archive_sha256", "coordinate_source_table",
    "coordinate_source_paper_version", "coordinate_source_url",
    "coordinate_source_archive_url", "coordinate_source_archive_sha256",
    "extraction_date", "selection_criteria",
]


def _require_columns(frame: pd.DataFrame, fields: Iterable[str], label: str) -> None:
    if missing := sorted(set(fields) - set(frame.columns)):
        raise ValueError(f"{label} missing columns: {missing}")


def validate_thrils_raw(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate the seven authoritative Davis et al. Appendix Table 5 rows."""
    required = {
        "measurement_id", "object_id", "survey", "program", "field",
        "source_caveat_tags", *NUMERIC_FIELDS,
    }
    _require_columns(raw, required, "THRILS raw table")
    if len(raw) != 7 or not raw["measurement_id"].is_unique:
        raise ValueError("Davis et al. Table 5 must contain seven unique measurements")
    result = raw.copy()
    for field in NUMERIC_FIELDS:
        original = result[field]
        result[field] = pd.to_numeric(original, errors="coerce")
        invalid = result[field].isna() & original.notna() & original.astype(str).str.strip().ne("")
        if invalid.any():
            raise ValueError(f"THRILS field {field} contains nonnumeric published values")
    required_numeric = [
        "thrils_id", "ceers_photometry_id", "ra_deg", "dec_deg", "redshift",
        "program_redshift", "zphot", "halpha_flux_broad_1e20_erg_s_cm2",
        "halpha_flux_broad_err_1e20", "halpha_flux_narrow_1e19_erg_s_cm2",
        "halpha_flux_narrow_err_1e19", "log_mbh_msun", "log_mbh_err",
    ]
    if result[required_numeric].isna().any().any():
        raise ValueError("THRILS published Table 5 and coordinate-join values cannot be missing")
    if set(result["thrils_id"].astype(int)) != {49400, 101567, 25501, 40467, 44774, 46155, 24975}:
        raise ValueError("THRILS Table 5 ID set mismatch")
    if int(result["redshift"].ge(4.0).sum()) != 6:
        raise ValueError("THRILS Table 5 must retain six rows at z >= 4")
    if result["lrd_flag"].notna().any():
        raise ValueError("Davis et al. Table 5 does not publish row-level LRD markers")
    fwhm = result[result["halpha_broad_fwhm_km_s"].notna()]
    if len(fwhm) != 1 or int(fwhm.iloc[0]["thrils_id"]) != 40467:
        raise ValueError("Only THRILS 40467 has a source-text FWHM measurement")
    if not np.isclose(fwhm.iloc[0]["halpha_broad_fwhm_km_s"], 1696):
        raise ValueError("THRILS 40467 FWHM anchor mismatch")
    anchor = result.set_index("thrils_id").loc[101567]
    if not np.isclose(anchor["log_mbh_msun"], 6.55) or not np.isclose(anchor["log_mbh_err"], 0.17):
        raise ValueError("THRILS 101567 mass anchor mismatch")
    return result


def standardize_thrils(raw: pd.DataFrame) -> pd.DataFrame:
    validated = validate_thrils_raw(raw)
    canonical = pd.DataFrame(index=validated.index, columns=CANONICAL_RAW_FIELDS)
    for field in ["measurement_id", "object_id", "ra_deg", "dec_deg", "redshift", "survey"]:
        canonical[field] = validated[field]
    canonical["redshift_kind"] = "spec"
    canonical["object_class"] = "broad-line-agn"
    canonical["log_mbh_msun"] = validated["log_mbh_msun"]
    canonical["log_mbh_err_plus"] = validated["log_mbh_err"]
    canonical["log_mbh_err_minus"] = validated["log_mbh_err"]
    canonical["mbh_method"] = THRILS_MASS_METHOD
    canonical["detection_evidence"] = "individual_robust"
    canonical["agn_contam_flag"] = 1
    canonical["source_key"] = THRILS_SOURCE_KEY
    canonical["source_table"] = "Appendix Table 5; coordinates from Hutchison et al. Table 3"
    canonical["notes"] = (
        "Deep G395M broad-Halpha detection; formal mass errors exclude the stated "
        "approximately 0.5 dex single-epoch systematic."
    )
    standardized = standardize_dataframe(
        canonical, project_version="v6", mbh_tag=THRILS_MASS_METHOD,
        lbol_tag="unavailable", min_redshift=4.0,
    )

    extras = validated.copy()
    extras["selection_channel"] = "photometric-eelg-parent;deep-g395m-broad-halpha"
    extras["broad_line_species"] = "Halpha"
    extras["halpha_flux_broad_1e18_erg_s_cm2"] = extras["halpha_flux_broad_1e20_erg_s_cm2"] * 0.01
    extras["halpha_flux_broad_err_plus"] = extras["halpha_flux_broad_err_1e20"] * 0.01
    extras["halpha_flux_broad_err_minus"] = extras["halpha_flux_broad_err_1e20"] * 0.01
    extras["halpha_flux_narrow_1e18_erg_s_cm2"] = extras["halpha_flux_narrow_1e19_erg_s_cm2"] * 0.1
    extras["halpha_flux_narrow_err_plus"] = extras["halpha_flux_narrow_err_1e19"] * 0.1
    extras["halpha_flux_narrow_err_minus"] = extras["halpha_flux_narrow_err_1e19"] * 0.1
    extras["halpha_broad_fwhm_err_plus"] = extras["halpha_broad_fwhm_err"]
    extras["halpha_broad_fwhm_err_minus"] = extras["halpha_broad_fwhm_err"]
    extras["fwhm_instrument_corrected_flag"] = np.nan
    extras["lrd_definition"] = "not reported per Table 5 row"
    extras["halpha_absorption_fit_flag"] = np.nan
    extras["log_mbh_systematic_dex"] = 0.5
    extras["mbh_systematic_kind"] = "intrinsic scatter in single-epoch black-hole mass recipes"
    extras["mbh_systematic_applied_flag"] = False
    extras["mbh_formal_uncertainty_kind"] = "observational posterior uncertainty from broad-Halpha flux and FWHM fit"
    extras["dust_correction_applied_flag"] = np.nan
    extras["source_paper_version"] = THRILS_PAPER_VERSION
    extras["source_url"] = "https://arxiv.org/abs/2602.23310v1"
    extras["source_doi"] = "10.48550/arXiv.2602.23310"
    extras["source_archive_url"] = "https://arxiv.org/e-print/2602.23310v1"
    extras["source_archive_sha256"] = THRILS_ARCHIVE_SHA256
    extras["coordinate_source_table"] = "Hutchison et al. THRILS survey redshift catalogue Table 3"
    extras["coordinate_source_paper_version"] = THRILS_PROGRAM_VERSION
    extras["coordinate_source_url"] = "https://arxiv.org/abs/2512.12509v1"
    extras["coordinate_source_archive_url"] = "https://arxiv.org/e-print/2512.12509v1"
    extras["coordinate_source_archive_sha256"] = THRILS_PROGRAM_ARCHIVE_SHA256
    extras["extraction_date"] = "2026-08-25"
    extras["selection_criteria"] = (
        "photometric EELG parent sample; deep 8.36-8.85 hr NIRSpec G395M; "
        "broad component >3 sigma and implied FWHM >1000 km/s"
    )
    return standardized.merge(
        extras[["measurement_id", *THRILS_EXTRA_FIELDS]],
        on="measurement_id", validate="one_to_one",
    )


def _aggregate_objects(measurements: pd.DataFrame) -> pd.DataFrame:
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
    phenotype_rows = measurements[measurements["phenotype_tags"].fillna("").astype(str).str.strip().ne("")]
    phenotype_ids = phenotype_rows.groupby("physical_object_id")["measurement_id"].agg(lambda values: ";".join(values.astype(str)))
    phenotype_sources = phenotype_rows.groupby("physical_object_id")["source_key"].agg(lambda values: ";".join(dict.fromkeys(values.astype(str))))
    phenotype_union = grouped["phenotype_tags"].agg(
        lambda values: ";".join(dict.fromkeys(
            tag for value in values.dropna().astype(str) for tag in value.split(";") if tag
        ))
    )
    aggregates["phenotype_evidence_measurement_ids"] = aggregates["physical_object_id"].map(phenotype_ids)
    aggregates["phenotype_evidence_source_keys"] = aggregates["physical_object_id"].map(phenotype_sources)
    aggregates["all_measurements_phenotype_tags"] = aggregates["physical_object_id"].map(phenotype_union)
    evidence_priority = measurements["evidence_status"].map(EVIDENCE_STATUS_PRIORITY)
    worst_priority = evidence_priority.groupby(measurements["physical_object_id"]).max()
    worst_status = worst_priority.map({value: key for key, value in EVIDENCE_STATUS_PRIORITY.items()})
    evidence_rows = measurements[evidence_priority.eq(measurements["physical_object_id"].map(worst_priority))]
    evidence_ids = evidence_rows.groupby("physical_object_id")["measurement_id"].agg(lambda values: ";".join(values.astype(str)))
    evidence_sources = evidence_rows.groupby("physical_object_id")["source_key"].agg(lambda values: ";".join(dict.fromkeys(values.astype(str))))
    evidence_bases = evidence_rows.groupby("physical_object_id")["evidence_status_basis"].agg(lambda values: ";".join(dict.fromkeys(values.astype(str))))
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
        lambda row: bool(row["lrd_reported_by_any_measurement"])
        if bool(row["lrd_designation_reported_by_any_measurement"]) else np.nan,
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
    return objects


def build_v6_catalogues(
    v5_measurements: pd.DataFrame,
    thrils_raw: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return v6 measurements, objects, links, aliases, and match candidates."""
    inherited_link_columns = [
        "measurement_id", "physical_object_id", "preferred_measurement_flag",
        "preferred_measurement_reason", "match_method", "match_reference",
    ]
    _require_columns(v5_measurements, inherited_link_columns, "v5 measurements")
    new = standardize_thrils(thrils_raw)
    candidates = candidate_matches(new, v5_measurements)
    if not candidates.empty:
        raise ValueError("THRILS retained rows have unresolved v5 identity candidates")

    inherited = v5_measurements[inherited_link_columns].copy()
    reserved = set(inherited["physical_object_id"].astype(str))
    link_rows = []
    for _, row in new.iterrows():
        physical_id = stable_object_id(
            str(row["object_id"]), source_key=THRILS_SOURCE_KEY, reserved_ids=reserved,
        )
        reserved.add(physical_id)
        link_rows.append({
            "measurement_id": row["measurement_id"], "physical_object_id": physical_id,
            "preferred_measurement_flag": True,
            "preferred_measurement_reason": "only catalogue measurement in this release",
            "match_method": "singleton assignment after coordinate-redshift search",
            "match_reference": "no v5 candidate within 0.5 arcsec and delta-z 0.01",
        })
    links = pd.concat([inherited, pd.DataFrame(link_rows)], ignore_index=True)
    release_columns = list(dict.fromkeys([*v5_measurements.columns, *new.columns]))
    measurements = pd.DataFrame.from_records([
        *v5_measurements.reindex(columns=release_columns).to_dict("records"),
        *new.reindex(columns=release_columns).to_dict("records"),
    ], columns=release_columns)
    measurements = measurements.drop(
        columns=[column for column in inherited_link_columns[1:] if column in measurements],
        errors="ignore",
    ).merge(links, on="measurement_id", validate="one_to_one")
    measurements["catalogue_release"] = CATALOGUE_RELEASE
    measurements = add_blagn_taxonomy(measurements)
    is_thrils = measurements["source_key"].eq(THRILS_SOURCE_KEY)
    measurements.loc[is_thrils, "selection_channels"] = "photometric_eelg_parent;deep_g395m_broad_halpha"
    validate_taxonomy(measurements)
    preferred_counts = measurements.groupby("physical_object_id")["preferred_measurement_flag"].sum()
    if len(measurements) != 112 or measurements["physical_object_id"].nunique() != 105 or not preferred_counts.eq(1).all():
        raise ValueError("v6 must contain 112 measurements, 105 objects, and one default per object")

    objects = _aggregate_objects(measurements)
    aliases = measurements[[
        "physical_object_id", "measurement_id", "object_id", "source_key",
        "ra_deg", "dec_deg", "redshift",
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
        candidates.reindex(columns=CANDIDATE_COLUMNS),
    )
