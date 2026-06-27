from __future__ import annotations

from pathlib import Path

from package_import_smoke import assert_package_tree_importable


def test_hla_backend_certi_package_modules_import() -> None:
    assert_package_tree_importable(Path(__file__).resolve().parents[1])
