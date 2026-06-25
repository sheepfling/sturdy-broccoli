# Docs

This tree is the navigation layer for the repo. It should help you pick a lane
fast, not force you to read everything.

Use this rule:

- start with one goal
- read one short guide
- move to reference only when blocked

## Start Here

If you are new, use these in order:

1. [`../README.md`](../README.md)
2. [`onboarding.md`](onboarding.md)
3. [`first_run.md`](first_run.md)
4. [`python_environment.md`](python_environment.md)
5. [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md)

Read [`first_run.md`](first_run.md) for the 2010 pure-Python bootstrap lane.
Read [`python_rti_backend.md`](python_rti_backend.md) for the main 2025 Python RTI lane in `hla-backend-python1516-2025`.
Use `./tools/python verify-main-2025` as the normal direct `python1516_2025` proof lane.
Read [`networked_rti_python.md`](networked_rti_python.md) only if you need the bounded hosted 2025 route or its parity/hygiene lane.
Use `./tools/python verify-routes-2025` when you need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane.
Read [`verification/time_model_compliance.md`](verification/time_model_compliance.md) when the question is time, lookahead, GALT/LITS, or save/restore window proof.

If you already know what you need, pick a lane:

- choose backend, transport, and FOM together from one page:
  [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)
- run the base Python example:
  [`first_run.md`](first_run.md)
- set up or repair the environment:
  [`python_environment.md`](python_environment.md)
- run the two-federate flow:
  [`two_federate_quickstart.md`](two_federate_quickstart.md)
- understand startup order, `ReadyToRun`, callback pumping, local execution
  topology, and how to improve performance without changing RTI semantics:
  [`federation_orchestration.md`](federation_orchestration.md)
- edit one runtime service:
  [`python_rti_edit_one_service.md`](python_rti_edit_one_service.md)
- get the repo mental model first:
  [`repo_mental_model.md`](repo_mental_model.md)
- inspect package boundaries:
  [`package_layout.md`](package_layout.md),
  [`package_hierarchy_and_versioning.md`](package_hierarchy_and_versioning.md),
  [`import_boundary_rules.md`](import_boundary_rules.md),
  [`package_dependency_tree.md`](package_dependency_tree.md)
- work on FOM tooling:
  [`fom_tooling_front_door.md`](fom_tooling_front_door.md)
- run local verification:
  [`local_verification_commands.md`](local_verification_commands.md)
- choose a lane or focused restart target:
  [`test_surface.md`](test_surface.md)
- get to repo-green and diagnose failures as a junior:
  [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md)
- understand Java/vendor/runtime support:
  [`java_toolchain.md`](java_toolchain.md),
  [`vendor_runtime_runner_guide.md`](vendor_runtime_runner_guide.md),
  [`backend_conformance_matrix.md`](backend_conformance_matrix.md)
- minimally wrap Java RTIs through JPype or Py4J:
  [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md),
  [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md),
  [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md)
- keep the 2010 and 2025 Python routes structurally similar:
  [`python_route_wrapping_guide.md`](python_route_wrapping_guide.md)
- extend ambassador connection or wire-format routes without changing RTI semantics:
  [`extending_ambassador_transports.md`](extending_ambassador_transports.md)
- adapt a slightly different `grpc` layer or add a whole new transport route:
  [`transport_extension_playbook.md`](transport_extension_playbook.md)

Concrete operator entrypoints that matter early:

- [`../tools/bootstrap`](../tools/bootstrap)
- [`../tools/test`](../tools/test)
- [`../tools/test-focus`](../tools/test-focus)
- [`../tools/python`](../tools/python)
- [`../tools/certi-easy`](../tools/certi-easy)
- [`../tools/pitch`](../tools/pitch)

## Reference

Use these when you need structure, not onboarding:

