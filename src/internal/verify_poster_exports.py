"""Verify reviewed PDF/source pairs without regenerating or blessing exports."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import posixpath
import unicodedata
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from pypdf import PdfReader

from src.internal.poster_layout import poster_slide_parts, relationship_part
from src.internal.poster_figures import verify_inputs

ROOT = Path(__file__).resolve().parents[2]
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'


def slide_fingerprint(data, part):
    """Hash a slide and its linked package parts, including images and notes."""
    visited = set()

    def visit(name):
        if name in visited:
            return
        visited.add(name)
        rel = relationship_part(name)
        if rel not in data:
            return
        visited.add(rel)
        for node in ET.fromstring(data[rel]):
            if node.get('TargetMode') != 'External':
                target = node.get('Target')
                visit(target.lstrip('/') if target.startswith('/') else
                      posixpath.normpath(posixpath.dirname(name)+'/'+target))

    visit(part)
    digest = hashlib.sha256()
    for name in sorted(visited):
        digest.update(name.encode()+b'\0')
        digest.update(hashlib.sha256(data[name]).digest())
    return digest.hexdigest()


def text_characters(text):
    # Exporters concatenate adjacent text boxes differently. Ignore whitespace,
    # bullet glyphs and punctuation, but retain all letters, digits and Greek
    # symbols. Reviewed byte hashes, not this coverage check, detect every edit.
    return Counter(c for c in unicodedata.normalize('NFKC', text) if c.isalnum())


def font_is_embedded(font):
    font = font.get_object()
    children = font.get('/DescendantFonts')
    if children:
        return all(font_is_embedded(child) for child in children)
    descriptor = font.get('/FontDescriptor')
    return bool(descriptor and any(key in descriptor.get_object()
                                  for key in ('/FontFile', '/FontFile2', '/FontFile3')))


def verify_exports(root=ROOT):
    root = Path(root)
    manifest = json.loads((root/'data/poster_exports.json').read_text())
    if manifest['schema_version'] != 2:
        raise ValueError('Unsupported poster export manifest version')
    for entry in manifest['exports']:
        for name, key in ((entry['source'], 'source_sha256'), (entry['pdf'], 'pdf_sha256')):
            actual = hashlib.sha256((root/name).read_bytes()).hexdigest()
            if actual != entry[key]:
                raise ValueError(f'Reviewed poster artifact changed: {name}. Review the changed slides and their export mapping before updating hashes.')
        with ZipFile(root/entry['source']) as archive:
            if archive.testzip() is not None:
                raise ValueError(f'Invalid poster package: {entry["source"]}')
            data = {name: archive.read(name) for name in archive.namelist()}
            parts = poster_slide_parts(data)
            exported_part = parts[entry['exported_slide']-1]
            if slide_fingerprint(data, exported_part) != entry['exported_slide_sha256']:
                raise ValueError(f'PDF source slide changed: {entry["source"]}. Re-export and review before updating its fingerprint.')
            size = ET.fromstring(data['ppt/presentation.xml']).find(P+'sldSz')
            source_size = tuple(int(size.get(key))/914400 for key in ('cx', 'cy'))
            source_text = ''.join(n.text or '' for n in
                                  ET.fromstring(data[exported_part]).iter(A+'t'))
        reader = PdfReader(root/entry['pdf'])
        if reader.is_encrypted or len(reader.pages) != 1:
            raise ValueError(f'Expected an unencrypted one-page poster: {entry["pdf"]}')
        page = reader.pages[0]
        pdf_size = (float(page.mediabox.width)/72, float(page.mediabox.height)/72)
        expected = tuple(entry['page_size_inches'])
        if source_size != expected or pdf_size != expected or page.rotation != 0:
            raise ValueError(f'Poster dimensions differ from the reviewed source: {entry["pdf"]}')
        if tuple(page.cropbox) != tuple(page.mediabox):
            raise ValueError(f'Poster PDF crops its page: {entry["pdf"]}')
        if text_characters(source_text) != text_characters(page.extract_text()):
            raise ValueError(f'Poster PDF text coverage differs from its source: {entry["pdf"]}')
        font_resource = page['/Resources'].get_object().get('/Font')
        fonts = font_resource.get_object() if font_resource is not None else {}
        if not fonts or not all(font_is_embedded(font) for font in fonts.values()):
            raise ValueError(f'Poster PDF contains an unembedded font: {entry["pdf"]}')
    return len(manifest['exports'])


if __name__ == '__main__':
    verify_inputs()
    count = verify_exports()
    print(f'Verified {count} reviewed poster PDF/source pairs, dimensions, text coverage and embedded fonts; scientific input hashes unchanged.')
