"""Independent checks of the supplementary radiation-inclusive ages."""
import unittest

import numpy as np

from src import models
from src.internal.early_start_cosmology import (
    cosmic_time_gyr, H0_GYR_INVERSE, OMEGA_M, OMEGA_R,
)


class EarlyStartCosmologyTests(unittest.TestCase):
    def test_quadrature_convergence_and_age_order(self):
        z = np.array([4, 7, 10.603, 20, 30, 3400])
        age = cosmic_time_gyr(z)
        np.testing.assert_allclose(age, cosmic_time_gyr(z, quadrature_order=256), rtol=1e-9)
        self.assertTrue(np.all(np.diff(age) < 0))
        self.assertTrue(np.all(age < models.cosmic_time_gyr(z)))

    def test_equality_age_against_matter_radiation_solution(self):
        # Lambda is negligible at equality; integrate a/sqrt(r + m*a) exactly.
        a = 1 / 3401.0
        exact = 2 / (3 * OMEGA_M**2 * H0_GYR_INVERSE) * (
            (OMEGA_M * a - 2 * OMEGA_R) * np.sqrt(OMEGA_R + OMEGA_M * a)
            + 2 * OMEGA_R**1.5
        )
        self.assertAlmostEqual(float(cosmic_time_gyr(3400)) / exact, 1, places=9)


if __name__ == '__main__':
    unittest.main()
