# Verification

This family is the executable-and-artifact side of the docs tree.

Use it for anything that answers:

- what is implemented
- what is proven
- what is still partial
- what artifact records the proof

If you are entering from the top level, pair this page with:

1. [`../requirements/ieee-1516-2010/README.md`](../requirements/ieee-1516-2010/README.md) for the 2010 requirement/proof surface
2. [`../requirements/ieee-1516-2025/README.md`](../requirements/ieee-1516-2025/README.md) for the 2025 requirement/proof surface
3. [`requirements_verification_flow.md`](requirements_verification_flow.md) for the canonical rule that requirements must resolve through canonical rows, live evidence, and code rather than plan/worklist prose
4. [`../spec_reading_map.md`](../spec_reading_map.md)

## Canonical Order

Keep verification docs in this order:

1. requirements and clause matrices
2. traceability notes
3. executable test suites
4. generated evidence packets
5. comparison and attribution reports

## Primary Entry Points

- [../requirements/ieee-1516-2010/README.md](../requirements/ieee-1516-2010/README.md): 2010 requirement-facing front door
- [../requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md](../requirements/ieee-1516-2010/mixed_backend_priority_boundaries.md): canonical reading for the closed 2010 priority rows whose backend-resolution truth still differs by runtime
- [../requirements/ieee-1516-2010/federation_management_bounded_family.md](../requirements/ieee-1516-2010/federation_management_bounded_family.md): canonical reading for the maintained Clause 4 bounded reconciliation tail after owner-summary closeout
- [../requirements/ieee-1516-2010/declaration_management_bounded_family.md](../requirements/ieee-1516-2010/declaration_management_bounded_family.md): canonical reading for the maintained Clause 5 bounded reconciliation tail after owner-summary closeout
- [../requirements/ieee-1516-2010/object_management_bounded_family.md](../requirements/ieee-1516-2010/object_management_bounded_family.md): canonical reading for the maintained Clause 6 bounded reconciliation tail after owner-summary closeout
- [../requirements/ieee-1516-2010/ownership_management_bounded_family.md](../requirements/ieee-1516-2010/ownership_management_bounded_family.md): canonical reading for the maintained Clause 7 bounded reconciliation tail after owner-summary closeout
- [../requirements/ieee-1516-2010/time_management_bounded_family.md](../requirements/ieee-1516-2010/time_management_bounded_family.md): canonical reading for the maintained Clause 8 bounded reconciliation tail after owner-summary closeout
- [../requirements/ieee-1516-2010/data_distribution_management_bounded_family.md](../requirements/ieee-1516-2010/data_distribution_management_bounded_family.md): canonical reading for the maintained Clause 9 bounded reconciliation tail after owner-summary closeout
- [../requirements/ieee-1516-2010/omt_xml_bounded_family.md](../requirements/ieee-1516-2010/omt_xml_bounded_family.md): canonical reading for the maintained 1516.2 XML atom and Annex B normalization bounded tail
- [../requirements/ieee-1516-2010/api_binding_bounded_family.md](../requirements/ieee-1516-2010/api_binding_bounded_family.md): canonical reading for the maintained 2010 API-binding residual family after splitting mapped method surface from imported binding-catalog tails
- [../requirements/ieee-1516-2010/clause13_conformance_closeout.md](../requirements/ieee-1516-2010/clause13_conformance_closeout.md): canonical reading for the fully mapped 2010 Clause 13 conformance owner surface without overclaiming external certification
- [../requirements/ieee-1516-2010/support_services_bounded_family.md](../requirements/ieee-1516-2010/support_services_bounded_family.md): canonical reading for the maintained Clause 10 bounded reconciliation tail after owner-summary closeout
- [../requirements/ieee-1516-2025/README.md](../requirements/ieee-1516-2025/README.md): 2025 requirements-facing claim map and bounded proof-note index
- [../../requirements/2010/canonical_requirements.json](../../requirements/2010/canonical_requirements.json): canonical 2010 row-level requirement truth
- [../../requirements/2010/backend_resolution.json](../../requirements/2010/backend_resolution.json): canonical 2010 backend-resolution truth
- [../../requirements/2025/canonical_requirements.json](../../requirements/2025/canonical_requirements.json): canonical 2025 row-level requirement truth
- [../../requirements/2025/backend_resolution.json](../../requirements/2025/backend_resolution.json): canonical 2025 backend- and route-resolution truth
- [shard_registry.md](shard_registry.md): canonical runnable shard registry and repo-green gating map
- [view_registry.md](view_registry.md): canonical focused-target and overlapping audit-view registry
- [requirements_verification_flow.md](requirements_verification_flow.md): canonical rule for requirements -> live evidence -> code flow, and the ban on using plan/worklist prose as a requirement truth source
- [../../requirements/README.md](../../requirements/README.md): edition index for the source-side requirement surfaces
- [requirements_structure_packet.md](requirements_structure_packet.md): current packet explaining the requirements layout, bridge strategy, and pinned harmonization state
- [requirements_hierarchy.md](requirements_hierarchy.md): L1/L2/L3 capability-feature-requirement hierarchy with test anchors
- [callback_model_compliance.md](callback_model_compliance.md): callback delivery behavior, compliance boundary, and test evidence
- [time_model_compliance.md](time_model_compliance.md): GALT, LITS, lookahead, and time-advance compliance proof
- [../requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md](../requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md): explicit 2025 non-claim map for legacy aliases, Java/C++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope OMT extension semantics
- [imported_packet_requirements_v1_0/README.md](imported_packet_requirements_v1_0/README.md): generated packet-style markdown views from the imported canonical v1.0 requirements catalog
- [clause13_conformance_packet.md](clause13_conformance_packet.md): generated federate/RTI Clause 13 conformance packet
- [clause13_conformance_packet.json](clause13_conformance_packet.json): machine-readable Clause 13 conformance packet
- [verification_validation_split.md](verification_validation_split.md): canonical split between standards verification and operational validation
- [verification_plan.md](verification_plan.md): layered conformance plan
- [validation_plan.md](validation_plan.md): layered operational validation plan
- [../backend_route_inventory.md](../backend_route_inventory.md): runtime and transport route inventory
- [../backend_capability_matrix.md](../backend_capability_matrix.md): feature coverage by backend
- [../backend_conformance_matrix.md](../backend_conformance_matrix.md): clause-level conformance matrix
- [requirement_compliance_exports.md](requirement_compliance_exports.md): manager-facing CSV/XLSX export contract for the 2010 and 2025 backend-compliance packets
- [../certi_spec_traceability.md](../../packages/hla-backend-certi/docs/certi_spec_traceability.md): CERTI clause traceability
- [../local_verification.md](../local_verification.md): local verification workflow
- [../source_documents.md](../source_documents.md): source provenance and reference map
- [../evidence/README.md](../evidence/README.md): promoted evidence packets
- [../specs/README.md](../specs/README.md): planned spec/evidence artifact family
- [run_sequence.md](run_sequence.md): documented full verification sequence
- `python3 scripts/generate_requirement_compliance_spreadsheets.py`: generate boss-facing CSV/XLSX packets for `2010 / 1516e` and `2025 / 1516_2025` from the canonical requirement and backend-resolution artifacts

