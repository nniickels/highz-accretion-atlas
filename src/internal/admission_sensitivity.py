"""Correlated source-model alternatives for newly admitted Balmer objects.

These fixed-assumption comparisons neither add measurements nor reinterpret
assumed-Eddington bounds as independent growth evidence.
"""

from pathlib import Path
import pandas as pd
from src.models import required_fedd_for_seed
from src.internal.october2026_additions import log_interval

ROOT = Path(__file__).resolve().parents[2]


def build_source_model_sensitivity(root=ROOT):
    rows = []

    def add(name, label, z, mass, minus, plus, location, assumption):
        rows.append(
            dict(
                object_id=name,
                alternative=label,
                redshift=z,
                log_mbh=mass,
                log_error_minus=minus,
                log_error_plus=plus,
                required_fedd=float(required_fedd_for_seed(2, mass, 0.1, 30, z)),
                seed_log_mass=2.0,
                seed_redshift=30.0,
                epsilon=0.1,
                merger_boost=1.0,
                independent_object=False,
                assumption=assumption,
                source_location=location,
            )
        )

    capers = pd.read_csv(root / "data/raw/capers_lrd_z9_v4_mass_alternatives.csv")
    capers_redshift = float(
        pd.read_csv(root / "data/raw/capers_lrd_z9_v4_properties.csv").iloc[0].redshift
    )
    for r in capers.itertuples():
        if r.censoring != "detection":
            continue
        add(
            r.object_id,
            r.estimate,
            capers_redshift,
            r.log_mbh_msun,
            r.reported_error_dex,
            r.reported_error_dex,
            r.source_locator,
            r.assumptions,
        )
    j = pd.read_csv(root / "data/raw/schindler25_j1007_agn_mass_alternatives.csv")
    for r in j.itertuples():
        mass, minus, plus = log_interval(
            r.mass_1e7_msun * 1e7,
            r.mass_err_minus_1e7_msun * 1e7,
            r.mass_err_plus_1e7_msun * 1e7,
        )
        add(
            r.object_id,
            r.dust_treatment,
            r.redshift,
            mass,
            minus,
            plus,
            r.source_location,
            "Correlated same-spectrum dust interpretation; no sample-membership replacement",
        )
    return pd.DataFrame(rows)
