"""Render the canonical per-object seed-redshift/mass maps."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.models import required_fedd_for_seed
from src.internal import atlas


ROOT = Path(__file__).resolve().parents[2]
LOG_MSEED = np.linspace(1.0, 6.2, 150)
N_Z_SEED = 150
Z_SEED_MAX = 30.0
EPSILON = 0.1
MERGER_BOOST = 1.0


def panel_path(version: str, obj: pd.Series) -> Path:
    stem = atlas.slug(obj["physical_object_id"])
    return (
        ROOT / "results" / version / "parameter_maps" / "seedredshift_mass_maps"
        / f"{version}_seedredshift_mass_map_{stem}.png"
    )


def plot_seedredshift_mass_map(version: str, obj: pd.Series, output: Path) -> None:
    z_obs = float(obj["redshift"])
    z_seed = np.linspace(z_obs + 0.1, Z_SEED_MAX, N_Z_SEED)
    log_seed, seed_redshift = np.meshgrid(LOG_MSEED, z_seed, indexing="xy")
    required = required_fedd_for_seed(
        log_mseed=log_seed,
        log_mbh_final=float(obj["log_mbh_msun_std"]),
        epsilon=EPSILON,
        z_seed=seed_redshift,
        z_obs=z_obs,
        merger_boost=MERGER_BOOST,
    )
    fig, ax = plt.subplots(figsize=(9.0, 6.5), constrained_layout=True)
    mesh = ax.pcolormesh(
        log_seed, seed_redshift, np.clip(required, 0.0, 3.0),
        shading="auto", cmap="magma_r", vmin=0.0, vmax=3.0, rasterized=True,
    )
    visible = [level for level in (0.3, 1.0, 2.0) if np.nanmin(required) <= level <= np.nanmax(required)]
    if visible:
        contour = ax.contour(log_seed, seed_redshift, required, levels=visible, colors="white", linewidths=1.15)
        ax.clabel(contour, fmt={0.3: "0.3", 1.0: "1", 2.0: "2"}, fontsize=8)
    for mass in (2.0, 4.0, 5.0):
        ax.axvline(mass, color="white", ls=":", lw=0.9, alpha=0.8)
    colorbar = fig.colorbar(mesh, ax=ax, pad=0.02)
    colorbar.set_label(r"Required lifetime-average $f_{\rm Edd}$ (clipped at 3)")
    ax.set(
        xlabel=r"$\log_{10}(M_{\rm seed}/M_\odot)$",
        ylabel=r"Seed redshift $z_{\rm seed}$",
        title=(
            f"{version}: {obj['object_id']} | z={z_obs:.3f} | "
            f"log MBH={float(obj['log_mbh_msun_std']):.2f}"
        ),
        xlim=(LOG_MSEED.min(), LOG_MSEED.max()), ylim=(z_obs + 0.1, Z_SEED_MAX),
    )
    ax.text(
        0.01, 0.01,
        r"Baseline: $\epsilon=0.1$, no merger boost; contours mark $f_{\rm Edd}=0.3,1,2$.",
        transform=ax.transAxes, color="white", fontsize=8.5, va="bottom",
        bbox={"facecolor": "black", "alpha": 0.42, "edgecolor": "none", "pad": 3},
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, facecolor="white")
    plt.close(fig)


def materialize(version: str, objects: pd.DataFrame, *, rebuild: bool) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, obj in objects.sort_values(["object_class", "redshift", "physical_object_id"]).iterrows():
        eligible = atlas.boolish(obj["growth_ranking_eligible_flag"])
        output = panel_path(version, obj)
        if rebuild or not output.exists():
            if eligible:
                plot_seedredshift_mass_map(version, obj, output)
            else:
                atlas.VERSION = version
                atlas.status_panel(obj, "seedredshift_mass_map", output)
        rows.append({
            "release": version,
            "physical_object_id": obj["physical_object_id"],
            "object_id": obj["object_id"],
            "object_class": obj["object_class"],
            "growth_ranking_eligible_flag": eligible,
            "product_kind": "seedredshift_mass_map",
            "product_status": "numerical_growth_product" if eligible else "no_inference_status_panel",
            "status_reason": (
                "eligible_canonical_numeric_mbh" if eligible
                else obj["growth_ranking_eligibility_reason"]
            ),
            "path": output.relative_to(ROOT).as_posix(),
        })
    result = pd.DataFrame(rows)
    if len(result) != len(objects) or result["physical_object_id"].nunique() != len(objects):
        raise AssertionError("Seed-redshift/mass maps must contain one panel per object")
    return result
