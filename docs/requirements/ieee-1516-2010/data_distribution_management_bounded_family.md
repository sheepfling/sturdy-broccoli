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
  - `./tools/test-focus run backends`
  - `./tools/test-focus run time`

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

- `207 mapped`
- `16 partial`

The remaining `16 partial` rows cluster into stable categories:

- `10 EXC_API`
- `6 EXC`

There are no remaining partial DDM rows for:

- service presence
- API signature shape
- main effect slices
- MOM service-reporting observability
- return-value slices
- broad DDM overview routing rows

That means the family is no longer broad proof debt across all of Clause 9.
The remaining bounded area is the negative-path exception envelope.

## What The Categories Mean

### Precondition-envelope tail

There is no remaining `PRE` tail in the current DDM owner ledger.

Recent tightening examples:

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

### Exception-envelope tail

The `6 EXC` and `10 EXC_API` rows usually keep a broader failure envelope than
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
- the broader exception-envelope owner rows
  `HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-EXC-001` and
  `HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-EXC-001` remain
  partial because their full exception universes still exceed the currently
  isolated direct evidence
- this specifically includes
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
