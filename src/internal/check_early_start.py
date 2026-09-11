"""Reproduce the appendix's z_start=30 versus 3400 timing comparison.

Uses the manuscript's matter-plus-Lambda cosmology and constant-efficiency
accretion prescription. This is an extrapolation, not a PBH evolution model.
Run from the repository root: .venv/bin/python -m src.internal.check_early_start
"""
import json
import numpy as np
from src import models


def main():
    extra_time = float(models.cosmic_time_gyr(30) - models.cosmic_time_gyr(3400))
    result = {
        "cosmology": "manuscript matter+Lambda; radiation neglected",
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
        later = float(models.available_growth_time_gyr(30, redshift))
        earlier = float(models.available_growth_time_gyr(3400, redshift))
        result["fixed_mass_required_fedd_reduction"].append({
            "observed_redshift": redshift,
            "reduction_percent": 100 * (1 - later / earlier),
        })
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
