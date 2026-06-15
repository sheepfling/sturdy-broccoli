from __future__ import annotations

import json
from functools import lru_cache

from hla2010_repo_internal.requirements_source import SOURCE_OF_TRUTH_PATH

from tests.typed_json_models import RequirementSourceOfTruth


@lru_cache(maxsize=1)
def _source_of_truth() -> RequirementSourceOfTruth:
    return RequirementSourceOfTruth.from_mapping(
        json.loads(SOURCE_OF_TRUTH_PATH.read_text(encoding="utf-8"))
    )


def requirement_document_title(binding: str) -> str:
    return _source_of_truth().title_for_binding(binding)


def framework_document_title() -> str:
    return requirement_document_title("framework_rules")


def federate_interface_document_title() -> str:
    return requirement_document_title("federate_interface")


def omt_document_title() -> str:
    return requirement_document_title("omt")


def requirements_matrix_source_label() -> str:
    return " / ".join(
        (
            framework_document_title(),
            federate_interface_document_title(),
            omt_document_title(),
        )
    )


def standard_document_titles() -> set[str]:
    return {
        framework_document_title(),
        federate_interface_document_title(),
        omt_document_title(),
    }


def federate_interface_section_ref(clause_root: str) -> str:
    return f"{federate_interface_document_title()} §{clause_root}"
