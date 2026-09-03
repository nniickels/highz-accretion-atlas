"""Build the complete all-object visual atlas for a canonical dataset.

Numerical growth products are calculated only for objects with a supported
canonical black-hole mass; all remaining objects receive explicit no-inference
panels.
"""

from __future__ import annotations

import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MPLCONFIGDIR = ROOT / ".codex_tmp" / "matplotlib"
MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from src.internal.fedd_mass_maps import (
    COMPATIBILITY_FEDD,
    MERGER_CASES,
    SEED_MODELS,
    SPIN_CASES,
    plot_fedd_mass_map,
)
from src.models import (
    cosmic_time_gyr,
    predicted_log_mbh,
    required_seed_mass_for_growth,
    slim_disk_effective_efficiency,
    thin_disk_radiative_efficiency,
)


VERSION = "v3"
CATALOGUE = ROOT / "data/processed/v3/v3_accreting_objects.csv"
UNCERTAINTY = ROOT / "results/v3/tables/v3_object_uncertainty_ranking.csv"
FIGURES = ROOT / "results/v3/figures"
TABLES = ROOT / "results/v3/tables"
GALLERY = ROOT / "results/v3/gallery"

FIGURE_PATHS = {
    "catalogue_landscape": FIGURES / "v3_catalogue_growth_landscape.png",
    "class_aware_pressure": FIGURES / "v3_class_aware_growth_pressure.png",
    "measurement_sensitivity": FIGURES / "v3_measurement_sensitivity.png",
    "growth_tracks": FIGURES / "v3_all_object_growth_tracks.png",
    "full_assumption_growth_tracks": FIGURES / "v3_all_object_growth_tracks_full_assumptions.png",
    "filtered_full_assumption_growth_tracks": (
        FIGURES / "v3_all_object_growth_tracks_full_assumptions_uncertainty_filtered.png"
    ),
    "compatibility_summary": FIGURES / "v3_compatibility_summary.png",
    "uncertainty_summary": FIGURES / "v3_monte_carlo_summary.png",
    "fedd_mass_gallery": FIGURES / "v3_all_object_fedd_mass_map_gallery.png",
    "compatibility": FIGURES / "v3_all_object_compatibility_atlas.png",
    "uncertainty": FIGURES / "v3_all_object_monte_carlo_uncertainty.png",
}
TABLE_PATHS = {
    "coverage": TABLES / "v3_all_object_visual_coverage.csv",
    "compatibility": TABLES / "v3_all_object_compatibility.csv",
}

COLORS = {
    "broad_line_agn": "#176B87",
    "luminous_quasar_comparison": "#B66A1E",
    "narrow_line_agn_candidate": "#6B5CA5",
    "xray_agn_candidate": "#777777",
}
LABELS = {
    "broad_line_agn": "Broad-line AGN",
    "luminous_quasar_comparison": "Luminous quasars",
    "narrow_line_agn_candidate": "Narrow-line candidates",
    "xray_agn_candidate": "X-ray candidates",
}
SEED_LABELS = {
    "light_popiii": "Light / Pop III",
    "intermediate_cluster": "Intermediate / cluster",
    "heavy_dcbh": "Heavy / DCBH",
    "pbh": "Primordial black hole",
}

FULL_TRACK_SEEDS = (
    (2.0, r"$10^2\,M_\odot$", "#2F6B9A"),
    (4.0, r"$10^4\,M_\odot$", "#3A8B5C"),
    (5.0, r"$10^5\,M_\odot$", "#B66A1E"),
)
FULL_TRACK_FEDD_STYLES = (
    (0.3, (0, (5, 3))),
    (1.0, "-"),
    (2.0, (0, (1, 1))),
)
FULL_TRACK_EPSILON_CASES = (
    (0.1, r"$\epsilon=0.100$", 0.75),
    (float(thin_disk_radiative_efficiency(-1.0)), r"$\epsilon=0.038$", 0.95),
    (float(thin_disk_radiative_efficiency(0.0)), r"$\epsilon=0.057$", 1.15),
    (float(thin_disk_radiative_efficiency(1.0)), r"$\epsilon=0.423$", 1.35),
)
FULL_TRACK_MERGER_CASES = (
    (1.0, "no merger boost", 0.95),
    (2.0, r"$B_{\rm merge}=2$", 0.45),
)
FULL_TRACK_CURVE_COUNT = (
    len(FULL_TRACK_SEEDS)
    * len(FULL_TRACK_FEDD_STYLES)
    * len(FULL_TRACK_EPSILON_CASES)
    * len(FULL_TRACK_MERGER_CASES)
)
HIGH_UNCERTAINTY_LUMINOUS_QUASAR_THRESHOLD_DEX = 0.5


