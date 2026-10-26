"""Compact v3 results and comparisons using the existing growth models."""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd

from src import models, pbh
from src.internal.compatibility.v7_science_core import (
    DEFAULT_N_SAMPLES, DEFAULT_RANDOM_SEED, _boolish, _rng,
)
from src.internal.publication_selection import build_publication_membership
from src.internal.uncertainty import asymmetric_normal_samples, resolve_mbh_uncertainty


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path("data/scenarios/catalogue_growth_comparisons.json")
OUTPUT_NAMES = (
    "object_results", "growth_assumption_comparison", "field_availability",
    "minimum_seed_mass",
)
REFERENCE = dict(log10_seed_mass=2.0, epsilon=0.1, z_seed=30.0,
                 mass_offset_dex=0.0, merger_boost=1.0)
SAMPLE_FIELDS = (
    "publication_primary_flag", "publication_exploratory_flag", "excluded_identity_flag",
)


def load_config(root: Path = ROOT) -> dict:
    config = json.loads((root / CONFIG_PATH).read_text())
    if (config["catalogue_version"] != "v3" or config["reference"] != REFERENCE
            or config["comparison_cosmology"] != "flat_matter_lambda"):
        raise ValueError("Catalogue comparisons must retain the v3 reference model")
    scenarios = config["comparison_scenarios"]
    names = [row.get("name") for row in scenarios]
    if (not names or any(not isinstance(name, str) or not name.strip() for name in names)
            or len(names) != len(set(names)) or scenarios[0] != {"name": "reference"}):
        raise ValueError("Scenarios need unique names and an unchanged reference first")
    for scenario in scenarios:
        if set(scenario) - ({"name"} | set(REFERENCE)):
            raise ValueError("Unknown comparison parameter")
        parameters = REFERENCE | {k: v for k, v in scenario.items() if k != "name"}
        if not np.isfinite(list(parameters.values())).all():
            raise ValueError("Comparison parameters must be finite")
        if (not 0 < parameters["epsilon"] < 1 or parameters["z_seed"] <= 0
                or parameters["merger_boost"] != 1):
            raise ValueError("Invalid comparison efficiency, starting time, or merger factor")
    minimum = config["minimum_seed"]
    if (minimum["cosmology"] != "flat_matter_radiation_lambda"
            or minimum["merger_boost"] != 1):
        raise ValueError("Minimum seeds require the radiation-inclusive model without mergers")
    for field in ("onset_redshifts", "epsilon_values", "average_fedd_caps", "mass_offsets_dex"):
        values = np.asarray(minimum[field], dtype=float)
        if (values.ndim != 1 or not values.size or not np.isfinite(values).all()
                or np.unique(values).size != values.size):
            raise ValueError(f"{field} must contain unique finite values")
    onsets = np.asarray(minimum["onset_redshifts"])
    if (onsets <= 0).any() or (onsets > pbh.EQUALITY_REDSHIFT).any():
        raise ValueError("Invalid minimum-seed starting redshift")
    pbh._validate_growth_parameters(minimum["average_fedd_caps"], 0.1)
    pbh._validate_growth_parameters(1.0, minimum["epsilon_values"])
    return config


def _mass_draws(row, n_samples: int, random_seed: int):
    spec = resolve_mbh_uncertainty(row.log_mbh_err_plus_std, row.log_mbh_err_minus_std)
    has_error = spec.mode != "point_estimate_no_reported_mbh_error"
    draws = asymmetric_normal_samples(
        row.log_mbh_msun_std, row.log_mbh_err_plus_std, row.log_mbh_err_minus_std,
        n_samples=n_samples, rng=_rng(random_seed, str(row.physical_object_id)),
    )
    return draws, has_error


