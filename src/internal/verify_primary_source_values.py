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
    if failures:
        raise AssertionError("Primary-source mismatches:\n" + "\n".join(failures))
    return len(reference["checks"])


def main() -> None:
    print(f"Verified {verify_primary_source_values()} independent primary-source value checks")


if __name__ == "__main__":
    main()