def high_uncertainty_luminous_quasars(objects: pd.DataFrame) -> pd.DataFrame:
    """Return growth-eligible luminous quasars above the declared mass-error cut."""
    max_error = objects[
        ["log_mbh_err_minus_std", "log_mbh_err_plus_std"]
    ].fillna(0.0).max(axis=1)
    mask = (
        objects["growth_ranking_eligible_flag"].map(boolish)
        & objects["object_class"].eq("luminous_quasar_comparison")
        & max_error.gt(HIGH_UNCERTAINTY_LUMINOUS_QUASAR_THRESHOLD_DEX)
    )
    columns = [
        "physical_object_id", "object_id", "source_key", "redshift",
        "log_mbh_msun_std", "log_mbh_err_minus_std", "log_mbh_err_plus_std",
    ]
    excluded = objects.loc[mask, columns].copy()
    excluded["max_mass_uncertainty_dex"] = max_error.loc[mask]
    excluded["exclusion_threshold_dex"] = HIGH_UNCERTAINTY_LUMINOUS_QUASAR_THRESHOLD_DEX
    excluded["exclusion_reason"] = "luminous_quasar_mass_uncertainty_gt_0p5_dex"
    return excluded.sort_values("max_mass_uncertainty_dex", ascending=False)


def boolish(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return bool(value)


def slug(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    objects = pd.read_csv(CATALOGUE, low_memory=False)
    uncertainty = pd.read_csv(UNCERTAINTY)
    if objects.empty or not objects["physical_object_id"].is_unique:
        raise ValueError(f"{VERSION} catalogue must contain unique objects")
    eligible = objects["growth_ranking_eligible_flag"].map(boolish)
    if set(uncertainty["physical_object_id"]) != set(objects.loc[eligible, "physical_object_id"]):
        raise ValueError("Monte Carlo table must exactly cover the growth-eligible objects")
    return objects, uncertainty


def object_paths(obj: pd.Series) -> dict[str, Path]:
    stem = slug(obj["physical_object_id"])
    return {
        "fedd_mass_map": GALLERY / "fedd_mass_maps" / f"{VERSION}_fedd_mass_map_{stem}.png",
    }


def status_panel(obj: pd.Series, product: str, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7.8), constrained_layout=True)
    ax.set_facecolor("#F2F1EC")
    ax.axis("off")
    reason = str(obj["growth_ranking_eligibility_reason"]).replace("_", " ")
    lines = [
        str(obj["object_id"]),
        str(obj["physical_object_id"]),
        f"z = {float(obj['redshift']):.3f}",
        LABELS.get(str(obj["object_class"]), str(obj["object_class"])),
        "",
        f"{product.replace('_', ' ').title()} unavailable",
        "No numerical growth inference was made.",
        f"Reason: {reason}.",
        f"The object remains part of the {VERSION} catalogue and visual audit.",
    ]
    ax.text(0.5, 0.55, "\n".join(lines), ha="center", va="center", fontsize=17,
            linespacing=1.45, color="#303030")
    ax.add_patch(plt.Rectangle((0.04, 0.05), 0.92, 0.9, fill=False, lw=2,
                               edgecolor=COLORS.get(str(obj["object_class"]), "#777777"),
                               transform=ax.transAxes))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160, facecolor="white")
    plt.close(fig)


