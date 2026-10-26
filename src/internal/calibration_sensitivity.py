"""Targeted calibration-scatter sensitivity; does not replace reported-error results."""
from __future__ import annotations

from math import hypot, isclose, isfinite
from statistics import NormalDist
import numpy as np
import pandas as pd

# These primary-tail measurements report separate, omitted calibration scales.
# GN-38509 and ZS7 already include calibration scatter: do not add it again.
TARGETS = {
    'RUBIES-EGS-55604': 'RUBIESEGS55604_kocevski25',
    'J0910_2028_12910': 'J0910202812910_baccus26',
    'J1007_AGN': 'J1007AGN_schindler25_observed',
}


def probability_above_threshold(margin_dex, reported_sigma_dex, added_sigma_dex):
    """Exact normal tail for independent zero-mean Gaussian log-mass errors."""
    if reported_sigma_dex <= 0 or added_sigma_dex < 0:
        raise ValueError('Require positive reported scatter and nonnegative added scatter')
    return NormalDist().cdf(margin_dex / hypot(reported_sigma_dex, added_sigma_dex))


def asymmetric_probability_above_threshold(margin_dex, sigma_plus, sigma_minus,
                                           added_sigma_dex, *, order=96):
    """Convolve equal-side half-normal log errors with independent normal scatter.

    Integrate each half over 0--10 standard deviations with Gauss--Legendre
    quadrature; the omitted total half-normal tail is below 2e-23. Symmetric
    errors retain the exact normal result. With no added scatter, use the
    exact piecewise half-normal tail. The added scale is an assumed Gaussian
    standard deviation, not an inferred calibration posterior.
    """
    if (not all(isfinite(x) for x in (margin_dex, sigma_plus, sigma_minus, added_sigma_dex))
            or min(sigma_plus, sigma_minus) <= 0 or added_sigma_dex < 0):
        raise ValueError('Require finite margin, positive errors and nonnegative calibration scatter')
    if sigma_plus == sigma_minus:
        return probability_above_threshold(margin_dex, sigma_plus, added_sigma_dex)
    if added_sigma_dex == 0:
        scale = sigma_minus if margin_dex >= 0 else sigma_plus
        return NormalDist().cdf(margin_dex / scale)
    nodes, weights = np.polynomial.legendre.leggauss(order)
    x = 5 * (nodes + 1)
    density = np.exp(-x*x/2) / np.sqrt(2*np.pi)
    normal = NormalDist()
    upper = np.array([normal.cdf(float(v)) for v in
                      (margin_dex + sigma_plus*x) / added_sigma_dex])
    lower = np.array([normal.cdf(float(v)) for v in
                      (margin_dex - sigma_minus*x) / added_sigma_dex])
    return float(np.dot(5 * weights * density, upper + lower))


def build_calibration_sensitivity(tail):
    """Use the same critical mass as the reference 100-Msun, z=30 growth model."""
    rows = []
    for name, measurement in TARGETS.items():
        subset = tail.loc[tail.object_id.eq(name)]
        if len(subset) != 1:
            raise ValueError(f'Expected exactly one primary-tail measurement for {name}')
        obj = subset.iloc[0]
        if obj.measurement_id != measurement:
            raise ValueError(f'Calibration assumption needs review for {name}')
        plus = float(obj.log_mbh_err_plus_std)
        minus = float(obj.log_mbh_err_minus_std)
        symmetric = plus == minus
        added = float(obj.log_mbh_systematic_dex)
        expected_scale = .43 if name == 'J1007_AGN' else .5
        if not isclose(added, expected_scale, rel_tol=0, abs_tol=1e-12):
            raise ValueError('Separate calibration scale differs from reviewed source value')
        for offset in (0., -.5):
            margin = float(obj.mass_reduction_to_f1_dex) + offset
            rows.append(dict(object_id=name, measurement_id=measurement,
                source_key=obj.source_key, mass_offset_dex=offset,
                reported_sigma_dex=plus if symmetric else np.nan,
                reported_sigma_plus_dex=plus, reported_sigma_minus_dex=minus,
                added_sigma_dex=added,
                combined_sigma_dex=hypot(plus, added) if symmetric else np.nan,
                margin_above_critical_mass_dex=margin,
                probability_reported_exact=asymmetric_probability_above_threshold(margin, plus, minus, 0),
                probability_with_calibration=asymmetric_probability_above_threshold(margin, plus, minus, added),
                assumption='independent_zero_mean_gaussian_calibration',
                integration_method='exact_normal' if symmetric else 'half_normal_quadrature_96',
                scope='three_primary_tail_objects_only'))
    return pd.DataFrame(rows)


def main():
    """Run the sensitivity calculation without importing the repository package."""
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Reference target_robustness.csv')
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--output', type=Path, help='Write the additional sensitivity table')
    action.add_argument('--verify', type=Path, help='Compare against an existing sensitivity table')
    args = parser.parse_args()
    generated = build_calibration_sensitivity(pd.read_csv(args.input))
    if args.output:
        generated.to_csv(args.output, index=False)
    else:
        pd.testing.assert_frame_equal(pd.read_csv(args.verify), generated,
                                      check_exact=False, rtol=1e-13, atol=1e-14)
        print('Verified calibration sensitivity from the supplied reference table.')


if __name__ == '__main__':
    main()
