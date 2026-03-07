## This code defines functions for testing objects against different seed+growth models 


from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
import numpy as np

LN_10 = np.log(10.0)


@dataclass(frozen=True)
class SeedModel:
    """Simple seed-mass prior in log10(Msun)."""

    name: str
    log_mseed_min: float
    log_mseed_max: float


SEED_MODELS: dict[str, SeedModel] = {
    "light_popiii": SeedModel("light_popiii", 1.0, 2.0),
    "intermediate_cluster": SeedModel("intermediate_cluster", 3.0, 4.0),
    "heavy_dcbh": SeedModel("heavy_dcbh", 4.0, 6.0),
    "pbh": SeedModel("pbh", 2.0, 6.0),
}


def apply_mbh_interpretation(log_mbh_msun: float | np.ndarray, delta_dex: float = 0.0) -> np.ndarray:
    """Shift inferred log BH mass by an interpretation systematic in dex."""
    return np.asarray(log_mbh_msun, dtype=float) + float(delta_dex)


def apply_lbol_interpretation(log_lbol_erg_s: float | np.ndarray, delta_dex: float = 0.0) -> np.ndarray:
    """Shift inferred bolometric luminosity by an interpretation systematic in dex."""
    return np.asarray(log_lbol_erg_s, dtype=float) + float(delta_dex)


def apply_mstar_agn_contamination(
    log_mstar_msun: float | np.ndarray,
    agn_fraction: float,
) -> np.ndarray:
    """Correct host stellar mass for AGN contamination.

    Args:
        log_mstar_msun: observed host stellar mass in log10(Msun).
        agn_fraction: fraction of inferred host light attributed to AGN (0 <= f < 1).

    Returns:
        Corrected log10(Mstar/Msun).
    """
    if not (0.0 <= agn_fraction < 1.0):
        raise ValueError("agn_fraction must satisfy 0 <= f < 1")

    mstar_linear = np.power(10.0, np.asarray(log_mstar_msun, dtype=float))
    corrected = mstar_linear * (1.0 - agn_fraction)
    return np.log10(corrected)


def salpeter_efold_time_gyr(epsilon: float = 0.1, f_edd: float = 1.0) -> float:
    """Return BH e-folding time in Gyr for radiative efficiency and Eddington ratio."""
    if epsilon <= 0 or epsilon >= 1:
        raise ValueError("epsilon must be in (0, 1)")
    if f_edd <= 0:
        raise ValueError("f_edd must be positive")

    salpeter_base_gyr = 0.45
    return salpeter_base_gyr * (epsilon / (1.0 - epsilon)) / f_edd


def required_seed_mass_log10(
    log_mbh_final: float | np.ndarray,
    delta_t_gyr: float | np.ndarray,
    f_edd_avg: float = 1.0,
    epsilon: float = 0.1,
    merger_boost: float = 1.0,
) -> np.ndarray:
    """Compute required seed mass log10(Msun) to reach final BH mass in available time."""
    if merger_boost <= 0:
        raise ValueError("merger_boost must be > 0")

    t_sal = salpeter_efold_time_gyr(epsilon=epsilon, f_edd=f_edd_avg)
    growth_efolds = np.asarray(delta_t_gyr, dtype=float) / t_sal
    log_growth = growth_efolds / LN_10
    return np.asarray(log_mbh_final, dtype=float) - log_growth - np.log10(merger_boost)


def required_average_fedd(
    log_mseed: float | np.ndarray,
    log_mbh_final: float | np.ndarray,
    delta_t_gyr: float | np.ndarray,
    epsilon: float = 0.1,
    merger_boost: float = 1.0,
) -> np.ndarray:
    """Solve for mean f_Edd required over delta_t to reach final mass."""
    if merger_boost <= 0:
        raise ValueError("merger_boost must be > 0")

    if epsilon <= 0 or epsilon >= 1:
        raise ValueError("epsilon must be in (0, 1)")

    log_mass_gain = (
        np.asarray(log_mbh_final, dtype=float)
        - np.asarray(log_mseed, dtype=float)
        - np.log10(merger_boost)
    )
    efolds_needed = log_mass_gain * LN_10

    delta_t = np.asarray(delta_t_gyr, dtype=float)
    base = 0.45 * (epsilon / (1.0 - epsilon))
    return efolds_needed * base / delta_t


def evaluate_seed_model(
    *,
    log_mbh_final: float,
    delta_t_gyr: float,
    model_name: str,
    f_edd_avg: float = 1.0,
    epsilon: float = 0.1,
    merger_boost: float = 1.0,
    seed_models: Mapping[str, SeedModel] | None = None,
) -> dict[str, float | str | bool]:
    """Evaluate whether a seed model can satisfy a target BH mass for growth settings."""
    model_bank = SEED_MODELS if seed_models is None else dict(seed_models)
    if model_name not in model_bank:
        raise KeyError(f"Unknown seed model: {model_name}")

    model = model_bank[model_name]
    req = float(
        required_seed_mass_log10(
            log_mbh_final=log_mbh_final,
            delta_t_gyr=delta_t_gyr,
            f_edd_avg=f_edd_avg,
            epsilon=epsilon,
            merger_boost=merger_boost,
        )
    )

    feasible = model.log_mseed_min <= req <= model.log_mseed_max

    return {
        "model_name": model.name,
        "required_log_mseed": req,
        "model_log_mseed_min": model.log_mseed_min,
        "model_log_mseed_max": model.log_mseed_max,
        "is_feasible": feasible,
    }