def materialize_fedd_mass_maps(objects: pd.DataFrame, *, rebuild: bool) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, obj in objects.sort_values(["object_class", "redshift", "physical_object_id"]).iterrows():
        eligible = boolish(obj["growth_ranking_eligible_flag"])
        paths = object_paths(obj)
        for kind, output in paths.items():
            output.parent.mkdir(parents=True, exist_ok=True)
            if rebuild or not output.exists():
                if eligible:
                    plot_fedd_mass_map(obj, output)
                else:
                    status_panel(obj, kind, output)
            rows.append({
                "release": VERSION,
                "physical_object_id": obj["physical_object_id"],
                "object_id": obj["object_id"],
                "object_class": obj["object_class"],
                "growth_ranking_eligible_flag": eligible,
                "product_kind": kind,
                "product_status": "numerical_growth_product" if eligible else "no_inference_status_panel",
                "status_reason": "eligible_canonical_numeric_mbh" if eligible else obj["growth_ranking_eligibility_reason"],
                "path": output.relative_to(ROOT).as_posix(),
            })
    coverage = pd.DataFrame(rows)
    if len(coverage) != len(objects) or coverage["physical_object_id"].nunique() != len(objects):
        raise AssertionError("f_Edd/mass-map coverage must contain one panel for every object")
    return coverage


def plot_all_object_growth_tracks(objects: pd.DataFrame, output: Path) -> None:
    eligible = objects[objects["growth_ranking_eligible_flag"].map(boolish)].copy()
    unavailable = objects[~objects["growth_ranking_eligible_flag"].map(boolish)].copy()
    redshift = np.linspace(4.0, 12.0, 300)
    fig, (ax, status) = plt.subplots(2, 1, figsize=(15, 10.5),
                                     gridspec_kw={"height_ratios": [4.2, 1]},
                                     constrained_layout=True)
    track_colors = {2.0: "#2F6B9A", 4.0: "#3A8B5C", 6.0: "#A74335"}
    for seed in (2.0, 4.0, 6.0):
        for fedd, ls in ((0.3, "--"), (1.0, "-")):
            ax.plot(redshift, predicted_log_mbh(seed, fedd, 0.1, 30.0, redshift),
                    color=track_colors[seed], ls=ls, lw=1.35,
                    label=rf"$10^{{{int(seed)}}}\,M_\odot$, $f_{{\rm Edd}}={fedd:g}$")
    for object_class, group in eligible.groupby("object_class"):
        ax.scatter(group["redshift"], group["log_mbh_msun_std"], s=30, alpha=0.75,
                   color=COLORS[object_class], edgecolor="white", linewidth=0.35,
                   label=f"{LABELS[object_class]} ({len(group)})")
    ax.set(xlim=(12.2, 3.8), ylim=(4.5, 10.8), xlabel="Observed redshift",
           ylabel=r"Canonical $\log_{10}(M_{\rm BH}/M_\odot)$",
           title=f"{VERSION}: all-object growth-track atlas")
    ax.grid(alpha=0.2)
    ax.legend(ncol=3, frameon=False, fontsize=9)

    status.set_xlim(12.2, 3.8)
    status.set_ylim(-0.6, 3.6)
    for y, (object_class, group) in enumerate(unavailable.groupby("object_class", sort=True)):
        status.scatter(group["redshift"], np.full(len(group), y), marker="|", s=260,
                       linewidths=2, color=COLORS[object_class])
    classes = list(unavailable.groupby("object_class", sort=True).groups)
    status.set_yticks(range(len(classes)), [f"{LABELS[key]} (no numerical mass)" for key in classes])
    status.set_xlabel(f"Redshift of all {len(unavailable)} catalogue-only objects")
    status.grid(axis="x", alpha=0.2)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, facecolor="white")
    plt.close(fig)


