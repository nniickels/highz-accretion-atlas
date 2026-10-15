"""Rebuild scientific figures in the reviewed landscape poster.

The committed PPTX files are editable text/layout inputs. Scientific values are
read only. Rebuilding retains the reviewed landscape layout and formatting,
checks its text against the portrait edition, and regenerates both science plots.
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


def first(node, namespace, name):
    return node.getElementsByTagNameNS(namespace, name)[0]


def text_content(node):
    return ''.join(child.data for child in node.childNodes
                   if child.nodeType in (child.TEXT_NODE, child.CDATA_SECTION_NODE))


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


def paragraph_contract(document):
    """Ignore run splits and whitespace introduced by PowerPoint restyling."""
    return Counter(' '.join(''.join(text_content(t) for t in p.getElementsByTagNameNS(A, 't')).split())
                   for p in document.getElementsByTagNameNS(A, 'p')
                   if any(text_content(t).strip() for t in p.getElementsByTagNameNS(A, 't')))


def picture_media(data, slide_part, identity):
    document = minidom.parseString(data[slide_part])
    picture = next(node for node in document.getElementsByTagNameNS(P, 'pic')
                   if first(node, P, 'cNvPr').getAttribute('id') == str(identity))
    embed = first(picture, A, 'blip').getAttributeNS(R, 'embed')
    relationships = minidom.parseString(data[relationship_part(slide_part)])
    target = next(node.getAttribute('Target')
                  for node in relationships.getElementsByTagName('Relationship')
                  if node.getAttribute('Id') == embed)
    return posixpath.normpath(posixpath.dirname(slide_part) + '/' + target)


def build(output: Path):
    if output.exists():
        raise FileExistsError(f'Choose a new output path: {output}')
    with ZipFile(ROOT/'posters/48x36.pptx') as archive:
        data = {name: archive.read(name) for name in archive.namelist()}
    with ZipFile(ROOT/'posters/36x48.pptx') as archive:
        source = {name: archive.read(name) for name in archive.namelist()}
    target_part = poster_slide_part(data)
    portrait = minidom.parseString(source[poster_slide_part(source)])
    landscape = minidom.parseString(data[target_part])
    if paragraph_contract(portrait) != paragraph_contract(landscape):
        raise ValueError('Portrait and landscape poster text differs; reconcile the reviewed editions first')
    math = lambda doc: [node.toxml() for node in doc.getElementsByTagNameNS(M, 'oMath')]
    if math(portrait) != math(landscape):
        raise ValueError('Portrait and landscape native equations differ')
    # Both editable decks are reviewed authoring inputs. Reusing the landscape
    # XML preserves manual geometry, separate reference columns, font sizes and
    # run formatting; the former fixed positions predated those final edits.
    with tempfile.TemporaryDirectory(prefix='cupc-plot-') as temporary:
        subprocess.run([sys.executable, '-m', 'src.internal.poster_figures',
                        '--output-dir', temporary], cwd=ROOT, check=True)
        data[picture_media(data, target_part, 14)] = (Path(temporary)/'onset.png').read_bytes()
        subprocess.run([sys.executable, '-m', 'src.internal.poster_figures',
                        '--output-dir', temporary, '--landscape-uncertainty-only'],
                       cwd=ROOT, check=True)
        data[picture_media(data, target_part, 4)] = (Path(temporary)/'uncertainty.png').read_bytes()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'w') as archive:
        for name, content in data.items():
            entry = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            archive.writestr(entry, content)
    print(f'Saved {output}; reviewed layout and text preserved, both science plots regenerated.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    build(parser.parse_args().output.resolve())
