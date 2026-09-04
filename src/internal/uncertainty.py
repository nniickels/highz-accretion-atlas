"""Shared asymmetric-uncertainty sampling helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MbhUncertaintySpec:
    sigma_plus: float
    sigma_minus: float
    mode: str


def resolve_mbh_uncertainty(
    err_plus: float | None,
    err_minus: float | None,
) -> MbhUncertaintySpec:
    """Return the sigma values and provenance mode used for mass sampling."""
    plus = float(err_plus) if pd.notna(err_plus) else np.nan
    minus = float(err_minus) if pd.notna(err_minus) else np.nan
    if np.isfinite(plus) and plus < 0:
        raise ValueError("MBH uncertainties must be non-negative where finite")
    if np.isfinite(minus) and minus < 0:
        raise ValueError("MBH uncertainties must be non-negative where finite")
    if np.isfinite(plus) and np.isfinite(minus):
        mode = "asymmetric" if not np.isclose(plus, minus) else "symmetric_reported"
        return MbhUncertaintySpec(plus, minus, mode)
    if np.isfinite(plus):
        return MbhUncertaintySpec(plus, plus, "symmetric_from_plus")
    if np.isfinite(minus):
        return MbhUncertaintySpec(minus, minus, "symmetric_from_minus")
    return MbhUncertaintySpec(0.0, 0.0, "point_estimate_no_reported_mbh_error")


def asymmetric_normal_samples(
    center: float,
    err_plus: float | None,
    err_minus: float | None,
    *,
    n_samples: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample an equal-side two-piece normal approximation in log space."""
    spec = resolve_mbh_uncertainty(err_plus, err_minus)
    z = rng.standard_normal(int(n_samples))
    sigma = np.where(z >= 0.0, spec.sigma_plus, spec.sigma_minus)
    return float(center) + z * sigma


def summarize_distribution(values: np.ndarray, *, prefix: str) -> dict[str, float]:
    """Return the stored percentile summary for one finite distribution."""
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        raise ValueError("Cannot summarize an empty distribution")
    if not np.isfinite(arr).all():
        raise ValueError(f"{prefix} distribution contains non-finite values")
    p5, p16, p50, p84, p95 = np.percentile(arr, [5, 16, 50, 84, 95])
    return {
        f"{prefix}_p5": float(p5),
        f"{prefix}_p16": float(p16),
        f"{prefix}_p50": float(p50),
        f"{prefix}_p84": float(p84),
        f"{prefix}_p95": float(p95),
    }


def reported_error_scope(source_key: str, has_reported_error: bool) -> str:
    """Describe retained source errors; no statistical-only assumption is made."""
    if not has_reported_error:
        return "not_reported"
    if source_key == "ubler24_zs7_offset_blagn":
        return "includes_source_calibration_scatter"
    return "as_published_components_not_decomposed"
