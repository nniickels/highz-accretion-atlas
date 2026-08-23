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


def stable_object_id(object_id: str) -> str:
    """Create a readable stable ID for a newly introduced singleton."""
    token = re.sub(r"[^A-Za-z0-9]+", "-", str(object_id)).strip("-").upper()
    if not token:
        raise ValueError("Cannot create a physical-object ID from a blank object_id")
    return f"HZA-{token}"


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
                }
            )
    return pd.DataFrame(rows)


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
