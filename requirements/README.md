# Requirements

This directory is the source side of the verification package.

Use it to track the three standards as three requirement sources:

- `hla1516_framework_rules.csv`: IEEE 1516-2010 framework and architecture rules
- `hla1516_clause_12_save_restore.csv`: clause-level IEEE 1516-2010 save/restore architecture tranche
- `hla1516_1_federate_interface.csv`: IEEE 1516.1-2010 federate interface families
- `hla1516_1_priority_clauses_4_8_11.csv`: first clause-level extraction tranche for lifecycle time and MOM
- `hla1516_1_clause_4_fm_service_decomposition.csv`: harmonized Federation Management service decomposition for core lifecycle services using `SIG/PRE/EFF/CB/EXC/MOM/TEST` row kinds
- `hla1516_1_clause_5_declaration_management.csv`: clause-level declaration-management extraction tranche
- `hla1516_1_clause_5_dm_detailed_reconciliation.csv`: packet-derived detailed Clause 5 service reconciliation keyed to current repo tests and statuses
- `hla1516_1_clause_6_object_management.csv`: clause-level object-management extraction tranche including scoped transport supported-subset rows
- `hla1516_1_clause_6_om_detailed_reconciliation.csv`: packet-derived detailed Clause 6 service reconciliation keyed to current repo tests and statuses
- `hla1516_1_clause_7_own_detailed_reconciliation.csv`: packet-derived detailed Clause 7 ownership-management reconciliation keyed to current repo tests and statuses
- `hla1516_1_clause_8_tm_detailed_reconciliation.csv`: packet-derived detailed Clause 8 time-management reconciliation keyed to current repo tests and statuses
- `hla1516_1_clause_9_ddm_detailed_reconciliation.csv`: packet-derived detailed Clause 9 data-distribution-management reconciliation keyed to current repo tests and statuses
- `hla1516_1_priority_clauses_7_9_10.csv`: second clause-level extraction tranche for ownership DDM and support services
- `hla1516_2_omt.csv`: IEEE 1516.2-2010 OMT/FOM/MIM families
- `hla1516_2_priority_omt.csv`: clause-level extraction tranche for OMT structure synchronization transportation update-rate switch datatype notes merge and XML rows
- `requirement_id_registry.yaml`: stable ID namespaces and prefixes
- `traceability_matrix.csv`: hand-maintained bridge from seeded family requirements to generated repo artifacts

This directory is intentionally upstream of the generated packet in `analysis/compliance/`.

The repo also carries a versioned raw packet intake at
`requirements/imports/hla_1516_requirements_codebase_packet_v1_0/`.
Use that import tree when you need the external v1.0 dump, its manifest,
history files, or the integration workpacket.

That import is deliberately not flattened onto the curated top-level
`requirements/*.csv` files. The top-level files remain the harmonized
working set for repo-native requirement engineering.

Restricted IEEE source inputs from the packet were intentionally not copied
into the committed import tree; see the import README for the policy note.

Use the files together like this:

`requirements/*.csv -> analysis/compliance/requirements_matrix_2010.* -> tests/verification/*`

The family seed rows are placeholders for requirement extraction.

The first concrete clause-level extraction tranches are:

- `hla1516_1_priority_clauses_4_8_11.csv`
- `hla1516_1_clause_4_fm_service_decomposition.csv`
- `hla1516_1_clause_5_declaration_management.csv`
- `hla1516_1_clause_5_dm_detailed_reconciliation.csv`
- `hla1516_1_clause_6_object_management.csv`
- `hla1516_1_clause_6_om_detailed_reconciliation.csv`
- `hla1516_1_clause_7_own_detailed_reconciliation.csv`
- `hla1516_1_clause_8_tm_detailed_reconciliation.csv`
- `hla1516_1_clause_9_ddm_detailed_reconciliation.csv`
- `hla1516_clause_12_save_restore.csv`
- `hla1516_1_priority_clauses_7_9_10.csv`
- `hla1516_2_priority_omt.csv`

`hla1516_1_clause_4_fm_service_decomposition.csv` is the bridge from coarse service rows to implementation-driving requirements:

- `SIG`: service signature and callable API surface
- `PRE`: required preconditions and state guards
- `EFF`: state transition and durable side effects
- `CB`: required callback behavior or callback consequences
- `EXC`: distinct exception and failure families
- `MOM`: MOM or reporting obligations exposed to observers
- `TEST`: executable verification and transport-equivalence expectations

This decomposition file is still an engineering seed. It is deliberately narrower than a certified paragraph-by-paragraph extraction and should be expanded clause-by-clause as the spec text is normalized.

`hla1516_1_clause_5_dm_detailed_reconciliation.csv` plays a similar bridge role for Declaration Management, but starts from the imported packet's finer-grained `SVC/SIG/ARG/PRE/EFF/EXC/MOM/TEST` service slices and maps them onto the repo's current tests and `mapped/partial/planned` status vocabulary.

`hla1516_1_clause_6_om_detailed_reconciliation.csv` applies that same packet-to-curated bridge pattern to Clause 6 Object Management, starting from the imported packet's `SEM/SVC/SIG/ARG/PRE/EFF/EXC/MOM` slices and explicitly marking where the current repo only covers a supported transport subset or still lacks direct MOM and callback-family evidence.

`hla1516_1_clause_7_own_detailed_reconciliation.csv` extends that packet-to-curated bridge pattern to Clause 7 Ownership Management, starting from the imported packet's `SVC/SIG/ARG/PRE/EFF/EXC/MOM/TEST` service slices plus callback `CB/CB_SIG/CB_PAYLOAD/CB_ORDER` rows and marking where current ownership coverage is direct, broader-than-current, or still missing static-signature and MOM observer evidence.

`hla1516_1_clause_8_tm_detailed_reconciliation.csv` applies that same packet-to-curated bridge pattern to Clause 8 Time Management, starting from the imported packet's service `SVC/SIG/ARG/PRE/EFF/EXC/MOM/TEST` slices plus callback `CB/CB_SIG/CB_PAYLOAD/CB_ORDER` rows and marking where current time-management coverage is direct, broader-than-current, or still missing dedicated MOM observer evidence.

`hla1516_1_clause_9_ddm_detailed_reconciliation.csv` applies that same packet-to-curated bridge pattern to Clause 9 Data Distribution Management, starting from the imported packet's service `SVC/SIG/ARG/PRE/EFF/EXC/MOM/TEST` slices and marking where current region-lifecycle, region-subscription, and region-filtering coverage is direct, broader-than-current, or still missing dedicated MOM observer evidence.

The canonical hierarchy view for these sources lives in
[`docs/verification/requirements_hierarchy.md`](../docs/verification/requirements_hierarchy.md).
