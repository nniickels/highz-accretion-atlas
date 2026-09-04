"""Log aggregate rendering errors only; never accept or upload new baselines."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops
from src.internal.verify_regenerated_artifacts import ARTIFACT_ROOTS


def report(baseline: Path, generated: Path) -> None:
    histogram = np.zeros(256, dtype=np.int64)
    maximum_rms = 0.0
    count = missing = dimensions = 0
    old_limit = Image.MAX_IMAGE_PIXELS
    try:
        Image.MAX_IMAGE_PIXELS = None
        for root in ARTIFACT_ROOTS:
            for expected in sorted((baseline/root).rglob('*.png')):
                actual = generated/expected.relative_to(baseline)
                if not actual.exists():
                    missing += 1
                    continue
                with Image.open(expected) as a, Image.open(actual) as b:
                    if a.size != b.size:
                        dimensions += 1
                        continue
                    local = np.zeros(256, dtype=np.int64)
                    for y in range(0, a.height, 256):
                        box = (0, y, a.width, min(y+256, a.height))
                        delta = ImageChops.difference(a.crop(box).convert('RGB'),
                                                     b.crop(box).convert('RGB'))
                        local += np.asarray(delta.histogram()).reshape(3, 256).sum(axis=0)
                    rms = float(np.sqrt(np.dot(local, np.arange(256, dtype=np.float64)**2)/local.sum()))
                    maximum_rms = max(maximum_rms, rms)
                    histogram += local
                    count += 1
        print('Compared images:', count, 'missing:', missing, 'dimension mismatches:', dimensions)
        print('Maximum image RMS:', maximum_rms)
        print('RGB absolute-error histogram:', {i:int(n) for i,n in enumerate(histogram) if n})
    finally:
        Image.MAX_IMAGE_PIXELS = old_limit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('generated', type=Path)
    args = parser.parse_args()
    report(args.baseline, args.generated)
