# Binding and Hosted Route Boundaries

Source: IEEE 1516.1-2025 binding and hosted-route proof rows.

This note records the repo's current requirement-facing reading for the three
binding rows. It does not introduce a second Python RTI lane. The main 2025
Python RTI implementation lane is `hla-backend-python1516-2025`; the Java and C++
packages remain adapter/binding surfaces over that runtime, and the hosted
FedPro route remains a transport-facing runtime slice over the same lane.

| ID | Summary | Current repo evidence anchors | Current bounded reading |
| --- | --- | --- | --- |
| HLA2025-BND-001 | Java binding surface | `tests/requirements/test_2025_tail_backlog_evidence.py`, `tests/requirements/test_2025_route_parity_matrix.py`, `tests/backends/test_standard_shim_artifacts.py`, `requirements/2025/STRICT_DOC_INVENTORY.json`, `requirements/2025/SOURCE_TRACE.md`, `docs/evidence/shim_routes/java-standard-2025.json` | Closed as bounded Java binding traceability: it proves source-surface accounting and scenario/runtime-capability parity over `hla-backend-python1516-2025`, not an independent Java RTI or full cross-binding behavior conformance pass. |
| HLA2025-BND-002 | C++ binding surface | `tests/requirements/test_2025_tail_backlog_evidence.py`, `tests/requirements/test_2025_route_parity_matrix.py`, `tests/backends/test_standard_shim_artifacts.py`, `requirements/2025/SOURCE_TRACE.md`, `docs/evidence/shim_routes/cpp-standard-2025.json`, `docs/evidence/cpp-intake/cpp-standard-2025-2025-pybind.json` | Closed as bounded C++ binding traceability: it proves header/API source trace plus scenario/runtime-capability parity over `hla-backend-python1516-2025`, not an independent C++ RTI or full cross-binding behavior conformance pass. |
| HLA2025-BND-003 | Hosted FedPro/protobuf surface | `tests/requirements/test_2025_tail_backlog_evidence.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`, `packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto`, `packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto`, `packages/hla-transport-grpc/proto/rti1516_2025/fedpro/FederateAmbassador_2025.proto` | Closed as bounded hosted-route traceability: it proves typed request/response/callback transport parity and hosted replay over `hla-backend-python1516-2025`, not a second RTI implementation lane and not a full RTI semantics or exhaustive cross-binding conformance pass. |

## Boundary Notes

- `hla-backend-python1516-2025` is the only main 2025 Python RTI implementation lane
  behind these rows.
- `hla-backend-shim` remains a legacy compatibility shim and is not a runtime owner
  for the binding rows above.
- Java bridge packages and `hla-backend-cpp-shim` remain wrapper/binding
  surfaces over the main Python 2025 runtime rather than alternate 2025 RTIs.
- Hosted FedPro is a bounded transport/runtime slice over
  `hla-backend-python1516-2025`; its remaining proof burden is transport-seam and
  cross-binding evidence, not evidence that the core 2025 Python RTI lane is
  owned somewhere else.
- The repo should not promote these rows to full binding or hosted conformance
  claims unless it gains exhaustive behavior-equivalence evidence beyond the
  current route-parity and runtime-capability traces.
