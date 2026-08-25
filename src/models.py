"""v1 black-hole growth and interpretation models.

The v1 growth model follows the Dayal-style exponential form used in the
README:

    M_BH(t_obs) = M_seed * exp[
        f_Edd * ((1 - epsilon) / epsilon) * Delta_t / t_Edd
    ]

where ``t_Edd = c sigma_T / (4 pi G m_p) ~= 0.45 Gyr``. Inputs are expressed as
cosmic time in Gyr, masses in log10(Msun), redshifts as dimensionless values,
``f_Edd`` as an average Eddington fraction, and radiative efficiency
``epsilon`` as a fraction in ``0 < epsilon < 1``.

The default cosmology is a flat Planck 2018-style Lambda-CDM cosmology:
``H0 = 67.3 km/s/Mpc``, ``Omega_m = 0.315``, and
``Omega_Lambda = 0.685``.

NaN policy: NaN inputs propagate to NaN outputs so missing catalogue values can
be carried through tables. Finite unphysical inputs, such as negative redshift,
``z_seed <= z_obs``, negative ``f_Edd``, or invalid ``epsilon``, raise
``ValueError`` instead of being silently clipped.
"""

# ---------------------------------- Imports -----------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

# ---------------------------------- Variables ---------------------------------------------------

LN_10 = np.log(10.0)
EDDINGTON_TIME_GYR = 0.45
DEFAULT_H0_KM_S_MPC = 67.3
DEFAULT_OMEGA_M = 0.315
DEFAULT_OMEGA_LAMBDA = 0.685


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

# ------------------------------ Validation helpers ---------------------------------------------


def _as_float_array(value: float | np.ndarray, name: str) -> np.ndarray:
    """Convert an input to a float array with a useful error message."""
    try:
        arr = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc

    if np.isinf(arr).any():
        raise ValueError(f"{name} cannot contain +/-inf")
    return arr


def _finite_mask(arr: np.ndarray) -> np.ndarray:
    """Return True for non-NaN array entries."""
    return ~np.isnan(arr)


def _validate_nonnegative(arr: np.ndarray, name: str) -> None:
    finite = _finite_mask(arr)
    if np.any(finite & (arr < 0.0)):
        raise ValueError(f"{name} must be >= 0 where finite")


def _validate_positive(arr: np.ndarray, name: str) -> None:
    finite = _finite_mask(arr)
    if np.any(finite & (arr <= 0.0)):
        raise ValueError(f"{name} must be > 0 where finite")


def _validate_epsilon(arr: np.ndarray) -> None:
    finite = _finite_mask(arr)
    if np.any(finite & ((arr <= 0.0) | (arr >= 1.0))):
        raise ValueError("epsilon must satisfy 0 < epsilon < 1 where finite")


def _validate_1d_grid(values: np.ndarray, name: str) -> None:
    if values.ndim != 1:
        raise ValueError(f"{name} must be a 1D grid array")
    if values.size == 0:
        raise ValueError(f"{name} cannot be empty")


# ------------------------------ Interpretation helpers -----------------------------------------


def apply_mbh_interpretation(log_mbh_msun: float | np.ndarray, delta_dex: float = 0.0) -> np.ndarray:
    """Shift inferred log BH mass by an interpretation systematic in dex."""
    return _as_float_array(log_mbh_msun, "log_mbh_msun") + float(delta_dex)


def apply_lbol_interpretation(log_lbol_erg_s: float | np.ndarray, delta_dex: float = 0.0) -> np.ndarray:
    """Shift inferred bolometric luminosity by an interpretation systematic in dex."""
    return _as_float_array(log_lbol_erg_s, "log_lbol_erg_s") + float(delta_dex)


def apply_mstar_agn_contamination(
    log_mstar_msun: float | np.ndarray,
    agn_fraction: float,
) -> np.ndarray:
    """Correct host stellar mass for AGN contamination.

    Args:
        log_mstar_msun: Observed host stellar mass in log10(Msun).
        agn_fraction: Fraction of inferred host light attributed to AGN
            contamination. Must satisfy ``0 <= agn_fraction < 1``.

    Returns:
        Corrected log10(Mstar/Msun). NaN stellar masses remain NaN.
    """
    if not (0.0 <= agn_fraction < 1.0):
        raise ValueError("agn_fraction must satisfy 0 <= f < 1")

    mstar_linear = np.power(10.0, _as_float_array(log_mstar_msun, "log_mstar_msun"))
    corrected = mstar_linear * (1.0 - agn_fraction)
    return np.log10(corrected)