def plot_full_assumption_growth_tracks(
    objects: pd.DataFrame,
    output: Path,
    *,
    exclude_high_uncertainty_luminous_quasars: bool = False,
) -> None:
    """Render the historical v1 72-curve grid against v3 catalogue objects."""
    eligible = objects[objects["growth_ranking_eligible_flag"].map(boolish)].copy()
    unavailable = objects[~objects["growth_ranking_eligible_flag"].map(boolish)].copy()
    if exclude_high_uncertainty_luminous_quasars:
        excluded_ids = set(high_uncertainty_luminous_quasars(objects)["physical_object_id"])
        eligible = eligible.loc[~eligible["physical_object_id"].isin(excluded_ids)].copy()
    redshift = np.linspace(12.0, 4.0, 400)
    fig, (ax, status) = plt.subplots(
        2, 1, figsize=(15, 12.5), gridspec_kw={"height_ratios": [4.4, 1]},
    )
    fig.subplots_adjust(left=0.14, right=0.985, bottom=0.20, top=0.87, hspace=0.16)

    for log_seed, _, color in FULL_TRACK_SEEDS:
        for fedd, linestyle in FULL_TRACK_FEDD_STYLES:
            for epsilon, _, linewidth in FULL_TRACK_EPSILON_CASES:
                for boost, _, alpha in FULL_TRACK_MERGER_CASES:
                    ax.plot(
                        redshift,
                        predicted_log_mbh(log_seed, fedd, epsilon, 30.0, redshift,
                                          merger_boost=boost),
                        color=color, ls=linestyle, lw=linewidth, alpha=alpha,
                    )

    for object_class, group in eligible.groupby("object_class"):
        yerr = np.vstack([
            group["log_mbh_err_minus_std"].fillna(0.0).to_numpy(float),
            group["log_mbh_err_plus_std"].fillna(0.0).to_numpy(float),
        ])
        ax.errorbar(
            group["redshift"], group["log_mbh_msun_std"], yerr=yerr, fmt="o",
            ms=4.2, mfc=COLORS[object_class], mec="white", mew=0.35,
            ecolor=COLORS[object_class], elinewidth=0.55, capsize=1.4, alpha=0.8,
        )

    title = f"{VERSION}: all-object growth tracks"
    if exclude_high_uncertainty_luminous_quasars:
        title += "\nexcluding luminous quasars with mass uncertainty > 0.5 dex"
    ax.set(
        xlim=(12.2, 3.8), ylim=(4.5, 10.8), xlabel="Observed redshift",
        ylabel=r"Canonical $\log_{10}(M_{\rm BH}/M_\odot)$",
        title=title,
    )
    ax.grid(alpha=0.2)

    age_axis = ax.twiny()
    age_axis.set_xlim(ax.get_xlim())
    age_redshifts = np.array([12, 10, 8, 7, 6, 5, 4], dtype=float)
    age_axis.set_xticks(age_redshifts)
    age_axis.set_xticklabels([f"{age:.2f}" for age in cosmic_time_gyr(age_redshifts)])
    age_axis.set_xlabel("Age of the Universe (Gyr)", labelpad=7)

    seed_handles = [Line2D([0], [0], color=color, lw=2.2, label=label)
                    for _, label, color in FULL_TRACK_SEEDS]
    class_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLORS[key],
               markeredgecolor="white", markersize=6,
               label=f"{LABELS[key]} ({len(group)})")
        for key, group in eligible.groupby("object_class")
    ]
    object_legend = ax.legend(
        handles=seed_handles + class_handles, title="Seed mass and v3 objects",
        loc="upper left", ncols=3, frameon=False, fontsize=8.5,
    )
    ax.add_artist(object_legend)

    encoding_handles = [
        Line2D([0], [0], color="#4A4A4A", lw=2.2, ls=linestyle,
               label=rf"$f_{{\rm Edd}}={fedd:g}$")
        for fedd, linestyle in FULL_TRACK_FEDD_STYLES
    ] + [
        Line2D([0], [0], color="#4A4A4A", lw=linewidth, label=label)
        for _, label, linewidth in FULL_TRACK_EPSILON_CASES
    ] + [
        Line2D([0], [0], color="#4A4A4A", lw=2.2, alpha=alpha, label=label)
        for _, label, alpha in FULL_TRACK_MERGER_CASES
    ]

    status.set_xlim(12.2, 3.8)
    status.set_ylim(-0.6, 3.6)
    for y, (object_class, group) in enumerate(unavailable.groupby("object_class", sort=True)):
        status.scatter(group["redshift"], np.full(len(group), y), marker="|", s=260,
                       linewidths=2, color=COLORS[object_class])
    classes = list(unavailable.groupby("object_class", sort=True).groups)
    status.set_yticks(range(len(classes)), [LABELS[key] for key in classes])
    status.set_ylabel("No numerical mass", labelpad=12)
    status.set_xlabel(f"Redshift of all {len(unavailable)} catalogue-only objects")
    status.grid(axis="x", alpha=0.2)

    fig.legend(
        handles=encoding_handles,
        title="Growth encoding; all 24 combinations are plotted for each seed mass",
        loc="lower center", bbox_to_anchor=(0.55, 0.025), ncols=5,
        frameon=False, fontsize=9, columnspacing=1.15,
    )
    fig.text(
        0.55, 0.008,
        "Line style encodes f_Edd; width encodes constant radiative efficiency; "
        "opacity encodes merger boost.",
        ha="center", fontsize=8,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, facecolor="white")
    plt.close(fig)

