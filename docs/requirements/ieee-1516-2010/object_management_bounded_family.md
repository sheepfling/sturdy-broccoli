# 2010 Object-Management Bounded Family

Use this page when the question is:

- which single document owns the 2010 Clause 6 object-management closeout
  surface?
- did the OM owner family still carry bounded `partial` rows, or is it now
  fully mapped?
- where should reviewers look for the final execution-membership and
  transportation-subset readings for object and interaction services?

Short answer:

- the canonical OM owner ledger is now fully mapped
- the earlier bounded Clause 6 tail has been closed by narrowing claims to the
  directly exercised runtime surface
- this page remains the canonical closeout note for how that final reading is
  supposed to be interpreted

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/object_management_bounded_family.md`
- canonical source owner:
  `requirements/2010/hla1516_1_om_detailed_reconciliation.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- supporting decomposition seed:
  `requirements/2010/hla1516_1_clause_6_object_management.csv`
- export and handoff surface:
  `docs/verification/requirement_compliance_exports.md`
- primary shards:
  - `unit-scenarios-light`
  - `unit-python-core`
- maintained focused rerun views:
  - `./tools/test-focus run execution-membership`
  - `./tools/test-focus run backends`

## Final Claim Rule

- keep Clause 6 rows `mapped` only when the claim is narrowed to the directly
  exercised executable surface the repo actually proves
- do not describe object management as missing naming, registration,
  discovery, update, interaction, delete, or local-delete capability
- do not widen a row back to the full standard exception or callback-order
  universe unless new direct witnesses are added for that broader surface
- treat the current state as an explicit evidence-bounded final reading, not as
  implied support for unexercised transport, callback-order, or multi-effect
  combinations

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-OM`
  family
- the owner ledger no longer carries any remaining OM `partial` rows
- the final family reading is that Clause 6 is fully mapped because the last
  bounded callback-order, exception-envelope, and supported-subset rows were
  narrowed to the directly exercised runtime surface
- future work should widen claims only by adding stronger isolated witnesses,
  not by reintroducing vague bounded-partial wording

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the repo adds stronger isolated witnesses that justify widening any current
   narrowed OM claim
2. the owner ledger regresses away from fully mapped status
3. the current family owner ledger stops being the right canonical location for
   the Clause 6 closeout story

If none of those happen, preserve the current fully mapped family reading and
do not reintroduce a bounded-partial framing.

## Current Family Shape

The current owner ledger has `391` OM packet rows:

- `391 mapped`
- `0 partial`

There are no remaining partial OM rows for:

- service presence
- API signature shape
- callback delivery or callback payload slices
- MOM service-reporting observability
- return-value slices
- object and interaction routing effect slices
- precondition-envelope rows
- exception-envelope rows

That means the family no longer carries any bounded closeout debt inside the
owner ledger.

## What The Final Reading Means

- the repo already had direct proof for the main Clause 6 executable surface
- the remaining work was to convert the last broad exception, callback-order,
  and supported-subset rows into honest narrowed claims
- the family is fully mapped because those last rows now point at explicit
  runtime witnesses instead of broad unverified standard universes

Recent closeout examples:

- the `updateAttributeValues` exception, precondition, and effect rows no
  longer live in a partial tail because direct routing and negative-path
  witnesses now isolate the exercised object-knownness, ownership,
  publication-state, invalid-logical-time, execution-membership, connection,
  and save/restore surfaces they claimed
- the `registerObjectInstance` precondition, effect, and exception rows no
  longer live in a partial tail because direct positive and negative-path
  witnesses now isolate the exercised object creation, discovery eligibility,
  duplicate-name, publication-state, class-definition, execution-membership,
  connection, and save/restore surfaces they claimed
- the `deleteObjectInstance` and `localDeleteObjectInstance` precondition,
  effect, exception, and return-value rows no longer live in a partial tail
  because direct lifecycle and time-managed witnesses now isolate the
  exercised object-knownness, privilege, membership, connection, save/restore,
  invalid-logical-time, and deferred-removal surfaces they claimed
- the name-reservation and name-release families no longer live in a partial
  tail because direct naming-state and guard-path witnesses now isolate the
  exercised reservation success or release effect plus the applicable
  membership, connection, and save/restore failures

## What Is Already Proved

The current repo directly proves most of the Clause 6 executable surface,
including:

- object-instance name reservation and release families
- registration, discovery, local-delete, and remove-object flows
- attribute update and interaction routing through declaration and DDM filters
- request-attribute-value-update and update-advisory slices
- attributes-in-scope and attributes-out-of-scope callback slices
- implemented reliable plus best-effort transportation override query,
  confirm, report, and restore-persistence subset
- representative MOM service-reporting visibility for Clause 6 services

Primary evidence anchors:

- `tests/backends/test_python_backend_time_ddm_extended.py`
- `tests/backends/test_python_backend_object_ownership_extended.py`
- `tests/backends/test_python_backend_support_services.py`
- `tests/scenarios/test_target_radar_scenario.py`
- `requirements/2010/traceability_matrix.csv`

Execution-membership reading for this family:

- after a federate resigns, before it joins, or after it disconnects, object
  and interaction services are expected to reject the caller as not connected
  or not joined rather than silently accept the operation
- that includes basic delete, local-delete, update, send, request, and
  transportation-query paths, not just federation-management services
- that same joined-state guard surface also covers plain object registration on
  the shared backend path before join and again after resign or disconnect

Primary owner rows for that execution-state reading include:

- `HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-PRE-001`
- `HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-PRE-001`
- `HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001`
- `HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-PRE-001`
- `HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001`
- `HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001`
- `HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001`
- `HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001`
- `HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-PRE-001`
- `HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-PRE-001`
- `HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-PRE-001`

Supported-subset reading for this family:

- the repo directly proves the implemented `HLAreliable` plus `HLAbestEffort`
  transportation subset
- broader full-semantic transportation claims should only be widened if new
  direct witnesses are added
- time-managed delete behavior is mapped only because the current witness
  directly proves deferred removal until grant on the shared Python lane

Use these rerun commands before dropping to raw file paths:

- `./tools/test-focus run execution-membership`
- `./tools/test-focus run backends`
- `./tools/test-surface run unit-scenarios-light`

High-signal execution-member guard anchors inside those suites include:

- `test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore`
- `test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore`
- `test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore`
- `test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore`
- `test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`

## Reading Order

1. `requirements/2010/hla1516_1_om_detailed_reconciliation.csv`
2. `requirements/2010/hla1516_1_clause_6_object_management.csv`
3. `requirements/2010/traceability_matrix.csv`
4. `docs/verification/requirement_compliance_exports.md`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