- [python_rti_backend.md](python_rti_backend.md): main 2025 Python RTI lane, wrapper boundary, and bounded working-surface claim
- [backend_transport_fom_selection_guide.md](backend_transport_fom_selection_guide.md): combined decision guide for backend selection, transport selection, and FOM starting points
- [python_rti_reading_map.md](python_rti_reading_map.md): shortest editing path for the main `python1516_2025` RTI lane
- [../tools/python](../tools/python): operator entrypoint for `verify-main-2025` and `verify-routes-2025`
- [verification/time_model_compliance.md](verification/time_model_compliance.md): time-management, lookahead, GALT/LITS, and radar-window proof front door for the primary 2025 Python RTI lane
- [../tools/pitch](../tools/pitch): narrow vendor-runtime operator path when you need the Pitch-safe two-federate `time-window-probe` or `time-window-restore-state-probe` bounded credence routes without widening the main `python1516_2025` claim
- [requirements/ieee-1516-2025/README.md](requirements/ieee-1516-2025/README.md): 2025 requirements index, bounded proof notes, and requirement-facing evidence map for the main `python1516_2025` lane
- [requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md](requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md): tracked proto2025 and Target/Radar example/FOM-backed scenario boundary for the bounded `python1516_2025` claim
- [requirements/ieee-1516-2025/save_restore_bounded_proof.md](requirements/ieee-1516-2025/save_restore_bounded_proof.md): explicit save/restore rollback-family boundary for lifecycle control, routing/policy rollback, ownership rollback, and time-window rollback on the bounded `python1516_2025` claim
- [requirements/ieee-1516-2025/callback_bounded_proof.md](requirements/ieee-1516-2025/callback_bounded_proof.md): explicit callback-delivery family boundary for direct/hosted `python1516_2025` callback proofs, callback-control hygiene, and callback surface limits on the bounded `python1516_2025` claim
- [requirements/ieee-1516-2025/lookahead_window_bounded_proof.md](requirements/ieee-1516-2025/lookahead_window_bounded_proof.md): explicit Target/Radar lookahead-window proof ladder, negative-oracle guards, and Pitch-safe vendor-credence boundary for the bounded `python1516_2025` claim
- [requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md](requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md)
- [requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md): explicit non-claim map for shim aliases, Java/C++ bindings, hosted-route boundaries, umbrella rows, retired rows, and OMT extension semantics around the main `python1516_2025` lane
- [language_shim_routes.md](language_shim_routes.md): Java/C++ standard-surface binding routes and evidence contract
- [extending_ambassador_transports.md](extending_ambassador_transports.md): one-page guide to in-process vs remote routes, transport seams, and where to extend ambassador connection or wire-format logic
- [transport_extension_playbook.md](transport_extension_playbook.md): concrete implementation playbook for variant `grpc` layers, new transport kinds, and hosted route adapters
- [python_route_wrapping_guide.md](python_route_wrapping_guide.md): keep 2010 and 2025 Python wrapper examples aligned at the factory/import edge
- [federation_orchestration.md](federation_orchestration.md): startup order, `ReadyToRun` synchronization, callback pumping, local execution topology, parallelism limits, and the performance tradeoff between deterministic proof lanes and higher-throughput routes
- [`package_layout.md`](package_layout.md): package ownership map
- [`repo_mental_model.md`](repo_mental_model.md): shortest explanation of the layers
- [`package_hierarchy_and_versioning.md`](package_hierarchy_and_versioning.md): package family overview
- [`package_dependency_tree.md`](package_dependency_tree.md): dependency graph
- [`import_boundary_rules.md`](import_boundary_rules.md): import constraints and layering
- [`package_responsibilities.md`](package_responsibilities.md): where code belongs
- [`callback_model_guide.md`](callback_model_guide.md): callback behavior
- [`language_shim_routes.md`](language_shim_routes.md): Java/C++ route surfaces
- [`workspace_layout.md`](workspace_layout.md): repo topography and where code, docs, tools, and generated evidence live
- [`repo_seed_scope.md`](repo_seed_scope.md): bounded seed-surface statement for the repo
- [`spec_reading_map.md`](spec_reading_map.md): shortest path into standards-facing reading and traceability
- [`requirements_trace_one_method.md`](requirements_trace_one_method.md): method-level traceability workflow
- [`supported_subset_policy.md`](supported_subset_policy.md): supported-scope policy and non-claim boundary
- [`upstream_compliance.md`](upstream_compliance.md): frozen `upstream_reference` contract boundary and layout rules
- [`fom_workbench.md`](fom_workbench.md): FOM workbench scope and operator path
- [`fom_tooling_front_door.md`](fom_tooling_front_door.md): one-page routing for FOM inspection, validation, UI/workbench, and authoring
- [`fom_reading_map.md`](fom_reading_map.md): FOM inventory, baseline, and inspection front door
- [`fom_validate.md`](fom_validate.md): FOM validation front door and command guide
- [`fom_siso_quirks.md`](fom_siso_quirks.md): short explanation of SISO family load order, main-vs-add-on structure, and common quirks
- [`fom_siso_showcase.md`](fom_siso_showcase.md): standards-backed SISO showcase packet front door
- [`fom_siso_runtime_showcase.md`](fom_siso_runtime_showcase.md): executable SISO runtime showcase front door
- [`fom_siso_pitch_micro_parity.md`](fom_siso_pitch_micro_parity.md): Pitch-eligible micro-scenario parity front door
- [`create_federate_and_fom.md`](create_federate_and_fom.md): authoring workflow for choosing, validating, and wiring a FOM into a federate or scenario
- [`preflight_artifacts.md`](preflight_artifacts.md): quick map for environment and runtime preflight artifacts
- [`top_to_bottom_green.md`](top_to_bottom_green.md): top-level repo-green path summary
- [`codex_runner_authorization.md`](codex_runner_authorization.md): copyable runner-policy request for hosted-route loopback authorization
- [`reference/README.md`](reference/README.md): reference index
- [`verification/README.md`](verification/README.md): verification doc index
- [`compliance/README.md`](compliance/README.md): retained compliance packet index

## Historical / Provenance

These are useful, but they are not start-here docs:

- [`reference/archive_index.md`](reference/archive_index.md)
- [`reference/source_index.md`](reference/source_index.md)
- [`evidence/README.md`](evidence/README.md)
- [`source_documents_inventory.md`](source_documents_inventory.md)
- [`migration/upstream_contract_snapshot.md`](migration/upstream_contract_snapshot.md)
- [`plans/README.md`](plans/README.md)
- [`development_next_steps.md`](development_next_steps.md)

## Read Next

1. [`onboarding.md`](onboarding.md)
2. [`first_run.md`](first_run.md)
3. [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md)
4. [`repo_mental_model.md`](repo_mental_model.md)
5. [`package_layout.md`](package_layout.md)
