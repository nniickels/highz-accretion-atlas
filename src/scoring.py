## This code defines functions for scoring feasibility of objects under different seed+growth models

# ---------------------------------- Imports -----------------------------------------------------

from __future__ import annotations
from typing import Iterable
import numpy as np
import pandas as pd

# ------------------------------ Functions -----------------------------------------------------

def _clip01(x: float | np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=float), 0.0, 1.0)


def score_required_seed_mass(
    required_log_mseed: float,
    model_log_mseed_min: float,
    model_log_mseed_max: float,
    soft_margin_dex: float = 0.5,
) -> float:
    """Score seed-mass compatibility in [0, 1] with soft penalties outside prior range."""
    req = float(required_log_mseed)
    lo = float(model_log_mseed_min)
    hi = float(model_log_mseed_max)

    if np.isnan(req) or np.isnan(lo) or np.isnan(hi):
        return np.nan
    if soft_margin_dex <= 0:
        raise ValueError("soft_margin_dex must be > 0")
    if lo > hi:
        raise ValueError("model_log_mseed_min cannot exceed model_log_mseed_max")

    if lo <= req <= hi:
        return 1.0

    distance = min(abs(req - lo), abs(req - hi))
    return float(_clip01(1.0 - distance / soft_margin_dex))


def score_required_fedd(
    required_fedd: float,
    plausible_max: float = 1.0,
    hard_max: float = 3.0,
) -> float:
    """Score mean accretion intensity requirement.

    1.0 is fully plausible (<= plausible_max), then linearly decays to 0 at hard_max.
    """
    if plausible_max <= 0 or hard_max <= plausible_max:
        raise ValueError("Need 0 < plausible_max < hard_max")

    req = float(required_fedd)
    if np.isnan(req):
        return np.nan
    if req <= plausible_max:
        return 1.0
    if req >= hard_max:
        return 0.0
    return float((hard_max - req) / (hard_max - plausible_max))


def aggregate_feasibility_score(
    seed_score: float,
    fedd_score: float,
    weights: tuple[float, float] = (0.6, 0.4),
) -> float:
    """Combine component scores into a single [0,1] feasibility score."""
    w_seed, w_fedd = map(float, weights)
    if w_seed < 0 or w_fedd < 0 or (w_seed + w_fedd) == 0:
        raise ValueError("weights must be non-negative and not both zero")

    total = w_seed + w_fedd
    score = (seed_score * w_seed + fedd_score * w_fedd) / total
    return float(_clip01(score))


def score_model_table(
    evaluations: pd.DataFrame,
    *,
    required_seed_col: str = "required_log_mseed",
    seed_min_col: str = "model_log_mseed_min",
    seed_max_col: str = "model_log_mseed_max",
    required_fedd_col: str = "required_fedd",
) -> pd.DataFrame:
    """Attach component + aggregate feasibility scores to evaluation table rows."""
    missing = {
        required_seed_col,
        seed_min_col,
        seed_max_col,
        required_fedd_col,
    } - set(evaluations.columns)
    if missing:
        raise ValueError(f"Missing required columns for scoring: {sorted(missing)}")

    scored = evaluations.copy()

    scored["seed_mass_score"] = [
        score_required_seed_mass(req, lo, hi)
        for req, lo, hi in zip(
            scored[required_seed_col],
            scored[seed_min_col],
            scored[seed_max_col],
            strict=False,
        )
    ]

    scored["fedd_score"] = [score_required_fedd(f) for f in scored[required_fedd_col]]

    scored["feasibility_score"] = [
        aggregate_feasibility_score(s, f)
        for s, f in zip(scored["seed_mass_score"], scored["fedd_score"], strict=False)
    ]

    return scored


def summarize_scores(scores: Iterable[float]) -> dict[str, float]:
    """Return compact summary stats for a collection of feasibility scores."""
    arr = np.asarray(list(scores), dtype=float)
    if arr.size == 0:
        raise ValueError("scores cannot be empty")

    return {
        "mean": float(arr.mean()),
        "median": float(np.median(arr)),
        "p10": float(np.percentile(arr, 10)),
        "p90": float(np.percentile(arr, 90)),
    }
