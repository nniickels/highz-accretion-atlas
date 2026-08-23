"""Deterministic measurement-to-object identity utilities.

Coordinates and redshift produce review candidates, not automatic scientific
truth.  A match is accepted only when it is unambiguous under explicit
thresholds or appears in a manual override table.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

import numpy as np
import pandas as pd


DEFAULT_MAX_SEPARATION_ARCSEC = 0.5
DEFAULT_MAX_REDSHIFT_DELTA = 0.01
CANDIDATE_COLUMNS = [
    "measurement_id", "candidate_measurement_id", "candidate_object_id",
    "candidate_physical_object_id", "separation_arcsec", "redshift_delta",
    "match_scope", "candidate_source_key",
]


def angular_separation_arcsec(
    ra1_deg: float | np.ndarray,
    dec1_deg: float | np.ndarray,
    ra2_deg: float | np.ndarray,
    dec2_deg: float | np.ndarray,
) -> np.ndarray:
    """Great-circle angular separation in arcseconds."""
    ra1 = np.deg2rad(np.asarray(ra1_deg, dtype=float))
    dec1 = np.deg2rad(np.asarray(dec1_deg, dtype=float))
    ra2 = np.deg2rad(np.asarray(ra2_deg, dtype=float))
    dec2 = np.deg2rad(np.asarray(dec2_deg, dtype=float))
    cosine = np.sin(dec1) * np.sin(dec2) + np.cos(dec1) * np.cos(dec2) * np.cos(ra1 - ra2)
    return np.rad2deg(np.arccos(np.clip(cosine, -1.0, 1.0))) * 3600.0


def stable_object_id(
    object_id: str,
    *,
    source_key: str | None = None,
    reserved_ids: Iterable[str] = (),
) -> str:
    """Allocate a readable ID, using a source namespace on token collision.

    Existing release IDs are passed as ``reserved_ids``.  This preserves the
    historical un-namespaced form when unique and prevents two unrelated
    source labels from silently receiving the same physical-object ID.
    """
    token = re.sub(r"[^A-Za-z0-9]+", "-", str(object_id)).strip("-").upper()
    if not token:
        raise ValueError("Cannot create a physical-object ID from a blank object_id")
    candidate = f"HZA-{token}"
    reserved = {str(value) for value in reserved_ids}
    if candidate not in reserved:
        return candidate
    if source_key is None:
        raise ValueError(f"Physical-object ID collision for {candidate}; source_key is required")
    source_token = re.sub(r"[^A-Za-z0-9]+", "-", str(source_key)).strip("-").upper()
    if not source_token:
        raise ValueError("Cannot resolve physical-object ID collision from a blank source_key")
    namespaced = f"HZA-{source_token}-{token}"
    if namespaced in reserved:
        raise ValueError(f"Physical-object ID collision remains after namespacing: {namespaced}")
    return namespaced


def candidate_matches(
    new_rows: pd.DataFrame,
    reference_rows: pd.DataFrame,
    *,
    max_separation_arcsec: float = DEFAULT_MAX_SEPARATION_ARCSEC,
    max_redshift_delta: float = DEFAULT_MAX_REDSHIFT_DELTA,
) -> pd.DataFrame:
    """Return all coordinate/redshift candidate links within fixed thresholds."""
    required_new = {"measurement_id", "ra_deg", "dec_deg", "redshift"}
    required_ref = required_new | {"physical_object_id", "object_id"}
    if missing := required_new - set(new_rows.columns):
        raise ValueError(f"New measurements missing identity fields: {sorted(missing)}")
    if missing := required_ref - set(reference_rows.columns):
        raise ValueError(f"Reference measurements missing identity fields: {sorted(missing)}")

    rows: list[dict[str, object]] = []
    for _, new in new_rows.iterrows():
        separations = angular_separation_arcsec(
            float(new["ra_deg"]),
            float(new["dec_deg"]),
            reference_rows["ra_deg"].to_numpy(float),
            reference_rows["dec_deg"].to_numpy(float),
        )
        dz = np.abs(reference_rows["redshift"].to_numpy(float) - float(new["redshift"]))
        mask = (separations <= max_separation_arcsec) & (dz <= max_redshift_delta)
        for idx in np.flatnonzero(mask):
            ref = reference_rows.iloc[int(idx)]
            rows.append(
                {
                    "measurement_id": new["measurement_id"],
                    "candidate_measurement_id": ref["measurement_id"],
                    "candidate_object_id": ref["object_id"],
                    "candidate_physical_object_id": ref["physical_object_id"],
                    "separation_arcsec": float(separations[idx]),
                    "redshift_delta": float(dz[idx]),
                    "match_scope": "prior_release",
                    "candidate_source_key": ref.get("source_key", np.nan),
                }
            )
    return pd.DataFrame(rows, columns=CANDIDATE_COLUMNS)


def cross_source_candidate_matches(
    new_rows: pd.DataFrame,
    *,
    max_separation_arcsec: float = DEFAULT_MAX_SEPARATION_ARCSEC,
    max_redshift_delta: float = DEFAULT_MAX_REDSHIFT_DELTA,
) -> pd.DataFrame:
    """Return within-release candidates between different literature sources."""
    required = {"measurement_id", "object_id", "source_key", "ra_deg", "dec_deg", "redshift"}
    if missing := required - set(new_rows.columns):
        raise ValueError(f"New measurements missing cross-source identity fields: {sorted(missing)}")
    rows: list[dict[str, object]] = []
    ordered = new_rows.reset_index(drop=True)
    for left_index in range(len(ordered)):
        left = ordered.iloc[left_index]
        for right_index in range(left_index + 1, len(ordered)):
            right = ordered.iloc[right_index]
            if left["source_key"] == right["source_key"]:
                continue
            separation = float(angular_separation_arcsec(
                float(left["ra_deg"]), float(left["dec_deg"]),
                float(right["ra_deg"]), float(right["dec_deg"]),
            ))
            dz = abs(float(left["redshift"]) - float(right["redshift"]))
            if separation <= max_separation_arcsec and dz <= max_redshift_delta:
                rows.append({
                    "measurement_id": left["measurement_id"],
                    "candidate_measurement_id": right["measurement_id"],
                    "candidate_object_id": right["object_id"],
                    "candidate_physical_object_id": np.nan,
                    "separation_arcsec": separation,
                    "redshift_delta": dz,
                    "match_scope": "same_release_cross_source",
                    "candidate_source_key": right["source_key"],
                })
    return pd.DataFrame(rows, columns=CANDIDATE_COLUMNS)


def apply_reviewed_identity_overrides(
    candidates: pd.DataFrame,
    overrides: pd.DataFrame,
    *,
    known_measurement_ids: Iterable[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Require candidate decisions and allow documented manual assertions.

    ``threshold_candidate`` rows must correspond to a generated candidate.
    ``manual_assertion`` rows may fall outside the numerical thresholds, but
    both measurements must be known and the review metadata must be complete.
    """
    required = {
        "measurement_id", "candidate_measurement_id", "decision", "physical_object_id",
        "review_basis", "review_reference", "review_date", "match_origin",
    }
    if missing := required - set(overrides.columns):
        raise ValueError(f"Identity override registry missing fields: {sorted(missing)}")
    keys = ["measurement_id", "candidate_measurement_id"]
    if overrides.duplicated(keys).any():
        raise ValueError("Identity override registry contains duplicate candidate decisions")
    origins = {"threshold_candidate", "manual_assertion"}
    if invalid := set(overrides["match_origin"]) - origins:
        raise ValueError(f"Invalid identity match origins: {sorted(invalid)}")
    allowed = {"accepted", "rejected"}
    if invalid := set(overrides["decision"]) - allowed:
        raise ValueError(f"Invalid identity decisions: {sorted(invalid)}")
    for column in ["review_basis", "review_reference", "review_date"]:
        if overrides[column].isna().any() or overrides[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Identity override registry requires nonblank {column}")
    candidate_keys = set(map(tuple, candidates[keys].astype(str).to_numpy()))
    threshold_overrides = overrides[overrides["match_origin"].eq("threshold_candidate")]
    threshold_keys = set(map(tuple, threshold_overrides[keys].astype(str).to_numpy()))
    if unexpected := threshold_keys - candidate_keys:
        raise ValueError(f"Identity registry contains stale threshold-candidate pairs: {sorted(unexpected)}")
    manual = overrides[overrides["match_origin"].eq("manual_assertion")]
    if not manual.empty:
        if known_measurement_ids is None:
            raise ValueError("Manual identity assertions require known_measurement_ids")
        known = {str(value) for value in known_measurement_ids}
        asserted = set(manual["measurement_id"].astype(str)) | set(manual["candidate_measurement_id"].astype(str))
        if unknown := asserted - known:
            raise ValueError(f"Manual identity assertions contain unknown measurements: {sorted(unknown)}")
    reviewed = candidates.merge(threshold_overrides, on=keys, how="left", validate="one_to_one")
    if reviewed["decision"].isna().any():
        missing_pairs = reviewed.loc[reviewed["decision"].isna(), keys].to_dict("records")
        raise ValueError(f"Unreviewed identity candidates: {missing_pairs}")
    manual_reviewed = manual.copy()
    for column in CANDIDATE_COLUMNS:
        if column not in manual_reviewed:
            manual_reviewed[column] = np.nan
    reviewed = pd.concat([reviewed, manual_reviewed.reindex(columns=reviewed.columns)], ignore_index=True)
    accepted = reviewed[reviewed["decision"].eq("accepted")]
    if accepted["physical_object_id"].isna().any():
        raise ValueError("Accepted identity candidates require physical_object_id")
    prior = accepted[accepted["candidate_physical_object_id"].notna()]
    if not prior.empty and not prior["physical_object_id"].eq(prior["candidate_physical_object_id"]).all():
        raise ValueError("Accepted prior-release identity conflicts with its stable physical-object ID")
    accepted_pairs: dict[str, str] = {}
    for _, row in accepted.iterrows():
        physical_id = str(row["physical_object_id"])
        for measurement_id in [row["measurement_id"], row["candidate_measurement_id"]]:
            prior = accepted_pairs.get(str(measurement_id))
            if prior is not None and prior != physical_id:
                raise ValueError(f"Conflicting accepted identities for {measurement_id}")
            accepted_pairs[str(measurement_id)] = physical_id
    return reviewed, accepted_pairs


def require_unambiguous_candidates(candidates: pd.DataFrame, measurement_ids: Iterable[str]) -> None:
    """Reject two-or-more candidate objects for any new measurement."""
    if candidates.empty:
        return
    counts = candidates.groupby("measurement_id")["candidate_physical_object_id"].nunique()
    ambiguous = counts[counts > 1]
    if not ambiguous.empty:
        raise ValueError(f"Ambiguous physical-object candidates: {ambiguous.index.tolist()}")
    unexpected = set(candidates["measurement_id"]) - set(measurement_ids)
    if unexpected:
        raise ValueError(f"Candidate table contains unknown measurements: {sorted(unexpected)}")
