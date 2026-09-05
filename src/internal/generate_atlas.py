"""Canonical entry point for the shared v1/v2/v3 all-object atlas renderer."""

from __future__ import annotations

import argparse

import pandas as pd

from src.internal import atlas
from src.internal.fedd_mass_maps import configure_style
from src.internal.seedredshift_mass_maps import materialize as materialize_seedredshift_mass


def configure(version: str) -> None:
    atlas.VERSION = version
    atlas.CATALOGUE = atlas.ROOT / "data/processed" / version / f"{version}_accreting_objects.csv"
    atlas.TABLES = atlas.ROOT / "results" / version / "tables"
    atlas.FIGURES = atlas.ROOT / "results" / version / "figures"
    atlas.PARAMETER_MAPS = atlas.ROOT / "results" / version / "parameter_maps"
    atlas.UNCERTAINTY = atlas.TABLES / f"{version}_object_uncertainty_ranking.csv"
    atlas.FIGURE_PATHS = {
        "growth_tracks": atlas.FIGURES / f"{version}_all_object_growth_tracks.png",
        "compatibility_summary": atlas.FIGURES / f"{version}_compatibility_summary.png",
        "uncertainty_summary": atlas.FIGURES / f"{version}_monte_carlo_summary.png",
        "fedd_mass_gallery": atlas.FIGURES / f"{version}_all_object_fedd_mass_map_gallery.png",
        "compatibility": atlas.FIGURES / f"{version}_all_object_compatibility_atlas.png",
        "uncertainty": atlas.FIGURES / f"{version}_all_object_monte_carlo_uncertainty.png",
    }
    if version == "v3":
        atlas.FIGURE_PATHS["full_assumption_growth_tracks"] = (
            atlas.FIGURES / "v3_all_object_growth_tracks_full_assumptions.png"
        )
        atlas.FIGURE_PATHS["full_assumption_growth_tracks_zseed3400"] = (
            atlas.FIGURES / "v3_all_object_growth_tracks_full_assumptions_zseed3400.png"
        )
    atlas.TABLE_PATHS = {
        "coverage": atlas.TABLES / f"{version}_all_object_visual_coverage.csv",
        "compatibility": atlas.TABLES / f"{version}_all_object_compatibility.csv",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", choices=["v1", "v2", "v3"])
    parser.add_argument("--rebuild-panels", action="store_true")
    args = parser.parse_args()
    configure(args.version)
    # Cached and rebuilt panel runs must establish the same matplotlib state.
    configure_style()
    objects, uncertainty = atlas.load_inputs()
    coverage = pd.concat([
        atlas.materialize_fedd_mass_maps(objects, rebuild=args.rebuild_panels),
        materialize_seedredshift_mass(args.version, objects, rebuild=args.rebuild_panels),
    ], ignore_index=True)
    compatibility = atlas.build_object_compatibility(objects)
    atlas.TABLE_PATHS["coverage"].parent.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(atlas.TABLE_PATHS["coverage"], index=False)
    compatibility.to_csv(atlas.TABLE_PATHS["compatibility"], index=False)
    atlas.plot_all_object_growth_tracks(objects, atlas.FIGURE_PATHS["growth_tracks"])
    if args.version == "v3":
        atlas.plot_full_assumption_growth_tracks(
            objects, atlas.FIGURE_PATHS["full_assumption_growth_tracks"],
        )
        atlas.plot_full_assumption_growth_tracks(
            objects, atlas.FIGURE_PATHS["full_assumption_growth_tracks_zseed3400"],
            z_seed=3400.0,
        )
    atlas.compile_fedd_mass_gallery(objects, atlas.FIGURE_PATHS["fedd_mass_gallery"])
    atlas.plot_compatibility_summary(objects, compatibility, atlas.FIGURE_PATHS["compatibility_summary"])
    atlas.plot_compatibility_atlas(objects, compatibility, atlas.FIGURE_PATHS["compatibility"])
    atlas.plot_uncertainty_summary(objects, uncertainty, atlas.FIGURE_PATHS["uncertainty_summary"])
    atlas.plot_all_object_uncertainty(objects, uncertainty, atlas.FIGURE_PATHS["uncertainty"])
    print(f"Generated {args.version}: {len(objects)} objects, {len(uncertainty)} numerical")


if __name__ == "__main__":
    main()
