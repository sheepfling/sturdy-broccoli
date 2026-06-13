# First Run

This is the shortest supported path from a fresh checkout to a working
pure-Python example.

Use this if you are new to the repo and do not need CERTI, Pitch, JPype, or
Py4J yet.

## Goal

Prove all of these in order:

1. the repo-local Python environment is bootstrapped
2. the editable split workspace packages are installed
3. the installed RTI factory list is visible
4. the pure-Python RTI path runs
5. the Target/Radar scenario runs

## Prerequisites

- Python 3.10 or newer
- `bash`
- `git`

## One Command Path

Run these commands from the repository root:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
./tools/rti-factories show in-memory --probe
./tools/examples backend-recording
./tools/examples target-radar --backend in-memory --steps 5
```

`./tools/bootstrap python` is the canonical bootstrap step. It creates or
refreshes `.venv` and installs the supported split workspace packages in
editable mode. The repository root is tooling-only and is not installed as a
package, so do not use `pip install -e .` and do not add a separate manual
editable-install step here.

`./tools/rti-factories show in-memory --probe` is the shortest backend-choice
checkpoint. It proves that the default development route resolves to the pure
Python RTI factory before you start running larger examples.

## Expected Output

`./tools/examples backend-recording` should print the lightweight backend
smoke shape:

```text
HLA 1516.1-2010
connect CallbackModel.HLA_EVOKED
```

`./tools/examples target-radar --backend in-memory --steps 5` should
print a summary line plus five track rows. A representative sample lives at
[`examples/target_radar_python_expected_output.txt`](examples/target_radar_python_expected_output.txt).

The wrapper commands above run these underlying example scripts through the
workspace Python environment:

- [`../examples/backend_recording.py`](../examples/backend_recording.py)
- [`../examples/rti_factory_selection.py`](../examples/rti_factory_selection.py)
- [`../examples/target_radar_simulation.py`](../examples/target_radar_simulation.py)

`./tools/rti-factories show in-memory --probe` should report:

- selected factory name `python`
- selectable names that include `in-memory`
- probe `available: true`
- backend kind `python/in-memory`

`./tools/examples target-radar --backend in-memory --steps 5` and
`python examples/target_radar_simulation.py --backend python --steps 5`
should both land on the same pure Python RTI route.

## What Worked

If the commands succeed:

- `.venv` exists and is usable
- the split packages import from the bootstrapped environment
- the default `python` / `in-memory` factory selection resolves cleanly
- the pure-Python RTI backend works
- the packaged Target/Radar FOM and scenario helpers work

## What To Run Next

- `./tools/test`
- `./tools/two-federate`
- `./tools/examples rti-factory-selection --name in-memory --probe`
- [`python_environment.md`](python_environment.md)
- [`two_federate_quickstart.md`](two_federate_quickstart.md)

## Troubleshooting

Check these first:

1. you are running from the repo root
2. `./tools/bootstrap doctor` reports `workspace_imports: ok`
3. you reran `./tools/bootstrap python` after creating or refreshing `.venv`
4. `.venv` is activated before you run the example commands
5. your Python version is 3.10 or newer

If `./tools/bootstrap doctor` reports `workspace packages are not importable in
.venv`, the venv exists but the workspace is not bootstrapped yet. Rerun:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

If you need the broader setup story, go to
[`python_environment.md`](python_environment.md).

## What Not To Do First

Do not start with:

- `./tools/certi-easy`
- `./tools/pitch`
- JPype-only examples
- Py4J-only examples
- manual `pip install -e ...` recovery commands unless the canonical bootstrap
  step has already failed and you are debugging that failure

Those routes depend on the base Python environment already working.

## Read Next

1. [`python_environment.md`](python_environment.md)
2. [`two_federate_quickstart.md`](two_federate_quickstart.md)
3. [`../README.md`](../README.md)
