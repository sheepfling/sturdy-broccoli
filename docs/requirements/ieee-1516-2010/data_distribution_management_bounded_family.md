# 2010 Data-Distribution-Management Bounded Family

Use this page when the question is:

- which single document owns the 2010 Clause 9 data-distribution-management
  closeout surface?
- did the DDM owner family still carry bounded `partial` rows, or is it now
  fully mapped?
- where should reviewers look for the final execution-membership and exception
  readings for region-gated object and interaction services?

Short answer:

- the canonical DDM owner ledger is now fully mapped
- the earlier bounded exception tail has been closed by narrowing claims to the
  directly exercised exception surface
- this page remains the canonical closeout note for how that final reading is
  supposed to be interpreted

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2010/data_distribution_management_bounded_family.md`
- edition-wide canonical requirement truth:
  `requirements/2010/canonical_requirements.json`
- edition-wide backend-resolution companion:
  `requirements/2010/backend_resolution.json`
- family mapping bridge:
  `requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv`
- generated projection bridge:
  `requirements/2010/traceability_matrix.csv`
- imported-master companion:
  `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
- primary shards:
  - `unit-python-core`
  - `unit-scenarios-light` when object or interaction routing behavior is the
    narrowest practical proof
- wider time/scenario view only when needed:
  - `./tools/test-focus run backends`
  - `./tools/test-focus run time`

## Final Claim Rule

- keep Clause 9 rows `mapped` only when the claim is narrowed to the directly
  exercised executable surface the repo actually proves
- do not describe DDM as missing region lifecycle, overlap-routing,
  subscription, send-with-regions, or request-update capability
- do not widen a row back to the full standard exception universe unless new
  direct witnesses are added for that broader surface
- treat the current state as an explicit evidence-bounded final reading, not as
  implied support for unexercised exception combinations

## Default Final Stance

- this owner note is the canonical final reading for the current `CAP-DDM`
  family
- the owner ledger no longer carries any remaining DDM `partial` rows
- the final family reading is that Clause 9 is fully mapped only because the
  last exception-envelope rows were intentionally narrowed to the directly
  exercised runtime surface
- future work should widen claims only by adding stronger isolated witnesses,
  not by reintroducing vague bounded partial wording

## Exit Condition

Treat this bucket as closed for documentation ownership and closeout-surface
purposes unless one of these becomes true:

1. the repo adds stronger isolated witnesses that justify widening any current
   narrowed DDM exception claim
2. the owner ledger regresses away from fully mapped status
3. the current family owner ledger stops being the right canonical location for
   the Clause 9 closeout story

If none of those happen, preserve the current fully mapped family reading and
do not reintroduce a bounded-partial framing.

## Current Family Shape

The current owner ledger has `223` DDM packet rows:

- `223 mapped`
- `0 partial`

There are no remaining partial DDM rows for:

- service presence
- API signature shape
- main effect slices
- MOM service-reporting observability
- return-value slices
- broad DDM overview routing rows
- precondition-envelope rows
- exception-envelope rows

That means the family no longer carries any bounded closeout debt inside the
owner ledger.

## What The Final Reading Means

- the repo already had direct proof for the main DDM executable surface
- the remaining work was to convert the last broad exception rows into honest
  narrowed claims
- the family is fully mapped because those last rows now point at explicit
  negative-path witnesses instead of broad unverified standard universes

Recent closeout examples:

- the `deleteRegion` PRE row no longer lives in this tail because direct
  negative-path witnesses now isolate the exercised connection-state,
  execution-membership, invalid-region, foreign-region ownership,
  region-in-use, and save/restore guard surfaces it claimed
- the subscription and region-association PRE rows no longer live in this tail
  because direct negative-path witnesses now isolate the exercised
  connection-state, execution-membership, handle-validation, invalid-region,
  invalid-update-rate, object-knownness, and save/restore guard surfaces they
  claimed
- the `registerObjectInstanceWithRegions` PRE row no longer lives in this tail
  because direct negative-path witnesses now isolate the exercised
  connection-state, execution-membership, class-handle and attribute-definition
  validation, publication-state, duplicate-name, invalid-region, and
  save/restore guard surfaces it claimed
- the `createRegion`, `commitRegionModifications`, and
  `unsubscribeInteractionClassWithRegions` PRE rows no longer live in this tail
  because direct negative-path witnesses now isolate the exercised
  connection-state, execution-membership, invalid-dimension or
  empty-dimension-set, interaction-class validation, invalid-region, and
  save/restore guard surfaces they claimed

