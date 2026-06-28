# 2010 Support-Services Bounded Family

Use this page when the question is:

- did the 2010 Clause 10 support-services family really close cleanly, or are
  there still hidden residual `partial` rows?
- which single document owns the final `CAP-SUP` reading?
- if the family is fully mapped, what evidence actually justifies that claim?

Short answer:

- the 2010 Clause 10 support-services family no longer carries any `partial`
  rows in the Python lane
- the canonical owner ledger is now fully mapped
- the closeout claim is anchored in direct runtime and negative-path evidence,
  not in plan or packet prose

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

- keep Clause 10 support-service rows `mapped` only where the current repo
  proves the actual Python public-path contract for that service family:
  positive behavior, signature presence, and the exact negative-path guards the
  runtime enforces
- do not keep rows `partial` merely because imported packet prose names a
  broader hypothetical precondition or exception universe than the Python lane
  actually exposes
- do not describe the family as fully mapped unless the row notes are narrowed
  to the real exercised public-path guard surface

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-SUP`
  family
- the family is no longer in a bounded-partial state
- the remaining work, if any, is future drift detection or broader
  cross-backend comparison, not unresolved Python-lane Clause 10 proof debt

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. runtime behavior changes and invalidates the current mapped guard-surface
   reading
2. a backend-resolution artifact starts recording Python-lane divergence for a
   currently mapped Clause 10 row
3. the current family owner ledger stops being the right canonical location for
   the Clause 10 support-services story

## Current Family Shape

The current owner ledger has `603` support-service packet rows:

- `603 mapped`
- `0 partial`

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

- `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv`
- `requirements/2010/traceability_matrix.csv`
- `docs/verification/requirement_compliance_exports.md`

There are no remaining partial support rows for:

- service presence
- API signature shape
- return values or main effect slices
- MOM service-reporting observability
- test-suite ownership slices

That means the family is no longer broad proof debt across Clause 10.
The prior negative-path envelope has been replaced by narrowed mapped rows that
name the actual Python public-path guards.

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

## Why The Rows Now Map

The current closeout does not claim a universal imported exception universe for
each support service.

Instead, the mapped rows are now explicitly narrowed to the real Python public
path:

- joined lookup helpers map against connection-state, membership, and direct
  invalid-name or invalid-handle validation
- advisory-switch helpers map against switch-state plus save/restore, member,
  and connection guards where the runtime enforces them
- callback-control helpers map against connected-surface behavior, save or
  restore on `enableCallbacks`/`disableCallbacks`, and within-callback
  rejection on `evokeCallback`/`evokeMultipleCallbacks`

That narrower statement is fully exercised by direct tests, so the family no
longer needs `partial` rows to represent honesty.

## Good Reading

Good reading:

- the support-service family is implemented, linked, and strongly tested
- the mapped rows are tied to the actual Python guard surface, not to a plan
  document or generic closeout claim
- the family has a defensible fully mapped supported-scope reading

Bad reading:

- Clause 10 is still mostly negative-path debt
- the closeout depends on packet prose rather than runtime evidence
- the family is only "green" because the tests stopped checking anything

## Reading Order

1. `requirements/2010/hla1516_1_sup_detailed_reconciliation.csv`
2. `requirements/2010/traceability_matrix.csv`
3. `tests/backends/test_python_backend_support_services.py`
4. `tests/scenarios/test_support_services_backend_matrix.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
