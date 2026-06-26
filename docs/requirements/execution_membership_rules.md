# Execution-Membership Rules

Use this page when the question is:

- do the `2010` and `2025` requirement surfaces explicitly cover basic
  execution-state rules?
- where do create, join, resign, destroy, update, delete, query, and
  region-gated not-joined rules live?
- which tests should I rerun before changing execution-membership behavior?

Short answer:

- yes, both editions already carry explicit owner rows and executable anchors
  for the basic execution-membership state machine
- the same core rule is read across federation-management, object-management,
  and DDM owner surfaces rather than pretending it belongs to only one clause
- this page is the cross-edition index for that rule set
- this is also the canonical "have we joined yet?" owner note for create,
  join, resign, destroy, update, delete, query, and region-gated DDM
  behavior

## Core State-Machine Reading

For both editions, the intended execution-membership reading is:

- `NotConnected` before connect or after disconnect
- `FederateNotExecutionMember` before join and again after resign
- `FederatesCurrentlyJoined` when destroy is attempted while federates are
  still joined
- `FederationExecutionDoesNotExist` after destroy succeeds and a later destroy
  or join targets the missing federation

The lifecycle services at the center of this state machine are:

- `createFederationExecution`
- `joinFederationExecution`
- `resignFederationExecution`
- `destroyFederationExecution`

The practical service-level rule is also the same in both editions:

- create must happen before join on the exercised execution path
- join must happen before execution-affecting object, interaction, query, and
  region-gated DDM services
- after resign, those same services must keep rejecting the caller as no
  longer joined
- destroy must stay blocked until the federation is empty

Concrete execution-affecting calls that are part of this rule set include:

- `registerObjectInstance` and object-name reservation or release calls that
  require the caller to be an execution member on the exercised path
- `deleteObjectInstance` and `localDeleteObjectInstance`
- `updateAttributeValues`
- `sendInteraction`
- `requestAttributeValueUpdate`
- `queryAttributeTransportationType`
- `sendInteractionWithRegions`
- `requestAttributeValueUpdateWithRegions`

In plain terms:

- before join, these calls reject the caller as `FederateNotExecutionMember`
- after resign, the same calls still reject the caller as no longer joined
- while federates remain joined, destroy rejects with
  `FederatesCurrentlyJoined`
- after destroy succeeds, later destroy or join attempts reject with
  `FederationExecutionDoesNotExist`

## 2010 Owner Surface

Start with:

- [`ieee-1516-2010/README.md`](ieee-1516-2010/README.md)
- [`ieee-1516-2010/federation_management_bounded_family.md`](ieee-1516-2010/federation_management_bounded_family.md)
- [`ieee-1516-2010/object_management_bounded_family.md`](ieee-1516-2010/object_management_bounded_family.md)
- [`ieee-1516-2010/data_distribution_management_bounded_family.md`](ieee-1516-2010/data_distribution_management_bounded_family.md)

Representative 2010 requirement rows:

- `HLA1516.1-FM-4_2-RTIAPI-001-EXC` for connect-state guard exceptions
- `HLA1516.1-FM-4_6-RTIAPI-001-EXC` for destroy rejection while federates are
  still joined and for missing-federation rejection after destroy
- `HLA1516.1-FM-4_9-RTIAPI-001-EXC` for join preconditions
- `HLA1516.1-FM-4_10-RTIAPI-001-EXC` for resign preconditions and joined-state
  exit guards
- `HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001` for register-before-join
  rejection
- `HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-PRE-001` and
  `HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001` for update-state gating
- `HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001` and
  `HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001` for interaction-send gating
- `HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001` and
  `HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-PRE-001` for delete-state
  gating
- `HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-PRE-001` and
  `HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-PRE-001` for
  request/query joined-state guards
- `HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001` and
  `HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-PRE-001` for
  region-gated joined-state guards

Primary 2010 executable anchors:

