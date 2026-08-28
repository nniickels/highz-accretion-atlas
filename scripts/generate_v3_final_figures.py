"""Create final-style figures from the frozen v3 JADES + Taylor products."""

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


RESULTS = PROJECT_ROOT / "results/past_releases/v3/tables"
OUTPUT = PROJECT_ROOT / "results/past_releases/v3/figures/main_text"
OBJECT_POINT = RESULTS / "v3_blagn_physical_object_point_ranking.csv"
OBJECT_UNCERTAINTY = RESULTS / "v3_blagn_physical_object_uncertainty_ranking.csv"
MEASUREMENTS = PROJECT_ROOT / "data/processed/v3/v3_blagn_measurements.csv"

SOURCE_STYLE = {
    "juodzbalis25_jades_blagn": ("JADES", "#204A87", "o"),
    "taylor24_ceers_rubies_blagn": ("CEERS/RUBIES", "#B24C28", "s"),
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
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    z = np.linspace(4, 10, 240)
    for log_seed, fedd, color, label in [(2, 1.0, "#4B8BBE", r"$10^2 M_\odot$, $f_{\rm Edd}=1$"), (4, 0.3, "#4D8B5F", r"$10^4 M_\odot$, $f_{\rm Edd}=0.3$"), (5, 0.3, "#B88724", r"$10^5 M_\odot$, $f_{\rm Edd}=0.3$")]:
        ax.plot(z, predicted_log_mbh(log_seed, fedd, 0.1, 30, z), color=color, lw=1.7, label=label)
    for key, (label, color, marker) in SOURCE_STYLE.items():
        d = point[point["source_key"].eq(key)]
        yerr = np.vstack([d["log_mbh_err_minus_reported"].fillna(0), d["log_mbh_err_plus_reported"].fillna(0)])
        ax.errorbar(d["redshift"], d["log_mbh_msun"], yerr=yerr, fmt=marker, ms=5, color=color, ecolor=color, alpha=0.78, capsize=1.7, label=f"{label} physical objects")
    ax.set(xlim=(10.1, 3.9), ylim=(5.7, 9.35), xlabel="Observed redshift, z", ylabel=r"$\log_{10}(M_{\rm BH}/M_\odot)$", title="v3 broad-line AGN mass–redshift coverage")
    top = ax.secondary_xaxis("top")
    ticks = [10, 9, 8, 7, 6, 5, 4]
    top.set_xticks(ticks, [f"{float(cosmic_time_gyr(x)):.2f}" for x in ticks])
    top.set_xlabel("Cosmic age (Gyr)")
    ax.legend(frameon=False, ncol=2, fontsize=8)
    fig.text(0.5, -0.01, r"Reference tracks assume $z_{seed}=30$, $\epsilon=0.1$, and merger boost 1; they are diagnostics, not fitted histories.", ha="center", fontsize=8)
    return save(fig, "v3_main_text_mbh_redshift_growth_overview.png")


def ranked_fedd(point: pd.DataFrame) -> Path:
    d = point.nsmallest(25, "rank_growth_pressure").sort_values("rank_growth_pressure", ascending=False)
    fig, ax = plt.subplots(figsize=(7.2, 7.0))
    colors = [SOURCE_STYLE[key][1] for key in d["source_key"]]
    ax.barh(np.arange(len(d)), d["req_fedd_seed1e2_z30_eps0p1_b1"], color=colors, alpha=0.82)
    ax.scatter(d["req_fedd_seed1e4_z30_eps0p1_b1"], np.arange(len(d)), color="#222222", marker="D", s=20, label=r"$10^4 M_\odot$ seed")
    ax.axvline(1.0, color="#8B1A1A", ls="--", lw=1, label=r"$f_{\rm Edd}=1$")
    ax.set_yticks(np.arange(len(d)), d["object_id"])
    ax.set_xlabel(r"Required lifetime-average $f_{\rm Edd}$")
    ax.set_title("v3 top physical-object growth-pressure ranking")
    ax.legend(frameon=False)
    fig.text(0.5, 0.01, "Each physical object appears once; CEERS-2782/RUBIES-EGS-50052 uses the documented preferred measurement.", ha="center", fontsize=8)
    return save(fig, "v3_main_text_ranked_required_fedd.png")


def uncertainty_forest(uncertainty: pd.DataFrame) -> Path:
    d = uncertainty.nsmallest(20, "rank_uncertainty_pressure").sort_values("rank_uncertainty_pressure", ascending=False)
    y = np.arange(len(d))
    med = d["req_fedd_seed1e2_p50_baseline"].to_numpy(float)
    err = np.vstack([med - d["req_fedd_seed1e2_p16_baseline"], d["req_fedd_seed1e2_p84_baseline"] - med])
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    ax.errorbar(med, y, xerr=err, fmt="o", color="#273C75", ecolor="#5577A8", capsize=2, label="reported statistical MBH uncertainty")
    ax.scatter(d["req_fedd_seed1e2_p50_mbh_minus_0p3dex"], y, marker="<", color="#4D8B5F", s=25, label="MBH -0.3 dex")
    ax.scatter(d["req_fedd_seed1e2_p50_mbh_plus_0p3dex"], y, marker=">", color="#B24C28", s=25, label="MBH +0.3 dex")
    ax.axvline(1, color="#8B1A1A", ls="--", lw=1)
    ax.set_yticks(y, d["object_id"])
    ax.set_xlabel(r"Required lifetime-average $f_{\rm Edd}$ for a $10^2 M_\odot$ seed")
    ax.set_title("v3 uncertainty-aware physical-object pressure")
    ax.legend(frameon=False, fontsize=8)
    fig.text(0.5, 0.01, "Statistical intervals and fixed calibration comparisons are shown separately and are not combined.", ha="center", fontsize=8)
    return save(fig, "v3_main_text_uncertainty_forest.png")


def source_coverage(point: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.6))
    for key, (label, color, _) in SOURCE_STYLE.items():
        d = point[point["source_key"].eq(key)]
        axes[0].hist(d["redshift"], bins=np.arange(4, 9.6, 0.5), histtype="step", lw=2, color=color, label=label)
        axes[1].hist(d["log_mbh_msun"], bins=np.arange(5.8, 9.3, 0.3), histtype="step", lw=2, color=color, label=label)
    axes[0].set(xlabel="Redshift", ylabel="Physical-object count", title="Redshift coverage")
    axes[1].set(xlabel=r"$\log_{10}(M_{\rm BH}/M_\odot)$", ylabel="Physical-object count", title="Mass coverage")
    axes[0].legend(frameon=False)
    fig.suptitle("v3 source-stratified coverage (descriptive, not demographic)")
    fig.text(0.5, -0.02, "Histograms retain source strata because the JADES and CEERS/RUBIES selection functions are not interchangeable.", ha="center", fontsize=8)
    return save(fig, "v3_main_text_source_stratified_coverage.png")


def main() -> None:
    configure()
    point = pd.read_csv(OBJECT_POINT)
    uncertainty = pd.read_csv(OBJECT_UNCERTAINTY)
    paths = [mass_redshift(point), ranked_fedd(point), uncertainty_forest(uncertainty), source_coverage(point)]
    for path in paths:
        print(f"Wrote: {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
