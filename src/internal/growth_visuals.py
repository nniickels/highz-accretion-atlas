"""Shared per-object growth visualizations for canonical datasets."""

from __future__ import annotations

import os
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

from src.models import (
    SEED_MODELS,
    growth_parameter_grid,
    predicted_log_mbh,
    slim_disk_effective_efficiency,
    thin_disk_radiative_efficiency,
)


Z_SEED = 30.0
LOG_SEED_AXIS = np.linspace(0.0, 8.0, 100)
FEDD_AXIS = np.linspace(0.0, 3.0, 90)
COMPATIBILITY_FEDD = (0.1, 0.3, 0.5, 1.0, 2.0, 3.0)
SPIN_CASES = (
    (-1.0, "spin_minus1_eps0p038", "a=-1"),
    (0.0, "spin_0_eps0p057", "a=0"),
    (1.0, "spin_plus1_eps0p423", "a=+1"),
)
MERGER_CASES = ((1.0, "no_merger_boost"), (2.0, "merger_boost_x2"))


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
    """Render the six spin/merger parameter maps for one eligible object."""
    configure_style()
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
        thin_epsilon = float(thin_disk_radiative_efficiency(spin))
        ax.set_title(f"{spin_label}, thin epsilon={thin_epsilon:.3f}, {boost_label}")
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
        "White contour reproduces the canonical mass; photon-trapping efficiency "
        "is used above Eddington. z_seed=30.",
        ha="center", fontsize=7.5,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160)
    plt.close(fig)


def plot_growth_track(obj: pd.Series, output: Path) -> None:
    """Render reference growth tracks and the canonical mass for one object."""
    configure_style()
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
    err_minus = pd.to_numeric(
        pd.Series([obj.get("log_mbh_err_minus_std")]), errors="coerce",
    ).iloc[0]
    err_plus = pd.to_numeric(
        pd.Series([obj.get("log_mbh_err_plus_std")]), errors="coerce",
    ).iloc[0]
    yerr = None if pd.isna(err_minus) or pd.isna(err_plus) else [
        [float(err_minus)], [float(err_plus)],
    ]
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
    fig.text(
        0.5, 0.012,
        "Reference tracks use z_seed=30, epsilon=0.1, and no merger boost.",
        ha="center", fontsize=7.5,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)
