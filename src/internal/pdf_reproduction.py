"""Compare PDF object graphs after decoding storage-level compression.

Object numbers, xref offsets and stream compression are serialization details.
Page content, font programs, image samples and all other document properties
remain exact. No rasterization or pixel tolerance is used for PDFs.
"""
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject, StreamObject


def compare_pdf(expected: Path, actual: Path) -> None:
    readers = [PdfReader(path, strict=True) for path in (expected, actual)]
    visited = set()

    def compare(left, right, location):
        # Parent links in the PDF page tree form cycles. Compare each pair once.
        if isinstance(left, IndirectObject) and isinstance(right, IndirectObject):
            pair = (left.idnum, left.generation, right.idnum, right.generation)
            if pair in visited:
                return
            visited.add(pair)
        left, right = left.get_object(), right.get_object()
        if isinstance(left, StreamObject) and isinstance(right, StreamObject):
            if left.get_data() != right.get_data():
                raise AssertionError(f'{actual}: PDF decoded stream differs at {location}')
            # The decoded bytes above replace these encoding-specific properties.
            ignored = {'/Length', '/Filter', '/DecodeParms'}
        else:
            ignored = set()
            if isinstance(left, StreamObject) != isinstance(right, StreamObject):
                raise AssertionError(f'{actual}: PDF stream type differs at {location}')
        if isinstance(left, DictionaryObject) and isinstance(right, DictionaryObject):
            keys = set(left) - ignored
            if keys != set(right) - ignored:
                raise AssertionError(f'{actual}: PDF dictionary keys differ at {location}')
            for key in sorted(keys):
                compare(left.raw_get(key), right.raw_get(key), f'{location}{key}')
        elif isinstance(left, ArrayObject) and isinstance(right, ArrayObject):
            if len(left) != len(right):
                raise AssertionError(f'{actual}: PDF array length differs at {location}')
            for index, (a, b) in enumerate(zip(left, right)):
                compare(a, b, f'{location}[{index}]')
        elif type(left) is not type(right) or left != right:
            raise AssertionError(f'{actual}: PDF value differs at {location}')

    for key in ('/Root', '/Info'):
        present = [key in reader.trailer for reader in readers]
        if present[0] != present[1]:
            raise AssertionError(f'{actual}: PDF trailer {key} membership differs')
        if present[0]:
            compare(*(reader.trailer.raw_get(key) for reader in readers), key)
