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
- `hla1516_2_omt_detailed_reconciliation.csv`: OMT reconciliation
- `hla1516_2_omt_xml_detailed_reconciliation.csv`: OMT/XML reconciliation
- `hla1516_xml_detailed_reconciliation.csv`: XML reconciliation
- `hla_1516_master_harmonization_index_v1_0.csv`: imported-master harmonization index
- `hla_1516_packet_hookup_status_v1_0.csv`: packet hookup status ledger
- `requirement_id_registry.yaml`: stable requirement ID registry
- `traceability_matrix.csv`: top-level traceability bridge

## Reading Order

Use this order:

1. `traceability_matrix.csv` for the broad bridge
2. one clause or family reconciliation file for the area you care about
3. `hla_1516_master_harmonization_index_v1_0.csv` only when you need the whole imported-master view
