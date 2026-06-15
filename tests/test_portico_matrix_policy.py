from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from conftest import REPO_ROOT, load_compliance_json, load_compliance_text
from tests.compliance_row_models import RequirementDispositionRow
from tests.requirement_label_helpers import federate_interface_document_title, framework_document_title

ROOT = REPO_ROOT
FEDERATE_INTERFACE_DOCUMENT = federate_interface_document_title()
FRAMEWORK_DOCUMENT = framework_document_title()
PORTICO_POLICY_DOC = ROOT / "packages" / "hla2010-rti-portico" / "docs" / "portico_requirement_disposition_policy.md"
PORTICO_MATRIX_PATH = ROOT / "tests" / "vendors" / "test_portico_real_backend_matrix.py"
SCENARIO_ENTRYPOINT_RE = re.compile(r"\b((?:run|probe)_[A-Za-z0-9_]+)\(")
DIRECT_BACKEND_CALL_RE = re.compile(
    r"\b(?:leader|wing|publisher|subscriber|owner|acquirer|observer|rti)\.[A-Za-z_][A-Za-z0-9_]*\("
)
TARGET_FUNCTIONS = {
    "test_portico_backend_exchange_matrix": "run_two_federate_exchange_scenario",
    "test_portico_backend_synchronization_matrix": "run_synchronization_scenario",
}
PORTICO_PROFILE_MARKDOWN_CASES = (
    ("portico-jpype_requirement_disposition.md", "portico-jpype"),
    ("portico-py4j_requirement_disposition.md", "portico-py4j"),
)
PORTICO_PROFILE_JSON_CASES = (
    "portico-jpype_requirement_disposition.json",
    "portico-py4j_requirement_disposition.json",
)
PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS = {
    "REQ-RTI-FM-4_2-connect": (
        "scenario_federation_lifecycle.py::run_federation_lifecycle_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",
    ),
    "REQ-RTI-FM-4_5-createFederationExecution": (
        "scenario_federation_lifecycle.py::run_federation_lifecycle_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",
    ),
    "REQ-RTI-FM-4_9-joinFederationExecution": (
        "scenario_federation_lifecycle.py::run_federation_lifecycle_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",
    ),
    "REQ-RTI-FM-4_11-registerFederationSynchronizationPoint": (
        "scenario_sync.py::run_synchronization_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_synchronization_matrix",
    ),
    "REQ-FED-FM-4_12-synchronizationPointRegistrationSucceeded": (
        "scenario_sync.py::run_synchronization_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_synchronization_matrix",
    ),
    "REQ-FED-FM-4_13-announceSynchronizationPoint": (
        "scenario_sync.py::run_synchronization_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_synchronization_matrix",
    ),
    "REQ-RTI-FM-4_14-synchronizationPointAchieved": (
        "scenario_sync.py::run_synchronization_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_synchronization_matrix",
    ),
    "REQ-FED-FM-4_15-federationSynchronized": (
        "scenario_sync.py::run_synchronization_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_synchronization_matrix",
    ),
}
PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS = {
    "REQ-RTI-OM-6_8-registerObjectInstance": (
        "scenario_exchange.py::run_two_federate_exchange_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",
    ),
    "REQ-FED-OM-6_9-discoverObjectInstance": (
        "scenario_exchange.py::run_two_federate_exchange_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",
    ),
    "REQ-RTI-OM-6_10-updateAttributeValues": (
        "scenario_exchange.py::run_two_federate_exchange_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",
    ),
    "REQ-FED-OM-6_11-reflectAttributeValues": (
        "scenario_exchange.py::run_two_federate_exchange_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",
    ),
    "REQ-RTI-OM-6_12-sendInteraction": (
        "scenario_exchange.py::run_two_federate_exchange_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",
    ),
    "REQ-FED-OM-6_13-receiveInteraction": (
        "scenario_exchange.py::run_two_federate_exchange_scenario",
        "tests/vendors/test_portico_real_backend_matrix.py::test_portico_backend_exchange_matrix",
    ),
}


def _load_rows(filename: str) -> list[RequirementDispositionRow]:
    payload = load_compliance_json(filename)
    return [
        typed_row
        for typed_row in (
            RequirementDispositionRow.from_mapping(row)
            for row in payload["rows"]
        )
        if typed_row.document in {FEDERATE_INTERFACE_DOCUMENT, FRAMEWORK_DOCUMENT}
    ]


def _portico_matrix_function_sources() -> dict[str, str]:
    source = PORTICO_MATRIX_PATH.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(PORTICO_MATRIX_PATH))
    functions: dict[str, str] = {}
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in TARGET_FUNCTIONS:
            segment = ast.get_source_segment(source, node)
            assert segment is not None, node.name
            functions[node.name] = segment
    return functions


def _scenario_entrypoints(source: str) -> list[str]:
    return SCENARIO_ENTRYPOINT_RE.findall(source)


def _assert_portico_matrix_wrappers_follow_policy() -> None:
    sources = _portico_matrix_function_sources()
    assert set(TARGET_FUNCTIONS).issubset(sources)

    for function_name, runner_name in TARGET_FUNCTIONS.items():
        source = sources[function_name]
        assert _scenario_entrypoints(source) == [runner_name], function_name
        assert not DIRECT_BACKEND_CALL_RE.search(source), function_name


