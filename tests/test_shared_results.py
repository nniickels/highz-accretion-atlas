"""Check that plot sharing preserves each edition's scientific inputs."""
from pathlib import Path
import hashlib
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from src.internal import atlas, seedredshift_mass_maps
from src.internal.dataset_manifests import canonical_artifacts
from src.internal.shared_results import MAP_FIELDS, fedd_map_paths, sensitivity_figure_path


ROOT = Path(__file__).resolve().parents[1]


class SharedResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.objects = pd.read_csv(ROOT/'data/processed/v3/v3_accreting_objects.csv')

    def test_changed_mass_redshift_or_label_keeps_a_separate_map(self):
        obj = self.objects.loc[self.objects.physical_object_id.eq('HZA-GN-1093')].copy()
        key = obj.physical_object_id.iloc[0]
        self.assertEqual(fedd_map_paths(ROOT, 'v3', obj)[key].relative_to(ROOT).parts[1], 'v1')
        for field in MAP_FIELDS:
            changed = obj.copy()
            changed[field] = changed[field] + (0.01 if field in ('redshift', 'log_mbh_msun_std') else ' changed')
            with self.subTest(field=field):
                self.assertEqual(fedd_map_paths(ROOT, 'v3', changed)[key].relative_to(ROOT).parts[1], 'v3')

    def test_no_mass_preserves_reasons_without_creating_images(self):
        objects = self.objects.loc[~self.objects.growth_ranking_eligible_flag]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(atlas, 'ROOT', root), patch.object(atlas, 'VERSION', 'v1'), \
                 patch.object(seedredshift_mass_maps, 'ROOT', root), \
                 patch.object(atlas, 'plot_fedd_mass_map') as fedd, \
                 patch.object(seedredshift_mass_maps, 'plot_seedredshift_mass_map') as seed:
                coverage = pd.concat([atlas.materialize_fedd_mass_maps(objects, rebuild=True),
                                      seedredshift_mass_maps.materialize('v1', objects, rebuild=True)])
                fedd.assert_not_called()
                seed.assert_not_called()
            self.assertTrue(coverage.path.eq('').all())
            self.assertTrue(coverage.product_status.eq('no_numerical_mass').all())
            self.assertEqual(set(coverage.status_reason), set(objects.growth_ranking_eligibility_reason))
            self.assertEqual(list(root.rglob('*.png')), [])

    def test_missing_shared_file_is_rendered_at_its_canonical_path(self):
        obj = self.objects.loc[self.objects.physical_object_id.eq('HZA-GN-1093')]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for v in ('v1', 'v2'):
                path = root/'data/processed'/v/f'{v}_accreting_objects.csv'
                path.parent.mkdir(parents=True)
                obj.to_csv(path, index=False)
            def render(row, path):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'newly rendered map')
            with patch.object(atlas, 'ROOT', root), patch.object(atlas, 'VERSION', 'v3'), \
                 patch.object(atlas, 'plot_fedd_mass_map', side_effect=render) as renderer:
                first = atlas.materialize_fedd_mass_maps(obj, rebuild=True)
                second = atlas.materialize_fedd_mass_maps(obj, rebuild=True)
            renderer.assert_called_once()
            self.assertEqual(first.path.tolist(), second.path.tolist())
            self.assertTrue((root/first.path.iloc[0]).is_file())
            self.assertIn('results/v1/', first.path.iloc[0])

    def test_sharing_covers_both_figures_and_all_referencing_manifests(self):
        self.assertEqual(sensitivity_figure_path(ROOT, 'v3'), sensitivity_figure_path(ROOT, 'v2'))
        coverage = pd.read_csv(ROOT/'results/v3/tables/v3_all_object_visual_coverage.csv')
        referenced = {ROOT/name for name in coverage.path.dropna()}
        referenced.add(sensitivity_figure_path(ROOT, 'v3'))
        self.assertTrue(referenced <= set(canonical_artifacts('v3')))
        self.assertEqual(len(coverage.loc[coverage.growth_ranking_eligible_flag]), 482)

    def test_retained_pngs_have_no_exact_copies_and_no_evaluation_aliases(self):
        seen = {}
        for path in sorted((ROOT/'results').rglob('*.png')):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertNotIn(digest, seen, f'{path} duplicates {seen.get(digest)}')
            seen[digest] = path
        self.assertEqual(list((ROOT/'results').rglob('*_evaluation_table.csv')), [])


if __name__ == '__main__':
    unittest.main()
