# Agent Runbook

This page is for agents or automation entering the repo cold.

The main failure mode is starting with vendor tooling before the base Python
environment exists. Do not do that.

## First Sequence

From the repository root:

```bash
./scripts/bootstrap_profile.sh doctor
./scripts/bootstrap_profile.sh python
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

- `src/hla2010/` is the main Python package root
- `hla2010/` is a narrow shim area
- `packages/*/src/` owns split backend and support implementations
- `examples/` contains runnable entrypoints
- `scripts/` contains operator and CI entrypoints

## Safe Starting Commands

Use these before anything vendor-specific:

```bash
./scripts/bootstrap_profile.sh doctor
./scripts/bootstrap_profile.sh python
source .venv/bin/activate
python examples/backend_recording.py
python examples/target_radar_simulation.py --backend python --steps 5
./scripts/ci/test.sh
```

## Escalation Order

Use this order:

1. base Python environment
2. pure-Python example
3. test wrapper
4. bridge extras if required
5. vendor-runtime tooling if explicitly needed

## When To Install Extras

- Need JPype: `HLA2010_BOOTSTRAP_EXTRAS=jpype ./scripts/bootstrap_python.sh`
- Need Py4J: `HLA2010_BOOTSTRAP_EXTRAS=py4j ./scripts/bootstrap_python.sh`
- Need both: `HLA2010_BOOTSTRAP_EXTRAS=java ./scripts/bootstrap_python.sh`
- Need QA plus Java extras after activation:
  `python -m pip install --no-build-isolation -e ".[qa,java]"`

## Where To Send Humans

When a user asks where to begin, point them here:

1. [`first_run.md`](first_run.md)
2. [`python_environment.md`](python_environment.md)
3. [`two_federate_quickstart.md`](two_federate_quickstart.md)
4. [`install_matrix.md`](install_matrix.md)
