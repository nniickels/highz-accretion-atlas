"""Create the deliberate v5 paper-facing figures from canonical CSV products."""

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


RESULTS = PROJECT_ROOT / "results"
OUTPUT = RESULTS / "v5_main_text_figures"
SOURCE_STYLE = {
    "juodzbalis25_jades_blagn": ("JADES", "#204A87", "o"),
    "taylor24_ceers_rubies_blagn": ("CEERS/RUBIES", "#B24C28", "s"),
    "matthee23_eiger_fresco_blagn": ("EIGER/FRESCO", "#4D8B5F", "^"),
    "lin24_aspire_blagn": ("ASPIRE", "#8055A2", "D"),
    "harikane23_nirspec_blagn": ("Harikane NIRSpec", "#C58A18", "P"),
}


def configure() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "figure.dpi": 130, "savefig.dpi": 350, "font.family": "DejaVu Serif",
        "font.size": 9, "axes.grid": True, "grid.alpha": 0.22,
        "axes.spines.top": False, "axes.spines.right": False,
    })


def save(fig: plt.Figure, name: str) -> Path:
    path = OUTPUT / name
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def mass_redshift(point: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(7.6, 5.1))
    redshift = np.linspace(4, 10, 240)
    tracks = [
        (2, 1.0, "#4B8BBE", r"$10^2 M_\odot$, $f_{\rm Edd}=1$"),
        (4, 0.3, "#4D8B5F", r"$10^4 M_\odot$, $f_{\rm Edd}=0.3$"),
        (5, 0.3, "#B88724", r"$10^5 M_\odot$, $f_{\rm Edd}=0.3$"),
    ]
    for log_seed, fedd, color, label in tracks:
        ax.plot(
            redshift, predicted_log_mbh(log_seed, fedd, 0.1, 30, redshift),
            color=color, lw=1.5, label=label,
        )
    for key, (label, color, marker) in SOURCE_STYLE.items():
        data = point[point["source_key"].eq(key)]
        yerr = np.vstack([
            data["log_mbh_err_minus_reported"].fillna(0),
            data["log_mbh_err_plus_reported"].fillna(0),
        ])
        ax.errorbar(
            data["redshift"], data["log_mbh_msun"], yerr=yerr, fmt=marker,
            ms=4.6, color=color, ecolor=color, alpha=0.76, capsize=1.4,
            label=f"{label} ({len(data)})",
        )
    candidate = point[~point["primary_growth_ranking_flag"].astype(bool)]
    ax.scatter(
        candidate["redshift"], candidate["log_mbh_msun"], s=100,
        facecolors="none", edgecolors="#111111", linewidths=1.4,
        label="exploratory candidate (excluded from primary rank)", zorder=6,
    )
    ax.set(
        xlim=(10.1, 3.9), ylim=(5.7, 9.45), xlabel="Observed redshift, z",
        ylabel=r"$\log_{10}(M_{\rm BH}/M_\odot)$",
        title="v5 BLAGN physical-object mass–redshift coverage",
    )
    top = ax.secondary_xaxis("top")
    ticks = [10, 9, 8, 7, 6, 5, 4]
    top.set_xticks(ticks, [f"{float(cosmic_time_gyr(value)):.2f}" for value in ticks])
    top.set_xlabel("Cosmic age (Gyr)")
    ax.legend(frameon=False, ncol=2, fontsize=7.1)
    fig.text(
        0.5, -0.01,
        r"Tracks assume $z_{seed}=30$, $\epsilon=0.1$, merger boost 1; source samples have unlike selection functions.",
        ha="center", fontsize=8,
    )
    return save(fig, "v5_main_text_mbh_redshift_growth_overview.png")


