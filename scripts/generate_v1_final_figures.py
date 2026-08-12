"""Create final-style v1 figure prototypes for the observational atlas.

The figures are main-text candidates driven by the v1 ranking and uncertainty
products. They are saved into a separate directory and do not delete or replace
exploratory outputs.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MPLCONFIGDIR = REPO_ROOT / ".codex_tmp" / "matplotlib"
MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import matplotlib

matplotlib.use("Agg")

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

sys.path.insert(0, str(REPO_ROOT))

from src.models import cosmic_time_gyr, predicted_log_mbh

RESULTS_DIR = REPO_ROOT / "results"
FIGURE_DIR = RESULTS_DIR / "v1_main_text_figures"
RANKING_PATH = RESULTS_DIR / "v1_object_ranking_table.csv"
UNCERTAINTY_RANKING_PATH = RESULTS_DIR / "v1_uncertainty_aware_ranking_table.csv"
UNCERTAINTY_FEDD_PATH = RESULTS_DIR / "v1_uncertainty_required_fedd_summary.csv"
UNCERTAINTY_MSEED_PATH = RESULTS_DIR / "v1_uncertainty_required_mseed_summary.csv"

SPOTLIGHT_MAPS = {
    "GN-38509": RESULTS_DIR / "v1_seed_redshift_maps" / "v1_seed_redshift_map_gn38509-juodzbalis25.png",
    "GS-20057765": RESULTS_DIR
    / "v1_seed_redshift_maps"
    / "v1_seed_redshift_map_gs20057765-juodzbalis25.png",
}

HIGH_LEVERAGE_OBJECTS = {"GN-38509", "GS-20057765", "GS-20030333", "GS-164055", "GN-4685", "GN-954"}

FIGURE_PATHS = {
    "growth_overview": FIGURE_DIR / "v1_main_text_mbh_redshift_growth_overview.png",
    "ranked_fedd": FIGURE_DIR / "v1_main_text_ranked_required_fedd.png",
    "ranked_seed": FIGURE_DIR / "v1_main_text_ranked_required_seed_mass.png",
    "pressure_confidence": FIGURE_DIR / "v1_main_text_pressure_vs_confidence.png",
    "uncertainty_forest": FIGURE_DIR / "v1_main_text_uncertainty_forest.png",
    "spotlight_maps": FIGURE_DIR / "v1_main_text_spotlight_seed_redshift_maps.png",
}

COLOR_ROBUST = "#283845"
COLOR_TENTATIVE = "#D56A2C"
COLOR_HIGH = "#B83232"
COLOR_MEDIUM = "#D89C2B"
COLOR_LOW = "#4A7C59"
COLOR_MUTED = "#777777"


def configure_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 130,
            "savefig.dpi": 350,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.16,
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 9.5,
            "axes.labelsize": 10.5,
            "axes.titlesize": 12,
            "axes.titleweight": "regular",
            "legend.fontsize": 8.4,
            "xtick.labelsize": 8.6,
            "ytick.labelsize": 8.4,
            "axes.linewidth": 0.8,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "grid.color": "#D9D9D9",
            "grid.linewidth": 0.55,
            "grid.alpha": 0.7,
        }
    )


def read_ranking() -> pd.DataFrame:
    if not RANKING_PATH.exists():
        raise FileNotFoundError(
            f"Ranking table not found: {RANKING_PATH}. Run scripts/generate_v1_rankings.py first."
        )
    ranking = pd.read_csv(RANKING_PATH)
    required = {
        "object_id",
        "redshift",
        "quality_flag",
        "log_mbh_msun",
        "log_mbh_err_plus",
        "log_mbh_err_minus",
        "rank_physical_pressure",
        "req_fedd_seed1e2_z30_eps0p1_b1",
        "req_fedd_seed1e4_z30_eps0p1_b1",
        "req_fedd_seed1e5_z30_eps0p1_b1",
        "req_log_mseed_fedd0p3_z30_eps0p1_b1",
        "req_log_mseed_fedd1_z30_eps0p1_b1",
        "physical_growth_pressure_tier",
        "growth_pressure_robustness_label",
        "measurement_confidence_tier",
        "measurement_confidence_score_0_100",
        "physical_pressure_score_0_100",
        "mbh_mstar_tension_label",
        "missing_mstar_flag",
        "followup_priority_category",
    }
    missing = required - set(ranking.columns)
    if missing:
        raise ValueError(f"Ranking table is missing required columns: {sorted(missing)}")
    return ranking


def read_uncertainty_products() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Read and validate the uncertainty products used by the forest plot."""
    paths = [UNCERTAINTY_RANKING_PATH, UNCERTAINTY_FEDD_PATH, UNCERTAINTY_MSEED_PATH]
    missing_paths = [str(path) for path in paths if not path.exists()]
    if missing_paths:
        raise FileNotFoundError(
            "Uncertainty products are missing: "
            f"{missing_paths}. Run scripts/generate_v1_uncertainty_rankings.py first."
        )

    uncertainty_ranking = pd.read_csv(UNCERTAINTY_RANKING_PATH)
    fedd_summary = pd.read_csv(UNCERTAINTY_FEDD_PATH)
    mseed_summary = pd.read_csv(UNCERTAINTY_MSEED_PATH)

    ranking_required = {
        "measurement_id",
        "object_id",
        "quality_flag",
        "rank_uncertainty_pressure",
        "req_fedd_seed1e2_z30_eps0p1_b1",
        "req_log_mseed_fedd0p3_z30_eps0p1_b1",
    }
    fedd_required = {
        "measurement_id",
        "scenario",
        "seed_mass_short",
        "required_fedd_p5",
        "required_fedd_p16",
        "required_fedd_p50",
        "required_fedd_p84",
        "required_fedd_p95",
        "prob_required_fedd_gt_1",
    }
    mseed_required = {
        "measurement_id",
        "scenario",
        "growth_history",
        "required_log_mseed_p5",
        "required_log_mseed_p16",
        "required_log_mseed_p50",
        "required_log_mseed_p84",
        "required_log_mseed_p95",
        "prob_required_mseed_gt_1e6",
    }
    for path, table, required in [
        (UNCERTAINTY_RANKING_PATH, uncertainty_ranking, ranking_required),
        (UNCERTAINTY_FEDD_PATH, fedd_summary, fedd_required),
        (UNCERTAINTY_MSEED_PATH, mseed_summary, mseed_required),
    ]:
        missing = required - set(table.columns)
        if missing:
            raise ValueError(f"{path.name} is missing required columns: {sorted(missing)}")

    return uncertainty_ranking, fedd_summary, mseed_summary