def build_object_results(objects, point, uncertainty, membership, reference):
    columns = [
        "physical_object_id", "object_id", "measurement_id", "source_key", "source_url",
        "object_class", "evidence_status", "mass_comparability_group", "redshift",
        "log_mbh_msun_std", "log_mbh_err_plus_std", "log_mbh_err_minus_std", "mbh_method",
        "growth_ranking_eligible_flag", "growth_ranking_eligibility_reason",
        "scientific_identity_status", "scientific_identity_issue_group",
        "log_mbh_systematic_dex", "mbh_systematic_kind", "source_caveat_tags",
    ]
    keys = ["physical_object_id", "measurement_id"]
    result = objects[columns].merge(
        membership[[*keys, *SAMPLE_FIELDS]], on=keys, validate="one_to_one",
    )
    point_fields = [
        "required_fedd_seed1e2", "required_fedd_seed1e4", "required_fedd_seed1e5",
        "required_log_mseed_fedd1",
    ]
    result = result.merge(point[[*keys, *point_fields]], on=keys, how="left", validate="one_to_one")
    error_fields = [
        "required_fedd_seed1e2_p16", "required_fedd_seed1e2_p50",
        "required_fedd_seed1e2_p84", "prob_required_fedd_seed1e2_gt_1",
    ]
    errors = uncertainty[[*keys, "reported_mass_errors_sampled", *error_fields]].copy()
    # The older uncertainty table repeats point masses for missing errors.
    # This compact view leaves their intervals and probabilities unavailable.
    errors.loc[~errors.reported_mass_errors_sampled.map(_boolish), error_fields] = np.nan
    result = result.merge(errors, on=keys, how="left", validate="one_to_one")
    result["reported_mass_errors_sampled"] = result.reported_mass_errors_sampled.map(_boolish)
    result["reference_z_seed"] = reference["z_seed"]
    result["reference_epsilon"] = reference["epsilon"]
    result["reference_merger_boost"] = reference["merger_boost"]
    return result.sort_values("physical_object_id").reset_index(drop=True)


def build_field_availability(measurements, objects):
    rows = []
    for level, frame in (("measurement", measurements), ("object", objects)):
        def finite(column):
            return np.isfinite(pd.to_numeric(frame[column], errors="coerce"))

        masks = {
            "redshift": finite("redshift"),
            "coordinates": finite("ra_deg") & finite("dec_deg"),
            "black_hole_mass": finite("log_mbh_msun_std"),
            "black_hole_mass_error": finite("log_mbh_msun_std") & (
                finite("log_mbh_err_plus_std") | finite("log_mbh_err_minus_std")),
            "stellar_mass": finite("log_mstar_msun_std"),
            "stellar_mass_upper_limit": finite("log_mstar_upper_limit_msun"),
            "bolometric_luminosity": finite("log_lbol_erg_s_std"),
            "reported_eddington_ratio": finite("edd_ratio_std"),
        }
        groups = [("all", "all", frame.index)]
        for field in ("source_key", "object_class"):
            for value, group in frame.groupby(field, sort=True, dropna=False):
                groups.append((field, value, group.index))
        for dimension, value, indexes in groups:
            for field, mask in masks.items():
                available = int(mask.loc[indexes].sum())
                total = len(indexes)
                rows.append(dict(entity_level=level, group_by=dimension, group=value,
                                 field=field, n_rows=total, n_available=available,
                                 n_missing=total - available, fraction_available=available / total))
    return pd.DataFrame(rows)


