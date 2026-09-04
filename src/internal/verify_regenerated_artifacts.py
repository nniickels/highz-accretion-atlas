"""Compare regenerated products to an independent baseline before refreshing hashes.

CSV values use the shared cross-platform numeric tolerance; PNG RGB channels
allow at most two 8-bit levels of rasterization roundoff at the same pixel.
Image dimensions and alpha remain exact; --exact-pixels also requires exact RGB.
The default baseline is Git HEAD, never the just-regenerated files. CI archive
checkouts use HIGHZ_BASELINE_ROOT.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import subprocess
import tempfile

import pandas as pd
from PIL import Image, ImageChops

from src.internal.dataset_manifests import write_manifests
from src.internal.reproduction import assert_frames_semantically_equal

ROOT = Path(__file__).resolve().parents[2]
# Absolute channel bound: no averaging, spatial shifts, resizing, or blurring.
PNG_CHANNEL_ATOL = 2
VERSIONS = ('v1', 'v2', 'v3')
ARTIFACT_ROOTS = [f'{base}/{v}' for v in VERSIONS for base in ('data/processed', 'data/crossmatch', 'results')]


def compare_artifact(expected: Path, actual: Path, *, exact_pixels: bool = False) -> None:
    if expected.suffix == '.csv':
        assert_frames_semantically_equal(pd.read_csv(expected), pd.read_csv(actual), label=str(actual))
    elif expected.suffix == '.png':
        # These are trusted repository-generated atlases, including the 131-Mpixel gallery.
        old_limit = Image.MAX_IMAGE_PIXELS
        try:
            Image.MAX_IMAGE_PIXELS = None
            with Image.open(expected) as left, Image.open(actual) as right:
                if left.size != right.size:
                    raise AssertionError(f'{actual}: image dimensions changed {left.size} -> {right.size}')
                for y in range(0, left.height, 256):
                    box = (0, y, left.width, min(y + 256, left.height))
                    left_strip = left.crop(box).convert('RGBA')
                    right_strip = right.crop(box).convert('RGBA')
                    difference = ImageChops.difference(left_strip, right_strip).convert('RGB')
                    maximum = max(high for low, high in difference.getextrema())
                    tolerance = 0 if exact_pixels else PNG_CHANNEL_ATOL
                    if maximum > tolerance:
                        raise AssertionError(
                            f'{actual}: rendered pixels differ; maximum RGB channel '
                            f'difference={maximum}, allowed={tolerance}, strip_y={y}, '
                            f'local_difference_bounds={difference.getbbox()}'
                        )
                    if left_strip.getchannel('A').tobytes() != right_strip.getchannel('A').tobytes():
                        raise AssertionError(f'{actual}: image transparency differs')
        finally:
            Image.MAX_IMAGE_PIXELS = old_limit
    elif expected.read_bytes() != actual.read_bytes():
        raise AssertionError(f'{actual}: bytes differ')


@contextmanager
def git_baseline(root: Path):
    """Export committed canonical artifacts without using the worktree as truth."""
    with tempfile.TemporaryDirectory(prefix='highz-baseline-') as directory:
        baseline = Path(directory)
        names = subprocess.check_output(['git', '-C', str(root), 'ls-tree', '-r', '--name-only', 'HEAD', '--', *ARTIFACT_ROOTS], text=True).splitlines()
        for name in names:
            path = baseline / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('wb') as output:
                subprocess.run(['git', '-C', str(root), 'show', f'HEAD:{name}'], stdout=output, check=True)
        yield baseline


def verify_against(baseline: Path, generated: Path, *, exact_pixels: bool = False) -> int:
    def paths(root):
        return {p.relative_to(root).as_posix() for part in ARTIFACT_ROOTS for p in (root / part).rglob('*') if p.is_file() and p.name != '.DS_Store'}
    expected, actual = paths(baseline), paths(generated)
    if not expected or expected != actual:
        raise AssertionError(f'Artifact membership differs: missing={sorted(expected-actual)[:5]}, unexpected={sorted(actual-expected)[:5]}')
    for name in sorted(expected):
        compare_artifact(baseline / name, generated / name, exact_pixels=exact_pixels)
    return len(expected)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-root', type=Path, default=os.environ.get('HIGHZ_BASELINE_ROOT'))
    parser.add_argument('--exact-pixels', action='store_true', help='Require exact RGB for identical rendering environments')
    parser.add_argument('--refresh-manifests', action='store_true', help='Write manifests only after successful independent comparison')
    args = parser.parse_args()
    if args.baseline_root:
        baseline = Path(args.baseline_root).resolve()
        if baseline == ROOT.resolve():
            raise ValueError('Baseline must be independent of the generated worktree')
        count = verify_against(baseline, ROOT, exact_pixels=args.exact_pixels)
    else:
        with git_baseline(ROOT) as baseline:
            count = verify_against(baseline, ROOT, exact_pixels=args.exact_pixels)
    print(f'Verified {count} regenerated artifacts against independent baseline; '
          f'CSV values agree, PNG RGB channel tolerance={0 if args.exact_pixels else PNG_CHANNEL_ATOL}/255, '
          'dimensions and alpha exact')
    if args.refresh_manifests:
        write_manifests()


if __name__ == '__main__':
    main()
