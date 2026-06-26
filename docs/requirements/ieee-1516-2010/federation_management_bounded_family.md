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

- `523 mapped`
- `109 partial`

The remaining `109 partial` rows cluster into stable categories:

- `43 ARG`
- `23 EFF`
- `17 CB_ORD`
- `15 EXC`
- `11` residual overview, callback-surface, or traceability-bounded rows

Residual bounded row kinds in that last group:

- `3 OVW`
- `2 CB`
- `1 FED_CB`
- `1 MOM`
- `1 PRE`
- `1 SVC`
- `1 EXC_API`
- `1 MOM_TRACE`

## What The Categories Mean

### Argument-decomposition tail

The `43 ARG` rows are mostly imported packet argument slices that do not yet
map cleanly onto one direct row in
`hla1516_1_clause_4_fm_service_decomposition.csv`.

This is primarily a harmonization-granularity limit, not evidence that the
underlying services are absent.

### State-vector breadth tail

The `23 EFF` rows usually describe a broader postcondition vector than the
current direct proof asserts in one place.

Typical pattern:

- several important effect slices are already proven
- the full multi-field state transition is not yet claimed as one exhaustive
  witness

### Callback-order breadth tail

The `17 CB_ORD` rows are mostly callback-order or callback-model breadth rows.

These are not callback-delivery gaps.
They are rows where:

- the callback is already delivered directly
- the signature is already present
- the broader ordering, timing, or scope envelope remains stated more broadly
  than the currently isolated proof

### Exception-envelope breadth tail

The `15 EXC` rows usually keep a broader failure envelope than the current
tests isolate directly, especially where the standard language includes
internal-error or broader callback-trigger failure wording.

### Residual overview and fault-surface tail

The last `11` rows are the small bounded remainder:

- broad overview rows
- connection-lost callback/fault-surface rows
- one service/meta traceability row that is broader than the current direct
  executable witness

These rows are already explicit enough to review honestly, but they are not yet
standalone exhaustive service proofs.

## What Is Already Proved

The current repo directly proves most of the Clause 4 executable surface,
including:

- connect, disconnect, create, destroy, join, and resign service behavior
- synchronization registration, announcement, achievement, and federation-wide
  completion paths
- save and restore request, status, outcome, abort, and callback families
- representative MOM-observer visibility for key lifecycle and save/restore
  states
- many direct negative-path guards and callback outcome paths
- hosted transport equivalence coverage for the main federation-management
  lifecycle and save/restore lanes

Primary evidence anchors:

- `tests/backends/test_python_backend_federation_extended.py`
- `tests/scenarios/test_federation_management_backend_matrix.py`
- `tests/verification/test_requirements_ledger_v013.py`
- `requirements/2010/traceability_matrix.csv`

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
- [`../../plans/requirements_gap_register.md`](../../plans/requirements_gap_register.md)
