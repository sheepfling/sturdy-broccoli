# Top To Bottom Green

This document defines what it means for this repository to be "working top to
bottom".

That phrase should be treated as an explicit acceptance contract, not as a
vague aspiration.

## Goal

A top-to-bottom green repo has all of these layers aligned:

1. package boundaries are clear and physically owned by the right package
2. public operator entrypoints are stable and documented
3. the default Python bootstrap path works on a fresh checkout
4. repo-green verification passes in ordinary environments
5. CERTI and Pitch real-runtime lanes are supported on a best-effort basis,
   with clear preflight, failure classification, and next steps

## The Three Execution Levels

The repo now has three distinct expectations.

### 1. Base Python Green

This is the minimum supported success path on a fresh machine.

Required outcome:

- repo-local `.venv` bootstraps successfully
- the workspace installs in editable mode
- the pure Python backend runs
- the example federate path runs

Canonical commands:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
python examples/backend_recording.py
python examples/target_radar_simulation.py --backend python --steps 5
```

### 2. Repo Green

This is the default full verification lane for normal local development and CI.

Required outcome:

- repo-owned tests and wrappers pass
- generated status and parity artifacts are produced
- vendor prerequisites are still checked
- blocked CERTI or Pitch runtime prerequisites do not fail the whole lane

If you need to inspect the Java toolchain that backs Rosetta route evidence,
use `./tools/java`.

Canonical command:

```bash
./tools/python verify
```

Repo-green is the standard answer to "does the repo work here?"

### 3. Vendor Green

This is the strict real-runtime lane for dedicated vendor execution.

Required outcome:

- vendor preflight runs first
- dedicated runner state validates before runtime execution
- CERTI and Pitch runtime failures are distinguished from provisioning failures
- real-runtime slices pass when the host is correctly provisioned

Canonical commands:

```bash
./tools/vendor-green certi
./tools/vendor-green certi-compare
./tools/vendor-green pitch
./tools/vendor-green matrix
```

Vendor-green is not expected to pass on every machine. It is expected to be
honest, reproducible, and explicit about why it cannot run.

## CERTI And Pitch Best-Effort Contract

"Best effort" does not mean hand-wavy. It means:

- the supported operator routes are stable:
  - `./tools/certi-easy ...`
  - `./tools/pitch ...`
- the preflight checks are machine-readable
- blocked environments are classified clearly
- known-gap routes emit explicit status rather than silent failure
- dedicated runner contracts are documented and validated

For this repo, CERTI and Pitch are considered healthy when one of these is
true:

1. the real-runtime lane passes on a provisioned host, or
2. the repo clearly reports that the environment is blocked and emits the
   expected artifacts and next-step guidance

Best-effort operator examples:

- `./tools/certi-easy verify-best-effort`
- `./tools/pitch verify-best-effort`

That second case is still "working" for repo-green. It is not "green" for
vendor-green.

## Acceptance Criteria

The repo should be considered top-to-bottom green only when all of the
following are true.

### Structure

- backend families are physically separated into package-owned trees
- shared verification/harness code has an obvious owner
- the root directory is reserved for docs, manifests, config, and a small
  number of obvious top-level areas

### Public Interface

- `tools/` is the canonical human-facing operator surface
- root helper executables are gone
- docs, workflows, tests, artifacts, and next-step text all point to the same
  command surface

### Default Local Success

- the pure Python path works without CERTI, Pitch, Docker, JPype, or Py4J
- `first_run.md` stays accurate
- a new contributor can reach a working example without guesswork

### Verification

- repo-green passes locally and in CI
- generated runtime status and parity artifacts are current and internally
  consistent
- drift tests guard the documented command surface and workflow templates

### Vendor Runtime

- `./tools/certi-easy preflight` and `./tools/pitch preflight` produce useful
  status on any host
- strict vendor lanes succeed on provisioned hosts
- when vendor lanes cannot run, they fail for concrete, diagnosed reasons
- runner provisioning requirements are documented and machine-validated

## Practical Finish Line

When deciding what to work on next, use this order:

1. keep the pure Python path solid
2. keep repo-green green
3. keep vendor best-effort diagnostics honest
4. harden real CERTI and Pitch execution on provisioned hosts

This ordering prevents vendor-runtime complexity from degrading the default
developer path.

## Related Docs

- [first_run.md](first_run.md)
- [python_environment.md](python_environment.md)
- [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md)
- [vendor_runner_provisioning.md](vendor_runner_provisioning.md)
- [workspace_layout.md](workspace_layout.md)
