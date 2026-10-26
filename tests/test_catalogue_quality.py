"""Check complete diagnostics and distinguish assembly from scientific identity."""
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from src.catalogue_quality import annotate_scientific_identity, JADES_PROVENANCE_FIELDS
from src.internal.process_catalogues import build_versions
from src.internal.publication_selection import build_publication_membership
from src.standardize_data import add_eddington_ratio_consistency


ROOT = Path(__file__).resolve().parents[1]


class CatalogueQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.versions = build_versions()

    def test_consistency_uses_independent_luminosity_mass_algebra(self):
        frame = pd.DataFrame({
            'log_mbh_msun_std': [8.] * 6,
            'log_lbol_erg_s_std': [np.log10(1.26e45)] * 6,
            'edd_ratio_std': [.1, .01, 0., -1., np.nan, np.inf],
        })
        result = add_eddington_ratio_consistency(frame)
        pd.testing.assert_frame_equal(result[frame.columns], frame)
        self.assertAlmostEqual(result.loc[0, 'edd_ratio_from_mbh_lbol'], .1)
        self.assertAlmostEqual(result.loc[1, 'edd_ratio_log_residual_dex'], -1)
        self.assertEqual(result.edd_ratio_consistency_flag.tolist(),
                         ['consistent', 'inconsistent'] + ['not_evaluable'] * 4)
        self.assertTrue(result.loc[2:, 'edd_ratio_log_residual_dex'].isna().all())

    def test_all_evaluable_measurements_and_objects_are_assessed(self):
        for name, count in [('measurements', 102), ('objects', 97)]:
            frame = self.versions['v3'][name]
            valid = (frame.log_mbh_msun_std.notna() & frame.log_lbol_erg_s_std.notna()
                     & frame.edd_ratio_std.gt(0))
            self.assertEqual(int(valid.sum()), count)
            self.assertTrue(frame.loc[valid, 'edd_ratio_consistency_flag'].isin(
                ['consistent', 'inconsistent']).all())
            self.assertTrue(frame.loc[~valid, 'edd_ratio_consistency_flag'].eq('not_evaluable').all())
            self.assertEqual(frame.loc[frame.edd_ratio_consistency_flag.eq('inconsistent'),
                                       'object_id'].unique().tolist(), ['GN-11836'])

    def test_open_audit_status_survives_version_subsetting(self):
        for version, count in [('v1', 2), ('v2', 3), ('v3', 6)]:
            products = self.versions[version]
            objects = products['objects']
            self.assertEqual(int(objects.scientific_identity_status.eq('unresolved').sum()), count)
            self.assertTrue(objects.identity_resolution_status.eq('resolved').all())
            self.assertEqual(set(objects.scientific_identity_status),
                             {'unresolved', 'no_open_issue_recorded'})
            links = products['measurement_object_links'].set_index('measurement_id')
            measurements = products['measurements'].set_index('measurement_id')
            pd.testing.assert_series_equal(links.scientific_identity_status.sort_index(),
                                           measurements.scientific_identity_status.sort_index())

    def test_alternates_inherit_an_objects_open_group(self):
        frame = pd.DataFrame({'measurement_id': ['a', 'b', 'alternate', 'other'],
                              'physical_object_id': ['A', 'B', 'A', 'C']})
        result = annotate_scientific_identity(frame, [{'left': 'a', 'right': 'b', 'issue_group': 'open'}])
        self.assertEqual(result.scientific_identity_status.tolist(),
                         ['unresolved'] * 3 + ['no_open_issue_recorded'])
        self.assertEqual(result.scientific_identity_issue_group.tolist(), ['open'] * 3 + [''])

    def test_unknown_or_conflicting_audit_groups_are_rejected(self):
        frame = pd.DataFrame({'measurement_id': ['a', 'b'], 'physical_object_id': ['A', 'B']})
        with self.assertRaisesRegex(ValueError, 'unknown measurement'):
            annotate_scientific_identity(frame, [{'left': 'a', 'right': 'missing', 'issue_group': 'x'}])
        with self.assertRaisesRegex(ValueError, 'Overlapping'):
            annotate_scientific_identity(frame, [
                {'left': 'a', 'right': 'b', 'issue_group': 'x'},
                {'left': 'a', 'right': 'b', 'issue_group': 'y'},
            ])

    def test_scientific_status_agrees_with_publication_exclusions(self):
        products = self.versions['v3']
        membership = build_publication_membership(
            measurements=products['measurements'], objects=products['objects'])
        status = products['objects'].set_index('physical_object_id').scientific_identity_status
        self.assertEqual(set(membership.loc[membership.excluded_identity_flag, 'physical_object_id']),
                         set(status.loc[status.eq('unresolved')].index))
        self.assertEqual((int(membership.publication_primary_flag.sum()),
                          int(membership.publication_exploratory_flag.sum())), (223, 238))
        broken = products['objects'].copy()
        broken.loc[broken.scientific_identity_status.eq('unresolved'), 'scientific_identity_status'] = 'no_open_issue_recorded'
        with self.assertRaisesRegex(AssertionError, 'scientific identity status'):
            build_publication_membership(measurements=products['measurements'], objects=broken)

    def test_jades_provenance_preserves_unknown_extraction_dates(self):
        registry = pd.read_csv(ROOT/'data/source_provenance_registry.csv').set_index('provenance_id')
        source = registry.loc['juodzbalis25_primary']
        for version, products in self.versions.items():
            rows = products['measurements'].loc[
                products['measurements'].source_key.eq('juodzbalis25_jades_blagn')]
            self.assertEqual(len(rows), 23, version)
            for field in JADES_PROVENANCE_FIELDS:
                self.assertTrue(rows[field].eq(source[field]).all(), field)
            self.assertTrue(rows.extraction_date.eq('not_recorded_in_frozen_v1_source_layer').all())
            self.assertTrue(rows.extraction_date_status.eq('not_recorded').all())


if __name__ == '__main__':
    unittest.main()
