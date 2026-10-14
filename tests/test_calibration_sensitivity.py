"""Check analytic uncertainty propagation and avoid adding scatter twice."""
import unittest
from math import sqrt
from statistics import NormalDist
import numpy as np
from src.internal.calibration_sensitivity import probability_above_threshold
from src.internal.publication_selection import build_publication_outputs


class CalibrationSensitivityTests(unittest.TestCase):
    def test_gaussian_convolution_matches_independent_draws(self):
        rng = np.random.default_rng(42)
        draws = .33 + rng.normal(0, .01, 200000) + rng.normal(0, .5, 200000)
        analytic = probability_above_threshold(.33, .01, .5)
        self.assertAlmostEqual(analytic, np.mean(draws > 0), delta=.004)
        self.assertEqual(probability_above_threshold(0, .1, .5), .5)
        self.assertAlmostEqual(probability_above_threshold(.2, .1, 0), NormalDist().cdf(2))

    def test_target_scope_and_baseline_are_preserved(self):
        outputs = build_publication_outputs()
        table = outputs['calibration_sensitivity']
        self.assertEqual(set(table.object_id), {'RUBIES-EGS-55604', 'J0910_2028_12910'})
        self.assertEqual(len(table), 4)
        # GN-38509 and ZS7 must not receive a second calibration contribution.
        self.assertFalse(table.object_id.isin(['GN-38509', 'ZS7']).any())
        j = table.loc[(table.object_id == 'J0910_2028_12910') & (table.mass_offset_dex == 0)].iloc[0]
        self.assertTrue(.74 < j.probability_with_calibration < .75)
        rubies = table.loc[(table.object_id == 'RUBIES-EGS-55604') & (table.mass_offset_dex == -.5)].iloc[0]
        self.assertTrue(.97 < rubies.probability_with_calibration < .99)
        self.assertAlmostEqual(rubies.combined_sigma_dex, sqrt(.1**2 + .5**2))
        self.assertEqual(int(outputs['target_robustness'].probability_gt_1.ge(.95).sum()), 5)
        self.assertEqual(int(outputs['publication_object_selection'].publication_primary_flag.sum()), 220)


if __name__ == '__main__':
    unittest.main()
