# Callback, Configuration, and Binding Delta Requirements

Source: IEEE 1516.1-2025 callback/configuration/binding delta backlog rows.

These rows remain `duplicate/umbrella` in the harmonization ledger. They are
not standalone runtime claims. Each row closes only through the linked child
FI/binding rows plus executable evidence on the main `hla-backend-python2025`
runtime lane and the bounded route artifacts that sit above it.

| ID | Summary | Linked child rows | Current repo evidence anchors | Current bounded reading |
| --- | --- | --- | --- | --- |
| HLA2025-FI-CB-001 | Callback model selection | `HLA2025-FI-005`, `HLA2025-MOD-001` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/test_hla_factory_composition.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through connect/auth/configuration coverage that proves IMMEDIATE and EVOKED model selection on the direct `python1516_2025` lane and the hosted FedPro route. |
| HLA2025-FI-CB-002 | Evoke Callback | `HLA2025-FI-SVC-193` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/backends/test_python_backend_support_services.py`, `docs/evidence/shim_routes/java-standard-2025.json` | Closed through explicit EVOKED callback dispatch behavior on the runtime lane plus bounded route-surface evidence for Java/C++ wrapper methods. |
| HLA2025-FI-CB-003 | Evoke Multiple Callbacks | `HLA2025-FI-SVC-194` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/backends/test_python_backend_support_services.py`, `docs/evidence/shim_routes/java-standard-2025.json` | Closed through queue-drain timing behavior on the runtime lane plus route-surface evidence for wrapper parity. |
| HLA2025-FI-CB-004 | Enable/Disable Callbacks | `HLA2025-FI-SVC-195`, `HLA2025-FI-SVC-196` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/backends/test_python_backend_support_services.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through callback-control service behavior on the runtime lane and explicit hosted route transport calls for enable/disable semantics. |
| HLA2025-FI-CB-005 | Federate Resigned callback | `HLA2025-FI-SVC-012` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through forced/automatic resign coverage and the corresponding federate callback/reporting behavior on the direct and hosted `python1516_2025` surfaces. |
| HLA2025-FI-CB-006 | Federation execution member reporting | `HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-009` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through explicit `reportFederationExecutions` and `reportFederationExecutionMembers` callback proof on the runtime lane and hosted FedPro replay. |
| HLA2025-FI-CB-007 | Directed interaction callback parameterization | `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`, `HLA2025-BND-003` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py` | Closed through distinct directed send/receive runtime semantics and bounded FedPro route parity, not by reusing ordinary interaction proof alone. |
| HLA2025-FI-CB-008 | Flush Queue Grant callback | `HLA2025-FI-SVC-112` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through explicit `flushQueueGrant` callback behavior on the runtime lane and hosted transport callback decoding, separate from ordinary timeAdvanceGrant proof. |
| HLA2025-FI-CFG-001 | Configuration and additional settings result | `HLA2025-FI-005`, `HLA2025-MOD-001`, `HLA2025-BND-003` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/test_hla_factory_composition.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through connect-time configuration/result semantics on the direct lane plus hosted/local-settings route coverage. |
| HLA2025-FI-AUTH-001 | Authorization credentials | `HLA2025-FI-005`, `HLA2025-MOD-001`, `HLA2025-BND-003` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/test_hla_factory_composition.py`, `packages/hla-rti-core/src/hla/rti/factory.py` | Closed through explicit `HLAnoCredentials` and `HLAplainTextPassword` authorization validation on the main `python1516_2025` lane. |
| HLA2025-BIND-FEDPRO-001 | FedPro protocol split | `HLA2025-BND-003`, `HLA2025-FI-004` | `tests/transport/test_grpc_transport_2025.py`, `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`, `packages/hla-transport-grpc/proto/rti1516_2025/fedpro` | Closed as a bounded wire-surface row: it proves hosted FedPro request/response/callback parity over `hla-backend-python2025`, not an independent RTI implementation lane. |
| HLA2025-BIND-JAVA-CPP-001 | Java/C++ binding split | `HLA2025-BND-001`, `HLA2025-BND-002`, `HLA2025-FI-003`, `HLA2025-FI-004` | `tests/requirements/test_2025_route_parity_matrix.py`, `tests/backends/test_standard_shim_artifacts.py`, `docs/evidence/shim_routes/route_traces` | Closed as a bounded binding-capability row: it proves adapter/runtime-capability and route-trace parity over the `python1516_2025` runtime, not full independent Java/C++ RTI semantics. |

## Closure Notes

- `HLA2025-FI-CB-001` through `HLA2025-BIND-JAVA-CPP-001` remain umbrella
  rows because their normative force is already carried by the linked child FI,
  callback-control, time, auth, configuration, and binding rows above.
- The repo should not promote these rows to standalone `covered` runtime claims
  unless they gain narrower executable proof than the child rows already carry.
- The primary runtime owner behind the executable anchors above is
  `hla-backend-python2025`.
- `hla-backend-shim`, `hla-backend-cpp-shim`, and the Java bridge packages are
  wrapper/binding surfaces over that runtime lane; they are not alternate 2025
  Python RTI implementations.