# ------------------------------ Cosmology and growth -------------------------------------------


def cosmic_time_gyr(
    redshift: float | np.ndarray,
    h0_km_s_mpc: float = DEFAULT_H0_KM_S_MPC,
    omega_m: float = DEFAULT_OMEGA_M,
    omega_lambda: float = DEFAULT_OMEGA_LAMBDA,
) -> np.ndarray:
    """Return cosmic age in Gyr for redshift in flat matter + Lambda cosmology.

    The closed form is:

        t(z) = 2 / (3 H0 sqrt(Omega_Lambda)) * asinh[
            sqrt(Omega_Lambda / Omega_m) / (1 + z)^(3/2)
        ]

    ``H0`` is converted from km/s/Mpc to s^-1 internally. NaN redshifts
    propagate; finite redshifts must be nonnegative.
    """
    z = _as_float_array(redshift, "redshift")
    _validate_nonnegative(z, "redshift")

    if h0_km_s_mpc <= 0:
        raise ValueError("h0_km_s_mpc must be > 0")
    if omega_m <= 0 or omega_lambda <= 0:
        raise ValueError("omega_m and omega_lambda must be > 0")
    if not np.isclose(omega_m + omega_lambda, 1.0):
        raise ValueError("v1 cosmic_time_gyr assumes a flat cosmology")

    h0_s = h0_km_s_mpc * 1000.0 / 3.0856775814913673e22
    sec_per_gyr = 3.15576e16
    prefactor_gyr = (2.0 / (3.0 * h0_s * np.sqrt(omega_lambda))) / sec_per_gyr
    arg = np.sqrt(omega_lambda / omega_m) / np.power(1.0 + z, 1.5)
    return prefactor_gyr * np.arcsinh(arg)


def available_growth_time_gyr(
    z_seed: float | np.ndarray,
    z_obs: float | np.ndarray,
    h0_km_s_mpc: float = DEFAULT_H0_KM_S_MPC,
    omega_m: float = DEFAULT_OMEGA_M,
    omega_lambda: float = DEFAULT_OMEGA_LAMBDA,
) -> np.ndarray:
    """Return available growth time ``t(z_obs) - t(z_seed)`` in Gyr.

    In v1, seed formation must occur earlier than observation, so finite
    ``z_seed`` values must be greater than finite ``z_obs`` values. NaNs
    propagate.
    """
    seed, obs = np.broadcast_arrays(
        _as_float_array(z_seed, "z_seed"),
        _as_float_array(z_obs, "z_obs"),
    )
    _validate_nonnegative(seed, "z_seed")
    _validate_nonnegative(obs, "z_obs")

    finite_pair = _finite_mask(seed) & _finite_mask(obs)
    if np.any(finite_pair & (seed <= obs)):
        raise ValueError("z_seed must be greater than z_obs for finite pairs")

    return cosmic_time_gyr(obs, h0_km_s_mpc, omega_m, omega_lambda) - cosmic_time_gyr(
        seed,
        h0_km_s_mpc,
        omega_m,
        omega_lambda,
    )


def salpeter_efold_time_gyr(epsilon: float | np.ndarray = 0.1, f_edd: float | np.ndarray = 1.0) -> np.ndarray:
    """Return the e-folding time in Gyr for constant ``epsilon`` and ``f_Edd``.

    This is the inverse of the Dayal-style exponential coefficient:
    ``t_efold = t_Edd * epsilon / ((1 - epsilon) * f_Edd)``.
    """
    eps, fedd = np.broadcast_arrays(
        _as_float_array(epsilon, "epsilon"),
        _as_float_array(f_edd, "f_edd"),
    )
    _validate_epsilon(eps)
    _validate_positive(fedd, "f_edd")
    return EDDINGTON_TIME_GYR * (eps / (1.0 - eps)) / fedd


