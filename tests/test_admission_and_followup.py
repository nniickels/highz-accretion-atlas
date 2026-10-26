"""Admission completeness and consistent follow-up treatment across source labels."""

from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from src.internal.compatibility.v7_admission import validate_v7_admission
from src.internal.compatibility.v7_science_core import prepare_science_view
from src.science import build_followup_priority, science_context


ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION_FIELDS = (
    "object_class", "evidence_status", "spectroscopic_type", "lensing_status",
    "lensing_mass_correction_status", "mass_comparability_group",
    "host_property_scope", "identity_resolution_status",
)


class AdmissionClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.measurements = pd.read_csv(
            ROOT / "data/processed/v1/v1_accreting_measurements.csv",
        )
        cls.primary_index = cls.measurements.index[
            cls.measurements.primary_growth_ranking_flag
        ][0]

    def test_missing_required_classifications_are_rejected(self):
        for field in CLASSIFICATION_FIELDS:
            for missing in (None, np.nan, pd.NA, "", " "):
                with self.subTest(field=field, missing=repr(missing)):
                    invalid = self.measurements.copy()
                    invalid.loc[self.primary_index, field] = missing
                    with self.assertRaisesRegex(ValueError, field):
                        validate_v7_admission(invalid)

    def test_missing_evidence_cannot_enter_the_science_view(self):
        invalid = self.measurements.copy()
        invalid.loc[self.primary_index, "evidence_status"] = np.nan
        with self.assertRaisesRegex(ValueError, "evidence_status"):
            prepare_science_view(invalid, view="measurement")

    def test_valid_catalogues_still_pass_admission(self):
        for version in ("v1", "v2", "v3"):
            for view in ("measurements", "objects"):
                with self.subTest(version=version, view=view):
                    validate_v7_admission(pd.read_csv(
                        ROOT / f"data/processed/{version}/{version}_accreting_{view}.csv",
                    ))


class FollowupQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.objects = pd.read_csv(ROOT / "data/processed/v3/v3_accreting_objects.csv")
        cls.point = pd.read_csv(ROOT / "results/v3/tables/v3_object_point_ranking.csv")
        cls.uncertainty = pd.read_csv(
            ROOT / "results/v3/tables/v3_object_uncertainty_ranking.csv",
        )

    def build(self, objects=None, point=None):
        with science_context("v3"):
            return build_followup_priority(
                self.objects if objects is None else objects,
                self.point if point is None else point, self.uncertainty,
            )

    def test_secure_and_robust_quality_labels_give_identical_priorities(self):
        normalized = self.objects.copy()
        normalized.loc[normalized.quality_flag.eq("secure"), "quality_flag"] = "robust"
        pd.testing.assert_frame_equal(
            self.build().drop(columns="quality_flag"),
            self.build(normalized).drop(columns="quality_flag"),
        )

    def test_secure_primary_targets_receive_robust_high_pressure_priority(self):
        result = self.build().set_index("object_id")
        for name in ("CAPERS-LRD-z9", "CANUCS-LRD-z8.6", "J1007_AGN"):
            with self.subTest(object_id=name):
                self.assertEqual(
                    result.loc[name, "followup_priority_category"], "A_robust_high_pressure",
                )
        self.assertEqual(result.loc["CAPERS-LRD-z9", "rank_followup_global_navigation"], 1)

    def test_secure_medium_pressure_target_is_a_comparison_anchor(self):
        point = self.point.copy()
        target_id = self.objects.loc[
            self.objects.object_id.eq("CAPERS-LRD-z9"), "physical_object_id",
        ].item()
        point.loc[point.physical_object_id.eq(target_id), "growth_pressure_tier"] = "medium"
        result = self.build(point=point).set_index("object_id")
        self.assertEqual(
            result.loc["CAPERS-LRD-z9", "followup_priority_category"], "E_comparison_anchor",
        )

    def test_quality_does_not_override_eligibility_or_source_consistency(self):
        target = self.objects.object_id.eq("CAPERS-LRD-z9")
        target_id = self.objects.loc[target, "physical_object_id"].item()
        for eligible, primary, consistency, expected in (
            (False, False, "consistent", "not_ranked_no_canonical_mass"),
            (True, False, "consistent", "B_caveated_high_pressure"),
            (True, True, "inconsistent", "C_source_consistency"),
        ):
            with self.subTest(category=expected):
                objects, point = self.objects.copy(), self.point.copy()
                objects.loc[target, "growth_ranking_eligible_flag"] = eligible
                objects.loc[target, "primary_growth_ranking_flag"] = primary
                point.loc[point.physical_object_id.eq(target_id), "edd_ratio_consistency_flag"] = consistency
                result = self.build(objects, point).set_index("object_id")
                self.assertEqual(result.loc["CAPERS-LRD-z9", "followup_priority_category"], expected)


if __name__ == "__main__":
    unittest.main()
