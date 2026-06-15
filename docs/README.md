# Docs

Project documentation for the IEEE 1516-2010 (2010 edition)-focused workspace.

This tree uses one simple pattern:

`start here -> reference -> historical/provenance`

Use this page as the documentation index, not as a second front-door README.

If you only need the shortest path:

1. read [`../README.md`](../README.md)
2. read [`onboarding.md`](onboarding.md)
3. read [`first_run.md`](first_run.md)
4. read [`package_layout.md`](package_layout.md)
5. read [`../packages/README.md`](../packages/README.md)

## Start Here

Primary entrypoints:

- [../README.md](../README.md): repo purpose, bootstrap, first commands, and operator entrypoints
- [onboarding.md](onboarding.md): canonical ordered run/edit/scaffold/trace path
- [first_run.md](first_run.md): shortest path from fresh checkout to one working pure-Python example
- [package_layout.md](package_layout.md): canonical package hierarchy and family roles
- [package_hierarchy_and_versioning.md](package_hierarchy_and_versioning.md): quick package dependency tree and current versioning model
- [../packages/README.md](../packages/README.md): package ownership cards and where to edit first
- [python_environment.md](python_environment.md): bootstrap, `.venv`, extras, and install order
- [test_surface.md](test_surface.md): canonical verification lanes and discovery flow

Concrete contributor lanes:

- [python_rti_edit_one_service.md](python_rti_edit_one_service.md): edit one Python RTI service
- [create_federate_and_fom.md](create_federate_and_fom.md): create one package-backed FOM and federate
- [requirements_trace_one_method.md](requirements_trace_one_method.md): trace one method from requirement row to code and proof

Focused reading maps and setup notes:

- [spec_reading_map.md](spec_reading_map.md): smallest practical reading path for the abstract/public spec surface
- [fom_reading_map.md](fom_reading_map.md): smallest practical reading path for FOM parsing and merge behavior
- [python_rti_reading_map.md](python_rti_reading_map.md): smallest practical reading path for Python RTI edits
- [python_rti_backend.md](python_rti_backend.md): broader Python RTI backend map
- [rti_factory_reading_map.md](rti_factory_reading_map.md): installed RTI factory listing, selection, and introspection
- [two_federate_quickstart.md](two_federate_quickstart.md): first stop for the composite two-federate example
- [networked_rti_python.md](networked_rti_python.md): hosted Python RTI over gRPC
- [install_matrix.md](install_matrix.md): extras, backend families, and dependency order
- [agent_runbook.md](agent_runbook.md): start-here sequence for agents and automation
- [requirements_edit_one_row.md](requirements_edit_one_row.md): use only when the traced active row itself is wrong
- [requirements_traceability.md](requirements_traceability.md): broader requirement -> implementation -> test -> artifact model
- [requirements_authoring_map.md](requirements_authoring_map.md): secondary ordered reading path for broader traceability maintenance
- [codex_runner_authorization.md](codex_runner_authorization.md): draft loopback-socket authorization request for Codex verification sessions

## Package And Architecture

Use these together:

- [package_layout.md](package_layout.md): human-readable package hierarchy
- [package_hierarchy_and_versioning.md](package_hierarchy_and_versioning.md): quick hierarchy tree and lockstep-versus-independent versioning status
- [../packages/README.md](../packages/README.md): package ownership cards
- [package_dependency_tree.md](package_dependency_tree.md): generated dependency evidence
- [import_boundary_rules.md](import_boundary_rules.md): allowed dependency directions
- [workspace_layout.md](workspace_layout.md): top-level workspace areas and ownership split

## Reference

- [documentation_hierarchy.md](documentation_hierarchy.md): canonical doc flow and hierarchy
- [python_api_spec.md](python_api_spec.md): clean Python spec package and runtime facade split
- [callback_model_guide.md](callback_model_guide.md): evoked vs immediate callback behavior, tests, and implementation entry points
- [verification/run_sequence.md](verification/run_sequence.md): full verification sequence and run order
- [top_to_bottom_green.md](top_to_bottom_green.md): explicit repo-wide finish definition for base Python, repo-green, and vendor-green

Backend and runtime docs:

- [backend_route_inventory.md](backend_route_inventory.md): exhaustive runtime families, bridge routes, transport routes, named baselines, and evidence anchors
- [backend_compliance_discovery.md](backend_compliance_discovery.md): shortest path to enumerating backend/spec compliance from generated artifacts
- [rti_options_and_test_matrix.md](rti_options_and_test_matrix.md): operator-facing runtime and test matrix
- [backend_capability_matrix.md](backend_capability_matrix.md): backend feature coverage
- [backend_conformance_matrix.md](backend_conformance_matrix.md): clause-level conformance and parity status
- [vendor_runtime_gap_map.md](vendor_runtime_gap_map.md): promoted slices, blocked prerequisites, and remaining vendor/runtime gaps
- [backend_route_inventory_routes.md](backend_route_inventory_routes.md): backend route table
- [backend_route_inventory_baselines.md](backend_route_inventory_baselines.md): CERTI baseline attribution
- [backend_route_inventory_remote.md](backend_route_inventory_remote.md): remote transport routes
- [backend_route_inventory_commands.md](backend_route_inventory_commands.md): backend route commands
- [../packages/hla2010-rti-certi/docs/certi_spec_traceability.md](../packages/hla2010-rti-certi/docs/certi_spec_traceability.md): real CERTI sync/ownership coverage
- [../packages/hla2010-rti-certi/docs/certi_runtime_limitations.md](../packages/hla2010-rti-certi/docs/certi_runtime_limitations.md): patched-vs-upstream CERTI baseline policy and runtime shortfalls
- [../packages/hla2010-rti-certi/docs/certi_negotiated_ownership_findings.md](../packages/hla2010-rti-certi/docs/certi_negotiated_ownership_findings.md): CERTI negotiated ownership investigation
- [../packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md](../packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md): Pitch runtime selection and troubleshooting
- [../packages/hla2010-rti-pitch-common/docs/pitch_docker_quickstart.md](../packages/hla2010-rti-pitch-common/docs/pitch_docker_quickstart.md): shortest Pitch operator path
- [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md): repo-green versus vendor-green runner contract
- [vendor_runner_provisioning.md](vendor_runner_provisioning.md): dedicated runner provisioning spec and CI variable checklist
- [vendor_runner_provisioning_template.yaml](vendor_runner_provisioning_template.yaml): machine-readable runner provisioning template
- [codex_runner_authorization.md](codex_runner_authorization.md): draft Codex sandbox and runner authorization contract for hosted transport checks
- [preflight_artifacts.md](preflight_artifacts.md): JSON artifact contract for CERTI and Pitch preflight wrappers
- [vendor_parity_artifacts.md](vendor_parity_artifacts.md): harmonized vendor artifact packet
- [../packages/hla2010-rti-certi/docs/certi_section8_runbook.md](../packages/hla2010-rti-certi/docs/certi_section8_runbook.md): CERTI operator runbook
- [compliance/hla1516_2010_time_management_matrix.md](compliance/hla1516_2010_time_management_matrix.md): generated time-management clause matrix
- [compliance/time_management_known_limits.md](compliance/time_management_known_limits.md): generated known-limits companion for the time matrix

## Historical / Provenance

These pages are for audit, source provenance, retained packet contents, and
historical evidence. They are not the primary onboarding path.

- [source_documents.md](source_documents.md): retained source references and provenance
- [source_documents_inventory.md](source_documents_inventory.md): source inventory
- [source_documents_policy.md](source_documents_policy.md): source policy and extraction notes
- [local_verification_notes.md](local_verification_notes.md): machine-local caveats and operator notes from the latest successful verification run
- [repo_seed_scope.md](repo_seed_scope.md): original repo-seed scope and retained seeding constraints
- [reference/README.md](reference/README.md): reference family index
- [reference/source_index.md](reference/source_index.md): reference source index
- [reference/archive_index.md](reference/archive_index.md): reference archive index
- [specs/README.md](specs/README.md): spec-index family and parallel artifact order
- [evidence/README.md](evidence/README.md): unpacked verification packets
- [evidence/packet_index.md](evidence/packet_index.md): unpacked packet index
- [verification/README.md](verification/README.md): verification family index
- [verification/requirements_hierarchy.md](verification/requirements_hierarchy.md): requirements capability-feature-requirement hierarchy
- [verification/callback_model_compliance.md](verification/callback_model_compliance.md): callback delivery behavior, compliance boundary, and proof anchors
- [verification/time_model_compliance.md](verification/time_model_compliance.md): GALT, LITS, lookahead, and time-advance compliance proof
- [verification/verification_validation_split.md](verification/verification_validation_split.md): verification vs validation split
- [verification/verification_plan.md](verification/verification_plan.md): layered verification plan
- [verification/validation_plan.md](verification/validation_plan.md): layered validation plan
- [supported_subset_policy.md](supported_subset_policy.md): explicit broad-spec versus supported-subset policy statements for defended partial compliance rows

Planning:

- [plans/README.md](plans/README.md): plan index
- [plans/human_editability_reassessment_2026_06.md](plans/human_editability_reassessment_2026_06.md): current assessment of remaining human editability pain points after the guardrail work
- [plans/imported_requirements_backlog_v1_0.md](plans/imported_requirements_backlog_v1_0.md): generated requirement-driven implementation queues
- [plans/requirements_finish_line.md](plans/requirements_finish_line.md): handoff note for finishing remaining requirement rows without overclaiming
- [plans/human_editability_smell_inventory.md](plans/human_editability_smell_inventory.md): smell inventory and closure targets for the human-editability tranche
- [plans/hla2010_spec_source_root_migration.md](plans/hla2010_spec_source_root_migration.md): source-root migration note for the spec package
- [development_next_steps.md](development_next_steps.md): current next-step backlog
- [inbox_inventory_2026-06-05.md](inbox_inventory_2026-06-05.md): source-drop promotion out of `INBOX`

## Read Next

1. [onboarding.md](onboarding.md)
2. [first_run.md](first_run.md)
3. [python_rti_edit_one_service.md](python_rti_edit_one_service.md)
4. [create_federate_and_fom.md](create_federate_and_fom.md)
5. [requirements_trace_one_method.md](requirements_trace_one_method.md)
