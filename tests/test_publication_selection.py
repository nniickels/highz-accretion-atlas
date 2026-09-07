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
