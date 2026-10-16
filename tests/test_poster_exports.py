"""Reject stale poster PDFs and changes to reviewed export pairs."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from pypdf import PdfWriter
from src.internal.verify_poster_exports import ROOT, verify_exports
from src.internal.poster_layout import poster_slide_parts


class PosterExportTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory)
        (root/'data').mkdir()
        (root/'posters').mkdir()
        shutil.copy2(ROOT/'data/poster_exports.json', root/'data/poster_exports.json')
        for name in ('36x48.pptx', '36x48.pdf', '48x36.pptx', '48x36.pdf'):
            shutil.copy2(ROOT/'posters'/name, root/'posters'/name)
        return root

    def test_reviewed_exports_match_sources(self):
        self.assertEqual(verify_exports(), 2)

    def test_deck_hash_refresh_cannot_bless_a_changed_pdf_source_slide(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            path = root/'posters/36x48.pptx'
            with ZipFile(path) as archive:
                data = {name: archive.read(name) for name in archive.namelist()}
            part = poster_slide_parts(data)[0]
            data[part] = data[part].replace(b'<p:cSld', b'<p:cSld name="Changed"', 1)
            with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
                for name, value in data.items():
                    archive.writestr(name, value)
            manifest_path = root/'data/poster_exports.json'
            manifest = json.loads(manifest_path.read_text())
            manifest['exports'][0]['source_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'PDF source slide changed'):
                verify_exports(root)

    def test_source_edit_and_pdf_edit_require_review(self):
        for name in ('36x48.pptx', '36x48.pdf'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = self.fixture(directory)
                path = root/'posters'/name
                path.write_bytes(path.read_bytes()+b'changed')
                with self.assertRaisesRegex(ValueError, 'Reviewed poster artifact changed'):
                    verify_exports(root)

    def test_hash_refresh_does_not_bypass_page_and_text_checks(self):
        for dimensions, error in (((100, 100), 'dimensions'), ((2592, 3456), 'text coverage')):
            with self.subTest(dimensions=dimensions), tempfile.TemporaryDirectory() as directory:
                root = self.fixture(directory)
                path = root/'posters/36x48.pdf'
                writer = PdfWriter()
                writer.add_blank_page(width=dimensions[0], height=dimensions[1])
                writer.write(path)
                manifest_path = root/'data/poster_exports.json'
                manifest = json.loads(manifest_path.read_text())
                manifest['exports'][0]['pdf_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                manifest_path.write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, error):
                    verify_exports(root)