def build_growth_comparisons(eligible, membership, config, n_samples, random_seed):
    selection = membership.set_index("physical_object_id")
    scenarios = [(row["name"], REFERENCE | {k: v for k, v in row.items() if k != "name"})
                 for row in config["comparison_scenarios"]]
    settings = config["minimum_seed"]
    minimum_grid = list(product(settings["onset_redshifts"], settings["epsilon_values"],
                                settings["average_fedd_caps"], settings["mass_offsets_dex"]))
    comparison_rows, minimum_rows = [], []
    for row in eligible.sort_values("physical_object_id").itertuples(index=False):
        draws, has_error = _mass_draws(row, n_samples, random_seed)
        base = dict(physical_object_id=row.physical_object_id, object_id=row.object_id,
                    measurement_id=row.measurement_id, source_key=row.source_key,
                    object_class=row.object_class, mass_comparability_group=row.mass_comparability_group,
                    redshift=float(row.redshift),
                    **{field: bool(selection.loc[row.physical_object_id, field]) for field in SAMPLE_FIELDS},
                    reported_mass_errors_sampled=has_error, n_mass_draws=n_samples if has_error else 0,
                    random_seed=random_seed)
        for name, parameters in scenarios:
            seed, eps = parameters["log10_seed_mass"], parameters["epsilon"]
            start, offset = parameters["z_seed"], parameters["mass_offset_dex"]
            boost = parameters["merger_boost"]
            center = float(row.log_mbh_msun_std) + offset
            raw = float(models.required_fedd_for_seed(
                seed, center, eps, start, row.redshift, boost, clip_nonnegative=False))
            values = models.required_fedd_for_seed(seed, draws + offset, eps, start, row.redshift, boost)
            p16, p50, p84 = np.quantile(values, [.16, .5, .84]) if has_error else (np.nan,) * 3
            status = ("seed_exceeds_target" if raw < 0 else
                      "requires_mean_above_one" if raw > 1 else "within_zero_to_one")
            comparison_rows.append(dict(
                **base, scenario=name, cosmology=config["comparison_cosmology"], **parameters,
                required_fedd=max(0.0, raw), required_fedd_p16=p16, required_fedd_p50=p50,
                required_fedd_p84=p84, prob_required_fedd_gt_1=float(np.mean(values > 1)) if has_error else np.nan,
                fraction_mass_draws_within_eddington_cap=(
                    float(np.mean((draws + offset >= seed) & (values <= 1))) if has_error else np.nan),
                central_status=status,
            ))
        mass_quantiles = np.quantile(draws, [.16, .5, .84]) if has_error else np.full(3, np.nan)
        for onset, eps, cap, offset in minimum_grid:
            delta_t = float(pbh.growth_interval_gyr(onset, row.redshift))
            gain = float(models.growth_log10_factor(cap, eps, delta_t))
            p16, p50, p84 = mass_quantiles + offset - gain
            minimum_rows.append(dict(
                **base, cosmology=settings["cosmology"], z_accretion=onset, epsilon=eps,
                fedd_cap=cap, mass_offset_dex=offset, merger_boost=settings["merger_boost"],
                growth_time_gyr=delta_t, log10_minimum_seed_central=float(row.log_mbh_msun_std) + offset - gain,
                log10_minimum_seed_p16=p16, log10_minimum_seed_p50=p50, log10_minimum_seed_p84=p84,
            ))
    return pd.DataFrame(comparison_rows), pd.DataFrame(minimum_rows)


def build_outputs(measurements, objects, point, uncertainty, *, root=ROOT,
                  n_samples=DEFAULT_N_SAMPLES, random_seed=DEFAULT_RANDOM_SEED):
    """Build all four tables without reading existing result files."""
    if type(n_samples) is not int or n_samples < 1 or type(random_seed) is not int or random_seed < 0:
        raise ValueError("Require positive integer n_samples and nonnegative integer random_seed")
    config = load_config(root)
    eligible = objects.loc[objects.growth_ranking_eligible_flag.map(_boolish)].copy()
    if not objects.physical_object_id.is_unique or not measurements.measurement_id.is_unique:
        raise ValueError("Catalogue product inputs must have unique object and measurement IDs")
    keys = ["physical_object_id", "measurement_id"]
    expected = set(map(tuple, eligible[keys].to_numpy()))
    for frame in (point, uncertainty):
        if (frame.duplicated(keys).any() or frame.physical_object_id.duplicated().any()
                or set(map(tuple, frame[keys].to_numpy())) != expected):
            raise ValueError("Science inputs must match eligible preferred measurements exactly")
    if not uncertainty.n_samples.eq(n_samples).all() or not uncertainty.random_seed.eq(random_seed).all():
        raise ValueError("Mass draws must use the same sample count and seed as the uncertainty table")
    membership = build_publication_membership(root, measurements=measurements, objects=objects)
    comparison, minimum = build_growth_comparisons(eligible, membership, config, n_samples, random_seed)
    return dict(object_results=build_object_results(objects, point, uncertainty, membership, config["reference"]),
                growth_assumption_comparison=comparison,
                field_availability=build_field_availability(measurements, objects), minimum_seed_mass=minimum)