def primary_vs_full(point: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(9.1, 5.0), gridspec_kw={"width_ratios": [1.35, 1]})
    leaders = point.nsmallest(15, "rank_growth_pressure").sort_values(
        "rank_growth_pressure", ascending=False,
    )
    colors = [SOURCE_STYLE[key][1] for key in leaders["source_key"]]
    bars = axes[0].barh(
        np.arange(len(leaders)), leaders["req_fedd_seed1e2_z30_eps0p1_b1"],
        color=colors, alpha=0.83,
    )
    for bar, included in zip(bars, leaders["primary_growth_ranking_flag"], strict=True):
        if not bool(included):
            bar.set_edgecolor("#111111")
            bar.set_linewidth(1.6)
            bar.set_hatch("//")
    labels = [
        f"{row.object_id}  [full {int(row.rank_growth_pressure)}"
        + (f", primary {int(row.rank_primary_growth_pressure)}]" if pd.notna(row.rank_primary_growth_pressure) else ", no primary rank]")
        for row in leaders.itertuples()
    ]
    axes[0].set_yticks(np.arange(len(leaders)), labels, fontsize=7.4)
    axes[0].axvline(1.0, color="#8B1A1A", ls="--", lw=1)
    axes[0].set(
        xlabel=r"Required lifetime-average $f_{\rm Edd}$ ($100\,M_\odot$ seed)",
        title="Highest full diagnostic ranks",
    )

    primary = point[point["primary_growth_ranking_flag"].astype(bool)]
    axes[1].scatter(
        primary["rank_growth_pressure"], primary["rank_primary_growth_pressure"],
        s=24, color="#315D86", alpha=0.65,
    )
    limit = len(point) + 1
    axes[1].plot([1, limit], [1, limit], color="#777777", ls=":", lw=1)
    candidate = point[~point["primary_growth_ranking_flag"].astype(bool)].iloc[0]
    axes[1].scatter(
        candidate["rank_growth_pressure"], limit, marker="x", s=70,
        color="#B24C28", linewidths=2,
    )
    axes[1].annotate(
        f"{candidate['object_id']}\nexcluded from primary",
        (candidate["rank_growth_pressure"], limit), xytext=(12, -7),
        textcoords="offset points", fontsize=7.5,
    )
    axes[1].set(
        xlim=(0, limit + 4), ylim=(limit + 4, 0),
        xlabel="Full exploratory rank", ylabel="Primary evidence-supported rank",
        title="Population definition changes rank",
    )
    fig.suptitle("v5 physical-object growth-pressure ranking: full versus primary", y=1.01)
    fig.text(
        0.5, -0.025,
        "Hatching marks the retained alternative-interpretation candidate; exclusion is evidential, not a numerical penalty.",
        ha="center", fontsize=8,
    )
    return save(fig, "v5_main_text_primary_vs_full_ranking.png")


