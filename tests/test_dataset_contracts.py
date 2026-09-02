from __future__ import annotations

import unittest

from src.internal.verify_versions import verify_nested_membership, verify_version


class VersionContractTests(unittest.TestCase):
    def test_v1(self):
        verify_version("v1")

    def test_v2(self):
        verify_version("v2")

    def test_v3(self):
        verify_version("v3")

    def test_nested_membership(self):
        verify_nested_membership()


if __name__ == "__main__":
    unittest.main()
