"""Independent equations, selection boundaries, and v4 output reproduction."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from src import models, pbh
from src.internal.pbh_growth_v4 import (
    ROOT, build_tables, load_config, select_targets, verify_outputs, write_outputs,
)
from src.internal.early_start_cosmology import cosmic_time_gyr


class PBHGrowthTests(unittest.TestCase):
    def test_inverse_equation_independent_of_model_helper(self):
        # Dayal Eq. 1: 0.1 Gyr at f=1, epsilon=.1 supplies two e-folds.
        # Independently express the expected minimum seed in natural logs.
        dt = float(cosmic_time_gyr(10.603) - cosmic_time_gyr(3400))
        expected = (np.log(10**6.2) - 9 * dt / .45) / np.log(10)
        actual = float(pbh.minimum_seed_log10(6.2, 3400, 10.603))
        self.assertAlmostEqual(actual, expected, places=12)
        predicted = float(models.predicted_log_mbh_from_delta_t(actual, 1, .1, dt))
        self.assertAlmostEqual(predicted, 6.2, places=12)

    def test_delayed_onset_and_lower_cap_require_larger_seed(self):
        earlier = float(pbh.minimum_seed_log10(8.17, 3400, 8.5))
        delayed = float(pbh.minimum_seed_log10(8.17, 30, 8.5))
        slower = float(pbh.minimum_seed_log10(8.17, 3400, 8.5, .3))
        self.assertGreater(delayed, earlier)
        self.assertGreater(slower, earlier)
        self.assertAlmostEqual(float(pbh.minimum_seed_log10(8.17, 30, 8.5, 0)), 8.17)
        shift = float(pbh.minimum_seed_log10(7.67, 3400, 8.5))
        self.assertAlmostEqual(shift - earlier, -.5)

    def test_support_matches_brute_force_and_excludes_overmassive_seeds(self):
        draws = np.array([1., 2., 3., 4., 5.])
        seeds = np.array([0., 2., 4., 6.])
        fraction, excessive = pbh.compatible_mass_draw_fraction(draws, seeds, 30, 10, .3)
        dt = float(cosmic_time_gyr(10) - cosmic_time_gyr(30))
        gain = .3 * 9 * dt / (.45 * np.log(10))
        for i, seed in enumerate(seeds):
            expected = np.mean((draws >= seed) & (draws <= seed + gain))
            self.assertEqual(fraction[i], expected)
            self.assertEqual(excessive[i], np.mean(draws < seed))
        self.assertEqual(fraction[-1], 0)
        self.assertEqual(excessive[-1], 1)
        # Zero accretion accepts exact seed=target equality, nothing else.
        point, _ = pbh.compatible_mass_draw_fraction(draws, 3, 30, 10, 0)
        self.assertEqual(point, .2)

    def test_invalid_histories_and_draws_rejected(self):
        for onset, obs in [(10, 10), (9, 10), (3401, 10), (30, -1), (np.nan, 10)]:
            with self.subTest(onset=onset, obs=obs), self.assertRaises(ValueError):
                pbh.growth_interval_gyr(onset, obs)
        for cap, eps in [(-1, .1), (np.inf, .1), (1, 0), (1, 1), (1, np.nan)]:
            with self.assertRaises(ValueError):
                pbh.minimum_seed_log10(8, 30, 10, cap, eps)
        for draws in [[], [2, 1], [np.nan]]:
            with self.assertRaises(ValueError):
                pbh.compatible_mass_draw_fraction(draws, 2, 30, 10)


class PBHWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = build_tables()

    def test_targets_are_selected_from_eligible_primary_plus_uv_comparator(self):
        targets = self.tables['targets']
        self.assertEqual(targets.object_id.tolist(), [
            'UNCOVER-20466', 'COSMOS3D-13852', 'RUBIES-EGS-55604', 'GN-z11'])
        self.assertEqual(targets.publication_primary_flag.tolist(), [True, True, True, False])
        self.assertTrue(targets.reported_mass_errors_sampled.all())
        self.assertTrue(select_targets().excluded_identity_flag.eq(False).all())
        self.assertAlmostEqual(targets.iloc[0].reference_required_fedd_matter_lambda,
                               1.452204136497696, places=12)

    def test_fixed_origin_label_cannot_change_growth_for_identical_parameters(self):
        controls = self.tables['controls']
        for row in controls.loc[controls.control.eq('stellar_remnant_control')].itertuples():
            counterpart = controls.loc[
                controls.object_id.eq(row.object_id) & controls.control.eq('PBH_growth_hypothesis')
                & controls.log10_seed_msun.eq(row.log10_seed_msun)
                & controls.z_accretion.eq(row.z_accretion) & controls.epsilon.eq(row.epsilon)
                & controls.mass_offset_dex.eq(row.mass_offset_dex)].iloc[0]
            self.assertEqual(row.required_mean_fedd_raw, counterpart.required_mean_fedd_raw)
            self.assertEqual(row.mass_draw_fraction_within_eddington_cap,
                             counterpart.mass_draw_fraction_within_eddington_cap)

    def test_sensitivity_shifts_are_applied_to_draws_and_central_mass(self):
        table = self.tables['minimum_seed_mass']
        keys = ['object_id', 'epsilon', 'fedd_cap', 'z_accretion']
        central = table.loc[table.mass_offset_dex.eq(0)].set_index(keys)
        shifted = table.loc[table.mass_offset_dex.eq(-.5)].set_index(keys)
        for column in ['log10_minimum_seed_central', 'log10_minimum_seed_p16', 'log10_minimum_seed_p84']:
            np.testing.assert_allclose(shifted[column] - central[column], -.5, atol=1e-12)
        grid = self.tables['seed_onset_compatibility']
        self.assertTrue(grid.mass_draw_fraction_within_growth_cap.between(0, 1).all())
        self.assertTrue((grid.mass_draw_fraction_within_growth_cap
                         + grid.mass_draw_fraction_seed_overpredicts <= 1 + 1e-15).all())
        excessive = grid.central_status.eq('seed_overpredicts_target')
        self.assertTrue(grid.loc[excessive, 'required_mean_fedd_raw'].lt(0).all())

    def test_missing_mass_error_not_converted_into_probability(self):
        # Run a minimal synthetic root with a missing-error target. A missing
        # interval supports a point estimate, never a claimed 100% certainty.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            from src.internal.pbh_growth_v4 import INPUT_PATHS
            for relative in INPUT_PATHS:
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                (root / relative).write_bytes((ROOT / relative).read_bytes())
            catalogue = pd.read_csv(root / INPUT_PATHS[1])
            mask = catalogue.object_id.eq('UNCOVER-20466')
            catalogue.loc[mask, ['log_mbh_err_plus_std', 'log_mbh_err_minus_std']] = np.nan
            catalogue.to_csv(root / INPUT_PATHS[1], index=False)
            tables = build_tables(root)
            grid = tables['seed_onset_compatibility'].query("object_id == 'UNCOVER-20466'")
            self.assertTrue(grid.mass_draw_fraction_within_growth_cap.isna().all())
            target = tables['targets'].query("object_id == 'UNCOVER-20466'").iloc[0]
            self.assertEqual(target.n_mass_draws, 0)

    def test_v4_tables_reproduce_and_inputs_are_pinned(self):
        self.assertEqual(verify_outputs(verify_figures=False)['v4_verification'], 'pass')
        self.assertEqual(load_config()['population_viability_status'], 'not_assessed')

    def test_protected_output_location_is_rejected_before_writing(self):
        with self.assertRaises(ValueError):
            write_outputs(destination=ROOT / 'results/manuscript')

    def test_optional_notebook_is_clean_and_compilable(self):
        notebook = json.loads((ROOT / 'scripts/05_pbh_growth_v4.ipynb').read_text())
        ids = [cell['id'] for cell in notebook['cells']]
        self.assertEqual(len(ids), len(set(ids)))
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                self.assertIsNone(cell['execution_count'])
                self.assertEqual(cell['outputs'], [])
                compile(''.join(cell['source']), 'v4_notebook', 'exec')


if __name__ == '__main__':
    unittest.main()
