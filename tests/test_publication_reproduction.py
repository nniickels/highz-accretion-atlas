"""The quick manuscript check must catch stale PDF exports beside matching PNGs."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
from pypdf import PdfWriter

from src.internal.publication_figures import verify_figures


def write_exports(destination, creator):
    destination.mkdir(parents=True, exist_ok=True)
    Image.new('RGB', (12, 12), 'white').save(destination/'example.png')
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_metadata({'/Creator': creator})
    writer.write(destination/'example.pdf')


class PublicationReproductionTests(unittest.TestCase):
    def test_verifier_checks_pdf_even_when_png_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_exports(root/'paper/figures', 'old renderer')

            def render(root, destination):
                write_exports(Path(destination), 'pinned renderer')

            with patch('src.internal.publication_figures.NAMES', ('example',)), \
                 patch('src.internal.publication_figures.render_figures', render):
                with self.assertRaisesRegex(AssertionError, '/Info/Creator'):
                    verify_figures(root)
                write_exports(root/'paper/figures', 'pinned renderer')
                verify_figures(root)
