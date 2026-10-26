"""Verify the public manuscript snapshot without private sources or a TeX install."""
from pathlib import Path
from io import BytesIO
import csv
import re
import shutil
import subprocess
import tempfile
import unittest
from zipfile import ZipFile

from pypdf import PdfReader, PdfWriter
from src.internal.pdf_reproduction import compare_pdf

from src.internal.package_overleaf import ROOT, PDF_NAME, ZIP_NAME, verify_public, package


def verify_packaged_figures(archive, root):
    for name in archive.namelist():
        if name.startswith('figures/') and name.endswith('.pdf'):
            folder = 'results/v4' if Path(name).stem.startswith('v4_') else 'results/for_manuscript'
            # Regeneration may change compression across platforms. Keep exact
            # decoded content/resource checks, as in the notebook verifier.
            compare_pdf(BytesIO(archive.read(name)), root/folder/name)


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
            # Canonical results retain PNGs only. Rebuild the PDF dependencies
            # temporarily to keep independently checking the packaged sources.
            from src.internal.publication_figures import render_figures
            from src.internal.plot_early_start import render as render_early_start
            from src.internal.plot_seed_timing_comparison import render as render_seed_timing
            from src.internal.pbh_growth_v4 import build_tables, make_figures
            with tempfile.TemporaryDirectory() as directory:
                generated = Path(directory)
                figures = generated/'results/for_manuscript/figures'
                render_figures(ROOT, figures, formats=('pdf',))
                render_early_start(figures, formats=('pdf',))
                render_seed_timing(figures, formats=('pdf',))
                make_figures(build_tables(), generated/'results/v4/figures', formats=('pdf',))
                verify_packaged_figures(archive, generated)

    def test_general_draft_matches_onset_seed_masses_and_compatibility(self):
        with (ROOT/'results/v4/tables/v4_minimum_seed_mass.csv').open() as stream:
            seeds = [round(10 ** float(row['log10_minimum_seed_central']))
                     for row in csv.DictReader(stream)
                     if float(row['mass_offset_dex']) == 0
                     and float(row['epsilon']) == .1
                     and float(row['fedd_cap']) == 1
                     and float(row['z_accretion']) == 3400]
        self.assertEqual(len(seeds), 4)
        with (ROOT/'results/for_manuscript/tables/publication_object_selection.csv').open() as stream:
            selection = list(csv.DictReader(stream))
        with (ROOT/'results/v3/tables/v3_all_object_compatibility.csv').open() as stream:
            compatibility = [row for row in csv.DictReader(stream)
                             if row['seed_model'] == 'heavy_seeds'
                             and row['spin_case'] == 'spin_plus1_eps0p423'
                             and float(row['f_edd_avg']) == 1]
        percentages = []
        for flag in ('publication_primary_flag', 'publication_exploratory_flag'):
            ids = {row['physical_object_id'] for row in selection if row[flag] == 'True'}
            for merger in ('no_merger_boost', 'merger_boost_x2'):
                rows = [row for row in compatibility
                        if row['physical_object_id'] in ids and row['merger_case'] == merger]
                self.assertEqual(len(rows), len(ids))
                percentages.append(round(100 * sum(row['compatible'] == 'True' for row in rows)
                                         / len(rows)))
        with ZipFile(ROOT/'paper'/ZIP_NAME) as archive:
            texts = [archive.read('main.tex').decode()]
        for text in texts:
            prose = ' '.join(text.split())
            masses = re.search(
                r'equality-onset minimum seeds are approximately (\d+), (\d+), (\d+), '
                r'and \$(\d+)\\,M_\\odot\$', prose)
            self.assertIsNotNone(masses)
            self.assertEqual(list(map(int, masses.groups())), seeds)
            fractions = re.search(
                r'raises compatibility from (\d+) to (\d+) per cent in the primary sample '
                r'and from (\d+) to (\d+) per cent in the expanded sample', prose)
            self.assertIsNotNone(fractions)
            self.assertEqual(list(map(int, fractions.groups())), percentages)

    def test_packaged_figures_allow_recompression_but_reject_changed_geometry(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root/'results/for_manuscript/figures/compatibility.pdf'
            path.parent.mkdir(parents=True)
            with ZipFile(ROOT/'paper'/ZIP_NAME) as archive:
                original = archive.read('figures/compatibility.pdf')
                # Keep the other packaged figures unchanged to test the complete gate.
                for name in archive.namelist():
                    if name.startswith('figures/') and name.endswith('.pdf'):
                        base = 'results/v4' if Path(name).stem.startswith('v4_') else 'results/for_manuscript'
                        target = root/base/name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(archive.read(name))
                writer = PdfWriter(clone_from=PdfReader(BytesIO(original)))
                for page in writer.pages:
                    page.compress_content_streams(level=0)
                writer.write(path)
                self.assertNotEqual(original, path.read_bytes())
                verify_packaged_figures(archive, root)
                writer.pages[0].mediabox.upper_right = (100, 100)
                writer.write(path)
                with self.assertRaisesRegex(AssertionError, 'PDF'):
                    verify_packaged_figures(archive, root)

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
