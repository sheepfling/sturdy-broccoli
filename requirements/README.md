# Requirements

This directory is the source side of the verification package.

Use it to track the three standards as three requirement sources:

- `hla1516_framework_rules.csv`: IEEE 1516-2010 framework and architecture rules
- `hla1516_clause_12_save_restore.csv`: clause-level IEEE 1516-2010 save/restore architecture tranche
- `hla1516_1_federate_interface.csv`: IEEE 1516.1-2010 federate interface families
- `hla1516_1_priority_clauses_4_8_11.csv`: first clause-level extraction tranche for lifecycle time and MOM
- `hla1516_1_clause_4_fm_service_decomposition.csv`: harmonized Federation Management service decomposition for core lifecycle services using `SIG/PRE/EFF/CB/EXC/MOM/TEST` row kinds
- `hla1516_1_clause_5_declaration_management.csv`: clause-level declaration-management extraction tranche
- `hla1516_1_clause_6_object_management.csv`: clause-level object-management extraction tranche including scoped transport supported-subset rows
- `hla1516_1_priority_clauses_7_9_10.csv`: second clause-level extraction tranche for ownership DDM and support services
- `hla1516_2_omt.csv`: IEEE 1516.2-2010 OMT/FOM/MIM families
- `hla1516_2_priority_omt.csv`: clause-level extraction tranche for OMT structure synchronization transportation update-rate switch datatype notes merge and XML rows
- `requirement_id_registry.yaml`: stable ID namespaces and prefixes
- `traceability_matrix.csv`: hand-maintained bridge from seeded family requirements to generated repo artifacts

This directory is intentionally upstream of the generated packet in `analysis/compliance/`.

Use the files together like this:

`requirements/*.csv -> analysis/compliance/requirements_matrix_2010.* -> tests/verification/*`

The family seed rows are placeholders for requirement extraction.

The first concrete clause-level extraction tranches are:

- `hla1516_1_priority_clauses_4_8_11.csv`
- `hla1516_1_clause_4_fm_service_decomposition.csv`
- `hla1516_1_clause_5_declaration_management.csv`
- `hla1516_1_clause_6_object_management.csv`
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

The canonical hierarchy view for these sources lives in
[`docs/verification/requirements_hierarchy.md`](../docs/verification/requirements_hierarchy.md).
