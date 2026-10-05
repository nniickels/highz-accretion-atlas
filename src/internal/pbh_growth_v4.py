"""Generate/verify the isolated v4 conditional PBH growth study.

Run ``python -m src.internal.pbh_growth_v4 --write`` or ``--verify``.
Inputs are read only. This driver never invokes manuscript regeneration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

import numpy as np
import pandas as pd

from src import models, pbh
from src.internal import early_start_cosmology as cosmology
from src.internal.uncertainty import asymmetric_normal_samples, resolve_mbh_uncertainty
from src.internal.reproduction import assert_csv_reproduction

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path("data/scenarios/v4_pbh_growth.json")
INPUT_PATHS = (
    CONFIG_PATH,
    Path("data/processed/v3/v3_accreting_objects.csv"),
    Path("results/manuscript/tables/publication_object_selection.csv"),
    Path("data/publication/identity_exclusions.json"),
    Path("data/publication/evidence_selection.json"),
)
CODE_PATHS = (Path("src/pbh.py"), Path("src/internal/pbh_growth_v4.py"),
              Path("src/models.py"), Path("src/internal/early_start_cosmology.py"),
              Path("src/internal/uncertainty.py"))
TABLE_NAMES = ("targets", "minimum_seed_mass", "seed_onset_compatibility", "controls")
FIGURE_NAMES = ("minimum_seed_mass", "seed_onset_maps", "controls")


def load_config(root=ROOT):
    config = json.loads((root / CONFIG_PATH).read_text())
    if (config["analysis_version"] != "v4" or config["catalogue_version"] != "v3"
            or config["merger_boost"] != 1.0
            or config["pbh_reference_epoch_redshift"] != cosmology.EQUALITY_REDSHIFT
            or config["target_selection"] !=
            "top_three_publication_primary_by_reference_required_ratio_plus_GN-z11"):
        raise ValueError("Unsupported v4 selection or model configuration")
    if (config["population_viability_status"] != "not_assessed"
            or config["external_constraints_status"] != "not_assessed"):
        raise ValueError("Growth-only v4 cannot claim population/constraint viability")
    if (config["pbh_formation_epoch"] != "assumed_before_matter_radiation_equality_not_modelled"
            or config["growth_before_accretion_onset"] != "omitted_seed_mass_held_constant"):
        raise ValueError("Unsupported pre-onset history")
    onsets = np.asarray(config["onset_redshifts"], dtype=float)
    if (not np.isfinite(onsets).all() or (onsets <= 0).any()
            or (onsets > cosmology.EQUALITY_REDSHIFT).any()
            or len(np.unique(onsets)) != len(onsets)):
        raise ValueError("Invalid onset anchors")
    for key in ("onset_grid_points", "mc_draws_per_object"):
        if type(config[key]) is not int or config[key] < 2:
            raise ValueError(f"{key} must be an integer >= 2")
    if type(config["random_seed"]) is not int or config["random_seed"] < 0:
        raise ValueError("random_seed must be a nonnegative integer")
    axis = config["log10_seed_mass_axis"]
    if (type(axis["points"]) is not int or axis["points"] < 2
            or not np.isfinite([axis["minimum"], axis["maximum"]]).all()
            or axis["minimum"] >= axis["maximum"]):
        raise ValueError("Invalid seed-mass axis")
    for key in ("epsilon_values", "average_fedd_caps", "mass_offsets_dex", "control_seed_log10_msun"):
        values = np.asarray(config[key], dtype=float)
        if not len(values) or not np.isfinite(values).all() or len(np.unique(values)) != len(values):
            raise ValueError(f"{key} must contain unique finite values")
    pbh._validate_growth_parameters(config["average_fedd_caps"], 0.1)
    pbh._validate_growth_parameters(1.0, config["epsilon_values"])
    if (not {30., 100., 3400.}.issubset(config["onset_redshifts"])
            or not {.3, 1., 2.}.issubset(config["average_fedd_caps"])
            or not {2., 5.}.issubset(config["control_seed_log10_msun"])
            or config["control_onset_redshift"] != 30.
            or 0. not in config["mass_offsets_dex"]
            or not np.isclose(config["epsilon_values"], .1).any()
            or not np.isclose(config["epsilon_values"], models.thin_disk_radiative_efficiency(0)).any()):
        raise ValueError("Configured anchors must retain the displayed baseline and controls")
    return config


def select_targets(root=ROOT):
    """Reuse frozen publication membership; independently recompute ranking.

    Membership is checked against raw identity/evidence exclusion policies so
    a stale or modified selection cannot quietly admit unresolved identities.
    """
    objects = pd.read_csv(root / INPUT_PATHS[1])
    selection = pd.read_csv(root / INPUT_PATHS[2])
    if (not objects.physical_object_id.is_unique or not selection.physical_object_id.is_unique
            or set(objects.physical_object_id) != set(selection.physical_object_id)):
        raise ValueError("Publication membership must cover v3 objects one-to-one")
    merged = objects.merge(selection[["physical_object_id", "measurement_id",
        "publication_primary_flag", "publication_exploratory_flag", "excluded_identity_flag"]],
        on=["physical_object_id", "measurement_id"], validate="one_to_one")
    if len(merged) != len(objects):
        raise ValueError("Publication selection uses stale preferred measurements")
    evidence = json.loads((root / INPUT_PATHS[4]).read_text())
    identity = json.loads((root / INPUT_PATHS[3]).read_text())
    if (identity.get("disposition") != "exclude_all_open_identity_groups_from_manuscript_inference"
            or evidence.get("disposition") != "retain_tentative_individual_detections_in_exploratory_only"):
        raise ValueError("Unrecognized input exclusion policy")
    excluded_mids = {mid for group in identity["groups"] for mid in group["measurement_ids"]}
    # available_measurement_ids is pipe-separated in the object catalogue.
    # Resolve policy membership directly through each object's measurement IDs.
    def excluded(row):
        mids = str(row.available_measurement_ids).replace(";", "|").split("|")
        return bool(set(mids + [row.measurement_id]) & excluded_mids)
    expected_excluded = merged.apply(excluded, axis=1)
    if not np.array_equal(expected_excluded, merged.excluded_identity_flag):
        raise ValueError("Publication identity exclusions differ from policy")
    tentative = merged.object_id.isin([entry["object_id"] for entry in evidence["objects"]])
    expected_primary = merged.primary_growth_ranking_flag & ~expected_excluded & ~tentative
    expected_expanded = merged.growth_ranking_eligible_flag & ~expected_excluded
    if (not np.array_equal(expected_primary, merged.publication_primary_flag)
            or not np.array_equal(expected_expanded, merged.publication_exploratory_flag)):
        raise ValueError("Publication evidence membership differs from policy")
    sample = merged.loc[merged.publication_exploratory_flag].copy()
    sample["reference_required_fedd_matter_lambda"] = models.required_fedd_for_seed(
        2, sample.log_mbh_msun_std, 0.1, 30, sample.redshift
    )
    top = sample.loc[sample.publication_primary_flag].sort_values(
        ["reference_required_fedd_matter_lambda", "physical_object_id"], ascending=[False, True]
    ).head(3).copy()
    if len(top) != 3:
        raise ValueError("Not enough eligible primary targets")
    top["selection_reason"] = "top_three_primary_reference_growth_pressure"
    gn = sample.loc[sample.object_id.eq("GN-z11")].copy()
    if len(gn) != 1:
        raise ValueError("GN-z11 must be uniquely present in expanded sample")
    gn["selection_reason"] = "expanded_UV_mass_high_redshift_comparator"
    selected = pd.concat([top, gn], ignore_index=True)
    if not selected.physical_object_id.is_unique:
        raise ValueError("Target selection is not unique")
    return selected


def _object_draws(row, config):
    # Stable per-object streams: adding another target does not change existing draws.
    token = hashlib.sha256(str(row.physical_object_id).encode()).digest()
    seed = int.from_bytes(token[:8], "little")
    rng = np.random.default_rng(np.random.SeedSequence([config["random_seed"], seed]))
    spec = resolve_mbh_uncertainty(row.log_mbh_err_plus_std, row.log_mbh_err_minus_std)
    has_error = spec.mode != "point_estimate_no_reported_mbh_error"
    draws = asymmetric_normal_samples(row.log_mbh_msun_std, row.log_mbh_err_plus_std,
                                     row.log_mbh_err_minus_std,
                                     n_samples=config["mc_draws_per_object"], rng=rng)
    return np.sort(draws), has_error, spec.mode


def build_tables(root=ROOT):
    config = load_config(root)
    targets = select_targets(root)
    # Every grid uses the same radiation-inclusive cosmology, including controls.
    onsets = np.unique(np.r_[np.geomspace(min(config["onset_redshifts"]),
        max(config["onset_redshifts"]), config["onset_grid_points"]), config["onset_redshifts"]])
    axis = config["log10_seed_mass_axis"]
    seeds = np.unique(np.r_[np.linspace(axis["minimum"], axis["maximum"], axis["points"]),
                            config["control_seed_log10_msun"]])
    minimum_rows, map_rows, control_rows, target_rows = [], [], [], []
    for row in targets.itertuples(index=False):
        draws, has_error, mode = _object_draws(row, config)
        base = dict(physical_object_id=row.physical_object_id, object_id=row.object_id,
                    z_obs=float(row.redshift), reported_mass_errors_sampled=has_error)
        target_rows.append(dict(**base, measurement_id=row.measurement_id,
            source_key=row.source_key, source_url=row.source_url, mbh_method=row.mbh_method,
            log_mbh_msun=float(row.log_mbh_msun_std),
            log_mbh_err_plus=row.log_mbh_err_plus_std, log_mbh_err_minus=row.log_mbh_err_minus_std,
            source_caveat_tags=row.source_caveat_tags, lensing_status=row.lensing_status,
            log_mbh_systematic_dex=row.log_mbh_systematic_dex,
            mbh_systematic_kind=row.mbh_systematic_kind,
            source_paper_version=row.source_paper_version, source_table=row.source_table,
            selection_reason=row.selection_reason, publication_primary_flag=row.publication_primary_flag,
            reference_required_fedd_matter_lambda=row.reference_required_fedd_matter_lambda,
            uncertainty_mode=mode, n_mass_draws=config["mc_draws_per_object"] if has_error else 0))
        intervals = pbh.growth_interval_gyr(onsets, row.redshift)
        onset_grid, seed_grid = np.meshgrid(onsets, seeds, indexing="ij")
        for offset in config["mass_offsets_dex"]:
            shifted_draws = draws + offset
            center = row.log_mbh_msun_std + offset
            quantiles = np.quantile(shifted_draws, [.05, .16, .5, .84, .95])
            for eps in config["epsilon_values"]:
                req = models.required_average_fedd(seed_grid, center,
                    pbh.growth_interval_gyr(onset_grid, row.redshift), eps, clip_nonnegative=False)
                for cap in config["average_fedd_caps"]:
                    gain = models.growth_log10_factor(cap, eps, intervals)
                    for j, onset in enumerate(onsets):
                        quant = {f"log10_minimum_seed_{label}": float(value - gain[j]) if has_error else np.nan
                                 for label, value in zip(("p5", "p16", "p50", "p84", "p95"), quantiles)}
                        minimum_rows.append(dict(**base, mass_offset_dex=offset, epsilon=eps,
                            fedd_cap=cap, z_accretion=float(onset), growth_time_gyr=float(intervals[j]),
                            log10_minimum_seed_central=float(center - gain[j]), **quant))
                    # Store the displayed baseline map; full sensitivity grids
                    # are captured much more compactly by minimum_seed_mass.
                    if offset == 0 and np.isclose(eps, .1) and cap == 1:
                        support, overpredict = pbh.compatible_mass_draw_fraction(
                            shifted_draws, seed_grid, onset_grid, row.redshift, cap, eps)
                        status = np.where(seed_grid > center, "seed_overpredicts_target",
                                          np.where(req > cap, "requires_mean_above_cap", "within_growth_cap"))
                        frame = pd.DataFrame({
                            **{key: value for key, value in base.items()},
                            "mass_offset_dex": offset, "epsilon": eps, "fedd_cap": cap,
                            "z_accretion": onset_grid.ravel(), "log10_seed_msun": seed_grid.ravel(),
                            "required_mean_fedd_raw": req.ravel(), "central_status": status.ravel(),
                            "mass_draw_fraction_within_growth_cap": support.ravel() if has_error else np.nan,
                            "mass_draw_fraction_seed_overpredicts": overpredict.ravel() if has_error else np.nan,
                        })
                        map_rows.append(frame)
                # Explicit controls at z=30 and equality/delayed PBH-onset scenarios.
                controls = [("stellar_remnant_control", 2., config["control_onset_redshift"]),
                            ("heavy_astrophysical_control", 5., config["control_onset_redshift"])]
                controls += [("PBH_growth_hypothesis", float(seed), float(onset))
                             for seed in config["control_seed_log10_msun"]
                             for onset in config["onset_redshifts"]]
                for label, seed, onset in controls:
                    dt = pbh.growth_interval_gyr(onset, row.redshift)
                    raw = float(models.required_average_fedd(seed, center, dt, eps, clip_nonnegative=False))
                    rdraw = models.required_average_fedd(seed, shifted_draws, dt, eps,
                                                         clip_nonnegative=False)
                    support, overpredict = pbh.compatible_mass_draw_fraction(
                        shifted_draws, seed, onset, row.redshift, 1., eps)
                    control_rows.append(dict(**base, mass_offset_dex=offset, epsilon=eps,
                        control=label, log10_seed_msun=seed, z_accretion=onset,
                        growth_time_gyr=float(dt), required_mean_fedd_raw=raw,
                        required_mean_fedd_p16=float(np.quantile(rdraw, .16)) if has_error else np.nan,
                        required_mean_fedd_p50=float(np.quantile(rdraw, .5)) if has_error else np.nan,
                        required_mean_fedd_p84=float(np.quantile(rdraw, .84)) if has_error else np.nan,
                        mass_draw_fraction_within_eddington_cap=float(support) if has_error else np.nan,
                        mass_draw_fraction_seed_overpredicts=float(overpredict) if has_error else np.nan))
    return {"targets": pd.DataFrame(target_rows), "minimum_seed_mass": pd.DataFrame(minimum_rows),
            "seed_onset_compatibility": pd.concat(map_rows, ignore_index=True),
            "controls": pd.DataFrame(control_rows)}


def make_figures(tables, destination):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    destination.mkdir(parents=True, exist_ok=True)
    ids = tables["targets"].object_id.tolist()
    colors = ("#386cb0", "#00846a", "#ca6b16")
    style = dict(matplotlib.rcParamsDefault)
    style.update({"font.size": 10, "font.family": "DejaVu Sans",
                  "axes.spines.top": False, "axes.spines.right": False})
    with plt.rc_context(style):
        fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True, sharey=True)
        for ax, oid in zip(axes.flat, ids):
            subset = tables["minimum_seed_mass"].query("object_id == @oid and mass_offset_dex == 0")
            for cap, color in zip((.3, 1., 2.), colors):
                part = subset.loc[np.isclose(subset.epsilon, .1) & np.isclose(subset.fedd_cap, cap)]
                ax.plot(part.z_accretion, part.log10_minimum_seed_central, color=color, label=f"mean cap {cap:g}")
                ax.fill_between(part.z_accretion, part.log10_minimum_seed_p16,
                                part.log10_minimum_seed_p84, color=color, alpha=.13)
            part = subset.loc[np.isclose(subset.epsilon, models.thin_disk_radiative_efficiency(0))
                              & np.isclose(subset.fedd_cap, 1.)]
            ax.plot(part.z_accretion, part.log10_minimum_seed_central, color="#555555", ls="--",
                    label=r"cap 1, $\epsilon=0.05719$")
            ax.axvline(30, color="grey", ls=":", lw=1)
            ax.axhline(2, color="grey", ls=":", lw=1)
            ax.axhline(5, color="grey", ls=":", lw=1)
            ax.set_xscale("log"); ax.set_title(oid); ax.grid(alpha=.15)
            ax.set_xlabel("Accretion-onset redshift (earlier to the right)")
            ax.set_ylabel(r"Minimum $\log_{10}(M_{\rm seed}/M_\odot)$")
        axes[0, 0].legend(fontsize=8)
        fig.suptitle("Minimum seed masses under fixed growth caps")
        fig.text(.5, .025, "Bands: 16–84% of reported log-mass-error draws. Colored curves: efficiency 0.1.\n"
                 "Dotted lines: onset z=30 and seed masses 100 / 100,000 solar masses. No mergers.",
                 ha="center", fontsize=9)
        fig.tight_layout(rect=(0, .09, 1, .95))
        _save_figure(fig, destination, "minimum_seed_mass")
        plt.close(fig)

        fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True, sharey=True)
        for ax, oid in zip(axes.flat, ids):
            part = tables["seed_onset_compatibility"].query("object_id == @oid and mass_offset_dex == 0")
            part = part.loc[np.isclose(part.epsilon, .1) & np.isclose(part.fedd_cap, 1.)]
            pivot = part.pivot(index="log10_seed_msun", columns="z_accretion",
                               values="mass_draw_fraction_within_growth_cap")
            mesh = ax.pcolormesh(pivot.columns, pivot.index, pivot.values, shading="nearest",
                                 cmap="viridis", vmin=0, vmax=1, rasterized=True)
            req = tables["minimum_seed_mass"].query("object_id == @oid and mass_offset_dex == 0")
            req = req.loc[np.isclose(req.epsilon, .1) & np.isclose(req.fedd_cap, 1.)]
            ax.plot(req.z_accretion, req.log10_minimum_seed_central, color="white", lw=1.4)
            ax.axvline(30, color="white", ls=":", lw=1)
            ax.set_xscale("log"); ax.set_xlim(pivot.columns.min(), pivot.columns.max())
            ax.set_ylim(pivot.index.min(), pivot.index.max()); ax.set_title(oid)
            ax.set_xlabel("Accretion-onset redshift (earlier to the right)")
            ax.set_ylabel(r"$\log_{10}(M_{\rm seed}/M_\odot)$")
        fig.suptitle(r"Fraction of mass-error draws reachable for $0\leq\overline{f}_{\rm Edd}\leq1$, $\epsilon=0.1$")
        fig.subplots_adjust(left=.08, right=.85, bottom=.15, top=.9, hspace=.3)
        fig.colorbar(mesh, cax=fig.add_axes([.88, .22, .02, .6]), label="Fraction of mass-error draws reachable")
        fig.text(.5, .045, "White curve: minimum seed at central mass. Seeds exceeding a draw's mass are excluded.",
                 ha="center", fontsize=9)
        _save_figure(fig, destination, "seed_onset_maps")
        plt.close(fig)

        controls = tables["controls"].query("mass_offset_dex == 0")
        controls = controls.loc[np.isclose(controls.epsilon, .1)]
        scenarios = [("stellar_remnant_control", 2., 30., "100 solar masses; onset z=30"),
                     ("PBH_growth_hypothesis", 2., 3400., "100 solar masses; onset z=3400"),
                     ("PBH_growth_hypothesis", 2., 100., "100 solar masses; onset z=100"),
                     ("heavy_astrophysical_control", 5., 30., "100,000 solar masses; onset z=30")]
        fig, ax = plt.subplots(figsize=(11, 5))
        styles = ("o", "s", "^", "D")
        for i, (label, seed, onset, title) in enumerate(scenarios):
            part = controls.loc[controls.control.eq(label) & controls.log10_seed_msun.eq(seed)
                                & controls.z_accretion.eq(onset)].set_index("object_id").loc[ids]
            y = np.arange(len(ids)) + (i - 1.5) * .14
            center = part.required_mean_fedd_raw.to_numpy()
            # Plot the empirical median with percentile bars; central mass shown separately.
            median = part.required_mean_fedd_p50.to_numpy()
            error = np.vstack([median - part.required_mean_fedd_p16, part.required_mean_fedd_p84 - median])
            ax.errorbar(median, y, xerr=error, fmt=styles[i], capsize=2, label=title)
            ax.plot(center, y, "|", color="black", ms=6)
        ax.axvline(1, color="grey", ls="--"); ax.set_yticks(np.arange(len(ids)), ids)
        ax.invert_yaxis(); ax.set_xlabel(r"Required $\overline{f}_{\rm Edd}$ ($\epsilon=0.1$, no mergers)")
        ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1.01, 1))
        ax.set_title("Required average rates for selected seed masses and starting times")
        fig.text(.5, .025, "Symbols: Monte Carlo medians and 16–84% intervals; black ticks: central masses.",
                 ha="center", fontsize=9)
        fig.tight_layout(rect=(0, .1, 1, 1))
        _save_figure(fig, destination, "controls")
        plt.close(fig)


def _save_figure(fig, destination, name):
    fig.savefig(destination / f"v4_{name}.png", dpi=160)
    fig.savefig(destination / f"v4_{name}.pdf", metadata={"CreationDate": None, "ModDate": None})


def input_provenance(root=ROOT):
    return {str(path): hashlib.sha256((root / path).read_bytes()).hexdigest()
            for path in INPUT_PATHS + CODE_PATHS}


def verify_input_provenance(root, pinned, *, baseline_root=None):
    """Accept regenerated CSV roundoff only against an independently pinned input.

    CI regenerates v3 before rerunning the regression suite. A CSV may then
    have different serialization bytes despite passing numerical reproduction.
    Code/configuration remain byte-exact; CSV contents use the existing shared
    comparison only when the independent baseline matches the original hash.
    """
    current = input_provenance(root)
    if current.keys() != pinned.keys():
        raise AssertionError("v4 input/code provenance membership differs")
    baseline_root = baseline_root or os.environ.get("HIGHZ_BASELINE_ROOT")
    csv_inputs = {str(path) for path in INPUT_PATHS if path.suffix == ".csv"}
    for name, digest in pinned.items():
        if current[name] == digest:
            continue
        if name not in csv_inputs or not baseline_root:
            raise AssertionError(f"v4 input or implementation changed: {name}")
        baseline = Path(baseline_root).resolve()
        if baseline == root.resolve():
            raise AssertionError("v4 CSV baseline must be independent of regenerated inputs")
        original = baseline / name
        if hashlib.sha256(original.read_bytes()).hexdigest() != digest:
            raise AssertionError(f"v4 CSV baseline does not match pinned input: {name}")
        assert_csv_reproduction(original, pd.read_csv(root / name))


def write_outputs(root=ROOT, destination=None):
    destination = Path(destination) if destination is not None else root / "results/v4"
    resolved = destination.resolve()
    if resolved.is_relative_to(root.resolve()) and resolved != (root / "results/v4").resolve():
        raise ValueError("Within the repository, v4 output is restricted to results/v4")
    tables = build_tables(root)
    (destination / "tables").mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        table.to_csv(destination / "tables" / f"v4_{name}.csv", index=False)
    make_figures(tables, destination / "figures")
    artifact_names = [f"tables/v4_{name}.csv" for name in TABLE_NAMES]
    artifact_names += [f"figures/v4_{name}.{ext}" for name in FIGURE_NAMES for ext in ("png", "pdf")]
    manifest = {
        "analysis_version": "v4", "catalogue_version": "v3",
        "claim_scope": "conditional_growth_compatibility_only",
        "population_viability": "not_assessed", "external_constraints": "not_assessed",
        "config": load_config(root),
        "cosmology": {"name": "flat_matter_radiation_lambda", "h0_km_s_mpc": cosmology.H0_KM_S_MPC,
                      "omega_m": cosmology.OMEGA_M, "omega_r": cosmology.OMEGA_R,
                      "omega_lambda": cosmology.OMEGA_LAMBDA},
        "input_and_code_sha256": input_provenance(root),
        "table_rows": {name: len(table) for name, table in tables.items()},
        "artifacts": {name: hashlib.sha256((destination / name).read_bytes()).hexdigest()
                      for name in artifact_names},
    }
    (destination / "v4_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    if resolved == (root / "results/v4").resolve():
        from src.internal.build_results_inventory import build_inventory
        build_inventory(results_root=root / "results")
    return manifest


def verify_outputs(root=ROOT, *, verify_figures=True):
    destination = root / "results/v4"
    manifest = json.loads((destination / "v4_manifest.json").read_text())
    metadata = {"analysis_version": "v4", "catalogue_version": "v3",
                "claim_scope": "conditional_growth_compatibility_only",
                "population_viability": "not_assessed", "external_constraints": "not_assessed"}
    if any(manifest.get(key) != value for key, value in metadata.items()):
        raise AssertionError("v4 manifest claim scope differs")
    verify_input_provenance(root, manifest["input_and_code_sha256"])
    if manifest["config"] != load_config(root):
        raise AssertionError("v4 manifest configuration differs")
    expected = {f"tables/v4_{name}.csv" for name in TABLE_NAMES}
    expected |= {f"figures/v4_{name}.{ext}" for name in FIGURE_NAMES for ext in ("png", "pdf")}
    if set(manifest["artifacts"]) != expected:
        raise AssertionError("v4 manifest artifact membership differs")
    for name, digest in manifest["artifacts"].items():
        if hashlib.sha256((destination / name).read_bytes()).hexdigest() != digest:
            raise AssertionError(f"v4 artifact changed: {name}")
    tables = build_tables(root)
    if manifest["table_rows"] != {name: len(table) for name, table in tables.items()}:
        raise AssertionError("v4 row counts differ")
    for name, table in tables.items():
        assert_csv_reproduction(destination / "tables" / f"v4_{name}.csv", table)
    if verify_figures:
        from src.internal.verify_regenerated_artifacts import compare_artifact
        with tempfile.TemporaryDirectory(prefix="highz-v4-verify-") as directory:
            temporary = Path(directory)
            make_figures(tables, temporary)
            for name in FIGURE_NAMES:
                for ext in ("png", "pdf"):
                    filename = f"v4_{name}.{ext}"
                    compare_artifact(destination / "figures" / filename, temporary / filename)
    return {"v4_verification": "pass", "targets": len(tables["targets"]),
            "claim_scope": "conditional_growth_compatibility_only"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--write", action="store_true")
    actions.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.write:
        manifest = write_outputs()
        print(json.dumps({"written": "results/v4", "table_rows": manifest["table_rows"]}, indent=2))
    else:
        print(json.dumps(verify_outputs(), indent=2))


if __name__ == "__main__":
    main()
