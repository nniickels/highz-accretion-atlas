"""Schema and validation gate for heterogeneous v7 source admission.

This module defines the contract only.  It does not ingest a source, build a
catalogue release, or modify the frozen v1--v6 products.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


OBJECT_CLASSES = {
    "broad_line_agn",
    "narrow_line_agn_candidate",
    "xray_agn_candidate",
    "high_ionization_line_candidate",
    "photometric_agn_candidate",
}
EVIDENCE_STATUSES = {"secure", "probable", "candidate", "disputed"}
SPECTROSCOPIC_TYPES = {
    "type1_broad_line",
    "type1_broad_line_candidate",
    "type2_narrow_line",
    "intermediate_or_ambiguous",
    "unknown",
}
SELECTION_CHANNELS = {
    "broad_balmer_line",
    "broad_halpha",
    "broad_hbeta",
    "broad_uv_line",
    "narrow_line_diagnostics",
    "xray",
    "photometric_sed",
    "high_ionization_line",
    "host_selected",
    "photometric_eelg_parent",
    "deep_g395m_broad_halpha",
}
PHENOTYPE_TAGS = {"lrd", "compact", "red", "merger", "clumpy", "dual_nucleus"}
LENSING_STATUSES = {"lensed", "unlensed", "not_reported", "not_applicable", "unknown"}
LENSING_MASS_CORRECTION_STATUSES = {"applied", "not_required", "not_applied", "unresolved"}
MASS_COMPARABILITY_GROUPS = {
    "virial_balmer_single_epoch",
    "virial_uv_single_epoch",
    "reverberation_or_dynamical_direct",
    "xray_or_bolometric_proxy",
    "sed_or_scaling_proxy",
    "assumed_eddington_ratio_mass",
    "no_numeric_mass",
}
HOST_PROPERTY_SCOPES = {"object_specific", "shared_host_system_total", "not_published"}
IDENTITY_RESOLUTION_STATUSES = {"resolved", "unresolved"}
OBSERVABLE_CENSORING = {"detection", "upper_limit", "lower_limit"}
CONDITIONAL_MASS_REASONS = {
    "mass_valid_only_if_broad_component_is_blr",
    "mass_depends_on_assumed_eddington_ratio",
    "mass_depends_on_sed_or_scaling_model",
    "mass_depends_on_unresolved_lensing",
}

# Frozen v5/v6 files retain their historical spellings.  A future v7 builder
# may use this explicit adapter when copying their rows into a new release.
V6_TO_V7_OBJECT_CLASS = {"broad-line-agn": "broad_line_agn"}
V6_TO_V7_EVIDENCE_STATUS = {
    "secure_accreting_mbh": "secure",
    "probable_accreting_mbh": "probable",
    "candidate_accreting_mbh": "candidate",
    "disputed_accreting_mbh": "disputed",
}
V6_TO_V7_PHENOTYPE_TAG = {"compact_source": "compact", "red_agn": "red"}

V7_REQUIRED_FIELDS = [
    "measurement_id",
    "object_id",
    "physical_object_id",
    "host_system_id",
    "identity_resolution_status",
    "source_key",
    "survey",
    "field",
    "source_table",
    "source_paper_version",
    "source_url",
    "source_doi",
    "source_archive_url",
    "extraction_date",
    "selection_criteria",
    "source_caveat_tags",
    "redshift",
    "object_class",
    "evidence_status",
    "evidence_status_basis",
    "spectroscopic_type",
    "selection_channels",
    "phenotype_tags",
    "lensing_status",
    "lensing_mu",
    "lensing_mass_correction_status",
    "lensing_provenance",
    "mbh_method",
    "mstar_method",
    "lbol_method",
    "edd_ratio_method",
    "log_mbh_msun_std",
    "log_mbh_err_plus",
    "log_mbh_err_minus",
    "mbh_statistical_uncertainty_kind",
    "log_mbh_systematic_dex",
    "mbh_systematic_kind",
    "mbh_systematic_applied_flag",
    "mass_comparability_group",
    "conditional_mass_flag",
    "conditional_mass_reason",
    "primary_mass_comparison_flag",
    "primary_mass_comparison_reason",
    "log_mstar_msun_std",
    "log_mstar_upper_limit_msun",
    "host_property_scope",
    "log_lbol_erg_s_std",
    "edd_ratio_std",
    "growth_ranking_eligible_flag",
    "growth_ranking_eligibility_reason",
    "primary_growth_ranking_flag",
    "primary_growth_ranking_reason",
]

OBSERVABLE_REQUIRED_FIELDS = [
    "observable_id",
    "measurement_id",
    "observable_name",
    "value",
    "err_plus",
    "err_minus",
    "censoring",
    "unit",
    "uncertainty_kind",
    "source_location",
]

GROWTH_ELIGIBLE_REASON = "eligible_numeric_mass_with_resolved_identity_and_lensing"
PRIMARY_ELIGIBLE_REASON = "eligible_secure_or_probable_primary_comparable_mass"


def _require_columns(frame: pd.DataFrame, fields: Iterable[str], label: str) -> None:
    if missing := sorted(set(fields) - set(frame.columns)):
        raise ValueError(f"{label} missing columns: {missing}")


def _nonempty(value: object) -> bool:
    return not pd.isna(value) and bool(str(value).strip())


def _strict_bool(value: object, field: str) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str) and value.strip().lower() in {"true", "false"}:
        return value.strip().lower() == "true"
    raise ValueError(f"{field} must contain explicit boolean values")


def _tokens(value: object) -> set[str]:
    if pd.isna(value) or not str(value).strip():
        return set()
    return {token.strip() for token in str(value).split(";") if token.strip()}


def normalize_v7_vocabulary(catalogue: pd.DataFrame) -> pd.DataFrame:
    """Translate known frozen-release labels without mutating the input."""
    result = catalogue.copy()
    if "object_class" in result:
        result["object_class"] = result["object_class"].replace(V6_TO_V7_OBJECT_CLASS)
    if "evidence_status" in result:
        result["evidence_status"] = result["evidence_status"].replace(
            V6_TO_V7_EVIDENCE_STATUS
        )
    if "phenotype_tags" in result:
        result["phenotype_tags"] = result["phenotype_tags"].map(
            lambda value: ";".join(
                V6_TO_V7_PHENOTYPE_TAG.get(token, token) for token in sorted(_tokens(value))
            )
        )
    return result


def expected_growth_eligibility_reason(row: pd.Series) -> str:
    """Return the single controlled reason implied by a measurement row."""
    if pd.isna(pd.to_numeric(pd.Series([row["log_mbh_msun_std"]]), errors="coerce").iloc[0]):
        return "missing_numeric_mbh"
    if pd.isna(pd.to_numeric(pd.Series([row["redshift"]]), errors="coerce").iloc[0]):
        return "missing_redshift"
    if not _nonempty(row["mbh_method"]):
        return "missing_mass_method"
    if row["mass_comparability_group"] == "no_numeric_mass":
        return "no_numeric_mass_method"
    if not _nonempty(row["mbh_statistical_uncertainty_kind"]):
        return "missing_uncertainty_semantics"
    if row["lensing_mass_correction_status"] == "unresolved":
        return "unresolved_lensing_treatment"
    if row["lensing_mass_correction_status"] == "not_applied":
        return "lensing_correction_not_applied"
    if row["identity_resolution_status"] != "resolved":
        return "unresolved_physical_identity"
    return GROWTH_ELIGIBLE_REASON


def expected_primary_eligibility_reason(row: pd.Series, growth_eligible: bool) -> str:
    if not growth_eligible:
        return "not_exploratory_eligible"
    if row["evidence_status"] == "candidate":
        return "candidate_evidence_excluded"
    if row["evidence_status"] == "disputed":
        return "disputed_evidence_excluded"
    if _strict_bool(row["conditional_mass_flag"], "conditional_mass_flag"):
        return "conditional_mass_interpretation_excluded"
    if not _strict_bool(row["primary_mass_comparison_flag"], "primary_mass_comparison_flag"):
        return "mass_method_not_primary_comparable"
    return PRIMARY_ELIGIBLE_REASON


def validate_v7_admission(catalogue: pd.DataFrame) -> None:
    """Validate a proposed heterogeneous measurement table before admission."""
    _require_columns(catalogue, V7_REQUIRED_FIELDS, "v7 admission table")
    if catalogue.empty:
        raise ValueError("v7 admission table cannot be empty")
    catalogue = catalogue.copy().reset_index(drop=True)
    for field in [
        "measurement_id", "object_id", "physical_object_id", "host_system_id",
        "source_key", "survey", "field", "source_table", "source_paper_version",
        "source_url", "extraction_date", "selection_criteria",
    ]:
        if not catalogue[field].map(_nonempty).all():
            raise ValueError(f"{field} cannot be missing or blank")
    if not catalogue["measurement_id"].is_unique:
        raise ValueError("measurement_id must be unique")
    object_to_system = catalogue.groupby("physical_object_id")["host_system_id"].nunique()
    if object_to_system.gt(1).any():
        raise ValueError("Each physical_object_id must map to one host_system_id")

    controlled = {
        "object_class": OBJECT_CLASSES,
        "evidence_status": EVIDENCE_STATUSES,
        "spectroscopic_type": SPECTROSCOPIC_TYPES,
        "lensing_status": LENSING_STATUSES,
        "lensing_mass_correction_status": LENSING_MASS_CORRECTION_STATUSES,
        "mass_comparability_group": MASS_COMPARABILITY_GROUPS,
        "host_property_scope": HOST_PROPERTY_SCOPES,
        "identity_resolution_status": IDENTITY_RESOLUTION_STATUSES,
    }
    for field, allowed in controlled.items():
        invalid = set(catalogue[field].dropna()) - allowed
        if invalid:
            raise ValueError(f"Invalid {field} values: {sorted(invalid)}")
    if catalogue["evidence_status_basis"].map(_nonempty).eq(False).any():
        raise ValueError("Every evidence status requires a nonempty basis")

    for field, allowed in [
        ("selection_channels", SELECTION_CHANNELS), ("phenotype_tags", PHENOTYPE_TAGS),
    ]:
        for value in catalogue[field]:
            tokens = _tokens(value)
            if field == "selection_channels" and not tokens:
                raise ValueError("selection_channels cannot be empty")
            if invalid := tokens - allowed:
                raise ValueError(f"Invalid {field} values: {sorted(invalid)}")

    numeric_fields = [
        "redshift", "lensing_mu", "log_mbh_msun_std", "log_mbh_err_plus",
        "log_mbh_err_minus", "log_mbh_systematic_dex", "log_mstar_msun_std",
        "log_mstar_upper_limit_msun", "log_lbol_erg_s_std", "edd_ratio_std",
    ]
    numeric = catalogue[numeric_fields].apply(pd.to_numeric, errors="coerce")
    for field in numeric_fields:
        invalid = catalogue[field].map(_nonempty) & numeric[field].isna()
        if invalid.any():
            raise ValueError(f"{field} contains nonnumeric values")
    for field in ["log_mbh_err_plus", "log_mbh_err_minus", "log_mbh_systematic_dex"]:
        if numeric[field].dropna().lt(0).any():
            raise ValueError(f"{field} cannot be negative")

    lensed = catalogue["lensing_status"].eq("lensed")
    if numeric.loc[lensed, "lensing_mu"].isna().any():
        raise ValueError("Lensed rows require numeric lensing_mu")
    if catalogue.loc[lensed, "lensing_provenance"].map(_nonempty).eq(False).any():
        raise ValueError("Lensed rows require lensing provenance")
    not_lensed = ~lensed
    if numeric.loc[not_lensed, "lensing_mu"].notna().any():
        raise ValueError("Only lensed rows may carry lensing_mu")
    correction_used = catalogue["lensing_mass_correction_status"].isin({"applied", "not_applied"})
    if (correction_used & ~lensed).any():
        raise ValueError("Applied/not-applied lensing corrections require lensing_status=lensed")

    mass = numeric["log_mbh_msun_std"].notna()
    if catalogue.loc[mass, "mbh_method"].map(_nonempty).eq(False).any():
        raise ValueError("Numeric masses require mbh_method")
    stellar_mass = numeric["log_mstar_msun_std"].notna()
    if catalogue.loc[stellar_mass, "mstar_method"].map(_nonempty).eq(False).any():
        raise ValueError("Numeric stellar masses require mstar_method")
    bolometric_luminosity = numeric["log_lbol_erg_s_std"].notna()
    if catalogue.loc[bolometric_luminosity, "lbol_method"].map(_nonempty).eq(False).any():
        raise ValueError("Numeric bolometric luminosities require lbol_method")
    eddington_ratio = numeric["edd_ratio_std"].notna()
    if catalogue.loc[eddington_ratio, "edd_ratio_method"].map(_nonempty).eq(False).any():
        raise ValueError("Numeric Eddington ratios require edd_ratio_method")
    if catalogue.loc[mass, "mbh_statistical_uncertainty_kind"].map(_nonempty).eq(False).any():
        raise ValueError("Numeric masses require statistical-uncertainty semantics")
    if catalogue.loc[mass, "mass_comparability_group"].eq("no_numeric_mass").any():
        raise ValueError("Numeric masses cannot use no_numeric_mass")
    if catalogue.loc[~mass, "mass_comparability_group"].ne("no_numeric_mass").any():
        raise ValueError("Rows without a numeric mass must use no_numeric_mass")
    systematic = numeric["log_mbh_systematic_dex"].notna()
    if catalogue.loc[systematic, "mbh_systematic_kind"].map(_nonempty).eq(False).any():
        raise ValueError("Numeric mass systematics require a separate systematic kind")
    applied_systematic = catalogue["mbh_systematic_applied_flag"].map(
        lambda value: _strict_bool(value, "mbh_systematic_applied_flag")
    )
    if (systematic & applied_systematic).any():
        raise ValueError("v7 admission requires calibration systematics separate from statistical errors")
    if (applied_systematic & ~systematic).any():
        raise ValueError("A mass systematic cannot be applied when no numeric systematic is recorded")
    if (systematic & ~mass).any():
        raise ValueError("Rows without numeric masses cannot carry mass systematics")
    mass_errors = numeric[["log_mbh_err_plus", "log_mbh_err_minus"]].notna().any(axis=1)
    if (mass_errors & ~mass).any():
        raise ValueError("Rows without numeric masses cannot carry mass errors")

    conditional = catalogue["conditional_mass_flag"].map(
        lambda value: _strict_bool(value, "conditional_mass_flag")
    )
    if catalogue.loc[conditional, "conditional_mass_reason"].map(_nonempty).eq(False).any():
        raise ValueError("Conditional masses require a machine-readable reason")
    invalid_conditional_reasons = (
        set(catalogue.loc[conditional, "conditional_mass_reason"]) - CONDITIONAL_MASS_REASONS
    )
    if invalid_conditional_reasons:
        raise ValueError(f"Invalid conditional mass reasons: {sorted(invalid_conditional_reasons)}")
    if catalogue.loc[~conditional, "conditional_mass_reason"].map(_nonempty).any():
        raise ValueError("Unconditional masses must leave conditional_mass_reason blank")
    if (conditional & ~mass).any():
        raise ValueError("Rows without numeric masses cannot be conditional masses")

    host_value = numeric["log_mstar_msun_std"].notna() | numeric["log_mstar_upper_limit_msun"].notna()
    if catalogue.loc[host_value, "host_property_scope"].eq("not_published").any():
        raise ValueError("Published host values require an explicit property scope")
    if catalogue.loc[~host_value, "host_property_scope"].ne("not_published").any():
        raise ValueError("Missing host values must use host_property_scope=not_published")
    shared = catalogue["host_property_scope"].eq("shared_host_system_total")
    for system_id, group in catalogue.loc[shared].groupby("host_system_id"):
        if group["physical_object_id"].nunique() < 2:
            raise ValueError(f"Shared host system {system_id} must contain multiple physical objects")
        for field in ["log_mstar_msun_std", "log_mstar_upper_limit_msun"]:
            values = pd.to_numeric(group[field], errors="coerce").dropna().unique()
            if len(values) > 1:
                raise ValueError(f"Shared host system {system_id} has inconsistent {field}")

    primary_mass = catalogue["primary_mass_comparison_flag"].map(
        lambda value: _strict_bool(value, "primary_mass_comparison_flag")
    )
    if catalogue["primary_mass_comparison_reason"].map(_nonempty).eq(False).any():
        raise ValueError("Every row requires a primary-mass-comparison reason")
    if (primary_mass & ~mass).any():
        raise ValueError("A row without numeric mass cannot be primary-mass comparable")

    growth = catalogue["growth_ranking_eligible_flag"].map(
        lambda value: _strict_bool(value, "growth_ranking_eligible_flag")
    )
    primary = catalogue["primary_growth_ranking_flag"].map(
        lambda value: _strict_bool(value, "primary_growth_ranking_flag")
    )
    for index, row in catalogue.iterrows():
        expected_growth_reason = expected_growth_eligibility_reason(row)
        expected_growth = expected_growth_reason == GROWTH_ELIGIBLE_REASON
        if growth.loc[index] != expected_growth or row["growth_ranking_eligibility_reason"] != expected_growth_reason:
            raise ValueError(f"Growth-ranking outcome/reason mismatch for {row['measurement_id']}")
        expected_primary_reason = expected_primary_eligibility_reason(row, expected_growth)
        expected_primary = expected_primary_reason == PRIMARY_ELIGIBLE_REASON
        if primary.loc[index] != expected_primary or row["primary_growth_ranking_reason"] != expected_primary_reason:
            raise ValueError(f"Primary-ranking outcome/reason mismatch for {row['measurement_id']}")


def validate_v7_observables(
    observables: pd.DataFrame,
    known_measurement_ids: Iterable[str] | None = None,
) -> None:
    """Validate a long-form table of detections and censored observables."""
    _require_columns(observables, OBSERVABLE_REQUIRED_FIELDS, "v7 observable table")
    if not observables["observable_id"].is_unique:
        raise ValueError("observable_id must be unique")
    for field in ["observable_id", "measurement_id", "observable_name", "unit", "source_location"]:
        if not observables[field].map(_nonempty).all():
            raise ValueError(f"Observable {field} cannot be missing or blank")
    if invalid := set(observables["censoring"]) - OBSERVABLE_CENSORING:
        raise ValueError(f"Invalid observable censoring values: {sorted(invalid)}")
    if known_measurement_ids is not None:
        unknown = set(observables["measurement_id"]) - set(known_measurement_ids)
        if unknown:
            raise ValueError(f"Observable rows reference unknown measurements: {sorted(unknown)}")
    numeric = observables[["value", "err_plus", "err_minus"]].apply(pd.to_numeric, errors="coerce")
    if numeric["value"].isna().any():
        raise ValueError("Detections and limits require a numeric value")
    if numeric[["err_plus", "err_minus"]].lt(0).any().any():
        raise ValueError("Observable uncertainties cannot be negative")
    limits = observables["censoring"].ne("detection")
    if numeric.loc[limits, ["err_plus", "err_minus"]].notna().any().any():
        raise ValueError("Censored limits must not masquerade as symmetric detections")
    if observables.loc[limits, "uncertainty_kind"].ne("limit").any():
        raise ValueError("Censored rows require uncertainty_kind=limit")
    detections = ~limits
    published_uncertainty = observables["uncertainty_kind"].ne("not_published")
    require_errors = detections & published_uncertainty
    if numeric.loc[require_errors, ["err_plus", "err_minus"]].isna().any().any():
        raise ValueError("Detected values require both errors unless uncertainty is not published")
