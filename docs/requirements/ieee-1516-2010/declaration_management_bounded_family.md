# 2010 Declaration-Management Bounded Family

Use this page when the question is:

- why does the 2010 Clause 5 declaration-management family still carry
  `partial` rows even though the repo already has strong direct publication,
  subscription, declaration-callback, and MOM evidence?
- which single document owns the remaining `CAP-DM` partial pattern?
- are those partial rows still vague, or already in an explicit bounded final
  state?

Short answer:

- the remaining `CAP-DM` partial rows are already in an explicit bounded
  family state
- the canonical owner ledger stays `partial` for those rows
- the bounded reasons are now structured and reviewable instead of implied

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md`
- canonical source owner:
  `requirements/2010/hla1516_1_dm_detailed_reconciliation.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- imported-master companion:
  `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
- primary shards:
  - `unit-foundation`
  - `unit-scenarios-light` when declaration state only becomes visible through
    multi-federate update or receive behavior
- maintained focused rerun views:
  - `./tools/test-focus run backends`

## Final Claim Rule

- keep the remaining Clause 5 family rows `partial` when the repo already
  proves the main service surface, signature shape, declaration state
  transitions, callback delivery, and representative MOM observability, but
  does not yet prove every imported packet slice as a one-row exhaustive
  witness
- do not describe these rows as missing declaration-management services
- do not describe these rows as unsupported publication, subscription, or
  declaration-callback behavior
- do not flatten the family into `mapped` merely because the primary
  declaration paths are strong
- treat the current state as an explicit bounded final reading of the present
  evidence, not as hidden uncertainty

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-DM`
  partial family
- the remaining rows are not waiting on wording cleanup; they are already in
  their intended bounded supported-scope presentation
- the unresolved part is only optional future precondition-envelope isolation
  or exception-envelope isolation, not ambiguity about whether the currently
  exercised Clause 5 service surface exists
- keep the family rows `partial` in
  `hla1516_1_dm_detailed_reconciliation.csv` unless narrower direct proof is
  actually added for the remaining packet slices

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the remaining `PRE`, `EXC`, or `EXC_API` rows gain new direct isolated
   witnesses
2. the repo decides to make a stronger one-row-per-packet Clause 5 claim
3. the current family owner ledger stops being the right canonical location for
   the bounded Clause 5 declaration-management story

If none of those happen, preserve the current bounded family reading and do not
keep describing `CAP-DM` as vague or structurally unfinished.

## Current Family Shape

The current owner ledger has `212` declaration-management packet rows:

- `174 mapped`
- `38 partial`

The remaining `38 partial` rows cluster into stable categories:

- `14 EXC_API`
- `12 EXC`
- `12 PRE`

There are no remaining partial declaration rows for:

- service presence
- API signature shape
- main effect slices
- declaration callback delivery and callback-order slices
- MOM service-reporting observability
- broad publication or subscription overview rows

That means the family is no longer broad proof debt across all of Clause 5.
The remaining bounded area is the negative-path and precondition envelope.

## What The Categories Mean

### Precondition-envelope tail

The `12 PRE` rows mostly state a broader service-precondition universe than the
current isolated witnesses prove directly for one row at a time.

Typical pattern:

- key not-connected, not-joined, save/restore, invalid-handle, and strict
  declared-state guards are already proven
- the packet row still claims a larger clause-level precondition envelope than
  the direct witness currently isolates

### Exception-envelope tail

The `12 EXC` and `14 EXC_API` rows usually keep a broader failure envelope than
the current tests isolate directly.

Typical pattern:

- representative standard exceptions are already exercised on the direct
  declaration lane
- the packet row still claims the full exception universe, including broader
  internal-error or full service-wide failure combinations, as one exhaustive
  witness

## What Is Already Proved

The current repo directly proves most of the Clause 5 executable surface,
including:

- publish and unpublish object-class attributes
- publish and unpublish interaction classes
- subscribe and unsubscribe object-class attributes, including passive variants
- subscribe and unsubscribe interaction classes, including passive variants
- declaration-driven registration and interaction usefulness callbacks
- strict publication or subscription gates on update, discovery, and receive
  behavior
- representative MOM service-reporting visibility for Clause 5 services
- direct service-signature and callback-signature metadata coverage

Primary evidence anchors:

- `tests/backends/test_python_backend_object_ownership_extended.py`
- `tests/backends/test_python_backend_time_ddm_extended.py`
- `tests/backends/test_python_backend.py`
- `requirements/2010/traceability_matrix.csv`

Use these rerun commands before dropping to raw file paths:

- `./tools/test-focus run backends` for the main 2010 declaration-management
  backend slice
- `./tools/test-surface run unit-scenarios-light` when declaration state is
  only visible through multi-federate scenario behavior

## Good Reading

Good reading:

- declaration management is broadly implemented, linked, and strongly tested
- the remaining partial rows describe bounded precondition-envelope and
  exception-envelope granularity limits
- the family already has a defensible supported-scope reading

Bad reading:

- Clause 5 is mostly unproven
- publication, subscription, or declaration-callback behavior is still
  speculative
- the partial rows imply missing support for declaration-management services
  themselves

## Reading Order

1. `requirements/2010/hla1516_1_dm_detailed_reconciliation.csv`
2. `requirements/2010/traceability_matrix.csv`
3. `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
4. `tests/backends/test_python_backend_object_ownership_extended.py`
5. `tests/backends/test_python_backend_time_ddm_extended.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../plans/requirements_gap_register.md`](../../plans/requirements_gap_register.md)
