"""Generate seed-redshift diagnostic figures for the v1 catalogue.

These plots complement the fixed-z_seed parameter maps from v1_evaluate.ipynb.
The 2D maps solve for the average f_Edd required to reach each object's
observed black-hole mass across seed mass and seed redshift. The 3D plot is an
exploratory rendering of the same surface for the highest-redshift v1 object.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.models import required_fedd_for_seed


PROCESSED_PATH = REPO_ROOT / "data/processed/v1/v1_processed.csv"
GALLERY_DIR = REPO_ROOT / "results/past_releases/v1/galleries"
SEED_REDSHIFT_MAP_DIR = GALLERY_DIR / "seed_redshift_maps"
SEED_REDSHIFT_3D_DIR = GALLERY_DIR / "seed_redshift_3d_tests"

Z_SEED_MAX = 30.0
LOG_MSEED_AXIS = np.linspace(1.0, 6.2, 180)
N_Z_SEED = 180
EPSILON = 0.1
MERGER_BOOST = 1.0

CAPTION_STYLE = {
    "ha": "center",
    "va": "bottom",
    "fontsize": 8.4,
    "fontfamily": "serif",
    "color": "#222222",
    "linespacing": 1.18,
}


def configure_plot_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 130,
            "savefig.dpi": 350,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.18,
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "font.size": 10,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "axes.titleweight": "regular",
            "axes.titlepad": 8,
            "axes.labelpad": 5,
            "legend.fontsize": 8.5,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "axes.linewidth": 0.9,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.minor.visible": True,
            "ytick.minor.visible": True,
            "grid.color": "#D8D8D8",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.55,
        }
    )


def add_figure_caption(fig: plt.Figure, caption: str, y: float = 0.045) -> None:
    fig.text(0.5, y, caption, **CAPTION_STYLE)


def save_figure(fig: plt.Figure, png_path: Path) -> None:
    fig.savefig(png_path, dpi=350, facecolor="white")
    plt.close(fig)


def safe_filename(value: object) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "-", str(value)).strip("-")
    return text.lower() or "object"


def seed_redshift_axis(z_obs: float) -> np.ndarray:
    z_min = min(Z_SEED_MAX - 0.1, float(z_obs) + 0.1)
    if z_min >= Z_SEED_MAX:
        raise ValueError(f"z_obs={z_obs:g} leaves no seed-redshift range below {Z_SEED_MAX:g}")
    return np.linspace(z_min, Z_SEED_MAX, N_Z_SEED)


def required_fedd_surface(obj: pd.Series) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z_seed_axis = seed_redshift_axis(float(obj["redshift"]))
    x_grid, y_grid = np.meshgrid(LOG_MSEED_AXIS, z_seed_axis, indexing="xy")
    fedd_grid = required_fedd_for_seed(
        log_mseed=x_grid,
        log_mbh_final=float(obj["log_mbh_msun_std"]),
        epsilon=EPSILON,
        z_seed=y_grid,
        z_obs=float(obj["redshift"]),
        merger_boost=MERGER_BOOST,
    )
    return x_grid, y_grid, fedd_grid


def draw_seed_thresholds(ax: plt.Axes, *, y_text: float) -> None:
    for x_ref, label in [(2.0, r"$10^2$"), (4.0, r"$10^4$"), (5.0, r"$10^5$")]:
        ax.axvline(x_ref, color="white", lw=0.9, ls=":", alpha=0.82)
        ax.text(x_ref + 0.03, y_text, label, color="white", fontsize=8.0, rotation=90, va="top")


def plot_seed_redshift_map(obj: pd.Series, png_path: Path) -> None:
    x_grid, y_grid, fedd_grid = required_fedd_surface(obj)

    fig, ax = plt.subplots(figsize=(6.4, 6.05))
    fig.subplots_adjust(left=0.12, right=0.86, bottom=0.285, top=0.895)
    mesh = ax.pcolormesh(
        x_grid,
        y_grid,
        np.clip(fedd_grid, 0.0, 3.0),
        shading="auto",
        cmap="magma_r",
        vmin=0.0,
        vmax=3.0,
        rasterized=True,
    )
    cbar = fig.colorbar(mesh, ax=ax, pad=0.02)
    cbar.set_label(r"Required average $f_{\rm Edd}$ (clipped at 3)", labelpad=7)

    levels = [0.3, 1.0, 2.0]
    f_min = float(np.nanmin(fedd_grid))
    f_max = float(np.nanmax(fedd_grid))
    visible_levels = [level for level in levels if f_min <= level <= f_max]
    if visible_levels:
        contour = ax.contour(x_grid, y_grid, fedd_grid, levels=visible_levels, colors="white", linewidths=1.25)
        ax.clabel(contour, fmt={0.3: "0.3", 1.0: "1", 2.0: "2"}, inline=True, fontsize=8.0)

    draw_seed_thresholds(ax, y_text=Z_SEED_MAX - 0.4)
    ax.axhline(Z_SEED_MAX, color="white", lw=1.0, ls="-", alpha=0.78)
    ax.text(1.08, Z_SEED_MAX - 0.18, r"$z_{\rm seed}=30$", color="white", fontsize=8.5, va="top")

    quality_text = str(obj.get("quality_flag", "")).title()
    title = f"{obj['object_id']}  |  z = {float(obj['redshift']):.3f}  |  {quality_text}"
    ax.set_title(title)
    ax.set_xlabel(r"$\log_{10}(M_{\rm seed}/M_\odot)$")
    ax.set_ylabel(r"Seed redshift $z_{\rm seed}$")
    ax.set_xlim(LOG_MSEED_AXIS.min(), LOG_MSEED_AXIS.max())
    ax.set_ylim(y_grid.min(), Z_SEED_MAX)
    ax.grid(False)

    caption = (
        "Colour gives the average Eddington fraction required to reach the observed black-hole mass.\n"
        "White contours mark required $f_{\\rm Edd}=0.3$, 1, and 2; vertical lines mark seed-mass thresholds.\n"
        "The scan is restricted to late-to-early astrophysical seed timing with $z_{\\rm seed}\\leq30$; ages use Planck cosmology."
    )
    add_figure_caption(fig, caption)
    save_figure(fig, png_path)


def plot_seed_redshift_3d_test(obj: pd.Series, png_path: Path) -> None:
    x_grid, y_grid, fedd_grid = required_fedd_surface(obj)
    z_grid = np.clip(fedd_grid, 0.0, 3.0)

    fig = plt.figure(figsize=(7.0, 6.1))
    fig.subplots_adjust(left=0.02, right=0.95, bottom=0.21, top=0.88)
    ax = fig.add_subplot(111, projection="3d")
    surface = ax.plot_surface(
        x_grid,
        y_grid,
        z_grid,
        cmap="magma_r",
        vmin=0.0,
        vmax=3.0,
        linewidth=0,
        antialiased=True,
        alpha=0.96,
        rcount=90,
        ccount=90,
    )
    ax.contour(x_grid, y_grid, z_grid, levels=[0.3, 1.0, 2.0], zdir="z", offset=0.0, colors="white", linewidths=0.9)
    ax.set_xlabel(r"$\log_{10}(M_{\rm seed}/M_\odot)$", labelpad=7)
    ax.set_ylabel(r"$z_{\rm seed}$", labelpad=7)
    ax.set_zlabel(r"Required $f_{\rm Edd}$", labelpad=7)
    ax.set_xlim(LOG_MSEED_AXIS.min(), LOG_MSEED_AXIS.max())
    ax.set_ylim(seed_redshift_axis(float(obj["redshift"])).min(), Z_SEED_MAX)
    ax.set_zlim(0.0, 3.0)
    ax.view_init(elev=27, azim=-132)
    ax.set_title(
        f"3D seed-timing test: {obj['object_id']}  |  z = {float(obj['redshift']):.3f}",
        pad=12,
    )
    cbar = fig.colorbar(surface, ax=ax, shrink=0.68, pad=0.08)
    cbar.set_label(r"Required average $f_{\rm Edd}$ (clipped at 3)", labelpad=7)
    caption = (
        "Exploratory 3D rendering of the same seed-redshift surface used in the 2D maps.\n"
        "The vertical scale is clipped at $f_{\\rm Edd}=3$ so extreme late-seed cases do not dominate the perspective; ages use Planck cosmology."
    )
    add_figure_caption(fig, caption, y=0.035)
    save_figure(fig, png_path)


def main() -> None:
    configure_plot_style()
    SEED_REDSHIFT_MAP_DIR.mkdir(parents=True, exist_ok=True)
    SEED_REDSHIFT_3D_DIR.mkdir(parents=True, exist_ok=True)

    for old_map in SEED_REDSHIFT_MAP_DIR.glob("v1_seed_redshift_map_*.png"):
        old_map.unlink()
    for old_map in SEED_REDSHIFT_3D_DIR.glob("v1_seed_redshift_3d_test_*.png"):
        old_map.unlink()

    df = pd.read_csv(PROCESSED_PATH)
    map_paths = []
    for _, obj in df.sort_values(["redshift", "object_id"]).iterrows():
        stem = f"v1_seed_redshift_map_{safe_filename(obj['measurement_id'])}"
        png_path = SEED_REDSHIFT_MAP_DIR / f"{stem}.png"
        plot_seed_redshift_map(obj, png_path)
        map_paths.append(png_path)

    test_obj = df.sort_values(["redshift", "object_id"], ascending=[False, True]).iloc[0]
    test_stem = f"v1_seed_redshift_3d_test_{safe_filename(test_obj['measurement_id'])}"
    test_path = SEED_REDSHIFT_3D_DIR / f"{test_stem}.png"
    plot_seed_redshift_3d_test(test_obj, test_path)

    print(f"Saved {len(map_paths)} seed-redshift 2D maps in {SEED_REDSHIFT_MAP_DIR.relative_to(REPO_ROOT)}")
    print(f"Saved 1 seed-redshift 3D test in {SEED_REDSHIFT_3D_DIR.relative_to(REPO_ROOT)}")
    print(f"3D test object: {test_obj['object_id']} at z={float(test_obj['redshift']):.3f}")


if __name__ == "__main__":
    main()
