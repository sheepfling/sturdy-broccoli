from __future__ import annotations

from conftest import load_compliance_json
from tests.compliance_row_models import RequirementDispositionRow, VendorBacklogRow
from tests.requirement_label_helpers import federate_interface_document_title


FEDERATE_INTERFACE_DOCUMENT = federate_interface_document_title()
PITCH_LOST_FEDERATE_GAP_NOTE = (
    "packages/hla2010-rti-pitch-common/docs/evidence/"
    "pitch_clause4_lost_federate_gap_2026-06-11.md"
)
PITCH_CLAUSE4_ALLOWED_EVIDENCE_PREFIXES = (
    "packages/hla2010-verification-harness/",
    "tests/scenarios/",
    "tests/vendors/",
    "packages/hla2010-rti-pitch-common/docs/evidence/",
    "analysis/preflight_artifacts/",
    "analysis/vendor_runtime_status/",
    "tests/test_rti_pitch_split_packages.py::",
)
PITCH_CLAUSE4_BLOCKED_REQUIREMENT_IDS = {
    "HLA1516.1-FM-4.1.5-001",
    "HLA1516.1-FM-4.1.5-002",
}
PITCH_CLAUSE4_BLOCKED_NOTES_FRAGMENTS = (
    "./tools/pitch lost-federate-probe",
    "Docker is unreachable",
    "loopback ports are blocked",
)
PITCH_CLAUSE4_BLOCKED_FAMILY_REFS = {
    PITCH_LOST_FEDERATE_GAP_NOTE,
    "analysis/preflight_artifacts/pitch-preflight.json",
    "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
    "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
    "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_connection_lost.py::run_connection_lost_callback_scenario",
    "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_lost_federate.py::run_lost_federate_mom_scenario",
    "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_resign.py::run_disconnect_mom_cleanup_scenario",
    "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_lost_federate_mom_matrix",
    "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix",
}
PITCH_CLAUSE4_BLOCKED_JPYPE_REFS = {
    PITCH_LOST_FEDERATE_GAP_NOTE,
    "analysis/preflight_artifacts/pitch-preflight.json",
    "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
    "tests/test_rti_pitch_split_packages.py::test_pitch_jpype_factory_uses_inprocess_runtime_without_gateway_process",
    "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_lost_federate.py::run_external_lost_federate_observer_scenario",
    "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix",
}
PITCH_CLAUSE4_BLOCKED_PY4J_REFS = {
    PITCH_LOST_FEDERATE_GAP_NOTE,
    "analysis/preflight_artifacts/pitch-preflight.json",
    "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_summary.json",
    "analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/vendor_runtime_status_report.md",
    "packages/hla2010-verification-harness/src/hla2010_verification_harness/scenario_lost_federate.py::run_lost_federate_mom_scenario",
    "tests/test_rti_pitch_split_packages.py::test_pitch_py4j_factory_attaches_gateway_process",
    "tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix",
}
PITCH_CLAUSE4_RESIDUAL_FRONTIER = {
    "AREA-1516.1-4": "not-applicable",
    "HLA1516.1-FM-001": "not-applicable",
    "REQ-RTI-FM-4_5-createFederationExecutionWithMIM": "vendor-divergent",
    "HLA1516.1-FM-4.1.5-001": "blocked",
    "HLA1516.1-FM-4.1.5-002": "blocked",
    "HLA1516.1-FM-4.5-EXC-001": "vendor-divergent",
    "HLA1516.1-FM-4.9-EXC-001": "vendor-divergent",
}
PITCH_CLAUSE4_BACKLOG_FRONTIER = {
    ("pitch-requirements", "blocked", "pitch-requirement-disposition-row"),
    ("pitch-jpype", "blocked", "pitch-requirement-profile-row"),
    ("pitch-py4j", "blocked", "pitch-requirement-profile-row"),
}


def load_requirement_rows(filename: str) -> list[RequirementDispositionRow]:
    payload = load_compliance_json(filename)
    return [RequirementDispositionRow.from_mapping(row) for row in payload["rows"]]


def load_vendor_backlog_rows(filename: str) -> list[VendorBacklogRow]:
    payload = load_compliance_json(filename)
    return [VendorBacklogRow.from_mapping(row) for row in payload["rows"]]


def pitch_clause_rows(filename: str, clause_root: str) -> list[RequirementDispositionRow]:
    return [
        row
        for row in load_requirement_rows(filename)
        if row.document == FEDERATE_INTERFACE_DOCUMENT and row.clause_root == clause_root
    ]

