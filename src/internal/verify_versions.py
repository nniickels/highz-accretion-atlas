"""Verify the dataset contracts and independently rebuilt results."""

from __future__ import annotations

from pathlib import Path
import pandas as pd
from PIL import Image

from src.datasets import DATASET_SPECS
from src.internal.dataset_manifests import verify_manifest
from src.internal.build_results_inventory import collect_inventory
from src.internal import atlas
from src.internal.shared_results import fedd_map_paths, sensitivity_figure_path
from src.internal.atlas import (
    MERGER_CASES,
    SEED_MODELS,
    SPIN_CASES,
)
from src.internal.process_catalogues import build_versions, output_paths
from src.internal.reproduction import assert_csv_reproduction
from src.science import DEFAULT_N_SAMPLES, DEFAULT_RANDOM_SEED, build_outputs

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FIGURES = (
    "catalogue_growth_landscape", "class_aware_growth_pressure",
    "uncertainty_robustness", "all_object_growth_tracks",
    "compatibility_summary", "monte_carlo_summary",
)


def verify_version(version: str) -> None:
    spec = DATASET_SPECS[version]
    data = ROOT / "data/processed" / version
    results = ROOT / "results" / version
    measurements = pd.read_csv(data / f"{version}_accreting_measurements.csv", low_memory=False)
    objects = pd.read_csv(data / f"{version}_accreting_objects.csv", low_memory=False)
    hosts = pd.read_csv(data / f"{version}_host_systems.csv")
    observed = (len(measurements), len(objects), len(hosts))
    expected = (spec.expected_measurements, spec.expected_objects, spec.expected_hosts)
    if observed != expected:
        raise AssertionError(f"{version} catalogue counts: {observed} != {expected}")
    if not objects["physical_object_id"].is_unique:
        raise AssertionError(f"{version} object IDs are not unique")
    if not measurements["catalogue_release"].eq(spec.catalogue_release).all():
        raise AssertionError(f"{version} catalogue metadata mismatch")

    eligible = int(objects["growth_ranking_eligible_flag"].astype(bool).sum())
    expected_eligible = {"v1": 23, "v2": 215, "v3": 241}[version]
    if eligible != expected_eligible:
        raise AssertionError(f"{version} growth eligibility changed")
    uncertainty = pd.read_csv(results / "tables" / f"{version}_object_uncertainty_ranking.csv")
    if len(uncertainty) != eligible or not uncertainty["n_samples"].eq(10_000).all():
        raise AssertionError(f"{version} Monte Carlo coverage/sample count mismatch")
    duty = pd.read_csv(results / "tables" / f"{version}_object_accretion_history.csv")
    if len(duty) != 3 * eligible or not duty["n_samples"].eq(10_000).all():
        raise AssertionError(f"{version} duty-cycle coverage mismatch")
    evaluation = pd.read_csv(results / "tables" / f"{version}_object_point_ranking.csv")
    required_fedd = pd.read_csv(results / "tables" / f"{version}_required_fedd_by_seed_mass.csv")
    required_mseed = pd.read_csv(results / "tables" / f"{version}_required_mseed_by_growth_assumption.csv")
    if (len(evaluation), len(required_fedd), len(required_mseed)) != (
        eligible, 3 * eligible, 2 * eligible,
    ):
        raise AssertionError(f"{version} baseline evaluation coverage mismatch")
    coverage = pd.read_csv(results / "tables" / f"{version}_all_object_visual_coverage.csv")
    if (
        len(coverage) != 2 * len(objects)
        or coverage["physical_object_id"].nunique() != len(objects)
        or set(coverage["product_kind"]) != {"fedd_mass_map", "seedredshift_mass_map"}
    ):
        raise AssertionError(f"{version} per-object visual coverage mismatch")
    if coverage["path"].str.contains("/gallery/|/per_object/|/growth_tracks/", regex=True).any():
        raise AssertionError(f"{version} parameter maps contain an obsolete path")
    numerical = coverage.loc[coverage.growth_ranking_eligible_flag]
    unavailable = coverage.loc[~coverage.growth_ranking_eligible_flag]
    if not unavailable.path.isna().all() or not unavailable.product_status.eq('no_numerical_mass').all():
        raise AssertionError(f'{version} missing-mass records must not export placeholder images')
    expected_fedd = {key: path.relative_to(ROOT).as_posix()
                     for key, path in fedd_map_paths(ROOT, version, objects).items()}
    fedd = numerical.loc[numerical.product_kind.eq('fedd_mass_map')]
    if fedd.set_index('physical_object_id').path.to_dict() != expected_fedd:
        raise AssertionError(f'{version} shared-map paths do not match their rendering inputs')
    seed_maps = numerical.loc[numerical.product_kind.eq('seedredshift_mass_map')]
    if not seed_maps.path.str.startswith(f'results/{version}/parameter_maps/seedredshift_mass_maps/').all():
        raise AssertionError(f'{version} seed-redshift maps must retain their edition labels')
    parameter_map_dirs = {
        path.name for path in (results / "parameter_maps").iterdir() if path.is_dir()
    }
    if parameter_map_dirs != {"fedd_mass_maps", "seedredshift_mass_maps"}:
        raise AssertionError(
            f"{version} parameter-map folders are not canonical: {sorted(parameter_map_dirs)}"
        )
    if any(not (ROOT / path).is_file() for path in numerical["path"]):
        raise AssertionError(f"{version} has missing per-object panels")
    compatibility = pd.read_csv(results / "tables" / f"{version}_all_object_compatibility.csv")
    expected_rows = len(objects) * len(SEED_MODELS) * len(SPIN_CASES) * len(MERGER_CASES) * 3
    if len(compatibility) != expected_rows:
        raise AssertionError(f"{version} compatibility coverage mismatch")
    followup = pd.read_csv(results / "tables" / f"{version}_followup_priority.csv")
    if len(followup) != len(objects) or followup["physical_object_id"].nunique() != len(objects):
        raise AssertionError(f"{version} follow-up matrix coverage mismatch")
    unresolved = followup.scientific_identity_status.eq("unresolved")
    if (not followup.loc[unresolved, 'followup_priority_category'].eq('identity_review_required').all()
            or followup.loc[unresolved, ['followup_value_score_0_100',
                                       'rank_followup_global_navigation',
                                       'rank_followup_within_object_class']].notna().any().any()):
        raise AssertionError(f"{version} unresolved identities must await review, without numerical follow-up ranks")
    ranked = followup[followup["growth_ranking_eligible_flag"].astype(bool) & ~unresolved]
    if sorted(ranked["rank_followup_global_navigation"].astype(int)) != list(range(1, len(ranked) + 1)):
        raise AssertionError(f"{version} follow-up navigation ranks are not contiguous")
    caveats = pd.read_csv(results / "tables" / f"{version}_source_caveat_summary.csv")
    if set(caveats["source_key"]) != set(measurements["source_key"]):
        raise AssertionError(f"{version} source-caveat coverage mismatch")
    selection = pd.read_csv(
        results / "tables" / f"{version}_selection_completeness_summary.csv"
    )
    if set(selection["source_key"]) != set(measurements["source_key"]):
        raise AssertionError(f"{version} selection/completeness coverage mismatch")
    if selection["pooled_demographic_inference_allowed"].astype(bool).any():
        raise AssertionError(f"{version} unexpectedly enables pooled demographic inference")
    if selection["catalogue_inverse_probability_weight"].notna().any():
        raise AssertionError(f"{version} unexpectedly assigns inverse-probability weights")
    figure_paths = [results / 'figures' / f'{version}_{stem}.png' for stem in REQUIRED_FIGURES]
    figure_paths.append(sensitivity_figure_path(ROOT, version))
    for path in figure_paths:
        with Image.open(path) as image:
            if image.format != "PNG" or image.width < 3000 or image.height < 1800:
                raise AssertionError(f"{version} figure is not paper resolution: {path}")
    if version == "v3":
        from src.internal.catalogue_products import load_config
        config = load_config()
        summary = pd.read_csv(results / "tables/v3_object_results.csv")
        if (len(summary) != len(objects) or not summary.physical_object_id.is_unique
                or set(summary.physical_object_id) != set(objects.physical_object_id)):
            raise AssertionError("v3 compact results must cover all objects exactly once")
        comparison = pd.read_csv(results / "tables/v3_growth_assumption_comparison.csv")
        minimum = pd.read_csv(results / "tables/v3_minimum_seed_mass.csv")
        settings = config["minimum_seed"]
        minimum_cases = 1
        for key in ("onset_redshifts", "epsilon_values", "average_fedd_caps", "mass_offsets_dex"):
            minimum_cases *= len(settings[key])
        if (len(comparison) != eligible * len(config["comparison_scenarios"])
                or len(minimum) != eligible * minimum_cases):
            raise AssertionError("v3 assumption/minimum-seed coverage differs from configuration")
        availability = pd.read_csv(results / "tables/v3_field_availability.csv")
        if set(availability.entity_level) != {"object", "measurement"}:
            raise AssertionError("v3 field availability must cover both catalogue views")


