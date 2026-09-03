"""Assemble the complete catalogue from retained historical builders.

This module is an internal compatibility bridge. Its inputs have neutral,
role-based names under ``data/assembly``; public datasets are materialized by
``src.internal.process_catalogues``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.internal.compatibility.v7_catalogue import finalize_v7_catalogues
from src.internal.compatibility.v7_core_catalogue import build_v7_base_catalogues
from src.internal.compatibility.v7_scholtz_catalogue import build_v7_scholtz_catalogues
from src.internal.compatibility.v7_uhz1_catalogue import build_v7_uhz1_catalogues
from src.internal.canonical_mass_additions import append_additions
from src.internal.heterogeneous_v3_additions import append_heterogeneous_v3


ROOT = Path(__file__).resolve().parents[3]
INPUTS = {
    "foundation_measurements": ROOT / "data/assembly/blagn_foundation_measurements.csv",
    "ren_table1": ROOT / "data/raw/ren25_alpine_cristal_jwst_table1.csv",
    "ren_table2": ROOT / "data/raw/ren25_alpine_cristal_jwst_table2_observables.csv",
    "uhz1_history": ROOT / "data/raw/uhz1_xray_evidence_history.csv",
    "uhz1_miri": ROOT / "data/raw/zou26_uhz1_miri_table3.csv",
    "scholtz_source": ROOT / "data/raw/scholtz25_jades_narrow_line_agn_zge4.csv",
    "scholtz_correction": ROOT / "data/raw/scholtz25_jades_narrow_line_agn_correction.csv",
    "scholtz_overrides": ROOT / "data/assembly/scholtz_identity_overrides.csv",
    "greene_additions": ROOT / "data/raw/greene24_uncover_blagn_table3.csv",
    "kocevski_additions": ROOT / "data/raw/kocevski25_lrd_blagn_table5_zge4_new.csv",
    "skyfire_additions": ROOT / "data/raw/skyfire26_ceers_blagn_table3_zge4_mass.csv",
    "ceers1019_addition": ROOT / "data/raw/larson23_ceers1019.csv",
    "j0647_addition": ROOT / "data/raw/killi24_j0647_lrd.csv",
    "zs7_addition": ROOT / "data/raw/ubler24_zs7_blagn.csv",
    "gnz11_addition": ROOT / "data/raw/maiolino24_gnz11_agn.csv",
    "heterogeneous_v3_expansion": ROOT / "data/raw/v3_jwst_heterogeneous_expansion.csv",
}
FULL_TABLE = ROOT / "data/raw/scholtz25_jades_table_sample_full.tex"


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(INPUTS[name])


def _normalize_historical_labels(frame: pd.DataFrame) -> pd.DataFrame:
    """Translate release-era prose into canonical dataset-neutral metadata."""
    result = frame.copy()
    replacements = (
        (r"\bno v[4-7] candidate\b", "no previously admitted candidate"),
        ("v7 evidence and conditional-mass fields", "canonical evidence and conditional-mass fields"),
        ("against v7", "against the admitted atlas source set"),
        ("v7 reviewed identity registry", "reviewed identity registry"),
    )
    for field in result.select_dtypes(include=["object", "string"]).columns:
        values = result[field].astype("string")
        for old, new in replacements:
            values = values.str.replace(old, new, regex=True)
        result[field] = values.astype(object).where(values.notna(), pd.NA)
    return result


def build_outputs() -> dict[str, pd.DataFrame]:
    base = build_v7_base_catalogues(
        _read("foundation_measurements"), _read("ren_table1"), _read("ren_table2"),
    )
    uhz1 = build_v7_uhz1_catalogues(
        base["measurements"], base["observables"], base["aliases"],
        _read("uhz1_history"), _read("uhz1_miri"),
    )
    scholtz = build_v7_scholtz_catalogues(
        uhz1["measurements"], uhz1["observables"], uhz1["aliases"],
        _read("scholtz_source"), _read("scholtz_overrides"),
    )
    final = finalize_v7_catalogues(
        scholtz["measurements"], scholtz["observables"], scholtz["aliases"],
        scholtz["reviewed_match_candidates"], _read("scholtz_source"),
        _read("scholtz_correction"), str(FULL_TABLE),
    )
    final["external_literature_identity_audit"] = pd.DataFrame(columns=[
        "catalogue_release", "measurement_id", "object_id", "literature_alias",
        "literature_reference", "atlas_prior_candidate_count",
        "identity_disposition", "review_basis", "review_date",
    ])
    addition_names = [
        "greene_additions", "kocevski_additions", "skyfire_additions",
        "ceers1019_addition", "j0647_addition", "zs7_addition", "gnz11_addition",
    ]
    additions = pd.concat([_read(name) for name in addition_names], ignore_index=True, sort=False)
    final = append_additions(final, additions)
    final = append_heterogeneous_v3(final, _read("heterogeneous_v3_expansion"))
    return {name: _normalize_historical_labels(frame) for name, frame in final.items()}