def thin_disk_radiative_efficiency(spin: float | np.ndarray) -> np.ndarray:
    """Return the ideal thin-disk radiative efficiency for Kerr spin ``a``.

    The calculation uses the specific binding energy at the innermost stable
    circular orbit (ISCO), ``epsilon = 1 - E_ISCO``. Finite spins must lie in
    ``-1 <= a <= 1``; negative values describe retrograde disks and positive
    values prograde disks. The ideal endpoint efficiencies are approximately
    0.038, 0.057, and 0.423 for ``a = -1, 0, +1``, respectively.
    """
    a = _as_float_array(spin, "spin")
    finite = _finite_mask(a)
    if np.any(finite & ((a < -1.0) | (a > 1.0))):
        raise ValueError("spin must satisfy -1 <= a <= 1 where finite")

    z1 = 1.0 + np.cbrt(1.0 - a**2) * (np.cbrt(1.0 + a) + np.cbrt(1.0 - a))
    z2 = np.sqrt(3.0 * a**2 + z1**2)
    r_isco = 3.0 + z2 - np.sign(a) * np.sqrt((3.0 - z1) * (3.0 + z1 + 2.0 * z2))
    e_isco = np.sqrt(1.0 - 2.0 / (3.0 * r_isco))
    return 1.0 - e_isco


def slim_disk_effective_efficiency(
    spin: float | np.ndarray,
    f_edd: float | np.ndarray,
) -> np.ndarray:
    """Return a photon-trapping effective efficiency above Eddington.

    ``thin_disk_radiative_efficiency(spin)`` is retained for ``f_Edd <= 1``.
    Above Eddington, this uses the phenomenological slim-disk luminosity
    relation ``f_Edd = 1 + ln(mdot)``. Since luminosity also scales as
    ``epsilon_eff * mdot``, the resulting efficiency is
    ``epsilon_eff = epsilon_spin * f_Edd / exp(f_Edd - 1)``.

    This is an illustrative coupling for parameter scans, not a full
    relativistic slim-disk or spin-evolution calculation.
    """
    a, fedd = np.broadcast_arrays(
        _as_float_array(spin, "spin"),
        _as_float_array(f_edd, "f_edd"),
    )
    _validate_nonnegative(fedd, "f_edd")
    epsilon_spin = thin_disk_radiative_efficiency(a)
    super_eddington_factor = fedd / np.exp(fedd - 1.0)
    return np.where(fedd <= 1.0, epsilon_spin, epsilon_spin * super_eddington_factor)


def growth_log10_factor(
    f_edd: float | np.ndarray,
    epsilon: float | np.ndarray,
    delta_t_gyr: float | np.ndarray,
) -> np.ndarray:
    """Return the logarithmic mass gain, ``log10(M_final / M_seed)``.

    The physical exponential is in natural-log space; dividing by ``ln(10)``
    converts the e-fold count into dex.
    """
    fedd, eps, delta_t = np.broadcast_arrays(
        _as_float_array(f_edd, "f_edd"),
        _as_float_array(epsilon, "epsilon"),
        _as_float_array(delta_t_gyr, "delta_t_gyr"),
    )
    _validate_nonnegative(fedd, "f_edd")
    _validate_epsilon(eps)
    _validate_nonnegative(delta_t, "delta_t_gyr")

    efolds = fedd * ((1.0 - eps) / eps) * (delta_t / EDDINGTON_TIME_GYR)
    return efolds / LN_10


def predicted_log_mbh_from_delta_t(
    log_mseed: float | np.ndarray,
    f_edd: float | np.ndarray,
    epsilon: float | np.ndarray,
    delta_t_gyr: float | np.ndarray,
    merger_boost: float | np.ndarray = 1.0,
) -> np.ndarray:
    """Predict final log10(M_BH/Msun) from seed mass and elapsed time."""
    log_seed, boost, log_growth = np.broadcast_arrays(
        _as_float_array(log_mseed, "log_mseed"),
        _as_float_array(merger_boost, "merger_boost"),
        growth_log10_factor(f_edd, epsilon, delta_t_gyr),
    )
    _validate_positive(boost, "merger_boost")
    return log_seed + np.log10(boost) + log_growth


