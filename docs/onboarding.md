# Onboarding

This repo gets intimidating when the question is too broad.

Do not start with "understand the system." Start with one concrete job and
follow only that path.

## Start Here

Pick the closest match:

1. I need to know which work surface I am in
   - read [`work_surfaces.md`](work_surfaces.md)
1. I want to run something
   - read [`first_run.md`](first_run.md)
   - then run `./tools/bootstrap python`
   - then run `python examples/target_radar_simulation.py --backend python1516e --steps 5`
2. I need the environment working
   - read [`python_environment.md`](python_environment.md)
   - run `./tools/bootstrap doctor`
3. I need to edit runtime behavior
   - read [`python_rti_edit_one_service.md`](python_rti_edit_one_service.md)
   - read [`repo_mental_model.md`](repo_mental_model.md)
   - then read [`package_layout.md`](package_layout.md)
4. I need to understand package ownership
   - read [`repo_mental_model.md`](repo_mental_model.md)
   - read [`package_layout.md`](package_layout.md)
   - then read [`import_boundary_rules.md`](import_boundary_rules.md)
   - then read [`package_responsibilities.md`](package_responsibilities.md)
5. I need to work on FOMs
   - read [`fom_tooling_front_door.md`](fom_tooling_front_door.md)
   - then branch to [`fom_reading_map.md`](fom_reading_map.md),
     [`fom_validate.md`](fom_validate.md),
     [`fom_workbench.md`](fom_workbench.md), or
     [`create_federate_and_fom.md`](create_federate_and_fom.md)
6. I need to choose a backend, transport, and FOM together
   - read [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)
   - then branch to [`rti_factory_reading_map.md`](rti_factory_reading_map.md),
     [`transport_extension_playbook.md`](transport_extension_playbook.md), or
     [`fom_reading_map.md`](fom_reading_map.md) as needed
7. I need to run verification
   - read [`repo_green_quickstart.md`](repo_green_quickstart.md)
   - then read [`local_verification_commands.md`](local_verification_commands.md)
   - then read [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md)
   - then use [`../tools/python`](../tools/python) or [`../tools/test`](../tools/test)
8. I need to understand requirements, claims, or proof coverage
   - read [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md) or [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md)
   - then read [`verification/README.md`](verification/README.md)
   - then read [`spec_reading_map.md`](spec_reading_map.md)
   - then branch to one bounded proof note such as [`requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md`](requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md) or [`requirements/ieee-1516-2025/save_restore_bounded_proof.md`](requirements/ieee-1516-2025/save_restore_bounded_proof.md)
9. I need vendor or Java routes
   - read [`work_surfaces.md`](work_surfaces.md)
   - read [`java_toolchain.md`](java_toolchain.md)
   - read [`cpp_toolchain.md`](cpp_toolchain.md)
   - read [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
   - then read [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md)
   - then read [`java_bridge_encoding_and_bytes.md`](java_bridge_encoding_and_bytes.md) if the issue involves encoders, `userSuppliedTag`, or raw bytes
   - then read [`vendor_runtime_runner_guide.md`](vendor_runtime_runner_guide.md)

## What To Ignore At First

Do not start with:

- the full package tree
- archived evidence bundles
- historical plan documents
- every backend family
- every verification lane

Those matter later. They are the wrong first read.

## Mental Model

Use this simplified map:

- `hla.rti1516e` and `hla.rti1516_2025`: standard-facing API packages
- `hla.rti`: runtime discovery and ambassador creation
- `hla.backends.*`: concrete backend behavior
- `hla.transports.*`: wire transport layers
- `hla.vendors.*` and `hla.bridges.*`: external runtime integrations
- `hla.foms.*`: concrete FOM packages and resources
- `hla.verification`: verification harness and repo-internal reporting support

If you only keep that much in your head, it is enough to work productively.

For the cleaner version of that model, use
[`repo_mental_model.md`](repo_mental_model.md).

## Good First Stops By Role

- operator:
  [`../README.md`](../README.md),
  [`first_run.md`](first_run.md),
  [`repo_green_quickstart.md`](repo_green_quickstart.md),
  [`local_verification_commands.md`](local_verification_commands.md),
  [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md)
- requirements / proof reader:
  [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md),
  [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md),
  [`verification/README.md`](verification/README.md),
  [`spec_reading_map.md`](spec_reading_map.md)
- runtime engineer:
  [`python_rti_edit_one_service.md`](python_rti_edit_one_service.md),
  [`package_layout.md`](package_layout.md)
- architecture cleanup:
  [`package_responsibilities.md`](package_responsibilities.md),
  [`import_boundary_rules.md`](import_boundary_rules.md),
  [`package_dependency_tree.md`](package_dependency_tree.md)
- FOM tooling:
  [`fom_tooling_front_door.md`](fom_tooling_front_door.md)
- combined backend + transport + FOM choice:
  [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)

## Read Next

1. [`first_run.md`](first_run.md)
2. [`python_environment.md`](python_environment.md)
3. [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md)
4. [`repo_mental_model.md`](repo_mental_model.md)
5. [`package_layout.md`](package_layout.md)