def compile_fedd_mass_gallery(objects: pd.DataFrame, output: Path) -> None:
    ordered = objects.sort_values(["object_class", "redshift", "physical_object_id"])
    paths = [object_paths(obj)["fedd_mass_map"] for _, obj in ordered.iterrows()]
    columns, cell, gutter, header, footer = 6, (760, 490), 8, 90, 90
    rows = math.ceil(len(paths) / columns)
    width = columns * cell[0] + (columns - 1) * gutter
    height = header + rows * cell[1] + (rows - 1) * gutter + footer
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.load_default(size=30)
    body_font = ImageFont.load_default(size=20)
    draw.text((20, 20), f"{VERSION} - complete {len(objects)}-object f_Edd/mass-map gallery", fill="black", font=title_font)
    for index, path in enumerate(paths):
        with Image.open(path) as source:
            panel = source.convert("RGB")
            panel.thumbnail(cell, Image.Resampling.LANCZOS)
        row, col = divmod(index, columns)
        x = col * (cell[0] + gutter) + (cell[0] - panel.width) // 2
        y = header + row * (cell[1] + gutter) + (cell[1] - panel.height) // 2
        canvas.paste(panel, (x, y))
    draw.text((20, height - footer + 20),
              f"{int(objects['growth_ranking_eligible_flag'].map(boolish).sum())} numerical sheets; "
              f"{int((~objects['growth_ranking_eligible_flag'].map(boolish)).sum())} no-inference panels.",
              fill="black", font=body_font)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, format="PNG", compress_level=6, dpi=(300, 300))


def build_object_compatibility(objects: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, obj in objects.sort_values(["object_class", "physical_object_id"]).iterrows():
        eligible = boolish(obj["growth_ranking_eligible_flag"])
        for seed_name, seed_model in SEED_MODELS.items():
            for spin, spin_case, _ in SPIN_CASES:
                for boost, merger_case in MERGER_CASES:
                    for fedd in (0.3, 1.0, 2.0):
                        required = np.nan
                        compatible: object = pd.NA
                        if eligible:
                            epsilon = float(slim_disk_effective_efficiency(spin, fedd))
                            required = float(required_seed_mass_for_growth(
                                float(obj["log_mbh_msun_std"]), fedd, epsilon, 30.0,
                                float(obj["redshift"]), merger_boost=boost,
                            ))
                            compatible = bool(seed_model.log_mseed_min <= required <= seed_model.log_mseed_max)
                        rows.append({
                            "release": VERSION, "physical_object_id": obj["physical_object_id"],
                            "object_id": obj["object_id"], "object_class": obj["object_class"],
                            "growth_ranking_eligible_flag": eligible, "seed_model": seed_name,
                            "spin_case": spin_case, "merger_case": merger_case, "f_edd_avg": fedd,
                            "required_log_mseed": required, "compatible": compatible,
                            "status": "calculated" if eligible else str(obj["growth_ranking_eligibility_reason"]),
                        })
    result = pd.DataFrame(rows)
    if len(result) != len(objects) * len(SEED_MODELS) * len(SPIN_CASES) * len(MERGER_CASES) * 3:
        raise AssertionError("Compatibility table does not cover every object/scenario")
    return result


def plot_compatibility_atlas(objects: pd.DataFrame, compatibility: pd.DataFrame, output: Path) -> None:
    ordered = objects.sort_values(["object_class", "redshift", "physical_object_id"]).reset_index(drop=True)
    ids = ordered["physical_object_id"].tolist()
    fig, axes = plt.subplots(1, len(SEED_MODELS), figsize=(32, 48), sharey=True, constrained_layout=True)
    cmap = ListedColormap(["#D5D2CA", "#A74335", "#2E8B57"])
    for ax, seed_name in zip(axes, SEED_MODELS, strict=True):
        subset = compatibility[compatibility["seed_model"].eq(seed_name)].copy()
        subset["scenario"] = subset.apply(
            lambda r: f"{r.spin_case.replace('spin_', '').replace('_eps0p038', '').replace('_eps0p057', '').replace('_eps0p423', '')}\nB={int(r.merger_case == 'merger_boost_x2') + 1}, f={r.f_edd_avg:g}", axis=1)
        scenario_order = list(dict.fromkeys(subset["scenario"]))
        matrix = np.full((len(ids), len(scenario_order)), -1.0)
        lookup = {(pid, scenario): value for pid, scenario, value in zip(
            subset["physical_object_id"], subset["scenario"], subset["compatible"], strict=True)}
        for i, pid in enumerate(ids):
            for j, scenario in enumerate(scenario_order):
                value = lookup[(pid, scenario)]
                matrix[i, j] = -1 if pd.isna(value) else int(bool(value))
        ax.imshow(matrix, aspect="auto", interpolation="nearest", cmap=cmap, vmin=-1, vmax=1)
        ax.set_xticks(range(len(scenario_order)), scenario_order, rotation=90, fontsize=7)
        ax.set_title(f"{SEED_LABELS[seed_name]} compatibility")
        ax.set_xlabel("spin / merger boost / average f_Edd")
    axes[0].set_yticks(range(len(ids)), ordered["object_id"], fontsize=5.2)
    axes[0].set_ylabel(f"All {len(objects)} catalogue objects")
    fig.suptitle(f"{VERSION}: object-by-object seed/growth compatibility", fontsize=20)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200, facecolor="white")
    plt.close(fig)