- the `registerObjectInstanceWithRegions` exception rows are now mapped because
  they were narrowed to the directly exercised invalid-region,
  publication-state, duplicate-name, class-handle, membership, connection, and
  save/restore failures
- the object-subscription-with-regions exception rows are now mapped because
  they were narrowed to the directly exercised invalid-region-context,
  foreign-region ownership, invalid-region, attribute-definition, class-handle,
  update-rate, membership, connection, and save/restore failures
- the `sendInteractionWithRegions` and
  `requestAttributeValueUpdateWithRegions` exception rows are now mapped
  because they were narrowed to the directly exercised invalid-region,
  definition-validation, class-handle, publication-state, invalid-logical-time,
  membership, connection, and save/restore failures

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

Execution-membership reading for this family:

- before a federate joins, after it resigns, or after it disconnects,
  region-gated interaction and request-update services are expected to reject
  the caller as not connected or not joined rather than silently accept the
  operation
- the direct guard witnesses now fully close the PRE owner rows
  `HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001` and
  `HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-PRE-001`
- the direct guard witnesses now also fully close the region-lifecycle
  exception rows `HLA1516.1-DDM-9_2-CREATEREGION-EXC-001`,
  `HLA1516.1-DDM-9_2-RTIAPI-001-EXC`,
  `HLA1516.1-DDM-9_3-COMMITREGIONMODIFICATIONS-EXC-001`,
  `HLA1516.1-DDM-9_3-RTIAPI-001-EXC`,
  `HLA1516.1-DDM-9_4-DELETEREGION-EXC-001`, and
  `HLA1516.1-DDM-9_4-RTIAPI-001-EXC` because the current negative-path suite
  now isolates the exercised invalid-dimension, foreign-region ownership,
  invalid-region, region-in-use, execution-membership, connection, and
  save/restore guard surfaces they claimed
- the direct guard witnesses now also fully close the
  `unassociateRegionsForUpdates` exception rows
  `HLA1516.1-DDM-9_7-UNASSOCIATEREGIONSFORUPDATES-EXC-001` and
  `HLA1516.1-DDM-9_7-RTIAPI-001-EXC` because the current negative-path suite
  now isolates the exercised foreign-region ownership, invalid-region,
  attribute-definition, object-knownness, execution-membership, connection,
  and save/restore guard surfaces they claimed
- the direct guard witnesses now also fully close the
  `registerObjectInstanceWithRegions` exception rows
  `HLA1516.1-DDM-9_5-REGISTEROBJECTINSTANCEWITHREGIONS-EXC-001`,
  `HLA1516.1-DDM-9_5-RTIAPI-001-EXC`, and
  `HLA1516.1-DDM-9_5-RTIAPI-002-EXC` because the current negative-path suite
  now isolates the exercised invalid-region, publication-state,
  attribute-definition, duplicate-name, class-handle, execution-membership,
  connection, and save/restore guard surfaces they claimed
- the direct guard witnesses now also fully close the
  `subscribeObjectClassAttributesWithRegions`,
  `subscribeObjectClassAttributesPassivelyWithRegions`, and
  `unsubscribeObjectClassAttributesWithRegions` exception rows
  `HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-EXC-001`,
  `HLA1516.1-DDM-9_8-RTIAPI-001-EXC`,
  `HLA1516.1-DDM-9_8-RTIAPI-002-EXC`,
  `HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESPASSIVELYWITHREGIONS-EXC-001`,
  `HLA1516.1-DDM-9_8-RTIAPI-001-EXC-DUP02`,
  `HLA1516.1-DDM-9_8-RTIAPI-002-EXC-DUP02`,
  `HLA1516.1-DDM-9_9-UNSUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-EXC-001`,
  and `HLA1516.1-DDM-9_9-RTIAPI-001-EXC` because the current negative-path
  suite now isolates the exercised invalid-region-context, foreign-region
  ownership, invalid-region, attribute-definition, class-handle, update-rate,
  execution-membership, connection, and save/restore guard surfaces they
  claimed
- the direct guard witnesses now also fully close the
  `associateRegionsForUpdates` exception rows
  `HLA1516.1-DDM-9_6-ASSOCIATEREGIONSFORUPDATES-EXC-001` and
  `HLA1516.1-DDM-9_6-RTIAPI-001-EXC` because the current negative-path suite
  now isolates the exercised invalid-region-context, foreign-region ownership,
  invalid-region, attribute-definition, object-knownness,
  execution-membership, connection, and save/restore guard surfaces they
  claimed
