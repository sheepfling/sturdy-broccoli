from __future__ import annotations

from package_import_smoke import assert_package_tree_importable, package_root_from_test_file


def test_hla_fom_target_radar_package_modules_import() -> None:
    assert_package_tree_importable(package_root_from_test_file(__file__))
