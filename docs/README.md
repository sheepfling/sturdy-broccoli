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

If you already know what you need, pick a lane:

- run the base Python example:
  [`first_run.md`](first_run.md)
- set up or repair the environment:
  [`python_environment.md`](python_environment.md)
- run the two-federate flow:
  [`two_federate_quickstart.md`](two_federate_quickstart.md)
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
  [`create_federate_and_fom.md`](create_federate_and_fom.md),
  [`fom_workbench.md`](fom_workbench.md)
- run local verification:
  [`local_verification_commands.md`](local_verification_commands.md)
- understand Java/vendor/runtime support:
  [`java_toolchain.md`](java_toolchain.md),
  [`vendor_runtime_runner_guide.md`](vendor_runtime_runner_guide.md),
  [`backend_conformance_matrix.md`](backend_conformance_matrix.md)

Concrete operator entrypoints that matter early:

- [`../tools/bootstrap`](../tools/bootstrap)
- [`../tools/test`](../tools/test)
- [`../tools/python`](../tools/python)
- [`../tools/certi-easy`](../tools/certi-easy)
- [`../tools/pitch`](../tools/pitch)

## Reference

Use these when you need structure, not onboarding:

- [`package_layout.md`](package_layout.md): package ownership map
- [`repo_mental_model.md`](repo_mental_model.md): shortest explanation of the layers
- [`package_hierarchy_and_versioning.md`](package_hierarchy_and_versioning.md): package family overview
- [`package_dependency_tree.md`](package_dependency_tree.md): dependency graph
- [`import_boundary_rules.md`](import_boundary_rules.md): import constraints and layering
- [`package_responsibilities.md`](package_responsibilities.md): where code belongs
- [`callback_model_guide.md`](callback_model_guide.md): callback behavior
- [`language_shim_routes.md`](language_shim_routes.md): Java/C++ route surfaces
- [`fom_workbench.md`](fom_workbench.md): FOM workbench scope and operator path
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
3. [`repo_mental_model.md`](repo_mental_model.md)
4. [`package_layout.md`](package_layout.md)