def _assert_portico_profile_rows_inherit_family_rows(
    family_rows: dict[str, RequirementDispositionRow],
    profile_filename: str,
    requirement_ids: set[str],
) -> None:
    profile_rows = {
        row.requirement_id: row
        for row in _load_rows(profile_filename)
        if row.requirement_id in requirement_ids
    }
    assert set(profile_rows) == requirement_ids, profile_filename

    for requirement_id, family_row in family_rows.items():
        profile_row = profile_rows[requirement_id]
        assert profile_row.runtime_disposition == family_row.runtime_disposition, (
            profile_filename,
            requirement_id,
        )
        assert profile_row.evidence_refs == family_row.evidence_refs, (
            profile_filename,
            requirement_id,
        )
        assert profile_row.notes == family_row.notes, (
            profile_filename,
            requirement_id,
        )


def _assert_portico_explicit_rows_match_policy(
    requirement_map: dict[str, tuple[str, ...]],
    *,
    filename: str,
) -> dict[str, RequirementDispositionRow]:
    rows = {
        row.requirement_id: row
        for row in _load_rows(filename)
        if row.requirement_id in requirement_map
    }
    assert set(rows) == set(requirement_map)

    for requirement_id, expected_refs in requirement_map.items():
        row = rows[requirement_id]
        assert row.runtime_disposition == "classification-required"
        refs = set(row.evidence_refs)
        for fragment in expected_refs:
            assert any(fragment in ref for ref in refs), (requirement_id, fragment, refs)
        assert "Portico now has an optional real-runtime thin wrapper" in row.notes
        assert "classification-required" in row.notes
    return rows


def _assert_portico_profile_markdown_cases() -> None:
    for filename, profile in PORTICO_PROFILE_MARKDOWN_CASES:
        text = load_compliance_text(filename)
        for fragment in (
            f"every row has an explicit generated `{profile}` disposition.",
            "inherits the Portico family-level requirement disposition",
            "no profile-specific requirement evidence is generated yet",
        ):
            assert fragment in text


def test_portico_package_docs_keep_requirement_disposition_boundary_explicit() -> None:
    text = (ROOT / "packages" / "hla2010-rti-portico" / "docs" / "README.md").read_text(encoding="utf-8")

    assert "portico_requirement_disposition_policy.md" in text
    assert "analysis/compliance/portico_requirement_disposition.md" in text
    assert "analysis/compliance/portico-jpype_requirement_disposition.md" in text
    assert "analysis/compliance/portico-py4j_requirement_disposition.md" in text
    assert "tests/vendors/test_portico_real_backend_matrix.py" in text
    assert "classification-required" in text
    assert "./tools/vendor-green" in text


def test_portico_requirement_disposition_policy_doc_states_promotion_rule() -> None:
    text = PORTICO_POLICY_DOC.read_text(encoding="utf-8")

    assert "classification-required" in text
    assert "must not inherit CERTI or Pitch package docs" in text
    assert "as evidence" in text
    assert "thin Portico backend wrapper" in text
    assert "shared harness scenario" in text


def test_generated_portico_requirement_disposition_markdown_keeps_current_boundary_explicit() -> None:
    text = load_compliance_text("portico_requirement_disposition.md")

    assert "every row has an explicit generated `portico` disposition." in text
    assert "no promoted package-owned real-runtime requirement evidence" in text
    assert "applicable rows stay `classification-required` until" in text


def test_generated_portico_profile_requirement_dispositions_keep_inheritance_note_explicit() -> None:
    _assert_portico_profile_markdown_cases()


def test_portico_family_artifacts_do_not_fall_back_to_not_yet_tested() -> None:
    for filename in (
        "portico_requirement_disposition.json",
        "portico-jpype_requirement_disposition.json",
        "portico-py4j_requirement_disposition.json",
    ):
        rows = _load_rows(filename)
        dispositions = {row.runtime_disposition for row in rows}
        assert "not-yet-tested" not in dispositions, filename


def test_portico_matrix_wrappers_stay_shared_harness_driven() -> None:
    _assert_portico_matrix_wrappers_follow_policy()


def test_portico_clause4_first_wrapper_tranche_stays_explicit_but_unpromoted() -> None:
    _assert_portico_explicit_rows_match_policy(
        PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS,
        filename="portico_requirement_disposition.json",
    )


def test_portico_profile_clause4_first_wrapper_tranche_inherits_family_evidence() -> None:
    family_rows = _assert_portico_explicit_rows_match_policy(
        PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS,
        filename="portico_requirement_disposition.json",
    )

    for filename in PORTICO_PROFILE_JSON_CASES:
        _assert_portico_profile_rows_inherit_family_rows(
            family_rows,
            filename,
            set(PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS),
        )


def test_portico_clause6_first_wrapper_tranche_stays_explicit_but_unpromoted() -> None:
    _assert_portico_explicit_rows_match_policy(
        PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS,
        filename="portico_requirement_disposition.json",
    )


def test_portico_profile_clause6_first_wrapper_tranche_inherits_family_evidence() -> None:
    family_rows = _assert_portico_explicit_rows_match_policy(
        PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS,
        filename="portico_requirement_disposition.json",
    )

    for filename in PORTICO_PROFILE_JSON_CASES:
        _assert_portico_profile_rows_inherit_family_rows(
            family_rows,
            filename,
            set(PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS),
        )
