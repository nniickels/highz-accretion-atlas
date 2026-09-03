"""Shared per-object Eddington-fraction/mass maps for canonical datasets."""

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


def plot_fedd_mass_map(obj: pd.Series, output: Path) -> None:
    """Render the six spin/merger f_Edd/mass maps for one eligible object."""
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
