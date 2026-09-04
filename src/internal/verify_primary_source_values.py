"""Compare catalogue values with independently retrieved primary-source cells.

The fixture records its exact scope; these checks do not certify unreviewed
sources. It is independent of the production catalogue assembly adapters.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CHECKS = ROOT / "data/validation/primary_source_checks.json"


def verify_primary_source_values() -> int:
    reference = json.loads(CHECKS.read_text())
    frames = {}
    failures = []
    for item in reference["checks"]:
        path = item["path"]
        if path not in frames:
            frames[path] = pd.read_csv(ROOT / path, low_memory=False)
        frame = frames[path]
        rows = frame.loc[frame[item["key_column"]].eq(item["key"])]
        label = f"{path}: {item['key']} / {item['column']}"
        if len(rows) != 1 or item["column"] not in frame:
            failures.append(f"{label}: missing column or nonunique row")
            continue
        actual = rows.iloc[0][item["column"]]
        expected = item["expected"]
        if expected is None:
            matches = pd.isna(actual)
        elif isinstance(expected, (int, float)):
            matches = pd.notna(actual) and np.isclose(float(actual), expected, rtol=0, atol=1e-10)
        else:
            matches = pd.notna(actual) and str(actual) == expected
        if not matches:
            failures.append(f"{label}: {actual!r} != source value {expected!r}")
    anchors = json.loads((ROOT / "data/validation/primary_family_anchors.json").read_text())["anchors"]
    catalogue = pd.read_csv(ROOT / "data/processed/v3/v3_accreting_measurements.csv", low_memory=False)
    registry = pd.read_csv(ROOT / "data/source_provenance_registry.csv")
    primary = registry.loc[registry.source_role.eq("primary_measurement")].set_index("source_key")
    # These four families are independently checked by the table fixture above.
    source_map = {"cosmos": "lin25_cosmos3d_blagn", "nexus": "zhuang25_nexus_wfss",
                  "jades": "juodzbalis25_jades_blagn", "seven": "napolitano25_seven_wonders"}
    covered = {source_map[item["source"]] for item in reference["checks"]}
    anchor_count = 0
    for item in anchors:
        key = item["source_key"]
        covered.add(key)
        for field in ("source_url", "source_archive_sha256", "source_member", "source_member_sha256", "locator", "evidence"):
            if not item.get(field):
                failures.append(f"{key}: missing anchor provenance {field}")
        if key not in primary.index or item["source_archive_sha256"] != primary.loc[key, "source_archive_sha256"]:
            failures.append(f"{key}: anchor archive does not match registered measurement version")
        rows = catalogue.loc[catalogue.measurement_id.eq(item["measurement_id"]) & catalogue.source_key.eq(key)]
        if len(rows) != 1 or not item["expected"]:
            failures.append(f"{key}: missing/nonunique anchor or no expected values")
            continue
        for column, expected in item["expected"].items():
            anchor_count += 1
            actual = rows.iloc[0].get(column, "MISSING_COLUMN")
            matches = pd.isna(actual) if expected is None else isinstance(actual, (int, float, np.number)) and pd.notna(actual) and np.isclose(actual, expected, rtol=0, atol=1e-8)
            if not matches:
                failures.append(f"{item['measurement_id']} / {column}: {actual!r} != source value {expected!r}")
    required = set(catalogue.source_key)
    if covered != required:
        failures.append(f"Source-family coverage differs: missing={sorted(required-covered)}, unexpected={sorted(covered-required)}")
    if failures:
        raise AssertionError("Primary-source mismatches:\n" + "\n".join(failures))
    return len(reference["checks"]) + anchor_count


def main() -> None:
    print(f"Verified {verify_primary_source_values()} independent primary-source value checks")


if __name__ == "__main__":
    main()
