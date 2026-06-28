# HLA 1516 2010 requirements and mappings

This directory is a path-stable view of the 2010 requirements corpus and
mapping set.

Use this page when the question is:

- where is the full 2010 requirement inventory?
- which file owns one 2010 requirement family?
- how do I stay inside the 2010 surface without mixing in 2025 traceability?

Use this folder when you want a single path that means "all of the 2010
requirements and mappings" without mixing in the 2025 traceability block.

The 2025 traceability and source-trace block lives in [`../2025/`](../2025/).

## Canonical 2010 Inventory

Treat this as the single source-side list for the 2010 edition:

- `README.md`: edition front door for the 2010 source-side surface
- `hla1516_framework_rules.csv`: framework and architecture rule seeds
- `hla1516_framework_detailed_reconciliation.csv`: detailed framework reconciliation
- `hla1516_clause_12_save_restore.csv`: clause-level save/restore tranche
- `hla1516_1_federate_interface.csv`: federate interface family ledger
- `hla1516_1_priority_clauses_4_8_11.csv`: first clause-priority extraction tranche
- `hla1516_1_priority_backend_resolution.csv`: backend-resolution companion for the priority rows where canonical owner status is closed but vendor/runtime truth still differs
- `hla1516_1_priority_clauses_7_9_10.csv`: second clause-priority extraction tranche
- `hla1516_1_clause_4_fm_service_decomposition.csv`: federation management decomposition bridge
- `hla1516_1_fm_detailed_reconciliation.csv`: federation management reconciliation
- `hla1516_1_clause_5_declaration_management.csv`: declaration management clause ledger
- `hla1516_1_clause_5_dm_detailed_reconciliation.csv`: declaration management clause reconciliation
- `hla1516_1_dm_detailed_reconciliation.csv`: declaration management family reconciliation
- `hla1516_1_clause_6_object_management.csv`: object management clause ledger
- `hla1516_1_clause_6_om_detailed_reconciliation.csv`: object management clause reconciliation
- `hla1516_1_om_detailed_reconciliation.csv`: object management family reconciliation
- `hla1516_1_clause_7_own_detailed_reconciliation.csv`: ownership management clause reconciliation
- `hla1516_1_own_detailed_reconciliation.csv`: ownership management family reconciliation
- `hla1516_1_clause_8_tm_detailed_reconciliation.csv`: time management clause reconciliation
- `hla1516_1_tm_detailed_reconciliation.csv`: time management family reconciliation
- `hla1516_1_clause_9_ddm_detailed_reconciliation.csv`: DDM clause reconciliation
- `hla1516_1_ddm_detailed_reconciliation.csv`: DDM family reconciliation
- `hla1516_1_clause_10_sup_detailed_reconciliation.csv`: support services clause reconciliation
- `hla1516_1_sup_detailed_reconciliation.csv`: support services family reconciliation
- `hla1516_1_clause_11_mom_detailed_reconciliation.csv`: MOM clause reconciliation
- `hla1516_1_mom_detailed_reconciliation.csv`: MOM family reconciliation
- `hla1516_1_api_detailed_reconciliation.csv`: API-binding reconciliation
- `hla1516_1_conf_detailed_reconciliation.csv`: Clause 13 conformance reconciliation
- `hla1516_2_omt.csv`: OMT family ledger
- `hla1516_2_priority_omt.csv`: priority OMT tranche
- `hla1516_2_omt_detailed_reconciliation.csv`: OMT family reconciliation
- `hla1516_2_omt_xml_detailed_reconciliation.csv`: legacy OMT/XML bridge reconciliation artifact
- `hla1516_xml_detailed_reconciliation.csv`: XML family reconciliation
- `hla_1516_master_harmonization_index_v1_0.csv`: imported-master harmonization index
- `hla_1516_packet_hookup_status_v1_0.csv`: packet hookup status ledger
- `requirement_id_registry.yaml`: stable requirement ID registry
- `traceability_matrix.csv`: top-level traceability bridge

## Reading Order

Use this order:

1. `traceability_matrix.csv` for the broad bridge
2. one clause or family reconciliation file for the area you care about
3. `hla_1516_master_harmonization_index_v1_0.csv` only when you need the whole imported-master view

## Canonical Owner Surfaces

