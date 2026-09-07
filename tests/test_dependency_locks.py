"""The numerical/rendering stack and build backend must not float on reinstall."""
from importlib.metadata import requires, version
from pathlib import Path
import tomllib
import unittest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]


class DependencyLockTests(unittest.TestCase):
    def test_core_dependency_closure_is_pinned_and_satisfied(self):
        locked = {}
        for line in (ROOT/'requirements-lock.txt').read_text().splitlines():
            if line.strip() and not line.startswith('#'):
                req = Requirement(line)
                self.assertEqual(len(req.specifier), 1)
                self.assertEqual(next(iter(req.specifier)).operator, '==')
                locked[canonicalize_name(req.name)] = req
        project = tomllib.loads((ROOT/'pyproject.toml').read_text())
        pending = [Requirement(s).name for s in project['project']['dependencies']]
        seen = set()
        while pending:
            name = canonicalize_name(pending.pop())
            if name in seen:
                continue
            seen.add(name)
            self.assertIn(name, locked, f'Unpinned core dependency: {name}')
            self.assertIn(version(name), locked[name].specifier)
            for raw in requires(name) or []:
                req = Requirement(raw)
                if req.marker is None or req.marker.evaluate({'extra': ''}):
                    self.assertIn(version(req.name), req.specifier)
                    pending.append(req.name)

    def test_build_backend_has_matching_install_pin(self):
        project = tomllib.loads((ROOT/'pyproject.toml').read_text())
        build = project['build-system']
        self.assertEqual(build['build-backend'], 'setuptools.build_meta')
        installed = (ROOT/'requirements-build-lock.txt').read_text().splitlines()
        for requirement in build['requires']:
            self.assertIn(requirement, installed)
