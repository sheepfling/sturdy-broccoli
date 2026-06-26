# 2010 Data-Distribution-Management Bounded Family

Use this page when the question is:

- why does the 2010 Clause 9 data-distribution-management family still carry
  `partial` rows even though the repo already has strong direct region,
  overlap-routing, subscription, send-with-regions, and request-update
  evidence?
- which single document owns the remaining `CAP-DDM` partial pattern?
- are those partial rows still vague, or already in an explicit bounded final
  state?

Short answer:

- the remaining `CAP-DDM` partial rows are already in an explicit bounded
  family state
- the canonical owner ledger stays `partial` for those rows
- the bounded reasons are now structured and reviewable instead of implied

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/data_distribution_management_bounded_family.md`
- canonical source owner:
  `requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- imported-master companion:
  `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
- primary shards:
  - `unit-python-core`
  - `unit-scenarios-light` when object or interaction routing behavior is the
    narrowest practical proof
- wider time/scenario view only when needed:
  - `./tools/test-focus run python-2025-time`

## Final Claim Rule

- keep the remaining Clause 9 family rows `partial` when the repo already
  proves the main region lifecycle, overlap routing, DDM-gated object and
  interaction exchange, service signature shape, and representative MOM
  observability, but does not yet prove every imported packet slice as a
  one-row exhaustive witness
- do not describe these rows as missing DDM services
- do not describe these rows as unsupported region or overlap-routing behavior
- do not flatten the family into `mapped` merely because the primary region and
  routing paths are strong
- treat the current state as an explicit bounded final reading of the present
  evidence, not as hidden uncertainty

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-DDM`
  partial family
- the remaining rows are not waiting on wording cleanup; they are already in
  their intended bounded supported-scope presentation
- the unresolved part is only optional future precondition-envelope isolation
  or exception-envelope isolation, not ambiguity about whether the currently
  exercised Clause 9 service surface exists
- keep the family rows `partial` in
  `hla1516_1_ddm_detailed_reconciliation.csv` unless narrower direct proof is
  actually added for the remaining packet slices

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the remaining `PRE`, `EXC`, or `EXC_API` rows gain new direct isolated
   witnesses
2. the repo decides to make a stronger one-row-per-packet Clause 9 claim
3. the current family owner ledger stops being the right canonical location for
   the bounded Clause 9 data-distribution-management story

If none of those happen, preserve the current bounded family reading and do not
keep describing `CAP-DDM` as vague or structurally unfinished.

## Current Family Shape

The current owner ledger has `223` DDM packet rows:

- `177 mapped`
- `46 partial`

The remaining `46 partial` rows cluster into stable categories:

- `18 EXC_API`
- `14 EXC`
- `14 PRE`

There are no remaining partial DDM rows for:

- service presence
- API signature shape
- main effect slices
- MOM service-reporting observability
- return-value slices
- broad DDM overview routing rows

That means the family is no longer broad proof debt across all of Clause 9.
The remaining bounded area is the negative-path and precondition envelope.

## What The Categories Mean

### Precondition-envelope tail

The `14 PRE` rows mostly state a broader service-precondition universe than the
current isolated witnesses prove directly for one row at a time.

Typical pattern:

- key not-connected, not-joined, save/restore, invalid-region, invalid-region
  context, and ownership-of-region guards are already proven
- the packet row still claims a larger clause-level precondition envelope than
  the direct witness currently isolates

### Exception-envelope tail

The `14 EXC` and `18 EXC_API` rows usually keep a broader failure envelope than
the current tests isolate directly.

Typical pattern:

- representative standard exceptions are already exercised on the direct DDM
  lane
- the packet row still claims the full exception universe, including broader
  internal-error or full service-wide failure combinations, as one exhaustive
  witness

## What Is Already Proved

The current repo directly proves most of the Clause 9 executable surface,
including:

- create, commit, and delete region families
- associate and unassociate region-update flows
- object and interaction subscription with regions, including passive variants
- register-object-instance-with-regions and send-interaction-with-regions flows
- DDM-gated discovery, reflect, receive, and request-attribute-value-update
  routing
- representative MOM service-reporting visibility for Clause 9 services
- direct service-signature metadata coverage

Primary evidence anchors:

- `tests/backends/test_python_backend_time_ddm_extended.py`
- `tests/verification/test_compliance_slice_v011.py`
- `tests/backends/test_python_backend_object_ownership_extended.py`
- `requirements/2010/traceability_matrix.csv`

## Good Reading

Good reading:

- DDM is broadly implemented, linked, and strongly tested
- the remaining partial rows describe bounded precondition-envelope and
  exception-envelope granularity limits
- the family already has a defensible supported-scope reading

Bad reading:

- Clause 9 is mostly unproven
- region overlap, DDM-gated routing, or region lifecycle behavior is still
  speculative
- the partial rows imply missing support for DDM services themselves

## Reading Order

1. `requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv`
2. `requirements/2010/traceability_matrix.csv`
3. `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
4. `tests/backends/test_python_backend_time_ddm_extended.py`
5. `tests/verification/test_compliance_slice_v011.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../plans/requirements_gap_register.md`](../../plans/requirements_gap_register.md)
