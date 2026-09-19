"""Reproduce the appendix's z_start=30 versus 3400 timing comparison.

Includes radiation in the supplementary cosmology and retains the
constant-efficiency accretion prescription. This is not a PBH evolution model.
Run from the repository root: .venv/bin/python -m src.internal.check_early_start
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src import models
from src.internal.early_start_cosmology import cosmic_time_gyr, OMEGA_R, OMEGA_LAMBDA


def reference_cosmology_sensitivity():
    """Reproduce the main paper's radiation sensitivity with fixed mass draws."""
    root = Path(__file__).resolve().parents[2]
    tables = root / 'results/manuscript/tables'
    selection = pd.read_csv(tables / 'publication_object_selection.csv')
    objects = pd.read_csv(root / 'data/processed/v3/v3_accreting_objects.csv')
    sample = objects.merge(selection[
        ['physical_object_id', 'publication_primary_flag', 'publication_exploratory_flag']
    ], on='physical_object_id', validate='one_to_one')
    sample = sample.loc[sample.publication_exploratory_flag]

    def rate_ratio(redshift):
        old_time = models.cosmic_time_gyr(redshift) - models.cosmic_time_gyr(30)
        new_time = cosmic_time_gyr(redshift) - cosmic_time_gyr(30)
        return old_time / new_time

    ratio = rate_ratio(sample.redshift)
    required = models.required_fedd_for_seed(
        2, sample.log_mbh_msun_std, .1, 30, sample.redshift
    ) * ratio
    ceers = pd.read_csv(tables / 'target_robustness.csv').set_index('object_id').loc['CEERS-00717']
    direct = pd.read_csv(tables / 'external_direct_mass_comparison.csv')
    dynamical = direct.set_index('comparison').loc['external_dynamical']
    return {
        'required_ratio_increase_percent_range': [
            float(100 * (ratio.min() - 1)), float(100 * (ratio.max() - 1)),
        ],
        'radiation_included_counts_above_unity': {
            'primary': int(np.sum((required > 1) & sample.publication_primary_flag)),
            'expanded': int(np.sum(required > 1)),
        },
        'ceers_00717_sampled_p16': {
            'matter_lambda': float(ceers.p16),
            'with_radiation': float(ceers.p16 * rate_ratio(ceers.redshift)),
        },
        'a2744_qso1_dynamical_required_ratio': {
            'matter_lambda': float(dynamical.required_fedd),
            'with_radiation': float(dynamical.required_fedd * rate_ratio(dynamical.redshift)),
        },
    }


def main():
    extra_time = float(cosmic_time_gyr(30) - cosmic_time_gyr(3400))
    result = {
        "cosmology": "flat matter+radiation+Lambda; z_eq=3400",
        "omega_r": OMEGA_R,
        "omega_lambda": OMEGA_LAMBDA,
        "extra_growth_time_myr": 1000 * extra_time,
        "fixed_fedd_1_mass_shift": [],
        "fixed_mass_required_fedd_reduction": [],
    }
    for epsilon in (0.1, 1 - np.sqrt(8 / 9)):
        dex = float(models.growth_log10_factor(1, epsilon, extra_time))
        result["fixed_fedd_1_mass_shift"].append({
            "epsilon": float(epsilon), "dex": dex, "mass_factor": 10 ** dex,
        })
    for redshift in (4, 7, 10.603):
        later = float(cosmic_time_gyr(redshift) - cosmic_time_gyr(30))
        earlier = float(cosmic_time_gyr(redshift) - cosmic_time_gyr(3400))
        result["fixed_mass_required_fedd_reduction"].append({
            "observed_redshift": redshift,
            "reduction_percent": 100 * (1 - later / earlier),
        })
    result['reference_cosmology_sensitivity'] = reference_cosmology_sensitivity()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