## Front-Door Decision Table

Use this when someone asks "where do I start?" and the answer depends on
whether they need claim ownership, runnable proof, or presentation output.

| If the need is... | Start here | Then read |
| --- | --- | --- |
| understand the canonical 2010 requirement owner | [../requirements/ieee-1516-2010/README.md](../requirements/ieee-1516-2010/README.md) | [../spec_reading_map.md](../spec_reading_map.md), [../test_surface.md](../test_surface.md) |
| understand the canonical 2025 requirement owner | [../requirements/ieee-1516-2025/README.md](../requirements/ieee-1516-2025/README.md) | [../spec_reading_map.md](../spec_reading_map.md), [../test_surface.md](../test_surface.md) |
| inspect exact canonical 2025 row status and owner doc | [../../requirements/2025/canonical_requirements.json](../../requirements/2025/canonical_requirements.json) | [../requirements/ieee-1516-2025/README.md](../requirements/ieee-1516-2025/README.md), [requirements_verification_flow.md](requirements_verification_flow.md) |
| inspect backend or route divergence for a 2025 row | [../../requirements/2025/backend_resolution.json](../../requirements/2025/backend_resolution.json) | [../requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md](../requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md), [../requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md](../requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md) |
| pick a shard or rerun lane | [../test_surface.md](../test_surface.md) | [../local_verification_commands.md](../local_verification_commands.md), [../junior_test_diagnosis_runbook.md](../junior_test_diagnosis_runbook.md) |
| understand canonical shard ownership or repo-green gating | [shard_registry.md](shard_registry.md) | [../test_surface.md](../test_surface.md), [view_registry.md](view_registry.md) |
| understand overlapping focused reruns or audit slices | [view_registry.md](view_registry.md) | [shard_registry.md](shard_registry.md), [../test_surface.md](../test_surface.md) |
| rerun execution-membership guards without guessing files | [../test_surface.md](../test_surface.md) | [view_registry.md](view_registry.md), [../junior_test_diagnosis_runbook.md](../junior_test_diagnosis_runbook.md); current hosted 2025 proof here is the gRPC/FedPro route slice plus the REST-hosted Python route |
| understand route or backend support instead of canonical status | [../spec_reading_map.md](../spec_reading_map.md) | [../requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md](../requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md), [../requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md](../requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md) |
| answer "are we actually done?" honestly | [../../requirements/2025/canonical_requirements.json](../../requirements/2025/canonical_requirements.json) | [../../requirements/2025/backend_resolution.json](../../requirements/2025/backend_resolution.json), [requirements_verification_flow.md](requirements_verification_flow.md), [../spec_reading_map.md](../spec_reading_map.md) |
| hand a manager a spreadsheet packet | [requirement_compliance_exports.md](requirement_compliance_exports.md) | [../plans/requirements_completion_audit.md](../plans/requirements_completion_audit.md), [../requirements/ieee-1516-2010/README.md](../requirements/ieee-1516-2010/README.md), [../requirements/ieee-1516-2025/README.md](../requirements/ieee-1516-2025/README.md) |

