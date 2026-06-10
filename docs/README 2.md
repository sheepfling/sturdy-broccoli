# Docs

Project documentation for the IEEE 1516-2010-focused workspace.

This tree uses one simple parallel pattern:

`family -> mechanism -> evidence`

Start here:

- [documentation_hierarchy.md](documentation_hierarchy.md): canonical doc flow and hierarchy
- [workspace_layout.md](workspace_layout.md): top-level workspace areas and ownership split
- [package_dependency_tree.md](package_dependency_tree.md): machine-derived installable package dependency tree
- [../README.md](../README.md): install, bootstrap, smoke, and operator commands
- [first_run.md](first_run.md): shortest path from fresh checkout to a working pure-Python example
- [python_environment.md](python_environment.md): Python bootstrap, `.venv`, extras, and install order
- [top_to_bottom_green.md](top_to_bottom_green.md): explicit repo-wide finish definition for base Python, repo-green, and vendor-green
- [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md): supported unsandboxed-local and dedicated-runner path for real CERTI/Pitch runtimes
- [vendor_runner_provisioning.md](vendor_runner_provisioning.md): dedicated runner variables, marker paths, and provisioning checklist
- [vendor_runner_provisioning_template.yaml](vendor_runner_provisioning_template.yaml): machine-readable dedicated runner provisioning template
- [install_matrix.md](install_matrix.md): extras, backend families, and dependency order
- [agent_runbook.md](agent_runbook.md): start-here sequence for agents and automation
- [python_api_spec.md](python_api_spec.md): clean Python spec package
- [callback_model_guide.md](callback_model_guide.md): evoked vs immediate callback behavior, tests, and implementation entry points
- [import_boundary_rules.md](import_boundary_rules.md): package-family import rules and transport-versus-backend boundaries
- [verification/run_sequence.md](verification/run_sequence.md): full verification sequence and run order
- [two_federate_quickstart.md](two_federate_quickstart.md): first stop for the composite two-federate example

Doc families:

- `reference/`: source acquisition notes and retained archive copies
- `evidence/`: unpacked verification packets and imported analysis artifacts
- `specs/`: clause indexes, matrices, and evidence-ledger artifacts
- `verification/`: requirements, traceability, proof, and comparison artifacts
- `plans/`: roadmap items and implementation sequencing

Backend and runtime docs:

- [backend_route_inventory.md](backend_route_inventory.md): exhaustive runtime families, bridge routes, transport routes, named baselines, and evidence anchors
- [backend_route_inventory_routes.md](backend_route_inventory_routes.md): backend route table
- [backend_route_inventory_baselines.md](backend_route_inventory_baselines.md): CERTI baseline attribution
- [backend_route_inventory_remote.md](backend_route_inventory_remote.md): remote transport routes
- [backend_route_inventory_commands.md](backend_route_inventory_commands.md): backend route commands
- [backend_compliance_discovery.md](backend_compliance_discovery.md): shortest path to enumerating backend/spec compliance from generated artifacts
- [rti_options_and_test_matrix.md](rti_options_and_test_matrix.md): operator-facing runtime and test matrix
- [backend_capability_matrix.md](backend_capability_matrix.md): backend feature coverage
- [backend_conformance_matrix.md](backend_conformance_matrix.md): clause-level conformance and parity status
- [vendor_runtime_gap_map.md](vendor_runtime_gap_map.md): promoted slices, blocked prerequisites, and remaining vendor/runtime gaps
- [../packages/hla2010-rti-certi/docs/certi_spec_traceability.md](../packages/hla2010-rti-certi/docs/certi_spec_traceability.md): real CERTI sync/ownership coverage
- [../packages/hla2010-rti-certi/docs/certi_runtime_limitations.md](../packages/hla2010-rti-certi/docs/certi_runtime_limitations.md): patched-vs-upstream CERTI baseline policy and runtime shortfalls
- [../packages/hla2010-rti-certi/docs/certi_negotiated_ownership_findings.md](../packages/hla2010-rti-certi/docs/certi_negotiated_ownership_findings.md): CERTI negotiated ownership investigation
- [../packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md](../packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md): Pitch runtime selection and troubleshooting
- [../packages/hla2010-rti-pitch-common/docs/pitch_docker_quickstart.md](../packages/hla2010-rti-pitch-common/docs/pitch_docker_quickstart.md): shortest Pitch operator path
- [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md): repo-green versus vendor-green runner contract
- [vendor_runner_provisioning.md](vendor_runner_provisioning.md): dedicated runner provisioning spec and CI variable checklist
- [vendor_runner_provisioning_template.yaml](vendor_runner_provisioning_template.yaml): machine-readable runner provisioning template
- [vendor_parity_artifacts.md](vendor_parity_artifacts.md): harmonized vendor artifact packet
- [../packages/hla2010-rti-certi/docs/certi_section8_runbook.md](../packages/hla2010-rti-certi/docs/certi_section8_runbook.md): CERTI operator runbook

Verification and provenance:

- [source_documents.md](source_documents.md): retained source references and provenance
- [source_documents_inventory.md](source_documents_inventory.md): source inventory
- [source_documents_policy.md](source_documents_policy.md): source policy and extraction notes
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
- [verification/run_sequence.md](verification/run_sequence.md): full verification sequence and run order
- [supported_subset_policy.md](supported_subset_policy.md): explicit broad-spec versus supported-subset policy statements for defended partial compliance rows

Planning:

- [plans/README.md](plans/README.md): plan index
- [plans/imported_requirements_backlog_v1_0.md](plans/imported_requirements_backlog_v1_0.md): generated requirement-driven implementation queues
- [plans/requirements_finish_line.md](plans/requirements_finish_line.md): handoff note for finishing remaining requirement rows without overclaiming
- [development_next_steps.md](development_next_steps.md): current next-step backlog
- [inbox_inventory_2026-06-05.md](inbox_inventory_2026-06-05.md): source-drop promotion out of `INBOX`
