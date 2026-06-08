from __future__ import annotations

from setuptools import find_packages


def test_installable_package_excludes_repo_internal_testing_helpers():
    packages = set(find_packages(include=["hla2010*"], exclude=["hla2010.testing*"]))
    assert "hla2010" in packages
    assert "hla2010.backends" in packages
    assert "hla2010.testing" not in packages