def add_caption(fig: plt.Figure, text: str, y: float = 0.02) -> None:
    fig.text(
        0.5,
        y,
        text,
        ha="center",
        va="bottom",
        fontsize=8.2,
        color="#202020",
        linespacing=1.15,
    )


def save_figure(fig: plt.Figure, path: Path) -> Path:
    """Save a figure, falling back to a polished-copy filename if a PNG is open."""
    try:
        fig.savefig(path, facecolor="white")
        return path
    except PermissionError:
        fallback = path.with_name(f"{path.stem}_polished{path.suffix}")
        counter = 2
        while fallback.exists():
            fallback = path.with_name(f"{path.stem}_polished_{counter}{path.suffix}")
            counter += 1
        fig.savefig(fallback, facecolor="white")
        return fallback


def quality_style(quality: str) -> tuple[str, str]:
    if str(quality).lower() == "robust":
        return COLOR_ROBUST, "o"
    return COLOR_TENTATIVE, "s"


def pressure_color(tier: str) -> str:
    return {"high": COLOR_HIGH, "medium": COLOR_MEDIUM, "low": COLOR_LOW}.get(str(tier), COLOR_MUTED)


def y_labels(objects: pd.Series) -> list[str]:
    return [str(obj) for obj in objects]


def plot_growth_overview(ranking: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    fig.subplots_adjust(left=0.12, right=0.96, bottom=0.33, top=0.86)

    z_grid = np.linspace(4.0, 10.0, 220)
    track_specs = [
        (2.0, 1.0, "#2878B5", "-", r"$10^2 M_\odot$, $f_{\rm Edd}=1$"),
        (4.0, 0.3, "#5A9E6F", "--", r"$10^4 M_\odot$, $f_{\rm Edd}=0.3$"),
        (4.0, 1.0, "#2E8B57", "-", r"$10^4 M_\odot$, $f_{\rm Edd}=1$"),
        (5.0, 0.3, "#B98218", "--", r"$10^5 M_\odot$, $f_{\rm Edd}=0.3$"),
    ]
    for log_seed, fedd, color, linestyle, label in track_specs:
        ax.plot(
            z_grid,
            predicted_log_mbh(log_seed, fedd, 0.1, 30.0, z_grid),
            color=color,
            lw=1.9,
            ls=linestyle,
            label=label,
        )

    for quality in ["robust", "tentative"]:
        subset = ranking[ranking["quality_flag"].str.lower() == quality]
        color, marker = quality_style(quality)
        yerr = np.vstack(
            [
                subset["log_mbh_err_minus"].fillna(0.0).to_numpy(float),
                subset["log_mbh_err_plus"].fillna(0.0).to_numpy(float),
            ]
        )
        ax.errorbar(
            subset["redshift"],
            subset["log_mbh_msun"],
            yerr=yerr,
            fmt=marker,
            ms=5.8,
            mfc="white" if quality == "tentative" else color,
            mec=color,
            ecolor=color,
            elinewidth=0.85,
            capsize=2.2,
            alpha=0.9,
            label=f"{quality.title()} v1 objects",
        )

    for _, row in ranking[ranking["object_id"].isin(["GN-38509", "GS-20057765"])].iterrows():
        ax.annotate(
            row["object_id"],
            xy=(row["redshift"], row["log_mbh_msun"]),
            xytext=(5, 7),
            textcoords="offset points",
            fontsize=8.3,
            color="#111111",
        )

    ax.set_xlim(10.1, 3.9)
    ax.set_ylim(5.65, 9.25)
    ax.set_xlabel("Observed redshift, z")
    ax.set_ylabel(r"$\log_{10}(M_{\rm BH}/M_\odot)$")
    ax.set_title("v1 mass-redshift overview with selected reference growth tracks")
    ax.grid(True, zorder=0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), frameon=False, ncol=3)

    top = ax.secondary_xaxis("top")
    top.set_xticks([10, 9, 8, 7, 6, 5, 4])
    top.set_xticklabels([f"{float(cosmic_time_gyr(z)):.2f}" for z in [10, 9, 8, 7, 6, 5, 4]])
    top.set_xlabel("Cosmic age at observed redshift (Gyr)")

    caption = (
        "Main-text prototype: points are source-reported v1 black-hole masses; curves are reference diagnostics, not fitted histories.\n"
        r"All curves assume $z_{\rm seed}=30$, $\epsilon=0.1$, and no merger boost; rankings are used for object triage."
    )
    add_caption(fig, caption)
    path = save_figure(fig, FIGURE_PATHS["growth_overview"])
    plt.close(fig)
    return path