Use these files as the single source-side owners for the main 2010 requirement
bucket families:

| Bucket | Canonical owner file |
| --- | --- |
| framework and architecture reconciliation | `hla1516_framework_detailed_reconciliation.csv` |
| federation management | `hla1516_1_fm_detailed_reconciliation.csv` |
| declaration management | `hla1516_1_dm_detailed_reconciliation.csv` |
| object management | `hla1516_1_om_detailed_reconciliation.csv` |
| ownership management | `hla1516_1_own_detailed_reconciliation.csv` |
| time management | `hla1516_1_tm_detailed_reconciliation.csv` |
| data distribution management | `hla1516_1_ddm_detailed_reconciliation.csv` |
| support services | `hla1516_1_sup_detailed_reconciliation.csv` |
| MOM/MIM | `hla1516_1_mom_detailed_reconciliation.csv` |
| API binding and Clause 13 conformance | `hla1516_1_conf_detailed_reconciliation.csv` |
| OMT family | `hla1516_2_omt_detailed_reconciliation.csv` |
| XML family | `hla1516_xml_detailed_reconciliation.csv` |
| legacy OMT/XML bridge artifact | `hla1516_2_omt_xml_detailed_reconciliation.csv` |
| broad status bridge | `traceability_matrix.csv` |
| bounded mixed-backend runtime split for priority rows | `hla1516_1_priority_backend_resolution.csv` |

If a future edit changes status for one of these families, update the canonical
owner file first, then reflect the change in `traceability_matrix.csv`,
`hla_1516_master_harmonization_index_v1_0.csv`, and the relevant verification
artifact.

Use `hla1516_1_priority_backend_resolution.csv` when the canonical owner row is
already closed for the repo-supported claim but the backend truth still differs
by runtime. That companion keeps `python`, `certi`, `pitch`, and `portico`
answers separate from the requirement-level status.

For the human-facing explanation of why those rows are now canonical `pass`
while backend resolution still differs by runtime,
use:

- `docs/requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md`

For the human-facing explanation of the remaining `CAP-SUP` partial family and
why the Clause 10 tail is now an explicit bounded `PRE/EXC/EXC_API` granularity
limit rather than a vague support-services gap, use:

- `docs/requirements/ieee-1516-2010/support_services_bounded_family.md`

For the human-facing explanation of the remaining `CAP-FM` partial family and
why the Clause 4 tail is now an explicit bounded `ARG/EFF/CB_ORD/EXC`
granularity limit rather than a vague federation-management gap, use:

- `docs/requirements/ieee-1516-2010/federation_management_bounded_family.md`

For the human-facing explanation of the final `CAP-DM` closeout reading and
how Clause 5 is now fully mapped through intentionally narrowed direct-guard
claims, use:

- `docs/requirements/ieee-1516-2010/declaration_management_bounded_family.md`

For the human-facing explanation of the final `CAP-OM` closeout reading and
how Clause 6 is now fully mapped through direct runtime witnesses plus
supported-subset boundaries, use:

- `docs/requirements/ieee-1516-2010/object_management_bounded_family.md`

For the human-facing explanation of the final `CAP-OWN` closeout reading and
how Clause 7 is now fully mapped through intentionally narrowed direct-guard
claims, use:

- `docs/requirements/ieee-1516-2010/ownership_management_bounded_family.md`

For the human-facing explanation of the remaining `CAP-TM` partial family and
why the Clause 8 tail is now an explicit bounded
`PRE/EXC/EXC_API` plus one broad overview-row granularity limit rather than a
vague time-management gap, use:

- `docs/requirements/ieee-1516-2010/time_management_bounded_family.md`

For the human-facing explanation of the remaining `CAP-DDM` partial family and
why the Clause 9 tail is now an explicit bounded
`PRE/EXC/EXC_API` granularity limit rather than a vague data-distribution
management gap, use:

- `docs/requirements/ieee-1516-2010/data_distribution_management_bounded_family.md`

For the human-facing explanation of how the separate `CAP-XML` atom-granularity
tail and the now-closed common-subset Annex B `CAP-OMT` normalization story fit
together as one bounded final-state reading rather than a vague parser or
schema-support gap, use:

- `docs/requirements/ieee-1516-2010/omt_xml_bounded_family.md`
