"""Render or independently verify the shared manuscript figure variants.

The scientific inputs and track-selection algorithm are unchanged. Only the
outlined targets and efficiency-boundary target selection differ from the
canonical selected-sample exports. Both manuscript editions use these variants;
local manuscript dependencies remain Git-ignored.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile

from src.internal.pdf_reproduction import compare_pdf
from src.internal.publication_figures import ROOT, render_figures


FIGURES = ('growth_tracks', 'growth_boundaries')
# Five primary objects retaining P >= 0.95 at -0.5 dex under reported errors,
# plus the expanded-sample UV-mass comparison. Offsets are display choices.
HIGHLIGHT_OFFSETS = {
    'CAPERS-LRD-z9': (12, -24),
    'CANUCS-LRD-z8.6': (14, -6),
    'UNCOVER-20466': (-18, 25),
    'COSMOS3D-13852': (12, 12),
    'RUBIES-EGS-55604': (-12, 6),
    'GN-z11': (12, -20),
}
BOUNDARY_TARGETS = (
    ('CAPERS-LRD-z9', '#0072B2', '-'),
    ('CANUCS-LRD-z8.6', '#009E73', '--'),
    ('UNCOVER-20466', '#CC79A7', '-.'),
    ('COSMOS3D-13852', '#874194', ':'),
    ('RUBIES-EGS-55604', '#555555', '-'),
    ('GN-z11', '#D55E00', '--'),
)


def render_apss_figures(root=ROOT, destination=None, *, verify=False):
    destination = Path(destination) if destination is not None else root/'paper/apss/figures'
    with tempfile.TemporaryDirectory(prefix='apss-figure-render-') as folder:
        generated = Path(folder)
        render_figures(root, generated, growth_highlights=HIGHLIGHT_OFFSETS,
                       boundary_targets=BOUNDARY_TARGETS, formats=('pdf',))
        if verify:
            for name in FIGURES:
                compare_pdf(destination/f'{name}.pdf', generated/f'{name}.pdf')
        else:
            destination.mkdir(parents=True, exist_ok=True)
            for name in FIGURES:
                shutil.copyfile(generated/f'{name}.pdf', destination/f'{name}.pdf')
    print(('Verified' if verify else 'Rendered') + ' two manuscript figure variants; canonical exports unchanged.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--destination', type=Path)
    args = parser.parse_args()
    render_apss_figures(destination=args.destination, verify=args.verify)


if __name__ == '__main__':
    main()
