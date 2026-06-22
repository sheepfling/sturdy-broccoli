from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_DIR = ROOT / "docs/requirements/ieee-1516-2025"
REGISTRY = REGISTRY_DIR / "requirements.json"


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
        "callback_binding_deltas.md",
        "declaration_management_bounded_proof.md",
        "ddm_bounded_proof.md",
        "federation_management_bounded_proof.md",
        "hosted_fedpro_bounded_proof.md",
        "framework_rules.md",
        "federate_interface.md",
        "object_management_bounded_proof.md",
        "omt_xs_any_extension_tolerance.md",
        "omt.md",
        "ownership_management_bounded_proof.md",
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
        "federation_management_bounded_proof.md",
        "declaration_management_bounded_proof.md",
        "object_management_bounded_proof.md",
        "ownership_management_bounded_proof.md",
        "ddm_bounded_proof.md",
        "support_services_bounded_proof.md",
        "standard_binding_runtime_capability_bounded_proof.md",
        "time_management_bounded_proof.md",
        "hosted_fedpro_bounded_proof.md",
        "binding_and_hosted_route_boundaries.md",
        "callback_binding_deltas.md",
        "omt_xs_any_extension_tolerance.md",
    ):
        assert f"`{filename}`" in text

    assert "bounded requirement-facing proof note" in normalized
    assert "main `python2025` lane plus hosted replay" in normalized
    assert "Java, C++, and hosted FedPro binding/route boundaries over the main `python2025` runtime" in text


@pytest.mark.requirements("HLA2025-BND-003", "HLA2025-MIL-001", "HLA2025-MIL-002")
def test_hosted_fedpro_bounded_proof_markdown_keeps_main_runtime_identity_and_boundary_explicit() -> None:
    text = (REGISTRY_DIR / "hosted_fedpro_bounded_proof.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "This note records the repo's current hosted-route claim for `python-2025-fedpro-grpc`." in normalized
    assert "bounded transport/runtime slice rather than a second RTI implementation family" in normalized
    assert "The hosted route is parity-covered across the tracked scenario families" in normalized
    assert "`tests/transport/test_grpc_transport_2025.py`" in text
    assert "`tests/scenarios/test_python_route_parity.py`" in text
    assert "`docs/backend_route_inventory_remote.md`" in text
    assert "`packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`" in text
    assert "`federation_lifecycle`" in text
    assert "`time_management`" in text
    assert "`support_services`" in text
    assert "`hla-backend-python2025`" in text
    assert "does not claim that `python-2025-fedpro-grpc` is a second full RTI implementation lane" in normalized


@pytest.mark.requirements("HLA2025-REQ-001")
def test_ieee_1516_2025_requirements_readme_tracks_current_runtime_proof_lane() -> None:
    text = (REGISTRY_DIR / "README.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "## Current Technical Lane" in text
    assert "deeper runtime-proof expansion over the promoted `python2025` RTI surface" in normalized
    assert "route-parity and hosted FedPro evidence that replays those runtime families" in normalized
    assert "wrapper-only shim boundaries" in normalized
    assert "FOM/OMT validation still matters inside that lane" in normalized
    assert "one proof family inside the broader 2025 runtime-evidence closeout" in normalized


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
