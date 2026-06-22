# First Run

This is the shortest supported path from a fresh checkout to a working example.

Use this if you are new to the repo and do not need CERTI, Pitch, JPype, or
Py4J yet.

This page is the 2010 pure-Python bootstrap path. It is not the main entry
point for the IEEE 1516.1-2025 runtime lane.

## Goal

Get all of these working in order:

1. the repo-local Python environment
2. the pure-Python 2010 backend
3. the Target/Radar example

## Prerequisites

- Python 3.10 or newer
- `bash`
- `git`

## Commands

From the repository root:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
python -m pip install --no-build-isolation -e packages/hla-rti1516e -e packages/hla-backend-common -e packages/hla-backend-inmemory -e packages/hla-rti-core -e packages/hla-fom-target-radar -e packages/hla-verification
python examples/backend_recording.py
python examples/target_radar_simulation.py --backend python --steps 5
```

If those commands succeed, your base environment is working.

For the primary 2025 Python RTI lane, switch next to:

- [`python_rti_backend.md`](python_rti_backend.md) for the main
  `hla-backend-python2025` runtime lane
- [`python_rti_reading_map.md`](python_rti_reading_map.md) for the shortest
  edit path through that runtime
- [`networked_rti_python.md`](networked_rti_python.md) for the bounded hosted
  `python-2025-fedpro-grpc` route

## What This Does

- `./tools/bootstrap python`
  creates or refreshes the repo-local virtual environment
- `source .venv/bin/activate`
  activates the repo-managed Python environment
- `python -m pip install ...`
  installs the core split packages in editable mode; the repo root itself is
  tooling-only and is not installed as a package
- `python examples/backend_recording.py`
  proves the lightweight backend path works
- `python examples/target_radar_simulation.py --backend python --steps 5`
  proves a real example federate path works

The 2025 runtime story is intentionally separate:

- `python2025` is the main IEEE 1516.1-2025 RTI lane
- `shim` is only a compatibility-wrapper provider name over that runtime

## What Not To Do First

Do not start with:

- `./tools/certi-easy`
- `./tools/pitch`
- JPype-only examples
- Py4J-only examples

Those routes depend on the base Python environment already working.

## If Something Fails

Check these first:

1. you are running from the repo root
2. `.venv` exists
3. `.venv` is activated
4. your Python version is 3.10 or newer

If you need the broader setup story, go to
[`python_environment.md`](python_environment.md).

If you want the two-federate verification path next, go to
[`two_federate_quickstart.md`](two_federate_quickstart.md).

## Read Next

1. [`python_environment.md`](python_environment.md)
2. [`two_federate_quickstart.md`](two_federate_quickstart.md)
3. [`../README.md`](../README.md)
