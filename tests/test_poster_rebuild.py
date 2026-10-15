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
    def test_final_definition_spacing_is_readable(self):
        for name in ['36x48.pptx', '48x36.pptx']:
            with ZipFile(ROOT/'posters'/name) as archive:
                data = {part: archive.read(part) for part in archive.namelist()}
                overview = ET.fromstring(archive.read(poster_slide_part(data)))
            concise = {shape.find('.//'+P+'cNvPr').get('id'): shape
                       for shape in overview.iter(P+'sp')}
            # The final editions retain the user-selected overview only.
            for paragraph in concise['73'].find(P+'txBody').findall(A+'p'):
                spacing = paragraph.find(A+'pPr/'+A+'lnSpc/'+A+'spcPct')
                self.assertIsNotNone(spacing)
                self.assertGreaterEqual(int(spacing.get('val')), 115000)

    def test_in_text_references_are_superscript_and_resolve(self):
        import re
        for name in ['36x48.pptx', '48x36.pptx']:
            with ZipFile(ROOT/'posters'/name) as archive:
                data = {n: archive.read(n) for n in archive.namelist()}
                slide = ET.fromstring(archive.read(poster_slide_part(data)))
            shapes = {s.find('.//'+P+'cNvPr').get('id'): s for s in slide.iter(P+'sp')}
            used = set()
            for identity, shape in shapes.items():
                if identity in ('82', '9'):
                    continue
                for run in shape.iter(A+'r'):
                    text = run.find(A+'t')
                    if text is None:
                        continue
                    citations = re.findall(r'\[([1-5])\]', text.text or '')
                    if citations:
                        self.assertEqual(run.find(A+'rPr').get('baseline'), '30000')
                        used.update(citations)
            self.assertEqual(used, set('12345'))
            for identity, citation in [('70','1'), ('207','2'), ('208','1'), ('217','3'), ('2','4'), ('15','5')]:
                self.assertIn('['+citation+']', ''.join(n.text or '' for n in shapes[identity].iter(A+'t')))
            references = ''.join(n.text or '' for identity in ('82', '9')
                                 if identity in shapes for n in shapes[identity].iter(A+'t'))
            for citation, author in [('1', 'Maiolino'), ('2', 'Shen'), ('3', 'Dayal'),
                                    ('4', 'Bardeen'), ('5', 'Juodzbalis')]:
                self.assertIn('['+citation+'] '+author, references)

    def test_overview_diagram_counts_match_catalogue_selection(self):
        import pandas as pd
        selection = pd.read_csv(ROOT/'results/for_manuscript/tables/publication_object_selection.csv')
        measurements = pd.read_csv(ROOT/'data/processed/v3/v3_accreting_measurements.csv')
        uncertainty = pd.read_csv(ROOT/'results/v3/tables/v3_object_uncertainty_ranking.csv')
        error_ids = set(uncertainty.loc[uncertainty.reported_mass_errors_sampled, 'physical_object_id'])
        primary_errors = int((selection.publication_primary_flag & selection.physical_object_id.isin(error_ids)).sum())
        expanded_errors = int((selection.publication_exploratory_flag & selection.physical_object_id.isin(error_ids)).sum())
        primary = int(selection.publication_primary_flag.sum())
        expanded = int(selection.publication_exploratory_flag.sum())
        excluded = int(selection.excluded_identity_flag.sum())
        no_mass = int((~selection.growth_ranking_eligible_flag & ~selection.excluded_identity_flag).sum())
        self.assertEqual(primary + (expanded-primary) + no_mass + excluded, len(selection))
        for name in ['36x48.pptx', '48x36.pptx']:
            with ZipFile(ROOT/'posters'/name) as archive:
                data = {part: archive.read(part) for part in archive.namelist()}
                slide = ET.fromstring(archive.read(poster_slide_part(data)))
            text = {shape.find('.//'+P+'cNvPr').get('id'):
                    ''.join(n.text or '' for n in shape.iter(A+'t'))
                    for shape in slide.iter(P+'sp')}
            self.assertIn(f'{len(measurements)} measurements', text['200'])
            self.assertIn(f'{len(selection)} provisional objects', text['202'])
            self.assertIn(f'{expanded} expanded-sample objects', text['206'])
            self.assertIn(f'{primary} primary', text['207'])
            self.assertIn(f'{expanded-primary} additional', text['208'])
            self.assertIn(f'{no_mass} without an', text['209'])
            self.assertIn(f'{excluded} with uncertain', text['209'])
            # The editable figures retain both processing paths and the missing-error caveat.
            self.assertIn('Central mass estimate', text['213'])
            self.assertIn('10,000 mass-error draws', text['214'])
            self.assertIn(f'{primary_errors} primary / {expanded_errors} expanded', text['223'])
            self.assertIn(f'The other {expanded-expanded_errors} enter central-mass tests only', text['223'])
            pictures = [n.find('.//'+P+'cNvPr').get('id') for n in slide.iter(P+'pic')]
            self.assertNotIn('3', pictures, 'The overview replaces the efficiency plot with the workflow')

    def test_final_editions_have_matching_content_and_preserved_dimensions(self):
        content = []
        for name, dimensions in [('36x48.pptx', (36, 48)), ('48x36.pptx', (48, 36))]:
            with ZipFile(ROOT/'posters'/name) as archive:
                presentation = ET.fromstring(archive.read('ppt/presentation.xml'))
                size = presentation.find(P+'sldSz')
                self.assertEqual((int(size.get('cx')), int(size.get('cy'))),
                                 tuple(inches * 914400 for inches in dimensions))
                self.assertEqual(len(presentation.find(P+'sldIdLst')), 1)
                data = {part: archive.read(part) for part in archive.namelist()}
                slides = [ET.fromstring(archive.read(part)) for part in poster_slide_parts(data)]
                # PowerPoint can split a word or symbol across runs when restyling it.
                # Compare nonempty paragraphs: run splits and empty paragraphs added by
                # PowerPoint are formatting, not changes to the scientific content.
                content.append([Counter(' '.join(''.join(node.text or ''
                                                        for node in paragraph.iter(A+'t')).split())
                                        for paragraph in slide.iter(A+'p')
                                        if any((node.text or '').strip()
                                               for node in paragraph.iter(A+'t'))) for slide in slides])
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
                words = lambda root: Counter(' '.join(''.join(n.text or '' for n in p.iter(A+'t')).split())
                                             for p in root.iter(A+'p')
                                             if any((n.text or '').strip() for n in p.iter(A+'t')))
                self.assertEqual(words(source), words(actual))
                # Rebuilding figures must not restore the old fixed layout or
                # collapse the reviewed two-column reference list.
                self.assertEqual(reviewed.read(target), rebuilt.read(target))
                math = lambda root: [ET.tostring(n) for n in root.iter(M+'oMath')]
                self.assertEqual(math(source), math(actual))
                for identity in (14, 4):
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
                    plot_media(portrait, poster_slide_part({n: portrait.read(n) for n in portrait.namelist()}), 4)))).convert('RGBA'))
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
