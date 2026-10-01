"""Bound the platform-roundoff allowance without weakening scientific checks."""

import unittest

import pandas as pd

from src.internal.reproduction import assert_frames_semantically_equal


class MinimumSeedReproductionTests(unittest.TestCase):
    def test_observed_linux_roundoff_is_accepted_for_minimum_seeds(self):
        # Exact values from the failed Linux CI run, row 197 of the v4 table.
        columns = [f"log10_minimum_seed_{suffix}"
                   for suffix in ("central", "p5", "p16", "p50", "p84", "p95")]
        stored = pd.DataFrame({name: [0.0081042758892095] for name in columns})
        regenerated = pd.DataFrame({name: [0.0081042758891953] for name in columns})
        assert_frames_semantically_equal(stored, regenerated)

    def test_minimum_seed_changes_larger_than_roundoff_are_rejected(self):
        for name in ("log10_minimum_seed_central", "log10_minimum_seed_p84"):
            with self.subTest(column=name):
                stored = pd.DataFrame({name: [0.0081042758892095]})
                for delta in (2e-13, 1e-8):
                    with self.subTest(delta=delta), self.assertRaises(AssertionError):
                        assert_frames_semantically_equal(stored, stored + delta)

    def test_unrelated_columns_keep_the_original_strict_tolerance(self):
        for name in ("log_mbh_msun", "mass_draw_fraction_within_growth_cap"):
            with self.subTest(column=name), self.assertRaises(AssertionError):
                assert_frames_semantically_equal(
                    pd.DataFrame({name: [0.0081042758892095]}),
                    pd.DataFrame({name: [0.0081042758891953]}),
                )


if __name__ == "__main__":
    unittest.main()
