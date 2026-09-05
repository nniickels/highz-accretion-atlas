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
