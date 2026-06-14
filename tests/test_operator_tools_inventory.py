from __future__ import annotations

import pytest

from tests.doc_test_helpers import (
    DocCase,
    actual_repo_root_files,
    actual_top_level_tool_wrappers,
    assert_doc_case,
    documented_tool_inventory,
    load_doc_cases,
    scripts_readme_supported_tool_inventory,
)

_SINGLE_PATH_CASES = load_doc_cases("operator_tools_inventory.json", "single_path_cases")


@pytest.mark.parametrize("case", _SINGLE_PATH_CASES, ids=lambda case: case.case_id)
def test_operator_inventory_docs(case: DocCase) -> None:
    assert_doc_case(case)


def test_tools_readme_inventory_matches_actual_top_level_tool_wrappers() -> None:
    assert documented_tool_inventory() == actual_top_level_tool_wrappers()


def test_scripts_readme_supported_tool_inventory_matches_canonical_tools_surface() -> None:
    assert scripts_readme_supported_tool_inventory() == documented_tool_inventory()


def test_repo_root_does_not_duplicate_documented_tool_entrypoints() -> None:
    duplicated = documented_tool_inventory() & actual_repo_root_files()
    assert not duplicated, sorted(duplicated)