def accretion_history(history: pd.DataFrame) -> Path:
    base = history[history["burst_fedd"].eq(1.0)].copy()
    base = base[base["primary_growth_ranking_flag"].astype(bool)]
    base = base.sort_values("required_lifetime_average_fedd_point", ascending=False).head(15)
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 5.3))
    y = np.arange(len(base))
    median = base["required_duty_cycle_p50"].to_numpy(float)
    errors = np.vstack([
        median - base["required_duty_cycle_p16"].to_numpy(float),
        base["required_duty_cycle_p84"].to_numpy(float) - median,
    ])
    axes[0].errorbar(
        median, y, xerr=errors, fmt="o", color="#204A87", ecolor="#6282A6",
        capsize=2, label=r"burst $f_{\rm Edd}=1$",
    )
    axes[0].scatter(median / 2.0, y, marker="s", s=22, color="#4D8B5F", label="burst 2")
    axes[0].scatter(median / 3.0, y, marker="^", s=24, color="#8055A2", label="burst 3")
    axes[0].axvline(1.0, color="#8B1A1A", ls="--", lw=1)
    axes[0].set_yticks(y, base["object_id"])
    axes[0].invert_yaxis()
    axes[0].set(
        xlabel="Required active duty fraction, D",
        title="Top primary objects under fixed bursts",
    )
    axes[0].legend(frameon=False, fontsize=8)

    current = history[history["burst_fedd"].eq(1.0)].copy()
    eligible = current[current["current_fedd_comparison_eligible_flag"].astype(bool)]
    for key, (label, color, marker) in SOURCE_STYLE.items():
        data = eligible[eligible["source_key"].eq(key)]
        if len(data):
            axes[1].scatter(
                data["required_lifetime_average_fedd_point"], data["reported_current_fedd"],
                label=label, color=color, marker=marker, s=35, alpha=0.78,
            )
    inconsistent = current[current["edd_ratio_consistency_flag"].eq("inconsistent")]
    axes[1].scatter(
        inconsistent["required_lifetime_average_fedd_point"],
        inconsistent["reported_current_fedd"], marker="x", s=70,
        color="#B83232", linewidths=2, label="source-table inconsistency (excluded)",
    )
    for row in inconsistent.itertuples():
        axes[1].annotate(
            row.object_id, (row.required_lifetime_average_fedd_point, row.reported_current_fedd),
            xytext=(6, -10), textcoords="offset points", fontsize=7.3,
        )
    low = 0.025
    high = 2.2
    axes[1].plot([low, high], [low, high], color="#777777", ls=":", lw=1)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set(
        xlim=(low, high), ylim=(low, high),
        xlabel=r"Required lifetime-average $f_{\rm Edd}$",
        ylabel=r"Published current $f_{\rm Edd}$",
        title="Current measurements are not histories",
    )
    axes[1].legend(frameon=False, fontsize=6.9)
    fig.suptitle("v5 effective two-state accretion-history diagnostics", y=1.01)
    fig.text(
        0.5, -0.025,
        r"$z_{seed}=30$, $100\,M_\odot$, $\epsilon=0.1$, $f_{quiet}=0$; duty ordering is a rescaling of required mean growth.",
        ha="center", fontsize=8,
    )
    return save(fig, "v5_main_text_accretion_history_diagnostics.png")


def measurement_sensitivity(sensitivity: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.9))
    labels = sensitivity["physical_object_id"].str.replace("HZA-", "", regex=False)
    x = np.arange(len(sensitivity))
    for ax, default, alternate, ylabel, title in [
        (axes[0], "default_log_mbh", "alternate_log_mbh", r"$\log_{10}(M_{\rm BH}/M_\odot)$", "Published mass choice"),
        (axes[1], "default_rank_growth_pressure", "alternate_rank_growth_pressure", "Growth-pressure rank", "One-object substitution"),
    ]:
        ax.scatter(x - 0.08, sensitivity[default], color="#204A87", label="release default", s=42)
        ax.scatter(x + 0.08, sensitivity[alternate], color="#B24C28", marker="s", label="alternate", s=38)
        for index in range(len(sensitivity)):
            ax.plot(
                [index - 0.08, index + 0.08],
                [sensitivity.iloc[index][default], sensitivity.iloc[index][alternate]],
                color="#777777", lw=1,
            )
        ax.set_xticks(x, labels, rotation=16, fontsize=7.1)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
    axes[1].invert_yaxis()
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle("v5 duplicate-measurement sensitivity")
    fig.text(
        0.5, -0.035,
        "Each alternate is substituted alone; all literature measurements and documented release defaults remain preserved.",
        ha="center", fontsize=8,
    )
    return save(fig, "v5_appendix_measurement_choice_sensitivity.png")


def main() -> None:
    configure()
    point = pd.read_csv(RESULTS / "v5_blagn_physical_object_point_ranking.csv")
    history = pd.read_csv(RESULTS / "v5_blagn_physical_object_accretion_history.csv")
    sensitivity = pd.read_csv(RESULTS / "v5_blagn_alternate_measurement_sensitivity.csv")
    paths = [
        mass_redshift(point), primary_vs_full(point), accretion_history(history),
        measurement_sensitivity(sensitivity),
    ]
    for path in paths:
        print(f"Wrote: {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
