"""Create final-style figures from the corrected v4 BLAGN products."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".codex_tmp" / "matplotlib"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.models import cosmic_time_gyr, predicted_log_mbh


RESULTS = PROJECT_ROOT / "results/releases/v4/tables"
OUTPUT = PROJECT_ROOT / "results/releases/v4/figures/main_text"
SOURCE_STYLE = {
    "juodzbalis25_jades_blagn": ("JADES", "#204A87", "o"),
    "taylor24_ceers_rubies_blagn": ("CEERS/RUBIES", "#B24C28", "s"),
    "matthee23_eiger_fresco_blagn": ("EIGER/FRESCO", "#4D8B5F", "^"),
    "lin24_aspire_blagn": ("ASPIRE", "#8055A2", "D"),
}


def configure() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 350, "font.family": "DejaVu Serif", "font.size": 9, "axes.grid": True, "grid.alpha": 0.25, "axes.spines.top": False, "axes.spines.right": False})


def save(fig: plt.Figure, name: str) -> Path:
    path = OUTPUT / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def mass_redshift(point: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    z = np.linspace(4, 10, 240)
    for log_seed, fedd, color, label in [(2, 1.0, "#4B8BBE", r"$10^2 M_\odot$, $f_{\rm Edd}=1$"), (4, 0.3, "#4D8B5F", r"$10^4 M_\odot$, $f_{\rm Edd}=0.3$"), (5, 0.3, "#B88724", r"$10^5 M_\odot$, $f_{\rm Edd}=0.3$")]:
        ax.plot(z, predicted_log_mbh(log_seed, fedd, 0.1, 30, z), color=color, lw=1.6, label=label)
    for key, (label, color, marker) in SOURCE_STYLE.items():
        data = point[point["source_key"].eq(key)]
        yerr = np.vstack([data["log_mbh_err_minus_reported"].fillna(0), data["log_mbh_err_plus_reported"].fillna(0)])
        ax.errorbar(data["redshift"], data["log_mbh_msun"], yerr=yerr, fmt=marker, ms=4.8, color=color, ecolor=color, alpha=0.78, capsize=1.5, label=f"{label} ({len(data)})")
    ax.set(xlim=(10.1, 3.9), ylim=(5.7, 9.45), xlabel="Observed redshift, z", ylabel=r"$\log_{10}(M_{\rm BH}/M_\odot)$", title="v4 broad-line AGN mass–redshift coverage")
    top = ax.secondary_xaxis("top")
    ticks = [10, 9, 8, 7, 6, 5, 4]
    top.set_xticks(ticks, [f"{float(cosmic_time_gyr(value)):.2f}" for value in ticks])
    top.set_xlabel("Cosmic age (Gyr)")
    ax.legend(frameon=False, ncol=2, fontsize=7.5)
    fig.text(0.5, -0.01, r"Tracks assume $z_{seed}=30$, $\epsilon=0.1$, merger boost 1; they are diagnostics, not fitted histories.", ha="center", fontsize=8)
    return save(fig, "v4_main_text_mbh_redshift_growth_overview.png")


def ranked_fedd(point: pd.DataFrame) -> Path:
    data = point.nsmallest(25, "rank_growth_pressure").sort_values("rank_growth_pressure", ascending=False)
    fig, ax = plt.subplots(figsize=(7.5, 7.1))
    colors = [SOURCE_STYLE[key][1] for key in data["source_key"]]
    bars = ax.barh(np.arange(len(data)), data["req_fedd_seed1e2_z30_eps0p1_b1"], color=colors, alpha=0.82)
    for bar, tier in zip(bars, data["mass_measurement_reliability_tier"], strict=True):
        if tier != "high":
            bar.set_edgecolor("#111111"); bar.set_linewidth(1.6); bar.set_hatch("//")
    ax.scatter(data["req_fedd_seed1e4_z30_eps0p1_b1"], np.arange(len(data)), color="#222222", marker="D", s=18, label=r"$10^4 M_\odot$ seed")
    ax.axvline(1.0, color="#8B1A1A", ls="--", lw=1, label=r"$f_{\rm Edd}=1$")
    ax.set_yticks(np.arange(len(data)), data["object_id"])
    ax.set(xlabel=r"Required lifetime-average $f_{\rm Edd}$", title="v4 top physical-object growth-pressure ranking")
    ax.legend(frameon=False)
    fig.text(0.5, 0.005, "Hatched bars flag mass/line-model caveats; robust detection confidence is recorded separately.", ha="center", fontsize=8)
    return save(fig, "v4_main_text_ranked_required_fedd.png")


def uncertainty_forest(uncertainty: pd.DataFrame) -> Path:
    data = uncertainty.nsmallest(20, "rank_uncertainty_pressure").sort_values("rank_uncertainty_pressure", ascending=False)
    y = np.arange(len(data)); median = data["req_fedd_seed1e2_p50_baseline"].to_numpy(float)
    error = np.vstack([median - data["req_fedd_seed1e2_p16_baseline"], data["req_fedd_seed1e2_p84_baseline"] - median])
    fig, ax = plt.subplots(figsize=(7.5, 6.3))
    ax.errorbar(median, y, xerr=error, fmt="o", color="#273C75", ecolor="#5577A8", capsize=2, label="reported statistical MBH uncertainty")
    ax.scatter(data["req_fedd_seed1e2_p50_mbh_minus_0p3dex"], y, marker="<", color="#4D8B5F", s=24, label="MBH -0.3 dex")
    ax.scatter(data["req_fedd_seed1e2_p50_mbh_plus_0p3dex"], y, marker=">", color="#B24C28", s=24, label="MBH +0.3 dex")
    ax.axvline(1, color="#8B1A1A", ls="--", lw=1)
    ax.set_yticks(y, data["object_id"])
    ax.set(xlabel=r"Required lifetime-average $f_{\rm Edd}$ for a $10^2 M_\odot$ seed", title="v4 uncertainty-aware physical-object pressure")
    ax.legend(frameon=False, fontsize=8)
    fig.text(0.5, 0.005, "Statistical intervals and fixed calibration comparisons are separate, not combined.", ha="center", fontsize=8)
    return save(fig, "v4_main_text_uncertainty_forest.png")


def source_coverage(point: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.7))
    for key, (label, color, _) in SOURCE_STYLE.items():
        data = point[point["source_key"].eq(key)]
        axes[0].hist(data["redshift"], bins=np.arange(4, 9.6, 0.5), histtype="step", lw=2, color=color, label=label)
        axes[1].hist(data["log_mbh_msun"], bins=np.arange(5.8, 9.5, 0.3), histtype="step", lw=2, color=color, label=label)
    axes[0].set(xlabel="Redshift", ylabel="Physical-object count", title="Redshift coverage")
    axes[1].set(xlabel=r"$\log_{10}(M_{\rm BH}/M_\odot)$", ylabel="Physical-object count", title="Mass coverage")
    axes[0].legend(frameon=False, fontsize=7.5)
    fig.suptitle("v4 source-stratified coverage (descriptive, not demographic)")
    fig.text(0.5, -0.02, "Source strata are retained because the four selection functions are not interchangeable.", ha="center", fontsize=8)
    return save(fig, "v4_main_text_source_stratified_coverage.png")


def measurement_sensitivity(sensitivity: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8))
    labels = sensitivity["physical_object_id"].str.replace("HZA-", "", regex=False)
    x = np.arange(len(sensitivity))
    axes[0].scatter(x - 0.08, sensitivity["default_log_mbh"], color="#204A87", label="release default", s=45)
    axes[0].scatter(x + 0.08, sensitivity["alternate_log_mbh"], color="#B24C28", marker="s", label="alternate", s=40)
    for index in range(len(sensitivity)):
        axes[0].plot([index - 0.08, index + 0.08], [sensitivity.iloc[index]["default_log_mbh"], sensitivity.iloc[index]["alternate_log_mbh"]], color="#777777", lw=1)
    axes[0].set_xticks(x, labels, rotation=12); axes[0].set_ylabel(r"$\log_{10}(M_{\rm BH}/M_\odot)$"); axes[0].set_title("Published mass choice")
    axes[1].scatter(x - 0.08, sensitivity["default_rank_growth_pressure"], color="#204A87", s=45)
    axes[1].scatter(x + 0.08, sensitivity["alternate_rank_growth_pressure"], color="#B24C28", marker="s", s=40)
    for index in range(len(sensitivity)):
        axes[1].plot([index - 0.08, index + 0.08], [sensitivity.iloc[index]["default_rank_growth_pressure"], sensitivity.iloc[index]["alternate_rank_growth_pressure"]], color="#777777", lw=1)
    axes[1].invert_yaxis(); axes[1].set_xticks(x, labels, rotation=12); axes[1].set_ylabel("Growth-pressure rank (1 = highest)"); axes[1].set_title("One-object substitution")
    axes[0].legend(frameon=False)
    fig.suptitle("v4 duplicate-measurement sensitivity")
    fig.text(0.5, -0.02, "Alternate rows are sensitivity tests only; release-default measurements remain unchanged.", ha="center", fontsize=8)
    return save(fig, "v4_main_text_measurement_choice_sensitivity.png")


def main() -> None:
    configure()
    point = pd.read_csv(RESULTS / "v4_blagn_physical_object_point_ranking.csv")
    uncertainty = pd.read_csv(RESULTS / "v4_blagn_physical_object_uncertainty_ranking.csv")
    sensitivity = pd.read_csv(RESULTS / "v4_blagn_alternate_measurement_sensitivity.csv")
    paths = [mass_redshift(point), ranked_fedd(point), uncertainty_forest(uncertainty), source_coverage(point), measurement_sensitivity(sensitivity)]
    for path in paths:
        print(f"Wrote: {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