def predicted_log_mbh(
    log_mseed: float | np.ndarray,
    f_edd: float | np.ndarray,
    epsilon: float | np.ndarray,
    z_seed: float | np.ndarray,
    z_obs: float | np.ndarray,
    merger_boost: float | np.ndarray = 1.0,
) -> np.ndarray:
    """Predict log10(M_BH/Msun) at ``z_obs`` from a seed at ``z_seed``."""
    delta_t = available_growth_time_gyr(z_seed=z_seed, z_obs=z_obs)
    return predicted_log_mbh_from_delta_t(
        log_mseed=log_mseed,
        f_edd=f_edd,
        epsilon=epsilon,
        delta_t_gyr=delta_t,
        merger_boost=merger_boost,
    )


def required_seed_mass_log10(
    log_mbh_final: float | np.ndarray,
    delta_t_gyr: float | np.ndarray,
    f_edd_avg: float | np.ndarray = 1.0,
    epsilon: float | np.ndarray = 0.1,
    merger_boost: float | np.ndarray = 1.0,
) -> np.ndarray:
    """Compute required seed mass in log10(Msun) for a chosen accretion history."""
    final_mass, boost, log_growth = np.broadcast_arrays(
        _as_float_array(log_mbh_final, "log_mbh_final"),
        _as_float_array(merger_boost, "merger_boost"),
        growth_log10_factor(f_edd_avg, epsilon, delta_t_gyr),
    )
    _validate_positive(boost, "merger_boost")
    return final_mass - np.log10(boost) - log_growth


def required_seed_mass_for_growth(
    log_mbh_final: float | np.ndarray,
    f_edd: float | np.ndarray,
    epsilon: float | np.ndarray,
    z_seed: float | np.ndarray,
    z_obs: float | np.ndarray,
    merger_boost: float | np.ndarray = 1.0,
) -> np.ndarray:
    """Compute required log10 seed mass from redshifts and accretion assumptions."""
    delta_t = available_growth_time_gyr(z_seed=z_seed, z_obs=z_obs)
    return required_seed_mass_log10(
        log_mbh_final=log_mbh_final,
        delta_t_gyr=delta_t,
        f_edd_avg=f_edd,
        epsilon=epsilon,
        merger_boost=merger_boost,
    )


def required_average_fedd(
    log_mseed: float | np.ndarray,
    log_mbh_final: float | np.ndarray,
    delta_t_gyr: float | np.ndarray,
    epsilon: float | np.ndarray = 0.1,
    merger_boost: float | np.ndarray = 1.0,
    *,
    clip_nonnegative: bool = True,
) -> np.ndarray:
    """Solve for average ``f_Edd`` required over ``delta_t_gyr``.

    If ``clip_nonnegative`` is true, cases where the seed plus merger boost
    already exceeds the final mass return 0 rather than a negative accretion
    fraction.
    """
    log_seed, log_final, delta_t, eps, boost = np.broadcast_arrays(
        _as_float_array(log_mseed, "log_mseed"),
        _as_float_array(log_mbh_final, "log_mbh_final"),
        _as_float_array(delta_t_gyr, "delta_t_gyr"),
        _as_float_array(epsilon, "epsilon"),
        _as_float_array(merger_boost, "merger_boost"),
    )
    _validate_positive(delta_t, "delta_t_gyr")
    _validate_epsilon(eps)
    _validate_positive(boost, "merger_boost")

    log_mass_gain = log_final - log_seed - np.log10(boost)
    efolds_needed = log_mass_gain * LN_10
    required = efolds_needed * EDDINGTON_TIME_GYR * eps / ((1.0 - eps) * delta_t)
    if clip_nonnegative:
        return np.maximum(required, 0.0)
    return required


def required_fedd_for_seed(
    log_mseed: float | np.ndarray,
    log_mbh_final: float | np.ndarray,
    epsilon: float | np.ndarray,
    z_seed: float | np.ndarray,
    z_obs: float | np.ndarray,
    merger_boost: float | np.ndarray = 1.0,
    *,
    clip_nonnegative: bool = True,
) -> np.ndarray:
    """Compute required average ``f_Edd`` for chosen seed masses and redshifts."""
    delta_t = available_growth_time_gyr(z_seed=z_seed, z_obs=z_obs)
    return required_average_fedd(
        log_mseed=log_mseed,
        log_mbh_final=log_mbh_final,
        delta_t_gyr=delta_t,
        epsilon=epsilon,
        merger_boost=merger_boost,
        clip_nonnegative=clip_nonnegative,
    )


