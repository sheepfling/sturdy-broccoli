from __future__ import annotations

import pytest

from tests.doc_test_helpers import DocCase, assert_doc_case, load_doc_cases

_CONTAINS_CASES = load_doc_cases("front_door_docs.json", "contains_cases")
_REQUIREMENTS_ROLE_CASES = load_doc_cases("front_door_docs.json", "requirements_role_cases")


@pytest.mark.parametrize("case", _CONTAINS_CASES, ids=lambda case: case.case_id)
def test_front_door_docs_contain_expected_signals(case: DocCase) -> None:
    assert_doc_case(case)


@pytest.mark.parametrize("case", _REQUIREMENTS_ROLE_CASES, ids=lambda case: case.case_id)
def test_requirements_docs_keep_distinct_roles(case: DocCase) -> None:
    assert_doc_case(case)
