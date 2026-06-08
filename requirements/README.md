# Requirements

This directory is the source side of the verification package.

Use it to track the three standards as three requirement sources:

- `hla1516_framework_rules.csv`: IEEE 1516-2010 framework and architecture rules
- `hla1516_framework_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516-2010 framework reconciliation keyed to current repo rules, docs, and cross-standard evidence
- `hla1516_clause_12_save_restore.csv`: clause-level IEEE 1516-2010 save/restore architecture tranche
- `hla1516_1_federate_interface.csv`: IEEE 1516.1-2010 federate interface families
- `hla1516_1_priority_clauses_4_8_11.csv`: first clause-level extraction tranche for lifecycle time and MOM
- `hla1516_1_clause_4_fm_service_decomposition.csv`: harmonized Federation Management service decomposition for core lifecycle services using `SIG/PRE/EFF/CB/EXC/MOM/TEST` row kinds
- `hla1516_1_fm_detailed_reconciliation.csv`: packet-derived detailed Federation Management reconciliation keyed to the Clause 4 decomposition, lifecycle tests, callback evidence, and save/restore observer slices
- `hla1516_1_clause_5_declaration_management.csv`: clause-level declaration-management extraction tranche
- `hla1516_1_clause_5_dm_detailed_reconciliation.csv`: packet-derived detailed Clause 5 service reconciliation keyed to current repo tests and statuses
- `hla1516_1_dm_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.1 declaration-management family reconciliation keyed to the Clause 5 bridge and current declaration callback and runtime tests
- `hla1516_1_clause_6_object_management.csv`: clause-level object-management extraction tranche including scoped transport supported-subset rows
- `hla1516_1_clause_6_om_detailed_reconciliation.csv`: packet-derived detailed Clause 6 service reconciliation keyed to current repo tests and statuses
- `hla1516_1_om_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.1 object-management family reconciliation keyed to the Clause 6 bridge and callback/runtime tests
- `hla1516_1_clause_7_own_detailed_reconciliation.csv`: packet-derived detailed Clause 7 ownership-management reconciliation keyed to current repo tests and statuses
- `hla1516_1_own_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.1 ownership-management family reconciliation keyed to the Clause 7 bridge and current ownership callback and runtime tests
- `hla1516_1_clause_8_tm_detailed_reconciliation.csv`: packet-derived detailed Clause 8 time-management reconciliation keyed to current repo tests and statuses
- `hla1516_1_tm_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.1 time-management family reconciliation keyed to the Clause 8 bridge and current time-management callback and runtime tests
- `hla1516_1_clause_9_ddm_detailed_reconciliation.csv`: packet-derived detailed Clause 9 data-distribution-management reconciliation keyed to current repo tests and statuses
- `hla1516_1_ddm_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.1 data-distribution-management family reconciliation keyed to the Clause 9 bridge and current DDM callback and runtime tests
- `hla1516_1_clause_10_sup_detailed_reconciliation.csv`: packet-derived detailed Clause 10 support-services reconciliation keyed to current repo tests and statuses
- `hla1516_1_clause_11_mom_detailed_reconciliation.csv`: packet-derived detailed Clause 11 MOM/MIM reconciliation keyed to current repo tests and statuses
- `hla1516_1_mom_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.1 MOM/MIM family reconciliation keyed to Clause 11, standard MIM catalog invariants, and MOM runtime tests
- `hla1516_1_sup_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.1 support-family reconciliation keyed to the Clause 10 bridge and support-service tests
- `hla1516_1_api_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.1 API-binding reconciliation keyed to current repo source-derived metadata, requirements-ledger, and imported binding catalogs
- `hla1516_1_conf_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.1 Clause 13 conformance-package reconciliation keyed to current harmonization, API traceability, and verification-package evidence
- `hla1516_xml_detailed_reconciliation.csv`: packet-derived detailed XML-family reconciliation keyed to current Annex D/E parser and schema-validation evidence
- `hla1516_2_omt_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.2 OMT-family reconciliation keyed to current OMT clause, parser, merge, documentation, and annex evidence
- `hla1516_2_omt_xml_detailed_reconciliation.csv`: packet-derived detailed IEEE 1516.2 OMT/XML reconciliation keyed to current repo parser, merge, MIM, and schema-validation tests
- `hla_1516_master_harmonization_index_v1_0.csv`: full imported-master index marking each packet requirement row as mapped, partial, or still unreconciled against the repo's current detailed bridges
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

## Honest Test Rule

When you turn a requirement row into `mapped` or `partial`, attach a concrete
evidence anchor that proves the claimed behavior. Use one of these shapes:

- a positive test that exercises the exact supported scope
- an explicit negative test that shows the unsupported boundary
- a generated artifact that is itself checked by a regression test

Do not promote a row just because the surrounding implementation looks close.
If the proof only covers a narrower supported subset, keep the broad row
`partial` and make the narrower row explicit. If the claim is vendor-facing,
name the vendor divergence or supported subset in the traceability row rather
than flattening it into an implied parity statement.

If you need to resume this work later, start from
[`docs/plans/requirements_finish_line.md`](../docs/plans/requirements_finish_line.md).
That note is the pinned handoff for the remaining rows and the stop condition.

The family seed rows are placeholders for requirement extraction.

The first concrete clause-level extraction tranches are:

- `hla1516_1_priority_clauses_4_8_11.csv`
- `hla1516_1_clause_4_fm_service_decomposition.csv`
- `hla1516_1_fm_detailed_reconciliation.csv`
- `hla1516_1_clause_5_declaration_management.csv`
- `hla1516_1_clause_5_dm_detailed_reconciliation.csv`
- `hla1516_1_dm_detailed_reconciliation.csv`
- `hla1516_1_clause_6_object_management.csv`
- `hla1516_1_clause_6_om_detailed_reconciliation.csv`
- `hla1516_1_om_detailed_reconciliation.csv`
- `hla1516_1_clause_7_own_detailed_reconciliation.csv`
- `hla1516_1_own_detailed_reconciliation.csv`
- `hla1516_1_clause_8_tm_detailed_reconciliation.csv`
- `hla1516_1_tm_detailed_reconciliation.csv`
- `hla1516_1_clause_9_ddm_detailed_reconciliation.csv`
- `hla1516_1_ddm_detailed_reconciliation.csv`
- `hla1516_1_clause_10_sup_detailed_reconciliation.csv`
- `hla1516_1_clause_11_mom_detailed_reconciliation.csv`
- `hla1516_1_mom_detailed_reconciliation.csv`
- `hla1516_1_sup_detailed_reconciliation.csv`
- `hla1516_1_api_detailed_reconciliation.csv`
- `hla1516_1_conf_detailed_reconciliation.csv`
- `hla1516_xml_detailed_reconciliation.csv`
- `hla1516_2_omt_detailed_reconciliation.csv`
- `hla1516_clause_12_save_restore.csv`
- `hla1516_framework_detailed_reconciliation.csv`
- `hla1516_1_priority_clauses_7_9_10.csv`
- `hla1516_2_priority_omt.csv`
- `hla1516_2_omt_xml_detailed_reconciliation.csv`
- `hla_1516_master_harmonization_index_v1_0.csv`

`hla1516_1_clause_4_fm_service_decomposition.csv` is the bridge from coarse service rows to implementation-driving requirements:

- `SIG`: service signature and callable API surface
- `PRE`: required preconditions and state guards
- `EFF`: state transition and durable side effects
- `CB`: required callback behavior or callback consequences
- `EXC`: distinct exception and failure families
- `MOM`: MOM or reporting obligations exposed to observers
- `TEST`: executable verification and transport-equivalence expectations

This decomposition file is still an engineering seed. It is deliberately narrower than a certified paragraph-by-paragraph extraction and should be expanded clause-by-clause as the spec text is normalized.

`hla1516_1_fm_detailed_reconciliation.csv` is the imported-master companion to that Clause 4 decomposition. It maps the packet's finer-grained Federation Management rows such as `SVC`, `ARG`, `PRE`, `EFF`, `EXC`, `MOM`, `RTI_API`, `SIG`, `EXC_API`, `MOM_TRACE`, `FED_CB`, `CB_SIG`, and `CB_ORD` onto the current repo-native Clause 4 decomposition and lifecycle/callback tests. Rows already directly closed by the decomposition inherit `mapped` or `partial` from the decomposition status, while the still-open disconnect MOM observer slice remains explicitly `planned`.

`hla1516_1_clause_5_dm_detailed_reconciliation.csv` plays a similar bridge role for Declaration Management, but starts from the imported packet's finer-grained `SVC/SIG/ARG/PRE/EFF/EXC/MOM/TEST` service slices and maps them onto the repo's current tests and `mapped/partial/planned` status vocabulary.

`hla1516_1_dm_detailed_reconciliation.csv` is the whole-family companion bridge for imported IEEE 1516.1 Declaration Management master rows. It lifts the existing Clause 5 service reconciliation onto the imported family row kinds such as `seed`, `RTI_API`, `SIG`, `EFF`, `EXC_API`, and `MOM_TRACE`, and it also maps the callback-side `FED_CB`, `CB`, `CB_SIG`, `CB_ORDER`, `CB_ORD`, and `CB_PAYLOAD` rows onto the repo's current declaration callback and observer tests. That lets the full declaration-management family count directly in the whole-catalog harmonization index instead of remaining outside it.

`hla1516_1_clause_6_om_detailed_reconciliation.csv` applies that same packet-to-curated bridge pattern to Clause 6 Object Management, starting from the imported packet's `SEM/SVC/SIG/ARG/PRE/EFF/EXC/MOM` slices and explicitly marking where the current repo only covers a supported transport subset or still lacks direct MOM and callback-family evidence.

`hla1516_1_om_detailed_reconciliation.csv` is the whole-family companion bridge for imported IEEE 1516.1 Object Management master rows. It lifts the existing Clause 6 service reconciliation onto the imported family row kinds such as `seed`, `RTI_API`, `SIG`, `RET`, `EXC_API`, and `MOM_TRACE`, and it also maps the callback-side `FED_CB`, `CB`, `CB_SIG`, `CB_ORDER`, `CB_ORD`, and `CB_PAYLOAD` rows onto the repo's current discovery, reflect, interaction, deletion, transport-confirmation, and update-advisory tests. That lets the full object-management family count directly in the whole-catalog harmonization index instead of remaining outside it.

`hla1516_1_clause_7_own_detailed_reconciliation.csv` extends that packet-to-curated bridge pattern to Clause 7 Ownership Management, starting from the imported packet's `SVC/SIG/ARG/PRE/EFF/EXC/MOM/TEST` service slices plus callback `CB/CB_SIG/CB_PAYLOAD/CB_ORDER` rows and marking where current ownership coverage is direct, broader-than-current, or still missing static-signature and MOM observer evidence.

`hla1516_1_own_detailed_reconciliation.csv` is the whole-family companion bridge for imported IEEE 1516.1 Ownership Management master rows. It lifts the existing Clause 7 service reconciliation onto the imported family row kinds such as `seed`, `RTI_API`, `SIG`, `RET`, `EXC_API`, and `MOM_TRACE`, and it also maps the callback-side `FED_CB`, `CB`, `CB_SIG`, `CB_ORDER`, `CB_ORD`, and `CB_PAYLOAD` rows onto the repo's current ownership callback, query, and observer tests. That lets the full ownership family count directly in the whole-catalog harmonization index instead of remaining outside it.

`hla1516_1_clause_8_tm_detailed_reconciliation.csv` applies that same packet-to-curated bridge pattern to Clause 8 Time Management, starting from the imported packet's service `SVC/SIG/ARG/PRE/EFF/EXC/MOM/TEST` slices plus callback `CB/CB_SIG/CB_PAYLOAD/CB_ORDER` rows and marking where current time-management coverage is direct, broader-than-current, or still missing dedicated MOM observer evidence.

`hla1516_1_tm_detailed_reconciliation.csv` is the whole-family companion bridge for imported IEEE 1516.1 Time Management master rows. It lifts the existing Clause 8 service reconciliation onto the imported family row kinds such as `seed`, `RTI_API`, `SIG`, `RET`, `EXC_API`, and `MOM_TRACE`, and it also maps the callback-side `FED_CB`, `CB`, `CB_SIG`, `CB_ORDER`, `CB_ORD`, and `CB_PAYLOAD` rows onto the repo's current time-enable, grant, retraction, query, and observer tests. That lets the full time-management family count directly in the whole-catalog harmonization index instead of remaining outside it.

`hla1516_1_clause_9_ddm_detailed_reconciliation.csv` applies that same packet-to-curated bridge pattern to Clause 9 Data Distribution Management, starting from the imported packet's service `SVC/SIG/ARG/PRE/EFF/EXC/MOM/TEST` slices and marking where current region-lifecycle, region-subscription, and region-filtering coverage is direct, broader-than-current, or still missing dedicated MOM observer evidence.

`hla1516_1_ddm_detailed_reconciliation.csv` is the whole-family companion bridge for imported IEEE 1516.1 Data Distribution Management master rows. It lifts the existing Clause 9 service reconciliation onto the imported family row kinds such as `seed`, `RTI_API`, `SIG`, `RET`, `EXC_API`, and `MOM_TRACE`, and it also maps the DDM service-family rows onto the repo's current region-lifecycle, region-subscription, region-overlap, and observer tests. That lets the full DDM family count directly in the whole-catalog harmonization index instead of remaining outside it.

`hla1516_1_clause_10_sup_detailed_reconciliation.csv` applies that same packet-to-curated bridge pattern to Clause 10 Support Services, starting from the imported packet's service `SVC/SIG/ARG/PRE/EFF/EXC/MOM/TEST` slices and mapping them onto the repo's current lookup, metadata, normalization, advisory-switch, and callback-control tests while explicitly marking the still-unreconciled MOM observer slice.

`hla1516_1_clause_11_mom_detailed_reconciliation.csv` applies the packet-to-curated bridge pattern to Clause 11 Management Object Model requirements, using the packet's `OVW/OBJ/INT/RTI/SRV/TABLE` row kinds rather than service slices and mapping them onto the repo's current MOM catalog, observer, reporting, action, and runtime evidence while keeping the remaining design-rule-only nonrevision row distinct.

`hla1516_1_mom_detailed_reconciliation.csv` is the whole-family companion bridge for imported IEEE 1516.1 MOM/MIM master rows. It lifts the existing Clause 11 MOM reconciliation onto the whole master family, including the standard-MIM object, interaction, attribute, parameter, and datatype rows. Where the repo already compares the carried standard MIM against the active catalog exactly, those per-atom MIM rows are marked `mapped` rather than left as a family placeholder.

`hla1516_1_sup_detailed_reconciliation.csv` is the whole-family companion bridge for imported IEEE 1516.1 Support Services master rows. It lifts the existing Clause 10 support reconciliation onto the imported master row kinds such as `seed`, `RTI_API`, `SIG`, `RET`, `EXC_API`, and `MOM_TRACE`, so the support-family API surface, observer traces, and service-level verification rows count directly in the whole-catalog harmonization index instead of remaining outside it.

`hla1516_1_api_detailed_reconciliation.csv` applies the same bridge pattern to the imported IEEE 1516.1 API-binding rows. It covers the Clause 12/13 overview rows, the `211` packet-derived C++ ambassador method rows, the imported C++ class/catalog rows, and the imported WSDL operation rows. The bridge marks the generated ambassador method surface `mapped` where the repo's source-derived `raw_api` metadata and requirements-ledger tests directly preserve the standard binding signature surface, while keeping the header-token and WSDL catalog families `partial` because the repo carries them as validated imported artifacts rather than as live binding implementations.

`hla1516_1_conf_detailed_reconciliation.csv` is the companion bridge for the imported IEEE 1516.1 Clause 13 conformance-package rows. It does not claim full conformance closure. Instead, it records that the current repo's harmonization index, ambassador traceability, explicit requirement markers, packet verification, and verification-package artifacts partially support the broad federate and RTI conformance-package claims while leaving those clause-13 package assertions broader than current direct proof.

`hla1516_xml_detailed_reconciliation.csv` is the whole-family companion bridge for imported XML master rows. It maps the two XML seed rows and the normative OMT XSD clause row directly onto the repo's current Annex D/E parser and schema-validation evidence, while keeping the per-element and per-type XML schema atom rows `partial` to reflect that the repo currently validates XML conformance at the schema-family level rather than as one curated requirement per XML element or type.

`hla1516_2_omt_detailed_reconciliation.csv` is the whole-family companion bridge for imported IEEE 1516.2 OMT master rows. It lifts the current 1516.2 clause, parser, merge, lexicon, conformance-boundary, and annex evidence onto the imported OMT-family seeds and clause-detail rows. Rows with direct parser, merge, or fixture evidence are `mapped`, broad introductory and documentation-heavy rows are intentionally `partial`, and Annex B normalization remains explicitly `planned` because the repo still lacks a direct normalization requirement and executable witness.

`hla1516_2_omt_xml_detailed_reconciliation.csv` applies that same bridge pattern to the imported IEEE 1516.2 OMT/XML detailed packet. It maps the clause-level `omt_clause_detail` rows directly onto the current curated 1516.2 parser, merge, MIM, and schema-conformance requirements where the repo already has clause-specific evidence, while keeping the imported per-element and per-type `xsd_element_detail` and `xsd_type_detail` rows `partial` to reflect that the repo currently validates Annex D/E behavior at the schema-family and round-trip level rather than as one repo-native requirement per XSD atom.

`hla1516_framework_detailed_reconciliation.csv` is the framework-standard companion bridge for the imported IEEE 1516-2010 master rows outside Clause 12. It reconciles the packet's framework concepts, federation rules, rationale, and bibliography rows against the repo's seeded framework rules, cross-standard clause bridges, and source-policy documents, using `mapped` where the current evidence directly closes the imported rule and `partial` where the repo only proves a narrower executable subset of a broader architectural statement.

`hla_1516_master_harmonization_index_v1_0.csv` is the whole-catalog companion to the detailed bridge files. It starts from the imported `hla_1516_requirements_master_v1_0.csv` canonical packet and records, for every master requirement row, whether the current repo has a packet-to-curated detailed reconciliation for it yet. Rows already represented in a detailed bridge inherit that bridge's `mapped` or `partial` status; all remaining master rows are explicitly marked `unreconciled` with a source-file hint pointing at the current repo-native family ledger that would need the next harmonization pass.

`hla_1516_packet_hookup_status_v1_0.csv` is the companion bridge for the imported work packet itself. It does not restate clause requirements; it records which codebase-hookup tasks from the packet are already satisfied by the current repo shape, which are only partially satisfied by the current curated workflow, and which remain explicitly open.

The canonical hierarchy view for these sources lives in
[`docs/verification/requirements_hierarchy.md`](../docs/verification/requirements_hierarchy.md).
