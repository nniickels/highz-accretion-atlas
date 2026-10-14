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
# uncertainty canvas. Left: Introduction and Methods. Upper right: Results.
# Lower right: Conclusions, then References. Text styles are retained.
POSITIONS = {
    32: (0, 0, 48, 4.8),
    33: (0.8, 0.6, 3.1, 3.1),
    36: (3.6, 1.15, 6.6, 2.381),
    37: (43.6, 0.5, 3.4, 3.4),
    5: (32.75117060367454, 1.0074074074074073, 5.781, 4.333),
    6: (33.79117060367454, 1.752962962962963, 2.224, 1.07),
    10: (35.538, -0.203, 8.958, 5.04),
    69: (1, 5.6, 16, 1.05),
    70: (1.5, 7, 15, 3.55),
    71: (1, 5.6, 16, 5.1),
    72: (1, 11.25, 16, 1.05),
    73: (1.5, 20, 15.3, 3.6),
    74: (1, 11.25, 16, 24.3),
    81: (17.5, 30, 29.5, 1.05),
    82: (18, 31.4, 28.5, 3.45),
    83: (17.5, 30, 29.5, 5.25),
    7: (17.5, 5.6, 29.5, 1.05),
    11: (17.5, 5.6, 29.5, 17.65),
    2: (17.85, 7, 14.4, 7.8),
    4: (17.65, 15.05, 14.8, 7.6),
    76: (33, 7, 13.6, 2.2),
    14: (32.5, 9.4, 14.8, 9.99),
    112: (33, 19.5, 13.6, 0.6),
    15: (33, 20.15, 13.6, 2.95),
    78: (17.5, 23.85, 29.5, 1.05),
    79: (18, 25.25, 28.5, 4.4),
    80: (17.5, 23.85, 29.5, 5.9),
    120: (1.5, 23.8, 15.3, 0.7),
    3: (1.5, 12.55, 15.3, 0.7),
    200: (1.5, 13.3, 15.3, 0.85),
    201: (8.96, 14.2, 0.38, 0.28),
    202: (1.5, 14.55, 15.3, 0.7),
    203: (6.05, 15.3, 0.38, 0.28),
    204: (13.925, 15.3, 0.38, 0.28),
    205: (1.5, 15.68, 9.486, 4.1),
    206: (1.56, 15.7, 9.366, 0.7),
    207: (1.7, 16.45, 9.086, 1),
    208: (1.7, 17.5, 9.086, 2.2),
    209: (11.436, 15.68, 5.364, 4.1),
    210: (1.5, 24.75, 15.3, 1.15),
    211: (4.985, 25.93, 0.38, 0.26),
    212: (12.935, 25.93, 0.38, 0.26),
    213: (1.5, 26.25, 7.35, 1),
    214: (9.45, 26.25, 7.35, 1),
    215: (4.985, 27.3, 0.38, 0.26),
    216: (12.935, 27.3, 0.38, 0.26),
    217: (1.5, 27.65, 15.3, 2.25),
    218: (1.5, 28.85, 15.3, 1),
    219: (4.985, 29.95, 0.38, 0.26),
    220: (12.935, 29.95, 0.38, 0.26),
    221: (1.5, 30.3, 7.35, 1.25),
    222: (9.45, 30.3, 7.35, 1.25),
    223: (1.5, 31.85, 15.3, 1.65),
    224: (1.5, 33.75, 15.3, 1.65),
}


def first(node, namespace, name):
    return node.getElementsByTagNameNS(namespace, name)[0]


def text_content(node):
    return ''.join(child.data for child in node.childNodes
                   if child.nodeType in (child.TEXT_NODE, child.CDATA_SECTION_NODE))


def text_contract(document):
    return Counter(' '.join(text_content(node).split())
                   for node in document.getElementsByTagNameNS(A, 't'))


def poster_slide_parts(data):
    """Resolve slides in presentation order, including full and overview versions."""
    presentation = minidom.parseString(data['ppt/presentation.xml'])
    relationships = minidom.parseString(data['ppt/_rels/presentation.xml.rels'])
    targets = {node.getAttribute('Id'): node.getAttribute('Target')
               for node in relationships.documentElement.childNodes
               if node.nodeType == node.ELEMENT_NODE}
    return [posixpath.normpath('ppt/' + targets[node.getAttributeNS(R, 'id')])
            for node in presentation.getElementsByTagNameNS(P, 'sldId')]


def poster_slide_part(data):
    """Select the last editable poster version, preserving earlier slides."""
    return poster_slide_parts(data)[-1]


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
    # The final overview explains growth in words. If an earlier full version
    # is present, it must retain its native equation.
    full_document = minidom.parseString(source[poster_slide_parts(source)[0]])
    if len(poster_slide_parts(source)) > 1 and not full_document.getElementsByTagNameNS(M, 'oMath'):
        raise ValueError('Full portrait poster lacks its native growth equation')
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