- the direct guard witnesses now also fully close the
  `subscribeInteractionClassWithRegions` and
  `subscribeInteractionClassPassivelyWithRegions` exception rows
  `HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSWITHREGIONS-EXC-001`,
  `HLA1516.1-DDM-9_10-RTIAPI-001-EXC`,
  `HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSPASSIVELYWITHREGIONS-EXC-001`,
  and `HLA1516.1-DDM-9_10-RTIAPI-001-EXC-DUP02` because the current
  negative-path suite now isolates the exercised service-reporting-via-MOM,
  invalid-region-context, foreign-region ownership, invalid-region,
  interaction-class-not-defined, execution-membership, connection, and
  save/restore guard surfaces they claimed
- the direct guard witnesses now also fully close the
  `unsubscribeInteractionClassWithRegions` exception rows
  `HLA1516.1-DDM-9_11-UNSUBSCRIBEINTERACTIONCLASSWITHREGIONS-EXC-001` and
  `HLA1516.1-DDM-9_11-RTIAPI-001-EXC` because the current negative-path suite
  now isolates the exercised foreign-region ownership, invalid-region,
  interaction-class-not-defined, execution-membership, connection, and
  save/restore guard surfaces they claimed
- the direct guard witnesses also fully close the PRE owner rows
  `HLA1516.1-DDM-9_6-ASSOCIATEREGIONSFORUPDATES-PRE-001`,
  `HLA1516.1-DDM-9_7-UNASSOCIATEREGIONSFORUPDATES-PRE-001`,
  `HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-PRE-001`,
  `HLA1516.1-DDM-9_8-SUBSCRIBEOBJECTCLASSATTRIBUTESPASSIVELYWITHREGIONS-PRE-001`,
  `HLA1516.1-DDM-9_9-UNSUBSCRIBEOBJECTCLASSATTRIBUTESWITHREGIONS-PRE-001`,
  `HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSWITHREGIONS-PRE-001`, and
  `HLA1516.1-DDM-9_10-SUBSCRIBEINTERACTIONCLASSPASSIVELYWITHREGIONS-PRE-001`
- the direct guard witnesses now also fully close the
  `sendInteractionWithRegions` and
  `requestAttributeValueUpdateWithRegions` exception rows
  `HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-EXC-001`,
  `HLA1516.1-DDM-9_12-RTIAPI-001-EXC`,
  `HLA1516.1-DDM-9_12-RTIAPI-002-EXC`,
  `HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-EXC-001`, and
  `HLA1516.1-DDM-9_13-RTIAPI-001-EXC` because the current negative-path suite
  now isolates the exercised invalid-region, definition-validation,
  class-handle, publication-state, invalid-logical-time,
  execution-membership, connection, and save/restore guard surfaces they
  claimed
- this specifically includes
  `test_register_object_instance_with_regions_rejects_not_connected_not_joined_and_invalid_region`,
  `test_strict_publication_gates_registration_update_and_interaction_sends`,
  `test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`
  and
  `test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`
- use `./tools/test-focus run execution-membership` when the question is about
  joined-versus-not-joined execution-state guards rather than the broader DDM
  capability surface

Use these rerun commands before dropping to raw file paths:

- `./tools/test-focus run backends` for the main 2010 DDM backend slice
- `./tools/test-focus run time` when the DDM issue is coupled to shared
  time/DDM behavior or backend matrices

## Good Reading

Good reading:

- DDM is broadly implemented, linked, and strongly tested
- the family is fully mapped because the last broad exception rows were
  narrowed to directly exercised claims
- the family has a defensible final supported-scope reading without hidden
  partial inventory

Bad reading:

- Clause 9 is mostly unproven
- region overlap, DDM-gated routing, or region lifecycle behavior is still
  speculative
- the old bounded-family partial framing still describes the current state

## Reading Order

1. `requirements/2010/canonical_requirements.json`
2. `requirements/2010/backend_resolution.json`
3. `requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv`
4. `requirements/2010/traceability_matrix.csv`
5. `requirements/2010/hla_1516_master_harmonization_index_v1_0.csv`
6. `tests/backends/test_python_backend_time_ddm_extended.py`
7. `tests/verification/test_compliance_slice_v011.py`

## Related Docs

- [`README.md`](README.md)
- [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