def two_state_average_fedd(
    duty_cycle: float | np.ndarray,
    burst_fedd: float | np.ndarray,
    quiescent_fedd: float | np.ndarray = 0.0,
) -> np.ndarray:
    """Return the time-weighted mean ``f_Edd`` for a two-state history.

    This effective model assumes the same radiative efficiency and growth
    coefficient in both states. It describes an integrated growth history,
    not an instantaneous light curve.
    """
    duty, burst, quiescent = np.broadcast_arrays(
        _as_float_array(duty_cycle, "duty_cycle"),
        _as_float_array(burst_fedd, "burst_fedd"),
        _as_float_array(quiescent_fedd, "quiescent_fedd"),
    )
    finite = _finite_mask(duty)
    if np.any(finite & ((duty < 0.0) | (duty > 1.0))):
        raise ValueError("duty_cycle must satisfy 0 <= D <= 1 where finite")
    _validate_nonnegative(burst, "burst_fedd")
    _validate_nonnegative(quiescent, "quiescent_fedd")
    finite_states = _finite_mask(burst) & _finite_mask(quiescent)
    if np.any(finite_states & (burst < quiescent)):
        raise ValueError("burst_fedd must be >= quiescent_fedd where finite")
    return duty * burst + (1.0 - duty) * quiescent


def required_duty_cycle(
    required_fedd_avg: float | np.ndarray,
    burst_fedd: float | np.ndarray,
    quiescent_fedd: float | np.ndarray = 0.0,
) -> np.ndarray:
    """Solve the two-state model for the duty cycle required by a mean rate.

    Values above one are intentionally retained: they mark a fixed-burst
    scenario that cannot supply the required lifetime-average growth. Negative
    values are invalid rather than silently clipped.
    """
    required, burst, quiescent = np.broadcast_arrays(
        _as_float_array(required_fedd_avg, "required_fedd_avg"),
        _as_float_array(burst_fedd, "burst_fedd"),
        _as_float_array(quiescent_fedd, "quiescent_fedd"),
    )
    _validate_nonnegative(required, "required_fedd_avg")
    _validate_nonnegative(burst, "burst_fedd")
    _validate_nonnegative(quiescent, "quiescent_fedd")
    finite_states = _finite_mask(burst) & _finite_mask(quiescent)
    if np.any(finite_states & (burst <= quiescent)):
        raise ValueError("burst_fedd must be > quiescent_fedd where finite")
    finite_required = _finite_mask(required) & _finite_mask(quiescent)
    if np.any(finite_required & (required < quiescent)):
        raise ValueError("required_fedd_avg must be >= quiescent_fedd where finite")
    return (required - quiescent) / (burst - quiescent)


def growth_parameter_grid(
    log_mseed_values: float | np.ndarray,
    f_edd_values: float | np.ndarray,
    epsilon: float | np.ndarray,
    z_seed: float | np.ndarray,
    z_obs: float | np.ndarray,
    merger_boost: float | np.ndarray = 1.0,
) -> dict[str, np.ndarray]:
    """Build a 2D grid of predicted log10(M_BH/Msun).

    The returned arrays use ``np.meshgrid(..., indexing="xy")`` so rows map to
    ``f_edd_values`` and columns map to ``log_mseed_values``. This is the shape
    expected by ``imshow``/``contour`` parameter maps.
    """
    log_mseed_axis = _as_float_array(log_mseed_values, "log_mseed_values")
    f_edd_axis = _as_float_array(f_edd_values, "f_edd_values")
    _validate_1d_grid(log_mseed_axis, "log_mseed_values")
    _validate_1d_grid(f_edd_axis, "f_edd_values")
    _validate_nonnegative(f_edd_axis, "f_edd_values")

    log_mseed_grid, f_edd_grid = np.meshgrid(log_mseed_axis, f_edd_axis, indexing="xy")
    predicted = predicted_log_mbh(
        log_mseed=log_mseed_grid,
        f_edd=f_edd_grid,
        epsilon=epsilon,
        z_seed=z_seed,
        z_obs=z_obs,
        merger_boost=merger_boost,
    )

    return {
        "log_mseed_grid": log_mseed_grid,
        "f_edd_grid": f_edd_grid,
        "predicted_log_mbh": predicted,
        "delta_t_gyr": available_growth_time_gyr(z_seed=z_seed, z_obs=z_obs),
    }


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
    """Evaluate whether a seed model can satisfy a target BH mass."""
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


