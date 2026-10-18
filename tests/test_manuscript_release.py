"""Verify the public manuscript snapshot without private sources or a TeX install."""
from pathlib import Path
import csv
import re
import shutil
import subprocess
import tempfile
import unittest
from zipfile import ZipFile

from src.internal.package_overleaf import ROOT, PDF_NAME, ZIP_NAME, verify_public, package


class ManuscriptReleaseTests(unittest.TestCase):
    def copy_release(self, root):
        paper = root / 'paper'
        paper.mkdir()
        for name in (PDF_NAME, ZIP_NAME):
            shutil.copy2(ROOT / 'paper' / name, paper / name)
        return paper

    def test_public_snapshot_verifies_without_local_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.copy_release(root)
            result = verify_public(root)
            self.assertEqual(result['manuscript_verification'], 'pass')
            self.assertLess(result['references_page'], result['appendix_page'])

    def test_both_drafts_match_current_growth_scenarios(self):
        with (ROOT/'results/for_manuscript/tables/identity_exclusion_sensitivity.csv').open() as stream:
            scenarios = {row['scenario']: row for row in csv.DictReader(stream)
                         if row['scope'] == 'publication' and row['sample'] == 'primary'}
        with ZipFile(ROOT/'paper'/ZIP_NAME) as archive:
            texts = [archive.read('main.tex').decode(),
                     (ROOT/'paper/apss/main.tex').read_text()]
            for text in texts:
                prose = ' '.join(text.split())
                counts = re.search(r'central masses from (\d+) to (\d+);', prose)
                self.assertIsNotNone(counts)
                self.assertEqual(tuple(map(int, counts.groups())),
                                 (int(scenarios['reference']['above_unity']),
                                  int(scenarios['seed_1e3']['above_unity'])))
                delayed = re.search(r'raises the primary count to (\d+)\.', prose)
                self.assertIsNotNone(delayed)
                self.assertEqual(int(delayed.group(1)), int(scenarios['seed_z20']['above_unity']))
            for name in archive.namelist():
                if name.startswith('figures/') and name.endswith('.pdf'):
                    folder = 'results/v4' if Path(name).stem.startswith('v4_') else 'results/for_manuscript'
                    self.assertEqual(archive.read(name), (ROOT/folder/name).read_bytes(), name)

    def test_changed_pdf_and_private_zip_entry_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paper = self.copy_release(root)
            pdf = paper / PDF_NAME
            pdf.write_bytes(pdf.read_bytes() + b'\nchanged\n')
            with self.assertRaisesRegex(ValueError, 'PDF hash'):
                verify_public(root)
            shutil.copy2(ROOT / 'paper' / PDF_NAME, pdf)
            with ZipFile(paper / ZIP_NAME, 'a') as archive:
                archive.writestr('apss/cover_letter.txt', 'private correspondence')
            with self.assertRaisesRegex(ValueError, 'membership'):
                verify_public(root)

    def test_packaging_is_deterministic_and_requires_all_dependencies(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            paper = self.copy_release(root)
            with ZipFile(paper / ZIP_NAME) as archive:
                archive.extractall(paper)
            package(root)
            original = (paper / ZIP_NAME).read_bytes()
            # File timestamps must not affect the public ZIP.
            (paper / 'main.tex').touch()
            package(root)
            self.assertEqual(original, (paper / ZIP_NAME).read_bytes())
            next((paper / 'figures').glob('*.pdf')).unlink()
            with self.assertRaises(FileNotFoundError):
                package(root)

    def test_public_allowlist_keeps_local_sources_and_editorial_materials_ignored(self):
        ignored = ('main.tex', 'README.md', 'apss/cover_letter.txt',
                   'apss/main.log', 'apss/main.aux', 'apss/main.out', 'apss/main.xdv',
                   'apss/README.md', 'apss/REPRODUCIBILITY.md',
                   'apss/build_package.py', 'apss/verify_package.py',
                   'apss/reproducibility_manifest.json', 'apss/figures/landscape.pdf',
                   'apss/tables/source_rows.tex', 'apss/apss_source.zip',
                   'apss/apss_supplementary.zip',
                   'previews/main.pdf', 'figures/landscape.pdf', 'AGENTS.md')
        public = (PDF_NAME, ZIP_NAME, 'apss/main.tex', 'apss/main.pdf')
        # Notebook regeneration uses git archives with no .git directory.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            shutil.copy2(ROOT / '.gitignore', root / '.gitignore')
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            for name in ignored + public:
                result = subprocess.run(['git', 'check-ignore', '--no-index', '-q',
                                         f'paper/{name}'], cwd=root)
                self.assertEqual(result.returncode, 0 if name in ignored else 1, name)


if __name__ == '__main__':
    unittest.main()
