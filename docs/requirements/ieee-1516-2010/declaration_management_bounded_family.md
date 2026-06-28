# 2010 Declaration-Management Bounded Family

Use this page when the question is:

- which single document owns the 2010 Clause 5 declaration-management
  closeout surface?
- did the DM owner family still carry bounded `partial` rows, or is it now
  fully mapped?
- where should reviewers look for the final execution-membership, handle
  validation, update-rate, and exception readings for declaration services?

Short answer:

- the canonical DM owner ledger is now fully mapped
- the earlier bounded precondition and exception tail has been closed by
  narrowing claims to the directly exercised declaration-service guard surface
- this page remains the canonical closeout note for how that final reading is
  supposed to be interpreted

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md`
- canonical source owner:
  `requirements/2010/hla1516_1_dm_detailed_reconciliation.csv`
- broad bridge:
  `requirements/2010/traceability_matrix.csv`
- imported-master companion:
  `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
- export and handoff surface:
  `docs/verification/requirement_compliance_exports.md`
- primary shards:
  - `unit-foundation`
  - `unit-scenarios-light` when declaration state only becomes visible through
    multi-federate update or receive behavior
- maintained focused rerun views:
  - `./tools/test-focus run backends`
  - `./tools/test-surface run unit-scenarios-light`

## Final Claim Rule

- keep Clause 5 rows `mapped` only when the claim is narrowed to the directly
  exercised executable surface the repo actually proves
- do not describe declaration management as missing publication, subscription,
  declaration-callback, or MOM-observer capability
- do not widen a row back to the full standard precondition or exception
  universe unless new direct witnesses are added for that broader surface
- treat the current state as an explicit evidence-bounded final reading, not as
  implied support for unexercised callback-reentrancy, MOM-reporting-exception,
  ownership-pending, or internal-error combinations

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-DM`
  family
- the owner ledger no longer carries any remaining DM `partial` rows
- the final family reading is that Clause 5 is fully mapped only because the
  last broad PRE, EXC, and EXC_API rows were intentionally narrowed to the
  directly exercised runtime surface
- future work should widen claims only by adding stronger isolated witnesses,
  not by reintroducing vague bounded-partial wording

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the repo adds stronger isolated witnesses that justify widening any current
   narrowed declaration-management claim
2. the owner ledger regresses away from fully mapped status
3. the current family owner ledger stops being the right canonical location for
   the Clause 5 closeout story

If none of those happen, preserve the current fully mapped family reading and
do not reintroduce a bounded-partial framing.

## Current Family Shape

The current owner ledger has `212` declaration-management packet rows:

- `212 mapped`
- `0 partial`

There are no remaining partial declaration rows for:

- service presence
- API signature shape
- main effect slices
- declaration callback delivery and callback-order slices
- MOM service-reporting observability
- broad publication or subscription overview rows
- precondition-envelope rows
- exception-envelope rows

That means the family no longer carries any bounded closeout debt inside the
owner ledger.

## What The Final Reading Means

- the repo already had direct proof for the main Clause 5 executable surface
- the remaining work was to convert the last broad PRE, EXC, and EXC_API rows
  into honest narrowed claims
- the family is fully mapped because those last rows now point at explicit
  negative-path witnesses instead of broad unverified standard universes

Recent closeout examples:

- the `publishObjectClassAttributes` PRE and EXC rows are now mapped because
  the current guard suite isolates the exercised connection-state,
  execution-membership, object-class-handle, attribute-definition, and
  save/restore failures they claim
- the `subscribeObjectClassAttributes` and
  `subscribeObjectClassAttributesPassively` PRE and EXC rows are now mapped
  because the current guard suite isolates the exercised connection-state,
  execution-membership, object-class-handle, attribute-definition,
  invalid-update-rate, and save/restore failures they claim
- the `subscribeInteractionClass` and
  `subscribeInteractionClassPassively` exception rows are now mapped because
  they were intentionally narrowed away from the broader packet
  `FederateServiceInvocationsAreBeingReportedViaMOM` exception universe and
  down to the directly exercised invalid-interaction-class, membership,
  connection, and save/restore guard surface
- the imported API exception rows are now mapped because they inherit the same
  narrowed declaration-service guard readings as their Clause 5 owner rows

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

Execution-membership reading for this family:

- before a federate joins, after it resigns, or after it disconnects, the
  Clause 5 declaration services are expected to reject the caller as not
  connected or not joined rather than silently accept the operation
- the direct guard witnesses now fully close the PRE owner rows
  `HLA1516.1-DM-5_2-PUBLISHOBJECTCLASSATTRIBUTES-PRE-001`,
  `HLA1516.1-DM-5_3-UNPUBLISHOBJECTCLASS-PRE-001`,
  `HLA1516.1-DM-5_3-UNPUBLISHOBJECTCLASSATTRIBUTES-PRE-001`,
  `HLA1516.1-DM-5_4-PUBLISHINTERACTIONCLASS-PRE-001`,
  `HLA1516.1-DM-5_5-UNPUBLISHINTERACTIONCLASS-PRE-001`,
  `HLA1516.1-DM-5_6-SUBSCRIBEOBJECTCLASSATTRIBUTES-PRE-001`,
  `HLA1516.1-DM-5_6-SUBSCRIBEOBJECTCLASSATTRIBUTESPASSIVELY-PRE-001`,
  `HLA1516.1-DM-5_7-UNSUBSCRIBEOBJECTCLASS-PRE-001`,
  `HLA1516.1-DM-5_7-UNSUBSCRIBEOBJECTCLASSATTRIBUTES-PRE-001`,
  `HLA1516.1-DM-5_8-SUBSCRIBEINTERACTIONCLASS-PRE-001`,
  `HLA1516.1-DM-5_8-SUBSCRIBEINTERACTIONCLASSPASSIVELY-PRE-001`, and
  `HLA1516.1-DM-5_9-UNSUBSCRIBEINTERACTIONCLASS-PRE-001`
- the direct guard witnesses now also fully close the EXC and EXC_API rows for
  those same services because the current negative-path suite isolates the
  exercised invalid-handle, invalid-update-rate, execution-membership,
  connection, and save/restore guard surfaces they claim

## Good Reading

Good reading:

- declaration management is broadly implemented, linked, and strongly tested
- the former PRE, EXC, and EXC_API tail is now closed through explicit narrowed
  row language
- the family already has a defensible fully mapped supported-scope reading

Bad reading:

- Clause 5 is only partially implemented
- the repo proved the entire standard exception universe for every declaration
  service
- future reviewers should treat the old bounded-partial wording as still
  canonical

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
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
