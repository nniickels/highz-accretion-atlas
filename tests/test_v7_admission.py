"""Synthetic tests for the heterogeneous v7 admission gate."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.v7_admission import (
    EVIDENCE_STATUSES,
    GROWTH_ELIGIBLE_REASON,
    OBJECT_CLASSES,
    PHENOTYPE_TAGS,
    PRIMARY_ELIGIBLE_REASON,
    SELECTION_CHANNELS,
    normalize_v7_vocabulary,
    validate_v7_admission,
    validate_v7_observables,
)


def _valid_admission_fixture() -> pd.DataFrame:
    common = {
        "identity_resolution_status": "resolved",
        "source_key": "synthetic_admission_fixture",
        "survey": "SYNTHETIC",
        "field": "TEST",
        "source_table": "Table 1",
        "source_paper_version": "synthetic fixture v1",
        "source_url": "https://example.test/source",
        "source_doi": "",
        "source_archive_url": "",
        "extraction_date": "2026-08-25",
        "selection_criteria": "host selected; broad Halpha fit passes synthetic thresholds",
        "source_caveat_tags": "synthetic_fixture",
        "object_class": "broad_line_agn",
        "spectroscopic_type": "type1_broad_line_candidate",
        "selection_channels": "host_selected;broad_halpha",
        "phenotype_tags": "merger;clumpy",
        "lensing_status": "not_reported",
        "lensing_mu": np.nan,
        "lensing_mass_correction_status": "not_required",
        "lensing_provenance": "",
        "mbh_method": "single-epoch-virial-halpha-example",
        "log_mbh_err_plus": 0.12,
        "log_mbh_err_minus": 0.10,
        "mbh_statistical_uncertainty_kind": "published_asymmetric_formal_posterior",
        "log_mbh_systematic_dex": 0.4,
        "mbh_systematic_kind": "single_epoch_virial_calibration",
        "mbh_systematic_applied_flag": False,
        "mass_comparability_group": "virial_balmer_single_epoch",
        "primary_mass_comparison_flag": True,
        "primary_mass_comparison_reason": "balmer_single_epoch_primary_stratum",
        "log_mstar_upper_limit_msun": np.nan,
        "log_lbol_erg_s_std": np.nan,
        "edd_ratio_std": np.nan,
        "growth_ranking_eligible_flag": True,
        "growth_ranking_eligibility_reason": GROWTH_ELIGIBLE_REASON,
    }
    rows = [
        {
            **common,
            "measurement_id": "ROBUST_source",
            "object_id": "ROBUST",
            "physical_object_id": "HZA-ROBUST",
            "host_system_id": "HZS-ROBUST",
            "redshift": 5.7,
            "evidence_status": "probable",
            "evidence_status_basis": "multiple_spatial_and_spectral_blr_diagnostics",
            "log_mbh_msun_std": 7.8,
            "conditional_mass_flag": False,
            "conditional_mass_reason": "",
            "log_mstar_msun_std": 10.3,
            "host_property_scope": "object_specific",
            "primary_growth_ranking_flag": True,
            "primary_growth_ranking_reason": PRIMARY_ELIGIBLE_REASON,
        },
        {
            **common,
            "measurement_id": "PAIR_A_source",
            "object_id": "PAIR_A",
            "physical_object_id": "HZA-PAIR-A",
            "host_system_id": "HZS-PAIR",
            "redshift": 5.3,
            "evidence_status": "candidate",
            "evidence_status_basis": "intermediate_width_component_may_be_outflow",
            "log_mbh_msun_std": 6.8,
            "conditional_mass_flag": True,
            "conditional_mass_reason": "mass_valid_only_if_broad_component_is_blr",
            "log_mstar_msun_std": 10.37,
            "host_property_scope": "shared_host_system_total",
            "primary_growth_ranking_flag": False,
            "primary_growth_ranking_reason": "candidate_evidence_excluded",
        },
        {
            **common,
            "measurement_id": "PAIR_B_source",
            "object_id": "PAIR_B",
            "physical_object_id": "HZA-PAIR-B",
            "host_system_id": "HZS-PAIR",
            "redshift": 5.3,
            "evidence_status": "candidate",
            "evidence_status_basis": "intermediate_width_component_may_be_outflow",
            "log_mbh_msun_std": 6.4,
            "conditional_mass_flag": True,
            "conditional_mass_reason": "mass_valid_only_if_broad_component_is_blr",
            "log_mstar_msun_std": 10.37,
            "host_property_scope": "shared_host_system_total",
            "primary_growth_ranking_flag": False,
            "primary_growth_ranking_reason": "candidate_evidence_excluded",
        },
    ]
    return pd.DataFrame(rows)


class V7AdmissionTests(unittest.TestCase):
    def test_valid_multinucleus_fixture_passes(self) -> None:
        frame = _valid_admission_fixture()
        validate_v7_admission(frame)
        self.assertEqual(frame["measurement_id"].nunique(), 3)
        self.assertEqual(frame["physical_object_id"].nunique(), 3)
        self.assertEqual(frame["host_system_id"].nunique(), 2)

    def test_frozen_vocabulary_translation_is_explicit_and_nonmutating(self) -> None:
        frozen = pd.DataFrame(
            {
                "object_class": ["broad-line-agn"],
                "evidence_status": ["probable_accreting_mbh"],
                "phenotype_tags": ["red_agn;compact_source"],
            }
        )
        translated = normalize_v7_vocabulary(frozen)
        self.assertEqual(translated.iloc[0]["object_class"], "broad_line_agn")
        self.assertEqual(translated.iloc[0]["evidence_status"], "probable")
        self.assertEqual(translated.iloc[0]["phenotype_tags"], "compact;red")
        self.assertEqual(frozen.iloc[0]["object_class"], "broad-line-agn")

    def test_all_frozen_v6_taxonomy_tokens_have_a_v7_path(self) -> None:
        frozen = pd.read_csv(ROOT / "data/processed/v6_blagn_measurements.csv")
        translated = normalize_v7_vocabulary(frozen)
        self.assertLessEqual(set(translated["object_class"]), OBJECT_CLASSES)
        self.assertLessEqual(set(translated["evidence_status"]), EVIDENCE_STATUSES)
        selections = {
            token
            for value in translated["selection_channels"].fillna("")
            for token in str(value).split(";") if token
        }
        phenotypes = {
            token
            for value in translated["phenotype_tags"].fillna("")
            for token in str(value).split(";") if token
        }
        self.assertLessEqual(selections, SELECTION_CHANNELS)
        self.assertLessEqual(phenotypes, PHENOTYPE_TAGS)

    def test_candidate_cannot_claim_primary_rank(self) -> None:
        frame = _valid_admission_fixture()
        frame.loc[1, "primary_growth_ranking_flag"] = True
        with self.assertRaisesRegex(ValueError, "Primary-ranking outcome/reason mismatch"):
            validate_v7_admission(frame)

    def test_exact_exclusion_reason_is_required(self) -> None:
        frame = _valid_admission_fixture()
        frame.loc[0, "identity_resolution_status"] = "unresolved"
        with self.assertRaisesRegex(ValueError, "Growth-ranking outcome/reason mismatch"):
            validate_v7_admission(frame)
        frame.loc[0, "growth_ranking_eligible_flag"] = False
        frame.loc[0, "growth_ranking_eligibility_reason"] = "unresolved_physical_identity"
        frame.loc[0, "primary_growth_ranking_flag"] = False
        frame.loc[0, "primary_growth_ranking_reason"] = "not_exploratory_eligible"
        validate_v7_admission(frame)

    def test_conditional_mass_requires_a_reason(self) -> None:
        frame = _valid_admission_fixture()
        frame.loc[1, "conditional_mass_reason"] = ""
        with self.assertRaisesRegex(ValueError, "Conditional masses require"):
            validate_v7_admission(frame)

    def test_shared_host_property_cannot_be_double_invented(self) -> None:
        frame = _valid_admission_fixture()
        frame.loc[2, "log_mstar_msun_std"] = 10.1
        with self.assertRaisesRegex(ValueError, "inconsistent log_mstar"):
            validate_v7_admission(frame)
        singleton = _valid_admission_fixture().iloc[[0]].copy()
        singleton.loc[:, "host_property_scope"] = "shared_host_system_total"
        with self.assertRaisesRegex(ValueError, "multiple physical objects"):
            validate_v7_admission(singleton)

    def test_unpublished_optional_diagnostics_do_not_block_growth_rank(self) -> None:
        frame = _valid_admission_fixture().iloc[[0]].copy()
        frame.loc[:, ["log_mstar_msun_std", "log_lbol_erg_s_std", "edd_ratio_std"]] = np.nan
        frame.loc[:, "host_property_scope"] = "not_published"
        validate_v7_admission(frame)
        self.assertTrue(bool(frame.iloc[0]["growth_ranking_eligible_flag"]))
        self.assertTrue(bool(frame.iloc[0]["primary_growth_ranking_flag"]))

    def test_mass_systematic_must_stay_separate(self) -> None:
        frame = _valid_admission_fixture()
        frame.loc[0, "mbh_systematic_applied_flag"] = True
        with self.assertRaisesRegex(ValueError, "systematics separate"):
            validate_v7_admission(frame)

    def test_lensing_and_controlled_values_are_enforced(self) -> None:
        frame = _valid_admission_fixture()
        frame.loc[0, "object_class"] = "lrd"
        with self.assertRaisesRegex(ValueError, "Invalid object_class"):
            validate_v7_admission(frame)
        frame = _valid_admission_fixture()
        frame.loc[0, "lensing_status"] = "lensed"
        frame.loc[0, "lensing_mass_correction_status"] = "applied"
        with self.assertRaisesRegex(ValueError, "numeric lensing_mu"):
            validate_v7_admission(frame)

    def test_observable_detections_and_limits_remain_distinct(self) -> None:
        observables = pd.DataFrame(
            [
                {
                    "observable_id": "ROBUST_halpha",
                    "measurement_id": "ROBUST_source",
                    "observable_name": "halpha_broad_flux",
                    "value": 11.7,
                    "err_plus": 1.4,
                    "err_minus": 1.4,
                    "censoring": "detection",
                    "unit": "1e-18 erg s-1 cm-2",
                    "uncertainty_kind": "published_symmetric_1sigma",
                    "source_location": "Table 1",
                },
                {
                    "observable_id": "ROBUST_nii",
                    "measurement_id": "ROBUST_source",
                    "observable_name": "nii6584_flux",
                    "value": 0.2,
                    "err_plus": np.nan,
                    "err_minus": np.nan,
                    "censoring": "upper_limit",
                    "unit": "1e-18 erg s-1 cm-2",
                    "uncertainty_kind": "limit",
                    "source_location": "Table 2",
                },
            ]
        )
        validate_v7_observables(observables, {"ROBUST_source"})
        observables.loc[1, "err_plus"] = 0.1
        with self.assertRaisesRegex(ValueError, "Censored limits"):
            validate_v7_observables(observables, {"ROBUST_source"})

    def test_frozen_release_manifests_still_match(self) -> None:
        manifests = [
            "v4.0.1-manifest.json", "v5-manifest.json", "v5-figures-manifest.json",
            "v6-manifest.json",
        ]
        checked = 0
        for name in manifests:
            manifest = json.loads((ROOT / "releases" / name).read_text())
            entries = manifest.get("artifacts", manifest.get("files", {}))
            pairs = entries.items() if isinstance(entries, dict) else (
                (entry["path"], entry["sha256"]) for entry in entries
            )
            for path_value, digest in pairs:
                actual = hashlib.sha256((ROOT / path_value).read_bytes()).hexdigest()
                self.assertEqual(actual, digest, f"{name}: {path_value}")
                checked += 1
        self.assertGreater(checked, 50)


if __name__ == "__main__":
    unittest.main()
