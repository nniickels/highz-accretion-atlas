"""Independent source, integration, and presentation checks (not round trips)."""

from __future__ import annotations

import re
import json
from unittest.mock import patch
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src import models
from src.internal.atlas import GROWTH_TRACK_REDSHIFT_LIMITS
from src.internal.verify_primary_source_values import verify_primary_source_values


ROOT = Path(__file__).resolve().parents[1]


class IndependentValidationTests(unittest.TestCase):
    def test_primary_source_table_values(self):
        self.assertEqual(verify_primary_source_values(), 1309)

    def test_missing_source_family_anchor_is_rejected(self):
        loads = json.loads
        def omit_family(text):
            parsed = loads(text)
            if "anchors" in parsed:
                parsed["anchors"] = [a for a in parsed["anchors"] if a["source_key"] != "ubler24_zs7_offset_blagn"]
            return parsed
        with patch("src.internal.verify_primary_source_values.json.loads", side_effect=omit_family):
            with self.assertRaisesRegex(AssertionError, "Source-family coverage differs"):
                verify_primary_source_values()

    def test_wrong_measurement_source_version_is_rejected(self):
        loads = json.loads
        def change_version(text):
            parsed = loads(text)
            if "anchors" in parsed:
                parsed["anchors"][0]["source_archive_sha256"] = "0" * 64
            return parsed
        with patch("src.internal.verify_primary_source_values.json.loads", side_effect=change_version):
            with self.assertRaisesRegex(AssertionError, "registered measurement version"):
                verify_primary_source_values()

    def test_cosmic_age_against_numerical_friedmann_integral(self):
        # Integrate dt = da/[a H(a)] using a=x^2, independently of arcsinh.
        nodes, weights = np.polynomial.legendre.leggauss(128)
        h0_gyr = 67.3 / 3.0856775814913673e19 * 3.15576e16
        for redshift in (0, 4, 8.913, 12.34, 13, 30):
            xmax = np.sqrt(1 / (1 + redshift))
            x = (nodes + 1) * xmax / 2
            integrand = 2 * x**2 / (h0_gyr * np.sqrt(0.315 + 0.685 * x**6))
            expected = np.sum(weights * integrand) * xmax / 2
            self.assertAlmostEqual(float(models.cosmic_time_gyr(redshift)), expected, places=10)

    def test_growth_against_physical_constant_ode(self):
        # RK4 integration of dM/dt=(1-epsilon)*L_Edd*f/(epsilon*c^2).
        # SI constants avoid reusing the production t_Edd=0.45 Gyr approximation.
        grav, proton, light, thomson = 6.67430e-11, 1.67262192369e-27, 299792458., 6.6524587321e-29
        coefficient = 4 * np.pi * grav * proton / (light * thomson) * 3.15576e16
        for fedd, epsilon, boost in ((0., .1, 2.), (.3, .1, 1.), (1., .1, 2.)):
            rate = coefficient * fedd * (1 - epsilon) / epsilon
            mass, dt = 1e4, 0.2 / 1000
            for _ in range(1000):
                k1 = rate * mass
                k2 = rate * (mass + dt * k1 / 2)
                k3 = rate * (mass + dt * k2 / 2)
                k4 = rate * (mass + dt * k3)
                mass += dt * (k1 + 2*k2 + 2*k3 + k4) / 6
            numerical = np.log10(mass * boost)
            analytic = float(models.predicted_log_mbh_from_delta_t(4, fedd, epsilon, .2, boost))
            # 0.45 Gyr rounding differs from physical constants by ~0.1%.
            self.assertAlmostEqual(analytic, numerical, delta=.003)

    def test_ideal_isco_and_slim_disk_anchors(self):
        expected = 1 - np.sqrt(1 - 2 / (3 * np.array([9., 6., 1.])))
        np.testing.assert_allclose(models.thin_disk_radiative_efficiency([-1, 0, 1]), expected, atol=1e-12)
        np.testing.assert_allclose(models.slim_disk_effective_efficiency([-1, 0, 1], 2), expected * 2 / np.e, atol=1e-12)

    def test_growth_tracks_include_every_catalogue_redshift(self):
        upper, lower = GROWTH_TRACK_REDSHIFT_LIMITS
        for version in ('v1', 'v2', 'v3'):
            objects = pd.read_csv(ROOT / f'data/processed/{version}/{version}_accreting_objects.csv')
            self.assertTrue(objects.redshift.between(lower, upper).all(), version)

    def test_manuscript_top_table_uses_required_fedd_order_and_values(self):
        text = (ROOT / 'paper/highz_accretion_atlas_v3.tex').read_text()
        table = text[:text.index(r'\label{tab:top}')].rsplit(r'\midrule', 1)[1]
        rows = re.findall(r'^([^&\n]+) & ([\d.]+) & ([\d.]+) & ([\d.]+) & ([\d.]+)--([\d.]+)', table, re.M)
        point = pd.read_csv(ROOT / 'results/v3/tables/v3_object_point_ranking.csv')
        uncertainty = pd.read_csv(ROOT / 'results/v3/tables/v3_object_uncertainty_ranking.csv')
        expected = point.nlargest(5, 'required_fedd_seed1e2').merge(
            uncertainty[['physical_object_id', 'required_fedd_seed1e2_p16', 'required_fedd_seed1e2_p84']],
            on='physical_object_id', validate='one_to_one',
        )
        self.assertEqual([r[0].strip() for r in rows], expected.object_id.tolist())
        for displayed, (_, actual) in zip(rows, expected.iterrows(), strict=True):
            for value, column, decimals in zip(displayed[1:], ['redshift', 'log_mbh_msun_std', 'required_fedd_seed1e2', 'required_fedd_seed1e2_p16', 'required_fedd_seed1e2_p84'], [3, 2, 3, 3, 3]):
                self.assertEqual(value, f'{actual[column]:.{decimals}f}')

    def test_nexus_missing_errors_are_explicit_point_estimates(self):
        frame = pd.read_csv(ROOT / 'results/v3/tables/v3_object_uncertainty_ranking.csv')
        point_only = frame.loc[frame.mbh_uncertainty_mode.eq('point_estimate_no_reported_mbh_error')]
        self.assertEqual(len(point_only), 12)
        self.assertEqual(set(point_only.source_key), {'zhuang25_nexus_wfss'})
        self.assertTrue(point_only.log_mbh_err_plus_std.isna().all())
        self.assertTrue(point_only.prob_required_fedd_seed1e2_gt_1.isna().all())
        self.assertTrue(point_only.rank_uncertainty_global_navigation.isna().all())
        np.testing.assert_array_equal(point_only.required_fedd_seed1e2_p16, point_only.required_fedd_seed1e2_p84)

    def test_nexus_luminosity_error_reaches_observables(self):
        frame = pd.read_csv(ROOT / 'data/processed/v3/v3_source_observables.csv')
        row = frame.loc[frame.observable_id.eq('NX21958_zhuang25__log_broad_line_luminosity')].iloc[0]
        self.assertEqual(row.value, 42.45)
        self.assertEqual(row.err_plus, .10)
        self.assertEqual(row.err_minus, .10)
