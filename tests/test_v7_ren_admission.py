"""Source-specific admission tests for Ren et al. ALPINE--CRISTAL--JWST."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.identity import angular_separation_arcsec
from src.v7_ren import (
    MASS_METHOD,
    PAPER_VERSION,
    SOURCE_DOI,
    SOURCE_KEY,
    SOURCE_ARCHIVE_SHA256,
    build_ren_admission,
    build_ren_observables,
    v6_identity_candidates,
)


class RenV7AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.table1 = pd.read_csv(ROOT / "data/raw/ren25_alpine_cristal_jwst_table1.csv")
        cls.table2 = pd.read_csv(
            ROOT / "data/raw/ren25_alpine_cristal_jwst_table2_observables.csv"
        )
        cls.admission = build_ren_admission(cls.table1)
        cls.observables = build_ren_observables(
            cls.table2, cls.admission[["measurement_id", "object_id"]],
        )

    def test_authoritative_table_membership_and_counts(self) -> None:
        expected = {
            "DC_417567", "DC_519281", "DC_536534", "DC_683613",
            "DC_848185_a", "DC_848185_b", "DC_873321",
        }
        self.assertEqual(len(self.table1), 7)
        self.assertEqual(set(self.table1["object_id"]), expected)
        self.assertEqual(len(self.table2), 70)
        self.assertEqual(self.table2.groupby("measurement_id").size().unique().tolist(), [10])
        self.assertEqual(int(self.table2["censoring"].eq("upper_limit").sum()), 12)
        self.assertEqual(int(self.table2["censoring"].eq("detection").sum()), 58)

    def test_published_table1_anchors_are_preserved(self) -> None:
        indexed = self.table1.set_index("object_id")
        robust = indexed.loc["DC_536534"]
        self.assertEqual(robust["halpha_broad_flux_dustcorr_1e18"], 11.69)
        self.assertEqual(robust["halpha_broad_fwhm_instrumentcorr_km_s"], 2812)
        self.assertEqual(robust["log_mbh_msun"], 7.78)
        self.assertEqual(robust["log_lbol_erg_s"], 44.88)
        marginal = indexed.loc["DC_417567"]
        self.assertEqual(marginal["halpha_broad_fwhm_instrumentcorr_km_s"], 596)
        self.assertEqual(marginal["log_mbh_msun"], 6.00)
        self.assertTrue(self.table1["redshift"].gt(5).all())

    def test_table2_detections_and_limits_are_source_native(self) -> None:
        indexed = self.observables.set_index("observable_id")
        heii = indexed.loc["DC536534_heii4687"]
        self.assertEqual(heii["censoring"], "detection")
        self.assertEqual(heii["value"], 0.18)
        self.assertEqual(heii["err_plus"], 0.05)
        limit = indexed.loc["DC683613_hgamma"]
        self.assertEqual(limit["censoring"], "upper_limit")
        self.assertEqual(limit["value"], 0.30)
        self.assertTrue(pd.isna(limit["err_plus"]))
        self.assertTrue(pd.isna(limit["err_minus"]))

    def test_table2_measurement_object_mapping_is_exact(self) -> None:
        broken = self.table2.copy()
        left = broken.index[broken["object_id"].eq("DC_417567")][0]
        right = broken.index[broken["object_id"].eq("DC_519281")][0]
        broken.loc[left, "measurement_id"], broken.loc[right, "measurement_id"] = (
            broken.loc[right, "measurement_id"], broken.loc[left, "measurement_id"],
        )
        with self.assertRaisesRegex(ValueError, "mapping does not match Table 1"):
            build_ren_observables(
                broken, self.admission[["measurement_id", "object_id"]],
            )

    def test_measurement_object_and_host_system_cardinality(self) -> None:
        self.assertEqual(self.admission["measurement_id"].nunique(), 7)
        self.assertEqual(self.admission["physical_object_id"].nunique(), 7)
        self.assertEqual(self.admission["host_system_id"].nunique(), 6)
        pair = self.admission[self.admission["host_system_id"].eq("HZS-DC-848185")]
        self.assertEqual(len(pair), 2)
        self.assertEqual(pair["physical_object_id"].nunique(), 2)
        self.assertTrue(pair["host_property_scope"].eq("shared_host_system_total").all())
        self.assertTrue(pair["log_mstar_msun_std"].eq(10.37).all())
        separation = angular_separation_arcsec(
            pair.iloc[0]["ra_deg"], pair.iloc[0]["dec_deg"],
            pair.iloc[1]["ra_deg"], pair.iloc[1]["dec_deg"],
        )
        self.assertAlmostEqual(float(separation), 0.897, places=3)

    def test_evidence_and_conditional_mass_mapping(self) -> None:
        counts = self.admission["evidence_status"].value_counts().to_dict()
        self.assertEqual(counts, {"candidate": 6, "probable": 1})
        self.assertTrue(self.admission["growth_ranking_eligible_flag"].astype(bool).all())
        self.assertEqual(int(self.admission["primary_growth_ranking_flag"].sum()), 1)
        robust = self.admission.set_index("object_id").loc["DC_536534"]
        self.assertTrue(bool(robust["primary_growth_ranking_flag"]))
        self.assertFalse(bool(robust["conditional_mass_flag"]))
        candidates = self.admission[self.admission["evidence_status"].eq("candidate")]
        self.assertTrue(candidates["conditional_mass_flag"].astype(bool).all())
        self.assertTrue(
            candidates["conditional_mass_reason"].eq(
                "mass_valid_only_if_broad_component_is_blr"
            ).all()
        )

    def test_mass_luminosity_host_and_lrd_semantics(self) -> None:
        self.assertTrue(self.admission["mbh_method"].eq(MASS_METHOD).all())
        self.assertTrue(self.admission["mass_comparability_group"].eq(
            "virial_balmer_single_epoch"
        ).all())
        self.assertTrue(self.admission["log_mbh_systematic_dex"].eq(0.4).all())
        self.assertFalse(self.admission["mbh_systematic_applied_flag"].astype(bool).any())
        self.assertTrue(self.admission["lrd_flag"].isna().all())
        self.assertTrue(self.admission["object_class"].eq("broad_line_agn").all())
        expected_edd = np.power(10.0, self.admission["log_edd_ratio_published"])
        np.testing.assert_allclose(self.admission["edd_ratio_std"], expected_edd)
        self.assertTrue(self.admission["project_version"].eq("v7").all())
        self.assertTrue(self.admission["cosmic_time_gyr"].notna().all())
        for canonical, compatibility in [
            ("log_mbh_err_plus", "log_mbh_err_plus_std"),
            ("log_mbh_err_minus", "log_mbh_err_minus_std"),
            ("log_mstar_err_plus", "log_mstar_err_plus_std"),
            ("log_mstar_err_minus", "log_mstar_err_minus_std"),
            ("log_lbol_err_plus", "log_lbol_err_plus_std"),
            ("log_lbol_err_minus", "log_lbol_err_minus_std"),
        ]:
            np.testing.assert_allclose(
                self.admission[canonical], self.admission[compatibility],
            )

    def test_outflow_and_three_component_flags_are_not_generalized(self) -> None:
        indexed = self.admission.set_index("object_id")
        outflows = set(indexed.index[indexed["oiii_outflow_detected_flag"].eq(1)])
        self.assertEqual(outflows, {"DC_519281", "DC_536534", "DC_873321"})
        three_component = set(
            indexed.index[indexed["halpha_three_component_fit_flag"].eq(1)]
        )
        self.assertEqual(three_component, {"DC_536534"})

    def test_provenance_is_complete_and_current(self) -> None:
        self.assertTrue(self.admission["source_key"].eq(SOURCE_KEY).all())
        self.assertTrue(self.admission["source_paper_version"].eq(PAPER_VERSION).all())
        self.assertTrue(self.admission["source_doi"].eq(SOURCE_DOI).all())
        self.assertTrue(
            self.admission["source_archive_sha256"].eq(SOURCE_ARCHIVE_SHA256).all()
        )
        self.assertEqual(len(SOURCE_ARCHIVE_SHA256), 64)
        self.assertTrue(self.admission["source_table"].eq("Published Table 1").all())
        self.assertTrue(self.admission["selection_criteria"].str.contains("DeltaBIC").all())

    def test_no_coordinate_redshift_candidate_against_v6(self) -> None:
        v6 = pd.read_csv(ROOT / "data/processed/v6/v6_blagn_measurements.csv")
        self.assertTrue(v6_identity_candidates(self.admission, v6).empty)

if __name__ == "__main__":
    unittest.main()