- `tests/backends/test_python_backend_federation_extended.py::test_destroy_federation_execution_requires_no_joined_federates`
- `tests/backends/test_python_backend_federation_extended.py::test_resign_federation_execution_rejects_not_connected_and_not_joined`
- `tests/backends/test_python_backend_federation_extended.py::test_disconnect_requires_resign_and_marks_backend_not_connected`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_send_interaction_rejects_not_connected_not_joined_invalid_inputs_and_invalid_time`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore`
- `tests/backends/test_python_backend_time_ddm_extended.py::test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`
- `tests/backends/test_python_backend_time_ddm_extended.py::test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`
- `tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_join_precondition_matrix`
- `tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_precondition_matrix`

## 2025 Owner Surface

Start with:

- [`ieee-1516-2025/README.md`](ieee-1516-2025/README.md)
- [`ieee-1516-2025/federation_management_bounded_proof.md`](ieee-1516-2025/federation_management_bounded_proof.md)
- [`ieee-1516-2025/object_management_bounded_proof.md`](ieee-1516-2025/object_management_bounded_proof.md)
- [`ieee-1516-2025/ddm_bounded_proof.md`](ieee-1516-2025/ddm_bounded_proof.md)

Representative 2025 requirement rows:

- `HLA2025-FI-004-XT-REQ-CONNECT_BEFORE_RTI_INTERACTION` for the direct
  connect-before-service guard
- `HLA2025-FI-SVC-005` for destroy preconditions and joined-federate
  rejection
- `HLA2025-FI-SVC-008` for federation membership listing and reporting
- `HLA2025-FI-SVC-010` for join preconditions and membership entry
- `HLA2025-FI-SVC-011` for resign preconditions and membership exit cleanup
- `HLA2025-FI-SVC-051` and `HLA2025-FI-SVC-057` for reserve/register
  joined-state gating
- `HLA2025-FI-SVC-059` for update-state gating
- `HLA2025-FI-SVC-061` for interaction-send joined-state gating
- `HLA2025-FI-SVC-065` and `HLA2025-FI-SVC-067` for delete/local-delete
  joined-state gating
- `HLA2025-FI-SVC-070` and `HLA2025-FI-SVC-077` for request/query joined-state
  guards
- `HLA2025-FI-SVC-136` and `HLA2025-FI-SVC-137` for region-gated joined-state
  guards

Primary 2025 executable anchors:

- `tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_runs_federation_lifecycle_negative_scenario_end_to_end`
- `tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_runs_resign_precondition_scenario_end_to_end`
- `tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_reports_federation_executions_and_members`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_send_interaction_rejects_not_connected_not_joined_invalid_inputs_and_invalid_time`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore`
- `tests/backends/test_python_backend_time_ddm_extended.py::test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`
- `tests/backends/test_python_backend_time_ddm_extended.py::test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`
- `tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_federation_lifecycle_negative_scenario_over_fedpro_route`
- `tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_join_precondition_scenario_over_fedpro_route`
- `tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_resign_precondition_scenario_over_fedpro_route`
- `tests/transport/test_rest_transport.py::test_2025_rest_transport_server_runs_shared_federation_lifecycle_negative_scenario`
- `tests/transport/test_rest_transport.py::test_2025_rest_transport_server_runs_shared_join_precondition_scenario`
- `tests/transport/test_rest_transport.py::test_2025_rest_transport_server_runs_shared_resign_precondition_scenario`

## Rerun Surface

Use these first before digging through broader matrices:

- `./tools/test-focus run execution-membership`
- `./tools/test-focus run backends`
- `./tools/python verify-main-2025`
- `./tools/python verify-routes-2025`

## Practical Rule

- if the question is about join, resign, destroy, or membership listing,
  start with the federation-management owner note for the edition you care
  about
- if the question is about update, delete, send, request, or query behavior
  before join or after resign, read the object-management and DDM owner notes
  together with the federation-management owner
- if the question is "is this proved on the hosted routes too?", rerun the
  `execution-membership` slice and read the 2025 bounded proof notes
