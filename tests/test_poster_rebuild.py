"""Protect scientific content and native math during the landscape reflow."""
from collections import Counter
from io import BytesIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np
from PIL import Image

from posters import render_figures

ROOT = Path(__file__).resolve().parents[1]
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'


class PosterRebuildTests(unittest.TestCase):
    def test_landscape_reflow_preserves_reviewed_content(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'rebuilt.pptx'
            subprocess.run([sys.executable, str(ROOT/'posters/build_landscape.py'),
                            '--output', str(output)], cwd=ROOT, check=True,
                           capture_output=True, text=True)
            with ZipFile(ROOT/'CUPC_Poster_portrait_36x48.pptx') as portrait, \
                 ZipFile(ROOT/'CUPC_Poster.pptx') as reviewed, ZipFile(output) as rebuilt:
                self.assertEqual(reviewed.read('ppt/slides/slide1.xml'),
                                 rebuilt.read('ppt/slides/slide1.xml'))
                source = ET.fromstring(portrait.read('ppt/slides/slide1.xml'))
                actual = ET.fromstring(rebuilt.read('ppt/slides/slide2.xml'))
                words = lambda root: Counter(' '.join((n.text or '').split())
                                             for n in root.iter(A+'t'))
                self.assertEqual(words(source), words(actual))
                math = lambda root: [ET.tostring(n) for n in root.iter(M+'oMath')]
                self.assertTrue(math(source), 'Native equation must remain present')
                self.assertEqual(math(source), math(actual))
                for name in ('image2.png', 'image3.png', 'image7.png'):
                    media = 'ppt/media/landscape_current_'+name
                    expected = np.asarray(Image.open(BytesIO(reviewed.read(media))).convert('RGBA'))
                    generated = np.asarray(Image.open(BytesIO(rebuilt.read(media))).convert('RGBA'))
                    self.assertEqual(expected.shape, generated.shape)
                    np.testing.assert_array_equal(expected[..., 3], generated[..., 3])
                    self.assertLessEqual(int(np.max(np.abs(expected[..., :3].astype(int)
                                                           - generated[..., :3].astype(int)))), 3)

    def test_changed_scientific_input_stops_poster_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'posters').mkdir()
            (root/'posters/inputs.json').write_text('{"sha256":{"input.csv":"reviewed-hash"}}')
            (root/'input.csv').write_text('changed scientific value\n')
            with patch.object(render_figures, 'ROOT', root):
                with self.assertRaisesRegex(ValueError, 'Poster input changed: input.csv'):
                    render_figures.verify_inputs()


if __name__ == '__main__':
    unittest.main()
