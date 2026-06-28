# 2010 Time-Management Bounded Family

Use this page when the question is:

- why does the 2010 Clause 8 time-management family still carry `partial`
  rows even though the repo already has strong direct time, lookahead,
  GALT/LITS, retraction, MOM, and callback-order evidence?
- which single document owns the remaining `CAP-TM` partial pattern?
- are those partial rows still vague, or already in an explicit bounded final
  state?

Short answer:

- the remaining `CAP-TM` partial rows are already in an explicit bounded family
  state
- the canonical owner ledger stays `partial` for those rows
- the bounded reasons are now structured and reviewable instead of implied

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/time_management_bounded_family.md`
- canonical source owner:
  `requirements/2010/hla1516_1_tm_detailed_reconciliation.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- imported-master companion:
  `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
- primary shard:
  - `unit-python-core`
- wider time-family view only when needed:
  - `./tools/test-focus run time`
  - `./tools/test-focus run backends`
- separate mixed-backend bounded row note:
  `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md`

## Final Claim Rule

- keep the remaining Clause 8 family rows `partial` when the repo already
  proves the main service surface, signature shape, callback order, lookahead,
  GALT/LITS queries, retraction, and representative MOM visibility, but does
  not yet prove every imported packet slice as a one-row exhaustive witness
- do not describe these rows as missing time-management services
- do not describe these rows as unsupported logical-time behavior
- do not flatten the family into `mapped` merely because the primary time and
  lookahead paths are strong
- treat the current state as an explicit bounded final reading of the present
  evidence, not as hidden uncertainty

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-TM`
  partial family
- the remaining rows are not waiting on wording cleanup; they are already in
  their intended bounded supported-scope presentation
- the unresolved part is only optional future precondition-envelope isolation,
  exception-envelope isolation, or sharper overview decomposition, not
  ambiguity about whether the currently exercised Clause 8 service surface
  exists
- keep the family rows `partial` in
  `hla1516_1_tm_detailed_reconciliation.csv` unless narrower direct proof is
  actually added for the remaining packet slices

## Current Family Shape

The current owner ledger has `301` time-management packet rows:

- `292 mapped`
- `9 partial`

The remaining `9 partial` rows cluster into stable categories:

- `4 PRE`
- `2 EXC`
- `2 EXC_API`
- `1 OVW`

## What The Categories Mean

### Precondition-envelope tail

The `4 PRE` rows mostly state a broader service-precondition universe than the
current isolated witnesses prove directly for one row at a time.

Typical pattern:

- key not-connected, not-joined, save/restore, invalid-lookahead, pending, and
  disabled-state guards are already proven
- the packet row still claims a larger clause-level precondition envelope than
  the direct witness currently isolates

### Exception-envelope tail

The `2 EXC` and `2 EXC_API` rows usually keep a broader failure envelope than
the current tests isolate directly.

Typical pattern:

- representative standard exceptions are already exercised on the direct time
  lane
- the packet row still claims the full exception universe, including broader
  internal-error or full service-wide failure combinations, as one exhaustive
  witness

### Residual overview tail

The last `1 OVW` row is the broad time-axis overview row.

It is not a sign that Clause 8 is largely unproven.
It remains `partial` because that one overview sentence still compresses a
broader ordered-delivery and receive-order-conversion story than the current
single row can honestly claim as one direct exhaustive witness.

The specific mixed-backend RO/TSO divergence row is owned separately by:

- `requirements/2010/hla1516_1_priority_backend_resolution.csv`
- `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md`

That keeps the family-wide `CAP-TM` bounded reading separate from the narrower
cross-backend priority-row note.

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the remaining `PRE`, `EXC`, `EXC_API`, or overview rows gain new direct
   isolated witnesses
2. the repo decides to make a stronger one-row-per-packet Clause 8 claim
3. the current family owner ledger stops being the right canonical location for
   the bounded Clause 8 time-management story

If none of those happen, preserve the current bounded family reading and do not
keep describing `CAP-TM` as vague or structurally unfinished.

## What Is Already Proved

The current repo directly proves most of the Clause 8 executable surface,
including:

- enable and disable time regulation and time constrained flows
- time advance request, next message request, and flush queue request families
- GALT, LITS, logical-time, and lookahead query behavior
- lookahead modification and negative lookahead rejection
- retraction behavior and queued-TSO removal
- callback ordering for enablement and grant paths
- representative MOM service-reporting visibility for Clause 8 services
- core backend-matrix and time-state coverage for the direct Python lane

Primary evidence anchors:

- `tests/time/test_mom_mim_time_v10.py`
- `tests/time/test_mom_mim_and_time_semantics_v010.py`
- `tests/time/test_mom_mim_time_management_v010.py`
- `tests/time/test_lookahead_backend_matrix.py`
- `tests/backends/test_python_backend_object_ownership_extended.py`
- `requirements/2010/traceability_matrix.csv`

Use these rerun commands before dropping to raw file paths:

- `./tools/test-focus run time` for the main 2010 time-management and backend
  matrix slice
- `./tools/test-focus run backends` when the time issue crosses into shared
  backend negative-path or ownership-adjacent behavior

## Good Reading

Good reading:

- time management is broadly implemented, linked, and strongly tested
- the remaining partial rows describe bounded precondition-envelope,
  exception-envelope, or broad overview granularity limits
- the family already has a defensible supported-scope reading

Bad reading:

- Clause 8 is mostly unproven
- logical-time, lookahead, or retraction behavior is still speculative
- the partial rows imply missing support for time-management services
  themselves

## Reading Order

1. `requirements/2010/hla1516_1_tm_detailed_reconciliation.csv`
2. `requirements/2010/traceability_matrix.csv`
3. `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
4. `tests/time/test_mom_mim_time_v10.py`
5. `tests/time/test_mom_mim_and_time_semantics_v010.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
- [`mixed_backend_priority_boundaries.md`](mixed_backend_priority_boundaries.md)
