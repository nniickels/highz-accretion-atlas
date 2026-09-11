"""PDF compression may change; scientific marks and resources must not."""
from pathlib import Path
import tempfile
import unittest

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError
from pypdf.generic import (
    DecodedStreamObject, DictionaryObject, NameObject, NumberObject, TextStringObject,
)

from src.internal.verify_regenerated_artifacts import compare_artifact, verify_against


def write_figure(path, *, compress=False, padding=False, label='1.200',
                 endpoint=100, width=200, pixel=20, glyph=10):
    writer = PdfWriter()
    if padding:
        writer._add_object(TextStringObject('unused object changes reference numbers'))
    page = writer.add_blank_page(width=width, height=200)
    content = DecodedStreamObject()
    content.set_data(f'0 0 m {endpoint} 100 l S BT /F1 12 Tf 10 20 Td ({label}) Tj ET'.encode())
    image = DecodedStreamObject()
    image.set_data(bytes([pixel, 50, 70]))
    image.update({NameObject('/Type'): NameObject('/XObject'),
                  NameObject('/Subtype'): NameObject('/Image'),
                  NameObject('/Width'): NumberObject(1),
                  NameObject('/Height'): NumberObject(1),
                  NameObject('/ColorSpace'): NameObject('/DeviceRGB'),
                  NameObject('/BitsPerComponent'): NumberObject(8)})
    # A font's glyph programs must be checked even when page commands agree.
    charproc = DecodedStreamObject()
    charproc.set_data(f'0 0 m {glyph} 10 l S'.encode())
    font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                             NameObject('/Subtype'): NameObject('/Type3'),
                             NameObject('/CharProcs'): DictionaryObject({
                                 NameObject('/one'): writer._add_object(charproc)})})
    page[NameObject('/Resources')] = DictionaryObject({
        NameObject('/Font'): DictionaryObject({NameObject('/F1'): writer._add_object(font)}),
        NameObject('/XObject'): DictionaryObject({
            NameObject('/Im1'): writer._add_object(image.flate_encode() if compress else image)}),
    })
    page[NameObject('/Contents')] = writer._add_object(content.flate_encode() if compress else content)
    writer.write(path)


class PdfReproductionTests(unittest.TestCase):
    def test_encoding_and_object_numbers_do_not_affect_comparison(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a.pdf', Path(directory)/'b.pdf'
            write_figure(a)
            write_figure(b, compress=True, padding=True)
            self.assertNotEqual(a.read_bytes(), b.read_bytes())
            compare_artifact(a, b)

    def test_changed_figure_content_and_geometry_are_rejected(self):
        for changes in ({'label': '1.201'}, {'endpoint': 101}, {'pixel': 21},
                        {'glyph': 11}, {'width': 201}):
            with self.subTest(changes=changes), tempfile.TemporaryDirectory() as directory:
                baseline, generated = Path(directory)/'baseline', Path(directory)/'generated'
                for root in (baseline, generated):
                    (root/'paper/figures').mkdir(parents=True)
                a, b = [root/'paper/figures/early_start_comparison.pdf'
                        for root in (baseline, generated)]
                write_figure(a)
                write_figure(b, compress=True, **changes)
                with self.assertRaisesRegex(AssertionError, 'PDF'):
                    verify_against(baseline, generated)

    def test_missing_resource_and_invalid_pdf_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a.pdf', Path(directory)/'b.pdf'
            write_figure(a)
            writer = PdfWriter(clone_from=PdfReader(a))
            del writer.pages[0]['/Resources']['/XObject']
            writer.write(b)
            with self.assertRaisesRegex(AssertionError, 'keys differ'):
                compare_artifact(a, b)
            b.write_bytes(b'not a PDF')
            with self.assertRaises(PdfReadError):
                compare_artifact(a, b)

    def test_real_manuscript_pdf_survives_stream_recompression(self):
        source = Path(__file__).resolve().parents[1]/'paper/figures/compatibility.pdf'
        with tempfile.TemporaryDirectory() as directory:
            rewritten = Path(directory)/'compatibility.pdf'
            writer = PdfWriter(clone_from=PdfReader(source))
            for page in writer.pages:
                page.compress_content_streams(level=0)
            writer.write(rewritten)
            self.assertNotEqual(source.read_bytes(), rewritten.read_bytes())
            compare_artifact(source, rewritten)