def plot_ranked_required_fedd(ranking: pd.DataFrame) -> Path:
    plot_df = ranking.sort_values("rank_physical_pressure", ascending=True).reset_index(drop=True)
    y = np.arange(len(plot_df))

    fig, ax = plt.subplots(figsize=(7.0, 6.2))
    fig.subplots_adjust(left=0.28, right=0.97, bottom=0.19, top=0.9)
    colors = [pressure_color(t) for t in plot_df["physical_growth_pressure_tier"]]
    ax.barh(y, plot_df["req_fedd_seed1e2_z30_eps0p1_b1"], height=0.58, color=colors, alpha=0.82)
    ax.scatter(plot_df["req_fedd_seed1e4_z30_eps0p1_b1"], y, marker="D", s=28, color="#1F6F8B", zorder=3)
    ax.scatter(plot_df["req_fedd_seed1e5_z30_eps0p1_b1"], y, marker="o", s=28, color="#4F5D75", zorder=3)
    for quality in ["robust", "tentative"]:
        subset = plot_df[plot_df["quality_flag"].str.lower() == quality]
        edge, marker = quality_style(quality)
        ax.scatter(
            np.full(len(subset), -0.035),
            subset.index.to_numpy(),
            marker=marker,
            s=32,
            facecolors="white",
            edgecolors=edge,
            linewidths=1.1,
            clip_on=False,
            zorder=4,
        )

    for x in [0.3, 1.0, 2.0]:
        ax.axvline(x, color="#333333", lw=0.8, ls=":" if x != 1.0 else "--", alpha=0.82)

    ax.set_yticks(y)
    ax.set_yticklabels(y_labels(plot_df["object_id"]))
    ax.invert_yaxis()
    ax.set_xlabel(r"Required lifetime-average $f_{\rm Edd}$")
    ax.set_title(r"Ranked growth pressure from fixed seed masses")
    ax.set_xlim(-0.06, max(1.55, float(plot_df["req_fedd_seed1e2_z30_eps0p1_b1"].max()) + 0.12))
    ax.grid(True, axis="x")

    handles = [
        Line2D([0], [0], color=COLOR_HIGH, lw=6, label="High pressure bar"),
        Line2D([0], [0], color=COLOR_MEDIUM, lw=6, label="Medium pressure bar"),
        Line2D([0], [0], color=COLOR_LOW, lw=6, label="Low pressure bar"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor="#1F6F8B", markeredgecolor="#1F6F8B", label=r"$10^4 M_\odot$ seed"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#4F5D75", markeredgecolor="#4F5D75", label=r"$10^5 M_\odot$ seed"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=COLOR_ROBUST, label="Robust"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="white", markeredgecolor=COLOR_TENTATIVE, label="Tentative"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=False, ncol=2, columnspacing=1.0)

    caption = (
        r"Bars show required average $f_{\rm Edd}$ for a $100 M_\odot$ seed; markers show $10^4$ and $10^5 M_\odot$ seeds."
        "\n"
        r"Left margin symbols mark robust circles and tentative squares; high-pressure cases are under the stated baseline assumptions."
    )
    add_caption(fig, caption, y=0.02)
    path = save_figure(fig, FIGURE_PATHS["ranked_fedd"])
    plt.close(fig)
    return path


def plot_ranked_required_seed(ranking: pd.DataFrame) -> Path:
    plot_df = ranking.sort_values("rank_physical_pressure", ascending=True).reset_index(drop=True)
    y = np.arange(len(plot_df))

    fig, ax = plt.subplots(figsize=(7.0, 6.2))
    fig.subplots_adjust(left=0.28, right=0.97, bottom=0.29, top=0.9)
    colors = [pressure_color(t) for t in plot_df["physical_growth_pressure_tier"]]
    ax.barh(y, plot_df["req_log_mseed_fedd0p3_z30_eps0p1_b1"], height=0.58, color=colors, alpha=0.82)
    ax.scatter(plot_df["req_log_mseed_fedd1_z30_eps0p1_b1"], y, marker="o", s=30, color="#263238", zorder=3)
    for quality in ["robust", "tentative"]:
        subset = plot_df[plot_df["quality_flag"].str.lower() == quality]
        edge, marker = quality_style(quality)
        ax.scatter(
            np.full(len(subset), -0.82),
            subset.index.to_numpy(),
            marker=marker,
            s=32,
            facecolors="white",
            edgecolors=edge,
            linewidths=1.1,
            clip_on=False,
            zorder=4,
        )

    for x, label in [
        (2.0, "nominal light-seed scale"),
        (4.0, "nominal heavy-scale guide"),
        (6.0, "upper guide"),
    ]:
        ax.axvline(x, color="#333333", lw=0.8, ls=":", alpha=0.78)

    ax.set_yticks(y)
    ax.set_yticklabels(y_labels(plot_df["object_id"]))
    ax.invert_yaxis()
    ax.set_xlabel(r"Required seed mass, $\log_{10}(M_{\rm seed}/M_\odot)$")
    ax.set_title(r"Ranked seed-mass requirements for fixed growth histories")
    ax.set_xlim(-1.0, 7.25)
    ax.grid(True, axis="x")
    ax.legend(
        handles=[
            Line2D([0], [0], color=COLOR_HIGH, lw=6, label="High pressure bar"),
            Line2D([0], [0], color=COLOR_MEDIUM, lw=6, label="Medium pressure bar"),
            Line2D([0], [0], color=COLOR_LOW, lw=6, label="Low pressure bar"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor="#263238", markeredgecolor="#263238", label=r"$f_{\rm Edd}=1$ marker"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=COLOR_ROBUST, label="Robust"),
            Line2D([0], [0], marker="s", color="none", markerfacecolor="white", markeredgecolor=COLOR_TENTATIVE, label="Tentative"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.075),
        frameon=False,
        ncol=3,
        columnspacing=1.0,
    )

    caption = (
        r"Bars show seed mass required for gentle average growth at $f_{\rm Edd}=0.3$; markers show $f_{\rm Edd}=1$."
        "\n"
        r"Left margin symbols mark robust circles and tentative squares; values above $\log M_{\rm seed}=6$ mark triage leverage under this fixed-growth assumption, not proof of any channel."
    )
    add_caption(fig, caption, y=0.02)
    path = save_figure(fig, FIGURE_PATHS["ranked_seed"])
    plt.close(fig)
    return path


def plot_pressure_vs_confidence(ranking: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(6.6, 4.9))
    fig.subplots_adjust(left=0.12, right=0.98, bottom=0.24, top=0.88)

    for quality in ["robust", "tentative"]:
        subset = ranking[ranking["quality_flag"].str.lower() == quality]
        edge, marker = quality_style(quality)
        sizes = np.where(subset["mbh_mstar_tension_label"].eq("extreme"), 95, 55)
        ax.scatter(
            subset["physical_pressure_score_0_100"],
            subset["measurement_confidence_score_0_100"],
            s=sizes,
            marker=marker,
            facecolors=[pressure_color(t) for t in subset["physical_growth_pressure_tier"]],
            edgecolors=edge,
            linewidths=1.0,
            alpha=0.88,
            label=f"{quality.title()}",
        )

    label_offsets = {
        "GN-38509": (-55, 10),
        "GS-20057765": (8, -9),
        "GS-20030333": (8, 16),
        "GS-164055": (8, -20),
        "GN-4685": (8, -8),
        "GN-954": (12, 14),
    }
    for _, row in ranking[ranking["object_id"].isin(HIGH_LEVERAGE_OBJECTS)].iterrows():
        xytext = label_offsets.get(row["object_id"], (4, 4))
        ax.annotate(
            row["object_id"],
            xy=(row["physical_pressure_score_0_100"], row["measurement_confidence_score_0_100"]),
            xytext=xytext,
            textcoords="offset points",
            fontsize=7.8,
            color="#111111",
        )

    ax.axvspan(70, 100, color=COLOR_HIGH, alpha=0.06)
    ax.axhspan(75, 100, color=COLOR_LOW, alpha=0.06)
    ax.set_xlabel("Physical growth-pressure score")
    ax.set_ylabel("Measurement confidence score")
    ax.set_title("Physical pressure separated from measurement confidence")
    ax.set_xlim(0, 108)
    ax.set_ylim(25, 101)
    ax.grid(True)

    tier_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_HIGH, markeredgecolor=COLOR_HIGH, label="High pressure"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_MEDIUM, markeredgecolor=COLOR_MEDIUM, label="Medium pressure"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_LOW, markeredgecolor=COLOR_LOW, label="Low pressure"),
    ]
    quality_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor="white", markeredgecolor=COLOR_ROBUST, label="Robust"),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="white", markeredgecolor=COLOR_TENTATIVE, label="Tentative"),
    ]
    ax.legend(handles=tier_handles + quality_handles, loc="lower left", frameon=False, ncol=2)

    caption = (
        "Triage view: physical growth pressure and measurement confidence are shown as separate axes.\n"
        "Large symbols mark extreme MBH/Mstar tension; tentative high-pressure objects are follow-up targets rather than firm formation claims."
    )
    add_caption(fig, caption, y=0.02)
    path = save_figure(fig, FIGURE_PATHS["pressure_confidence"])
    plt.close(fig)
    return path


