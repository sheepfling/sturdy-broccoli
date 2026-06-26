# Pitch Docker First Run

Use this page when the question is:

- how do I get Pitch running on a new machine?
- where do I put the Pitch runtime bundle?
- what does the Docker-backed path actually do?
- how do I diagnose `./tools/pitch` when it blocks?

This is the canonical first-run page for the Docker-backed Pitch route.

## One-Page Summary

From the repo root:

```bash
./tools/bootstrap doctor
./tools/bootstrap pitch
source .venv/bin/activate
./tools/pitch doctor
./tools/pitch all
```

If that works, you have the default Docker-backed Pitch path working.

If it does not work, stay on the Docker-backed path first:

```bash
./tools/pitch preflight
./tools/pitch install
./tools/pitch start
./tools/pitch smoke
./tools/pitch verify-best-effort
```

## What This Path Assumes

You need:

- Docker installed and runnable
- a local Pitch runtime bundle available to the repo
- the repo root checked out locally

You do not need:

- host Java for the default Docker-backed path
- JPype or Py4J just to get Pitch started

JPype and Py4J are bridge-debugging routes, not the default first-run route.

## Before You Start

Use this checklist before you assume the repo is broken:

1. Docker Desktop is open, or your Docker daemon is running
2. `docker info` works in your shell
3. the Pitch bundle exists at `third_party/pitch/PITCH-prti1516e-manual`
4. the bundle contains `lib/prtifull.jar`
5. you are running commands from the repo root

If any of those are false, fix them first.

## Where The Pitch Runtime Bundle Goes

The default bundle location is:

- `third_party/pitch/PITCH-prti1516e-manual`

If you keep the bundle somewhere else, set:

```bash
export HLA2010_PITCH_HOME=/path/to/PITCH-prti1516e-manual
```

The preflight path also recognizes the extracted bundle layout under:

- `third_party/pitch/HLA_PITCH_linux/PITCH-prti1516e-manual`

What the repo expects inside that bundle:

- `lib/prtifull.jar`

If that jar is missing, `./tools/pitch preflight` should block honestly and tell
you the bundle is incomplete.

If you are unsure whether the bundle is in the right place, do not guess. Run:

```bash
./tools/pitch doctor
./tools/pitch preflight
```

Those two commands are the canonical truth source for path discovery and setup readiness.

## First-Run Commands

Run these in order.

### Step 1: Machine And Python Bootstrap

```bash
./tools/bootstrap doctor
./tools/bootstrap pitch
source .venv/bin/activate
```

### Step 2: Inspect The Pitch State Before Running

```bash
./tools/pitch doctor
```

Use this before trying smoke or verify.

Good signals:

- Docker is found
- Pitch bundle is found
- user-home path is shown
- container state is either ready to start or already running

If Docker Desktop is not open yet, `doctor` is the fastest way to see that
without running the full lane.

### Step 3: Preflight The Runtime

```bash
./tools/pitch preflight
```

This checks:

- Docker availability
- Pitch bundle presence
- local `user.home` state
- managed CRC and FedPro port expectations

Artifacts are written under:

- `artifacts/preflight_artifacts/pitch-preflight.json`
- `artifacts/vendor_runtime_status/vendor_green_pitch/vendor_runtime_status_summary.json`
- `artifacts/vendor_parity_artifacts/vendor_parity_artifacts_summary.json`

If preflight blocks, fix that first. Do not skip ahead to `smoke` or `verify`.

For a junior, the simplest rule is:

- `environment: ready` means continue
- `environment: blocked` or `bundle-blocked` means stop and fix setup first

### Step 4: Build The Docker-Backed Runtime State

```bash
./tools/pitch install
```

This:

- discovers the Pitch runtime bundle
- seeds the repo-managed Pitch `user.home`
- builds the Docker image used for the managed runtime path

### Step 5: Start The Managed Runtime

```bash
./tools/pitch start
```

This starts the managed container and waits for:

- CRC on `127.0.0.1:8989`
- FedPro on `127.0.0.1:15164`

Use:

```bash
./tools/pitch status
./tools/pitch logs
```

when startup looks suspicious.

### Step 6: Run The Smallest Real Proof

```bash
./tools/pitch smoke
```

If you are on a machine where Docker or the local vendor runtime is expected to
be unreliable, use:

```bash
./tools/pitch smoke-best-effort
```

### Step 7: Run The Broader Vendor Lane

```bash
./tools/pitch verify
```

Or, on a partially provisioned machine:

```bash
./tools/pitch verify-best-effort
```

## The Default Recovery Sequence

When the setup is broken, use this order:

1. `./tools/pitch doctor`
2. `./tools/pitch preflight`
3. `./tools/pitch install`
4. `./tools/pitch start`
5. `./tools/pitch smoke`
6. `./tools/pitch logs`

## Common Failure Meanings

### Docker Missing Or Unreachable

Typical signal:

- preflight says Docker is missing or blocked

Action:

- start Docker Desktop or your Docker service
- rerun `docker info`
- rerun `./tools/pitch preflight`

### Pitch Bundle Missing

Typical signal:

- preflight says the Pitch bundle is missing
- or `prtifull.jar` is missing

Action:

- place the runtime under `third_party/pitch/PITCH-prti1516e-manual`
- or set `HLA2010_PITCH_HOME`
- rerun `./tools/pitch preflight`

Do not move on to `install` until `preflight` sees the bundle.

### Container Starts But Runtime Does Not Stabilize

Typical signal:

- `start` hangs or reports unhealthy state
- `smoke` fails immediately after startup

Action:

- run `./tools/pitch status`
- run `./tools/pitch logs`
- rerun `./tools/pitch stop`
- rerun `./tools/pitch start`

If the container exists but the ports do not look right, `./tools/pitch doctor`
is usually easier to interpret than raw Docker output.

### Vendor Path Is Blocked But Repo Work Should Continue

Typical signal:

- you only need repo-owned work, not strict Pitch proof

Action:

- use `./tools/python verify`
- use `./tools/test-surface run unit-vendor-onboarding` for the onboarding wrapper/tests
- use `./tools/pitch verify-best-effort` instead of strict `verify`

## When To Use JPype Or Py4J

Do not start there.

Use the bridge routes only when the question becomes:

- is the problem in the Java bridge instead of Docker/runtime setup?
- does JPype behave differently from Py4J?
- do I need to inspect the Java adaptation boundary directly?

Start with:

- [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
- [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md)
- [`../packages/hla-vendor-pitch/docs/pitch_decision_tree.md`](../packages/hla-vendor-pitch/docs/pitch_decision_tree.md)

## What To Run In CI-Like Or Junior Flows

Use these in increasing cost order:

```bash
./tools/pitch preflight
./tools/pitch doctor
./tools/test-surface run unit-vendor-onboarding
./tools/pitch smoke-best-effort
./tools/pitch verify-best-effort
```

## Read Next

1. [`install_matrix.md`](install_matrix.md)
2. [`repo_green_quickstart.md`](repo_green_quickstart.md)
3. [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md)
4. [`../packages/hla-vendor-pitch/docs/pitch_decision_tree.md`](../packages/hla-vendor-pitch/docs/pitch_decision_tree.md)
