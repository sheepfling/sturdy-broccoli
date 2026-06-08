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
- `hla1516_1_clause_10_sup_detailed_reconciliation.csv`: packet-derived detailed Clause 10 support-services reconciliation keyed to current repo tests and statuses
- `hla1516_1_clause_11_mom_detailed_reconciliation.csv`: packet-derived detailed Clause 11 MOM/MIM reconciliation keyed to current repo tests and statuses
- `hla1516_2_omt_xml_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.2 OMT/XML reconciliation keyed to current repo parser, merge, MIM, and schema-validation tests
- `hla_1516_packet_hookup_status_v1_0.csv`: repo-native status ledger for the imported work-packet hookup tasks, marking which packet integration tasks are mapped, partial, or still planned in this codebase
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

For packet-facing canonical access inside this repo, use:

- `requirements/latest`: canonical packet latest bundle
- `requirements/catalogs`: carried-forward packet catalogs
- `requirements/history`: packet history bundle
- `requirements/dashboards`: packet dashboard previews
- `requirements/manifests`: committed packet manifest entrypoints

Those packet-facing paths are stable repo-native entrypoints layered on top of
the versioned import tree. The import tree remains the source of truth for the
raw packet version, while these canonical paths are the place to point repo
tooling, docs, and reviewers when they need the packet asset families.

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
- `hla1516_1_clause_10_sup_detailed_reconciliation.csv`
- `hla1516_1_clause_11_mom_detailed_reconciliation.csv`
- `hla1516_clause_12_save_restore.csv`
- `hla1516_1_priority_clauses_7_9_10.csv`
- `hla1516_2_priority_omt.csv`
- `hla1516_2_omt_xml_detailed_reconciliation.csv`

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

`hla1516_1_clause_10_sup_detailed_reconciliation.csv` applies that same packet-to-curated bridge pattern to Clause 10 Support Services, starting from the imported packet's service `SVC/SIG/ARG/PRE/EFF/EXC/MOM/TEST` slices and mapping them onto the repo's current lookup, metadata, normalization, advisory-switch, and callback-control tests while explicitly marking the still-unreconciled MOM observer slice.

`hla1516_1_clause_11_mom_detailed_reconciliation.csv` applies the packet-to-curated bridge pattern to Clause 11 Management Object Model requirements, using the packet's `OVW/OBJ/INT/RTI/SRV/TABLE` row kinds rather than service slices and mapping them onto the repo's current MOM catalog, observer, reporting, action, and runtime evidence while keeping the remaining design-rule-only nonrevision row distinct.

`hla1516_2_omt_xml_detailed_reconciliation.csv` applies that same bridge pattern to the imported IEEE 1516.2 OMT/XML detailed packet. It maps the clause-level `omt_clause_detail` rows directly onto the current curated 1516.2 parser, merge, MIM, and schema-conformance requirements where the repo already has clause-specific evidence, while keeping the imported per-element and per-type `xsd_element_detail` and `xsd_type_detail` rows `partial` to reflect that the repo currently validates Annex D/E behavior at the schema-family and round-trip level rather than as one repo-native requirement per XSD atom.

`hla_1516_packet_hookup_status_v1_0.csv` is the companion bridge for the imported work packet itself. It does not restate clause requirements; it records which codebase-hookup tasks from the packet are already satisfied by the current repo shape, which are only partially satisfied by the current curated workflow, and which remain explicitly open.

The canonical hierarchy view for these sources lives in
[`docs/verification/requirements_hierarchy.md`](../docs/verification/requirements_hierarchy.md).
