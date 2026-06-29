# 2010 Ownership-Management Bounded Family

Use this page when the question is:

- which single document owns the 2010 Clause 7 ownership-management closeout
  surface?
- did the Ownership owner family still carry bounded `partial` rows, or is it
  now fully mapped?
- where should reviewers look for the final ownership-state, acquisition-state,
  divestiture-state, and exception readings for ownership services?

Short answer:

- the canonical Ownership owner ledger is now fully mapped
- the earlier bounded precondition and exception tail has been closed by
  narrowing claims to the directly exercised ownership-service guard surface
- this page remains the canonical closeout note for how that final reading is
  supposed to be interpreted

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/ownership_management_bounded_family.md`
- edition-wide canonical requirement truth:
  `requirements/2010/canonical_requirements.json`
- edition-wide backend-resolution companion:
  `requirements/2010/backend_resolution.json`
- family mapping bridge:
  `requirements/2010/hla1516_1_own_detailed_reconciliation.csv`
- generated projection bridge:
  `requirements/2010/traceability_matrix.csv`
- imported-master companion:
  `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
- export and handoff surface:
  `docs/verification/requirement_compliance_exports.md`
- primary shard:
  - `unit-scenarios-light`
- wider ownership-family view only when needed:
  - `./tools/test-focus run backends`
  - `./tools/test-surface run unit-scenarios-light`

## Final Claim Rule

- keep Clause 7 rows `mapped` only when the claim is narrowed to the directly
  exercised executable surface the repo actually proves
- do not describe ownership management as missing acquisition, divestiture,
  ownership-query, callback, or MOM-observer capability
- do not widen a row back to the full standard precondition or exception
  universe unless new direct witnesses are added for that broader surface
- treat the current state as an explicit evidence-bounded final reading, not as
  implied support for unexercised callback-reentrancy, internal-error, or
  broader service-wide failure combinations

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-OWN`
  family
- the owner ledger no longer carries any remaining Ownership `partial` rows
- the final family reading is that Clause 7 is fully mapped only because the
  last PRE, EXC, and EXC_API rows were intentionally narrowed to the directly
  exercised runtime surface
- future work should widen claims only by adding stronger isolated witnesses,
  not by reintroducing vague bounded-partial wording

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the repo adds stronger isolated witnesses that justify widening any current
   narrowed ownership-management claim
2. the owner ledger regresses away from fully mapped status
3. the current family owner ledger stops being the right canonical location for
   the Clause 7 closeout story

If none of those happen, preserve the current fully mapped family reading and
do not reintroduce a bounded-partial framing.

## Current Family Shape

The current owner ledger has `225` ownership-management packet rows:

- `225 mapped`
- `0 partial`

There are no remaining partial ownership rows for:

- service presence
- API signature shape
- main effect slices
- MOM service-reporting observability
- callback delivery and callback-order slices
- ownership-state return-value slices
- precondition-envelope rows
- exception-envelope rows

That means the family no longer carries any bounded closeout debt inside the
owner ledger.

## What The Final Reading Means

- the repo already had direct proof for the main Clause 7 executable surface
- the remaining work was to convert the last broad PRE, EXC, and EXC_API rows
  into honest narrowed claims
- the family is fully mapped because those last rows now point at explicit
  negative-path witnesses instead of broad unverified standard universes

Recent closeout examples:

- the `unconditionalAttributeOwnershipDivestiture`,
  `queryAttributeOwnership`, and `isAttributeOwnedByFederate` rows are now
  mapped because the current guard suite isolates the exercised ownership-state,
  attribute-definition, object-knownness, connection-state,
  execution-membership, and save/restore failures they claim
- the `confirmDivestiture` rows are now mapped because the current guard suite
  and direct state tests isolate the exercised active-divestiture,
  pending-acquisition, ownership-state, attribute-definition,
  object-knownness, connection-state, execution-membership, and save/restore
  failures they claim
- the `attributeOwnershipAcquisition` and
  `attributeOwnershipAcquisitionIfAvailable` rows are now mapped because the
  current guard suite isolates the exercised publication-state,
  acquisition-state, ownership-state, attribute-definition,
  object-knownness, connection-state, execution-membership, and save/restore
  failures they claim
- the `attributeOwnershipDivestitureIfWanted` rows are now mapped because the
  current guard suite and state test isolate the exercised
  pending-acquisition-state, ownership-state, attribute-definition,
  object-knownness, connection-state, execution-membership, and save/restore
  surfaces they claim

## What Is Already Proved

The current repo directly proves most of the Clause 7 executable surface,
including:

- unconditional, negotiated, cancel-negotiated, and if-wanted divestiture
  families
- ownership acquisition, acquisition-if-available, release-denied, and cancel
  acquisition flows
- ownership callback delivery, payload, and ordering for negotiated and query
  paths
- ownership-state queries, including owned, unowned, and RTI-owned callback
  reporting paths
- representative MOM service-reporting visibility for Clause 7 services
- direct service-signature and callback-signature metadata coverage

Primary evidence anchors:

- `tests/backends/test_python_backend_object_ownership_extended.py`
- `tests/scenarios/test_ownership_management_backend_matrix.py`
- `requirements/2010/traceability_matrix.csv`

Execution-membership reading for this family:

- before a federate joins, after it resigns, or after it disconnects, the
  Clause 7 ownership services are expected to reject the caller as not
  connected or not joined rather than silently accept the operation
- the direct guard witnesses now fully close the PRE owner rows
  `HLA1516.1-OWN-7_2-UNCONDITIONALATTRIBUTEOWNERSHIPDIVESTITURE-PRE-001`,
  `HLA1516.1-OWN-7_3-NEGOTIATEDATTRIBUTEOWNERSHIPDIVESTITURE-PRE-001`,
  `HLA1516.1-OWN-7_6-CONFIRMDIVESTITURE-PRE-001`,
  `HLA1516.1-OWN-7_8-ATTRIBUTEOWNERSHIPACQUISITION-PRE-001`,
  `HLA1516.1-OWN-7_9-ATTRIBUTEOWNERSHIPACQUISITIONIFAVAILABLE-PRE-001`,
  `HLA1516.1-OWN-7_12-ATTRIBUTEOWNERSHIPRELEASEDENIED-PRE-001`,
  `HLA1516.1-OWN-7_13-ATTRIBUTEOWNERSHIPDIVESTITUREIFWANTED-PRE-001`, and
  `HLA1516.1-OWN-7_15-CANCELATTRIBUTEOWNERSHIPACQUISITION-PRE-001`
- the direct guard witnesses now also fully close the EXC and EXC_API rows for
  those same services plus the EXC and EXC_API rows for
  `cancelNegotiatedAttributeOwnershipDivestiture`,
  `queryAttributeOwnership`, and `isAttributeOwnedByFederate`

## Good Reading

Good reading:

- ownership management is broadly implemented, linked, and strongly tested
- the former PRE, EXC, and EXC_API tail is now closed through explicit narrowed
  row language
- the family already has a defensible fully mapped supported-scope reading

Bad reading:

- Clause 7 is only partially implemented
- the repo proved the entire standard exception universe for every ownership
  service
- future reviewers should treat the old bounded-partial wording as still
  canonical

## Reading Order

1. `requirements/2010/canonical_requirements.json`
2. `requirements/2010/backend_resolution.json`
3. `requirements/2010/hla1516_1_own_detailed_reconciliation.csv`
4. `requirements/2010/traceability_matrix.csv`
5. `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
6. `tests/backends/test_python_backend_object_ownership_extended.py`
7. `tests/scenarios/test_ownership_management_backend_matrix.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
