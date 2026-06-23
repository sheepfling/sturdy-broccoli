from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_DIR = ROOT / "docs/requirements/ieee-1516-2025"
REGISTRY = REGISTRY_DIR / "requirements.json"
HARMONIZATION_WORKLIST = ROOT / "requirements/2025/harmonization/hla_2025_harmonization_worklist.csv"
EXECUTABLE_REQUIREMENTS = REGISTRY_DIR / "executable_tests/hla_2025_executable_test_requirements_v3.csv"


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-REQ-002")
def test_ieee_1516_2025_requirements_registry_has_initial_tranche() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    requirements = {row["id"]: row for row in data["requirements"]}

    assert data["extraction_stance"]["classification"]["shall"] == "normative requirement"
    assert len(requirements) == 28
    assert {f"HLA2025-FR-{index:03d}" for index in range(1, 11)} <= set(requirements)
    assert {f"HLA2025-FI-{index:03d}" for index in range(1, 10)} <= set(requirements)
    assert {f"HLA2025-OMT-{index:03d}" for index in range(1, 8)} <= set(requirements)

    assert requirements["HLA2025-REQ-002"]["text_summary"].startswith("Do not label")
    assert "two-federate-core-exchange" in requirements["HLA2025-FR-003"]["tests"]
    assert "full interface service surface accounting" in requirements["HLA2025-FI-002"]["tests"]
    assert "validate_hla_name" in requirements["HLA2025-OMT-001"]["tests"]


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ieee_1516_2025_requirements_markdown_views_exist() -> None:
    expected = {
        "README.md",
        "binding_and_hosted_route_boundaries.md",
        "callback_bounded_proof.md",
        "callback_binding_deltas.md",
        "declaration_management_bounded_proof.md",
        "ddm_bounded_proof.md",
        "federation_management_bounded_proof.md",
        "fom_backed_scenario_bounded_proof.md",
        "hosted_fedpro_bounded_proof.md",
        "framework_rules.md",
        "federate_interface.md",
        "lookahead_window_bounded_proof.md",
        "object_management_bounded_proof.md",
        "omt_xs_any_extension_tolerance.md",
        "omt.md",
        "ownership_management_bounded_proof.md",
        "python2025_direct_bounded_proof.md",
        "python2025_exclusion_boundaries.md",
        "save_restore_bounded_proof.md",
        "support_services_bounded_proof.md",
        "standard_binding_runtime_capability_bounded_proof.md",
        "time_management_bounded_proof.md",
        "traceability_matrix.md",
    }
    assert expected <= {path.name for path in REGISTRY_DIR.iterdir()}


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ieee_1516_2025_requirements_readme_indexes_bounded_proof_notes() -> None:
    text = (REGISTRY_DIR / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    for filename in (
        "fom_backed_scenario_bounded_proof.md",
        "save_restore_bounded_proof.md",
        "callback_bounded_proof.md",
        "lookahead_window_bounded_proof.md",
        "federation_management_bounded_proof.md",
        "python2025_direct_bounded_proof.md",
        "declaration_management_bounded_proof.md",
        "object_management_bounded_proof.md",
        "ownership_management_bounded_proof.md",
        "ddm_bounded_proof.md",
        "support_services_bounded_proof.md",
        "standard_binding_runtime_capability_bounded_proof.md",
        "time_management_bounded_proof.md",
        "hosted_fedpro_bounded_proof.md",
        "binding_and_hosted_route_boundaries.md",
        "python2025_exclusion_boundaries.md",
        "callback_binding_deltas.md",
        "omt_xs_any_extension_tolerance.md",
    ):
        assert f"`{filename}`" in text

    assert "bounded requirement-facing proof note" in normalized
    assert "main `python2025` lane plus hosted replay" in normalized
    assert "tracked Proto2025 and Target/Radar example/FOM-backed scenario suite over the main `python2025` lanes" in normalized
    assert "save/restore lifecycle control, shared rollback, routing/policy rollback, ownership rollback, and time-window/time-state rollback" in normalized
    assert "callback-delivery families, callback-control hygiene, and direct-versus-hosted callback surface boundaries over the main `python2025` runtime" in normalized
    assert "Target/Radar lookahead ladder, including future-exclusion, output ordering, pipeline overlap, negative-oracle guards, and bounded save/restore window rollback" in normalized
    assert "direct `python2025` main-surface runtime lane over `hla-backend-python2025`" in normalized
    assert "Java, C++, and hosted FedPro binding/route boundaries over the main `python2025` runtime" in text
    assert "explicit exclusion map for legacy aliases, Java/C++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope OMT extension semantics" in normalized


@pytest.mark.requirements("HLA2025-BND-003", "HLA2025-MIL-001", "HLA2025-MIL-002")
def test_hosted_fedpro_bounded_proof_markdown_keeps_main_runtime_identity_and_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "hosted_fedpro_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current hosted-route claim for `python-2025-fedpro-grpc`." in normalized
    assert "bounded transport/runtime slice rather than a second RTI implementation family" in normalized
    assert "sole repo-owned IEEE 1516.1-2025 Python RTI implementation lane" in normalized
    assert "The hosted route is parity-covered across the tracked scenario families" in normalized
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/scenarios/test_python_route_parity.py`" in text
    assert "`docs/backend_route_inventory_remote.md`" in text
    assert "`packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`" in text
    assert "`docs/requirements/ieee-1516-2025/python2025_direct_bounded_proof.md`" in text
    assert "`docs/requirements/ieee-1516-2025/python2025_exclusion_boundaries.md`" in text
    assert "`federation_lifecycle`" in text
    assert "`time_management`" in text
    assert "`support_services`" in text
    assert "`hla-backend-python2025`" in text
    assert "shared Target/Radar example path" in normalized
    assert "`./tools/python verify-routes-2025`" in text
    assert "`./tools/python verify-main-2025`" in text
    assert "does not claim that `python-2025-fedpro-grpc` is a second full RTI implementation lane" in normalized


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ieee_1516_2025_requirements_readme_tracks_current_runtime_proof_lane() -> None:
    text = (REGISTRY_DIR / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "## Current Technical Lane" in text
    assert "deeper runtime-proof expansion over the promoted `python2025` RTI surface" in normalized
    assert "the tracked example/FOM-backed scenario bounded proof note" in normalized
    assert "the dedicated save/restore bounded proof note" in normalized
    assert "the dedicated callback bounded proof note" in normalized
    assert "the dedicated lookahead-window bounded proof note" in normalized
    assert "the dedicated direct `python2025` bounded proof note" in normalized
    assert "the dedicated hosted FedPro bounded proof plus route-parity evidence that replays those runtime families" in normalized
    assert "wrapper-only shim boundaries" in normalized
    assert "one explicit exclusion map that gathers the non-claim areas around the main `python2025` runtime lane" in normalized
    assert "FOM/OMT validation still matters inside that lane" in normalized
    assert "one proof family inside the broader 2025 runtime-evidence closeout" in normalized


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-BND-001", "HLA2025-BND-002", "HLA2025-BND-003")
def test_python2025_exclusion_boundaries_markdown_gathers_non_claim_areas() -> None:
    text = (REGISTRY_DIR / "python2025_exclusion_boundaries.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records what the repository is explicitly **not** claiming" in text
    assert "main IEEE 1516.1-2025 Python RTI implementation statement" in text
    assert "`hla-backend-python2025` is the sole repo-owned Python RTI implementation lane" in normalized
    assert "Legacy aliases and shim imports" in text
    assert "Java/C++ bindings" in text
    assert "Hosted transport boundaries" in text
    assert "Duplicate/umbrella rows" in text
    assert "Retired/legacy-only rows" in text
    assert "OMT extension semantics" in text
    assert "`hla-backend-shim` is deprecated temporary import-compatibility scaffolding and wrapper-only compatibility support" in normalized
    assert "not alternate Python RTIs and not exhaustive cross-binding behavior conformance" in normalized
    assert "bounded hosted transport/runtime slice over `hla-backend-python2025`" in normalized
    assert "normalization aids and mapping notes rather than standalone one-row conformance assertions" in normalized
    assert "explicit exclusions from active 2025 support obligations" in normalized
    assert "Arbitrary third-party extension execution semantics remain out of scope" in text
    assert "`../../python_rti_backend.md`" in text
    assert "`hosted_fedpro_bounded_proof.md`" in text
    assert "`standard_binding_runtime_capability_bounded_proof.md`" in text
    assert "`retired_legacy_mapping.md`" in text
    assert "`omt_xs_any_extension_tolerance.md`" in text


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-MIL-001", "HLA2025-MIL-002")
def test_python2025_direct_bounded_proof_markdown_keeps_main_lane_claim_explicit() -> None:
    text = (REGISTRY_DIR / "python2025_direct_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current direct-lane claim for `python2025`." in normalized
    assert "The direct lane is the main executable bounded proof surface for the current 2025 Python RTI." in normalized
    assert "sole repo-owned IEEE 1516.1-2025 Python RTI implementation lane" in normalized
    assert "`hla-backend-python2025`" in text
    assert "`federation_lifecycle`" in text
    assert "`object_exchange`" in text
    assert "`ownership`" in text
    assert "`ddm`" in text
    assert "`time_management`" in text
    assert "`save_restore`" in text
    assert "`mom`" in text
    assert "`support_services`" in text
    assert "`omt_validation`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/scenarios/test_target_radar_scenario.py`" in text
    assert "`tests/test_fom_target_radar_split_package.py`" in text
    assert "`tests/test_rti1516_2025_validation.py`" in text
    assert "`docs/test_surface.md`" in text
    assert "`docs/requirements/ieee-1516-2025/hosted_fedpro_bounded_proof.md`" in text
    assert "`docs/requirements/ieee-1516-2025/python2025_exclusion_boundaries.md`" in text
    assert "verify-main-2025" in text
    assert "`./tools/python verify-routes-2025`" in text
    assert "not a wrapper-owned surface and not a full unqualified conformance claim" in normalized
    assert "does not treat `hla-backend-shim` as part of the implementation owner claim for this lane" in normalized


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-MIL-002", "HLA2025-FR-001", "HLA2025-FR-003", "HLA2025-FR-004")
def test_fom_backed_scenario_bounded_proof_markdown_keeps_tracked_suite_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "fom_backed_scenario_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing claim for tracked example and FOM-backed scenario execution" in normalized
    assert "`message-test`" in text
    assert "`space-lite`" in text
    assert "`time-mgmt-test`" in text
    assert "`target-radar`" in text
    assert "`tests/scenarios/test_proto2025_fom_showcase.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/scenarios/test_python_route_parity.py`" in text
    assert "`Proto2025_MessageTest.xml`" in text
    assert "`Proto2025_SpaceLite.xml`" in text
    assert "`Proto2025_TimeMgmtTest.xml`" in text
    assert "It does not yet prove every conceivable example FOM scenario outside the tracked suite." in normalized
    assert "`hla-backend-python2025`. `hla-backend-shim` is not an implementation owner" in normalized


@pytest.mark.requirements("HLA2025-FI-SVC-018", "HLA2025-FI-SVC-024", "HLA2025-FI-005", "HLA2025-REQ-002")
def test_save_restore_bounded_proof_markdown_keeps_rollback_family_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "save_restore_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing save/restore claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-018`, `HLA2025-FI-SVC-019`, `HLA2025-FI-SVC-020`" in text
    assert "`HLA2025-REQ-002`" in text
    assert "`HLA2025-FI-SVC-024`, `HLA2025-FI-SVC-025`, `HLA2025-FI-SVC-033`, `HLA2025-FI-SVC-034`" in text
    assert "`HLA2025-FI-005`" in text
    assert "`HLA2025-FI-001`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/scenarios/test_save_restore_backend_matrix.py`" in text
    assert "`tests/scenarios/test_python_route_parity.py`" in text
    assert "`hla-backend-python2025`. `hla-backend-shim` is not an implementation owner" in normalized
    assert "Hosted FedPro remains transport-seam evidence over `hla-backend-python2025`" in text
    assert "does not claim that every save/restore requirement now has its own standalone clause-by-clause conformance proof" in normalized


@pytest.mark.requirements("HLA2025-FI-CB-001", "HLA2025-FI-CB-005", "HLA2025-FI-CB-008", "HLA2025-BIND-FEDPRO-001")
def test_callback_bounded_proof_markdown_keeps_callback_family_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "callback_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing callback claim as a bounded proof statement" in normalized
    assert "Declaration relevance and interest advisories" in text
    assert "Federation sync, save/restore, and reporting callbacks" in text
    assert "Object discovery, delivery, and removal" in text
    assert "Object advisory, transport, and name-reservation callbacks" in text
    assert "Supplemental callback context and region metadata" in text
    assert "Ownership negotiation and query callbacks" in text
    assert "Time grant, regulation, and retraction callbacks" in text
    assert "Callback control and backlog hygiene" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/scenarios/test_federation_management_backend_matrix.py`" in text
    assert "`tests/scenarios/test_save_restore_backend_matrix.py`" in text
    assert "`tests/scenarios/test_ownership_management_backend_matrix.py`" in text
    assert "`tests/scenarios/test_python_route_parity.py`" in text
    assert "`hla-backend-python2025`. `hla-backend-shim` is not an implementation owner" in normalized
    assert "does not claim exhaustive callback-by-callback signature equivalence" in normalized
    assert "Hosted FedPro remains transport-seam evidence over `hla-backend-python2025`" in text


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FR-003", "HLA2025-FR-004")
def test_traceability_and_worklists_name_python2025_as_runtime_owner_not_shim_route() -> None:
    traceability_text = (REGISTRY_DIR / "traceability_matrix.md").read_text(encoding="utf-8")
    traceability_normalized = " ".join(traceability_text.split())
    worklist_text = HARMONIZATION_WORKLIST.read_text(encoding="utf-8")
    executable_text = EXECUTABLE_REQUIREMENTS.read_text(encoding="utf-8")

    assert "primary-`python2025` runtime plus binding/hosted-route scenario mapping" in (
        REGISTRY_DIR / "README.md"
    ).read_text(encoding="utf-8")
    assert "| HLA2025-FR-003 | python2025 runtime + binding routes |" in traceability_text
    assert "| HLA2025-FR-004 | python2025 runtime + binding routes |" in traceability_text
    assert "| HLA2025-FI-004 | binding/intake routes |" in traceability_text
    assert "language shim routes" not in traceability_normalized
    assert "language shim intake" not in traceability_normalized
    assert "Map service to the primary python2025 runtime lane, Java surface, C++ surface, and FedPro/vendor route" in worklist_text
    assert "Map service to Python shim route" not in worklist_text
    assert "python2025-plus-binding route scenario" in executable_text
    assert "route-matrix scenario runner can produce normalized route traces and requirement-tagged evidence across the primary python2025 runtime lane" in executable_text
    assert "language-shim route scenario" not in executable_text


@pytest.mark.requirements("HLA2025-REQ-001", "HLA2025-FR-001", "HLA2025-FR-010")
def test_framework_rules_markdown_maps_umbrella_rows_to_child_evidence() -> None:
    text = (REGISTRY_DIR / "framework_rules.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "These rows remain `duplicate/umbrella` in the harmonization ledger." in text
    assert "`HLA2025-REQ-001`, `HLA2025-OMT-001`, `HLA2025-OMT-005`, `HLA2025-OMT-006`" in text
    assert "`HLA2025-FI-001`, `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-060`, `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`" in text
    assert "`HLA2025-FI-009`, `HLA2025-MOD-006`, `HLA2025-FI-SVC-101`, `HLA2025-FI-SVC-107`, `HLA2025-FI-SVC-112`, `HLA2025-FI-SVC-121`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "| HLA2025-FR-005 |" in text
    assert "| HLA2025-FR-010 |" in text
    assert "The primary implementation lane behind the executable anchors above is `hla-backend-python2025`." in normalized
    assert "`hla-backend-shim` is not a runtime owner for these framework rules." in normalized
    assert "Each rule closes only through linked child FI, OMT, and runtime evidence" in normalized


@pytest.mark.requirements("HLA2025-FI-SVC-107", "HLA2025-FI-SVC-116", "HLA2025-FI-SVC-121", "HLA2025-MOD-006")
def test_lookahead_window_bounded_proof_markdown_keeps_proof_ladder_and_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "lookahead_window_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing claim for lookahead window closure" in normalized
    assert "`time-window-core`" in text
    assert "`time-window-future-exclusion`" in text
    assert "`time-window-output-delivery`" in text
    assert "`time-window-consumer-order`" in text
    assert "`time-window-pipeline-two-scans`" in text
    assert "`time-window-receive-order-poison`" in text
    assert "`time-window-save-restore-window-state`" in text
    assert "`time-window-save-restore-output-resume`" in text
    assert "`time-window-save-restore-pipeline-resume`" in text
    assert "`lookahead-processing-window-certified`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/scenarios/test_python_route_parity.py`" in text
    assert "`./tools/pitch time-window-probe`" in text
    assert "`./tools/pitch time-window-restore-state-probe`" in text
    assert "must fail if the RTI allows a future-message exclusion bug or a closed-window causality leak" in normalized
    assert "`hla-backend-python2025`. `hla-backend-shim` is not an implementation owner" in normalized


@pytest.mark.requirements("HLA2025-FI-CB-001", "HLA2025-BIND-FEDPRO-001", "HLA2025-BIND-JAVA-CPP-001")
def test_callback_binding_delta_markdown_maps_umbrella_rows_to_runtime_and_binding_evidence() -> None:
    text = (REGISTRY_DIR / "callback_binding_deltas.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "These rows remain `duplicate/umbrella` in the harmonization ledger." in text
    assert "`HLA2025-FI-SVC-193`" in text
    assert "`HLA2025-FI-SVC-194`" in text
    assert "`HLA2025-FI-SVC-195`, `HLA2025-FI-SVC-196`" in text
    assert "`HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`, `HLA2025-BND-003`" in text
    assert "`HLA2025-BND-001`, `HLA2025-BND-002`, `HLA2025-FI-003`, `HLA2025-FI-004`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "| HLA2025-FI-CB-008 |" in text
    assert "| HLA2025-BIND-JAVA-CPP-001 |" in text
    assert "The primary runtime owner behind the executable anchors above is `hla-backend-python2025`." in normalized
    assert "`hla-backend-shim`, `hla-backend-cpp-shim`, and the Java bridge packages are wrapper/binding surfaces over that runtime lane;" in normalized
    assert "Each row closes only through the linked child FI/binding rows" in normalized


@pytest.mark.requirements("HLA2025-BND-001", "HLA2025-BND-002", "HLA2025-BND-003")
def test_binding_and_hosted_boundary_markdown_keeps_python2025_as_main_runtime_lane() -> None:
    text = (REGISTRY_DIR / "binding_and_hosted_route_boundaries.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing reading for the three binding rows." in normalized
    assert "`tests/requirements/test_2025_tail_backlog_evidence.py`" in text
    assert "`tests/requirements/test_2025_route_parity_matrix.py`" in text
    assert "`tests/backends/test_standard_shim_artifacts.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto`" in text
    assert "`hla-backend-python2025` is the only main 2025 Python RTI implementation lane" in normalized
    assert "`hla-backend-shim` remains a compatibility wrapper and is not a runtime owner" in normalized
    assert "Java bridge packages and `hla-backend-cpp-shim` remain wrapper/binding surfaces" in normalized
    assert "Hosted FedPro is a bounded transport/runtime slice over `hla-backend-python2025`;" in normalized


@pytest.mark.requirements("HLA2025-BND-001", "HLA2025-BND-002")
def test_standard_binding_runtime_capability_markdown_keeps_bounded_binding_claim_explicit() -> None:
    text = (REGISTRY_DIR / "standard_binding_runtime_capability_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing claim for the standard Java and C++ 2025 binding routes." in normalized
    assert "artifact-gated/runtime-capability traces over the main `hla-backend-python2025` runtime" in normalized
    assert "Both Java and C++ standard-route families are parity-covered across the tracked eight scenario families" in normalized
    assert "`java-standard-2025-jpype`" in text
    assert "`java-standard-2025-py4j`" in text
    assert "`cpp-standard-2025-pybind`" in text
    assert "`cpp-standard-2025-grpc`" in text
    assert "`tests/backends/test_standard_shim_artifacts.py`" in text
    assert "`docs/evidence/shim_routes/java-standard-2025.json`" in text
    assert "`docs/evidence/shim_routes/cpp-standard-2025.json`" in text
    assert "`packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`" in text
    assert "does not claim exhaustive cross-binding behavior equivalence" in normalized


@pytest.mark.requirements("HLA2025-OMT-COMP-006", "HLA2025-OMT-COMP-039", "HLA2025-OMT-COMP-224")
def test_omt_xs_any_markdown_keeps_bounded_payload_preservation_claim_explicit() -> None:
    text = (REGISTRY_DIR / "omt_xs_any_extension_tolerance.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This bounded-proof note covers the 45 OMT component rows" in normalized
    assert "payload preservation, schema-tolerant parsing, and serializer round-trip" in normalized
    assert "does not claim arbitrary third-party extension execution semantics" in normalized
    assert "`HLA2025-OMT-COMP-006`, `HLA2025-OMT-COMP-008`" in text
    assert "`HLA2025-OMT-COMP-019`, `HLA2025-OMT-COMP-021`, `HLA2025-OMT-COMP-027`" in text
    assert "`HLA2025-OMT-COMP-102`, `HLA2025-OMT-COMP-110`, `HLA2025-OMT-COMP-134`" in text
    assert "`HLA2025-OMT-COMP-145`, `HLA2025-OMT-COMP-147`, `HLA2025-OMT-COMP-154`" in text
    assert "`HLA2025-OMT-COMP-202`, `HLA2025-OMT-COMP-204`, `HLA2025-OMT-COMP-208`" in text
    assert "### `object-model-root-and-identity`" in text
    assert "### `container-table-and-reference-extension-points`" in text
    assert "`tests/test_rti1516_2025_validation.py`" in text
    assert "`packages/hla-rti1516e/src/hla/rti1516e/fom.py`" in text


@pytest.mark.requirements("HLA2025-REQ-001")
def test_support_services_bounded_proof_markdown_keeps_python_lane_and_bounded_route_claim_explicit() -> None:
    text = (REGISTRY_DIR / "support_services_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current support-services claim as a bounded, requirement-facing proof statement." in normalized
    assert "per-service runtime traceability across the Python 2025 lanes" in normalized
    assert "hosted FedPro remains a bounded runtime slice rather than a full support-service conformance route" in normalized
    assert "`name-reservation-and-release-flows`" in text
    assert "`identity-catalog-and-handle-normalization-lookups`" in text
    assert "`factory-decode-and-hosted-support-seam`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text


@pytest.mark.requirements("HLA2025-FI-SVC-101", "HLA2025-FI-SVC-107", "HLA2025-FI-SVC-116", "HLA2025-FI-SVC-121")
def test_time_management_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "time_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing time-management claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-101`, `HLA2025-FI-SVC-102`, `HLA2025-FI-SVC-103`" in text
    assert "`HLA2025-FI-SVC-107`, `HLA2025-FI-SVC-108`, `HLA2025-FI-SVC-109`" in text
    assert "`HLA2025-FI-SVC-116`, `HLA2025-FI-SVC-117`, `HLA2025-FI-SVC-118`" in text
    assert "`HLA2025-FI-SVC-121`, `HLA2025-FI-SVC-122`, `HLA2025-FI-SVC-123`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/backends/test_shim_route_trace_evidence.py`" in text
    assert "`hla-backend-python2025`. `hla-backend-shim` is not a runtime owner" in normalized
    assert "`./tools/pitch time-window-probe`" in text
    assert "`./tools/pitch time-window-restore-state-probe`" in text
    assert "useful vendor credence" in normalized
    assert "do not replace the broader `hla-backend-python2025` proof" in text


@pytest.mark.requirements("HLA2025-REQ-001")
def test_federation_management_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "federation_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing federation-management claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-001`, `HLA2025-FI-SVC-002`, `HLA2025-FI-SVC-004`" in text
    assert "`HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-009`, `HLA2025-FI-SVC-010`" in text
    assert "`HLA2025-FI-SVC-013`, `HLA2025-FI-SVC-014`, `HLA2025-FI-SVC-015`" in text
    assert "`HLA2025-FI-SVC-018`, `HLA2025-FI-SVC-019`, `HLA2025-FI-SVC-020`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/scenarios/test_federation_management_backend_matrix.py`" in text
    assert "`hla-backend-python2025`. `hla-backend-shim` is not a runtime owner" in normalized


@pytest.mark.requirements("HLA2025-REQ-001")
def test_declaration_management_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "declaration_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing declaration-management claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-035`, `HLA2025-FI-SVC-036`, `HLA2025-FI-SVC-037`" in text
    assert "`HLA2025-FI-SVC-041`, `HLA2025-FI-SVC-042`, `HLA2025-FI-SVC-043`" in text
    assert "`HLA2025-FI-SVC-047`, `HLA2025-FI-SVC-048`, `HLA2025-FI-SVC-049`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/scenarios/test_object_management_backend_matrix.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`hla-backend-python2025`. `hla-backend-shim` is not a runtime owner" in normalized


@pytest.mark.requirements("HLA2025-REQ-001")
def test_object_management_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "object_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing object-management claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-051`, `HLA2025-FI-SVC-052`, `HLA2025-FI-SVC-053`" in text
    assert "`HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`" in text
    assert "`HLA2025-FI-SVC-065`, `HLA2025-FI-SVC-066`, `HLA2025-FI-SVC-067`" in text
    assert "`HLA2025-FI-SVC-074`, `HLA2025-FI-SVC-075`, `HLA2025-FI-SVC-076`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/scenarios/test_object_management_backend_matrix.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`hla-backend-python2025`. `hla-backend-shim` is not a runtime owner" in normalized


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ownership_management_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "ownership_management_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing ownership-management claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-083`, `HLA2025-FI-SVC-084`, `HLA2025-FI-SVC-086`" in text
    assert "`HLA2025-FI-SVC-092`, `HLA2025-FI-SVC-093`, `HLA2025-FI-SVC-094`" in text
    assert "`HLA2025-FI-SVC-085`, `HLA2025-FI-SVC-088`, `HLA2025-FI-SVC-089`" in text
    assert "`HLA2025-FI-SVC-098`, `HLA2025-FI-SVC-099`, `HLA2025-FI-SVC-100`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/scenarios/test_ownership_management_backend_matrix.py`" in text
    assert "`tests/backends/test_python_backend_object_ownership_extended.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`hla-backend-python2025`. `hla-backend-shim` is not a runtime owner" in normalized


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ddm_bounded_proof_markdown_keeps_service_family_traceability_explicit() -> None:
    text = (REGISTRY_DIR / "ddm_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current requirement-facing data-distribution- management claim as a bounded proof statement" in normalized
    assert "`HLA2025-FI-SVC-126`, `HLA2025-FI-SVC-127`, `HLA2025-FI-SVC-130`" in text
    assert "`HLA2025-FI-SVC-128`, `HLA2025-FI-SVC-129`, `HLA2025-FI-SVC-131`, `HLA2025-FI-SVC-132`, `HLA2025-FI-SVC-133`, `HLA2025-FI-SVC-137`" in text
    assert "`HLA2025-FI-SVC-134`, `HLA2025-FI-SVC-135`" in text
    assert "`HLA2025-FI-SVC-136`" in text
    assert "`tests/test_rti1516_2025_python2025_runtime.py`" in text
    assert "`tests/backends/test_python_backend_time_ddm_extended.py`" in text
    assert "`tests/scenarios/test_ddm_backend_matrix.py`" in text
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`hla-backend-python2025`. `hla-backend-shim` is not a runtime owner" in normalized
