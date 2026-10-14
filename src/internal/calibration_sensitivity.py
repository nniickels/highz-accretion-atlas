"""Targeted calibration-scatter sensitivity; does not replace reported-error results."""
from __future__ import annotations

from math import hypot, isclose
from statistics import NormalDist
import pandas as pd

# These two primary-tail measurements report a separate, omitted 0.5-dex scale.
# GN-38509 and ZS7 already include calibration scatter: do not add it again.
TARGETS = {
    'RUBIES-EGS-55604': 'RUBIESEGS55604_kocevski25',
    'J0910_2028_12910': 'J0910202812910_baccus26',
}


def probability_above_threshold(margin_dex, reported_sigma_dex, added_sigma_dex):
    """Exact normal tail for independent zero-mean Gaussian log-mass errors."""
    if reported_sigma_dex <= 0 or added_sigma_dex < 0:
        raise ValueError('Require positive reported scatter and nonnegative added scatter')
    return NormalDist().cdf(margin_dex / hypot(reported_sigma_dex, added_sigma_dex))


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
        sigma = float(obj.log_mbh_err_plus_std)
        if not isclose(sigma, obj.log_mbh_err_minus_std, rel_tol=0, abs_tol=1e-12):
            raise ValueError('Analytic calculation requires symmetric reported errors')
        added = float(obj.log_mbh_systematic_dex)
        if not isclose(added, .5, rel_tol=0, abs_tol=1e-12):
            raise ValueError('Separate calibration scale differs from reviewed source value')
        for offset in (0., -.5):
            margin = float(obj.mass_reduction_to_f1_dex) + offset
            rows.append(dict(object_id=name, measurement_id=measurement,
                source_key=obj.source_key, mass_offset_dex=offset,
                reported_sigma_dex=sigma, added_sigma_dex=added,
                combined_sigma_dex=hypot(sigma, added),
                margin_above_critical_mass_dex=margin,
                probability_reported_exact=probability_above_threshold(margin, sigma, 0),
                probability_with_calibration=probability_above_threshold(margin, sigma, added),
                assumption='independent_zero_mean_gaussian_0.5dex',
                scope='two_primary_tail_objects_only'))
    return pd.DataFrame(rows)


def main():
    """Allow the supplementary copy to run without the repository package."""
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
