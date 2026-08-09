"""Generate the v1 observational-atlas ranking table.

This script builds a one-row-per-measurement ranking product from the processed
v1 catalogue and existing v1 result CSVs. It intentionally writes only new CSV
tables in ``results/`` and does not touch exploratory figure outputs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

PROCESSED_PATH = REPO_ROOT / "data" / "processed" / "v1_processed.csv"
RESULTS_DIR = REPO_ROOT / "results"
REQUIRED_FEDD_PATH = RESULTS_DIR / "v1_required_fedd_by_seed_mass.csv"
REQUIRED_MSEED_PATH = RESULTS_DIR / "v1_required_mseed_by_growth_assumption.csv"
RANKING_PATH = RESULTS_DIR / "v1_object_ranking_table.csv"

BASELINE_INTERPRETATION = "baseline"
MBH_MINUS_INTERPRETATION = "mbh_minus_0p3dex"
MBH_PLUS_INTERPRETATION = "mbh_plus_0p3dex"
BASELINE_FEDD_CONFIG = "eps0p1_no_merger_boost"
BASELINE_MSEED_FEDD0P3_CONFIG = "fedd0p3_eps0p1_no_merger_boost"
BASELINE_MSEED_FEDD1_CONFIG = "fedd1_eps0p1_no_merger_boost"

EXPECTED_HIGH_LEVERAGE = {
    "GN-38509",
    "GS-20057765",
    "GS-20030333",
    "GS-164055",
    "GN-4685",
    "GN-954",
}


def require_columns(df: pd.DataFrame, path: Path, columns: set[str]) -> None:
    missing = columns - set(df.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")


def read_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    for path in [PROCESSED_PATH, REQUIRED_FEDD_PATH, REQUIRED_MSEED_PATH]:
        if not path.exists():
            raise FileNotFoundError(f"Required input does not exist: {path}")

    catalogue = pd.read_csv(PROCESSED_PATH)
    required_fedd = pd.read_csv(REQUIRED_FEDD_PATH)
    required_mseed = pd.read_csv(REQUIRED_MSEED_PATH)

    require_columns(
        catalogue,
        PROCESSED_PATH,
        {
            "measurement_id",
            "object_id",
            "redshift",
            "cosmic_time_gyr",
            "survey",
            "object_class",
            "quality_flag",
            "source_key",
            "source_table",
            "log_mbh_msun_std",
            "log_mbh_err_plus_std",
            "log_mbh_err_minus_std",
            "mbh_method",
            "log_mstar_msun_std",
            "log_mstar_err_plus_std",
            "log_mstar_err_minus_std",
            "mstar_method",
            "edd_ratio_std",
            "log_mbh_mstar_ratio",
            "missing_mstar_flag",
            "missing_lbol_flag",
            "missing_edd_ratio_flag",
            "missing_lensing_flag",
            "agn_contam_flag",
            "notes",
        },
    )
    require_columns(
        required_fedd,
        REQUIRED_FEDD_PATH,
        {
            "measurement_id",
            "interpretation_variant",
            "fedd_requirement_config",
            "seed_mass_assumption",
            "delta_t_gyr",
            "required_fedd",
        },
    )
    require_columns(
        required_mseed,
        REQUIRED_MSEED_PATH,
        {
            "measurement_id",
            "interpretation_variant",
            "growth_config",
            "required_log_mseed",
            "required_mseed_msun",
        },
    )

    if not catalogue["measurement_id"].is_unique:
        duplicates = catalogue.loc[catalogue["measurement_id"].duplicated(), "measurement_id"].tolist()
        raise ValueError(f"Processed catalogue measurement_id values are not unique: {duplicates}")

    return catalogue, required_fedd, required_mseed


def pivot_required_fedd(required_fedd: pd.DataFrame) -> pd.DataFrame:
    baseline = required_fedd[
        (required_fedd["interpretation_variant"] == BASELINE_INTERPRETATION)
        & (required_fedd["fedd_requirement_config"] == BASELINE_FEDD_CONFIG)
        & (required_fedd["seed_mass_assumption"].isin(["seed_1e2_msun", "seed_1e4_msun", "seed_1e5_msun"]))
    ]
    baseline_pivot = baseline.pivot(
        index="measurement_id",
        columns="seed_mass_assumption",
        values="required_fedd",
    ).rename(
        columns={
            "seed_1e2_msun": "req_fedd_seed1e2_z30_eps0p1_b1",
            "seed_1e4_msun": "req_fedd_seed1e4_z30_eps0p1_b1",
            "seed_1e5_msun": "req_fedd_seed1e5_z30_eps0p1_b1",
        }
    )

    delta_t = (
        baseline[["measurement_id", "delta_t_gyr"]]
        .drop_duplicates(subset=["measurement_id"])
        .set_index("measurement_id")
        .rename(columns={"delta_t_gyr": "delta_t_z30_gyr"})
    )

    systematic = required_fedd[
        (required_fedd["interpretation_variant"].isin([MBH_MINUS_INTERPRETATION, MBH_PLUS_INTERPRETATION]))
        & (required_fedd["fedd_requirement_config"] == BASELINE_FEDD_CONFIG)
        & (required_fedd["seed_mass_assumption"] == "seed_1e2_msun")
    ]
    systematic_pivot = systematic.pivot(
        index="measurement_id",
        columns="interpretation_variant",
        values="required_fedd",
    ).rename(
        columns={
            MBH_MINUS_INTERPRETATION: "req_fedd_seed1e2_mbh_minus0p3",
            MBH_PLUS_INTERPRETATION: "req_fedd_seed1e2_mbh_plus0p3",
        }
    )

    return pd.concat([delta_t, baseline_pivot, systematic_pivot], axis=1).reset_index()


def pivot_required_mseed(required_mseed: pd.DataFrame) -> pd.DataFrame:
    baseline = required_mseed[
        (required_mseed["interpretation_variant"] == BASELINE_INTERPRETATION)
        & (required_mseed["growth_config"].isin([BASELINE_MSEED_FEDD0P3_CONFIG, BASELINE_MSEED_FEDD1_CONFIG]))
    ]
    baseline_log = baseline.pivot(
        index="measurement_id",
        columns="growth_config",
        values="required_log_mseed",
    ).rename(
        columns={
            BASELINE_MSEED_FEDD0P3_CONFIG: "req_log_mseed_fedd0p3_z30_eps0p1_b1",
            BASELINE_MSEED_FEDD1_CONFIG: "req_log_mseed_fedd1_z30_eps0p1_b1",
        }
    )
    baseline_linear = baseline.pivot(
        index="measurement_id",
        columns="growth_config",
        values="required_mseed_msun",
    ).rename(
        columns={
            BASELINE_MSEED_FEDD0P3_CONFIG: "req_mseed_fedd0p3_msun",
            BASELINE_MSEED_FEDD1_CONFIG: "req_mseed_fedd1_msun",
        }
    )

    systematic = required_mseed[
        (required_mseed["interpretation_variant"].isin([MBH_MINUS_INTERPRETATION, MBH_PLUS_INTERPRETATION]))
        & (required_mseed["growth_config"] == BASELINE_MSEED_FEDD0P3_CONFIG)
    ]
    systematic_pivot = systematic.pivot(
        index="measurement_id",
        columns="interpretation_variant",
        values="required_log_mseed",
    ).rename(
        columns={
            MBH_MINUS_INTERPRETATION: "req_log_mseed_fedd0p3_mbh_minus0p3",
            MBH_PLUS_INTERPRETATION: "req_log_mseed_fedd0p3_mbh_plus0p3",
        }
    )

    return pd.concat([baseline_log, baseline_linear, systematic_pivot], axis=1).reset_index()


def fedd_label(value: float) -> str:
    if pd.isna(value):
        return "not_available"
    if value < 0.3:
        return "sub_eddington"
    if value <= 1.0:
        return "eddington_like"
    if value <= 2.0:
        return "super_eddington"
    return "extreme"


def seed_label(value: float) -> str:
    if pd.isna(value):
        return "not_available"
    if value < 1.0:
        return "below_light_seed_scale"
    if value <= 2.0:
        return "light_seed_scale"
    if value < 4.0:
        return "intermediate_seed_scale"
    if value <= 6.0:
        return "heavy_seed_scale"
    return "above_heavy_seed_scale"


def mbh_mstar_tension_label(value: float) -> str:
    if pd.isna(value):
        return "not_available"
    if value < -2.0:
        return "low_or_typical"
    if value < -1.0:
        return "elevated"
    return "extreme"


def bool_value(value: object) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return bool(value)


def physical_growth_pressure_tier(row: pd.Series) -> str:
    req_fedd_1e2 = row["req_fedd_seed1e2_z30_eps0p1_b1"]
    req_fedd_1e4 = row["req_fedd_seed1e4_z30_eps0p1_b1"]
    req_mseed_0p3 = row["req_log_mseed_fedd0p3_z30_eps0p1_b1"]
    redshift = row["redshift"]

    high = (
        req_fedd_1e2 > 1.0
        or req_mseed_0p3 > 6.0
        or (req_fedd_1e4 > 0.8 and redshift > 7.0)
    )
    if high:
        return "high"

    medium = (
        0.7 < req_fedd_1e2 <= 1.0
        or 5.0 < req_mseed_0p3 <= 6.0
        or (redshift > 7.0 and req_fedd_1e2 > 0.8)
    )
    return "medium" if medium else "low"


def physical_pressure_score(row: pd.Series) -> float:
    light_seed = np.clip((row["req_fedd_seed1e2_z30_eps0p1_b1"] - 0.3) / 1.2, 0.0, 1.0)
    heavy_seed = np.clip((row["req_log_mseed_fedd0p3_z30_eps0p1_b1"] - 4.0) / 2.8, 0.0, 1.0)
    intermediate_seed = np.clip((row["req_fedd_seed1e4_z30_eps0p1_b1"] - 0.3) / 0.7, 0.0, 1.0)
    timing_bonus = np.clip((row["redshift"] - 6.0) / 4.0, 0.0, 1.0) * 8.0
    return float(np.clip(100.0 * max(light_seed, heavy_seed, intermediate_seed) + timing_bonus, 0.0, 100.0))


def growth_pressure_robustness_label(row: pd.Series) -> str:
    baseline_high = row["physical_growth_pressure_tier"] == "high"
    down_high = bool(row["light_seed_superedd_robust_mbh_minus0p3"]) or bool(
        row["gentle_growth_above_heavy_robust_mbh_minus0p3"]
    )
    plus_high = (
        row["req_fedd_seed1e2_mbh_plus0p3"] > 1.0
        or row["req_log_mseed_fedd0p3_mbh_plus0p3"] > 6.0
    )

    if baseline_high and down_high:
        return "robust_high"
    if baseline_high:
        return "baseline_high_only"
    if plus_high:
        return "systematics_sensitive"
    return "low"


def measurement_confidence_tier(row: pd.Series) -> str:
    quality = str(row["quality_flag"]).lower()
    missing_core = bool_value(row["missing_lbol_flag"]) or bool_value(row["missing_edd_ratio_flag"])
    if quality == "robust" and not missing_core:
        return "high"
    if quality == "robust":
        return "medium"
    if bool_value(row["missing_mstar_flag"]):
        return "low"
    return "medium"


def measurement_confidence_score(tier: str) -> int:
    return {"high": 90, "medium": 60, "low": 35}.get(tier, 50)


def caveat_tags(row: pd.Series) -> str:
    tags: list[str] = ["single_source_measurement"]
    quality = str(row["quality_flag"]).lower()
    if quality and quality != "robust":
        tags.append(quality)
    if bool_value(row["missing_mstar_flag"]):
        tags.append("missing_mstar")
    if bool_value(row["missing_lbol_flag"]):
        tags.append("missing_lbol")
    if bool_value(row["missing_edd_ratio_flag"]):
        tags.append("missing_edd_ratio")
    if bool_value(row["missing_lensing_flag"]):
        tags.append("missing_lensing")
    if bool_value(row.get("agn_contam_flag")):
        tags.append("agn_contam_mstar")
    return ";".join(tags)


def primary_caveat(row: pd.Series) -> str:
    if str(row["quality_flag"]).lower() != "robust":
        return "tentative source-paper classification"
    if bool_value(row["missing_mstar_flag"]):
        return "host stellar mass unavailable"
    if bool_value(row["missing_lbol_flag"]):
        return "bolometric luminosity unavailable"
    if bool_value(row["missing_edd_ratio_flag"]):
        return "reported Eddington ratio unavailable"
    return "single-source v1 measurement"


def most_needed_followup(row: pd.Series) -> str:
    if str(row["quality_flag"]).lower() != "robust":
        return "confirm broad-line/BH interpretation and refine virial mass"
    if bool_value(row["missing_mstar_flag"]):
        return "deeper host SED decomposition for stellar mass"
    if row["mbh_mstar_tension_label"] == "extreme":
        return "improved AGN-host decomposition and independent host mass"
    if row["physical_growth_pressure_tier"] == "high":
        return "independent BH-mass check and accretion-history constraints"
    return "use as robust comparison anchor in expanded atlas"


def followup_priority_category(row: pd.Series) -> str:
    if row["physical_growth_pressure_tier"] == "high" and str(row["quality_flag"]).lower() == "robust":
        return "A_robust_high_pressure"
    if row["physical_growth_pressure_tier"] == "high":
        return "B_tentative_high_pressure"
    if row["mbh_mstar_tension_label"] == "extreme":
        return "C_host_ratio_tension"
    if row["growth_pressure_robustness_label"] in {"baseline_high_only", "systematics_sensitive"}:
        return "D_systematics_leverage"
    if row["physical_growth_pressure_tier"] == "medium" and str(row["quality_flag"]).lower() == "robust":
        return "E_comparison_anchor"
    return "F_context"


def followup_priority_reason(row: pd.Series) -> str:
    object_id = row["object_id"]
    tier = row["physical_growth_pressure_tier"]
    req_fedd = row["req_fedd_seed1e2_z30_eps0p1_b1"]
    req_seed = row["req_log_mseed_fedd0p3_z30_eps0p1_b1"]
    caveat = row["primary_caveat"]

    if row["followup_priority_category"] == "A_robust_high_pressure":
        return (
            f"{object_id} is robust and high growth pressure under baseline assumptions: "
            f"light-seed required lifetime-average f_Edd={req_fedd:.3f}, "
            f"gentle-growth required log M_seed={req_seed:.3f}."
        )
    if row["followup_priority_category"] == "B_tentative_high_pressure":
        return (
            f"{object_id} is high growth pressure but measurement-sensitive ({caveat}): "
            f"light-seed required lifetime-average f_Edd={req_fedd:.3f}, "
            f"gentle-growth required log M_seed={req_seed:.3f}."
        )
    if row["followup_priority_category"] == "C_host_ratio_tension":
        return (
            f"{object_id} has extreme M_BH/Mstar tension "
            f"(log ratio={row['log_mbh_mstar_ratio']:.2f}) and merits host-mass follow-up."
        )
    if row["followup_priority_category"] == "D_systematics_leverage":
        return f"{object_id} changes ranking tier under +/-0.3 dex BH-mass systematics."
    if row["followup_priority_category"] == "E_comparison_anchor":
        return f"{object_id} is a robust {tier}-pressure comparison anchor for the high-leverage cases."
    return f"{object_id} is retained for atlas completeness; v1 growth-pressure tier is {tier}."


def followup_value_score(row: pd.Series) -> float:
    base = {
        "A_robust_high_pressure": 100.0,
        "B_tentative_high_pressure": 92.0,
        "C_host_ratio_tension": 78.0,
        "D_systematics_leverage": 70.0,
        "E_comparison_anchor": 58.0,
        "F_context": 30.0,
    }[row["followup_priority_category"]]
    return float(min(100.0, base + 0.05 * row["physical_pressure_score_0_100"]))


def ranking_note(row: pd.Series) -> str:
    return (
        f"{row['physical_growth_pressure_tier']} growth pressure; "
        f"{row['measurement_confidence_tier']} measurement confidence; "
        f"{row['mbh_mstar_tension_label']} MBH/Mstar tension."
    )


def build_ranking_table(catalogue: pd.DataFrame, required_fedd: pd.DataFrame, required_mseed: pd.DataFrame) -> pd.DataFrame:
    fedd_metrics = pivot_required_fedd(required_fedd)
    mseed_metrics = pivot_required_mseed(required_mseed)

    ranking = catalogue.merge(fedd_metrics, on="measurement_id", how="left", validate="one_to_one")
    ranking = ranking.merge(mseed_metrics, on="measurement_id", how="left", validate="one_to_one")

    ranking = ranking.rename(
        columns={
            "log_mbh_msun_std": "log_mbh_msun",
            "log_mbh_err_plus_std": "log_mbh_err_plus",
            "log_mbh_err_minus_std": "log_mbh_err_minus",
            "log_mstar_msun_std": "log_mstar_msun",
            "log_mstar_err_plus_std": "log_mstar_err_plus",
            "log_mstar_err_minus_std": "log_mstar_err_minus",
            "edd_ratio_std": "edd_ratio_reported",
        }
    )
    ranking["physical_object_id"] = ranking["object_id"]
    ranking["mbh_mstar_ratio"] = np.power(10.0, ranking["log_mbh_mstar_ratio"])
    ranking["mbh_mstar_tension_label"] = ranking["log_mbh_mstar_ratio"].map(mbh_mstar_tension_label)

    for seed in ["1e2", "1e4", "1e5"]:
        col = f"req_fedd_seed{seed}_z30_eps0p1_b1"
        ranking[f"req_fedd_seed{seed}_label"] = ranking[col].map(fedd_label)

    ranking["req_mseed_fedd0p3_label"] = ranking["req_log_mseed_fedd0p3_z30_eps0p1_b1"].map(seed_label)
    ranking["req_mseed_fedd1_label"] = ranking["req_log_mseed_fedd1_z30_eps0p1_b1"].map(seed_label)
    ranking["light_seed_superedd_robust_mbh_minus0p3"] = ranking["req_fedd_seed1e2_mbh_minus0p3"] > 1.0
    ranking["gentle_growth_above_heavy_robust_mbh_minus0p3"] = (
        ranking["req_log_mseed_fedd0p3_mbh_minus0p3"] > 6.0
    )
    ranking["physical_growth_pressure_tier"] = ranking.apply(physical_growth_pressure_tier, axis=1)
    ranking["physical_pressure_score_0_100"] = ranking.apply(physical_pressure_score, axis=1)
    ranking["growth_pressure_robustness_label"] = ranking.apply(growth_pressure_robustness_label, axis=1)
    ranking["measurement_confidence_tier"] = ranking.apply(measurement_confidence_tier, axis=1)
    ranking["measurement_confidence_score_0_100"] = ranking["measurement_confidence_tier"].map(measurement_confidence_score)
    ranking["caveat_tags"] = ranking.apply(caveat_tags, axis=1)
    ranking["primary_caveat"] = ranking.apply(primary_caveat, axis=1)
    ranking["most_needed_followup"] = ranking.apply(most_needed_followup, axis=1)
    ranking["followup_priority_category"] = ranking.apply(followup_priority_category, axis=1)
    ranking["followup_priority_reason"] = ranking.apply(followup_priority_reason, axis=1)
    ranking["followup_value_score_0_100"] = ranking.apply(followup_value_score, axis=1)
    ranking["ranking_note"] = ranking.apply(ranking_note, axis=1)

    ranking = ranking.sort_values(
        ["physical_pressure_score_0_100", "redshift", "log_mbh_msun"],
        ascending=[False, False, False],
    ).reset_index(drop=True)
    ranking["rank_physical_pressure"] = np.arange(1, len(ranking) + 1)

    followup_order = ranking.sort_values(
        ["followup_value_score_0_100", "physical_pressure_score_0_100", "redshift"],
        ascending=[False, False, False],
    ).reset_index()
    ranking.loc[followup_order["index"], "rank_followup_priority"] = np.arange(1, len(ranking) + 1)
    ranking["rank_followup_priority"] = ranking["rank_followup_priority"].astype(int)

    ordered_columns = [
        "rank_physical_pressure",
        "rank_followup_priority",
        "measurement_id",
        "physical_object_id",
        "object_id",
        "redshift",
        "cosmic_time_gyr",
        "delta_t_z30_gyr",
        "survey",
        "object_class",
        "quality_flag",
        "source_key",
        "source_table",
        "log_mbh_msun",
        "log_mbh_err_plus",
        "log_mbh_err_minus",
        "mbh_method",
        "log_mstar_msun",
        "log_mstar_err_plus",
        "log_mstar_err_minus",
        "mstar_method",
        "edd_ratio_reported",
        "log_mbh_mstar_ratio",
        "mbh_mstar_ratio",
        "mbh_mstar_tension_label",
        "missing_mstar_flag",
        "missing_lbol_flag",
        "missing_edd_ratio_flag",
        "missing_lensing_flag",
        "agn_contam_flag",
        "req_fedd_seed1e2_z30_eps0p1_b1",
        "req_fedd_seed1e4_z30_eps0p1_b1",
        "req_fedd_seed1e5_z30_eps0p1_b1",
        "req_fedd_seed1e2_label",
        "req_fedd_seed1e4_label",
        "req_fedd_seed1e5_label",
        "req_log_mseed_fedd0p3_z30_eps0p1_b1",
        "req_mseed_fedd0p3_msun",
        "req_mseed_fedd0p3_label",
        "req_log_mseed_fedd1_z30_eps0p1_b1",
        "req_mseed_fedd1_msun",
        "req_mseed_fedd1_label",
        "req_fedd_seed1e2_mbh_minus0p3",
        "req_fedd_seed1e2_mbh_plus0p3",
        "req_log_mseed_fedd0p3_mbh_minus0p3",
        "req_log_mseed_fedd0p3_mbh_plus0p3",
        "light_seed_superedd_robust_mbh_minus0p3",
        "gentle_growth_above_heavy_robust_mbh_minus0p3",
        "physical_growth_pressure_tier",
        "growth_pressure_robustness_label",
        "measurement_confidence_tier",
        "caveat_tags",
        "primary_caveat",
        "most_needed_followup",
        "followup_priority_category",
        "followup_priority_reason",
        "physical_pressure_score_0_100",
        "measurement_confidence_score_0_100",
        "followup_value_score_0_100",
        "ranking_note",
        "notes",
    ]
    return ranking[ordered_columns]


def verify_ranking(ranking: pd.DataFrame, catalogue: pd.DataFrame) -> None:
    print(f"Wrote ranking table: {RANKING_PATH.relative_to(REPO_ROOT)}")
    print(f"Row count: {len(ranking)} ranking rows; {len(catalogue)} processed catalogue rows")
    print(f"Unique measurement_id values: {ranking['measurement_id'].is_unique}")

    expected_missing = EXPECTED_HIGH_LEVERAGE - set(ranking["object_id"])
    top_objects = ranking.nsmallest(8, "rank_physical_pressure")[
        [
            "rank_physical_pressure",
            "object_id",
            "quality_flag",
            "physical_growth_pressure_tier",
            "req_fedd_seed1e2_z30_eps0p1_b1",
            "req_log_mseed_fedd0p3_z30_eps0p1_b1",
            "followup_priority_category",
        ]
    ]
    print("Top physical-pressure objects:")
    print(top_objects.to_string(index=False))

    top_set = set(ranking.nsmallest(8, "rank_physical_pressure")["object_id"])
    expected_in_top = EXPECTED_HIGH_LEVERAGE & top_set
    print(f"Expected high-leverage objects present: {sorted(EXPECTED_HIGH_LEVERAGE - expected_missing)}")
    print(f"Expected high-leverage objects in top 8 physical-pressure ranks: {sorted(expected_in_top)}")

    sanity_checks = {
        "row_count_matches_catalogue": len(ranking) == len(catalogue),
        "measurement_id_unique": ranking["measurement_id"].is_unique,
        "all_expected_high_leverage_present": not expected_missing,
        "gn38509_is_robust_high_pressure": bool(
            (
                (ranking["object_id"] == "GN-38509")
                & (ranking["quality_flag"] == "robust")
                & (ranking["physical_growth_pressure_tier"] == "high")
            ).any()
        ),
        "gs20057765_is_tentative_high_pressure": bool(
            (
                (ranking["object_id"] == "GS-20057765")
                & (ranking["quality_flag"] == "tentative")
                & (ranking["physical_growth_pressure_tier"] == "high")
            ).any()
        ),
        "missing_host_objects_retained": bool(
            ranking.loc[ranking["object_id"].isin(["GS-20030333", "GS-164055"]), "missing_mstar_flag"].all()
        ),
        "no_missing_baseline_required_fedd": not ranking["req_fedd_seed1e2_z30_eps0p1_b1"].isna().any(),
        "no_missing_baseline_required_mseed": not ranking["req_log_mseed_fedd0p3_z30_eps0p1_b1"].isna().any(),
    }
    print("Sanity checks:")
    for name, passed in sanity_checks.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")

    failed = [name for name, passed in sanity_checks.items() if not passed]
    if failed:
        raise AssertionError(f"Ranking verification failed: {failed}")


def main() -> None:
    catalogue, required_fedd, required_mseed = read_inputs()
    ranking = build_ranking_table(catalogue, required_fedd, required_mseed)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ranking.to_csv(RANKING_PATH, index=False)
    verify_ranking(ranking, catalogue)


if __name__ == "__main__":
    main()
