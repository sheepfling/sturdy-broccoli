# Docs

Project documentation for the Python-first IEEE HLA 1516.1-2010 and
1516.1-2025 workspace.

This tree uses one simple parallel pattern:

`start here -> reference -> historical/provenance`

If you only need the shortest on-ramp:

1. read [`../README.md`](../README.md)
2. read [`onboarding.md`](onboarding.md)
3. read [`first_run.md`](first_run.md) for the 2010 pure-Python bootstrap lane
4. read [`python_rti_backend.md`](python_rti_backend.md) for the main 2025 Python RTI lane in `hla-backend-python2025`
5. use `./tools/python verify-main-2025` as the normal direct `python2025` proof lane
6. read [`networked_rti_python.md`](networked_rti_python.md) only if you need the bounded hosted 2025 route or its parity/hygiene lane
7. use `./tools/python verify-routes-2025` when you need the bounded hosted `python-2025-fedpro-grpc` hygiene lane
8. run `python3 scripts/run_spec2025_finish_line.py` when you need to refresh the checked-in 2025 finish-line and route-parity artifacts after proof-lane changes
9. read [`verification/time_model_compliance.md`](verification/time_model_compliance.md) when the question is time, lookahead, GALT/LITS, or save/restore window proof
10. read [`package_layout.md`](package_layout.md) if you need the package hierarchy first

For 2025 work, keep the ownership rule simple:

- `hla-backend-python2025` is the implementation lane
- `hla-backend-shim` is wrapper-only compatibility code
- `verify-main-2025` is the default proof path
- `verify-routes-2025` is the hosted-route extension over that same runtime

## Start Here

- [../README.md](../README.md): install, bootstrap, smoke, and operator commands
- [first_run.md](first_run.md): shortest path from fresh checkout to a working pure-Python example
- [python_rti_backend.md](python_rti_backend.md): main 2025 Python RTI lane, wrapper boundary, and bounded working-surface claim
- [python_rti_reading_map.md](python_rti_reading_map.md): shortest editing path for the main `python2025` RTI lane
- [networked_rti_python.md](networked_rti_python.md): bounded hosted `python-2025-fedpro-grpc` route over the main `python2025` lane, with concrete entrypoints and usage shape
- [../tools/python](../tools/python): operator entrypoint for `verify-main-2025` and `verify-routes-2025`
- [../scripts/run_spec2025_finish_line.py](../scripts/run_spec2025_finish_line.py): regenerate the checked-in 2025 finish-line and route-parity evidence bundle
- [verification/time_model_compliance.md](verification/time_model_compliance.md): time-management, lookahead, GALT/LITS, and radar-window proof front door for the primary 2025 Python RTI lane
- [../tools/pitch](../tools/pitch): narrow vendor-runtime operator path when you need the Pitch-safe two-federate `time-window-probe` or `time-window-restore-state-probe` bounded credence routes without widening the main `python2025` claim
- [requirements/ieee-1516-2025/README.md](requirements/ieee-1516-2025/README.md): 2025 requirements index, bounded proof notes, and requirement-facing evidence map for the main `python2025` lane
- [requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md](requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md): tracked Proto2025 and Target/Radar example/FOM-backed scenario boundary for the bounded `python2025` claim
- [requirements/ieee-1516-2025/save_restore_bounded_proof.md](requirements/ieee-1516-2025/save_restore_bounded_proof.md): explicit save/restore rollback-family boundary for lifecycle control, routing/policy rollback, ownership rollback, and time-window rollback on the bounded `python2025` claim
- [requirements/ieee-1516-2025/callback_bounded_proof.md](requirements/ieee-1516-2025/callback_bounded_proof.md): explicit callback-delivery family boundary for direct/hosted `python2025` callback proofs, callback-control hygiene, and callback surface limits on the bounded `python2025` claim
- [requirements/ieee-1516-2025/lookahead_window_bounded_proof.md](requirements/ieee-1516-2025/lookahead_window_bounded_proof.md): explicit Target/Radar lookahead-window proof ladder, negative-oracle guards, and Pitch-safe vendor-credence boundary for the bounded `python2025` claim
- [requirements/ieee-1516-2025/python2025_direct_bounded_proof.md](requirements/ieee-1516-2025/python2025_direct_bounded_proof.md): direct-lane bounded executable-behavior note for the main `python2025` runtime surface
- [requirements/ieee-1516-2025/python2025_exclusion_boundaries.md](requirements/ieee-1516-2025/python2025_exclusion_boundaries.md): explicit non-claim map for shim aliases, Java/C++ bindings, hosted-route boundaries, umbrella rows, retired rows, and OMT extension semantics around the main `python2025` lane
- [python_environment.md](python_environment.md): Python bootstrap, `.venv`, extras, and install order
- [language_shim_routes.md](language_shim_routes.md): Java/C++ standard-surface binding routes and evidence contract
- [java_toolchain.md](java_toolchain.md): Java discovery, required tools, and Java shim artifact inventory
- [../tools/java](../tools/java): short Java toolchain inventory front door
- [test_surface.md](test_surface.md): canonical verification lanes and machine-readable discovery flow
- [codex_runner_authorization.md](codex_runner_authorization.md): draft loopback-socket authorization request for Codex verification sessions
- [spec_reading_map.md](spec_reading_map.md): smallest practical reading path for the abstract/public spec surface
- [fom_reading_map.md](fom_reading_map.md): smallest practical reading path for FOM parsing and merge behavior
- [fom_validate.md](fom_validate.md): single-command XML validation path with human-readable reports
- [rti_factory_reading_map.md](rti_factory_reading_map.md): installed RTI factory listing, selection, and introspection
- [two_federate_quickstart.md](two_federate_quickstart.md): first stop for the composite two-federate example
- [install_matrix.md](install_matrix.md): extras, backend families, and dependency order
- [agent_runbook.md](agent_runbook.md): start-here sequence for agents and automation

