# Junior Test Diagnosis Runbook

Use this when you are new to the repo and the question is:

- how do I get to green?
- what do I run first?
- how do I rerun one failure?
- how do I run focused tests?
- how do I figure out which package owns the failure?

This page is intentionally procedural.

## The Main Fix For Slow Test Loops

Do not keep rerunning full repo-green when the failure is local to one package
or one concern. Use:

```bash
./tools/test-focus inventory
./tools/test-focus run foundation
./tools/test-focus run python-examples
./tools/test-focus run java-bridges
./tools/test-focus run jpype
./tools/test-focus run target-radar
./tools/test-focus run execution-membership
./tools/test-focus run python-2025-time
./tools/test-focus run python-2025-ddm
./tools/test-focus run python-2025-runtime -- --maxfail=1
./tools/test-focus resume python-2025-runtime
```

This is the shortest restartable path in the repo right now.

If you think in submodule names instead of target ids, use aliases:

```bash
./tools/test-focus run fom-target-radar
./tools/test-focus run rti-factory
./tools/test-focus run bridge-jpype
./tools/test-focus run membership-guards
./tools/test-focus run save-restore-2025
./tools/test-focus run finish-line-2025
```

## The Shortest Good Path

From the repo root:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
./tools/test-surface recommend
./tools/python verify
```

If that works, you have the default repo-green path.

## If You Only Need A Fast Confidence Check

Run:

```bash
./tools/python verify-fast
```

Use this when:

- you changed docs or wrappers
- you want a cheaper first pass
- you are not ready for the full repo-green lane

## If Repo-Green Fails

Use this narrowing order:

1. identify which command failed
2. rerun the failing lane directly
3. rerun the failing test file
4. rerun the failing test node
5. inspect which package owns the code under failure

## Step 1: Identify The Right Lane

Use:

```bash
./tools/test-surface inventory
./tools/test-surface recommend
```

Common lanes:

- `./tools/python verify-fast`
- `./tools/python verify`
- `./tools/python verify-main-2025`
- `./tools/python verify-routes`
- `./tools/python verify-routes-2025`

If you do not know where to start, `./tools/python verify` is the default
repo-green lane.

If you need the canonical shard names, alias hints, or the difference between a
shard and a view, use:

- [`test_surface.md`](test_surface.md)
- [`verification/shard_registry.md`](verification/shard_registry.md)
- [`verification/view_registry.md`](verification/view_registry.md)

If the repo-green unit phase is too broad, use:

```bash
./tools/test-surface run repo-green-units
```

If you do not want to remember the canonical shard ids, use the alias forms:

```bash
./tools/test-surface run foundation
./tools/test-surface run onboarding
./tools/test-surface run shim-tooling
./tools/test-surface run transport
./tools/test-surface run scenarios
```

If you need to maintain that sweep:

- reorder shards in `testing/test_surface_manifest.json` under `repo-green-units.include_lanes`
- edit one shard by changing the matching `unit-*` lane in the same manifest

## Step 2: Rerun The Failing Lane

Examples:

```bash
./tools/python verify
./tools/python verify-fast
./tools/python verify-main-2025
./tools/python verify-routes
./tools/python verify-routes-2025
./tools/java test-bridges
./tools/python test-examples
```

Use the wrapper command first. Do not start by guessing a deep script path.

If the lane is too large, switch immediately to a focused target:

```bash
./tools/test-focus inventory
./tools/test-focus run <target>
./tools/test-focus resume <target>
```

## Step 3: Rerun One Failing Test File

Use the generic pytest wrapper:

```bash
./tools/test tests/test_python_route_examples.py
./tools/test tests/test_java_bridge_examples.py
./tools/test tests/test_hla_factory_composition.py
```

This is the normal answer when one file failed in repo-green.

## Step 4: Rerun One Failing Test Node

Use the full pytest node id:

```bash
./tools/test tests/test_python_route_examples.py::test_python_route_federate_example_runs_for_supported_editions
```

This is the normal answer when one test in a file failed.

To rerun only prior failures inside the same focused target, use:

```bash
./tools/test-focus resume foundation
./tools/test-focus resume python-2025-runtime
```

## Step 5: Rerun By Keyword

Use `-k` when you know a theme but not the exact node:

```bash
./tools/test -k java_bridge
./tools/test -k python_route
./tools/test -k ownership
```

This is useful when several related tests failed.

You can combine that with the direct wrapper:

```bash
./tools/test -k ownership --lf
./tools/test tests/transport --ff
```

## Focused Commands That Already Exist

Use these when you do not want the whole lane.

### Named focused targets

```bash
./tools/test-focus inventory
./tools/test-focus run foundation
./tools/test-focus run fom
./tools/test-focus run target-radar
./tools/test-focus run execution-membership
./tools/test-focus run rti-core
./tools/test-focus run python-2025-time
./tools/test-focus run python-2025-ddm
./tools/test-focus run python-2025-save-restore
./tools/test-focus run python-2025-ownership
./tools/test-focus run python-2025-mom-callbacks
./tools/test-focus run routes-2025
./tools/test-focus run transport
./tools/test-focus run requirements-2025
./tools/test-focus run verification
```

Treat these as the normal package/theme restart surface.

Use `./tools/test-focus run execution-membership` when the failure smells like:

- a join or resign precondition regression
- destroy while still joined
- disconnect without resign
- update, interaction, query, or DDM calls being accepted after a federate is
  no longer an execution member

Use that target specifically for the exercised execution-affecting calls:

- `updateAttributeValues`
- `sendInteraction`
- `deleteObjectInstance` and `localDeleteObjectInstance`
- `requestAttributeValueUpdate`
- `queryAttributeTransportationType`
- `sendInteractionWithRegions`
- `requestAttributeValueUpdateWithRegions`

Keep the hosted-route scope honest:

- this focused target includes the direct lanes plus the hosted 2025
  gRPC/FedPro and REST-hosted execution-membership proof
- it is not the generic transport lane
- if the question is "did generic REST or gRPC transport plumbing regress?" use
  `./tools/test-focus run transport`

Current exact membership of `execution-membership`:

- 2010 lifecycle and not-joined guards:
- `test_destroy_federation_execution_requires_no_joined_federates`
- `test_resign_federation_execution_rejects_not_connected_and_not_joined`
- `test_disconnect_requires_resign_and_marks_backend_not_connected`
- `test_reserve_object_instance_name_rejects_not_connected_not_joined_and_save_restore`
- `test_register_object_instance_rejects_not_connected_not_joined_name_in_use_and_save_restore`
- `test_name_release_and_query_interaction_transport_tail_reject_not_connected_not_joined_and_save_restore`
- `test_delete_and_local_delete_object_instance_reject_not_connected_not_joined_and_save_restore`
- `test_update_attribute_values_rejects_not_connected_not_joined_unknown_object_invalid_time_not_owned_and_save_restore`
- `test_send_interaction_rejects_not_connected_not_joined_invalid_inputs_and_invalid_time`
- `test_request_attribute_value_update_rejects_not_connected_not_joined_and_save_restore`
  - `test_query_attribute_transportation_type_and_reserve_multiple_names_reject_not_connected_not_joined_and_save_restore`
  - `test_ddm_send_interaction_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`
  - `test_request_attribute_value_update_with_regions_rejects_not_connected_not_joined_invalid_region_and_save_restore`
- shared federation-management scenario guards:
  - `test_python_backend_join_precondition_matrix`
  - `test_python_backend_resign_precondition_matrix`
- 2025 direct runtime guards:
  - `test_2025_provider_runs_federation_lifecycle_negative_scenario_end_to_end`
  - `test_2025_provider_runs_resign_precondition_scenario_end_to_end`
  - `test_2025_provider_reports_federation_executions_and_members`
- hosted 2025 route guards:
  - `test_2025_transport_server_runs_shared_federation_lifecycle_negative_scenario_over_fedpro_route`
  - `test_2025_transport_server_runs_shared_join_precondition_scenario_over_fedpro_route`
  - `test_2025_transport_server_runs_shared_resign_precondition_scenario_over_fedpro_route`
  - `test_2025_rest_transport_server_runs_shared_federation_lifecycle_negative_scenario`
  - `test_2025_rest_transport_server_runs_shared_join_precondition_scenario`
  - `test_2025_rest_transport_server_runs_shared_resign_precondition_scenario`

Current primary requirement owners behind `execution-membership`:

- 2010 federation-management lifecycle rows
  `HLA1516.1-FM-4_6-RTIAPI-001-EXC`,
  `HLA1516.1-FM-4_9-RTIAPI-001-EXC`, and
  `HLA1516.1-FM-4_10-RTIAPI-001-EXC`
- 2010 object-management joined-state rows
  `HLA1516.1-OM-6_2-RESERVEOBJECTINSTANCENAME-PRE-001`,
  `HLA1516.1-OM-6_4-RELEASEOBJECTINSTANCENAME-PRE-001`,
  `HLA1516.1-OM-6_8-REGISTEROBJECTINSTANCE-PRE-001`,
  `HLA1516.1-OM-6_14-DELETEOBJECTINSTANCE-PRE-001`,
  `HLA1516.1-OM-6_10-UPDATEATTRIBUTEVALUES-EXC-001`,
  `HLA1516.1-OM-6_12-SENDINTERACTION-PRE-001`,
  `HLA1516.1-OM-6_12-SENDINTERACTION-EXC-001`,
  `HLA1516.1-OM-6_19-REQUESTATTRIBUTEVALUEUPDATE-PRE-001`, and
  `HLA1516.1-OM-6_25-QUERYATTRIBUTETRANSPORTATIONTYPE-PRE-001`
- 2025 federation-management execution-state rows `HLA2025-FI-SVC-005`,
  `HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-010`, and `HLA2025-FI-SVC-011`
- 2025 object-management execution-state rows `HLA2025-FI-SVC-051`, `HLA2025-FI-SVC-053`,
  `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-061`,
  `HLA2025-FI-SVC-065`, `HLA2025-FI-SVC-070`, and `HLA2025-FI-SVC-077`

Use `./tools/test-focus run python-2025-ddm` when the failure smells like:

- region overlap routing
- `attributesInScope` or `attributesOutOfScope` transitions
- passive DDM alias behavior
- restore or disconnect cleanup for queued DDM delivery

### Direct Python example routes

```bash
./tools/python smoke-examples --all
./tools/python test-examples
```

### Java bridge routes

```bash
./tools/java smoke --all
./tools/java test-bridges
```

### Java bridge with the tiny built shim jar

```bash
./tools/java smoke --bridge jpype --edition 2010 --real-shim
./tools/java smoke --bridge py4j --edition 2025 --real-shim
```

### Pitch Docker onboarding path

```bash
./tools/pitch doctor
./tools/pitch preflight
./tools/test-surface run unit-vendor-onboarding
./tools/pitch smoke-best-effort
```

The shorter alias form is:

```bash
./tools/test-surface run onboarding
```

Use [`pitch_docker_first_run.md`](pitch_docker_first_run.md) when the blocker is
Pitch bundle placement, Docker readiness, or the managed CRC/FedPro path.

### Test-surface shard aliases

Use these when the full `unit-*` names are harder to remember than the job:

```bash
./tools/test-surface run foundation
./tools/test-surface run onboarding
./tools/test-surface run shim-tooling
./tools/test-surface run transport
./tools/test-surface run scenarios
```

## How To Tell Which Package Owns A Failure

Use these questions:

1. what file failed?
2. which `packages/<name>/src/...` tree contains the implementation?
3. is the failure in a standard API package, backend package, bridge package,
   transport package, vendor package, FOM package, or verification package?

Start with:

- [`package_layout.md`](package_layout.md)
- [`package_dependency_tree.md`](package_dependency_tree.md)
- [`import_boundary_rules.md`](import_boundary_rules.md)
- [`../packages/README.md`](../packages/README.md)

If you want the dependency graph regenerated:

```bash
./tools/package-deps generate
```

## Quick Ownership Heuristics

- `packages/hla-rti1516e/...`
  means IEEE 1516.1-2010 API surface
- `packages/hla-rti1516-2025/...`
  means IEEE 1516.1-2025 API surface
- `packages/hla-backend-python1516e/...`
  means direct 2010 Python RTI behavior
- `packages/hla-backend-python1516-2025/...`
  means main 2025 Python RTI behavior
- `packages/hla-bridge-java-jpype/...`
  means JPype Java bridge mechanics
- `packages/hla-bridge-java-py4j/...`
  means Py4J Java bridge mechanics
- `packages/hla-transport-...`
  means hosted transport code
- `packages/hla-vendor-...`
  means vendor-specific runtime support
- `packages/hla-verification/...`
  means verification harness and repo-internal proof/report support

## If The Failure Looks Like Environment Setup

Run:

```bash
./tools/bootstrap doctor
```

Then check:

- Python version
- `.venv` exists
- `.venv` is activated
- optional extras are installed for the lane you are using

For Java bridge work:

```bash
./tools/java
```

For hosted Python route work:

```bash
./tools/python verify-routes-preflight
```

## If The Failure Looks Like A Vendor Runtime Problem

Do not start with full repo-green debugging.

Use the vendor-facing wrappers first:

```bash
./tools/certi-easy preflight
./tools/pitch preflight
./tools/vendor-green matrix
```

Read:

- [`vendor_runtime_runner_guide.md`](vendor_runtime_runner_guide.md)

## If The Failure Looks Like A Java Bridge Problem

Use this order:

1. `./tools/java smoke --all`
2. `./tools/java test-bridges`
3. `./tools/test tests/test_java_bridge_examples.py`
4. `./tools/test tests/test_tools_java_wrapper.py`

Read:

- [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
- [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md)
- [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md)

## If The Failure Looks Like A Pure Python Example Problem

Use this order:

1. `./tools/python smoke-examples --all`
2. `./tools/python test-examples`
3. `./tools/test tests/test_python_route_examples.py`

## What To Do After You Fix Something

Use the smallest confirming command first:

1. rerun the single failing node
2. rerun the test file
3. rerun the focused wrapper or lane
4. rerun `./tools/python verify` only after the focused checks are green

That keeps iteration fast.

## Recommended Read Order

1. [`first_run.md`](first_run.md)
2. [`python_environment.md`](python_environment.md)
3. [`test_surface.md`](test_surface.md)
4. [`package_layout.md`](package_layout.md)
5. [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