def plot_compatibility_summary(objects: pd.DataFrame, compatibility: pd.DataFrame, output: Path) -> None:
    eligible_classes = [
        key for key in COLORS
        if bool(objects.loc[objects["object_class"].eq(key), "growth_ranking_eligible_flag"].map(boolish).any())
    ]
    fig, axes = plt.subplots(len(eligible_classes), len(SEED_MODELS), figsize=(18, 8.5),
                             sharex=True, sharey=True, constrained_layout=True, squeeze=False)
    image = None
    for row, object_class in enumerate(eligible_classes):
        for col, seed_name in enumerate(SEED_MODELS):
            group = compatibility[
                compatibility["object_class"].eq(object_class)
                & compatibility["seed_model"].eq(seed_name)
                & compatibility["growth_ranking_eligible_flag"]
            ].copy()
            pivot = group.pivot_table(index="spin_case", columns=["merger_case", "f_edd_avg"],
                                      values="compatible", aggfunc="mean").astype(float)
            pivot = pivot.reindex([case[1] for case in SPIN_CASES])
            image = axes[row, col].imshow(pivot, vmin=0, vmax=1, cmap="viridis", aspect="auto")
            for y in range(pivot.shape[0]):
                for x in range(pivot.shape[1]):
                    value = float(pivot.iloc[y, x])
                    axes[row, col].text(x, y, f"{value:.0%}", ha="center", va="center",
                                        fontsize=7, color="white" if value < 0.6 else "black")
            axes[row, col].set_title(f"{LABELS[object_class]} — {SEED_LABELS[seed_name]}")
            axes[row, col].set_xticks(range(pivot.shape[1]),
                                      [f"B={2 if b == 'merger_boost_x2' else 1}\nf={f:g}" for b, f in pivot.columns],
                                      fontsize=7)
            axes[row, col].set_yticks(range(len(SPIN_CASES)), ["a=-1", "a=0", "a=+1"])
    assert image is not None
    fig.colorbar(image, ax=axes.ravel().tolist(), fraction=0.018, pad=0.012,
                 label="Fraction of class objects compatible")
    fig.suptitle(f"{VERSION} compatibility summary — every growth-eligible object", fontsize=17)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, facecolor="white")
    plt.close(fig)


