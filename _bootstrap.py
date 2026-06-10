"""Compatibility shim for repo-local script imports.

Repo-local tooling should prefer ``scripts._bootstrap``. This module exists so
legacy ``import _bootstrap`` call sites still work while the scripts package is
being normalized.
"""

from scripts._bootstrap import *  # noqa: F401,F403
