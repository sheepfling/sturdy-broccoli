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
./tools/test-focus run python-2025-time
./tools/test-focus run python-2025-runtime -- --maxfail=1
./tools/test-focus resume python-2025-runtime
```

This is the shortest restartable path in the repo right now.

If you think in submodule names instead of target ids, use aliases:

```bash
./tools/test-focus run fom-target-radar
./tools/test-focus run rti-factory
./tools/test-focus run bridge-jpype
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
./tools/test-focus run rti-core
./tools/test-focus run python-2025-time
./tools/test-focus run python-2025-save-restore
./tools/test-focus run python-2025-ownership
./tools/test-focus run python-2025-mom-callbacks
./tools/test-focus run routes-2025
./tools/test-focus run transport
./tools/test-focus run requirements-2025
./tools/test-focus run verification
```

Treat these as the normal package/theme restart surface.

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
