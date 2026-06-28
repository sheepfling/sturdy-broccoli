# IEEE 1516-2010 Requirements And Traceability

Use this page when the question is:

- what is the repo's 2010 requirement source surface?
- where do the 2010 requirement ledgers and mappings live?
- where should someone start reading 2010 requirements-facing material?

Start here, then continue into:

1. [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
2. [`../../verification/README.md`](../../verification/README.md)
3. one focused 2010 source ledger or reconciliation file from the family you care about

Use this reading rule:

- this README is the human-facing front door for the 2010 requirement surface
- `requirements/2010/README.md` is the collected source-side inventory
- `verification/README.md` explains where proof packets, clause matrices, and generated evidence live

## Edition Inventory

The 2010 requirement surface is intentionally collected through the source-side
2010 view at [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md).
That edition inventory covers:

- framework and architecture rules
- federate interface clause extractions
- declaration, object, ownership, time, DDM, support, and MOM reconciliations
- OMT, OMT/XML, and XML reconciliations
- traceability and packet-hookup ledgers

## Practical Flow

Use this order:

1. open the 2010 source-side inventory
2. pick one requirement family or clause ledger
3. open `verification/README.md` when you need the proof packet or executable evidence side

## Basic Execution Rules

Use this section when the question is whether the 2010 requirement surface
already covers the basic federation-execution state rules:

- this is the canonical 2010 "have we joined yet?" rule family for
  execution-affecting calls

- connect before RTI interaction
- create and destroy federation execution preconditions
- joined versus not-joined execution-member guards
- plain object registration rejected until the caller has joined
- delete, local-delete, update, interaction, query, and region-gated DDM
  services rejected until the caller has joined
- concretely, `updateAttributeValues`, `sendInteraction`,
  `requestAttributeValueUpdate`, `queryAttributeTransportationType`,
  `sendInteractionWithRegions`, and
  `requestAttributeValueUpdateWithRegions` all stay inside that joined-state
  guard family
- after resign, those execution-affecting services continue to reject the
  caller as no longer joined, including delete/local-delete plus the
  region-gated DDM send and request-update variants
- resign before disconnect
- destroy rejected while federates are still joined
- after destroy succeeds, later destroy or join attempts against that missing
  federation reject with `FederationExecutionDoesNotExist`
- federation membership listing and reporting

Primary owner surfaces:

- `requirements/2010/hla1516_1_clause_4_fm_service_decomposition.csv` for the
  Clause 4 service-level `PRE`, `EFF`, and `EXC` rows
- `requirements/2010/hla1516_1_fm_detailed_reconciliation.csv` for the
  canonical 2010 federation-management closure rows
- [`../execution_membership_rules.md`](../execution_membership_rules.md) for
  one cross-edition index covering join, destroy, update, delete, query, and
  region-gated not-joined rules
- [`federation_management_bounded_family.md`](federation_management_bounded_family.md)
  for the bounded-family reading when a Clause 4 row remains `partial`
- [`object_management_bounded_family.md`](object_management_bounded_family.md)
  for the bounded-family reading covering not-joined rejection on update,
  interaction, and query services
- [`data_distribution_management_bounded_family.md`](data_distribution_management_bounded_family.md)
  for the bounded-family reading covering not-joined rejection on
  region-gated send and request-update services

Representative 2010 requirement rows for this rule set:

- `HLA1516.1-FM-4_2-RTIAPI-001-EXC` for connect-state guard exceptions
- `HLA1516.1-FM-4_6-RTIAPI-001-EXC` for destroy rejection while federates are
  still joined and for missing-federation rejection
- `HLA1516.1-FM-4_9-RTIAPI-001-EXC` for join preconditions, duplicate-name
  rejection, already-joined rejection, and not-connected rejection
- `HLA1516.1-FM-4_10-RTIAPI-001-EXC` for resign preconditions and joined-state
  exit guards
- `HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-PRE-001` for not-joined single-name
  reservation preconditions on the exercised path
- `HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001` for not-joined register
  preconditions and duplicate-name or save-restore guards on the exercised
  overloads
- `HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001` for not-joined delete
  preconditions on the exercised overloads
- `HLA1516.1-OM-6_16-LOCALDELETEOBJECTINSTANCE-PRE-001` for not-joined
  local-delete preconditions on the exercised overload
- `HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-PRE-001` for not-joined update
  preconditions
- `HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001` for not-joined interaction-send
  preconditions on the exercised overloads
- `HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001` for the explicit
  `updateAttributeValues` membership and connection exception envelope
- `HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001` for the matching
  `sendInteraction` membership and connection exception envelope
- `HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-PRE-001` for not-joined
  attribute-value-update request preconditions
- `HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-PRE-001` for not-joined
  transportation-query preconditions on the supported transport subset
- `HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-PRE-001` for not-joined
  region-gated interaction-send preconditions
- `HLA1516.1-DDM-9_12-SENDINTERACTIONWITHREGIONS-EXC-001` for the explicit
  `sendInteractionWithRegions` membership and connection exception envelope
- `HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-PRE-001` for
  not-joined region-gated attribute-value-update request preconditions
- `HLA1516.1-DDM-9_13-REQUESTATTRIBUTEVALUEUPDATEWITHREGIONS-EXC-001` for the
  explicit `requestAttributeValueUpdateWithRegions` membership and connection
  exception envelope

The main execution-state guard exceptions are already part of that ownership
surface:

- `NotConnected`
- `FederateNotExecutionMember`
- `FederatesCurrentlyJoined`
- `FederationExecutionDoesNotExist`

Primary executable anchors:

- `tests/backends/test_python_backend_federation_extended.py`
- `tests/backends/test_python_backend_object_ownership_extended.py`
- `tests/backends/test_python_backend_time_ddm_extended.py`
- `tests/scenarios/test_federation_lifecycle_backend_matrix.py`
- `tests/scenarios/test_federation_management_backend_matrix.py`
- `./tools/test-focus run execution-membership`

Use these concrete anchors first when the question is "have we proved the
basic execution lifecycle rules?" rather than "which broader bounded-family
tail remains partial?".

The intended 2010 state-machine reading is:

- `NotConnected` before connect or after disconnect
- `FederateNotExecutionMember` before join and again after resign
- `FederatesCurrentlyJoined` when destroy is attempted while members are still
  joined
- `FederationExecutionDoesNotExist` after the federation has already been
  destroyed

## Shards And Views

Use the shared matrix model from
[`../../plans/requirements_remaining_closure.md`](../../plans/requirements_remaining_closure.md):

- `shards` are the executable ownership units
- `views` are overlapping audit or closeout cuts across shards
- every 2010 requirement bucket should point at one narrowest primary shard first
- widen to a broader lane only when the requirement claim actually crosses that boundary

For 2010 work, the usual ownership pattern is:

- source requirement family in [`../../../requirements/2010/README.md`](../../../requirements/2010/README.md)
- canonical closure or status row in the family CSV or `traceability_matrix.csv`
- backend split in a linked companion artifact such as `requirements/2010/hla1516_1_priority_backend_resolution.csv` when backend truth differs by runtime even though the owner row is already closed for the repo-supported claim
- bounded mixed-backend final-state note in [`mixed_backend_priority_boundaries.md`](mixed_backend_priority_boundaries.md) when the question is how to read those canonical pass rows honestly without flattening vendor divergence
- bounded support-services family note in [`support_services_bounded_family.md`](support_services_bounded_family.md) when the question is why Clause 10 still has a narrow `PRE/EXC/EXC_API` partial tail even though service, signature, MOM, and main negative-path coverage are already strong
- bounded federation-management family note in [`federation_management_bounded_family.md`](federation_management_bounded_family.md) when the question is why Clause 4 still has a mixed `ARG/EFF/CB_ORD/EXC` partial tail even though most lifecycle, synchronization, and save/restore services are already strongly covered
- bounded declaration-management family note in [`declaration_management_bounded_family.md`](declaration_management_bounded_family.md) when the question is how to read Clause 5 as fully mapped through intentionally narrowed direct-guard claims instead of the older partial-tail framing
- bounded object-management family note in [`object_management_bounded_family.md`](object_management_bounded_family.md) when the question is how to read Clause 6 as fully mapped through direct runtime witnesses and supported-subset boundaries instead of the older partial-tail framing
- bounded ownership-management family note in [`ownership_management_bounded_family.md`](ownership_management_bounded_family.md) when the question is how to read Clause 7 as fully mapped through intentionally narrowed direct-guard claims instead of the older partial-tail framing
- bounded time-management family note in [`time_management_bounded_family.md`](time_management_bounded_family.md) when the question is why Clause 8 still has a `PRE/EXC/EXC_API` partial tail plus one broad overview row even though most direct logical-time, lookahead, callback-order, retraction, and query behavior is already strongly covered
- bounded data-distribution-management family note in [`data_distribution_management_bounded_family.md`](data_distribution_management_bounded_family.md) when the question is why Clause 9 still has a `PRE/EXC/EXC_API` partial tail even though most direct region lifecycle, overlap-routing, DDM-gated routing, and MOM behavior is already strongly covered
- bounded OMT/XML family note in [`omt_xml_bounded_family.md`](omt_xml_bounded_family.md) when the question is how the imported XML element or type rows remain partial while the Annex B normalization story is already closed on the supported common subset
- primary proof shard or focused command from [`../../test_surface.md`](../../test_surface.md)
- proof artifact or verification packet from [`../../verification/README.md`](../../verification/README.md)

Preferred closure-table columns:

| Column | Meaning |
| --- | --- |
| `Requirement family` | clause or capability family being closed |
| `Requirement IDs` | exact 2010 IDs or grouped clause rows |
| `Canonical status` | `planned`, `partial`, or `mapped` |
| `Backend resolution` | separate backend-specific result columns or a linked backend-resolution artifact such as `requirements_matrix_2010.*` or generated backend disposition ledgers |
| `Primary shard` | first canonical owning shard |
| `Widen to` | broader lane only if the requirement boundary requires it |
| `View tags` | overlapping audit cuts such as `ownership`, `time`, `fom-omt`, or `setup-preflight` |
| `Evidence artifact` | CSV, packet, JSON, or proof note that records the result |
| `Boundary note` | honest supported-scope note when the proof is narrower than the full standard wording |

Practical rule:

- keep 2010 closeout owned by shards
- use views to answer cross-family questions such as time, ownership, setup, or OMT
- do not let a view replace shard ownership in repo-green or requirement status changes
- do not overload one status field to mean both clause closure and backend-by-backend support

## Canonical Owner Surfaces

Use this index when the question is "which single document or ledger owns this
2010 requirement bucket?"

| Bucket | Canonical owner doc | Primary shard | Typical view tags |
| --- | --- | --- | --- |
| framework and architecture reconciliation | `../../../requirements/2010/hla1516_framework_detailed_reconciliation.csv` | `unit-foundation` | `2010-core`, `setup-preflight` |
| federation-management clause and family rows | `../../../requirements/2010/hla1516_1_fm_detailed_reconciliation.csv` | `unit-scenarios-light` | `2010-core`, `scenarios`, `save-restore` |
| federation-management bounded partial-family reading | `federation_management_bounded_family.md` | `unit-scenarios-light` | `2010-core`, `scenarios`, `save-restore` |
| declaration-management clause and family rows | `../../../requirements/2010/hla1516_1_dm_detailed_reconciliation.csv` | `unit-foundation` | `2010-core`, `setup-preflight` |
| declaration-management bounded family reading | `declaration_management_bounded_family.md` | `unit-foundation` | `2010-core`, `setup-preflight` |
| object-management clause and family rows | `../../../requirements/2010/hla1516_1_om_detailed_reconciliation.csv` | `unit-scenarios-light` | `2010-core`, `scenarios` |
| object-management bounded family reading | `object_management_bounded_family.md` | `unit-scenarios-light` | `2010-core`, `scenarios` |
| ownership-management clause and family rows | `../../../requirements/2010/hla1516_1_own_detailed_reconciliation.csv` | `unit-scenarios-light` | `2010-core`, `ownership`, `scenarios` |
| ownership-management bounded family reading | `ownership_management_bounded_family.md` | `unit-scenarios-light` | `2010-core`, `ownership`, `scenarios` |
| time-management clause and family rows | `../../../requirements/2010/hla1516_1_tm_detailed_reconciliation.csv` | `unit-python-core` | `2010-core`, `time` |
| time-management bounded partial-family reading | `time_management_bounded_family.md` | `unit-python-core` | `2010-core`, `time` |
| DDM clause and family rows | `../../../requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv` | `unit-python-core` | `2010-core`, `time`, `scenarios` |
| DDM bounded partial-family reading | `data_distribution_management_bounded_family.md` | `unit-python-core` | `2010-core`, `time`, `scenarios` |
| support-services clause and family rows | `../../../requirements/2010/hla1516_1_sup_detailed_reconciliation.csv` | `unit-python-core` | `2010-core`, `setup-preflight` |
| support-services bounded partial-family reading | `support_services_bounded_family.md` | `unit-python-core` | `2010-core`, `setup-preflight` |
| MOM/MIM clause and family rows | `../../../requirements/2010/hla1516_1_mom_detailed_reconciliation.csv` | `unit-python-core` | `2010-core`, `time` |
| API-binding and Clause 13 conformance rows | `../../../requirements/2010/hla1516_1_conf_detailed_reconciliation.csv` | `unit-shim-tooling` | `2010-core`, `java-shim`, `cpp-shim` |
| OMT family reconciliation rows | `../../../requirements/2010/hla1516_2_omt_detailed_reconciliation.csv` | `unit-fom-tooling` | `2010-core`, `fom-omt` |
| XML family reconciliation rows | `../../../requirements/2010/hla1516_xml_detailed_reconciliation.csv` | `unit-fom-tooling` | `2010-core`, `fom-omt` |
| legacy OMT/XML bridge artifact | `../../../requirements/2010/hla1516_2_omt_xml_detailed_reconciliation.csv` | `unit-fom-tooling` | `2010-core`, `fom-omt` |
| OMT/XML bounded family reading | `omt_xml_bounded_family.md` | `unit-fom-tooling` | `2010-core`, `fom-omt` |
| imported-master and broad bridge status | `../../../requirements/2010/traceability_matrix.csv` | `unit-foundation` | `2010-core`, `setup-preflight` |
| bounded mixed-backend priority-row runtime split | `../../../requirements/2010/hla1516_1_priority_backend_resolution.csv` | `unit-scenarios-light` or `unit-python-core` by row | `2010-core`, `scenarios`, `time` |
| bounded mixed-backend final-state reading | `mixed_backend_priority_boundaries.md` | `unit-scenarios-light` or `unit-python-core` by row | `2010-core`, `scenarios`, `time` |

Reading rule:

1. start with the canonical owner doc above
2. then open the supporting proof artifact or packet from `verification/README.md`
3. only after that widen to broader scenario, OMT, or cross-family views

## Honest 100 Percent Reading

Use this section when the question is not just "which 2010 owner doc applies?"
but "what would it take to finish the remaining bounded 2010 story honestly?"

Current closeout reading:

- the current `2010` backend-compliance packet no longer contains any hidden
  `planned` inventory
- the remaining non-`pass` packet rows are maintained bounded-family,
  mixed-backend, or explicitly aggregated OMT/XML boundary surfaces
- the active question is no longer whether owner docs are missing
- the active question is whether the repo wants to tighten specific bounded
  rows into narrower direct proof or keep the current bounded final-state
  reading

Use these owner companions for that closeout program:

- [`../../plans/PLN-004_python_rti_100_percent_compliance_plan.md`](../../plans/PLN-004_python_rti_100_percent_compliance_plan.md)
- [`../../plans/2010_python_rti_bounded_family_execution_worklist.md`](../../plans/2010_python_rti_bounded_family_execution_worklist.md)
- [`../../plans/requirements_completion_audit.md`](../../plans/requirements_completion_audit.md)

Reading rule:

1. use this README for the canonical 2010 owner map
2. use `2010_python_rti_bounded_family_execution_worklist.md` for the exact
   bounded buckets, primary shards, and tighten-versus-stay-bounded rule
3. use `requirements_completion_audit.md` for the cross-edition honest answer
   to whether closeout is finished

## Related Docs

- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
- [`../../plans/PLN-004_python_rti_100_percent_compliance_plan.md`](../../plans/PLN-004_python_rti_100_percent_compliance_plan.md)
- [`../../plans/requirements_completion_audit.md`](../../plans/requirements_completion_audit.md)
- [`../../plans/requirements_remaining_closure.md`](../../plans/requirements_remaining_closure.md)
- [`../../plans/2010_python_rti_bounded_family_execution_worklist.md`](../../plans/2010_python_rti_bounded_family_execution_worklist.md)
- [`mixed_backend_priority_boundaries.md`](mixed_backend_priority_boundaries.md)
- [`federation_management_bounded_family.md`](federation_management_bounded_family.md)
- [`declaration_management_bounded_family.md`](declaration_management_bounded_family.md)
- [`object_management_bounded_family.md`](object_management_bounded_family.md)
- [`ownership_management_bounded_family.md`](ownership_management_bounded_family.md)
- [`time_management_bounded_family.md`](time_management_bounded_family.md)
- [`data_distribution_management_bounded_family.md`](data_distribution_management_bounded_family.md)
- [`omt_xml_bounded_family.md`](omt_xml_bounded_family.md)
- [`support_services_bounded_family.md`](support_services_bounded_family.md)
- [`../../test_surface.md`](../../test_surface.md)
- [`../../spec_reading_map.md`](../../spec_reading_map.md)
- [`../../../requirements/README.md`](../../../requirements/README.md)