def run_growth_sanity_checks() -> dict[str, float]:
    """Run lightweight equation checks used by the v1 notebook/script path."""
    z_seed = 30.0
    z_obs = 6.0
    epsilon = 0.1
    log_seed = 5.0

    delta_t = float(available_growth_time_gyr(z_seed=z_seed, z_obs=z_obs))
    if delta_t <= 0:
        raise AssertionError("available growth time must be positive")

    no_growth = float(predicted_log_mbh(log_seed, 0.0, epsilon, z_seed, z_obs))
    if not np.isclose(no_growth, log_seed):
        raise AssertionError("zero f_Edd should leave seed mass unchanged")

    merger_only = float(predicted_log_mbh(log_seed, 0.0, epsilon, z_seed, z_obs, merger_boost=2.0))
    if not np.isclose(merger_only, log_seed + np.log10(2.0)):
        raise AssertionError("merger boost should add log10(boost) dex")

    spin_efficiencies = thin_disk_radiative_efficiency(np.array([-1.0, 0.0, 1.0]))
    expected_spin_efficiencies = np.array([0.03774955, 0.05719096, 0.42264973])
    if not np.allclose(spin_efficiencies, expected_spin_efficiencies, atol=1e-7):
        raise AssertionError("thin-disk spin efficiencies failed reference check")

    slim_efficiencies = slim_disk_effective_efficiency(0.0, np.array([1.0, 2.0, 3.0]))
    if not np.isclose(slim_efficiencies[0], spin_efficiencies[1]):
        raise AssertionError("slim-disk efficiency should match thin-disk efficiency at f_Edd=1")
    if not np.all(np.diff(slim_efficiencies) < 0.0):
        raise AssertionError("slim-disk effective efficiency should fall above Eddington")

    predicted = float(predicted_log_mbh(log_seed, 1.0, epsilon, z_seed, z_obs))
    recovered_fedd = float(required_fedd_for_seed(log_seed, predicted, epsilon, z_seed, z_obs))
    recovered_seed = float(required_seed_mass_for_growth(predicted, 1.0, epsilon, z_seed, z_obs))
    if not np.isclose(recovered_fedd, 1.0):
        raise AssertionError("required_fedd_for_seed failed round-trip check")
    if not np.isclose(recovered_seed, log_seed):
        raise AssertionError("required_seed_mass_for_growth failed round-trip check")

    grid = growth_parameter_grid([2.0, 5.0], [0.0, 1.0], epsilon, z_seed, z_obs)
    if grid["predicted_log_mbh"].shape != (2, 2):
        raise AssertionError("growth_parameter_grid returned an unexpected shape")

    return {
        "h0_km_s_mpc": DEFAULT_H0_KM_S_MPC,
        "omega_m": DEFAULT_OMEGA_M,
        "omega_lambda": DEFAULT_OMEGA_LAMBDA,
        "delta_t_z30_to_z6_gyr": delta_t,
        "no_growth_log_mbh": no_growth,
        "merger_boost_x2_dex": merger_only - log_seed,
        "epsilon_spin_minus1": float(spin_efficiencies[0]),
        "epsilon_spin_0": float(spin_efficiencies[1]),
        "epsilon_spin_plus1": float(spin_efficiencies[2]),
        "epsilon_spin0_fedd2_slim": float(slim_efficiencies[1]),
        "epsilon_spin0_fedd3_slim": float(slim_efficiencies[2]),
        "roundtrip_required_fedd": recovered_fedd,
        "roundtrip_required_log_mseed": recovered_seed,
    }
