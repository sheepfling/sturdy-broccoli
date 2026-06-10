# Python Environment

This is the canonical setup path for this repository.

If you are a person, an agent, or CI automation, start here before running
examples, tests, or backend tools.

## What You Need First

- Python 3.10 or newer
- `bash`
- `git`

Optional later:

- `jpype1` if you want the JPype bridge paths
- `py4j` if you want the Py4J bridge paths
- Docker if you want the Pitch Docker flow
- a local CERTI build or install if you want the CERTI runtime paths

## The Shortest Working Path

From the repository root:

```bash
./bootstrap python
source .venv/bin/activate
python examples/target_radar_simulation.py --backend python --steps 5
```

That is the shortest supported path to a working local Python setup.

If you want to check the machine and workspace before bootstrapping, run:

```bash
./bootstrap doctor
```

That verifies Python, `.venv`, workspace imports, and optional backend
prerequisites without trying to install anything.

## What The Bootstrap Commands Do

There are two normal entrypoints:

```bash
./bootstrap python
./scripts/bootstrap_python.sh
```

They are related, but not identical:

- `./bootstrap python` is the operator-first entrypoint.
  It defaults to the lean `test` extras.
- `./scripts/bootstrap_python.sh` is the direct Python bootstrap entrypoint.
  It defaults to the broader `qa` extras.

Both commands:

- create or refresh the repo-local virtual environment
- install the workspace in editable mode
- install the selected extras from the root `pyproject.toml`

## Where The Virtual Environment Lives

The repository-managed `.venv` path is a symlink into local state under:

```text
/private/tmp/hla-2010/.venv
```

From the repo root you should still use it normally:

```bash
source .venv/bin/activate
```

The same local-state mechanism is also used for caches, build trees, and some
generated artifacts.

## Which Extras To Install

Pick the smallest thing that matches your work.

### 1. Basic Python development

```bash
./bootstrap python
```

This gives you:

- editable workspace install
- pytest support

### 2. Full local QA flow

```bash
HLA2010_BOOTSTRAP_EXTRAS=qa ./scripts/bootstrap_python.sh
```

This adds:

- pytest
- Ruff
- Pyright

### 3. Java bridge work

JPype:

```bash
HLA2010_BOOTSTRAP_EXTRAS=jpype ./scripts/bootstrap_python.sh
```

Py4J:

```bash
HLA2010_BOOTSTRAP_EXTRAS=py4j ./scripts/bootstrap_python.sh
```

Both:

```bash
HLA2010_BOOTSTRAP_EXTRAS=java ./scripts/bootstrap_python.sh
```

If you need both bridge dependencies and QA tooling, install them after the
bootstrap:

```bash
source .venv/bin/activate
python -m pip install --no-build-isolation -e ".[qa,java]"
```

## Install Order

Use this order unless you have a specific reason not to.

0. Optionally run `./bootstrap doctor`.
1. Bootstrap Python first.
2. Activate `.venv`.
3. Run a pure-Python example or smoke test.
4. Add bridge extras if you need JPype or Py4J.
5. Only then install or build vendor runtimes such as CERTI or Pitch.

That order matters because the vendor flows assume the Python environment and
repo-local wrappers already work.

## First Commands After Bootstrap

After the Python environment is up:

```bash
source .venv/bin/activate
python examples/backend_recording.py
python examples/target_radar_simulation.py --backend python --steps 5
./scripts/ci/test.sh
```

If those commands work, the base environment is healthy.

## Vendor Runtime Order

Once the Python path is working:

### CERTI

```bash
./certi-easy preflight
./certi-easy install
./certi-easy smoke compare
```

### Pitch

```bash
./pitch preflight
./pitch install
./pitch smoke
./pitch verify
```

Do not start with CERTI or Pitch before the Python bootstrap succeeds.

For real runtime proof on an unrestricted local terminal or a dedicated CI
runner, use [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md).

## Repo Layout For Setup Purposes

The setup-relevant parts of this repo are:

- `src/hla2010/`: root Python package and compatibility facades
- `hla2010/`: narrow shim area for plugin-facing glue
- `packages/*/src/`: package-owned backend, FOM, and support implementations
- `examples/`: runnable entrypoints
- `scripts/`: bootstrap, CI, and operator wrappers
- `tests/`: pytest coverage

The root `pyproject.toml` installs the workspace across those package roots in
editable mode.

## If You Are An Agent

Use this sequence:

```bash
./bootstrap doctor
./bootstrap python
source .venv/bin/activate
python examples/backend_recording.py
```

Do not assume the environment is already active.
Do not start with vendor runtime flows unless the task explicitly requires them.
