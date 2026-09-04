"""Regression checks for source-error semantics and publication-version sensitivity."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.internal.verify_primary_source_values import verify_complete_mass_values
from src.internal.assess_baccus_revision import read_published_table

ROOT = Path(__file__).resolve().parents[1]


class MassReviewTests(unittest.TestCase):
    def test_complete_mass_audit_rejects_missing_measurement(self):
        fixture = json.loads((ROOT / 'data/validation/complete_mass_checks.json').read_text())
        fixture['checks'].pop()
        with patch('src.internal.verify_primary_source_values.json.loads', return_value=fixture):
            with self.assertRaisesRegex(AssertionError, 'exactly once'):
                verify_complete_mass_values()

    def test_killi_preserves_published_linear_bounds(self):
        row = pd.read_csv(ROOT / 'data/processed/v3/v3_accreting_measurements.csv').set_index('measurement_id').loc['J06471045_killi24']
        values = 10.0 ** np.array([row.log_mbh_msun_std,
                                  row.log_mbh_msun_std + row.log_mbh_err_plus_std,
                                  row.log_mbh_msun_std - row.log_mbh_err_minus_std])
        np.testing.assert_allclose(values, [8e8, 8.5e8, 7.6e8], rtol=3e-8)
        self.assertNotEqual(row.log_mbh_err_plus_std, row.log_mbh_err_minus_std)

    def test_zs7_calibration_scatter_retained_once(self):
        table = pd.read_csv(ROOT / 'results/v3/tables/v3_object_uncertainty_ranking.csv')
        row = table.loc[table.source_key.eq('ubler24_zs7_offset_blagn')].iloc[0]
        self.assertEqual(row.reported_mass_error_scope, 'includes_source_calibration_scatter')
        self.assertEqual(row.log_mbh_sigma_plus_used, 0.4)
        self.assertEqual(row.log_mbh_sigma_minus_used, 0.4)
        self.assertFalse(row.additional_systematic_scatter_added)
        self.assertNotIn('reported_statistical_errors_sampled', table.columns)

    def test_baccus_published_table_and_sensitivity_scope(self):
        source = read_published_table().loc['GDN_4762_33609']
        np.testing.assert_allclose([source.log_mbh_msun_std, source.log_mbh_err_plus_std, source.log_mbh_err_minus_std], [7.39, .0235, .0223])
        comparison = pd.read_csv(ROOT / 'results/v3/tables/v3_baccus_revision_comparison.csv')
        summary = pd.read_csv(ROOT / 'results/v3/tables/v3_baccus_revision_summary.csv')
        self.assertEqual(comparison.match_status.value_counts().to_dict(), {'exact_id': 44, 'absent_from_published_table': 5})
        self.assertEqual(summary.numerical_objects.tolist(), [237, 237, 232])
        self.assertEqual(summary.top5_required_fedd.nunique(), 1)
        self.assertTrue(summary.point_required_fedd_gt_1.eq(14).all())