def _ordered_uncertainty_values(
    summary: pd.DataFrame,
    measurement_ids: pd.Series,
    scenario: str,
    value_column: str,
) -> np.ndarray:
    """Return one uncertainty-summary value per ordered measurement ID."""
    subset = summary[summary["scenario"].eq(scenario)]
    if subset["measurement_id"].duplicated().any():
        duplicates = subset.loc[subset["measurement_id"].duplicated(), "measurement_id"].tolist()
        raise ValueError(f"Duplicate uncertainty rows for scenario {scenario}: {duplicates[:5]}")
    values = subset.set_index("measurement_id")[value_column].reindex(measurement_ids)
    if values.isna().any():
        missing_ids = measurement_ids[values.isna().to_numpy()].tolist()
        raise ValueError(f"Missing {value_column} values for scenario {scenario}: {missing_ids[:5]}")
    return values.to_numpy(float)


def plot_uncertainty_forest(
    uncertainty_ranking: pd.DataFrame,
    fedd_summary: pd.DataFrame,
    mseed_summary: pd.DataFrame,
) -> Path:
    """Plot baseline Monte Carlo intervals and separate MBH systematic shifts."""
    plot_df = uncertainty_ranking.sort_values("rank_uncertainty_pressure").reset_index(drop=True)
    measurement_ids = plot_df["measurement_id"]
    y = np.arange(len(plot_df))

    fedd_light = fedd_summary[fedd_summary["seed_mass_short"].eq("seed1e2")].copy()
    mseed_gentle = mseed_summary[mseed_summary["growth_history"].eq("fedd0p3")].copy()
    expected_rows = len(plot_df) * 3
    if len(fedd_light) != expected_rows or len(mseed_gentle) != expected_rows:
        raise ValueError(
            "Uncertainty forest inputs must contain one baseline and two systematic rows "
            f"per object; found {len(fedd_light)} required-fEdd and {len(mseed_gentle)} "
            f"required-seed rows for {len(plot_df)} objects."
        )

    panels = [
        {
            "summary": fedd_light,
            "prefix": "required_fedd",
            "point_column": "req_fedd_seed1e2_z30_eps0p1_b1",
            "probability_column": "prob_required_fedd_gt_1",
            "threshold": 1.0,
            "xlabel": r"Required lifetime-average $f_{\rm Edd}$ ($M_{\rm seed}=100\,M_\odot$)",
            "title": "Light-seed accretion requirement",
            "probability_header": r"$P(>1)$",
        },
        {
            "summary": mseed_gentle,
            "prefix": "required_log_mseed",
            "point_column": "req_log_mseed_fedd0p3_z30_eps0p1_b1",
            "probability_column": "prob_required_mseed_gt_1e6",
            "threshold": 6.0,
            "xlabel": r"Required $\log_{10}(M_{\rm seed}/M_\odot)$ ($f_{\rm Edd}=0.3$)",
            "title": "Gentle-growth seed requirement",
            "probability_header": r"$P(>10^6)$",
        },
    ]

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 7.3), sharey=True)
    fig.subplots_adjust(left=0.16, right=0.94, bottom=0.19, top=0.88, wspace=0.34)

    for ax, spec in zip(axes, panels, strict=True):
        summary = spec["summary"]
        prefix = spec["prefix"]
        p5 = _ordered_uncertainty_values(summary, measurement_ids, "baseline", f"{prefix}_p5")
        p16 = _ordered_uncertainty_values(summary, measurement_ids, "baseline", f"{prefix}_p16")
        p50 = _ordered_uncertainty_values(summary, measurement_ids, "baseline", f"{prefix}_p50")
        p84 = _ordered_uncertainty_values(summary, measurement_ids, "baseline", f"{prefix}_p84")
        p95 = _ordered_uncertainty_values(summary, measurement_ids, "baseline", f"{prefix}_p95")
        minus_median = _ordered_uncertainty_values(
            summary, measurement_ids, "mbh_minus_0p3dex", f"{prefix}_p50"
        )
        plus_median = _ordered_uncertainty_values(
            summary, measurement_ids, "mbh_plus_0p3dex", f"{prefix}_p50"
        )
        probabilities = _ordered_uncertainty_values(
            summary, measurement_ids, "baseline", spec["probability_column"]
        )

        ax.hlines(y, p5, p95, color="#7A8790", lw=0.85, zorder=1)
        ax.hlines(y, p16, p84, color="#324A5F", lw=4.0, zorder=2)
        ax.hlines(y, minus_median, plus_median, color="#B98218", lw=1.0, alpha=0.9, zorder=1)
        ax.scatter(minus_median, y, marker="<", s=22, color="#B98218", zorder=3)
        ax.scatter(plus_median, y, marker=">", s=22, color="#B98218", zorder=3)
        ax.scatter(
            plot_df[spec["point_column"]],
            y,
            marker="D",
            s=17,
            facecolors="white",
            edgecolors="#202020",
            linewidths=0.75,
            zorder=4,
        )

        robust = plot_df["quality_flag"].str.lower().eq("robust").to_numpy()
        ax.scatter(
            p50[robust],
            y[robust],
            marker="o",
            s=38,
            color=COLOR_ROBUST,
            edgecolors="white",
            linewidths=0.55,
            zorder=5,
        )
        ax.scatter(
            p50[~robust],
            y[~robust],
            marker="s",
            s=39,
            facecolors="white",
            edgecolors=COLOR_TENTATIVE,
            linewidths=1.35,
            zorder=5,
        )

        ax.axvline(spec["threshold"], color=COLOR_HIGH, lw=1.0, ls="--", alpha=0.9, zorder=0)
        ax.text(
            spec["threshold"],
            0.992,
            "threshold",
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=7.7,
            color=COLOR_HIGH,
        )
        for yi, probability in zip(y, probabilities, strict=True):
            ax.text(
                1.015,
                yi,
                f"{100.0 * probability:.0f}%",
                transform=ax.get_yaxis_transform(),
                ha="left",
                va="center",
                fontsize=7.5,
                color=COLOR_HIGH if probability >= 0.5 else COLOR_MUTED,
                clip_on=False,
            )
        ax.text(
            1.015,
            1.012,
            spec["probability_header"],
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=7.7,
            color="#202020",
            clip_on=False,
        )

        all_values = np.concatenate([p5, p95, minus_median, plus_median, [spec["threshold"]]])
        padding = 0.07 * (all_values.max() - all_values.min())
        ax.set_xlim(all_values.min() - padding, all_values.max() + padding)
        ax.set_xlabel(spec["xlabel"])
        ax.set_title(spec["title"])
        ax.grid(True, axis="x", zorder=0)
        ax.tick_params(axis="y", length=0)

    axes[0].set_yticks(y)
    axes[0].set_yticklabels(y_labels(plot_df["object_id"]))
    axes[0].invert_yaxis()
    fig.suptitle("Uncertainty-aware growth-pressure ranking", y=0.975, fontsize=13)

    legend_handles = [
        Line2D([0], [0], color="#7A8790", lw=0.85, label="5th–95th percentile"),
        Line2D([0], [0], color="#324A5F", lw=4.0, label="16th–84th percentile"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_ROBUST, label="Robust MC median"),
        Line2D(
            [0],
            [0],
            marker="s",
            color="none",
            markerfacecolor="white",
            markeredgecolor=COLOR_TENTATIVE,
            label="Tentative MC median",
        ),
        Line2D(
            [0],
            [0],
            marker="D",
            color="none",
            markerfacecolor="white",
            markeredgecolor="#202020",
            label="Point estimate",
        ),
        Line2D(
            [0],
            [0],
            marker="<",
            color="#B98218",
            markerfacecolor="#B98218",
            markeredgecolor="#B98218",
            label=r"Median at $M_{\rm BH}\pm0.3$ dex",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.075),
        frameon=False,
        ncol=3,
        columnspacing=1.4,
        handlelength=2.2,
    )
    caption = (
        r"Baseline Monte Carlo intervals propagate reported asymmetric $M_{\rm BH}$ errors; percentages give baseline threshold probabilities."
        "\n"
        r"Orange endpoints are separate $M_{\rm BH}-0.3$ and $+0.3$ dex systematic medians; all panels assume $z_{\rm seed}=30$, $\epsilon=0.1$, and no merger boost."
    )
    add_caption(fig, caption, y=0.015)
    path = save_figure(fig, FIGURE_PATHS["uncertainty_forest"])
    plt.close(fig)
    return path


