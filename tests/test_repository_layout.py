"""Repository-boundary checks for the public notebook migration."""

from __future__ import annotations

import json
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
    def test_results_figures_have_only_png_exports(self) -> None:
        self.assertEqual(list((ROOT / 'results').rglob('*.pdf')), [])

    def test_selected_samples_are_v3_outputs(self) -> None:
        from src.internal.dataset_manifests import canonical_artifacts
        from src.internal.verify_regenerated_artifacts import artifact_paths
        from src.internal.build_results_inventory import collect_inventory

        folder = ROOT / 'results/v3/selected_samples'
        outputs = {p for part in ('tables', 'figures')
                   for p in (folder / part).iterdir() if p.suffix in {'.csv', '.png'}}
        self.assertEqual(len(outputs), 19)
        self.assertFalse((ROOT / 'results/for_manuscript').exists())
        self.assertTrue(outputs <= set(canonical_artifacts('v3')))
        generated = artifact_paths(ROOT)
        self.assertTrue({p.relative_to(ROOT).as_posix() for p in outputs} <= generated)
        self.assertNotIn('results/v3/selected_samples/README.md', generated)
        self.assertNotIn(folder / 'README.md', canonical_artifacts('v3'))
        inventory = collect_inventory()
        selected = inventory[inventory.path.str.startswith('results/v3/selected_samples/')]
        self.assertEqual(len(selected), len(outputs))
        self.assertEqual(set(selected.release), {'v3'})
        self.assertEqual(set(selected.path_policy), {'selected_sample_product'})

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

    def test_complete_axis_named_parameter_maps(self) -> None:
        expected = {"v1": (23, 23), "v2": (192, 215), "v3": (26, 241)}
        for version, (fedd_count, seed_count) in expected.items():
            parameter_maps = ROOT / "results" / version / "parameter_maps"
            self.assertEqual(
                {path.name for path in parameter_maps.iterdir() if path.is_dir()},
                {"fedd_mass_maps", "seedredshift_mass_maps"},
                version,
            )
            self.assertEqual(len(list((parameter_maps / "fedd_mass_maps").glob("*.png"))), fedd_count, version)
            self.assertEqual(len(list((parameter_maps / "seedredshift_mass_maps").glob("*.png"))), seed_count, version)

    def test_parameter_maps_are_flat_and_have_no_individual_growth_tracks(self) -> None:
        for version in ("v1", "v2", "v3"):
            parameter_maps = ROOT / "results" / version / "parameter_maps"
            self.assertFalse((parameter_maps / "per_object").exists(), version)
            self.assertEqual(list(parameter_maps.rglob("growth_tracks")), [], version)
            self.assertEqual(list(parameter_maps.rglob("*_growth_track_*.png")), [], version)
            self.assertFalse((ROOT / "results" / version / "gallery").exists(), version)

    def test_followup_and_source_caveat_products(self) -> None:
        expected_objects = {"v1": 23, "v2": 215, "v3": 343}
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
