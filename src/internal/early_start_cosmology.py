"""Radiation-inclusive cosmic ages for the supplementary onset comparison.

The main catalogue retains its matter-plus-Lambda cosmology. Here the chosen
matter-radiation equality redshift fixes Omega_r, and flatness fixes Omega_Lambda.
"""
from functools import lru_cache

import numpy as np

H0_KM_S_MPC = 67.3
OMEGA_M = 0.315
EQUALITY_REDSHIFT = 3400.0
OMEGA_R = OMEGA_M / (1.0 + EQUALITY_REDSHIFT)
OMEGA_LAMBDA = 1.0 - OMEGA_M - OMEGA_R
H0_GYR_INVERSE = H0_KM_S_MPC / 3.0856775814913673e19 * 31557600.0 * 1e9


@lru_cache(maxsize=4)
def _quadrature(order):
    return np.polynomial.legendre.leggauss(order)


def cosmic_time_gyr(redshift, *, quadrature_order=128):
    """Integrate dt/da from a=0 to a=1/(1+z), in Gyr."""
    z = np.asarray(redshift, dtype=float)
    if not np.isfinite(z).all() or (z < 0).any():
        raise ValueError("redshift must be finite and non-negative")
    nodes, weights = _quadrature(quadrature_order)
    upper = 1.0 / (1.0 + z)
    a = upper[..., None] * (nodes + 1.0) / 2.0
    integrand = a / np.sqrt(OMEGA_R + OMEGA_M * a + OMEGA_LAMBDA * a**4)
    return upper / (2.0 * H0_GYR_INVERSE) * np.sum(integrand * weights, axis=-1)
