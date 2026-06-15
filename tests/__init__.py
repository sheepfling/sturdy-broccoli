"""Test support package markers for reliable in-repo imports under CI."""

from __future__ import annotations

import sys

from . import conftest as _tests_conftest

# Older helper modules still import `conftest` as a top-level module.
sys.modules.setdefault("conftest", _tests_conftest)
