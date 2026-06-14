from __future__ import annotations

from functools import lru_cache

from hla2010_repo_internal.requirements_source import requirement_document_title_for_binding, load_source_of_truth


@lru_cache(maxsize=1)
def _source_of_truth() -> dict[str, object]:
    return load_source_of_truth()


def requirement_document_title(binding: str) -> str:
    return requirement_document_title_for_binding(binding, _source_of_truth())


def framework_document_title() -> str:
    return requirement_document_title("framework_rules")


def federate_interface_document_title() -> str:
    return requirement_document_title("federate_interface")


def omt_document_title() -> str:
    return requirement_document_title("omt")


def standard_document_titles() -> set[str]:
    return {
        framework_document_title(),
        federate_interface_document_title(),
        omt_document_title(),
    }


def federate_interface_section_ref(clause_root: str) -> str:
    return f"{federate_interface_document_title()} §{clause_root}"
