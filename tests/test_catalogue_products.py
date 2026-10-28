"""Independent checks for compact results and catalogue-wide growth comparisons."""

from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.internal.catalogue_products import (
    CONFIG_PATH, OUTPUT_NAMES, build_outputs, build_growth_comparisons,
    build_field_availability, load_config,
)
from src.internal.publication_selection import build_publication_membership
from src.internal.reproduction import assert_csv_reproduction


ROOT = Path(__file__).resolve().parents[1]


class CatalogueProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.measurements = pd.read_csv(ROOT / 'data/processed/v3/v3_accreting_measurements.csv')
        cls.objects = pd.read_csv(ROOT / 'data/processed/v3/v3_accreting_objects.csv')
        cls.point = pd.read_csv(ROOT / 'results/v3/tables/v3_object_point_ranking.csv')
        cls.errors = pd.read_csv(ROOT / 'results/v3/tables/v3_object_uncertainty_ranking.csv')
        cls.config = load_config()
        cls.outputs = build_outputs(cls.measurements, cls.objects, cls.point, cls.errors)

    def test_compact_results_include_all_objects_and_preserve_sample_exclusions(self):
        summary = self.outputs['object_results']
        self.assertEqual(len(summary), 343)
        self.assertLessEqual(len(summary.columns), 35)
        self.assertTrue(summary.physical_object_id.is_unique)
        self.assertEqual(set(summary.physical_object_id), set(self.objects.physical_object_id))
        self.assertEqual(int(summary.publication_primary_flag.sum()), 223)
        self.assertEqual(int(summary.publication_exploratory_flag.sum()), 238)
        self.assertEqual(int(summary.excluded_identity_flag.sum()), 6)
        excluded = summary.loc[summary.excluded_identity_flag]
        self.assertFalse(excluded.publication_primary_flag.any())
        self.assertFalse(excluded.publication_exploratory_flag.any())

    def test_missing_masses_and_errors_do_not_become_growth_or_probability_estimates(self):
        summary = self.outputs['object_results']
        missing = summary.loc[~summary.growth_ranking_eligible_flag]
        self.assertEqual(len(missing), 102)
        self.assertTrue(missing.required_fedd_seed1e2.isna().all())
        no_error = summary.loc[~summary.reported_mass_errors_sampled]
        for field in ('required_fedd_seed1e2_p16', 'required_fedd_seed1e2_p50',
                      'required_fedd_seed1e2_p84', 'prob_required_fedd_seed1e2_gt_1'):
            self.assertTrue(no_error[field].isna().all(), field)
        for name in ('growth_assumption_comparison', 'minimum_seed_mass'):
            frame = self.outputs[name]
            no_error = frame.loc[~frame.reported_mass_errors_sampled]
            self.assertEqual(no_error.physical_object_id.nunique(), 12)
            self.assertTrue(no_error.n_mass_draws.eq(0).all())
            for field in frame.columns:
                if field.endswith(('_p16', '_p50', '_p84')) or field.startswith(('prob_', 'fraction_')):
                    self.assertTrue(no_error[field].isna().all(), field)

    def test_reference_comparison_reuses_the_existing_uncertainty_draws(self):
        comparison = self.outputs['growth_assumption_comparison']
        reference = comparison.loc[comparison.scenario.eq('reference')].set_index('physical_object_id')
        point = self.point.set_index('physical_object_id').loc[reference.index]
        errors = self.errors.set_index('physical_object_id').loc[reference.index]
        np.testing.assert_allclose(reference.required_fedd, point.required_fedd_seed1e2, rtol=1e-13)
        valid = reference.reported_mass_errors_sampled
        for suffix in ('p16', 'p50', 'p84'):
            np.testing.assert_allclose(reference.loc[valid, f'required_fedd_{suffix}'],
                                       errors.loc[valid, f'required_fedd_seed1e2_{suffix}'], rtol=1e-13)
        np.testing.assert_array_equal(reference.loc[valid, 'prob_required_fedd_gt_1'],
                                      errors.loc[valid, 'prob_required_fedd_seed1e2_gt_1'])

    def test_scenario_counts_reproduce_the_existing_publication_comparison(self):
        expected = pd.read_csv(ROOT / 'results/v3/selected_samples/tables/identity_exclusion_sensitivity.csv')
        comparison = self.outputs['growth_assumption_comparison']
        for row in expected.loc[expected.scope.eq('publication')].itertuples(index=False):
            flag = 'publication_primary_flag' if row.sample == 'primary' else 'publication_exploratory_flag'
            subset = comparison.loc[comparison.scenario.eq(row.scenario) & comparison[flag]]
            with self.subTest(sample=row.sample, scenario=row.scenario):
                self.assertEqual(len(subset), row.n_objects)
                self.assertEqual(int(subset.required_fedd.gt(1).sum()), row.above_unity)

    def test_mass_shifts_reproduce_existing_object_probabilities(self):
        existing = pd.read_csv(ROOT / 'results/v3/selected_samples/tables/mass_offset_object_sensitivity.csv')
        comparison = self.outputs['growth_assumption_comparison']
        names = {0.: 'reference', -.5: 'mass_minus_0p5', -.3: 'mass_minus_0p3',
                 .3: 'mass_plus_0p3', .5: 'mass_plus_0p5'}
        for offset, scenario in names.items():
            expected = existing.loc[existing.mass_offset_dex.eq(offset)].set_index('physical_object_id')
            actual = comparison.loc[comparison.scenario.eq(scenario)].set_index('physical_object_id').loc[expected.index]
            np.testing.assert_allclose(actual.required_fedd, expected.required_fedd, rtol=1e-13)
            np.testing.assert_allclose(actual.prob_required_fedd_gt_1, expected.probability_gt_1,
                                       rtol=0, atol=0, equal_nan=True)

    def test_seeds_above_the_final_mass_are_not_marked_as_successful_growth(self):
        objects = self.objects.loc[self.objects.growth_ranking_eligible_flag].head(1).copy()
        objects['log_mbh_msun_std'] = 4.0
        objects['log_mbh_err_plus_std'] = .01
        objects['log_mbh_err_minus_std'] = .01
        membership = build_publication_membership()
        comparison, _ = build_growth_comparisons(objects, membership, self.config, 100, 7)
        row = comparison.loc[comparison.scenario.eq('seed_1e5')].iloc[0]
        self.assertEqual(row.required_fedd, 0)
        self.assertEqual(row.central_status, 'seed_exceeds_target')
        self.assertEqual(row.fraction_mass_draws_within_eddington_cap, 0)

    def test_minimum_seeds_recover_the_target_by_independent_growth_algebra(self):
        frame = self.outputs['minimum_seed_mass']
        masses = self.objects.set_index('physical_object_id').log_mbh_msun_std
        gain = frame.fedd_cap * (1 - frame.epsilon) / frame.epsilon * frame.growth_time_gyr / (.45 * np.log(10))
        expected = frame.physical_object_id.map(masses) + frame.mass_offset_dex
        np.testing.assert_allclose(frame.log10_minimum_seed_central + gain, expected, rtol=0, atol=1e-13)
        self.assertEqual(len(frame), 241 * 3 * 2 * 3 * 3)

    def test_minimum_seed_centers_match_v4_where_the_settings_overlap(self):
        existing = pd.read_csv(ROOT / 'results/v4/tables/v4_minimum_seed_mass.csv', float_precision='round_trip')
        keys = ['physical_object_id', 'epsilon', 'fedd_cap', 'mass_offset_dex', 'z_accretion']
        shared = existing.merge(self.outputs['minimum_seed_mass'], on=keys, suffixes=('_v4', '_catalogue'),
                                validate='one_to_one')
        self.assertEqual(len(shared), 4 * 2 * 3 * 2 * 3)
        np.testing.assert_allclose(shared.log10_minimum_seed_central_v4,
                                   shared.log10_minimum_seed_central_catalogue, rtol=0, atol=1e-13)
        np.testing.assert_allclose(shared.growth_time_gyr_v4, shared.growth_time_gyr_catalogue, rtol=1e-13)

    def test_field_counts_have_explicit_denominators_and_partition_by_source_and_class(self):
        availability = self.outputs['field_availability']
        for level, total in (('object', 343), ('measurement', 355)):
            subset = availability.loc[availability.entity_level.eq(level)]
            overall = subset.loc[subset.group_by.eq('all')].set_index('field')
            self.assertTrue(overall.n_rows.eq(total).all())
            self.assertTrue(subset.n_available.add(subset.n_missing).eq(subset.n_rows).all())
            for dimension in ('source_key', 'object_class'):
                groups = subset.loc[subset.group_by.eq(dimension)].groupby('field')
                pd.testing.assert_series_equal(groups.n_available.sum(), overall.n_available.sort_index(), check_names=False)
        counts = availability.query("entity_level == 'object' and group_by == 'all'").set_index('field')
        self.assertEqual(counts.loc['black_hole_mass', 'n_available'], 241)
        self.assertEqual(counts.loc['black_hole_mass_error', 'n_available'], 229)
        self.assertEqual(counts.loc['stellar_mass', 'n_available'], 115)
        self.assertEqual(counts.loc['reported_eddington_ratio', 'n_available'], 98)

    def test_upper_limits_and_partial_coordinates_are_counted_separately(self):
        objects = self.objects.head(1).copy()
        objects['log_mstar_msun_std'] = np.nan
        objects['log_mstar_upper_limit_msun'] = 9.0
        objects['dec_deg'] = np.nan
        counts = build_field_availability(objects, objects).query(
            "entity_level == 'object' and group_by == 'all'").set_index('field')
        self.assertEqual(counts.loc['stellar_mass', 'n_available'], 0)
        self.assertEqual(counts.loc['stellar_mass_upper_limit', 'n_available'], 1)
        self.assertEqual(counts.loc['coordinates', 'n_available'], 0)

    def test_generation_is_order_independent_and_needs_no_stored_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (CONFIG_PATH, Path('data/publication/identity_exclusions.json'),
                             Path('data/publication/evidence_selection.json'),
                             Path('data/validation/redshift_identity_checks.json')):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / relative).read_bytes())
            actual = build_outputs(self.measurements.sample(frac=1, random_state=1),
                                   self.objects.sample(frac=1, random_state=2),
                                   self.point.sample(frac=1, random_state=3),
                                   self.errors.sample(frac=1, random_state=4), root=root)
            self.assertFalse((root / 'results').exists())
            for name in OUTPUT_NAMES:
                pd.testing.assert_frame_equal(self.outputs[name], actual[name])

    def test_stale_preferred_measurement_and_mismatched_draw_settings_are_rejected(self):
        point = self.point.copy()
        point.loc[0, 'measurement_id'] = 'stale measurement'
        with self.assertRaisesRegex(ValueError, 'preferred measurements'):
            build_outputs(self.measurements, self.objects, point, self.errors)
        with self.assertRaisesRegex(ValueError, 'same sample count'):
            build_outputs(self.measurements, self.objects, self.point, self.errors, n_samples=99)

    def test_stored_tables_reproduce(self):
        for name in OUTPUT_NAMES:
            assert_csv_reproduction(ROOT / f'results/v3/tables/v3_{name}.csv', self.outputs[name])

    def test_manifest_rejects_changed_settings_or_code_without_refresh(self):
        from src.internal import dataset_manifests as manifests
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in manifests.CATALOGUE_PRODUCT_INPUTS:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / name).read_bytes())
            with patch.object(manifests, 'ROOT', root), \
                 patch.object(manifests, 'MANIFESTS', root / 'data/manifests'), \
                 patch.object(manifests, 'canonical_artifacts', return_value=[]):
                path = manifests.manifest_path('v3')
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps(manifests.build_manifest('v3')))
                manifests.verify_manifest('v3')
                for name in (CONFIG_PATH, Path('src/internal/catalogue_products.py')):
                    source = root / name
                    original = source.read_bytes()
                    source.write_bytes(original + b'\n')
                    with self.subTest(input=name), self.assertRaisesRegex(AssertionError, 'input_changes='):
                        manifests.verify_manifest('v3')
                    source.write_bytes(original)

    def test_invalid_or_ambiguous_scenarios_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / CONFIG_PATH
            path.parent.mkdir(parents=True)
            for field, values in (('epsilon_values', [0]), ('onset_redshifts', [3401]),
                                  ('average_fedd_caps', [-1]), ('mass_offsets_dex', [0, 0])):
                config = json.loads(json.dumps(self.config))
                config['minimum_seed'][field] = values
                path.write_text(json.dumps(config))
                with self.subTest(field=field), self.assertRaises(ValueError):
                    load_config(root)
            config = json.loads(json.dumps(self.config))
            config['comparison_scenarios'].append({'name': 'reference'})
            path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, 'unique names'):
                load_config(root)


if __name__ == '__main__':
    unittest.main()
