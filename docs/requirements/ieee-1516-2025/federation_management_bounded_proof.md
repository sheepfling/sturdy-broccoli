# Federation Management Bounded Proof

Source: IEEE 1516.1-2025 federation-management service rows and the repo's
current federation-lifecycle proof families.

This note records the repo's current requirement-facing federation-management
claim as a bounded proof statement for the main `hla-backend-python2025`
runtime lane. It covers service-by-service runtime traceability for the 34
federation-management service rows together with the direct and hosted proof
families for connect/create/destroy control, membership reporting, resign and
disconnect cleanup, synchronization barriers, and save/restore lifecycle
recovery. It does not claim final clause-by-clause 2025 conformance or
exhaustive cross-binding behavior equivalence.

## Service Families

| Family | Rows | Current repo evidence anchors | Current bounded reading |
| --- | --- | --- | --- |
| Connect, create, destroy, and catalog control | `HLA2025-FI-SVC-001`, `HLA2025-FI-SVC-002`, `HLA2025-FI-SVC-004`, `HLA2025-FI-SVC-005`, `HLA2025-FI-SVC-006`, `HLA2025-FI-SVC-007` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/test_hla_factory_composition.py`, `packages/hla-rti-core/src/hla/rti/factory.py` | Closed as bounded runtime proof for connect or disconnect state, create or destroy federation control, federation listing and reporting, duplicate-create rejection, callback-model validation, and FOM-validation preconditions on the direct and hosted `python2025` routes. |
| Join, membership, and name-precondition control | `HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-009`, `HLA2025-FI-SVC-010` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_federation_management_backend_matrix.py` | Closed as bounded runtime proof for join preconditions, federation-execution member reporting, multi-participation visibility, and joined-state or federate-name uniqueness constraints across the main `python2025` lane and hosted FedPro replay. |
| Resign, disconnect, loss, and member cleanup | `HLA2025-FI-SVC-003`, `HLA2025-FI-SVC-011`, `HLA2025-FI-SVC-012` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_federation_management_backend_matrix.py` | Closed as bounded runtime proof for connectionLost teardown, resign and disconnect preconditions, federate-resigned callback delivery, and federation member cleanup after resign, disconnect, or loss on both the direct and hosted `python2025` routes. |
| Synchronization barriers and targeted callbacks | `HLA2025-FI-SVC-013`, `HLA2025-FI-SVC-014`, `HLA2025-FI-SVC-015`, `HLA2025-FI-SVC-016`, `HLA2025-FI-SVC-017` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_federation_management_backend_matrix.py` | Closed as bounded runtime proof for synchronization-point registration, announce or achieved flow, federationSynchronized completion, failure cases, late joiners, multiple sync points, and targeted sync callback routing. |
| Save and restore lifecycle control | `HLA2025-FI-SVC-018`, `HLA2025-FI-SVC-019`, `HLA2025-FI-SVC-020`, `HLA2025-FI-SVC-021`, `HLA2025-FI-SVC-022`, `HLA2025-FI-SVC-023`, `HLA2025-FI-SVC-024`, `HLA2025-FI-SVC-025`, `HLA2025-FI-SVC-026`, `HLA2025-FI-SVC-027`, `HLA2025-FI-SVC-028`, `HLA2025-FI-SVC-029`, `HLA2025-FI-SVC-030`, `HLA2025-FI-SVC-031`, `HLA2025-FI-SVC-032`, `HLA2025-FI-SVC-033`, `HLA2025-FI-SVC-034` | `tests/test_rti1516_2025_python2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_save_restore_backend_matrix.py` | Closed as bounded runtime proof for request, initiate, status, fail, abort, and completion control flow for federation save or restore across the current Python 2025 RTI lane and hosted FedPro route. |

## Federation-Lifecycle Closure Notes

- The repo's direct and hosted proof families also cover participant recovery
  after restore, multi-federate save/restore tracking, and rollback to saved
  participant state rather than dirty future state.
- The primary runtime owner behind the executable anchors above is
  `hla-backend-python2025`. `hla-backend-shim` is not a runtime owner for
  these federation-management rows.
- The claim remains bounded: Java and C++ bindings still rely on
  artifact/runtime-capability evidence rather than exhaustive behavior
  equivalence, and hosted FedPro remains a bounded runtime slice rather than a
  full cross-binding conformance route.