## Simple Reading Rule

Use this flow:

1. open the requirements-facing README when you need the claim or boundary
2. open this verification index when you need the proof artifact family
3. open the focused proof or comparison document only after the first two

## Planning Is Downstream

Planning and sequencing docs remain useful, but they are not requirement truth
surfaces and should not sit in the primary verification chain.

- use `docs/plans/*` for sequencing, staffing, or closure tracking only
- use `requirements_completion_audit.md` or other closeout docs as downstream
  reporting over canonical requirement rows
- do not use worklists, finish-line packets, or plan prose as substitutes for
  `canonical_requirements.json`, `backend_resolution.json`, owner docs, shards,
  or executable evidence

## Shard And View Rule

Use the same ownership model described in
[`../plans/requirements_remaining_closure.md`](../plans/requirements_remaining_closure.md):

- `shards` own executable pass/fail proof
- `views` are overlapping audit cuts that may collect evidence from multiple shards
- verification artifacts should name the primary owning shard when they change a requirement status
- views may help reading and closeout, but they must not replace canonical shard ownership

When a requirement bucket changes state, the expected flow is:

1. update the source-side canonical requirement row or backend-resolution row
2. record the bounded claim or exclusion note in the owning proof document
3. point at the narrowest shard or command that actually proved the change
4. widen to broader lanes only when the requirement claim crosses that boundary

## Status Rule

Do not overload one field to mean both:

- the canonical requirement status
- which backend currently supports that requirement

Use the canonical owner row for the requirement-level status, and keep backend
resolution in separate columns or linked evidence artifacts.

For the current 2025 surface, the concrete audit rule is:

- canonical `covered` rows should carry direct `tests/` or `packages/`
  evidence in `requirements/2025/canonical_requirements.json`
- grouped backend rows, vendor grouped rows, and other backend-resolution
  companions may instead point at the canonical catalog, owner docs, and
  bounded route artifacts because they summarize backend truth rather than
  replace canonical requirement closure

Good shape:

- canonical status: `partial`
- backend resolution: `python=verified`, `pitch=vendor-divergent`, `certi=verified`

Bad shape:

- one overloaded `status` cell trying to imply both the requirement judgment and
  the backend-by-backend support story

Pair this page with:

- [`../test_surface.md`](../test_surface.md) for shard and view terminology
- [`shard_registry.md`](shard_registry.md) for canonical runnable ownership
- [`view_registry.md`](view_registry.md) for overlapping focused-target and audit-view ownership
- [`../local_verification_commands.md`](../local_verification_commands.md) for end-to-end lane commands and restart paths
- [`../junior_test_diagnosis_runbook.md`](../junior_test_diagnosis_runbook.md) for failure triage and rerun flow
- [`../requirements/ieee-1516-2010/README.md`](../requirements/ieee-1516-2010/README.md) for the 2010 front door
- [`../requirements/ieee-1516-2025/README.md`](../requirements/ieee-1516-2025/README.md) for the 2025 front door

## What Belongs Here

- requirements ledgers
- requirement source registries
- service matrices
- spec traceability tables
- verification planning
- validation planning
- compliance packets
- generated analysis artifacts
- scenario comparison reports

## What Does Not Belong Here

- operator install instructions
- package layout rules
- backend implementation details
- ad hoc notes that do not feed verification output

That separation keeps the docs tree easy to scan for juniors:

- `README.md` tells you how to run the repo
- `docs/README.md` tells you where the docs live
- `docs/verification/README.md` tells you where the proof lives
