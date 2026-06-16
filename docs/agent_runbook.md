# Agent Runbook

This page is for agents or automation entering the repo cold.

The main failure mode is starting with vendor tooling before the base Python
environment exists. Do not do that.

## First Sequence

From the repository root:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
python examples/backend_recording.py
```

If that fails, stop and fix the Python environment first.

## Minimum Working Assumptions

Assume only this:

- the repo may be partially migrated
- the workspace may be dirty
- `.venv` may not exist yet
- vendor runtimes may not be installed

Do not assume:

- CERTI works
- Pitch works
- JPype or Py4J are installed
- the environment is already activated

## Repo Mental Model

- `packages/hla-rti1516e/src/hla/rti1516e/` owns the IEEE 1516.1-2010 API
- `packages/hla-rti-core/src/hla/rti/` owns cross-version discovery and factories
- `packages/*/src/` owns backend, transport, bridge, FOM, and support implementations
- `examples/` contains runnable entrypoints
- `tools/` contains the human-facing vendor/runtime entrypoints
- `scripts/` contains bootstrap, CI, and implementation entrypoints

## Safe Starting Commands

Use these before anything vendor-specific:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
python examples/backend_recording.py
python examples/target_radar_simulation.py --backend python --steps 5
./tools/test
```

## Escalation Order

Use this order:

1. base Python environment
2. pure-Python example
3. test wrapper
4. bridge extras if required
5. vendor-runtime tooling if explicitly needed

## When To Install Extras

- Need JPype: `HLA2010_BOOTSTRAP_EXTRAS=jpype ./tools/bootstrap python`
- Need Py4J: `HLA2010_BOOTSTRAP_EXTRAS=py4j ./tools/bootstrap python`
- Need both: `HLA2010_BOOTSTRAP_EXTRAS=java ./tools/bootstrap python`
- Need the full repo-green split workspace: `HLA2010_BOOTSTRAP_EXTRAS=qa ./tools/bootstrap python`
- Need QA plus Java extras after activation:
  `python -m pip install --no-build-isolation ruff pyright jpype1 py4j`

## Where To Send Humans

When a user asks where to begin, point them here:

1. [`first_run.md`](first_run.md)
2. [`python_environment.md`](python_environment.md)
3. [`two_federate_quickstart.md`](two_federate_quickstart.md)
4. [`install_matrix.md`](install_matrix.md)
