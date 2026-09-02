"""Orthogonal evidence, type, selection, and phenotype axes for atlas releases."""

from __future__ import annotations

import numpy as np
import pandas as pd


EVIDENCE_STATUSES = {
    "secure_accreting_mbh", "probable_accreting_mbh",
    "candidate_accreting_mbh", "disputed_accreting_mbh",
}
SPECTROSCOPIC_TYPES = {
    "type1_broad_line", "type2_narrow_line", "intermediate_or_ambiguous", "unknown",
}
TAXONOMY_FIELDS = [
    "evidence_status", "evidence_status_basis", "spectroscopic_type", "selection_channels",
    "phenotype_tags", "lensing_status", "growth_ranking_eligible_flag",
    "primary_growth_ranking_flag",
]

INTERPRETIVE_CANDIDATE_TAGS = {"alternative_non_agn"}
INTERPRETIVE_PROBABLE_TAGS = {
    "possible_outflow_contribution", "absorption_interpretation_uncertain",
}


def _boolish(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return bool(value)


def _tags(value: object) -> set[str]:
    if pd.isna(value):
        return set()
    return {tag.strip() for tag in str(value).split(";") if tag.strip()}


def _contains_any(tags: set[str], tokens: set[str]) -> bool:
    return any(token in tag for token in tokens for tag in tags)


def _evidence_assignment(row: pd.Series) -> tuple[str, str]:
    """Keep line-detection robustness separate from physical interpretation."""
    tags = _tags(row.get("source_caveat_tags"))
    if _contains_any(tags, INTERPRETIVE_CANDIDATE_TAGS):
        return (
            "candidate_accreting_mbh",
            "robust_broad_line_with_recorded_alternative_non_agn_interpretation",
        )
    if _contains_any(tags, INTERPRETIVE_PROBABLE_TAGS):
        return (
            "probable_accreting_mbh",
            "robust_broad_line_with_recorded_outflow_or_absorption_interpretive_caveat",
        )
    if str(row.get("quality_flag", "")).lower() == "robust":
        return (
            "secure_accreting_mbh",
            "published_blagn_with_robust_detection_and_no_recorded_alternative_interpretation",
        )
    return (
        "probable_accreting_mbh",
        "published_blagn_with_tentative_broad_line_detection",
    )


def add_blagn_taxonomy(catalogue: pd.DataFrame) -> pd.DataFrame:
    """Add canonical taxonomy axes without changing source classifications."""
    result = catalogue.copy()
    evidence = result.apply(_evidence_assignment, axis=1)
    result["evidence_status"] = [value[0] for value in evidence]
    result["evidence_status_basis"] = [value[1] for value in evidence]
    result["spectroscopic_type"] = "type1_broad_line"
    species = result.get("broad_line_species", pd.Series(index=result.index, dtype=object))
    result["selection_channels"] = species.astype("string").str.lower().map(
        {"halpha": "broad_halpha", "hbeta": "broad_hbeta"},
    ).fillna("broad_balmer_line")
    result["phenotype_tags"] = ""
    lrd = result.get("lrd_flag", pd.Series(index=result.index, dtype=object)).map(_boolish)
    result.loc[lrd, "phenotype_tags"] = "lrd"
    if "red_agn_flag" in result:
        red = result["red_agn_flag"].map(_boolish)
        result.loc[red, "phenotype_tags"] = result.loc[red, "phenotype_tags"].map(
            lambda value: ";".join(filter(None, [value, "red_agn"])),
        )
    if "compact_source_flag" in result:
        compact = result["compact_source_flag"].map(_boolish)
        result.loc[compact, "phenotype_tags"] = result.loc[compact, "phenotype_tags"].map(
            lambda value: ";".join(filter(None, [value, "compact_source"])),
        )
    result["lensing_status"] = np.where(result["lensing_mu"].notna(), "lensed", "unknown")
    result["growth_ranking_eligible_flag"] = (
        pd.to_numeric(result["log_mbh_msun_std"], errors="coerce").notna()
        & ~result["evidence_status"].eq("disputed_accreting_mbh")
    )
    result["primary_growth_ranking_flag"] = (
        result["growth_ranking_eligible_flag"]
        & result["evidence_status"].isin({"secure_accreting_mbh", "probable_accreting_mbh"})
    )
    validate_taxonomy(result)
    return result


def validate_taxonomy(catalogue: pd.DataFrame) -> None:
    missing = set(TAXONOMY_FIELDS) - set(catalogue.columns)
    if missing:
        raise ValueError(f"Catalogue missing taxonomy fields: {sorted(missing)}")
    if invalid := set(catalogue["evidence_status"]) - EVIDENCE_STATUSES:
        raise ValueError(f"Invalid evidence statuses: {sorted(invalid)}")
    if invalid := set(catalogue["spectroscopic_type"]) - SPECTROSCOPIC_TYPES:
        raise ValueError(f"Invalid spectroscopic types: {sorted(invalid)}")
    eligible = catalogue["growth_ranking_eligible_flag"].map(_boolish)
    if catalogue.loc[eligible, "log_mbh_msun_std"].isna().any():
        raise ValueError("Growth-ranking-eligible rows require a black-hole mass")
    primary = catalogue["primary_growth_ranking_flag"].map(_boolish)
    if (primary & ~eligible).any():
        raise ValueError("Primary growth-ranking rows must be growth-ranking eligible")
    if catalogue.loc[primary, "evidence_status"].isin(
        {"candidate_accreting_mbh", "disputed_accreting_mbh"}
    ).any():
        raise ValueError("Candidate or disputed rows cannot enter the primary growth ranking")
