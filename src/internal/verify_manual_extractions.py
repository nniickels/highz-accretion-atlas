"""Verify the immutable row-level extraction audit."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = ROOT / "data/manual_extraction_audit.csv"
REQUIRED_COLUMNS = (
    "raw_path", "expected_rows", "source_keys", "source_locator", "validation_checks",
    "raw_sha256", "validation_date", "status", "limitations",
)


def load_and_verify_audit(path: Path = AUDIT_PATH) -> pd.DataFrame:
    audit = pd.read_csv(path, dtype=str, keep_default_na=False)
    if tuple(audit.columns) != REQUIRED_COLUMNS or audit.empty:
        raise AssertionError("manual extraction audit does not match its schema")
    if audit.isna().any().any() or (audit == "").any().any() or not audit["raw_path"].is_unique:
        raise AssertionError("manual extraction audit fields and paths must be nonblank and unique")
    for row in audit.itertuples(index=False):
        raw_path = ROOT / row.raw_path
        if not raw_path.is_file():
            raise AssertionError(f"missing audited extraction: {row.raw_path}")
        digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        if digest != row.raw_sha256:
            raise AssertionError(f"audited extraction changed: {row.raw_path}")
        if raw_path.suffix == ".csv":
            frame = pd.read_csv(raw_path, low_memory=False)
            if len(frame) != int(row.expected_rows):
                raise AssertionError(f"row count changed: {row.raw_path}")
            if (
                "measurement_id" in frame
                and raw_path.name != "ren25_alpine_cristal_jwst_table2_observables.csv"
                and frame["measurement_id"].duplicated().any()
            ):
                raise AssertionError(f"duplicate measurement_id in {row.raw_path}")
            if "source_key" in frame and row.source_keys != "historical_mixed_source_layer":
                expected = set(row.source_keys.split(";"))
                if set(frame["source_key"].dropna().astype(str)) != expected:
                    raise AssertionError(f"source-key membership changed: {row.raw_path}")
        elif raw_path.name == "scholtz25_jades_table_sample_full.tex":
            from src.internal.compatibility.v7_scholtz import parse_full_table_membership
            if len(parse_full_table_membership(raw_path)) != int(row.expected_rows):
                raise AssertionError(f"parsed row count changed: {row.raw_path}")
    return audit


def main() -> None:
    audit = load_and_verify_audit()
    print(f"Verified {len(audit)} immutable row-level extraction artifacts")


if __name__ == "__main__":
    main()
