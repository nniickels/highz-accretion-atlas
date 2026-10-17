"""Scientific contracts for the five reviewed source families."""

import unittest
import numpy as np
import pandas as pd
from src.internal.october2026_additions import log_interval, source_records, METADATA
from src.internal.compatibility.build_complete_catalogue import INPUTS


class OctoberAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = {
            k: pd.read_csv(v)
            for k, v in INPUTS.items()
            if k.endswith("_expansion")
            or k in {"capers_alternatives", "canucs_variants"}
        }
        cls.rows = {r["source_key"]: r for r in source_records(cls.inputs)}

    def test_linear_endpoints_and_no_second_lens_correction(self):
        expected = {
            "tripodi25_canucs_lrd": (1e8, 6e7, 1.6e8),
            "schindler25_j1007": (1.152e8, 6.89e7, 2.163e8),
            "takechi26_macs0416_y1": (1.6e6, 0.6e6, 4.6e6),
        }
        for key, (center, low, high) in expected.items():
            mass, minus, plus = self.rows[key]["mass"]
            np.testing.assert_allclose(
                [10**mass, 10 ** (mass - minus), 10 ** (mass + plus)],
                [center, low, high],
                rtol=1e-13,
            )
        with self.assertRaises(ValueError):
            log_interval(1.0, 1.0, 2.0)

    def test_one_record_per_new_family_and_correlated_alternatives(self):
        self.assertEqual(len(self.rows), 5)
        self.assertEqual(set(self.rows), set(METADATA))
        self.assertTrue(all(r["object_id"] != "J1007+2115" for r in self.rows.values()))
        # Dust alternatives remain raw rows for one source object, not two admissions.
        self.assertEqual(len(self.inputs["j1007_expansion"]), 2)
        self.assertEqual(
            sum(r["object_id"] == "J1007_AGN" for r in self.rows.values()), 1
        )
        self.assertTrue(np.isnan(self.rows["fudamoto25_sapphires_z847"]["mass"][0]))
        self.assertEqual(
            self.rows["taylor25_capers_lrd_z9"]["mass"], (7.58, 0.15, 0.15)
        )

    def test_membership_and_evidence_are_distinct(self):
        from src.datasets import V2_SOURCES, V3_SOURCES

        catalogue = pd.read_csv("data/processed/v3/v3_accreting_objects.csv").set_index(
            "source_key"
        )
        for key in self.rows:
            self.assertIn(key, V3_SOURCES)
            self.assertEqual(key in V2_SOURCES, not key.startswith("fudamoto"))
        y = catalogue.loc["takechi26_macs0416_y1"]
        self.assertTrue(y.growth_ranking_eligible_flag)
        self.assertFalse(y.primary_growth_ranking_flag)
        self.assertEqual(str(y.lrd_flag).lower(), "false")
        s = catalogue.loc["fudamoto25_sapphires_z847"]
        self.assertFalse(s.growth_ranking_eligible_flag)
        self.assertTrue(pd.isna(s.log_mbh_msun_std))
        self.assertIn("foreground_neighbour_identity_unresolved", s.source_caveat_tags)


if __name__ == "__main__":
    unittest.main()
