from __future__ import annotations

import pytest

from tests.doc_test_helpers import (
    DocCase,
    MultiPathDocCase,
    assert_doc_case,
    assert_doc_case_across_paths,
    load_doc_cases,
    load_multi_path_doc_cases,
    normalized_primary_text,
    primary_text,
)

_NORMALIZED_CASES = load_doc_cases("operator_setup_policy.json", "normalized_cases")
_PRIMARY_TEXT_MULTI_PATH_CASES = load_multi_path_doc_cases(
    "operator_setup_policy.json",
    "primary_text_multi_path_cases",
)


@pytest.mark.parametrize("case", _NORMALIZED_CASES, ids=lambda case: case.case_id)
def test_public_setup_docs_keep_root_install_policy_explicit(case: DocCase) -> None:
    assert_doc_case(case, reader=normalized_primary_text)


@pytest.mark.parametrize("case", _PRIMARY_TEXT_MULTI_PATH_CASES, ids=lambda case: case.case_id)
def test_operator_setup_multi_path_policy(case: MultiPathDocCase) -> None:
    assert_doc_case_across_paths(case, reader=primary_text)
