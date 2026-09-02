"""Canonical entry point for the shared v1/v2/v3 all-object atlas renderer."""

from __future__ import annotations

import argparse

import pandas as pd

from src.internal import atlas
from src.internal.seed_redshift_gallery import materialize as materialize_seed_redshift


def configure(version: str) -> None:
    atlas.VERSION = version
    atlas.CATALOGUE = atlas.ROOT / "data/processed" / version / f"{version}_accreting_objects.csv"
    atlas.TABLES = atlas.ROOT / "results" / version / "tables"
    atlas.FIGURES = atlas.ROOT / "results" / version / "figures"
    atlas.GALLERY = atlas.ROOT / "results" / version / "gallery"
    atlas.PER_OBJECT = atlas.GALLERY / "per_object"
    atlas.UNCERTAINTY = atlas.TABLES / f"{version}_object_uncertainty_ranking.csv"
    atlas.FIGURE_PATHS = {
        "growth_tracks": atlas.FIGURES / f"{version}_all_object_growth_tracks.png",
        "compatibility_summary": atlas.FIGURES / f"{version}_compatibility_summary.png",
        "uncertainty_summary": atlas.FIGURES / f"{version}_monte_carlo_summary.png",
        "parameter_gallery": atlas.FIGURES / f"{version}_all_object_parameter_map_gallery.png",
        "compatibility": atlas.FIGURES / f"{version}_all_object_compatibility_atlas.png",
        "uncertainty": atlas.FIGURES / f"{version}_all_object_monte_carlo_uncertainty.png",
    }
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
    objects, uncertainty = atlas.load_inputs()
    coverage = pd.concat([
        atlas.materialize_per_object_panels(objects, rebuild=args.rebuild_panels),
        materialize_seed_redshift(args.version, objects, rebuild=args.rebuild_panels),
    ], ignore_index=True)
    compatibility = atlas.build_object_compatibility(objects)
    atlas.TABLE_PATHS["coverage"].parent.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(atlas.TABLE_PATHS["coverage"], index=False)
    compatibility.to_csv(atlas.TABLE_PATHS["compatibility"], index=False)
    atlas.plot_all_object_growth_tracks(objects, atlas.FIGURE_PATHS["growth_tracks"])
    atlas.compile_parameter_gallery(objects, atlas.FIGURE_PATHS["parameter_gallery"])
    atlas.plot_compatibility_summary(objects, compatibility, atlas.FIGURE_PATHS["compatibility_summary"])
    atlas.plot_compatibility_atlas(objects, compatibility, atlas.FIGURE_PATHS["compatibility"])
    atlas.plot_uncertainty_summary(objects, uncertainty, atlas.FIGURE_PATHS["uncertainty_summary"])
    atlas.plot_all_object_uncertainty(objects, uncertainty, atlas.FIGURE_PATHS["uncertainty"])
    print(f"Generated {args.version}: {len(objects)} objects, {len(uncertainty)} numerical")


if __name__ == "__main__":
    main()
