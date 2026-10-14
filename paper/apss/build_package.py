"""Rebuild the Ap&SS manuscript and archives; record hashes only after review."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import subprocess
import zipfile

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
SUPPLEMENT = {
    'calibration_sensitivity.py': 'src/internal/calibration_sensitivity.py',
    'target_robustness.csv': 'results/manuscript/tables/target_robustness.csv',
    'calibration_sensitivity.csv': 'results/manuscript/tables/calibration_sensitivity.csv',
    'core.txt': 'requirements/core.txt',
}


def archive(path, entries):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as output:
        for name, contents in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 14, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(info, contents)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record-reviewed-hashes', action='store_true')
    args = parser.parse_args()
    for name, source in SUPPLEMENT.items():
        (PACKAGE / 'supplementary' / name).write_bytes((REPO / source).read_bytes())
    with (REPO / SUPPLEMENT['calibration_sensitivity.csv']).open() as stream:
        values = {(r['object_id'], float(r['mass_offset_dex'])): r for r in csv.DictReader(stream)}
    def probability(value):
        value = float(value)
        return '$>0.999$' if value > .999 else '$<0.001$' if value < .001 else f'{value:.3f}'
    rows = []
    for name in ('RUBIES-EGS-55604', 'J0910_2028_12910'):
        cells = [probability(values[name, offset][column]) for offset in (0., -.5)
                 for column in ('probability_reported_exact', 'probability_with_calibration')]
        rows.append(name.replace('_', r'\_') + ' & ' + ' & '.join(cells) + r' \\')
    (PACKAGE / 'tables/calibration_rows.tex').write_text('\n'.join(rows) + '\n')
    subprocess.run(['tectonic', '-X', 'compile', 'main.tex', '--keep-logs'], cwd=PACKAGE, check=True)
    source = (PACKAGE / 'main.tex').read_text().replace('{figures/', '{').replace('{tables/', '{')
    assets = sorted((PACKAGE / 'figures').glob('*.pdf')) + sorted((PACKAGE / 'tables').glob('*.tex'))
    entries = {'main.tex': source.encode()}
    for item in assets:
        if item.name in entries:
            raise ValueError(f'Duplicate flattened filename: {item.name}')
        entries[item.name] = item.read_bytes()
    archive(PACKAGE / 'apss_source.zip', entries)
    supplement_names = [*SUPPLEMENT, 'README.md']
    archive(PACKAGE / 'apss_supplementary.zip', {
        n: (PACKAGE / 'supplementary' / n).read_bytes() for n in supplement_names})
    if args.record_reviewed_hashes:
        manifest_path = PACKAGE / 'reproducibility_manifest.json'
        manifest = json.loads(manifest_path.read_text())
        files = [PACKAGE / n for n in ('main.tex', 'main.pdf', 'apss_source.zip',
                                      'apss_supplementary.zip', 'verify_package.py', 'build_package.py')]
        files += assets + [PACKAGE / 'supplementary' / n for n in supplement_names]
        manifest['package_sha256'] = {
            str(p.relative_to(PACKAGE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        manifest['supplementary_sources'] = SUPPLEMENT
        manifest['calibration_scope'] = 'Separate two-object Gaussian-scatter test; baseline unchanged'
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
