# First Run

This is the shortest supported path from a fresh checkout to a working example.

Use this if you are new to the repo and do not need CERTI, Pitch, JPype, or
Py4J yet.

## Goal

Get all of these working in order:

1. the repo-local Python environment
2. the pure-Python backend
3. the Target/Radar example

## Prerequisites

- Python 3.10 or newer
- `bash`
- `git`

## Commands

From the repository root:

```bash
./scripts/bootstrap_profile.sh doctor
./scripts/bootstrap_profile.sh python
source .venv/bin/activate
python examples/backend_recording.py
python examples/target_radar_simulation.py --backend python --steps 5
```

If those commands succeed, your base environment is working.

## What This Does

- `./scripts/bootstrap_profile.sh python`
  creates or refreshes the repo-local virtual environment
- `source .venv/bin/activate`
  activates the repo-managed Python environment
- `python examples/backend_recording.py`
  proves the lightweight backend path works
- `python examples/target_radar_simulation.py --backend python --steps 5`
  proves a real example federate path works

## What Not To Do First

Do not start with:

- `./scripts/certi_easy.sh`
- `./scripts/pitch_docker_easy.sh`
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
