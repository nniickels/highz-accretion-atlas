"""Science workflow for the v5 BLAGN measurement-version release.

v5 inherits the verified v4 mathematics and scenario definitions. Harikane
et al. (2023) rows receive the baseline and global +/-0.3 dex comparison
scenarios only because that source does not publish a numeric virial
calibration systematic. Statistical errors remain sampled separately.
"""

from __future__ import annotations

import pandas as pd

from src import v4_science as v4
from src.v5_catalogue import CATALOGUE_RELEASE, HARIKANE_SOURCE_KEY
from src.object_taxonomy import TAXONOMY_FIELDS, validate_taxonomy


Z_SEED = v4.Z_SEED
EPSILON = v4.EPSILON
MERGER_BOOST = v4.MERGER_BOOST
DEFAULT_RANDOM_SEED = v4.DEFAULT_RANDOM_SEED
DEFAULT_N_SAMPLES = v4.DEFAULT_N_SAMPLES

SCIENCE_TAXONOMY_FIELDS = [
    *TAXONOMY_FIELDS,
    "preferred_measurement_phenotype_tags",
    "all_measurements_phenotype_tags",
    "phenotype_evidence_measurement_ids",
    "phenotype_evidence_source_keys",
    "preferred_measurement_evidence_status",
    "preferred_measurement_evidence_status_basis",
    "all_measurements_evidence_status",
    "all_measurements_evidence_status_basis",
    "evidence_status_measurement_ids",
    "evidence_status_source_keys",
]