def verify_nested_membership() -> None:
    views = {
        version: pd.read_csv(
            ROOT / "data/processed" / version / f"{version}_accreting_measurements.csv",
            low_memory=False,
        ) for version in DATASET_SPECS
    }
    ids = {version: set(frame["measurement_id"]) for version, frame in views.items()}
    if not ids["v1"] < ids["v2"] < ids["v3"]:
        raise AssertionError("dataset versions must be strict nested expansions")
    if set(views["v1"]["source_key"]) != DATASET_SPECS["v1"].source_keys:
        raise AssertionError("v1 source membership changed")
    if set(views["v2"]["source_key"]) != DATASET_SPECS["v2"].source_keys:
        raise AssertionError("v2 source membership changed")


def verify_reproduction() -> None:
    """Rebuild every canonical CSV in memory and compare it with the repository."""
    versions = build_versions()
    for version, catalogue_outputs in versions.items():
        for name, frame in catalogue_outputs.items():
            assert_csv_reproduction(output_paths(version)[name], frame)

        measurements = catalogue_outputs["measurements"]
        objects = catalogue_outputs["objects"]
        science_outputs = build_outputs(
            version,
            measurements,
            objects,
            n_samples=DEFAULT_N_SAMPLES,
            random_seed=DEFAULT_RANDOM_SEED,
        )
        if version == "v3":
            from src.internal.assess_baccus_revision import build_revision_outputs
            science_outputs.update(build_revision_outputs(objects))
            from src.internal.admission_sensitivity import build_source_model_sensitivity
            science_outputs["admission_source_model_sensitivity"] = build_source_model_sensitivity()
        table_dir = ROOT / "results" / version / "tables"
        previous_version = atlas.VERSION
        try:
            atlas.VERSION = version
            assert_csv_reproduction(
                table_dir / f"{version}_all_object_compatibility.csv",
                atlas.build_object_compatibility(objects),
            )
        finally:
            atlas.VERSION = previous_version
        for name, frame in science_outputs.items():
            assert_csv_reproduction(table_dir / f"{version}_{name}.csv", frame)


def verify_results_inventory() -> None:
    stored = pd.read_csv(ROOT / "results/results_inventory.csv")
    current = collect_inventory()
    pd.testing.assert_frame_equal(stored, current, check_dtype=False)


def main() -> None:
    for version in DATASET_SPECS:
        verify_version(version)
        verify_manifest(version)
        print(f"Verified {version}")
    verify_nested_membership()
    verify_reproduction()
    verify_results_inventory()
    print("Verified manifests, result inventory, exact CSV reproduction, shared analysis contract, and strict v1 < v2 < v3 dataset growth")


if __name__ == "__main__":
    main()
