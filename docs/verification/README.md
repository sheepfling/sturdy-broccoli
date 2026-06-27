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
3. [`../plans/requirements_completion_audit.md`](../plans/requirements_completion_audit.md) for the current honest answer to what still blocks full closeout
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
- [../requirements/ieee-1516-2010/federation_management_bounded_family.md](../requirements/ieee-1516-2010/federation_management_bounded_family.md): canonical reading for the remaining bounded Clause 4 federation-management partial-family tail
- [../requirements/ieee-1516-2010/declaration_management_bounded_family.md](../requirements/ieee-1516-2010/declaration_management_bounded_family.md): canonical reading for the remaining bounded Clause 5 declaration-management partial-family tail
- [../requirements/ieee-1516-2010/object_management_bounded_family.md](../requirements/ieee-1516-2010/object_management_bounded_family.md): canonical reading for the remaining bounded Clause 6 object-management partial-family tail
- [../requirements/ieee-1516-2010/ownership_management_bounded_family.md](../requirements/ieee-1516-2010/ownership_management_bounded_family.md): canonical reading for the remaining bounded Clause 7 ownership-management partial-family tail
- [../requirements/ieee-1516-2010/time_management_bounded_family.md](../requirements/ieee-1516-2010/time_management_bounded_family.md): canonical reading for the remaining bounded Clause 8 time-management partial-family tail
- [../requirements/ieee-1516-2010/data_distribution_management_bounded_family.md](../requirements/ieee-1516-2010/data_distribution_management_bounded_family.md): canonical reading for the remaining bounded Clause 9 data-distribution-management partial-family tail
- [../requirements/ieee-1516-2010/omt_xml_bounded_family.md](../requirements/ieee-1516-2010/omt_xml_bounded_family.md): canonical reading for the remaining bounded 1516.2 XML atom and Annex B normalization partial-family tail
- [../requirements/ieee-1516-2010/support_services_bounded_family.md](../requirements/ieee-1516-2010/support_services_bounded_family.md): canonical reading for the remaining bounded Clause 10 support-services partial-family tail
- [../plans/2010_python_rti_bounded_family_execution_worklist.md](../plans/2010_python_rti_bounded_family_execution_worklist.md): execution companion for the remaining bounded 2010 mixed-backend and partial-family surfaces
- [../requirements/ieee-1516-2025/README.md](../requirements/ieee-1516-2025/README.md): 2025 requirements-facing claim map and bounded proof-note index
- [../plans/PLN-004_python_rti_100_percent_compliance_plan.md](../plans/PLN-004_python_rti_100_percent_compliance_plan.md): program-level rule for an honest 2025-then-2010 Python RTI closeout
- [../plans/2025_python_rti_100_percent_worklist.md](../plans/2025_python_rti_100_percent_worklist.md): exact 2025 non-covered row inventory, denominator rule, and promotion criteria for literal `691 / 691 covered`
- [shard_registry.md](shard_registry.md): canonical runnable shard registry and repo-green gating map
- [view_registry.md](view_registry.md): canonical focused-target and overlapping audit-view registry
- [../plans/requirements_completion_audit.md](../plans/requirements_completion_audit.md): current-state audit of what still blocks an honest full requirements-complete claim
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
- `python3 scripts/generate_requirement_compliance_spreadsheets.py`: generate boss-facing CSV/XLSX packets for `2010 / 1516e` and `2025 / 1516_2025` from the canonical requirement and harmonization artifacts

## Front-Door Decision Table

Use this when someone asks "where do I start?" and the answer depends on
whether they need claim ownership, runnable proof, or presentation output.

