"""Read-only submission integrity check; run from any directory with Python 3."""
from pathlib import Path
import hashlib
import re
import json
import subprocess
import zipfile

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
manifest = json.loads((PACKAGE / 'reproducibility_manifest.json').read_text())
for name, expected in manifest['package_sha256'].items():
    actual = hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f'Package file changed since review: {name}')
for name, source in manifest['canonical_figures'].items():
    supplied = (PACKAGE / name).read_bytes()
    historical = manifest.get('historical_figure_paths', {}).get(name, source)
    pinned = subprocess.check_output(['git', 'show', manifest['analysis_commit'] + ':' + historical], cwd=REPO)
    if supplied != pinned or supplied != (REPO / source).read_bytes():
        raise SystemExit(f'Figure differs from pinned scientific export: {name}')
with zipfile.ZipFile(PACKAGE / 'apss_source.zip') as archive:
    expected = {'main.tex'} | {Path(n).name for n in manifest['package_sha256'] if n.startswith(('figures/', 'tables/'))}
    if set(archive.namelist()) != expected:
        raise SystemExit('ZIP membership mismatch')
    source = (PACKAGE / 'main.tex').read_text().replace('{figures/', '{').replace('{tables/', '{')
    if archive.read('main.tex').decode() != source:
        raise SystemExit('ZIP manuscript is stale')
    for name in manifest['package_sha256']:
        if name.startswith(('figures/', 'tables/')) and archive.read(Path(name).name) != (PACKAGE / name).read_bytes():
            raise SystemExit(f'ZIP asset mismatch: {name}')
for name, source in manifest.get('supplementary_sources', {}).items():
    if (PACKAGE / 'supplementary' / name).read_bytes() != (REPO / source).read_bytes():
        raise SystemExit(f'Supplementary source is stale: {name}')
with zipfile.ZipFile(PACKAGE / 'apss_supplementary.zip') as archive:
    expected = set(manifest['supplementary_sources']) | {'README.md'}
    if set(archive.namelist()) != expected:
        raise SystemExit('Supplementary ZIP membership mismatch')
    for name in expected:
        if archive.read(name) != (PACKAGE / 'supplementary' / name).read_bytes():
            raise SystemExit(f'Supplementary ZIP is stale: {name}')
text = (PACKAGE / 'main.tex').read_text()
ordered = [r'\appendix', r'\begin{thebibliography}',
           r'\section*{Statements and declarations}', r'\section*{Figures and legends}',
           r'\section*{Tables}']
positions = [text.index(marker) for marker in ordered]
if positions != sorted(positions):
    raise SystemExit('Journal section order is incorrect')
figure_labels = re.findall(r'\\label\{(fig:[^}]+)\}', text)
table_labels = re.findall(r'\\label\{(tab:[^}]+)\}', text)
if len(figure_labels) != 8 or len(table_labels) != 9:
    raise SystemExit('Unexpected figure or table membership')
narrative = text[:positions[-2]]
for labels in (figure_labels, table_labels):
    citations = [narrative.index(r'\ref{' + label + '}') for label in labels]
    if citations != sorted(citations):
        raise SystemExit('Figure/table order differs from first narrative citation')
print('PASS: reviewed hashes, pinned figures, source ZIP and supplementary ZIP consistency.')
print('This integrity check does not replace numerical regeneration; see REPRODUCIBILITY.md.')
