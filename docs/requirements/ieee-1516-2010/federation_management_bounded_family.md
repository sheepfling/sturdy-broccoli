# 2010 Federation-Management Bounded Family

Use this page when the question is:

- is the focused 2010 Clause 4 federation-management family now fully closed
  for the Python RTI lane?
- which single document owns the final human-facing FM closeout reading?
- what direct runtime evidence eliminated the former FM bounded tail?

Short answer:

- the focused Python 2010 FM family is now fully `mapped`
- the former FM bounded tail was closed with direct runtime witnesses
- this document remains the canonical human-facing closeout note for that work

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/federation_management_bounded_family.md`
- edition-wide canonical requirement truth:
  `requirements/2010/canonical_requirements.json`
- edition-wide backend-resolution companion:
  `requirements/2010/backend_resolution.json`
- family mapping bridge:
  `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv`
- generated projection bridge:
  `requirements/2010/traceability_matrix.csv`
- supporting decomposition seed:
  `requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv`
- primary shards:
  - `unit-scenarios-light`
  - `unit-python-core` for lifecycle and save/restore slices that stay within
    the local backend lane
- maintained focused rerun views:
  - `./tools/test-focus run execution-membership`
  - `./tools/test-focus run backends`

## Final State

- this owner note is the canonical closeout reading for the former `CAP-FM`
  bounded family
- `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv` is now fully
  `mapped`
- the closeout was achieved by adding direct lifecycle, FDD/MIM,
  lost-federate, and omitted-logical-time-default witnesses
- future edits should only reopen FM rows if the repo widens its Clause 4 claim
  beyond the currently witnessed Python 2010 behavior

## Reopen Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the repo decides to widen Clause 4 claims beyond the current direct
   witnesses
2. a backend change invalidates one of the direct FM witnesses
3. the current family owner ledger stops being the right canonical location for
   the Clause 4 federation-management story

If none of those happen, preserve the current mapped reading and do not
reintroduce bounded-tail language.

## Current Family Shape

The current owner ledger has `632` federation-management packet rows:

- `632 mapped`

No FM packet rows remain `partial`.

## Former Tail

The former FM bounded tail is now closed:

- the lost-federate overview row is directly mapped through loss-trigger,
  callback-model, membership-teardown, pending-acquisition-cancellation,
  owned-object-delete, and unconditional-divest cleanup witnesses
- the create-federation optional logical-time row is directly mapped through
  explicit-time and omitted-default witnesses that now prove the standard
  `HLAfloat64Time` default when the argument is omitted

## What Is Already Proved

The current repo directly proves most of the Clause 4 executable surface,
including:

- connect, disconnect, create, destroy, join, and resign service behavior
- synchronization registration, announcement, achievement, and federation-wide
  completion paths
- save and restore request, status, outcome, abort, and callback families
- direct runtime `connectionLost` callback delivery, lost-federate MOM
  reporting, post-loss execution-membership teardown, and direct
  disconnected-state transition after `connectionLost` delivery
- direct lost-federate automatic-resign cleanup for pending acquisitions,
  owned-object deletion, and unconditional attribute divestiture
- direct connected, joined, resigned, and disconnected lifecycle-state
  management for the Python 2010 lane
- direct current-FDD maintenance with supplied FOM modules plus accepted
  standard MIM exposure
- direct omitted-logical-time defaulting to the RTI-provided
  `HLAfloat64Time` representation
- direct disconnected-state transition after `connectionLost` delivery
- direct joined-live precondition coverage and callback-model dispatch
  coverage for `connectionLost`
- direct connect, join-generated-name, resign-directive, and
  federation-synchronized payload argument coverage
- direct callback-failure wrapping for `connectionLost` and
  `reportFederationExecutions`, plus MOM service-reporting visibility for
  `listFederationExecutions`
- direct scheduled-save replacement coverage for `requestFederationSave`, and
  direct cancel-capable resign coverage for pending ownership acquisitions
- direct `RTIinternalError` coverage for corrupted `listFederationExecutions`
  runtime state
- representative MOM-observer visibility for key lifecycle and save/restore
  states
- many direct negative-path guards and callback outcome paths
- hosted transport equivalence coverage for the main federation-management
  lifecycle and save/restore lanes

Primary evidence anchors:

- `tests/backends/test_python_backend_federation_extended.py`
- `tests/backends/test_python_backend_federation_extended.py::test_force_federate_loss_delivers_connection_lost_and_clears_execution_membership`
- `tests/backends/test_python_backend_federation_extended.py::test_force_federate_loss_requires_joined_live_victim_and_honors_callback_model`
- `tests/backends/test_python_backend_federation_extended.py::test_force_federate_loss_honors_cancel_delete_divest_automatic_resign_cleanup`
- `tests/backends/test_python_backend_federation_extended.py::test_force_federate_loss_honors_unconditional_divest_automatic_resign_cleanup`
- `tests/backends/test_python_backend_federation_extended.py::test_federation_management_lifecycle_states_cover_connected_joined_resigned_and_disconnected`
- `tests/backends/test_python_backend_federation_extended.py::test_create_federation_execution_maintains_current_fdd_modules_and_standard_mim`
- `tests/backends/test_python_backend_federation_extended.py::test_create_federation_execution_defaults_to_hlafloat64_time_when_logical_time_is_omitted`
- `tests/backends/test_python_backend_federation_extended.py::test_create_federation_execution_accepts_explicit_logical_time_implementation`
- `tests/backends/test_python_backend_federation_extended.py::test_connection_lost_and_report_federation_executions_wrap_callback_failures_as_federate_internal_error`
- `tests/backends/test_python_backend_federation_extended.py::test_list_federation_executions_is_observable_through_mom_service_invocation_reporting`
- `tests/backends/test_python_backend_federation_extended.py::test_list_federation_executions_surfaces_rti_internal_error_for_corrupt_runtime_state`
- `tests/backends/test_python_backend_federation_extended.py::test_request_federation_save_latest_scheduled_request_supersedes_prior_requested_save`
- `tests/backends/test_python_backend_federation_extended.py::test_resign_canceling_directives_clear_pending_acquisition_requests`
- `tests/scenarios/test_federation_management_backend_matrix.py`
- `tests/verification/test_requirements_ledger_v013.py`
- `requirements/2010/traceability_matrix.csv`

Execution-membership guard coverage is also part of the current 2010 bounded
reading:

- before join, after resign, or after disconnect, update, interaction, query,
  and DDM-side execution attempts are expected to fail with
  `NotConnected` or `FederateNotExecutionMember`
- destroy remains rejected with `FederatesCurrentlyJoined` until the joined
  federates resign
- after a successful destroy, repeated destroy or join attempts against that
  federation are expected to fail with `FederationExecutionDoesNotExist`
- those cross-clause execution-state rules are intentionally read together with
  [`object_management_bounded_family.md`](object_management_bounded_family.md)
  and the focused `execution-membership` rerun slice rather than pretending
  they belong only to one Clause 4 row

Current exact execution-membership evidence anchors for this 2010 reading:

- federation-management backend guards:
  - `tests/backends/test_python_backend_federation_extended.py::test_destroy_federation_execution_requires_no_joined_federates`
  - `tests/backends/test_python_backend_federation_extended.py::test_resign_federation_execution_rejects_not_connected_and_not_joined`
  - `tests/backends/test_python_backend_federation_extended.py::test_disconnect_requires_resign_and_marks_backend_not_connected`
- object/update/query and DDM guard witnesses that share the same joined-state
  rule:
  - `tests/backends/test_python_backend_object_ownership_extended.py::test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore`
  - `tests/backends/test_python_backend_object_ownership_extended.py::test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore`
  - `tests/backends/test_python_backend_object_ownership_extended.py::test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore`
  - `tests/backends/test_python_backend_time_ddm_extended.py::test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`
  - `tests/backends/test_python_backend_time_ddm_extended.py::test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`
- shared federation-management scenario guards:
  - `tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_join_precondition_matrix`
  - `tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_precondition_matrix`

Use these rerun commands before dropping to raw file paths:

- `./tools/test-focus run execution-membership` for join, resign, destroy,
  disconnect, and not-joined guard questions
- `./tools/test-focus run backends` for broader 2010 federation-management
  backend behavior
- `./tools/test-surface run unit-scenarios-light` when the narrowest owning
  shard is still the scenario layer

## Good Reading

Good reading:

- federation management is fully mapped for the focused Python 2010 lane
- the closeout is anchored in direct runtime witnesses rather than plan prose
- the owner and rollup surfaces agree on a fully mapped Clause 4 family

Bad reading:

- Clause 4 still carries a hidden bounded tail
- lifecycle or save/restore behavior is still speculative
- the closeout came from documentation harmonization without runtime evidence

## Reading Order

1. `requirements/2010/canonical_requirements.json`
2. `requirements/2010/backend_resolution.json`
3. `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv`
4. `requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv`
5. `requirements/2010/traceability_matrix.csv`
6. `tests/backends/test_python_backend_federation_extended.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
