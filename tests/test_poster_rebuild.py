"""Protect scientific content and native math during the landscape reflow."""
from collections import Counter
from io import BytesIO
from pathlib import Path
import hashlib
import json
import posixpath
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np
from PIL import Image

from src.internal import poster_figures as render_figures
from src.internal.poster_layout import poster_slide_part, poster_slide_parts, relationship_part

ROOT = Path(__file__).resolve().parents[1]
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'


def plot_media(archive, slide, identity):
    root = ET.fromstring(archive.read(slide))
    picture = next(node for node in root.iter(P+'pic')
                   if node.find('.//'+P+'cNvPr').get('id') == str(identity))
    embed = picture.find('.//'+A+'blip').get(R+'embed')
    relationships = ET.fromstring(archive.read(relationship_part(slide)))
    target = next(node.get('Target') for node in relationships if node.get('Id') == embed)
    return posixpath.normpath(posixpath.dirname(slide) + '/' + target)


class PosterRebuildTests(unittest.TestCase):
    def test_overview_changes_only_methods_with_less_text_and_wider_spacing(self):
        for name in ['36x48.pptx', '48x36.pptx']:
            with ZipFile(ROOT/'posters'/name) as archive:
                data = {part: archive.read(part) for part in archive.namelist()}
                full, overview = [ET.fromstring(archive.read(part))
                                  for part in poster_slide_parts(data)]
            def shapes(root):
                result = {}
                for shape in root.iter(P+'sp'):
                    identity = shape.find('.//'+P+'cNvPr').get('id')
                    # The native Choice precedes the compatibility Fallback.
                    result.setdefault(identity, shape)
                return result
            original, concise = shapes(full), shapes(overview)
            words = lambda shape: ' '.join(''.join(node.text or '' for node in paragraph.iter(A+'t'))
                                          for paragraph in shape.find(P+'txBody').findall(A+'p'))
            for identity in original:
                if identity != '73':
                    self.assertEqual(words(original[identity]), words(concise[identity]),
                                     'Overview must preserve non-Methods content')
            self.assertLessEqual(len(words(concise['73']).split()),
                                 0.7 * len(words(original['73']).split()))
            for paragraph in concise['73'].find(P+'txBody').findall(A+'p'):
                spacing = paragraph.find(A+'pPr/'+A+'lnSpc/'+A+'spcPct')
                self.assertIsNotNone(spacing)
                self.assertGreaterEqual(int(spacing.get('val')), 115000)

    def test_final_editions_have_matching_content_and_preserved_dimensions(self):
        content = []
        for name, dimensions in [('36x48.pptx', (36, 48)), ('48x36.pptx', (48, 36))]:
            with ZipFile(ROOT/'posters'/name) as archive:
                presentation = ET.fromstring(archive.read('ppt/presentation.xml'))
                size = presentation.find(P+'sldSz')
                self.assertEqual((int(size.get('cx')), int(size.get('cy'))),
                                 tuple(inches * 914400 for inches in dimensions))
                self.assertEqual(len(presentation.find(P+'sldIdLst')), 2)
                data = {part: archive.read(part) for part in archive.namelist()}
                slides = [ET.fromstring(archive.read(part)) for part in poster_slide_parts(data)]
                self.assertTrue(list(slides[0].iter(M+'oMath')), 'Full version must retain its equation')
                content.append([Counter(' '.join((node.text or '').split())
                                        for node in slide.iter(A+'t')) for slide in slides])
        self.assertEqual(content[0], content[1], 'Final poster editions must contain the same text')

    def test_landscape_reflow_preserves_reviewed_content(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'rebuilt.pptx'
            result = subprocess.run([sys.executable, '-m', 'src.internal.poster_layout',
                                     '--output', str(output)], cwd=ROOT,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+'\n'+result.stderr)
            with ZipFile(ROOT/'posters/36x48.pptx') as portrait, \
                 ZipFile(ROOT/'posters/48x36.pptx') as reviewed, ZipFile(output) as rebuilt:
                reviewed_data = {name: reviewed.read(name) for name in reviewed.namelist()}
                target = poster_slide_part(reviewed_data)
                for name in reviewed.namelist():
                    if name.startswith('ppt/slides/slide') and name.endswith('.xml') and name != target:
                        self.assertEqual(reviewed.read(name), rebuilt.read(name))
                self.assertEqual(len(ET.fromstring(reviewed.read('ppt/presentation.xml')).find(P+'sldIdLst')),
                                 len(ET.fromstring(rebuilt.read('ppt/presentation.xml')).find(P+'sldIdLst')))
                source_data = {name: portrait.read(name) for name in portrait.namelist()}
                source = ET.fromstring(portrait.read(poster_slide_part(source_data)))
                actual = ET.fromstring(rebuilt.read(target))
                words = lambda root: Counter(' '.join((n.text or '').split())
                                             for n in root.iter(A+'t'))
                self.assertEqual(words(source), words(actual))
                math = lambda root: [ET.tostring(n) for n in root.iter(M+'oMath')]
                self.assertEqual(math(source), math(actual))
                for identity in (3, 14, 4):
                    expected = np.asarray(Image.open(BytesIO(reviewed.read(plot_media(reviewed, target, identity)))).convert('RGBA'))
                    generated = np.asarray(Image.open(BytesIO(rebuilt.read(plot_media(rebuilt, target, identity)))).convert('RGBA'))
                    self.assertEqual(expected.shape, generated.shape)
                    np.testing.assert_array_equal(expected[..., 3], generated[..., 3])
                    self.assertLessEqual(int(np.max(np.abs(expected[..., :3].astype(int)
                                                           - generated[..., :3].astype(int)))), 3)

    def test_portrait_uncertainty_reproduces_reviewed_pixels(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, '-m', 'src.internal.poster_figures',
                                     '--output-dir', directory, '--uncertainty-only'],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+'\n'+result.stderr)
            with ZipFile(ROOT/'posters/36x48.pptx') as portrait:
                expected = np.asarray(Image.open(BytesIO(portrait.read(
                    plot_media(portrait, 'ppt/slides/slide1.xml', 4)))).convert('RGBA'))
            generated = np.asarray(Image.open(Path(directory)/'uncertainty.png').convert('RGBA'))
            self.assertEqual(expected.shape, generated.shape)
            np.testing.assert_array_equal(expected[..., 3], generated[..., 3])
            self.assertLessEqual(int(np.max(np.abs(expected[..., :3].astype(int)
                                                   - generated[..., :3].astype(int)))), 3)

    def test_changed_scientific_input_stops_poster_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'data').mkdir()
            (root/'data/poster_inputs.json').write_text('{"sha256":{"input.csv":"reviewed-hash"}}')
            (root/'input.csv').write_text('changed scientific value\n')
            with patch.object(render_figures, 'ROOT', root), patch.dict('os.environ', {'HIGHZ_BASELINE_ROOT': ''}):
                with self.assertRaisesRegex(ValueError, 'Poster input changed: input.csv'):
                    render_figures.verify_inputs()

    def test_csv_reserialization_requires_a_pinned_independent_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            root, baseline = Path(directory)/'run', Path(directory)/'baseline'
            (root/'data').mkdir(parents=True)
            baseline.mkdir()
            original = b'object_id,mass\nA,7.123456789012345\n'
            (baseline/'input.csv').write_bytes(original)
            (root/'input.csv').write_bytes(original.replace(b'\n', b'\r\n'))
            pinned = hashlib.sha256(original).hexdigest()
            manifest = {'sha256': {'input.csv': pinned}}
            (root/'data/poster_inputs.json').write_text(json.dumps(manifest))
            with patch.object(render_figures, 'ROOT', root), patch.dict('os.environ', {'HIGHZ_BASELINE_ROOT': ''}):
                with self.assertRaisesRegex(ValueError, 'Poster input changed'):
                    render_figures.verify_inputs()
                render_figures.verify_inputs(baseline_root=baseline)
                with self.assertRaisesRegex(ValueError, 'independent'):
                    render_figures.verify_inputs(baseline_root=root)
                (root/'input.csv').write_text('object_id,mass\nA,8.0\n')
                with self.assertRaisesRegex(AssertionError, 'mass'):
                    render_figures.verify_inputs(baseline_root=baseline)
                (baseline/'input.csv').write_text('object_id,mass\nA,8.0\n')
                with self.assertRaisesRegex(ValueError, 'pinned input'):
                    render_figures.verify_inputs(baseline_root=baseline)
                (root/'data/poster_inputs.json').write_text(json.dumps({'sha256': {'input.py': pinned}}))
                (root/'input.py').write_bytes(original.replace(b'\n', b'\r\n'))
                with self.assertRaisesRegex(ValueError, 'Poster input changed: input.py'):
                    render_figures.verify_inputs(baseline_root=baseline)


if __name__ == '__main__':
    unittest.main()