| If the need is... | Start here | Then read |
| --- | --- | --- |
| understand the canonical 2010 requirement owner | [../requirements/ieee-1516-2010/README.md](../requirements/ieee-1516-2010/README.md) | [../spec_reading_map.md](../spec_reading_map.md), [../test_surface.md](../test_surface.md) |
| understand how the remaining 2010 bounded families would stay bounded or tighten into narrower direct proof | [../plans/2010_python_rti_bounded_family_execution_worklist.md](../plans/2010_python_rti_bounded_family_execution_worklist.md) | [../requirements/ieee-1516-2010/README.md](../requirements/ieee-1516-2010/README.md), [shard_registry.md](shard_registry.md) |
| understand the canonical 2025 requirement owner | [../requirements/ieee-1516-2025/README.md](../requirements/ieee-1516-2025/README.md) | [../spec_reading_map.md](../spec_reading_map.md), [../test_surface.md](../test_surface.md) |
| understand what still blocks an honest `100%` outcome for the `2025` Python RTI lane | [../plans/2025_python_rti_100_percent_worklist.md](../plans/2025_python_rti_100_percent_worklist.md) | [../plans/PLN-004_python_rti_100_percent_compliance_plan.md](../plans/PLN-004_python_rti_100_percent_compliance_plan.md), [../requirements/ieee-1516-2025/README.md](../requirements/ieee-1516-2025/README.md) |
| pick a shard or rerun lane | [../test_surface.md](../test_surface.md) | [../local_verification_commands.md](../local_verification_commands.md), [../junior_test_diagnosis_runbook.md](../junior_test_diagnosis_runbook.md) |
| understand canonical shard ownership or repo-green gating | [shard_registry.md](shard_registry.md) | [../test_surface.md](../test_surface.md), [view_registry.md](view_registry.md) |
| understand overlapping focused reruns or audit slices | [view_registry.md](view_registry.md) | [shard_registry.md](shard_registry.md), [../test_surface.md](../test_surface.md) |
| rerun execution-membership guards without guessing files | [../test_surface.md](../test_surface.md) | [view_registry.md](view_registry.md), [../junior_test_diagnosis_runbook.md](../junior_test_diagnosis_runbook.md); current hosted 2025 proof here is the gRPC/FedPro route slice plus the REST-hosted Python route |
| understand route or backend support instead of canonical status | [../spec_reading_map.md](../spec_reading_map.md) | [../requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md](../requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md), [../requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md](../requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md) |
| answer "are we actually done?" honestly | [../plans/requirements_completion_audit.md](../plans/requirements_completion_audit.md) | [../plans/requirements_remaining_closure.md](../plans/requirements_remaining_closure.md), [../spec_reading_map.md](../spec_reading_map.md) |
| hand a manager a spreadsheet packet | [requirement_compliance_exports.md](requirement_compliance_exports.md) | [../plans/requirements_completion_audit.md](../plans/requirements_completion_audit.md), [../requirements/ieee-1516-2010/README.md](../requirements/ieee-1516-2010/README.md), [../requirements/ieee-1516-2025/README.md](../requirements/ieee-1516-2025/README.md) |

## Simple Reading Rule

Use this flow:

1. open the requirements-facing README when you need the claim or boundary
2. open this verification index when you need the proof artifact family
3. open the focused proof or comparison document only after the first two

## Shard And View Rule

Use the same ownership model described in
[`../plans/requirements_remaining_closure.md`](../plans/requirements_remaining_closure.md):

- `shards` own executable pass/fail proof
- `views` are overlapping audit cuts that may collect evidence from multiple shards
- verification artifacts should name the primary owning shard when they change a requirement status
- views may help reading and closeout, but they must not replace canonical shard ownership

When a requirement bucket changes state, the expected flow is:

1. update the source-side requirement row or harmonization ledger
2. record the bounded claim or exclusion note in the owning proof document
3. point at the narrowest shard or command that actually proved the change
4. widen to broader lanes only when the requirement claim crosses that boundary

## Status Rule

Do not overload one field to mean both:

- the canonical requirement status
- which backend currently supports that requirement

Use the canonical owner row for the requirement-level status, and keep backend
resolution in separate columns or linked evidence artifacts.

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
