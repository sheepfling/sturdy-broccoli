from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES_ROOT = ROOT / "packages"


def test_each_package_has_a_local_import_smoke_test() -> None:
    package_roots = sorted(path for path in PACKAGES_ROOT.iterdir() if (path / "pyproject.toml").exists())
    assert package_roots
    for package_root in package_roots:
        tests_dir = package_root / "tests"
        assert tests_dir.is_dir(), f"missing tests dir: {tests_dir}"
        smoke_tests = sorted(tests_dir.glob("test_*import_smoke.py"))
        assert smoke_tests, f"missing package import smoke test in {tests_dir}"
