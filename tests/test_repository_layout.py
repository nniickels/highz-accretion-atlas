"""Repository-boundary checks for the public notebook migration."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SRC = ROOT / "src"
WORKFLOW_NOTEBOOKS = [
    "00_process_catalogues.ipynb",
    "01_generate_science.ipynb",
    "02_generate_figures.ipynb",
    "03_generate_atlas.ipynb",
    "04_verify.ipynb",
]


class RepositoryLayoutTests(unittest.TestCase):
    def test_scripts_contains_no_python_modules(self) -> None:
        self.assertEqual(list(SCRIPTS.rglob("*.py")), [])

    def test_numbered_workflow_is_complete(self) -> None:
        present = sorted(path.name for path in SCRIPTS.glob("0[0-4]_*.ipynb"))
        self.assertEqual(present, WORKFLOW_NOTEBOOKS)

    def test_workflow_notebooks_are_clean_and_compilable(self) -> None:
        for name in WORKFLOW_NOTEBOOKS:
            path = SCRIPTS / name
            notebook = json.loads(path.read_text())
            self.assertEqual(notebook["nbformat"], 4, name)
            ids = [cell.get("id") for cell in notebook["cells"]]
            self.assertTrue(all(ids), name)
            self.assertEqual(len(ids), len(set(ids)), name)
            code = []
            for cell in notebook["cells"]:
                if cell["cell_type"] != "code":
                    continue
                self.assertIsNone(cell["execution_count"], name)
                self.assertEqual(cell["outputs"], [], name)
                code.append("".join(cell["source"]))
            compile("\n".join(code), str(path), "exec")

    def test_src_non_document_files_are_python(self) -> None:
        unexpected = [
            path.relative_to(ROOT).as_posix()
            for path in SRC.rglob("*")
            if path.is_file()
            and path.name != "README.md"
            and "__pycache__" not in path.parts
            and path.suffix != ".py"
        ]
        self.assertEqual(unexpected, [])

    def test_compiled_manuscript_is_present(self) -> None:
        manuscript = ROOT / "paper/highz_accretion_atlas_v3.pdf"
        self.assertTrue(manuscript.read_bytes().rstrip().endswith(b"%%EOF"))
        self.assertEqual(manuscript.read_bytes()[:5], b"%PDF-")

    def test_manuscript_links_repository_and_generated_tables(self) -> None:
        manuscript = (ROOT / "paper/highz_accretion_atlas_v3.tex").read_text()
        self.assertIn("https://github.com/nniickels/highz-accretion-atlas", manuscript)
        for fragment in re.findall(r"\\(?:tableinput|input)\{([^}]+)\}", manuscript):
            self.assertTrue((ROOT / 'paper' / fragment).is_file(), fragment)

    def test_manuscript_embeds_all_figures_without_live_plotting(self) -> None:
        manuscript = "\n".join((ROOT / "paper" / name).read_text() for name in
                               ("highz_accretion_atlas_v3.tex",))
        figures = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", manuscript)
        self.assertEqual(len(figures), 7)
        self.assertNotIn(r"\usepackage{pgfplots}", manuscript)
        self.assertNotIn(r"\begin{tikzpicture}", manuscript)
        for name in figures:
            self.assertEqual(Path(name).suffix, '.pdf')
            self.assertTrue((ROOT/'paper'/name).read_bytes().startswith(b'%PDF-'))

    def test_manuscript_citations_have_bibliography_entries(self) -> None:
        manuscript = (ROOT / "paper/highz_accretion_atlas_v3.tex").read_text()
        expected = {
            "baccus2026", "bogdan2024", "chavezortiz2026", "chisholm2024", "davis2026",
            "dayal2024", "shen2013", "goulding2023", "greene2024", "harikane2023",
            "fei2026", "hutchison2025", "juodzbalis2026", "killi2024", "kocevski2025",
            "larson2023", "leung2026", "lin2024", "lyu2024", "maiolino2024",
            "mascia2026", "matthee2024", "mazzolari2024", "naidu2026", "napolitano2025",
            "ren2025", "scholtz2025", "skyfire2026", "tang2025", "taylor2025",
            "treiber2025", "ubler2024", "zhang2026", "zou2026",
            "zhuang2025", "lin2025", "napolitano2024", "juodzbalis_direct2025", "bardeen1972", "poutanen2007",
        }
        all_cited = set()
        for name in ("highz_accretion_atlas_v3.tex",):
            manuscript = (ROOT / "paper" / name).read_text()
            # Check each document independently, including its generated tables.
            for fragment in re.findall(r"\\(?:tableinput|input)\{([^}]+)\}", manuscript):
                manuscript += (ROOT / 'paper' / fragment).read_text()
            cited = {
                key.strip()
                for group in re.findall(r"\\cite(?:p|t|author|yearpar|year)?\*?(?:\[[^\]]*\])*\{([^}]+)\}", manuscript)
                for key in group.split(",")
            }
            bibliography = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", manuscript))
            self.assertEqual(bibliography, cited, name)
            all_cited.update(cited)
        self.assertEqual(all_cited, expected)

    def test_complete_axis_named_parameter_maps(self) -> None:
        expected = {"v1": 23, "v2": 211, "v3": 338}
        for version, count in expected.items():
            parameter_maps = ROOT / "results" / version / "parameter_maps"
            self.assertEqual(
                {path.name for path in parameter_maps.iterdir() if path.is_dir()},
                {"fedd_mass_maps", "seedredshift_mass_maps"},
                version,
            )
            self.assertEqual(len(list((parameter_maps / "fedd_mass_maps").glob("*.png"))), count, version)
            self.assertEqual(len(list((parameter_maps / "seedredshift_mass_maps").glob("*.png"))), count, version)

    def test_parameter_maps_are_flat_and_have_no_individual_growth_tracks(self) -> None:
        for version in ("v1", "v2", "v3"):
            parameter_maps = ROOT / "results" / version / "parameter_maps"
            self.assertFalse((parameter_maps / "per_object").exists(), version)
            self.assertEqual(list(parameter_maps.rglob("growth_tracks")), [], version)
            self.assertEqual(list(parameter_maps.rglob("*_growth_track_*.png")), [], version)
            self.assertFalse((ROOT / "results" / version / "gallery").exists(), version)

    def test_followup_and_source_caveat_products(self) -> None:
        expected_objects = {"v1": 23, "v2": 211, "v3": 338}
        for version, count in expected_objects.items():
            tables = ROOT / "results" / version / "tables"
            followup = pd.read_csv(tables / f"{version}_followup_priority.csv")
            caveats = pd.read_csv(tables / f"{version}_source_caveat_summary.csv")
            self.assertEqual(len(followup), count, version)
            self.assertEqual(followup["physical_object_id"].nunique(), count, version)
            self.assertTrue(caveats["source_key"].is_unique, version)
            self.assertGreater(len(caveats), 0, version)
            selection = pd.read_csv(tables / f"{version}_selection_completeness_summary.csv")
            self.assertEqual(set(selection["source_key"]), set(caveats["source_key"]), version)
            self.assertFalse(selection["pooled_demographic_inference_allowed"].astype(bool).any())
            self.assertTrue(selection["catalogue_inverse_probability_weight"].isna().all())


if __name__ == "__main__":
    unittest.main()
