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
from src.internal.compatibility.v7_gnirs_catalogue import build_v7_gnirs_catalogues
from src.internal.compatibility.v7_scholtz_catalogue import build_v7_scholtz_catalogues
from src.internal.compatibility.v7_uhz1_catalogue import build_v7_uhz1_catalogues
from src.internal.compatibility.v7_xqr_catalogue import build_v7_xqr_catalogues


ROOT = Path(__file__).resolve().parents[3]
INPUTS = {
    "foundation_measurements": ROOT / "data/assembly/blagn_foundation_measurements.csv",
    "ren_table1": ROOT / "data/raw/ren25_alpine_cristal_jwst_table1.csv",
    "ren_table2": ROOT / "data/raw/ren25_alpine_cristal_jwst_table2_observables.csv",
    "xqr_table": ROOT / "data/raw/xqr30_mazzucchelli23_table1.csv",
    "xqr_coordinates": ROOT / "data/raw/xqr30_dodorico23_coordinates.csv",
    "xqr_overrides": ROOT / "data/assembly/xqr30_identity_overrides.csv",
    "xqr_audit": ROOT / "data/assembly/xqr30_external_identity_audit.csv",
    "gnirs_sample": ROOT / "data/raw/shen19_gnirs_table1.csv",
    "gnirs_catalogue": ROOT / "data/raw/shen19_gnirs_table3.csv",
    "gnirs_overrides": ROOT / "data/assembly/gnirs50_identity_overrides.csv",
    "uhz1_history": ROOT / "data/raw/uhz1_xray_evidence_history.csv",
    "uhz1_miri": ROOT / "data/raw/zou26_uhz1_miri_table3.csv",
    "scholtz_source": ROOT / "data/raw/scholtz25_jades_narrow_line_agn_zge4.csv",
    "scholtz_correction": ROOT / "data/raw/scholtz25_jades_narrow_line_agn_correction.csv",
    "scholtz_overrides": ROOT / "data/assembly/scholtz_identity_overrides.csv",
}
FULL_TABLE = ROOT / "data/raw/scholtz25_jades_table_sample_full.tex"


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(INPUTS[name])


def _normalize_historical_labels(frame: pd.DataFrame) -> pd.DataFrame:
    """Translate release-era prose into canonical dataset-neutral metadata."""
    result = frame.copy()
    replacements = (
        (r"\bno v[4-7] candidate\b", "no previously admitted candidate"),
        ("v7 XQR-30 measurement", "XQR-30 measurement"),
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
    xqr = build_v7_xqr_catalogues(
        base["measurements"], base["observables"], _read("xqr_table"),
        _read("xqr_coordinates"), _read("xqr_overrides"), _read("xqr_audit"),
    )
    gnirs = build_v7_gnirs_catalogues(
        xqr["measurements"], xqr["observables"], xqr["aliases"],
        _read("gnirs_sample"), _read("gnirs_catalogue"), _read("gnirs_overrides"),
    )
    uhz1 = build_v7_uhz1_catalogues(
        gnirs["measurements"], gnirs["observables"], gnirs["aliases"],
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
    final["external_literature_identity_audit"] = xqr[
        "external_literature_identity_audit"
    ].assign(catalogue_release="v7-accreting-atlas-catalogue")
    return {name: _normalize_historical_labels(frame) for name, frame in final.items()}
