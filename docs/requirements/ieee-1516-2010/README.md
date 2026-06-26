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
- backend split in a linked companion artifact such as `requirements/2010/hla1516_1_priority_backend_resolution.csv` when the owner row is still partial for cross-backend reasons
- bounded mixed-backend final-state note in [`mixed_backend_priority_boundaries.md`](mixed_backend_priority_boundaries.md) when the question is how to read those partial rows honestly
- bounded support-services family note in [`support_services_bounded_family.md`](support_services_bounded_family.md) when the question is why Clause 10 still has a narrow `PRE/EXC/EXC_API` partial tail even though service, signature, MOM, and main negative-path coverage are already strong
- bounded federation-management family note in [`federation_management_bounded_family.md`](federation_management_bounded_family.md) when the question is why Clause 4 still has a mixed `ARG/EFF/CB_ORD/EXC` partial tail even though most lifecycle, synchronization, and save/restore services are already strongly covered
- bounded declaration-management family note in [`declaration_management_bounded_family.md`](declaration_management_bounded_family.md) when the question is why Clause 5 still has a `PRE/EXC/EXC_API` partial tail even though most direct publication, subscription, declaration-callback, and MOM behavior is already strongly covered
- bounded object-management family note in [`object_management_bounded_family.md`](object_management_bounded_family.md) when the question is why Clause 6 still has a mixed `EFF/CB_ORD/CB_ORDER/EXC_API/EXC/PRE` partial tail even though most naming, discovery, update, interaction, delete, and supported transport-subset paths are already strongly covered
- bounded ownership-management family note in [`ownership_management_bounded_family.md`](ownership_management_bounded_family.md) when the question is why Clause 7 still has a `PRE/EXC/EXC_API` partial tail even though most direct divestiture, acquisition, callback, query, and MOM behavior is already strongly covered
- bounded time-management family note in [`time_management_bounded_family.md`](time_management_bounded_family.md) when the question is why Clause 8 still has a `PRE/EXC/EXC_API` partial tail plus one broad overview row even though most direct logical-time, lookahead, callback-order, retraction, and query behavior is already strongly covered
- bounded data-distribution-management family note in [`data_distribution_management_bounded_family.md`](data_distribution_management_bounded_family.md) when the question is why Clause 9 still has a `PRE/EXC/EXC_API` partial tail even though most direct region lifecycle, overlap-routing, DDM-gated routing, and MOM behavior is already strongly covered
- bounded OMT/XML family note in [`omt_xml_bounded_family.md`](omt_xml_bounded_family.md) when the question is why the imported XML element or type rows and the small Annex B normalization tail still remain partial even though parser, validator, and round-trip coverage are already strong
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
| declaration-management bounded partial-family reading | `declaration_management_bounded_family.md` | `unit-foundation` | `2010-core`, `setup-preflight` |
| object-management clause and family rows | `../../../requirements/2010/hla1516_1_om_detailed_reconciliation.csv` | `unit-scenarios-light` | `2010-core`, `scenarios` |
| object-management bounded partial-family reading | `object_management_bounded_family.md` | `unit-scenarios-light` | `2010-core`, `scenarios` |
| ownership-management clause and family rows | `../../../requirements/2010/hla1516_1_own_detailed_reconciliation.csv` | `unit-scenarios-light` | `2010-core`, `ownership`, `scenarios` |
| ownership-management bounded partial-family reading | `ownership_management_bounded_family.md` | `unit-scenarios-light` | `2010-core`, `ownership`, `scenarios` |
| time-management clause and family rows | `../../../requirements/2010/hla1516_1_tm_detailed_reconciliation.csv` | `unit-python-core` | `2010-core`, `time` |
| time-management bounded partial-family reading | `time_management_bounded_family.md` | `unit-python-core` | `2010-core`, `time` |
| DDM clause and family rows | `../../../requirements/2010/hla1516_1_ddm_detailed_reconciliation.csv` | `unit-python-core` | `2010-core`, `time`, `scenarios` |
| DDM bounded partial-family reading | `data_distribution_management_bounded_family.md` | `unit-python-core` | `2010-core`, `time`, `scenarios` |
| support-services clause and family rows | `../../../requirements/2010/hla1516_1_sup_detailed_reconciliation.csv` | `unit-python-core` | `2010-core`, `setup-preflight` |
| support-services bounded partial-family reading | `support_services_bounded_family.md` | `unit-python-core` | `2010-core`, `setup-preflight` |
| MOM/MIM clause and family rows | `../../../requirements/2010/hla1516_1_mom_detailed_reconciliation.csv` | `unit-python-core` | `2010-core`, `time` |
| API-binding and Clause 13 conformance rows | `../../../requirements/2010/hla1516_1_conf_detailed_reconciliation.csv` | `unit-shim-tooling` | `2010-core`, `java-shim`, `cpp-shim` |
| OMT family reconciliation rows | `../../../requirements/2010/hla1516_2_omt_detailed_reconciliation.csv` | `unit-fom-tooling` | `2010-core`, `fom-omt` |
| OMT clause-detail and OMT/XML bridge rows | `../../../requirements/2010/hla1516_2_omt_xml_detailed_reconciliation.csv` | `unit-fom-tooling` | `2010-core`, `fom-omt` |
| XML family reconciliation rows | `../../../requirements/2010/hla1516_xml_detailed_reconciliation.csv` | `unit-fom-tooling` | `2010-core`, `fom-omt` |
| OMT/XML bounded partial-family reading | `omt_xml_bounded_family.md` | `unit-fom-tooling` | `2010-core`, `fom-omt` |
| imported-master and broad bridge status | `../../../requirements/2010/traceability_matrix.csv` | `unit-foundation` | `2010-core`, `setup-preflight` |
| bounded mixed-backend priority-row runtime split | `../../../requirements/2010/hla1516_1_priority_backend_resolution.csv` | `unit-scenarios-light` or `unit-python-core` by row | `2010-core`, `scenarios`, `time` |
| bounded mixed-backend final-state reading | `mixed_backend_priority_boundaries.md` | `unit-scenarios-light` or `unit-python-core` by row | `2010-core`, `scenarios`, `time` |

Reading rule:

1. start with the canonical owner doc above
2. then open the supporting proof artifact or packet from `verification/README.md`
3. only after that widen to broader scenario, OMT, or cross-family views

## Related Docs

- [`../../verification/README.md`](../../verification/README.md)
- [`../../verification/requirement_compliance_exports.md`](../../verification/requirement_compliance_exports.md)
- [`../../plans/requirements_remaining_closure.md`](../../plans/requirements_remaining_closure.md)
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
