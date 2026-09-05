"""Mutation checks ensure source coverage and scientific identity gaps stay visible."""
import copy
import json
import unittest
import subprocess
import sys
from src.internal.verify_redshift_identity import FIXTURE, verify_redshift_identity

class RedshiftIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads(FIXTURE.read_text())

    def test_complete_numerical_audit_reports_open_identities(self):
        report = verify_redshift_identity()
        self.assertEqual(report['redshifts'], 350)
        self.assertEqual(report['coordinate_pairs'], 323)
        self.assertEqual(report['missing_coordinate_pairs'], 27)
        self.assertEqual(report['source_fields'], 1027)
        self.assertEqual(report['scientific_identity_status'], 'open')
        self.assertEqual(len(report['unresolved_identity_groups']), 5)

    def test_missing_measurement_rejected(self):
        f = copy.deepcopy(self.reference); f['measurements'].pop()
        with self.assertRaisesRegex(AssertionError, 'every measurement'):
            verify_redshift_identity(fixture=f)

    def test_wrong_source_redshift_rejected(self):
        f = copy.deepcopy(self.reference); f['measurements'][0]['fields']['redshift']['expected'] += .1
        with self.assertRaisesRegex(AssertionError, 'differs from source'):
            verify_redshift_identity(fixture=f)

    def test_omitted_duplicate_pair_rejected(self):
        f = copy.deepcopy(self.reference); f['pair_reviews'].pop(0)
        with self.assertRaisesRegex(AssertionError, 'identity pairs'):
            verify_redshift_identity(fixture=f)

    def test_wrong_registered_source_version_rejected(self):
        f = copy.deepcopy(self.reference); f['measurements'][0]['registered_primary_archive_sha256'] = '0'*64
        with self.assertRaisesRegex(AssertionError, 'source version differs'):
            verify_redshift_identity(fixture=f)

    def test_publication_gate_rejects_open_identities(self):
        result = subprocess.run(
            [sys.executable, '-m', 'src.internal.verify_redshift_identity', '--require-resolved'],
            cwd=FIXTURE.parents[2], capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Publication identity gate FAILED', result.stderr)
