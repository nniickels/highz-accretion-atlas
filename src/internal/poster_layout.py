"""Reflow the reviewed portrait poster into the final landscape slide.

The committed PPTX files are editable text/layout inputs. Scientific values are
read only, and the only newly rendered asset is the shorter uncertainty panel.
Uses the pinned core environment and Python's standard-library OOXML tools.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import posixpath
import subprocess
import sys
import tempfile
from xml.dom import minidom
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[2]
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
EMU = 914400

# Inches. Image heights preserve aspect ratios except the separately re-rendered
# uncertainty canvas. All paragraph styles and native Office math are retained.
POSITIONS = {
    32: (0, 0, 48, 4.8), 33: (.8, .6, 3.1, 3.1),
    36: (3.6, 1.15, 6.6, 2.381), 37: (43.6, .5, 3.4, 3.4),
    5: (32.75117060367454, 1.0074074074074073, 5.781, 4.333),
    6: (33.79117060367454, 1.752962962962963, 2.224, 1.070),
    10: (35.538, -.203, 8.958, 5.040),
    69: (1, 5.6, 14.75, 1.05), 70: (1.5, 7, 13.75, 3.55),
    71: (1, 5.6, 14.75, 5.1), 72: (1, 11.25, 14.75, 1.05),
    73: (1.5, 12.65, 13.75, 15.7), 74: (1, 11.25, 14.75, 17.6),
    81: (1, 29.4, 14.75, 1.05), 82: (1.5, 30.8, 13.75, 4.05),
    83: (1, 29.4, 14.75, 5.85),
    7: (16.35, 5.6, 30.65, 1.05), 11: (16.35, 5.6, 30.65, 17.45),
    2: (16.7, 7, 14.65, 6), 4: (16.5, 14.05, 14.8, 7.6),
    110: (16.85, 21.7, 14, 1), 76: (32.5, 7, 14, 2.2),
    14: (32.1, 9.4, 14.8, 9.99), 112: (32.5, 19.5, 14, .6),
    15: (32.5, 20.15, 14, 2.75), 78: (32, 23.35, 15, 1.05),
    79: (32.5, 24.75, 14, 9.85), 80: (32, 23.35, 15, 11.9),
    120: (16.65, 23.35, 14.35, .7), 3: (16.6, 24.25, 14.5, 10.106),
    111: (16.65, 34.4, 14.35, .85),
}


def first(node, namespace, name):
    return node.getElementsByTagNameNS(namespace, name)[0]


def text_content(node):
    return ''.join(child.data for child in node.childNodes
                   if child.nodeType in (child.TEXT_NODE, child.CDATA_SECTION_NODE))


def text_contract(document):
    return Counter(' '.join(text_content(node).split())
                   for node in document.getElementsByTagNameNS(A, 't'))


def poster_slide_part(data):
    """Select the only slide, or the last version in an older multi-slide deck."""
    presentation = minidom.parseString(data['ppt/presentation.xml'])
    identity = presentation.getElementsByTagNameNS(P, 'sldId')[-1].getAttributeNS(R, 'id')
    relationships = minidom.parseString(data['ppt/_rels/presentation.xml.rels'])
    relationship = next(node for node in relationships.documentElement.childNodes
                        if node.nodeType == node.ELEMENT_NODE
                        and node.getAttribute('Id') == identity)
    return posixpath.normpath('ppt/' + relationship.getAttribute('Target'))


def relationship_part(part):
    directory, name = posixpath.split(part)
    return directory + '/_rels/' + name + '.rels'


def build(output: Path):
    if output.exists():
        raise FileExistsError(f'Choose a new output path: {output}')
    with ZipFile(ROOT/'posters/48x36.pptx') as archive:
        data = {name: archive.read(name) for name in archive.namelist()}
    with ZipFile(ROOT/'posters/36x48.pptx') as archive:
        source = {name: archive.read(name) for name in archive.namelist()}
    source_part = poster_slide_part(source)
    target_part = poster_slide_part(data)
    target_relationships = minidom.parseString(data[relationship_part(target_part)])
    note_target = next(node.getAttribute('Target')
                       for node in target_relationships.documentElement.childNodes
                       if node.nodeType == node.ELEMENT_NODE
                       and node.getAttribute('Type').endswith('/notesSlide'))
    document = minidom.parseString(source[source_part])
    expected_text = text_contract(document)
    expected_math = [node.toxml() for node in document.getElementsByTagNameNS(M, 'oMath')]
    if not expected_math:
        raise ValueError('Portrait poster lacks its native growth equation')
    landscape_document = minidom.parseString(data[target_part])
    # Preserve existing artwork placements exactly, rather than accumulating offsets.
    landscape_pictures = {
        int(first(node, P, 'cNvPr').getAttribute('id')): node
        for node in landscape_document.getElementsByTagNameNS(P, 'pic')
    }
    shapes = list(document.getElementsByTagNameNS(P, 'sp'))
    pictures = list(document.getElementsByTagNameNS(P, 'pic'))
    for node in shapes + pictures:
        identity = int(first(node, P, 'cNvPr').getAttribute('id'))
        transform = first(first(node, P, 'spPr'), A, 'xfrm')
        if identity in (5, 6, 10):
            old_transform = first(first(landscape_pictures[identity], P, 'spPr'), A, 'xfrm')
            transform.parentNode.replaceChild(document.importNode(old_transform, deep=True), transform)
            continue
        if identity not in POSITIONS:
            raise ValueError(f'New poster object needs a landscape position: {identity}')
        x, y, width, height = POSITIONS[identity]
        offset, extent = first(transform, A, 'off'), first(transform, A, 'ext')
        if node.localName == 'pic' and identity != 4:
            height = width * int(extent.getAttribute('cy')) / int(extent.getAttribute('cx'))
        for target, key, value in ((offset, 'x', x), (offset, 'y', y),
                                   (extent, 'cx', width), (extent, 'cy', height)):
            target.setAttribute(key, str(round(value * EMU)))
        if identity == 32:
            body = first(node, A, 'bodyPr')
            for key, value in (('lIns', 10.3), ('rIns', 13), ('tIns', .1)):
                body.setAttribute(key, str(round(value * EMU)))
            for text in node.getElementsByTagNameNS(A, 't'):
                if text.firstChild:
                    text.firstChild.data = text.firstChild.data.replace('Growth\nConstraints', 'Growth Constraints')
    relationships = minidom.parseString(source[relationship_part(source_part)])
    uncertainty_id = first(next(node for node in pictures
                                if first(node, P, 'cNvPr').getAttribute('id') == '4'),
                           A, 'blip').getAttributeNS(R, 'embed')
    uncertainty_media = None
    for relationship in relationships.documentElement.childNodes:
        if relationship.nodeType != relationship.ELEMENT_NODE:
            continue
        kind = relationship.getAttribute('Type').rsplit('/', 1)[-1]
        target = relationship.getAttribute('Target')
        if kind == 'image':
            key = 'ppt/' + target.removeprefix('../')
            name = 'landscape_current_' + Path(key).name
            data['ppt/media/' + name] = source[key]
            relationship.setAttribute('Target', '../media/' + name)
            if relationship.getAttribute('Id') == uncertainty_id:
                uncertainty_media = 'ppt/media/' + name
        elif kind == 'notesSlide':
            source_note_part = posixpath.normpath(posixpath.dirname(source_part) + '/' + target)
            target_note_part = posixpath.normpath(posixpath.dirname(target_part) + '/' + note_target)
            data[target_note_part] = source[source_note_part]
            relationship.setAttribute('Target', note_target)
    with tempfile.TemporaryDirectory(prefix='cupc-plot-') as temporary:
        subprocess.run([sys.executable, '-m', 'src.internal.poster_figures',
                        '--output-dir', temporary, '--landscape-uncertainty-only'],
                       cwd=ROOT, check=True)
        if uncertainty_media is None:
            raise ValueError('Missing uncertainty plot relationship')
        data[uncertainty_media] = (Path(temporary)/'uncertainty.png').read_bytes()
    if text_contract(document) != expected_text:
        raise ValueError('Poster text changed during layout conversion')
    if [node.toxml() for node in document.getElementsByTagNameNS(M, 'oMath')] != expected_math:
        raise ValueError('Native growth equation changed during conversion')
    data[target_part] = document.toxml(encoding='UTF-8')
    data[relationship_part(target_part)] = relationships.toxml(encoding='UTF-8')
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'w') as archive:
        for name, content in data.items():
            entry = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            archive.writestr(entry, content)
    print(f'Saved {output}; other slides, poster wording and native equation preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    build(parser.parse_args().output.resolve())
