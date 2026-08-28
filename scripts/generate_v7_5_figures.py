"""Generate high-resolution paper figures and current gallery coverage for v7.5."""

from __future__ import annotations

import os
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


OBJECTS = ROOT / "data/processed/v7_5/v7_5_accreting_objects.csv"
TABLES = ROOT / "results/tables"
FIGURES = ROOT / "results/figures"
GALLERIES = ROOT / "results/galleries"
V74_COVERAGE = ROOT / "results/past_releases/v7_4/tables/v7_4_growth_product_coverage.csv"
OUTPUT_PATHS = {
    "catalogue_growth_landscape": FIGURES / "v7_5_catalogue_growth_landscape.png",
    "class_aware_growth_pressure": FIGURES / "v7_5_class_aware_growth_pressure.png",
    "uncertainty_robustness": FIGURES / "v7_5_uncertainty_robustness.png",
    "measurement_sensitivity": FIGURES / "v7_5_measurement_sensitivity.png",
    "gallery_coverage": TABLES / "v7_5_growth_gallery_coverage.csv",
}

COLORS = {
    "broad_line_agn": "#176B87",
    "luminous_quasar_comparison": "#B66A1E",
    "narrow_line_agn_candidate": "#6B5CA5",
    "xray_agn_candidate": "#8A8A8A",
}
LABELS = {
    "broad_line_agn": "Broad-line AGN",
    "luminous_quasar_comparison": "Luminous quasars",
    "narrow_line_agn_candidate": "Narrow-line candidates",
    "xray_agn_candidate": "X-ray candidates",
}


def _style() -> None:
    plt.rcParams.update({
        "font.size": 11, "axes.titlesize": 14, "axes.labelsize": 12,
        "legend.fontsize": 10, "figure.facecolor": "white", "axes.facecolor": "#FAFAF8",
        "axes.grid": True, "grid.alpha": 0.18, "savefig.bbox": "tight",
    })


def _load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_csv(OBJECTS),
        pd.read_csv(TABLES / "v7_5_class_aware_object_point_ranking.csv"),
        pd.read_csv(TABLES / "v7_5_class_aware_object_uncertainty_ranking.csv"),
        pd.read_csv(TABLES / "v7_5_class_aware_alternate_measurement_sensitivity.csv"),
    )


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=360, facecolor="white")
    plt.close(fig)


def plot_catalogue_landscape(objects: pd.DataFrame, point: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), constrained_layout=True)
    ax = axes[0]
    for object_class, group in point.groupby("object_class"):
        ax.scatter(group["redshift"], group["log_mbh_msun_std"], s=30, alpha=0.78,
                   color=COLORS[object_class], label=LABELS[object_class], edgecolor="white", linewidth=0.35)
    ax.set(xlabel="Redshift", ylabel=r"Canonical $\log_{10}(M_\mathrm{BH}/M_\odot)$",
           title="Growth-eligible physical objects")
    ax.legend(frameon=False)
    ax = axes[1]
    counts = objects.groupby(["object_class", "growth_ranking_eligible_flag"]).size().unstack(fill_value=0)
    for key in [True, False]:
        if key not in counts:
            counts[key] = 0
    order = list(COLORS)
    counts = counts.reindex(order, fill_value=0)
    y = np.arange(len(order))
    ax.barh(y, counts[True], color=[COLORS[key] for key in order], label="Growth products available")
    ax.barh(y, counts[False], left=counts[True], color="#D8D8D3", hatch="//", label="Catalogue-only")
    ax.set_yticks(y, [LABELS[key] for key in order])
    ax.set(xlabel="Physical objects", title="Catalogue and gallery coverage")
    ax.legend(frameon=False, loc="upper right")
    fig.suptitle("High-z accretion atlas: current v7.5 landscape", fontsize=17, fontweight="bold")
    _save(fig, OUTPUT_PATHS["catalogue_growth_landscape"])


def plot_pressure(point: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), constrained_layout=True)
    classes = [key for key in COLORS if key in set(point["object_class"])]
    for ax, column, ylabel, title in [
        (axes[0], "required_fedd_seed1e2", r"Required $f_\mathrm{Edd}$ for $10^2\,M_\odot$ seed", "Light-seed pressure"),
        (axes[1], "required_log_mseed_fedd0p3", r"Required $\log_{10}(M_\mathrm{seed}/M_\odot)$ at $f_\mathrm{Edd}=0.3$", "Heavy-seed pressure"),
    ]:
        data = [point.loc[point["object_class"].eq(key), column].to_numpy() for key in classes]
        boxes = ax.boxplot(data, patch_artist=True, widths=0.62, showfliers=False)
        for patch, key in zip(boxes["boxes"], classes, strict=True):
            patch.set(facecolor=COLORS[key], alpha=0.65)
        rng = np.random.default_rng(20260827)
        for index, (key, values) in enumerate(zip(classes, data, strict=True), start=1):
            ax.scatter(index + rng.uniform(-0.16, 0.16, len(values)), values, s=11,
                       color=COLORS[key], alpha=0.45, linewidth=0)
        ax.set_xticks(range(1, len(classes) + 1), [LABELS[key] for key in classes], rotation=16, ha="right")
        ax.set(ylabel=ylabel, title=title)
    fig.suptitle("Class-aware growth-pressure distributions (descriptive only)", fontsize=17, fontweight="bold")
    _save(fig, OUTPUT_PATHS["class_aware_growth_pressure"])


