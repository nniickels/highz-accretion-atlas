"""Sensitivity to the published Baccus revision, without changing frozen membership.

Two scenarios replace the 44 exact-ID matches with published redshift, mass and
quoted errors. One retains the five unmatched frozen rows; the other omits them.
Neither scenario admits new objects or reclassifies evidence. This isolates
measurement-version sensitivity, not a complete re-admission of the publication.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.internal.compatibility import v7_science_core as core
from src.science import science_context, DEFAULT_N_SAMPLES, DEFAULT_RANDOM_SEED

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "baccus26_nirspec_blagn"
TABLE = ROOT / "data/validation/source_inputs/baccus_published_table1.txt"


def read_published_table(path: Path = TABLE) -> pd.DataFrame:
    """Parse publisher-documented fixed-width columns; fail on invalid data rows."""
    rows = []
    for line in path.read_text().splitlines():
        # Data IDs have the documented survey_program_object form.
        name = line[:21].strip()
        if len(name.split("_")) < 3 or not name.split("_")[-1].isdigit():
            continue
        rows.append({
            "object_id": name, "ra_deg": float(line[22:32]),
            "dec_deg": float(line[33:43]), "redshift": float(line[44:50]),
            "log_mbh_msun_std": float(line[66:70]),
            "log_mbh_err_plus_std": float(line[71:78]),
            "log_mbh_err_minus_std": float(line[79:85]),
            "log_lbol_erg_s_std": float(line[86:90]),
            "edd_ratio_std": float(line[107:113]),
        })
    result = pd.DataFrame(rows)
    if result.empty or result.object_id.duplicated().any():
        raise AssertionError("Published Baccus table has missing or duplicate IDs")
    return result.set_index("object_id")


def build_revision_outputs(objects: pd.DataFrame, *, n_samples: int = DEFAULT_N_SAMPLES,
                           random_seed: int = DEFAULT_RANDOM_SEED) -> dict[str, pd.DataFrame]:
    published = read_published_table()
    frozen = objects.loc[objects.source_key.eq(SOURCE)]
    revised = objects.copy()
    comparisons = []
    missing = set()
    fields = ["redshift", "log_mbh_msun_std", "log_mbh_err_plus_std", "log_mbh_err_minus_std"]
    for row in frozen.itertuples():
        record = {"measurement_id": row.measurement_id, "physical_object_id": row.physical_object_id,
                  "object_id": row.object_id, "match_status": "exact_id" if row.object_id in published.index else "absent_from_published_table"}
        for field in fields:
            record[f"frozen_{field}"] = getattr(row, field)
            record[f"published_{field}"] = np.nan
        if row.object_id in published.index:
            new = published.loc[row.object_id]
            separation = float(np.hypot((new.ra_deg-row.ra_deg)*np.cos(np.deg2rad(row.dec_deg)), new.dec_deg-row.dec_deg)*3600)
            if separation > 0.5:
                raise AssertionError(f"Baccus ID {row.object_id} moved {separation} arcsec; review identity before substitution")
            record["position_check_arcsec"] = separation
            for field in fields:
                record[f"published_{field}"] = new[field]
            mask = revised.measurement_id.eq(row.measurement_id)
            for field in fields + ["log_lbol_erg_s_std", "edd_ratio_std"]:
                revised.loc[mask, field] = new[field]
        else:
            # Record the nearest published counterpart; never force a loose match.
            sep = np.hypot((published.ra_deg-row.ra_deg)*np.cos(np.deg2rad(row.dec_deg)), published.dec_deg-row.dec_deg)*3600
            if sep.min() <= 0.5:
                raise AssertionError(f"Possible renamed Baccus counterpart for {row.object_id}; review explicitly")
            record["position_check_arcsec"] = float(sep.min())
            missing.add(row.measurement_id)
        comparisons.append(record)
    comparison = pd.DataFrame(comparisons).sort_values("measurement_id").reset_index(drop=True)
    summary, ranked = [], {}
    scenarios = {
        "frozen_v1_measurements": objects,
        "published_values_keep_unmatched": revised,
        "published_values_omit_unmatched": revised.loc[~revised.measurement_id.isin(missing)].copy(),
    }
    with science_context("v3"):
        for name, frame in scenarios.items():
            view = core.prepare_science_view(frame, view="physical_object")
            point = core.build_point_ranking(view)
            uncertainty = core.build_uncertainty_ranking(view, n_samples=n_samples, random_seed=random_seed)
            ranked[name] = (point.set_index("measurement_id"), uncertainty.set_index("measurement_id"))
            ordered = point.sort_values(["required_fedd_seed1e2", "ranking_id"], ascending=[False, True])
            summary.append({
                "scenario": name, "numerical_objects": len(point),
                "matched_baccus_objects": len(frozen)-len(missing), "unmatched_baccus_objects": len(missing),
                "point_required_fedd_gt_1": int(point.required_fedd_seed1e2.gt(1).sum()),
                "median_required_fedd_gt_1": int(uncertainty.required_fedd_seed1e2_p50.gt(1).sum()),
                "p16_required_fedd_gt_1": int(uncertainty.required_fedd_seed1e2_p16.gt(1).sum()),
                "p84_required_fedd_gt_1": int(uncertainty.required_fedd_seed1e2_p84.gt(1).sum()),
                "prob_required_fedd_gt_1_ge_095": int(uncertainty.prob_required_fedd_seed1e2_gt_1.ge(.95).sum()),
                "top5_required_fedd": ";".join(ordered.object_id.head(5)),
                "n_samples": n_samples, "random_seed": random_seed,
                "interpretation": "measurement-version sensitivity at fixed evidence/method taxonomy; not demographic inference",
            })
    for scenario in ["frozen_v1_measurements", "published_values_keep_unmatched"]:
        point, uncertainty = ranked[scenario]
        for column in ["required_fedd_seed1e2", "growth_pressure_tier", "rank_global_navigation"]:
            comparison[f"{scenario}_{column}"] = comparison.measurement_id.map(point[column])
        for column in ["prob_required_fedd_seed1e2_gt_1", "required_fedd_seed1e2_p16", "required_fedd_seed1e2_p84"]:
            comparison[f"{scenario}_{column}"] = comparison.measurement_id.map(uncertainty[column])
    comparison["delta_log_mbh_dex"] = comparison.published_log_mbh_msun_std-comparison.frozen_log_mbh_msun_std
    return {"baccus_revision_comparison": comparison, "baccus_revision_summary": pd.DataFrame(summary)}
