"""Regression tests for the v7.5 publication package."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.verify_v7_5_publication import MANIFEST_PATH, verify_publication_contract


class V75PublicationTests(unittest.TestCase):
    def test_publication_contract(self) -> None:
        verify_publication_contract()

    def test_manifest_scope(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text())
        self.assertEqual(manifest["release"], "v7.5-publication")
        self.assertEqual(manifest["manuscript_pages"], 7)


if __name__ == "__main__":
    unittest.main()
