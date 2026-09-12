"""The numerical/rendering stack and build backend must not float on reinstall."""
from importlib.metadata import requires, version
from pathlib import Path
import tomllib
import unittest
from packaging.requirements import Requirement
from packaging.markers import default_environment
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]


class DependencyLockTests(unittest.TestCase):
    def test_notebook_dependency_closure_including_extras_is_pinned(self):
        project = tomllib.loads((ROOT/'pyproject.toml').read_text())['project']
        environment = default_environment()
        if environment['sys_platform'] not in ('linux', 'darwin'):
            self.skipTest('Notebook lock targets Linux and macOS')
        locked = {}

        def read_lock(path):
            for raw in path.read_text().splitlines():
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('-r '):
                    read_lock(path.parent / line[3:])
                    continue
                req = Requirement(line)
                self.assertEqual(len(req.specifier), 1)
                pin = next(iter(req.specifier))
                self.assertEqual(pin.operator, '==')
                self.assertNotIn('*', pin.version)
                if req.marker is None or req.marker.evaluate(environment):
                    name = canonicalize_name(req.name)
                    self.assertNotIn(name, locked, f'Duplicate lock entry: {name}')
                    locked[name] = req

        read_lock(ROOT/'requirements-notebook-lock.txt')
        pending = [Requirement(raw) for raw in
                   project['dependencies'] + project['optional-dependencies']['notebook']]
        seen = set()
        while pending:
            req = pending.pop()
            name = canonicalize_name(req.name)
            key = (name, frozenset(req.extras))
            if key in seen:
                continue
            seen.add(key)
            self.assertIn(name, locked, f'Unpinned notebook dependency: {name}')
            self.assertIn(version(name), locked[name].specifier)
            self.assertIn(version(name), req.specifier)
            for raw in requires(name) or []:
                child = Requirement(raw)
                # Jupyter requests extras such as jsonschema[format-nongpl].
                if child.marker is None or any(
                    child.marker.evaluate(dict(environment, extra=extra))
                    for extra in ('', *req.extras)
                ):
                    pending.append(child)

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