def _release(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    if "catalogue_release" in result:
        result["catalogue_release"] = CATALOGUE_RELEASE
    if "input_catalogue_release" in result:
        result["input_catalogue_release"] = CATALOGUE_RELEASE
    return result


def _boolish(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _require_growth_eligible(catalogue: pd.DataFrame) -> None:
    eligible = catalogue["growth_ranking_eligible_flag"].map(_boolish)
    if not eligible.all():
        ids = catalogue.loc[~eligible, "ranking_id"].astype(str).tolist()
        raise ValueError(
            "Growth workflow received ineligible catalogue rows; filter or review them "
            f"before ranking: {ids}"
        )


def _attach_taxonomy(frame: pd.DataFrame, catalogue: pd.DataFrame) -> pd.DataFrame:
    fields = [field for field in SCIENCE_TAXONOMY_FIELDS if field in catalogue]
    existing = [field for field in fields if field in frame]
    result = frame.drop(columns=existing, errors="ignore")
    metadata = catalogue[["ranking_id", *fields]].drop_duplicates("ranking_id")
    return result.merge(metadata, on="ranking_id", how="left", validate="many_to_one")


def _taxonomy_strata(frame: pd.DataFrame):
    for field, stratum_type in [
        ("object_class", "object_class"),
        ("evidence_status", "evidence_status"),
        ("spectroscopic_type", "spectroscopic_type"),
        ("growth_ranking_eligible_flag", "growth_ranking_eligibility"),
        ("primary_growth_ranking_flag", "primary_growth_ranking_population"),
    ]:
        values = frame[field].map(
            lambda value: str(_boolish(value)).lower()
            if field in {"growth_ranking_eligible_flag", "primary_growth_ranking_flag"}
            else ("not_reported" if pd.isna(value) else str(value))
        )
        for value in sorted(values.unique()):
            yield stratum_type, value, frame[values.eq(value)]


def _catalogue_taxonomy_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    view = str(frame["catalogue_view"].iloc[0])
    for stratum_type, value, group in _taxonomy_strata(frame):
        preferred_lrd = group.get("preferred_measurement_lrd_flag", group["lrd_flag"]).map(_boolish)
        any_lrd = group.get("lrd_reported_by_any_measurement", group["lrd_flag"]).map(_boolish)
        n_lrd = int(group["lrd_status"].eq("lrd").sum())
        n_non_lrd = int(group["lrd_status"].eq("non_lrd").sum())
        rows.append({
            "catalogue_release": CATALOGUE_RELEASE,
            "input_catalogue_release": CATALOGUE_RELEASE,
            "catalogue_view": view,
            "stratum_type": stratum_type,
            "stratum_value": value,
            "n_rows": len(group),
            "n_measurements_represented": (
                int(group["n_measurements"].sum()) if view == "physical_object" else len(group)
            ),
            "n_physical_objects": group["physical_object_id"].nunique(),
            "redshift_min": group["redshift"].min(),
            "redshift_max": group["redshift"].max(),
            "log_mbh_min": group["log_mbh_msun_std"].min(),
            "log_mbh_median": group["log_mbh_msun_std"].median(),
            "log_mbh_max": group["log_mbh_msun_std"].max(),
            "n_lrd": n_lrd,
            "n_non_lrd": n_non_lrd,
            "n_lrd_not_reported": int(group["lrd_status"].eq("not_reported_by_source").sum()),
            "stratum_identity_basis": (
                "measurement-row metadata" if view == "measurement"
                else "preferred-measurement taxonomy; phenotype tags union linked measurements"
            ),
            "demographic_inference_allowed": False,
            "selection_function_note": "descriptive taxonomy stratum only: no completeness correction or demographic pooling",
            "n_lrd_any_measurement": int(any_lrd.sum()),
            "n_lrd_preferred_measurement": int(preferred_lrd.sum()),
            "n_lrd_cross_source_only": int((any_lrd & ~preferred_lrd).sum()),
            "lrd_count_basis": (
                "measurement-row phenotype" if view == "measurement"
                else "any linked designation with missingness preserved; preferred attribution reported separately"
            ),
        })
    return pd.DataFrame(rows)


def _growth_taxonomy_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    view = str(frame["catalogue_view"].iloc[0])
    for stratum_type, value, group in _taxonomy_strata(frame):
        top = group.nsmallest(1, "rank_growth_pressure").iloc[0]
        rows.append({
            "catalogue_release": CATALOGUE_RELEASE,
            "input_catalogue_release": CATALOGUE_RELEASE,
            "catalogue_view": view,
            "stratum_type": stratum_type,
            "stratum_value": value,
            "n_rows": len(group),
            "n_high_pressure": int(group["physical_growth_pressure_tier"].eq("high").sum()),
            "n_medium_pressure": int(group["physical_growth_pressure_tier"].eq("medium").sum()),
            "n_low_pressure": int(group["physical_growth_pressure_tier"].eq("low").sum()),
            "median_required_fedd_seed1e2": group["req_fedd_seed1e2_z30_eps0p1_b1"].median(),
            "median_required_log_mseed_fedd0p3": group["req_log_mseed_fedd0p3_z30_eps0p1_b1"].median(),
            "top_ranking_id": top["ranking_id"],
            "top_object_id": top["object_id"],
            "top_growth_pressure_score": top["physical_pressure_score_0_100"],
            "demographic_inference_allowed": False,
            "selection_function_note": "descriptive taxonomy stratum only: no completeness correction or demographic pooling",
            "interpretation_note": (
                "Growth-pressure rankings are observational triage under stated assumptions; "
                "they do not identify or prove a black-hole seed channel."
            ),
        })
    return pd.DataFrame(rows)


def prepare_catalogue_view(catalogue: pd.DataFrame, *, view: str) -> pd.DataFrame:
    validate_taxonomy(catalogue)
    return _release(v4.prepare_catalogue_view(catalogue, view=view))


def evaluate_catalogue(catalogue: pd.DataFrame) -> pd.DataFrame:
    _require_growth_eligible(catalogue)
    return _attach_taxonomy(_release(v4.evaluate_catalogue(catalogue)), catalogue)


def build_point_ranking(catalogue: pd.DataFrame, evaluation: pd.DataFrame) -> pd.DataFrame:
    _require_growth_eligible(catalogue)
    result = _attach_taxonomy(_release(v4.build_point_ranking(catalogue, evaluation)), catalogue)
    harikane = result["source_key"].eq(HARIKANE_SOURCE_KEY)
    result.loc[harikane, "source_virial_sensitivity_note"] = (
        "Harikane statistical errors are propagated; no numeric virial-calibration "
        "systematic is published, so no source-specific scenario is inferred"
    )
    primary = result["primary_growth_ranking_flag"].map(_boolish)
    result["ranking_population"] = "exploratory_candidate_or_disputed"
    result.loc[primary, "ranking_population"] = "primary_evidence_supported"
    result["rank_primary_growth_pressure"] = pd.Series(pd.NA, index=result.index, dtype="Int64")
    primary_order = result.loc[primary].sort_values("rank_growth_pressure").index
    result.loc[primary_order, "rank_primary_growth_pressure"] = range(1, len(primary_order) + 1)
    return result


def build_uncertainty_summaries(
    catalogue: pd.DataFrame, *, n_samples: int = DEFAULT_N_SAMPLES,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    _require_growth_eligible(catalogue)
    fedd, mseed = v4.build_uncertainty_summaries(
        catalogue, n_samples=n_samples, random_seed=random_seed,
    )
    return (
        _attach_taxonomy(_release(fedd), catalogue),
        _attach_taxonomy(_release(mseed), catalogue),
    )


def build_uncertainty_ranking(
    point_ranking: pd.DataFrame, fedd_summary: pd.DataFrame, mseed_summary: pd.DataFrame,
) -> pd.DataFrame:
    result = _release(v4.build_uncertainty_ranking(point_ranking, fedd_summary, mseed_summary))
    primary = result["primary_growth_ranking_flag"].map(_boolish)
    result["rank_primary_uncertainty_pressure"] = pd.Series(pd.NA, index=result.index, dtype="Int64")
    primary_order = result.loc[primary].sort_values("rank_uncertainty_pressure").index
    result.loc[primary_order, "rank_primary_uncertainty_pressure"] = range(1, len(primary_order) + 1)
    return result


def _summary_group(objects: pd.DataFrame, stratum_type: str, value: str) -> pd.DataFrame:
    group = objects
    if stratum_type == "source":
        group = group[group["source_key"].astype("string").fillna("not_reported").eq(value)]
    elif stratum_type == "survey":
        group = group[group["survey"].astype("string").fillna("not_reported").eq(value)]
    elif stratum_type == "field":
        group = group[group["field"].astype("string").fillna("not_reported").eq(value)]
    elif stratum_type == "survey_field":
        combined = (
            group["survey"].astype("string").fillna("not_reported") + "/"
            + group["field"].astype("string").fillna("not_reported")
        )
        group = group[combined.eq(value)]
    elif stratum_type == "lrd_phenotype":
        group = group[group["lrd_status"].astype("string").fillna("not_reported").eq(value)]
    return group


def _correct_object_lrd_counts(result: pd.DataFrame, objects: pd.DataFrame) -> pd.DataFrame:
    corrected = result.copy()
    object_rows = corrected["catalogue_view"].eq("physical_object")
    preferred_strata = {"source", "survey", "field", "survey_field"}
    for index, row in corrected[object_rows].iterrows():
        stratum_type = str(row["stratum_type"])
        group = _summary_group(objects, stratum_type, str(row["stratum_value"]))
        if stratum_type in preferred_strata:
            status = group["preferred_measurement_lrd_flag"]
            reported = status.notna()
            lrd = status.map(_boolish)
        else:
            reported = group["lrd_status"].ne("not_reported_by_source")
            lrd = group["lrd_status"].eq("lrd")
        corrected.loc[index, "n_lrd"] = int(lrd.sum())
        corrected.loc[index, "n_non_lrd"] = int((reported & ~lrd).sum())
        corrected.loc[index, "n_lrd_not_reported"] = int((~reported).sum())
    return corrected


def build_catalogue_summary(measurements: pd.DataFrame, objects: pd.DataFrame) -> pd.DataFrame:
    result = _correct_object_lrd_counts(
        _release(v4.build_catalogue_summary(measurements, objects)), objects,
    )
    result.loc[result["stratum_type"].eq("overall"), "selection_function_note"] = (
        "descriptive only: mixes JADES, CEERS/RUBIES, EIGER/FRESCO, ASPIRE, "
        "and Harikane NIRSpec selection functions"
    )
    additions = pd.concat(
        [_catalogue_taxonomy_summary(measurements), _catalogue_taxonomy_summary(objects)],
        ignore_index=True,
    )
    return pd.concat([result, additions.reindex(columns=result.columns)], ignore_index=True)


def build_growth_summary(
    measurement_ranking: pd.DataFrame, object_ranking: pd.DataFrame,
) -> pd.DataFrame:
    result = _release(v4.build_growth_summary(measurement_ranking, object_ranking))
    result.loc[result["stratum_type"].eq("overall"), "selection_function_note"] = (
        "descriptive only: mixes JADES, CEERS/RUBIES, EIGER/FRESCO, ASPIRE, "
        "and Harikane NIRSpec selection functions"
    )
    additions = pd.concat(
        [_growth_taxonomy_summary(measurement_ranking), _growth_taxonomy_summary(object_ranking)],
        ignore_index=True,
    )
    return pd.concat([result, additions.reindex(columns=result.columns)], ignore_index=True)


def build_alternate_measurement_sensitivity(
    measurements: pd.DataFrame, objects: pd.DataFrame, *,
    n_samples: int = DEFAULT_N_SAMPLES, random_seed: int = DEFAULT_RANDOM_SEED,
) -> pd.DataFrame:
    return _release(v4.build_alternate_measurement_sensitivity(
        measurements, objects, n_samples=n_samples, random_seed=random_seed,
    ))


def verify_v5_outputs(outputs: dict[str, pd.DataFrame], *, n_samples: int) -> dict[str, bool]:
    checks = {
        "measurement_count": len(outputs["measurement_point_ranking"]) == 106,
        "physical_object_count": len(outputs["object_point_ranking"]) == 99,
        "measurement_evaluation_count": len(outputs["measurement_evaluation"]) == 464,
        "object_evaluation_count": len(outputs["object_evaluation"]) == 439,
        "measurement_uncertainty_fedd_count": len(outputs["measurement_uncertainty_fedd"]) == 1392,
        "object_uncertainty_fedd_count": len(outputs["object_uncertainty_fedd"]) == 1317,
        "measurement_uncertainty_mseed_count": len(outputs["measurement_uncertainty_mseed"]) == 928,
        "object_uncertainty_mseed_count": len(outputs["object_uncertainty_mseed"]) == 878,
        "sample_count": outputs["measurement_uncertainty_fedd"]["n_samples"].eq(n_samples).all(),
        "alternate_measurement_sensitivity_count": len(outputs["alternate_measurement_sensitivity"]) == 7,
        "taxonomy_in_evaluations": all(
            set(TAXONOMY_FIELDS).issubset(outputs[name].columns)
            for name in ["measurement_evaluation", "object_evaluation"]
        ),
        "taxonomy_in_rankings": all(
            set(TAXONOMY_FIELDS).issubset(outputs[name].columns)
            for name in [
                "measurement_point_ranking", "object_point_ranking",
                "measurement_uncertainty_ranking", "object_uncertainty_ranking",
            ]
        ),
        "only_eligible_rows_ranked": all(
            outputs[name]["growth_ranking_eligible_flag"].map(_boolish).all()
            for name in ["measurement_point_ranking", "object_point_ranking"]
        ),
        "primary_measurement_count": int(
            outputs["measurement_point_ranking"]["primary_growth_ranking_flag"].map(_boolish).sum()
        ) == 105,
        "primary_object_count": int(
            outputs["object_point_ranking"]["primary_growth_ranking_flag"].map(_boolish).sum()
        ) == 98,
        "primary_object_ranks_contiguous": sorted(
            outputs["object_point_ranking"]["rank_primary_growth_pressure"].dropna().astype(int)
        ) == list(range(1, 99)),
        "release_metadata": all(
            frame["catalogue_release"].eq(CATALOGUE_RELEASE).all() for frame in outputs.values()
        ),
    }
    if not all(checks.values()):
        failed = [name for name, passed in checks.items() if not passed]
        raise ValueError(f"v5 output verification failed: {failed}")
    return checks
