from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from compliance_helpers import is_1516_1_2010_row

ROOT = Path(__file__).resolve().parents[1]
PORTICO_POLICY_DOC = ROOT / "packages" / "hla-vendor-portico" / "docs" / "portico_requirement_disposition_policy.md"
PORTICO_MATRIX_PATH = ROOT / "tests" / "vendors" / "test_portico_real_backend_matrix.py"
SCENARIO_ENTRYPOINT_RE = re.compile(r"\b((?:run|probe)_[A-Za-z0-9_]+)\(")
DIRECT_BACKEND_CALL_RE = re.compile(
    r"\b(?:leader|wing|publisher|subscriber|owner|acquirer|observer|rti)\.[A-Za-z_][A-Za-z0-9_]*\("
)
TARGET_FUNCTIONS = {
    "test_portico_backend_exchange_matrix": "run_two_federate_exchange_scenario",
    "test_portico_backend_synchronization_matrix": "run_synchronization_scenario",
}
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


def _load_rows(filename: str) -> list[dict[str, object]]:
    payload = json.loads((ROOT / "analysis" / "compliance" / filename).read_text(encoding="utf-8"))
    return [
        row
        for row in payload["rows"]
        if is_1516_1_2010_row(row) or row.get("document") == "IEEE 1516-2010"
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


def test_portico_package_docs_keep_requirement_disposition_boundary_explicit() -> None:
    text = (ROOT / "packages" / "hla-vendor-portico" / "docs" / "README.md").read_text(encoding="utf-8")

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
    text = (ROOT / "analysis" / "compliance" / "portico_requirement_disposition.md").read_text(encoding="utf-8")

    assert "every row has an explicit generated `portico` disposition." in text
    assert "no promoted package-owned real-runtime requirement evidence" in text
    assert "applicable rows stay `classification-required` until" in text


def test_generated_portico_profile_requirement_dispositions_keep_inheritance_note_explicit() -> None:
    for filename, profile in (
        ("portico-jpype_requirement_disposition.md", "portico-jpype"),
        ("portico-py4j_requirement_disposition.md", "portico-py4j"),
    ):
        text = (ROOT / "analysis" / "compliance" / filename).read_text(encoding="utf-8")
        assert f"every row has an explicit generated `{profile}` disposition." in text
        assert "inherits the Portico family-level requirement disposition" in text
        assert "no profile-specific requirement evidence is generated yet" in text


def test_portico_family_artifacts_do_not_fall_back_to_not_yet_tested() -> None:
    for filename in (
        "portico_requirement_disposition.json",
        "portico-jpype_requirement_disposition.json",
        "portico-py4j_requirement_disposition.json",
    ):
        rows = _load_rows(filename)
        dispositions = {str(row.get("runtime_disposition", "")).strip() for row in rows}
        assert "not-yet-tested" not in dispositions, filename


def test_portico_matrix_wrappers_stay_shared_harness_driven() -> None:
    sources = _portico_matrix_function_sources()
    assert set(TARGET_FUNCTIONS).issubset(sources)

    for function_name, runner_name in TARGET_FUNCTIONS.items():
        source = sources[function_name]
        assert _scenario_entrypoints(source) == [runner_name], function_name
        assert not DIRECT_BACKEND_CALL_RE.search(source), function_name


def test_portico_clause4_first_wrapper_tranche_stays_explicit_but_unpromoted() -> None:
    rows = {
        str(row["requirement_id"]): row
        for row in _load_rows("portico_requirement_disposition.json")
        if str(row.get("requirement_id")) in PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS
    }
    assert set(rows) == set(PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS)

    for requirement_id, expected_refs in PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS.items():
        row = rows[requirement_id]
        assert row.get("runtime_disposition") == "classification-required"
        refs = set(row.get("evidence_refs", ()))
        for fragment in expected_refs:
            assert any(fragment in ref for ref in refs), (requirement_id, fragment, refs)
        note = str(row.get("notes", ""))
        assert "Portico now has an optional real-runtime thin wrapper" in note
        assert "classification-required" in note


def test_portico_profile_clause4_first_wrapper_tranche_inherits_family_evidence() -> None:
    family_rows = {
        str(row["requirement_id"]): row
        for row in _load_rows("portico_requirement_disposition.json")
        if str(row.get("requirement_id")) in PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS
    }
    assert set(family_rows) == set(PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS)

    for filename in (
        "portico-jpype_requirement_disposition.json",
        "portico-py4j_requirement_disposition.json",
    ):
        profile_rows = {
            str(row["requirement_id"]): row
            for row in _load_rows(filename)
            if str(row.get("requirement_id")) in PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS
        }
        assert set(profile_rows) == set(PORTICO_EXPLICIT_CLAUSE4_REQUIREMENT_IDS), filename

        for requirement_id, family_row in family_rows.items():
            profile_row = profile_rows[requirement_id]
            assert profile_row.get("runtime_disposition") == family_row.get("runtime_disposition"), (
                filename,
                requirement_id,
            )
            assert tuple(profile_row.get("evidence_refs", ())) == tuple(family_row.get("evidence_refs", ())), (
                filename,
                requirement_id,
            )
            assert str(profile_row.get("notes", "")) == str(family_row.get("notes", "")), (
                filename,
                requirement_id,
            )


def test_portico_clause6_first_wrapper_tranche_stays_explicit_but_unpromoted() -> None:
    rows = {
        str(row["requirement_id"]): row
        for row in _load_rows("portico_requirement_disposition.json")
        if str(row.get("requirement_id")) in PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS
    }
    assert set(rows) == set(PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS)

    for requirement_id, expected_refs in PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS.items():
        row = rows[requirement_id]
        assert row.get("runtime_disposition") == "classification-required"
        refs = set(row.get("evidence_refs", ()))
        for fragment in expected_refs:
            assert any(fragment in ref for ref in refs), (requirement_id, fragment, refs)
        note = str(row.get("notes", ""))
        assert "Portico now has an optional real-runtime thin wrapper" in note
        assert "classification-required" in note


def test_portico_profile_clause6_first_wrapper_tranche_inherits_family_evidence() -> None:
    family_rows = {
        str(row["requirement_id"]): row
        for row in _load_rows("portico_requirement_disposition.json")
        if str(row.get("requirement_id")) in PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS
    }
    assert set(family_rows) == set(PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS)

    for filename in (
        "portico-jpype_requirement_disposition.json",
        "portico-py4j_requirement_disposition.json",
    ):
        profile_rows = {
            str(row["requirement_id"]): row
            for row in _load_rows(filename)
            if str(row.get("requirement_id")) in PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS
        }
        assert set(profile_rows) == set(PORTICO_EXPLICIT_CLAUSE6_REQUIREMENT_IDS), filename

        for requirement_id, family_row in family_rows.items():
            profile_row = profile_rows[requirement_id]
            assert profile_row.get("runtime_disposition") == family_row.get("runtime_disposition"), (
                filename,
                requirement_id,
            )
            assert tuple(profile_row.get("evidence_refs", ())) == tuple(family_row.get("evidence_refs", ())), (
                filename,
                requirement_id,
            )
            assert str(profile_row.get("notes", "")) == str(family_row.get("notes", "")), (
                filename,
                requirement_id,
            )
