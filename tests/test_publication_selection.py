"""Conservative exclusions must be complete and cannot certify identity resolution."""
import json
import unittest
from unittest.mock import patch
import pandas as pd
from src.internal.publication_selection import ROOT, POLICY, build_publication_outputs, verify_publication_selection

class PublicationSelectionTests(unittest.TestCase):
    def test_exclusions_preserve_headlines_without_claiming_resolved_identities(self):
        result = verify_publication_selection()
        self.assertEqual(result['scientific_identity_status'], 'open')
        self.assertEqual(result['excluded_object_records'], 6)
        self.assertEqual(result['publication_primary_objects'], 224)
        self.assertEqual(result['publication_exploratory_objects'], 234)
        outputs = build_publication_outputs()
        s = outputs['identity_exclusion_sensitivity']
        before = s.loc[s.scope.eq('catalogue')].set_index(['sample','scenario'])
        after = s.loc[s.scope.eq('publication')].set_index(['sample','scenario'])
        for field in ['above_unity', 'top_five', 'p16_above_unity', 'probability_ge_095']:
            pd.testing.assert_series_equal(before[field], after[field])
        excluded = outputs['publication_object_selection'].query('excluded_identity_flag')
        self.assertEqual(set(excluded.physical_object_id), {
            'HZA-GDS-1210-9515','HZA-GS-8083','HZA-GS-10013704',
            'HZA-JADES-NS-GS00099671','HZA-JADES-NS-GS00016745','HZA-JADES-NS-GS00208643'})

    def test_omitting_an_open_group_is_rejected(self):
        policy = json.loads((ROOT/POLICY).read_text())
        policy['groups'].pop()
        with self.assertRaisesRegex(AssertionError, 'every open group'):
            build_publication_outputs(policy=policy)

    def test_omitting_a_measurement_from_a_group_is_rejected(self):
        policy = json.loads((ROOT/POLICY).read_text())
        policy['groups'][0]['measurement_ids'].pop()
        with self.assertRaisesRegex(AssertionError, 'every open group'):
            build_publication_outputs(policy=policy)

    def test_stored_publication_membership_cannot_readmit_an_excluded_object(self):
        original = pd.read_csv
        def changed(path, *args, **kwargs):
            frame = original(path, *args, **kwargs)
            if str(path).endswith('publication_object_selection.csv'):
                frame.loc[frame.physical_object_id.eq('HZA-GS-8083'), 'publication_primary_flag'] = True
            return frame
        with patch('src.internal.publication_selection.pd.read_csv', side_effect=changed):
            with self.assertRaises(AssertionError):
                verify_publication_selection()

    def test_figure_inputs_use_publication_samples_and_valid_probabilities(self):
        from src.internal.publication_figures import load_plot_inputs
        selection, primary, point, errors, compatibility, sensitivity = load_plot_inputs()
        excluded = set(selection.loc[selection.excluded_identity_flag, 'physical_object_id'])
        self.assertEqual((len(primary), len(point)), (224, 234))
        for frame in (point, errors, compatibility, sensitivity):
            self.assertFalse(set(frame.physical_object_id) & excluded)
        point_only = errors.mbh_uncertainty_mode.eq('point_estimate_no_reported_mbh_error')
        self.assertEqual(int(point_only.sum()), 12)
        self.assertTrue(set(errors.loc[point_only, 'physical_object_id']) <= primary)
        self.assertTrue(errors.loc[point_only, 'prob_required_fedd_seed1e2_gt_1'].isna().all())
        self.assertEqual(set(compatibility.physical_object_id), set(point.physical_object_id))
        self.assertTrue(set(sensitivity.physical_object_id) <= primary)

    def test_mass_offsets_recover_baseline_and_preserve_missing_errors(self):
        outputs = build_publication_outputs()
        detail = outputs['mass_offset_object_sensitivity']
        baseline = detail.loc[detail.mass_offset_dex.eq(0)].set_index('physical_object_id')
        original = pd.read_csv(ROOT/'results/v3/tables/v3_object_uncertainty_ranking.csv').set_index('physical_object_id').loc[baseline.index]
        sampled = baseline.reported_mass_errors_sampled
        import numpy as np
        np.testing.assert_allclose(baseline.loc[sampled, 'p16'], original.loc[sampled, 'required_fedd_seed1e2_p16'], rtol=1e-12)
        np.testing.assert_array_equal(baseline.loc[sampled, 'probability_gt_1'], original.loc[sampled, 'prob_required_fedd_seed1e2_gt_1'])
        missing = detail.loc[~detail.reported_mass_errors_sampled]
        self.assertEqual(len(missing), 12 * 5)
        self.assertTrue(missing[['p16', 'probability_gt_1']].isna().all().all())
        self.assertTrue(missing.n_samples.eq(0).all())
        summary = outputs['mass_offset_sensitivity'].query('mass_offset_dex == 0').set_index('sample')
        self.assertEqual(summary.loc['primary', ['above_unity','p16_above_unity','probability_ge_095']].tolist(), [12,8,6])
        self.assertEqual(summary.loc['exploratory', ['above_unity','p16_above_unity','probability_ge_095']].tolist(), [14,10,8])

    def test_mass_offsets_follow_analytic_response_and_monotonic_thresholds(self):
        import numpy as np
        from src import models
        outputs = build_publication_outputs()
        detail = outputs['mass_offset_object_sensitivity']
        original = pd.read_csv(ROOT/'results/v3/tables/v3_object_point_ranking.csv').set_index('physical_object_id')
        baseline = detail.query('mass_offset_dex == 0').set_index('physical_object_id')
        for offset, group in detail.groupby('mass_offset_dex'):
            group = group.set_index('physical_object_id')
            z = original.loc[group.index, 'redshift'].to_numpy()
            # At fixed efficiency and time, f_req changes by a known linear
            # coefficient per dex until the physical zero floor is reached.
            coefficient = (.1/.9) * .45 * np.log(10) / (models.cosmic_time_gyr(z) - models.cosmic_time_gyr(30))
            expected = np.maximum(0, baseline.loc[group.index, 'required_fedd'].to_numpy() + offset * coefficient)
            np.testing.assert_allclose(group.required_fedd, expected, rtol=1e-12)
        for _, group in detail.groupby('physical_object_id'):
            group = group.sort_values('mass_offset_dex')
            for field in ('required_fedd', 'p16', 'probability_gt_1'):
                self.assertTrue((np.diff(group[field].dropna()) >= -1e-12).all())
