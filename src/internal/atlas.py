"""Build numerical object maps and catalogue summary figures.

Numerical maps require a supported black-hole mass. Coverage tables retain
the reasons for unavailable maps without producing placeholder images.
"""

from __future__ import annotations

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
import numpy as np
import pandas as pd

from src.internal.fedd_mass_maps import (
    COMPATIBILITY_FEDD,
    MERGER_CASES,
    SEED_MODELS,
    SPIN_CASES,
    plot_fedd_mass_map,
)
from src.internal.shared_results import fedd_map_paths
from src.models import (
    predicted_log_mbh,
    required_seed_mass_for_growth,
    slim_disk_effective_efficiency,
)


VERSION = "v3"
CATALOGUE = ROOT / "data/processed/v3/v3_accreting_objects.csv"
UNCERTAINTY = ROOT / "results/v3/tables/v3_object_uncertainty_ranking.csv"
FIGURES = ROOT / "results/v3/figures"
TABLES = ROOT / "results/v3/tables"
PARAMETER_MAPS = ROOT / "results/v3/parameter_maps"

FIGURE_PATHS = {
    "growth_tracks": FIGURES / "v3_all_object_growth_tracks.png",
    "compatibility_summary": FIGURES / "v3_compatibility_summary.png",
    "uncertainty_summary": FIGURES / "v3_monte_carlo_summary.png",
}
TABLE_PATHS = {
    "coverage": TABLES / "v3_all_object_visual_coverage.csv",
    "compatibility": TABLES / "v3_all_object_compatibility.csv",
}

COLORS = {
    "broad_line_agn": "#176B87",
    "high_ionization_line_candidate": "#C45A23",
    "narrow_line_agn_candidate": "#6B5CA5",
    "xray_agn_candidate": "#777777",
    "photometric_agn_candidate": "#2A9D8F",
}
GROWTH_TRACK_COLORS = {
    **COLORS,
    "broad_line_agn": "#7B2CBF",
}
LABELS = {
    "broad_line_agn": "Broad-line AGN",
    "high_ionization_line_candidate": "High-ionization-line candidates",
    "narrow_line_agn_candidate": "Narrow-line candidates",
    "xray_agn_candidate": "X-ray candidates",
    "photometric_agn_candidate": "Photometric/SED candidates",
}
SEED_LABELS = {
    "light_seeds": "Light seeds\n($10^1$–$10^2\\,M_\\odot$)",
    "intermediate_seeds": "Intermediate seeds\n($10^3$–$10^4\\,M_\\odot$)",
    "heavy_seeds": "Heavy seeds\n($10^4$–$10^6\\,M_\\odot$)",
    "pbh_origin_hypothesis": "PBH-origin hypothesis\n(assumed $10^2$–$10^6\\,M_\\odot$)",
}

GROWTH_TRACK_REDSHIFT_LIMITS = (13.0, 3.0)


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


def materialize_fedd_mass_maps(objects: pd.DataFrame, *, rebuild: bool) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    shared_paths = fedd_map_paths(ROOT, VERSION, objects)
    for _, obj in objects.sort_values(["object_class", "redshift", "physical_object_id"]).iterrows():
        eligible = boolish(obj["growth_ranking_eligible_flag"])
        paths = {"fedd_mass_map": shared_paths.get(obj.physical_object_id)}
        for kind, output in paths.items():
            if eligible and (not output.exists() or (
                    rebuild and output.relative_to(ROOT).parts[1] == VERSION)):
                plot_fedd_mass_map(obj, output)
            rows.append({
                "release": VERSION,
                "physical_object_id": obj["physical_object_id"],
                "object_id": obj["object_id"],
                "object_class": obj["object_class"],
                "growth_ranking_eligible_flag": eligible,
                "product_kind": kind,
                "product_status": "numerical_growth_product" if eligible else "no_numerical_mass",
                "status_reason": "eligible_canonical_numeric_mbh" if eligible else obj["growth_ranking_eligibility_reason"],
                "path": output.relative_to(ROOT).as_posix() if eligible else "",
            })
    coverage = pd.DataFrame(rows)
    if len(coverage) != len(objects) or coverage["physical_object_id"].nunique() != len(objects):
        raise AssertionError("f_Edd/mass-map coverage must contain one record for every object")
    return coverage


