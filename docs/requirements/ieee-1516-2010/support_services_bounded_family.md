# 2010 Support-Services Bounded Family

Use this page when the question is:

- why does the 2010 Clause 10 support-services family still carry `partial`
  rows even though most support-service slices are already directly tested?
- which single document owns the remaining `CAP-SUP` partial pattern?
- are those partial rows still vague, or already in an explicit bounded final
  state?

Short answer:

- the remaining `CAP-SUP` partial rows are already in an explicit bounded
  family state
- the canonical owner ledger stays `partial` for those rows
- the bounded reason is now uniform and reviewable instead of implied

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/support_services_bounded_family.md`
- canonical source owner:
  `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- primary shards:
  - `unit-python-core`
  - `unit-scenarios-light` only where callback-control or matrix replay matters
- maintained focused rerun views:
  - `./tools/test-focus run backends`

## Final Claim Rule

- keep the remaining Clause 10 family rows `partial` when the current repo
  proves the support-service surface, signatures, lookup behavior, MOM
  observability, and representative negative-path guards, but does not yet
  prove every service-specific exception tuple as a one-row exhaustive matrix
- do not describe these rows as missing service surfaces
- do not describe these rows as unsupported
- do not flatten the family into `mapped` merely because the positive-path and
  most generic negative-path proof is strong
- treat the current state as an explicit bounded final reading of the present
  evidence, not as hidden uncertainty

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-SUP`
  partial family
- the remaining rows are not waiting on wording cleanup; they are already in
  their intended bounded supported-scope presentation
- the unresolved part is only optional future service-by-service negative-path
  decomposition, not ambiguity about whether the currently exercised Clause 10
  support-service surface exists
- keep the family rows `partial` in
  `hla1516_1_sup_detailed_reconciliation.csv` unless narrower direct proof is
  actually added for the remaining negative-path packet slices

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the remaining `PRE`, `EXC`, or `EXC_API` rows gain new direct per-service
   negative-matrix witnesses
2. the repo decides to make a stronger one-row-per-service-exception Clause 10
   claim
3. the current family owner ledger stops being the right canonical location for
   the bounded Clause 10 support-services story

If none of those happen, preserve the current bounded family reading and do not
keep describing `CAP-SUP` as vague or structurally unfinished.

## Current Family Shape

The current owner ledger has `603` support-service packet rows:

- `474 mapped`
- `129 partial`

The remaining `129 partial` rows are structurally narrow and uniform:

- `43 PRE`
- `43 EXC`
- `43 EXC_API`

Two formerly confusing support-service rows are worth naming explicitly because
they no longer belong in the live Python residual set:

- `REQ-RTI-SS-10_44-getMessageRetractionHandleFactory`
- `REQ-RTI-SS-10_44-getRegionHandleFactory`

Current reading for those two rows:

- the Python lane has implementation hooks and group-level support-service
  evidence
- the canonical row status now reads `pass`
- the Python backend-compliance packet now records them as
  `python_runtime_disposition=verified`
- that promotion makes the current family boundary clearer: the remaining
  `CAP-SUP` partial tail is the broad `PRE`/`EXC`/`EXC_API` envelope, not
  missing positive-path factory-helper coverage

Primary current artifacts for those two rows:

- `analysis/compliance/requirements_matrix_2010.csv`
- `analysis/compliance/requirements_ledger.csv`
- `analysis/compliance/service_conformance.json`

There are no remaining partial support rows for:

- service presence
- API signature shape
- return values or main effect slices
- MOM service-reporting observability
- test-suite ownership slices

That means the family is no longer broad proof debt across all of Clause 10.
The remaining bounded area is the negative-path envelope.

## What Is Already Proved

The current repo directly proves these support-service families:

- name and handle lookup round-trips
- ordering and transportation name or handle round-trips
- dimension and update-rate helper behavior
- advisory-switch toggle behavior and duplicate-switch guards
- callback-control behavior
- factory and normalization helpers
- MOM service-invocation reporting for Clause 10 services
- runtime membership guards for representative support-service helpers
- representative invalid-handle, invalid-name, invalid-type, region-ownership,
  save-in-progress, and restore-in-progress boundaries

Primary evidence anchors:

- `tests/backends/test_python_backend_support_services.py`
- `tests/scenarios/test_support_services_backend_matrix.py`
- `tests/backends/test_python_backend_time_ddm_extended.py::test_support_service_roundtrips_and_callback_controls_have_exact_behavior`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_clause_10_services_are_observable_through_mom_service_invocation_reporting`
- `tests/backends/test_python_backend_object_ownership_extended.py::test_clause_10_service_signature_metadata_matches_source_bindings`

Use these rerun commands before dropping to raw file paths:

- `./tools/test-focus run backends` for the main 2010 support-services backend
  slice
- `./tools/test-surface run unit-scenarios-light` when callback-control or
  matrix replay is the narrowest owning shard

## Why The Partial Rows Stay Partial

The remaining `PRE`, `EXC`, and `EXC_API` rows still use broader standard
language than the current direct proof.

More specifically, those rows often describe some combination of:

- every standard precondition that could apply
- every standard exception exposed by one specific Clause 10 service
- every API-level exception declaration for that service

The current tests are already strong enough to prove:

- connection-state guards
- joined-membership guards
- many invalid-name, invalid-handle, invalid-type, and invalid-region cases
- representative save/restore and advisory-switch guard behavior

But the repo does not yet claim that every service-specific exception tuple in
Clause 10 has its own one-row exhaustive negative matrix witness.

That is why these rows remain `partial` instead of `mapped`.

## Good Reading

Good reading:

- the support-service family is implemented, linked, and strongly tested
- the remaining partial rows describe a bounded negative-path granularity limit
- the family already has a defensible supported-scope reading

Bad reading:

- Clause 10 is mostly unproven
- support-service lookup and advisory behavior are still speculative
- the partial rows imply missing runtime support for the services themselves

## Reading Order

1. `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv`
2. `requirements/2010/traceability_matrix.csv`
3. `tests/backends/test_python_backend_support_services.py`
4. `tests/scenarios/test_support_services_backend_matrix.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../plans/requirements_gap_register.md`](../../plans/requirements_gap_register.md)
