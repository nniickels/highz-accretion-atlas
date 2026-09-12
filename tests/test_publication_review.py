"""Protect scientific distinctions introduced by the manuscript revision."""
import unittest
import numpy as np
from src import models
from src.internal.publication_selection import build_publication_outputs


class PublicationReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build_publication_outputs()

    def test_complete_tail_and_named_offset_survivors(self):
        tail = self.outputs['target_robustness']
        self.assertEqual(len(tail), 8)
        self.assertTrue(tail.required_fedd.gt(1).all())
        self.assertEqual(int(tail.probability_gt_1.ge(.95).sum()), 5)
        self.assertEqual(set(tail.loc[tail.p_minus05.ge(.95), 'object_id']),
                         {'UNCOVER-20466','COSMOS3D-13852','RUBIES-EGS-55604'})
        cosmos = tail.set_index('object_id').loc['COSMOS3D-13852']
        self.assertGreater(cosmos.f_minus1dex, 1)
        self.assertLess(cosmos.f_minus2dex, 1)

    def test_source_counts_use_measurements_and_preferred_objects_separately(self):
        sources = self.outputs['source_inventory']
        self.assertEqual(sources.source_key.nunique(), 32)
        self.assertEqual(sources[['n_measurements','n_growth_eligible_measurements',
                                 'n_publication_primary_preferred']].sum().tolist(), [350,244,220])

    def test_external_mass_is_borderline_and_does_not_change_membership(self):
        external = self.outputs['external_direct_mass_comparison'].set_index('comparison')
        old, new = external.loc['catalogue_virial'], external.loc['external_dynamical']
        self.assertAlmostEqual(old.log_mass, 7.3)
        self.assertAlmostEqual(new.log_mass, 7.7)
        self.assertLess(old.p84, 1)
        self.assertLess(new.required_fedd, 1)
        self.assertGreater(new.required_fedd, .999)
        self.assertLess(new.p16, 1)
        self.assertGreater(new.p84, 1)
        self.assertTrue(.49 < new.probability_gt_1 < .51)
        # Affine propagation in log mass gives identical normalized intervals.
        self.assertAlmostEqual((new.p84-new.p16)/(old.p84-old.p16), .3/.2)
        selection = self.outputs['publication_object_selection']
        self.assertEqual(int(selection.publication_primary_flag.sum()), 220)
        self.assertEqual(len(selection.loc[selection.object_id.eq('A2744-QSO1')]), 1)

    def test_matched_comparison_separates_measurement_and_clock_changes(self):
        matched = self.outputs['matched_literature_comparison']
        self.assertEqual(len(matched), 4)
        np.testing.assert_allclose(matched.earlier_inputs_z25+matched.delta_measurement+
                                   matched.delta_start_time, matched.current_inputs_z30)
        self.assertTrue(matched.delta_start_time.lt(0).all())
        qso = matched.set_index('object_id').loc['A2744-QSO1']
        self.assertEqual(qso.delta_measurement, 0)
        # Inverting the displayed f=1 boundary returns unit required rate.
        for zseed in (20,30):
            mass, z, seed = 8.17, 8.5, 2
            a = (models.cosmic_time_gyr(z)-models.cosmic_time_gyr(zseed))/(.45*np.log(10)*(mass-seed))
            self.assertAlmostEqual(float(models.required_fedd_for_seed(seed,mass,a/(1+a),zseed,z)), 1)

    def test_mass_reduction_reaches_eddington_limit(self):
        tail = self.outputs['target_robustness']
        reduction = tail.mass_reduction_to_f1_dex
        self.assertTrue(reduction.gt(0).all())
        # The reduced observed mass must require f=1 from a 100-solar-mass
        # seed at each object's redshift.
        critical_mass = tail.log_mbh_msun_std - reduction
        required = models.required_fedd_for_seed(2, critical_mass, .1, 30, tail.redshift)
        np.testing.assert_allclose(required, 1, atol=1e-12)
        self.assertTrue((models.required_fedd_for_seed(
            2, critical_mass - .01, .1, 30, tail.redshift) < 1).all())
        self.assertTrue((models.required_fedd_for_seed(
            2, critical_mass + .01, .1, 30, tail.redshift) > 1).all())
        j = tail.set_index('object_id').loc['J0910_2028_12910']
        self.assertAlmostEqual(j.mass_reduction_to_f1_dex, .330, places=3)
        self.assertLess(j.mass_reduction_to_f1_dex, j.log_mbh_systematic_dex)
