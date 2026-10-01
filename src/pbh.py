"""Conditional PBH-seed growth diagnostics, not a formation/abundance model.

The seed mass is its mass at accretion onset. Formation is assumed to precede
matter-radiation equality; growth before onset is omitted. Dayal (2024), Eq. 1
and Section 2 supply the equality-onset inversion benchmark. Delayed onset and
lower average rates are sensitivity tests, not predictions of that paper.
"""
from __future__ import annotations

import numpy as np

from src import models
from src.internal.early_start_cosmology import cosmic_time_gyr, EQUALITY_REDSHIFT


def growth_interval_gyr(z_accretion, z_obs):
    """Radiation-inclusive time between onset and observation, in Gyr.

    v4 considers only post-equality onset. Unlike a formation redshift,
    ``z_accretion`` specifies when the assumed growth prescription starts.
    """
    onset, observed = np.broadcast_arrays(
        np.asarray(z_accretion, dtype=float), np.asarray(z_obs, dtype=float)
    )
    if not np.isfinite(onset).all() or not np.isfinite(observed).all():
        raise ValueError("Redshifts must be finite")
    if (observed < 0).any() or (onset <= observed).any():
        raise ValueError("Accretion onset must precede observation: z_accretion > z_obs >= 0")
    if (onset > EQUALITY_REDSHIFT).any():
        raise ValueError("v4 does not model accretion before matter-radiation equality")
    return cosmic_time_gyr(observed) - cosmic_time_gyr(onset)


def minimum_seed_log10(log_mbh, z_accretion, z_obs, fedd_cap=1.0, epsilon=0.1):
    """Smallest onset seed reaching the target with mean f_Edd <= cap.

    No mergers or mass loss. Equality uses the cap throughout the interval;
    larger seeds up to the target mass can use smaller average rates.
    """
    if not np.isfinite(np.asarray(log_mbh, dtype=float)).all():
        raise ValueError("Target mass must be finite")
    _validate_growth_parameters(fedd_cap, epsilon)
    return models.required_seed_mass_log10(
        log_mbh, growth_interval_gyr(z_accretion, z_obs), fedd_cap, epsilon,
        merger_boost=1.0,
    )


def _validate_growth_parameters(fedd_cap, epsilon):
    cap, eps = np.broadcast_arrays(
        np.asarray(fedd_cap, dtype=float), np.asarray(epsilon, dtype=float)
    )
    if not np.isfinite(cap).all() or (cap < 0).any():
        raise ValueError("fedd_cap must be finite and non-negative")
    if not np.isfinite(eps).all() or ((eps <= 0) | (eps >= 1)).any():
        raise ValueError("epsilon must be finite and between zero and one")


def compatible_mass_draw_fraction(sorted_log_mass_draws, log_mseed, z_accretion,
                                  z_obs, fedd_cap=1.0, epsilon=0.1):
    """Fraction of draws reachable for SOME mean rate in [0, cap].

    This is conditional mass-error support, not a PBH posterior probability.
    Seeds above a draw's target mass are excluded rather than accepting the
    zero-clipped required rate. The second return value records that fraction.
    Sorted draws permit exact empirical CDF evaluation without a huge MC grid.
    """
    draws = np.asarray(sorted_log_mass_draws, dtype=float)
    if draws.ndim != 1 or not draws.size or not np.isfinite(draws).all():
        raise ValueError("Mass draws must be a nonempty finite 1D array")
    if (np.diff(draws) < 0).any():
        raise ValueError("Mass draws must be sorted")
    seed = np.asarray(log_mseed, dtype=float)
    if not np.isfinite(seed).all():
        raise ValueError("Seed masses must be finite")
    _validate_growth_parameters(fedd_cap, epsilon)
    maximum = models.predicted_log_mbh_from_delta_t(
        seed, fedd_cap, epsilon, growth_interval_gyr(z_accretion, z_obs)
    )
    below_seed = np.searchsorted(draws, seed, side="left")
    below_maximum = np.searchsorted(draws, maximum, side="right")
    return (below_maximum - below_seed) / draws.size, below_seed / draws.size

