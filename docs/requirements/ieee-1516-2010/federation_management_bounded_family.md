# 2010 Federation-Management Bounded Family

Use this page when the question is:

- why does the 2010 Clause 4 federation-management family still carry
  `partial` rows even though most lifecycle, synchronization, save, and restore
  services are already directly tested?
- which single document owns the remaining `CAP-FM` partial pattern?
- are those partial rows still vague, or already in an explicit bounded final
  state?

Short answer:

- the remaining `CAP-FM` partial rows are already in an explicit bounded family
  state
- the canonical owner ledger stays `partial` for those rows
- the bounded reasons are now structured and reviewable instead of implied

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/federation_management_bounded_family.md`
- canonical source owner:
  `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv`
- broad bridge:
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

## Final Claim Rule

- keep the remaining Clause 4 family rows `partial` when the repo already
  proves the main service surface, signature shape, major preconditions,
  representative callback delivery, save/restore outcomes, and many state
  transitions, but does not yet prove every imported packet slice as a one-row
  exhaustive witness
- do not describe these rows as missing federation-management services
- do not describe these rows as unsupported lifecycle behavior
- do not flatten the family into `mapped` merely because the primary lifecycle
  and save/restore paths are strong
- treat the current state as an explicit bounded final reading of the present
  evidence, not as hidden uncertainty

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-FM`
  partial family
- the remaining rows are not waiting on wording cleanup; they are already in
  their intended bounded supported-scope presentation
- the unresolved part is only optional future row-level decomposition or
  broader proof granularity, not ambiguity about whether the currently
  exercised Clause 4 service surface exists
- keep the family rows `partial` in
  `hla1516_1_fm_detailed_reconciliation.csv` unless narrower direct proof is
  actually added for the remaining packet slices

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the remaining `ARG`, `EFF`, `CB_ORD`, `EXC`, or residual rows gain new
   direct decomposition or narrower executable witnesses
2. the repo decides to make a stronger one-row-per-packet Clause 4 claim
3. the current family owner ledger stops being the right canonical location for
   the bounded Clause 4 federation-management story

If none of those happen, preserve the current bounded family reading and do not
keep describing `CAP-FM` as vague or structurally unfinished.

## Current Family Shape

The current owner ledger has `632` federation-management packet rows:

- `631 mapped`
- `1 partial`

The remaining `1 partial` row clusters into a stable category:

- `1 ARG`

Residual bounded row kinds in that last group:

- none

## What The Categories Mean

### Argument tail

This is the single remaining argument-tail row for `CAP-FM`.

The single remaining `ARG` row is the imported create-federation optional
logical-time-implementation slice that still claims the default should be
`HLAfloat64Time` when omitted.

That row stays `partial` because the current Python 2010 lane honestly proves
time-factory selection from the merged federation model instead of that broader
default-time statement.

Connect, join, resign, and federation-synchronized argument rows are now
directly mapped for the current Python 2010 lane.

### Residual overview and harmonization tail

The last `1` row is the small bounded remainder:

- one create-time logical-time-default argument row

The lost-federate overview row is now directly mapped through loss-trigger,
callback-model, membership-teardown, pending-acquisition-cancellation, owned-
object-delete, and unconditional-divest cleanup witnesses. The only remaining
bounded FM row is the create-time logical-time-default argument mismatch.

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

- federation management is broadly implemented, linked, and strongly tested
- the remaining partial rows describe bounded harmonization, callback-order, or
  state-vector granularity limits
- the family already has a defensible supported-scope reading

Bad reading:

- Clause 4 is mostly unproven
- lifecycle or save/restore behavior is still speculative
- the partial rows imply missing support for federation-management services
  themselves

## Reading Order

1. `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv`
2. `requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv`
3. `requirements/2010/traceability_matrix.csv`
4. `tests/backends/test_python_backend_federation_extended.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
