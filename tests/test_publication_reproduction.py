"""Canonical publication figures use PNGs and reject stale rendered content."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from src.internal.publication_figures import verify_figures
from src.internal import build_results_inventory, publication_figures
from src.internal.verify_versions import verify_results_inventory


def write_exports(destination, color):
    destination.mkdir(parents=True, exist_ok=True)
    Image.new('RGB', (12, 12), color).save(destination/'example.png')


class PublicationReproductionTests(unittest.TestCase):
    def test_checked_in_results_inventory_matches_exports(self):
        verify_results_inventory()

    def test_standalone_export_refreshes_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            results = Path(directory)/'results'
            destination = results/'for_manuscript/figures'
            inventory = results/'results_inventory.csv'
            with patch.object(build_results_inventory, 'RESULTS', results), \
                 patch.object(build_results_inventory, 'OUTPUT', inventory):
                write_exports(destination, 'white')
                build_results_inventory.build_inventory()
                original = inventory.read_bytes()
                with patch.object(publication_figures, 'render_figures',
                                  lambda: write_exports(destination, 'black')), \
                     patch('sys.argv', ['publication_figures']):
                    publication_figures.main()
                self.assertNotEqual(original, inventory.read_bytes())
                self.assertEqual(inventory.read_text(),
                                 build_results_inventory.collect_inventory().to_csv(index=False))

    def test_verifier_rejects_stale_png_and_accepts_regenerated_png(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_exports(root/'results/for_manuscript/figures', 'white')

            def render(root, destination):
                write_exports(Path(destination), 'black')

            with patch('src.internal.publication_figures.NAMES', ('example',)), \
                 patch('src.internal.publication_figures.render_figures', render):
                with self.assertRaisesRegex(AssertionError, 'rendered pixels differ'):
                    verify_figures(root)
                write_exports(root/'results/for_manuscript/figures', 'black')
                verify_figures(root)
