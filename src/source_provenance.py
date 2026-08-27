"""Controlled validation for the non-destructive source-provenance supplement."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = (
    "provenance_id", "source_key", "source_role", "publication_status",
    "evidence_status", "source_paper_version", "source_url", "source_doi",
    "dataset_doi", "source_archive_url", "source_archive_sha256",
    "catalogue_extraction_date", "provenance_verification_date",
    "status_review_due", "data_use", "catalogue_value_policy", "notes",
)
SOURCE_ROLES = {"primary_measurement", "coordinate_source", "context_source", "reanalysis"}
PUBLICATION_STATUSES = {"peer_reviewed", "preprint", "data_release"}
EVIDENCE_STATUSES = {"secure", "candidate", "disputed", "mixed", "not_applicable"}
CATALOGUE_VALUE_POLICIES = {
    "frozen_catalogue_values_unchanged", "supplement_only_frozen_rows_unchanged",
}
DATE_SENTINELS = {"not_recorded_in_frozen_v1_source_layer", "not_applicable"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise AssertionError(f"{field} must use YYYY-MM-DD: {value}") from exc


def validate_source_provenance_registry(registry: pd.DataFrame) -> None:
    """Validate schema, controlled vocabularies, dates, identifiers, and URLs."""
    if tuple(registry.columns) != REQUIRED_COLUMNS:
        raise AssertionError("source provenance registry columns do not match the contract")
    if registry.empty or registry.isna().any().any() or (registry == "").any().any():
        raise AssertionError("source provenance registry fields must be nonblank")
    if registry["provenance_id"].duplicated().any():
        raise AssertionError("provenance_id values must be unique")

    controlled = {
        "source_role": SOURCE_ROLES,
        "publication_status": PUBLICATION_STATUSES,
        "evidence_status": EVIDENCE_STATUSES,
        "catalogue_value_policy": CATALOGUE_VALUE_POLICIES,
    }
    for column, allowed in controlled.items():
        unexpected = sorted(set(registry[column]) - allowed)
        if unexpected:
            raise AssertionError(f"unexpected {column}: {unexpected}")

    if not registry["source_url"].str.startswith("https://").all():
        raise AssertionError("source_url values must use HTTPS")
    if not registry["source_archive_url"].str.startswith("https://").all():
        raise AssertionError("source_archive_url values must use HTTPS")
    if not registry["source_archive_sha256"].map(lambda value: bool(SHA256_RE.fullmatch(value))).all():
        raise AssertionError("source archive hashes must be lowercase SHA-256 values")

    for row in registry.itertuples(index=False):
        verified = _parse_date(row.provenance_verification_date, "provenance_verification_date")
        if row.catalogue_extraction_date not in DATE_SENTINELS:
            _parse_date(row.catalogue_extraction_date, "catalogue_extraction_date")
        if row.publication_status == "preprint":
            if row.source_doi == "not_applicable":
                raise AssertionError("preprints must record their arXiv DOI")
            if _parse_date(row.status_review_due, "status_review_due") <= verified:
                raise AssertionError("preprint status_review_due must follow verification")
        elif row.status_review_due != "not_applicable":
            raise AssertionError("only preprints may have a status review due date")
        if row.publication_status == "peer_reviewed" and row.source_doi == "not_applicable":
            raise AssertionError("peer-reviewed sources must record a DOI")


def load_source_provenance_registry(path: str | Path) -> pd.DataFrame:
    registry = pd.read_csv(path, dtype=str, keep_default_na=False)
    validate_source_provenance_registry(registry)
    return registry


def validate_catalogue_source_coverage(registry: pd.DataFrame, catalogue: pd.DataFrame) -> None:
    """Require every catalogue source family to have a measurement or reanalysis record."""
    admitted = registry[registry["source_role"].isin({"primary_measurement", "reanalysis"})]
    missing = sorted(set(catalogue["source_key"].dropna()) - set(admitted["source_key"]))
    if missing:
        raise AssertionError(f"catalogue source keys missing provenance: {missing}")
