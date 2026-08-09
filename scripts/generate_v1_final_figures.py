"""Create final-style v1 figure prototypes for the observational atlas.

The figures are main-text candidates driven by the v1 ranking table. They are
saved into a separate directory and do not delete or replace exploratory
outputs.
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
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    paths = [
        plot_growth_overview(ranking),
        plot_ranked_required_fedd(ranking),
        plot_ranked_required_seed(ranking),
        plot_pressure_vs_confidence(ranking),
        plot_spotlight_maps(ranking),
    ]

    print(f"Read ranking table: {RANKING_PATH.relative_to(REPO_ROOT)} ({len(ranking)} rows)")
    print(f"Saved {len(paths)} final-style v1 figure prototypes:")
    for path in paths:
        print(f"  {path.relative_to(REPO_ROOT)}")
    print("Exploratory result figures were not deleted or replaced.")


if __name__ == "__main__":
    main()