def plot_uncertainty(uncertainty: pd.DataFrame) -> None:
    top = uncertainty.nsmallest(20, "rank_uncertainty_global_navigation").sort_values(
        "required_fedd_seed1e2_p50"
    )
    y = np.arange(len(top))
    med = top["required_fedd_seed1e2_p50"].to_numpy()
    lo = med - top["required_fedd_seed1e2_p16"].to_numpy()
    hi = top["required_fedd_seed1e2_p84"].to_numpy() - med
    fig, ax = plt.subplots(figsize=(12.5, 9), constrained_layout=True)
    colors = [COLORS[value] for value in top["object_class"]]
    for index, color in enumerate(colors):
        ax.errorbar(med[index], y[index], xerr=[[lo[index]], [hi[index]]], fmt="none",
                    ecolor=color, elinewidth=1.7, capsize=2.5)
    ax.scatter(med, y, color=colors, s=42, zorder=3, edgecolor="white", linewidth=0.5)
    ax.axvline(1.0, color="#9B2C2C", linestyle="--", linewidth=1.2, label=r"$f_\mathrm{Edd}=1$")
    ax.set_yticks(y, top["object_id"].astype(str))
    ax.set(xlabel=r"Required $f_\mathrm{Edd}$ for a $10^2\,M_\odot$ seed (median and 16–84%)",
           title="Highest uncertainty-aware growth pressure: 20-object navigation view")
    ax.legend(frameon=False)
    _save(fig, OUTPUT_PATHS["uncertainty_robustness"])


def plot_sensitivity(sensitivity: pd.DataFrame) -> None:
    ordered = sensitivity.sort_values(
        ["object_class", "physical_object_id", "alternate_measurement_id"]
    ).reset_index(drop=True)
    fig, (ax, key_ax) = plt.subplots(
        1, 2, figsize=(14, 7), gridspec_kw={"width_ratios": [3.2, 1.35]},
        constrained_layout=True,
    )
    colors = [COLORS[value] for value in ordered["object_class"]]
    ax.scatter(ordered["delta_log_mbh_alternate_minus_default"],
               ordered["delta_required_fedd_alternate_minus_default"],
               c=colors, s=70, edgecolor="white", linewidth=0.6)
    ax.axhline(0, color="#555555", linewidth=1)
    ax.axvline(0, color="#555555", linewidth=1)
    for index, row in ordered.iterrows():
        ax.annotate(str(index + 1),
                    (row["delta_log_mbh_alternate_minus_default"], row["delta_required_fedd_alternate_minus_default"]),
                    xytext=(5, 5), textcoords="offset points", fontsize=9, fontweight="bold")
    ax.set(xlabel=r"Alternate minus preferred $\Delta\log_{10}M_\mathrm{BH}$",
           ylabel=r"Alternate minus preferred $\Delta f_\mathrm{Edd,required}$",
           title="Sensitivity to retained alternate measurements")
    key_ax.axis("off")
    lines = [
        f"{index + 1:>2}. {row['physical_object_id'].replace('HZA-', '')}\n"
        f"     {row['alternate_measurement_id']}"
        for index, row in ordered.iterrows()
    ]
    key_ax.text(0.0, 1.0, "Object / alternate measurement\n\n" + "\n".join(lines),
                va="top", ha="left", fontsize=8.2, family="monospace", linespacing=1.22)
    _save(fig, OUTPUT_PATHS["measurement_sensitivity"])


def build_gallery_coverage(objects: pd.DataFrame) -> pd.DataFrame:
    old = pd.read_csv(V74_COVERAGE).set_index("physical_object_id")
    rows = []
    for _, obj in objects.sort_values("physical_object_id").iterrows():
        object_id = obj["physical_object_id"]
        eligible = bool(obj["growth_ranking_eligible_flag"])
        inherited = object_id in old.index and old.loc[object_id, "growth_product_status"] == "complete"
        rows.append({
            "science_release": "v7.5-figures-and-gallery",
            "input_catalogue_release": "v7.5-accreting-atlas-catalogue",
            "physical_object_id": object_id, "object_id": obj["object_id"],
            "object_class": obj["object_class"], "growth_ranking_eligible_flag": eligible,
            "growth_product_status": "complete_inherited_v7_4" if inherited else "unavailable",
            "growth_product_status_reason": "eligible_values_unchanged_from_v7_4" if inherited else obj["growth_ranking_eligibility_reason"],
            "parameter_map_path": old.loc[object_id, "parameter_map_path"] if inherited else "",
            "seed_redshift_map_path": old.loc[object_id, "seed_redshift_map_path"] if inherited else "",
            "growth_track_path": old.loc[object_id, "growth_track_path"] if inherited else "",
        })
    result = pd.DataFrame(rows)
    if len(result) != 219 or int(result["growth_product_status"].eq("complete_inherited_v7_4").sum()) != 196:
        raise ValueError("v7.5 gallery coverage must contain 219 objects and 196 complete galleries")
    return result


def main() -> None:
    _style()
    objects, point, uncertainty, sensitivity = _load()
    plot_catalogue_landscape(objects, point)
    plot_pressure(point)
    plot_uncertainty(uncertainty)
    plot_sensitivity(sensitivity)
    coverage = build_gallery_coverage(objects)
    OUTPUT_PATHS["gallery_coverage"].parent.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(OUTPUT_PATHS["gallery_coverage"], index=False)
    for path in OUTPUT_PATHS.values():
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