def plot_all_object_growth_tracks(objects: pd.DataFrame, output: Path) -> None:
    eligible = objects[objects["growth_ranking_eligible_flag"].map(boolish)].copy()
    unavailable = objects[~objects["growth_ranking_eligible_flag"].map(boolish)].copy()
    redshift = np.linspace(
        GROWTH_TRACK_REDSHIFT_LIMITS[1], GROWTH_TRACK_REDSHIFT_LIMITS[0], 300,
    )
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
                   color=GROWTH_TRACK_COLORS[object_class], edgecolor="white", linewidth=0.35,
                   label=f"{LABELS[object_class]} ({len(group)})")
    ax.set(xlim=GROWTH_TRACK_REDSHIFT_LIMITS, ylim=(4.5, 10.8), xlabel="Observed redshift",
           ylabel=r"Canonical $\log_{10}(M_{\rm BH}/M_\odot)$",
           title=f"{VERSION}: all-object growth-track atlas")
    ax.grid(alpha=0.2)
    ax.legend(ncol=3, frameon=False, fontsize=9)

    status.set_xlim(*GROWTH_TRACK_REDSHIFT_LIMITS)
    status.set_ylim(-0.6, unavailable["object_class"].nunique() - 0.4)
    for y, (object_class, group) in enumerate(unavailable.groupby("object_class", sort=True)):
        status.scatter(group["redshift"], np.full(len(group), y), marker="|", s=260,
                       linewidths=2, color=GROWTH_TRACK_COLORS[object_class])
    classes = list(unavailable.groupby("object_class", sort=True).groups)
    status.set_yticks(range(len(classes)), [f"{LABELS[key]} (no numerical mass)" for key in classes])
    status.set_xlabel(f"Redshift of all {len(unavailable)} catalogue-only objects")
    status.grid(axis="x", alpha=0.2)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, facecolor="white")
    plt.close(fig)


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
            class_title = LABELS[object_class].removesuffix(" candidates")
            axes[row, col].set_title(f"{class_title} — {SEED_LABELS[seed_name]}")
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


def plot_uncertainty_summary(objects: pd.DataFrame, uncertainty: pd.DataFrame, output: Path) -> None:
    fig, (ax, status) = plt.subplots(1, 2, figsize=(15, 6.8),
                                     gridspec_kw={"width_ratios": [3.5, 1]}, constrained_layout=True)
    point_only = uncertainty["mbh_uncertainty_mode"].eq("point_estimate_no_reported_mbh_error")
    for object_class, group in uncertainty.loc[~point_only].groupby("object_class"):
        width = group["required_fedd_seed1e2_p84"] - group["required_fedd_seed1e2_p16"]
        ax.scatter(group["required_fedd_seed1e2_p50"], group["prob_required_fedd_seed1e2_gt_1"],
                   s=22 + 80 * np.clip(width, 0, 1), alpha=0.7, color=COLORS[object_class],
                   edgecolor="white", linewidth=0.35, label=f"{LABELS[object_class]} ({len(group)})")
    if point_only.any():
        points = uncertainty.loc[point_only]
        ax.scatter(points["required_fedd_seed1e2_p50"], np.full(len(points), -0.10),
                   marker="D", s=32, facecolors="none", edgecolors="#555555",
                   label=f"Point only ({len(points)}; probability unavailable)")
        ax.set_yticks([-0.10, 0, 0.2, 0.4, 0.6, 0.8, 1.0],
                      ["No error", "0", "0.2", "0.4", "0.6", "0.8", "1.0"])
        ax.axhline(-0.05, color="#999999", lw=0.6, ls=":")
    ax.axvline(1, color="#8B1A1A", ls="--", lw=1.1)
    ax.set(xlabel=r"Median required $f_{\rm Edd}$ for a $10^2\,M_\odot$ seed",
           ylabel=r"Monte Carlo $P(f_{\rm Edd,required}>1)$",
           title=f"{int((~point_only).sum())} reported-error summaries; {int(point_only.sum())} point estimates")
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
