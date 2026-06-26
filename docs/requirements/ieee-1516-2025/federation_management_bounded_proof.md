# Federation Management Bounded Proof

Source: IEEE 1516.1-2025 federation-management service rows and the repo's
current federation-lifecycle proof families.

This note records the repo's current requirement-facing federation-management
claim as a bounded proof statement for the main `hla-backend-python1516-2025`
runtime lane. It covers service-by-service runtime traceability for the 34
federation-management service rows together with the direct-lane and hosted
FedPro replay proof families for connect/create/destroy control, membership
reporting, resign and disconnect cleanup, synchronization barriers, and
save/restore lifecycle recovery. It does not claim final clause-by-clause 2025 conformance or
exhaustive cross-binding behavior equivalence.

## Service Families

Use `Evidence anchors` and `Bounded claim reading` here as owner-facing proof
vocabulary. They describe bounded evidence scope, not canonical requirement
disposition.

| Family | Rows | Evidence anchors | Bounded claim reading |
| --- | --- | --- | --- |
| Connect, create, destroy, and catalog control | `HLA2025-FI-SVC-001`, `HLA2025-FI-SVC-002`, `HLA2025-FI-SVC-004`, `HLA2025-FI-SVC-005`, `HLA2025-FI-SVC-006`, `HLA2025-FI-SVC-007` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/test_hla_factory_composition.py`, `packages/hla-rti-core/src/hla/rti/factory.py` | Closed as bounded runtime proof for connect or disconnect state, create or destroy federation control, federation listing and reporting, duplicate-create rejection, callback-model validation, and FOM-validation preconditions on the direct `python1516_2025` lane plus hosted FedPro replay. |
| Join, membership, and name-precondition control | `HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-009`, `HLA2025-FI-SVC-010` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_federation_management_backend_matrix.py` | Closed as bounded runtime proof for join preconditions, federation-execution member reporting, multi-participation visibility, and joined-state or federate-name uniqueness constraints across the main `python1516_2025` lane and hosted FedPro replay. |
| Resign, disconnect, loss, and member cleanup | `HLA2025-FI-SVC-003`, `HLA2025-FI-SVC-011`, `HLA2025-FI-SVC-012` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_federation_management_backend_matrix.py` | Closed as bounded runtime proof for connectionLost teardown, resign and disconnect preconditions, federate-resigned callback delivery, and federation member cleanup after resign, disconnect, or loss on both the direct `python1516_2025` lane and hosted FedPro replay. |
| Synchronization barriers and targeted callbacks | `HLA2025-FI-SVC-013`, `HLA2025-FI-SVC-014`, `HLA2025-FI-SVC-015`, `HLA2025-FI-SVC-016`, `HLA2025-FI-SVC-017` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_federation_management_backend_matrix.py` | Closed as bounded runtime proof for synchronization-point registration, announce or achieved flow, federationSynchronized completion, failure cases, late joiners, multiple sync points, and targeted sync callback routing. |
| Save and restore lifecycle control | `HLA2025-FI-SVC-018`, `HLA2025-FI-SVC-019`, `HLA2025-FI-SVC-020`, `HLA2025-FI-SVC-021`, `HLA2025-FI-SVC-022`, `HLA2025-FI-SVC-023`, `HLA2025-FI-SVC-024`, `HLA2025-FI-SVC-025`, `HLA2025-FI-SVC-026`, `HLA2025-FI-SVC-027`, `HLA2025-FI-SVC-028`, `HLA2025-FI-SVC-029`, `HLA2025-FI-SVC-030`, `HLA2025-FI-SVC-031`, `HLA2025-FI-SVC-032`, `HLA2025-FI-SVC-033`, `HLA2025-FI-SVC-034` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_save_restore_backend_matrix.py` | Closed as bounded runtime proof for request, initiate, status, fail, abort, and completion control flow for federation save or restore across the current Python 2025 RTI lane and hosted FedPro route. |

## Federation-Lifecycle Closure Notes

- The repo's direct-lane and hosted FedPro replay proof families also cover
  participant recovery after restore, multi-federate save/restore tracking, and
  rollback to saved participant state rather than dirty future state.
- Execution-membership guard coverage is part of this bounded claim.
  Before join, after resign, or after disconnect, the repo proves that update,
  interaction, query, and DDM-side execution attempts reject with
  `NotConnected` or `FederateNotExecutionMember` instead of silently mutating
  runtime state.
- The same execution-membership slice also proves that
  `destroyFederationExecution` rejects with `FederatesCurrentlyJoined` until
  the last joined federate resigns.
- After a successful destroy, repeated destroy or join attempts against that
  missing federation are expected to fail with
  `FederationExecutionDoesNotExist`.
- That focused slice now includes the hosted 2025 gRPC/FedPro route and the
  REST-hosted Python route for the lifecycle-negative, join-precondition, and
  resign-precondition proofs.
- Current exact execution-membership evidence anchors for this 2025 reading
  are:
  - direct runtime:
    - `tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_runs_federation_lifecycle_negative_scenario_end_to_end`
    - `tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_runs_resign_precondition_scenario_end_to_end`
    - `tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_reports_federation_executions_and_members`
  - shared scenario anchors:
    - `tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_join_precondition_matrix`
    - `tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_precondition_matrix`
  - hosted gRPC/FedPro route:
    - `tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_federation_lifecycle_negative_scenario_over_fedpro_route`
    - `tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_join_precondition_scenario_over_fedpro_route`
    - `tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_resign_precondition_scenario_over_fedpro_route`
  - hosted REST route:
    - `tests/transport/test_rest_transport.py::test_2025_rest_transport_server_runs_shared_federation_lifecycle_negative_scenario`
    - `tests/transport/test_rest_transport.py::test_2025_rest_transport_server_runs_shared_join_precondition_scenario`
    - `tests/transport/test_rest_transport.py::test_2025_rest_transport_server_runs_shared_resign_precondition_scenario`
- The primary runtime owner behind the executable anchors above is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner for
  these federation-management rows.
- The claim remains bounded: Java and C++ bindings still rely on
  artifact/runtime-capability evidence rather than exhaustive behavior
  equivalence, and hosted FedPro remains a bounded runtime slice rather than a
  full cross-binding conformance route.

Use these rerun commands first when the question is specifically about joined
state, destroy preconditions, or whether an update/send/query path should have
been rejected after a membership change:

- `./tools/test-focus run execution-membership`
- `./tools/python verify-main-2025`
- `./tools/python verify-routes-2025`