## Reference

- [documentation_hierarchy.md](documentation_hierarchy.md): canonical doc flow and hierarchy
- [workspace_layout.md](workspace_layout.md): top-level workspace areas and ownership split
- [package_dependency_tree.md](package_dependency_tree.md): machine-derived installable package dependency tree
- [package_hierarchy_and_versioning.md](package_hierarchy_and_versioning.md): simplified package dependency tree plus versioning status
- [python_api_spec.md](python_api_spec.md): clean Python spec package and runtime facade split
- [callback_model_guide.md](callback_model_guide.md): evoked vs immediate callback behavior, tests, and implementation entry points
- [import_boundary_rules.md](import_boundary_rules.md): package-family import rules and transport-versus-backend boundaries
- [package_layout.md](package_layout.md): package ownership map and front-door package roles
- [verification/run_sequence.md](verification/run_sequence.md): full verification sequence and run order
- [top_to_bottom_green.md](top_to_bottom_green.md): explicit repo-wide finish definition for base Python, repo-green, and vendor-green

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
- [../packages/hla-backend-certi/docs/certi_spec_traceability.md](../packages/hla-backend-certi/docs/certi_spec_traceability.md): real CERTI sync/ownership coverage
- [../packages/hla-backend-certi/docs/certi_runtime_limitations.md](../packages/hla-backend-certi/docs/certi_runtime_limitations.md): patched-vs-upstream CERTI baseline policy and runtime shortfalls
- [../packages/hla-backend-certi/docs/certi_negotiated_ownership_findings.md](../packages/hla-backend-certi/docs/certi_negotiated_ownership_findings.md): CERTI negotiated ownership investigation
- [../packages/hla-vendor-pitch/docs/pitch_decision_tree.md](../packages/hla-vendor-pitch/docs/pitch_decision_tree.md): Pitch runtime selection and troubleshooting
- [../packages/hla-vendor-pitch/docs/pitch_docker_quickstart.md](../packages/hla-vendor-pitch/docs/pitch_docker_quickstart.md): shortest Pitch operator path
- [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md): repo-green versus vendor-green runner contract
- [vendor_runner_provisioning.md](vendor_runner_provisioning.md): dedicated runner provisioning spec and CI variable checklist
- [vendor_runner_provisioning_template.yaml](vendor_runner_provisioning_template.yaml): machine-readable runner provisioning template
- [vendor_parity_artifacts.md](vendor_parity_artifacts.md): harmonized vendor artifact packet
- [../packages/hla-backend-certi/docs/certi_section8_runbook.md](../packages/hla-backend-certi/docs/certi_section8_runbook.md): CERTI operator runbook

## Historical / Provenance

These pages are for audit, source provenance, retained packet contents, and
historical evidence. They are not the primary onboarding path.

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
- [supported_subset_policy.md](supported_subset_policy.md): explicit broad-spec versus supported-subset policy statements for defended partial compliance rows
- [reference/hla_interface_contracts.md](reference/hla_interface_contracts.md): generated interface-contract snapshot

Planning:

- [plans/README.md](plans/README.md): plan index
- [plans/imported_requirements_backlog_v1_0.md](plans/imported_requirements_backlog_v1_0.md): generated requirement-driven implementation queues
- [plans/requirements_finish_line.md](plans/requirements_finish_line.md): handoff note for finishing remaining requirement rows without overclaiming
- [development_next_steps.md](development_next_steps.md): current next-step backlog
- [inbox_inventory_2026-06-05.md](inbox_inventory_2026-06-05.md): source-drop promotion out of `INBOX`

## Read Next

1. [first_run.md](first_run.md)
2. [python_environment.md](python_environment.md)
3. [two_federate_quickstart.md](two_federate_quickstart.md)
4. [package_dependency_tree.md](package_dependency_tree.md)
