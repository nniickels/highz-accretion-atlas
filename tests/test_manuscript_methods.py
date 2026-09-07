"""Check the editorial pass's subset and efficiency claims against canonical data."""
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from src import models

ROOT = Path(__file__).resolve().parents[1]

class ManuscriptMethodTests(unittest.TestCase):
    def test_primary_subset_counts_and_gnz11_caveat(self):
        point = pd.read_csv(ROOT/'results/v3/tables/v3_object_point_ranking.csv')
        errors = pd.read_csv(ROOT/'results/v3/tables/v3_object_uncertainty_ranking.csv')
        primary = point.loc[point.primary_growth_ranking_flag]
        uncertainty = errors.loc[errors.primary_growth_ranking_flag]
        self.assertEqual(len(primary), 227)
        objects = pd.read_csv(ROOT/'data/processed/v3/v3_accreting_objects.csv')
        eligible = objects.growth_ranking_eligible_flag
        declared_primary = (eligible & objects.evidence_status.isin(['secure', 'probable'])
                            & ~objects.conditional_mass_flag
                            & objects.primary_mass_comparison_flag)
        np.testing.assert_array_equal(declared_primary, objects.primary_growth_ranking_flag)
        excluded = objects.loc[eligible & ~declared_primary]
        self.assertEqual(int(excluded.evidence_status.eq('candidate').sum()), 9)
        self.assertEqual(int(excluded.conditional_mass_flag.sum()), 7)
        alternate = pd.read_csv(ROOT/'results/v3/tables/v3_alternate_measurement_sensitivity.csv')
        self.assertEqual((len(alternate), alternate.physical_object_id.nunique()), (7, 6))
        self.assertTrue(alternate.default_required_fedd_seed1e2.lt(1).all())
        self.assertTrue(alternate.alternate_required_fedd_seed1e2.lt(1).all())
        self.assertEqual(int(primary.required_fedd_seed1e2.gt(1).sum()), 12)
        self.assertEqual(int(uncertainty.required_fedd_seed1e2_p16.gt(1).sum()), 8)
        self.assertEqual(int(uncertainty.prob_required_fedd_seed1e2_gt_1.ge(.95).sum()), 6)
        gn = point.loc[point.object_id.eq('GN-z11')].iloc[0]
        self.assertFalse(gn.primary_growth_ranking_flag)
        self.assertEqual(gn.mass_comparability_group, 'virial_uv_single_epoch')

    def test_nonspinning_efficiency_sensitivity_from_independent_scaling(self):
        point = pd.read_csv(ROOT/'results/v3/tables/v3_object_point_ranking.csv')
        epsilon = 1-np.sqrt(8/9)
        factor = epsilon/(1-epsilon)/(.1/.9)
        expected = point.required_fedd_seed1e2.to_numpy()*factor
        actual = models.required_fedd_for_seed(2, point.log_mbh_msun_std,
                                               epsilon, 30, point.redshift)
        np.testing.assert_allclose(actual, expected, rtol=1e-13)
        self.assertEqual(int((actual>1).sum()), 0)
        self.assertEqual(f'{actual.max():.3f}', '0.793')
        self.assertEqual(f'{factor:.5f}', '0.54594')

    def test_seed_and_start_time_sensitivity_counts(self):
        point = pd.read_csv(ROOT/'results/v3/tables/v3_object_point_ranking.csv')
        primary = point.primary_growth_ranking_flag.to_numpy()
        for seed, zseed, expected in [(3, 30, (4, 5)), (5, 30, (0, 0)),
                                      (2, 20, (22, 24))]:
            required = models.required_fedd_for_seed(
                seed, point.log_mbh_msun_std, .1, zseed, point.redshift)
            self.assertEqual((int((required[primary] > 1).sum()),
                              int((required > 1).sum())), expected)
        delayed = models.required_fedd_for_seed(
            2, point.log_mbh_msun_std, .1, 20, point.redshift)
        self.assertEqual(point.iloc[int(np.argmax(delayed))].object_id, 'GN-z11')
        self.assertEqual(f'{delayed.max():.3f}', '1.880')