def plot_spotlight_maps(ranking: pd.DataFrame) -> Path:
    missing = [str(path) for path in SPOTLIGHT_MAPS.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Spotlight map products are missing: {missing}")

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.9))
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.17, top=0.9, wspace=0.06)

    for ax, object_id in zip(axes, ["GN-38509", "GS-20057765"], strict=True):
        image = mpimg.imread(SPOTLIGHT_MAPS[object_id])
        ax.imshow(image)
        ax.axis("off")

    fig.suptitle("Spotlight seed-timing maps for the two strongest v1 leverage cases", y=0.985, fontsize=12.5)
    gn = ranking.loc[ranking["object_id"] == "GN-38509"].iloc[0]
    gs = ranking.loc[ranking["object_id"] == "GS-20057765"].iloc[0]
    caption = (
        "Existing seed-redshift maps are reused as main-text spotlight prototypes. "
        f"GN-38509: growth-pressure rank {int(gn['rank_physical_pressure'])}, "
        rf"$f_{{\rm Edd}}(100 M_\odot)={gn['req_fedd_seed1e2_z30_eps0p1_b1']:.2f}$; "
        f"GS-20057765: growth-pressure rank {int(gs['rank_physical_pressure'])}, "
        rf"$f_{{\rm Edd}}(100 M_\odot)={gs['req_fedd_seed1e2_z30_eps0p1_b1']:.2f}$."
        "\n"
        r"Panels diagnose assumption sensitivity across seed mass and seed redshift; they do not select a unique formation path."
    )
    add_caption(fig, caption, y=0.015)
    path = save_figure(fig, FIGURE_PATHS["spotlight_maps"])
    plt.close(fig)
    return path


def main() -> None:
    configure_style()
    ranking = read_ranking()
    uncertainty_ranking, fedd_summary, mseed_summary = read_uncertainty_products()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    paths = [
        plot_growth_overview(ranking),
        plot_ranked_required_fedd(ranking),
        plot_ranked_required_seed(ranking),
        plot_pressure_vs_confidence(ranking),
        plot_uncertainty_forest(uncertainty_ranking, fedd_summary, mseed_summary),
        plot_spotlight_maps(ranking),
    ]

    print(f"Read ranking table: {RANKING_PATH.relative_to(REPO_ROOT)} ({len(ranking)} rows)")
    print(
        "Read uncertainty-aware ranking table: "
        f"{UNCERTAINTY_RANKING_PATH.relative_to(REPO_ROOT)} ({len(uncertainty_ranking)} rows)"
    )
    print(f"Saved {len(paths)} final-style v1 figure prototypes:")
    for path in paths:
        print(f"  {path.relative_to(REPO_ROOT)}")
    print("Exploratory result figures were not deleted or replaced.")


if __name__ == "__main__":
    main()
