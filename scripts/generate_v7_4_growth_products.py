"""Generate complete v7.4 eligible-object growth visualizations and audits.

The numerical products are restricted to objects that already satisfy the
catalogue's explicit growth-ranking eligibility contract. Objects without a
usable canonical mass remain in a separate, human-readable exclusion table;
this generator never invents a mass or converts a limit/range into a point.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MPLCONFIGDIR = ROOT / ".codex_tmp" / "matplotlib"
MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from src.models import (
    SEED_MODELS,
    growth_parameter_grid,
    predicted_log_mbh,
    required_fedd_for_seed,
    required_seed_mass_for_growth,
    slim_disk_effective_efficiency,
    thin_disk_radiative_efficiency,
)


CATALOGUE = ROOT / "data/processed/v7_4/v7_4_accreting_objects.csv"
RELEASE_DIR = ROOT / "results/releases/v7_4"
TABLE_DIR = RELEASE_DIR / "tables"
FIGURE_DIR = RELEASE_DIR / "figures"
GALLERY_DIR = RELEASE_DIR / "galleries"
PER_OBJECT_DIR = GALLERY_DIR / "per_object"
COMPILED_DIR = GALLERY_DIR / "compiled_by_class"

COVERAGE_PATH = TABLE_DIR / "v7_4_growth_product_coverage.csv"
UNAVAILABLE_PATH = TABLE_DIR / "v7_4_growth_unavailable_objects.csv"
COMPATIBILITY_PATH = TABLE_DIR / "v7_4_class_compatibility_fractions.csv"
GALLERY_INVENTORY_PATH = GALLERY_DIR / "v7_4_growth_gallery_inventory.csv"
COMPATIBILITY_FIGURE_PATH = FIGURE_DIR / "v7_4_class_compatibility_fractions.png"

Z_SEED = 30.0
LOG_SEED_AXIS = np.linspace(0.0, 8.0, 100)
FEDD_AXIS = np.linspace(0.0, 3.0, 90)
SEED_REDSHIFT_LOG_SEED_AXIS = np.linspace(1.0, 6.2, 110)
SEED_REDSHIFT_STEPS = 105
COMPATIBILITY_FEDD = (0.1, 0.3, 0.5, 1.0, 2.0, 3.0)
SCIENCE_RELEASE = "v7.4-growth-visualization"

SPIN_CASES = (
    (-1.0, "spin_minus1_eps0p038", "a=-1"),
    (0.0, "spin_0_eps0p057", "a=0"),
    (1.0, "spin_plus1_eps0p423", "a=+1"),
)
MERGER_CASES = ((1.0, "no_merger_boost"), (2.0, "merger_boost_x2"))
COMPILED_CAPTIONS = {
    "parameter_map": (
        "Shared assumptions: white contour reproduces the canonical mass; "
        "photon-trapping efficiency is used above Eddington; z_seed=30."
    ),
    "seed_redshift_map": (
        "Shared assumptions: baseline epsilon=0.1, no merger boost, and "
        "Planck-style cosmology."
    ),
    "growth_track": (
        "Shared assumptions: z_seed=30, epsilon=0.1, and no merger boost."
    ),
}
COMPILED_CAPTION_CROP_PX = {
    "parameter_map": 55,
    "seed_redshift_map": 42,
    "growth_track": 42,
}


def boolish(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def safe_slug(value: object) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", str(value)).strip("-").lower() or "object"


def class_slug(value: object) -> str:
    return safe_slug(value).replace("-", "_")


def load_catalogue() -> pd.DataFrame:
    catalogue = pd.read_csv(CATALOGUE)
    required = {
        "physical_object_id", "object_id", "object_class", "source_key", "redshift",
        "log_mbh_msun_std", "growth_ranking_eligible_flag",
        "growth_ranking_eligibility_reason", "primary_growth_ranking_flag",
    }
    missing = required - set(catalogue)
    if missing:
        raise ValueError(f"v7.4 catalogue is missing columns: {sorted(missing)}")
    if not catalogue["physical_object_id"].is_unique:
        raise ValueError("v7.4 physical-object catalogue IDs must be unique")
    return catalogue.sort_values(["object_class", "redshift", "physical_object_id"]).reset_index(drop=True)


def eligible_objects(catalogue: pd.DataFrame) -> pd.DataFrame:
    eligible = catalogue[catalogue["growth_ranking_eligible_flag"].map(boolish)].copy()
    if eligible["log_mbh_msun_std"].isna().any():
        raise ValueError("Every growth-eligible object must have a canonical numeric mass")
    if len(eligible) != 196:
        raise ValueError(f"Expected 196 growth-eligible v7.4 objects, found {len(eligible)}")
    return eligible


def object_product_paths(obj: pd.Series) -> dict[str, Path]:
    group = class_slug(obj["object_class"])
    stem = safe_slug(obj["physical_object_id"])
    return {
        "parameter_map": PER_OBJECT_DIR / "parameter_maps" / group / f"v7_4_parameter_map_{stem}.png",
        "seed_redshift_map": PER_OBJECT_DIR / "seed_redshift_maps" / group / f"v7_4_seed_redshift_map_{stem}.png",
        "growth_track": PER_OBJECT_DIR / "growth_tracks" / group / f"v7_4_growth_track_{stem}.png",
    }


def build_coverage_table(catalogue: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, obj in catalogue.iterrows():
        eligible = boolish(obj["growth_ranking_eligible_flag"])
        paths = object_product_paths(obj) if eligible else {}
        rows.append({
            "science_release": SCIENCE_RELEASE,
            "input_catalogue_release": "v7.4-accreting-atlas-catalogue",
            "physical_object_id": obj["physical_object_id"],
            "object_id": obj["object_id"],
            "object_class": obj["object_class"],
            "source_key": obj["source_key"],
            "growth_ranking_eligible_flag": eligible,
            "primary_growth_ranking_flag": boolish(obj["primary_growth_ranking_flag"]),
            "growth_product_status": "complete" if eligible else "unavailable",
            "growth_product_status_reason": (
                "eligible_canonical_numeric_mbh" if eligible
                else obj["growth_ranking_eligibility_reason"]
            ),
            "parameter_map_path": paths.get("parameter_map", "").relative_to(ROOT).as_posix() if eligible else "",
            "seed_redshift_map_path": paths.get("seed_redshift_map", "").relative_to(ROOT).as_posix() if eligible else "",
            "growth_track_path": paths.get("growth_track", "").relative_to(ROOT).as_posix() if eligible else "",
            "compatibility_scope": (
                f"object_class={obj['object_class']}" if eligible else "not_calculated"
            ),
            "demographic_inference_allowed": False,
        })
    return pd.DataFrame(rows).sort_values(["object_class", "physical_object_id"]).reset_index(drop=True)


def build_unavailable_table(catalogue: pd.DataFrame) -> pd.DataFrame:
    excluded = catalogue[~catalogue["growth_ranking_eligible_flag"].map(boolish)].copy()
    fields = [
        "physical_object_id", "object_id", "object_class", "source_key", "redshift",
        "log_mbh_msun_std", "growth_ranking_eligibility_reason", "conditional_mass_flag",
        "conditional_mass_reason", "lensing_status", "lensing_mass_correction_status",
    ]
    result = excluded.reindex(columns=fields)
    result.insert(0, "input_catalogue_release", "v7.4-accreting-atlas-catalogue")
    result.insert(0, "science_release", SCIENCE_RELEASE)
    result["parameter_map_status"] = "unavailable_not_inferred"
    result["seed_redshift_map_status"] = "unavailable_not_inferred"
    result["growth_track_status"] = "unavailable_not_inferred"
    result["compatibility_status"] = "unavailable_not_inferred"
    result["retained_in_catalogue_flag"] = True
    result["review_requirement"] = np.where(
        result["growth_ranking_eligibility_reason"].eq("lensing_correction_not_applied"),
        "apply_source_supported_lensing_correction_before_growth_products",
        "obtain_source_supported_canonical_numeric_mbh_before_growth_products",
    )
    if len(result) != 22:
        raise ValueError(f"Expected 22 unavailable v7.4 objects, found {len(result)}")
    return result.sort_values(["object_class", "physical_object_id"]).reset_index(drop=True)


def build_class_compatibility(eligible: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for object_class, group in eligible.groupby("object_class", sort=True):
        masses = group["log_mbh_msun_std"].astype(float).to_numpy()
        redshifts = group["redshift"].astype(float).to_numpy()
        for spin, spin_name, _ in SPIN_CASES:
            thin_epsilon = float(thin_disk_radiative_efficiency(spin))
            for merger_boost, merger_name in MERGER_CASES:
                for fedd in COMPATIBILITY_FEDD:
                    epsilon_eff = float(slim_disk_effective_efficiency(spin, fedd))
                    required = required_seed_mass_for_growth(
                        masses, fedd, epsilon_eff, Z_SEED, redshifts,
                        merger_boost=merger_boost,
                    )
                    for seed_name, seed_model in SEED_MODELS.items():
                        compatible = (
                            (required >= seed_model.log_mseed_min)
                            & (required <= seed_model.log_mseed_max)
                        )
                        rows.append({
                            "science_release": SCIENCE_RELEASE,
                            "input_catalogue_release": "v7.4-accreting-atlas-catalogue",
                            "object_class": object_class,
                            "n_objects": len(group),
                            "z_seed": Z_SEED,
                            "spin": spin,
                            "spin_case": spin_name,
                            "thin_disk_epsilon": thin_epsilon,
                            "effective_epsilon": epsilon_eff,
                            "merger_boost": merger_boost,
                            "merger_case": merger_name,
                            "f_edd_avg": fedd,
                            "seed_model": seed_name,
                            "seed_log_mass_min": seed_model.log_mseed_min,
                            "seed_log_mass_max": seed_model.log_mseed_max,
                            "n_compatible": int(compatible.sum()),
                            "compatible_object_fraction": float(compatible.mean()),
                            "median_required_log_mseed": float(np.median(required)),
                            "min_required_log_mseed": float(np.min(required)),
                            "max_required_log_mseed": float(np.max(required)),
                            "comparison_scope": "within_object_class_descriptive_only",
                            "demographic_inference_allowed": False,
                        })
    result = pd.DataFrame(rows)
    expected = eligible["object_class"].nunique() * len(SPIN_CASES) * len(MERGER_CASES) * len(COMPATIBILITY_FEDD) * len(SEED_MODELS)
    if len(result) != expected:
        raise ValueError(f"Expected {expected} compatibility rows, found {len(result)}")
    return result.sort_values(
        ["object_class", "spin", "merger_boost", "f_edd_avg", "seed_model"],
    ).reset_index(drop=True)


def configure_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Serif", "font.size": 8.5,
        "axes.titlesize": 9.5, "axes.labelsize": 9,
        "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
        "legend.fontsize": 7.3, "axes.linewidth": 0.8,
        "savefig.facecolor": "white", "savefig.bbox": "tight",
    })


def _object_title(obj: pd.Series) -> str:
    return (
        f"{obj['object_id']} | z={float(obj['redshift']):.3f} | "
        f"log MBH={float(obj['log_mbh_msun_std']):.2f} | "
        f"{str(obj['object_class']).replace('_', ' ')}"
    )


def plot_parameter_sheet(obj: pd.Series, output: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(12.0, 7.8), sharex=True, sharey=True)
    observed = float(obj["log_mbh_msun_std"])
    last_mesh = None
    for ax, (spin, _, spin_label), (boost, boost_name) in zip(
        axes.flat,
        [spin_case for spin_case in SPIN_CASES for _ in MERGER_CASES],
        list(MERGER_CASES) * len(SPIN_CASES),
        strict=True,
    ):
        epsilon = slim_disk_effective_efficiency(spin, FEDD_AXIS)[:, None]
        grid = growth_parameter_grid(
            LOG_SEED_AXIS, FEDD_AXIS, epsilon, Z_SEED, float(obj["redshift"]),
            merger_boost=boost,
        )
        predicted = grid["predicted_log_mbh"]
        last_mesh = ax.pcolormesh(
            grid["log_mseed_grid"], grid["f_edd_grid"], predicted,
            shading="auto", cmap="viridis", vmin=5.0, vmax=10.5, rasterized=True,
        )
        if float(np.nanmin(predicted)) <= observed <= float(np.nanmax(predicted)):
            ax.contour(
                grid["log_mseed_grid"], grid["f_edd_grid"], predicted,
                levels=[observed], colors="white", linewidths=1.6,
            )
        ax.axhline(1.0, color="white", lw=0.8, alpha=0.9)
        for x in (2.0, 4.0, 6.0):
            ax.axvline(x, color="white", lw=0.6, ls=":", alpha=0.75)
        boost_label = "B=1" if boost_name == "no_merger_boost" else "B=2"
        ax.set_title(f"{spin_label}, thin epsilon={float(thin_disk_radiative_efficiency(spin)):.3f}, {boost_label}")
        ax.set_xlim(0, 8)
        ax.set_ylim(0, 3)
    for ax in axes[-1, :]:
        ax.set_xlabel("log10 seed mass [Msun]")
    for ax in axes[:, 0]:
        ax.set_ylabel("average f_Edd")
    fig.suptitle(_object_title(obj), y=0.985, fontsize=11)
    assert last_mesh is not None
    cbar = fig.colorbar(last_mesh, ax=axes.ravel().tolist(), pad=0.012, fraction=0.025)
    cbar.set_label("predicted log10 MBH [Msun]")
    fig.text(
        0.5, 0.012,
        "White contour reproduces the canonical mass; photon-trapping efficiency is used above Eddington. z_seed=30.",
        ha="center", fontsize=7.5,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)


def _seed_redshift_axis(redshift: float) -> np.ndarray:
    lower = min(Z_SEED - 0.1, redshift + 0.1)
    if lower >= Z_SEED:
        raise ValueError(f"redshift {redshift} has no valid seed-redshift range")
    return np.linspace(lower, Z_SEED, SEED_REDSHIFT_STEPS)


def plot_seed_redshift_map(obj: pd.Series, output: Path) -> None:
    z_axis = _seed_redshift_axis(float(obj["redshift"]))
    x_grid, y_grid = np.meshgrid(SEED_REDSHIFT_LOG_SEED_AXIS, z_axis, indexing="xy")
    fedd = required_fedd_for_seed(
        x_grid, float(obj["log_mbh_msun_std"]), 0.1, y_grid,
        float(obj["redshift"]), merger_boost=1.0,
    )
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    mesh = ax.pcolormesh(
        x_grid, y_grid, np.clip(fedd, 0, 3), shading="auto",
        cmap="magma_r", vmin=0, vmax=3, rasterized=True,
    )
    visible = [level for level in (0.3, 1.0, 2.0) if np.nanmin(fedd) <= level <= np.nanmax(fedd)]
    if visible:
        contour = ax.contour(x_grid, y_grid, fedd, levels=visible, colors="white", linewidths=1.1)
        ax.clabel(contour, fmt="%g", fontsize=7)
    for x in (2.0, 4.0, 6.0):
        ax.axvline(x, color="white", lw=0.7, ls=":", alpha=0.8)
    ax.set_title(_object_title(obj))
    ax.set_xlabel("log10 seed mass [Msun]")
    ax.set_ylabel("seed redshift")
    cbar = fig.colorbar(mesh, ax=ax, pad=0.02)
    cbar.set_label("required average f_Edd (clipped at 3)")
    fig.text(0.5, 0.012, "Baseline epsilon=0.1 and no merger boost; Planck-style cosmology.", ha="center", fontsize=7.5)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_growth_track(obj: pd.Series, output: Path) -> None:
    redshift = np.linspace(4.0, 12.0, 260)
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    colors = {2.0: "#1f77b4", 4.0: "#2ca02c", 6.0: "#d62728"}
    for log_seed in (2.0, 4.0, 6.0):
        for fedd, linestyle in ((0.3, "--"), (1.0, "-")):
            mass = predicted_log_mbh(log_seed, fedd, 0.1, Z_SEED, redshift)
            ax.plot(
                redshift, mass, color=colors[log_seed], ls=linestyle, lw=1.35,
                label=f"seed 1e{int(log_seed)}, f_Edd={fedd:g}",
            )
    err_minus = pd.to_numeric(pd.Series([obj.get("log_mbh_err_minus_std")]), errors="coerce").iloc[0]
    err_plus = pd.to_numeric(pd.Series([obj.get("log_mbh_err_plus_std")]), errors="coerce").iloc[0]
    yerr = None if pd.isna(err_minus) or pd.isna(err_plus) else [[float(err_minus)], [float(err_plus)]]
    ax.errorbar(
        [float(obj["redshift"])], [float(obj["log_mbh_msun_std"])], yerr=yerr,
        fmt="o", color="black", ecolor="black", capsize=2.5, ms=5.5,
        label="canonical object mass", zorder=5,
    )
    ax.set_title(_object_title(obj))
    ax.set_xlabel("observed redshift")
    ax.set_ylabel("log10 MBH [Msun]")
    ax.set_xlim(12.2, 3.8)
    observed = float(obj["log_mbh_msun_std"])
    ax.set_ylim(min(4.5, observed - 2.0), max(10.8, observed + 1.0))
    ax.grid(alpha=0.22, lw=0.6)
    ax.legend(ncol=2, frameon=False, loc="best")
    fig.text(0.5, 0.012, "Reference tracks use z_seed=30, epsilon=0.1, and no merger boost.", ha="center", fontsize=7.5)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_compatibility_summary(compatibility: pd.DataFrame, output: Path) -> None:
    baseline = compatibility[
        compatibility["seed_model"].eq("heavy_dcbh")
        & compatibility["merger_boost"].eq(1.0)
    ]
    classes = sorted(baseline["object_class"].unique())
    fig, axes = plt.subplots(
        1, len(classes), figsize=(11.5, 4.6), squeeze=False, layout="constrained",
    )
    spin_labels = {
        case[1]: f"a={case[0]:+g}  (epsilon={float(thin_disk_radiative_efficiency(case[0])):.3f})"
        for case in SPIN_CASES
    }
    for index, (ax, object_class) in enumerate(zip(axes.flat, classes, strict=True)):
        group = baseline[baseline["object_class"].eq(object_class)]
        pivot = group.pivot(index="spin_case", columns="f_edd_avg", values="compatible_object_fraction")
        pivot = pivot.reindex([case[1] for case in SPIN_CASES])
        image = ax.imshow(pivot.to_numpy(), vmin=0, vmax=1, cmap="viridis", aspect="auto")
        ax.set_xticks(range(len(pivot.columns)), [f"{value:g}" for value in pivot.columns])
        ax.set_yticks(range(len(pivot.index)), [spin_labels[label] for label in pivot.index])
        for row in range(len(pivot.index)):
            for col in range(len(pivot.columns)):
                value = float(pivot.iloc[row, col])
                ax.text(col, row, f"{value:.0%}", ha="center", va="center", color="white" if value < 0.65 else "black", fontsize=8)
        ax.set_title(f"{object_class.replace('_', ' ')} (n={int(group['n_objects'].iloc[0])})")
        ax.set_xlabel(r"average $f_{\rm Edd}$")
        if index == 0:
            ax.set_ylabel("spin and thin-disk efficiency")
    cbar = fig.colorbar(image, ax=axes.ravel().tolist(), pad=0.02, fraction=0.03)
    cbar.set_label("compatible-object fraction")
    fig.suptitle(
        r"Class-specific heavy-seed compatibility ($10^4$--$10^6\,M_\odot$; $z_{\rm seed}=30$; $B=1$)",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220)
    plt.close(fig)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_contact_sheet(
    paths: list[Path],
    output: Path,
    *,
    cell: tuple[int, int],
    common_caption: str,
    caption_crop_px: int,
    columns: int = 5,
) -> tuple[int, int]:
    if not paths:
        raise ValueError(f"Cannot compile an empty contact sheet: {output}")
    rows = math.ceil(len(paths) / columns)
    gutter = 10
    banner = 70
    footer = 70
    width = columns * cell[0] + (columns - 1) * gutter
    height = banner + rows * cell[1] + (rows - 1) * gutter + footer
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=24)
    draw.text((18, 18), output.stem.replace("_", " "), fill="black", font=font)
    for index, path in enumerate(paths):
        with Image.open(path) as source:
            if caption_crop_px <= 0 or caption_crop_px >= source.height:
                raise ValueError(f"Invalid caption crop for {path}: {caption_crop_px}px")
            panel = source.crop((0, 0, source.width, source.height - caption_crop_px)).convert("RGB")
            panel.thumbnail(cell, Image.Resampling.LANCZOS)
        row, column = divmod(index, columns)
        x = column * (cell[0] + gutter) + (cell[0] - panel.width) // 2
        y = banner + row * (cell[1] + gutter) + (cell[1] - panel.height) // 2
        canvas.paste(panel, (x, y))
    caption_y = height - footer + 18
    draw.text((18, caption_y), common_caption, fill="black", font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, format="PNG", compress_level=9, dpi=(300, 300))
    return canvas.size


def generate_figures(eligible: pd.DataFrame) -> pd.DataFrame:
    configure_style()
    inventory = []
    ordered = eligible.sort_values(["object_class", "redshift", "physical_object_id"])
    for number, (_, obj) in enumerate(ordered.iterrows(), start=1):
        paths = object_product_paths(obj)
        plot_parameter_sheet(obj, paths["parameter_map"])
        plot_seed_redshift_map(obj, paths["seed_redshift_map"])
        plot_growth_track(obj, paths["growth_track"])
        for product_kind, path in paths.items():
            with Image.open(path) as image:
                width, height = image.size
            inventory.append({
                "science_release": SCIENCE_RELEASE,
                "artifact_kind": "per_object_figure",
                "product_kind": product_kind,
                "object_class": obj["object_class"],
                "physical_object_id": obj["physical_object_id"],
                "path": path.relative_to(ROOT).as_posix(),
                "width_px": width,
                "height_px": height,
                "dpi": 180 if product_kind != "parameter_map" else 160,
                "caption_policy": "standalone_plot_footer",
                "sha256": sha256(path),
            })
        if number % 20 == 0 or number == len(ordered):
            print(f"Generated all three growth figures for {number}/{len(ordered)} eligible objects")

    for object_class, group in ordered.groupby("object_class", sort=True):
        slug = class_slug(object_class)
        for product_kind, cell in [
            ("parameter_map", (1050, 720)),
            ("seed_redshift_map", (1050, 850)),
            ("growth_track", (1050, 850)),
        ]:
            paths = [object_product_paths(obj)[product_kind] for _, obj in group.iterrows()]
            output = COMPILED_DIR / f"v7_4_all_{slug}_{product_kind}s.png"
            width, height = compile_contact_sheet(
                paths,
                output,
                cell=cell,
                common_caption=COMPILED_CAPTIONS[product_kind],
                caption_crop_px=COMPILED_CAPTION_CROP_PX[product_kind],
            )
            inventory.append({
                "science_release": SCIENCE_RELEASE,
                "artifact_kind": "compiled_class_grid",
                "product_kind": product_kind,
                "object_class": object_class,
                "physical_object_id": "",
                "path": output.relative_to(ROOT).as_posix(),
                "width_px": width,
                "height_px": height,
                "dpi": 300,
                "caption_policy": "one_shared_gallery_footer",
                "sha256": sha256(output),
            })
            print(f"Compiled {len(paths)} {product_kind} panels: {output.relative_to(ROOT)}")
    return pd.DataFrame(inventory).sort_values(
        ["artifact_kind", "object_class", "product_kind", "physical_object_id"],
    ).reset_index(drop=True)


def verify_outputs(
    catalogue: pd.DataFrame,
    coverage: pd.DataFrame,
    unavailable: pd.DataFrame,
    compatibility: pd.DataFrame,
    gallery: pd.DataFrame | None = None,
) -> None:
    eligible = eligible_objects(catalogue)
    if len(coverage) != 218 or coverage["physical_object_id"].nunique() != 218:
        raise AssertionError("Coverage table must contain all 218 physical objects exactly once")
    if coverage["growth_product_status"].value_counts().to_dict() != {"complete": 196, "unavailable": 22}:
        raise AssertionError("Coverage table must identify 196 complete and 22 unavailable objects")
    if set(unavailable["physical_object_id"]) != set(catalogue[~catalogue["growth_ranking_eligible_flag"].map(boolish)]["physical_object_id"]):
        raise AssertionError("Unavailable table must exactly cover the ineligible catalogue objects")
    if compatibility["object_class"].nunique() != 2 or len(compatibility) != 288:
        raise AssertionError("Compatibility table must have 288 rows across two eligible classes")
    if not compatibility["compatible_object_fraction"].between(0, 1).all():
        raise AssertionError("Compatibility fractions must lie in [0, 1]")
    if compatibility.groupby("object_class")["n_objects"].first().to_dict() != eligible["object_class"].value_counts().to_dict():
        raise AssertionError("Compatibility class counts must match eligible catalogue membership")
    if gallery is not None:
        if len(gallery) != 594:
            raise AssertionError("Gallery inventory must contain 588 object figures and 6 class grids")
        if gallery["path"].nunique() != 594:
            raise AssertionError("Every gallery inventory path must be unique")
        if gallery["artifact_kind"].value_counts().to_dict() != {"per_object_figure": 588, "compiled_class_grid": 6}:
            raise AssertionError("Gallery artifact-kind counts are incorrect")


def main() -> None:
    catalogue = load_catalogue()
    eligible = eligible_objects(catalogue)
    coverage = build_coverage_table(catalogue)
    unavailable = build_unavailable_table(catalogue)
    compatibility = build_class_compatibility(eligible)
    verify_outputs(catalogue, coverage, unavailable, compatibility)

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(COVERAGE_PATH, index=False)
    unavailable.to_csv(UNAVAILABLE_PATH, index=False)
    compatibility.to_csv(COMPATIBILITY_PATH, index=False)
    plot_compatibility_summary(compatibility, COMPATIBILITY_FIGURE_PATH)
    gallery = generate_figures(eligible)
    gallery.to_csv(GALLERY_INVENTORY_PATH, index=False)
    verify_outputs(catalogue, coverage, unavailable, compatibility, gallery)

    print(f"Wrote {len(coverage)} coverage rows: {COVERAGE_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(unavailable)} unavailable-object rows: {UNAVAILABLE_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(compatibility)} class compatibility rows: {COMPATIBILITY_PATH.relative_to(ROOT)}")
    print(f"Indexed {len(gallery)} growth-gallery artifacts: {GALLERY_INVENTORY_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