def plot_all_object_uncertainty(objects: pd.DataFrame, uncertainty: pd.DataFrame, output: Path) -> None:
    joined = objects.merge(uncertainty, on=["physical_object_id", "object_id", "object_class"], how="left", suffixes=("", "_mc"))
    joined["class_order"] = joined["object_class"].map({key: i for i, key in enumerate(COLORS)})
    joined = joined.sort_values(["class_order", "rank_uncertainty_global_navigation", "redshift"]).reset_index(drop=True)
    y = np.arange(len(joined))
    med = joined["required_fedd_seed1e2_p50"].to_numpy(float)
    lo = med - joined["required_fedd_seed1e2_p16"].to_numpy(float)
    hi = joined["required_fedd_seed1e2_p84"].to_numpy(float) - med
    fig, ax = plt.subplots(figsize=(16, 52), constrained_layout=True)
    for object_class, group in joined.groupby("object_class", sort=False):
        idx = group.index.to_numpy()
        valid = np.isfinite(med[idx])
        ax.errorbar(med[idx][valid], y[idx][valid], xerr=np.vstack([lo[idx][valid], hi[idx][valid]]),
                    fmt="o", ms=3.8, elinewidth=1, capsize=1.5,
                    color=COLORS[object_class], ecolor=COLORS[object_class],
                    label=f"{LABELS[object_class]} ({valid.sum()} numerical)")
        if (~valid).any():
            ax.scatter(np.full((~valid).sum(), -0.08), y[idx][~valid], marker="x", s=28,
                       color=COLORS[object_class], label=f"{LABELS[object_class]} unavailable")
    ax.axvline(1.0, color="#8B1A1A", ls="--", lw=1.2)
    ax.axvline(0.0, color="#777777", lw=0.8)
    ax.set_yticks(y, joined["object_id"], fontsize=5.5)
    ax.invert_yaxis()
    ax.set(xlim=(-0.16, max(2.0, float(np.nanpercentile(med + hi, 99.5)) * 1.08)),
           xlabel=r"Monte Carlo required $f_{\rm Edd}$ for a $10^2\,M_\odot$ seed (median, 16–84%)",
           ylabel=f"All {len(objects)} catalogue objects",
           title=f"{VERSION}: complete object-level Monte Carlo uncertainty atlas")
    ax.grid(axis="x", alpha=0.2)
    ax.legend(frameon=False, ncol=2, loc="lower right")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200, facecolor="white")
    plt.close(fig)


def plot_uncertainty_summary(objects: pd.DataFrame, uncertainty: pd.DataFrame, output: Path) -> None:
    fig, (ax, status) = plt.subplots(1, 2, figsize=(15, 6.8),
                                     gridspec_kw={"width_ratios": [3.5, 1]}, constrained_layout=True)
    for object_class, group in uncertainty.groupby("object_class"):
        width = group["required_fedd_seed1e2_p84"] - group["required_fedd_seed1e2_p16"]
        ax.scatter(group["required_fedd_seed1e2_p50"], group["prob_required_fedd_seed1e2_gt_1"],
                   s=22 + 80 * np.clip(width, 0, 1), alpha=0.7, color=COLORS[object_class],
                   edgecolor="white", linewidth=0.35, label=f"{LABELS[object_class]} ({len(group)})")
    ax.axvline(1, color="#8B1A1A", ls="--", lw=1.1)
    ax.set(xlabel=r"Median required $f_{\rm Edd}$ for a $10^2\,M_\odot$ seed",
           ylabel=r"Monte Carlo $P(f_{\rm Edd,required}>1)$",
           title=f"All {len(uncertainty)} numerical Monte Carlo posteriors")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    unavailable = objects[~objects["growth_ranking_eligible_flag"].map(boolish)]
    counts = unavailable["object_class"].value_counts().reindex(COLORS, fill_value=0)
    shown = counts[counts.gt(0)]
    status.barh(range(len(shown)), shown, color=[COLORS[key] for key in shown.index])
    status.set_yticks(range(len(shown)), [LABELS[key] for key in shown.index])
    status.set(xlabel="Objects", title=f"Explicitly unavailable ({len(unavailable)})")
    for y, value in enumerate(shown):
        status.text(value + 0.2, y, str(int(value)), va="center")
    fig.suptitle(f"{VERSION} Monte Carlo uncertainty summary — all {len(objects)} objects represented", fontsize=17)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, facecolor="white")
    plt.close(fig)
