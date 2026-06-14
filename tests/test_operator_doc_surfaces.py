from __future__ import annotations

import pytest

from tests.doc_test_helpers import (
    DocCase,
    MultiPathDocCase,
    assert_doc_case,
    assert_doc_case_across_paths,
    load_doc_cases,
    load_multi_path_doc_cases,
    primary_text,
)

_CASES = load_doc_cases("operator_doc_surfaces.json", "cases")
_MULTI_PATH_CASES = load_multi_path_doc_cases("operator_doc_surfaces.json", "multi_path_cases")


@pytest.mark.parametrize("case", _CASES, ids=lambda case: case.case_id)
def test_operator_doc_surfaces(case: DocCase) -> None:
    assert_doc_case(case, reader=primary_text)


@pytest.mark.parametrize("case", _MULTI_PATH_CASES, ids=lambda case: case.case_id)
def test_operator_doc_surfaces_across_multiple_paths(case: MultiPathDocCase) -> None:
    assert_doc_case_across_paths(case, reader=primary_text)
