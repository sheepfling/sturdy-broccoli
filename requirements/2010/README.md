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
- `canonical_requirements.json`: canonical row-level requirement truth for 2010
- `canonical_requirements.csv`: canonical row-level CSV projection for 2010 with the same row schema as the JSON catalog
- `backend_resolution.json`: canonical backend-resolution companion for 2010
- `backend_resolution.csv`: canonical backend-resolution CSV projection for 2010 with the same row schema as the JSON catalog
- `canonical_row_triage.json`: machine-readable normalization triage over the current 2010 canonical rows marking `keep_in_canonical`, `move_to_projection`, or `needs_manual_decision` during the leaf-only normalization program
- `canonical_projection_rows.json`: explicit downstream projection carrying the demoted `section-area`, `omt-area`, and `verification-slice` rollup rows that no longer belong inside canonical requirement truth
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
- `traceability_matrix.csv`: generated or legacy top-level traceability bridge

## Reading Order

Use this order:

1. `canonical_requirements.json` for the primary row-level requirement surface
2. `canonical_requirements.csv` when you need the same canonical row surface in CSV form
3. `backend_resolution.json` when backend truth differs by runtime
4. `backend_resolution.csv` when you need the same backend-resolution surface in CSV form
5. `canonical_row_triage.json` when you are actively normalizing the 2010 truth surface and need the current keep versus move cut list
6. `canonical_projection_rows.json` when you need the demoted rollup rows without treating them as canonical requirement truth
7. `traceability_matrix.csv` or one clause or family reconciliation file only when you need a generated or legacy projection
8. `hla_1516_master_harmonization_index_v1_0.csv` only when you need the whole imported-master view

## Canonical Owner Surfaces

Use these files as the single source-side owners for the main 2010 requirement
bucket families:

| Bucket | Canonical owner file |
| --- | --- |
| canonical 2010 requirement catalog | `canonical_requirements.json` |
| canonical 2010 requirement catalog CSV projection | `canonical_requirements.csv` |
| canonical 2010 backend-resolution catalog | `backend_resolution.json` |
| canonical 2010 backend-resolution catalog CSV projection | `backend_resolution.csv` |
| framework and architecture reconciliation | `hla1516_framework_detailed_reconciliation.csv` |
| framework bounded-family reading | `docs/requirements/ieee-1516-2010/framework_bounded_family.md` |
| federation management | `hla1516_1_fm_detailed_reconciliation.csv` |
| declaration management | `hla1516_1_dm_detailed_reconciliation.csv` |
| object management | `hla1516_1_om_detailed_reconciliation.csv` |
| ownership management | `hla1516_1_own_detailed_reconciliation.csv` |
| time management | `hla1516_1_tm_detailed_reconciliation.csv` |
| data distribution management | `hla1516_1_ddm_detailed_reconciliation.csv` |
| support services | `hla1516_1_sup_detailed_reconciliation.csv` |
| MOM/MIM | `hla1516_1_mom_detailed_reconciliation.csv` |
| API binding | `hla1516_1_api_detailed_reconciliation.csv` |
| Clause 13 conformance | `hla1516_1_conf_detailed_reconciliation.csv` |
| OMT family | `hla1516_2_omt_detailed_reconciliation.csv` |
| XML family | `hla1516_xml_detailed_reconciliation.csv` |
| legacy OMT/XML bridge artifact | `hla1516_2_omt_xml_detailed_reconciliation.csv` |
| broad status bridge | `traceability_matrix.csv` |
| bounded mixed-backend runtime split for priority rows | `hla1516_1_priority_backend_resolution.csv` |

If a future edit changes status for one of these families, update the canonical
JSON catalog first, then reflect the change in any generated or legacy
projection such as `traceability_matrix.csv`,
`hla_1516_master_harmonization_index_v1_0.csv`, and the relevant verification
artifact.

The CSV companions `canonical_requirements.csv` and `backend_resolution.csv`
are canonical exports, not alternate schemas. They must stay row-for-row and
field-for-field aligned with the matching JSON catalogs.

The rollup-only rows moved into `canonical_projection_rows.json` are no longer
part of the canonical 2010 denominator. They remain available as a generated
projection for review, traceability, and historical continuity only.

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

For the human-facing explanation in the framework bounded-family note for the
remaining `CAP-FW` architectural family and why the framework rows stay partial
even though neighboring executable service families are strongly covered, use:

- `docs/requirements/ieee-1516-2010/framework_bounded_family.md`

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

For the human-facing explanation in the time-management closeout reading for
the final `CAP-TM` closeout state and how Clause 8 is now fully mapped at the
owner-ledger level while the narrower RO/TSO backend split stays owned
separately, use:

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

For the human-facing explanation of why the generated ambassador method surface
is already mapped while the imported C++ header-token and Web Services binding
catalog rows remain intentionally partial, use:

- `docs/requirements/ieee-1516-2010/api_binding_bounded_family.md`

For the human-facing explanation of how the imported Clause 13 federate and
RTI conformance rows are fully mapped through repo-native generated evidence
without claiming external certification, use:

- `docs/requirements/ieee-1516-2010/clause13_conformance_closeout.md`
