"""Cross-platform comparisons for deterministically generated CSV products."""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_float_dtype, is_integer_dtype


NUMERIC_RTOL = 1e-13
NUMERIC_ATOL = 1e-14
# The legacy great-circle calculation uses arccos near one, where platform
# libm implementations can differ through cancellation at sub-milliarcsecond
# scale.  This remains 5,000 times smaller than the 0.5-arcsec candidate cut.
COLUMN_ATOL = {"separation_arcsec": 1e-4}


def csv_round_trip(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply the same CSV parsing semantics used for checked-in products."""
    return pd.read_csv(io.StringIO(frame.to_csv(index=False)))


def assert_frames_semantically_equal(
    expected: pd.DataFrame,
    actual: pd.DataFrame,
    *,
    label: str = "generated CSV",
    rtol: float = NUMERIC_RTOL,
    atol: float = NUMERIC_ATOL,
) -> None:
    """Compare structure/text exactly and floating values at cross-platform tolerance."""
    if list(expected.columns) != list(actual.columns):
        raise AssertionError(f"{label}: column order or membership differs")
    if expected.shape != actual.shape:
        raise AssertionError(
            f"{label}: shape differs: expected {expected.shape}, found {actual.shape}"
        )

    expected = expected.reset_index(drop=True)
    actual = actual.reset_index(drop=True)
    for column in expected.columns:
        expected_values = expected[column]
        actual_values = actual[column]
        try:
            if is_float_dtype(expected_values.dtype) and is_float_dtype(actual_values.dtype):
                column_atol = max(atol, COLUMN_ATOL.get(column, 0.0))
                np.testing.assert_allclose(
                    expected_values.to_numpy(), actual_values.to_numpy(),
                    rtol=rtol, atol=column_atol, equal_nan=True,
                )
            elif (
                (is_integer_dtype(expected_values.dtype) or is_bool_dtype(expected_values.dtype))
                and (is_integer_dtype(actual_values.dtype) or is_bool_dtype(actual_values.dtype))
            ):
                pd.testing.assert_series_equal(
                    expected_values, actual_values, check_dtype=False, check_exact=True,
                )
            else:
                pd.testing.assert_series_equal(
                    expected_values, actual_values, check_dtype=False, check_exact=True,
                )
        except AssertionError as error:
            raise AssertionError(f"{label}: column {column!r} differs: {error}") from error


def assert_csv_reproduction(expected_path: Path, actual_frame: pd.DataFrame) -> None:
    """Compare a checked-in CSV with an independently rebuilt DataFrame."""
    expected = pd.read_csv(expected_path)
    actual = csv_round_trip(actual_frame)
    assert_frames_semantically_equal(expected, actual, label=str(expected_path))
