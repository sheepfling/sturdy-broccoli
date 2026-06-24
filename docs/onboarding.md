# Onboarding

This repo gets intimidating when the question is too broad.

Do not start with "understand the system." Start with one concrete job and
follow only that path.

## Start Here

Pick the closest match:

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
   - read [`create_federate_and_fom.md`](create_federate_and_fom.md)
   - then read [`fom_workbench.md`](fom_workbench.md)
6. I need to run verification
   - read [`local_verification_commands.md`](local_verification_commands.md)
   - then use [`../tools/python`](../tools/python) or [`../tools/test`](../tools/test)
7. I need vendor or Java routes
   - read [`java_toolchain.md`](java_toolchain.md)
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
  [`local_verification_commands.md`](local_verification_commands.md)
- runtime engineer:
  [`python_rti_edit_one_service.md`](python_rti_edit_one_service.md),
  [`package_layout.md`](package_layout.md)
- architecture cleanup:
  [`package_responsibilities.md`](package_responsibilities.md),
  [`import_boundary_rules.md`](import_boundary_rules.md),
  [`package_dependency_tree.md`](package_dependency_tree.md)
- FOM tooling:
  [`create_federate_and_fom.md`](create_federate_and_fom.md),
  [`fom_workbench.md`](fom_workbench.md)

## Read Next

1. [`first_run.md`](first_run.md)
2. [`python_environment.md`](python_environment.md)
3. [`repo_mental_model.md`](repo_mental_model.md)
4. [`package_layout.md`](package_layout.md)
