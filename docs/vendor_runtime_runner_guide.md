# Vendor Runtime Runner Guide

This guide is the supported path for running real CERTI and Pitch runtime
checks when the host matters.

Use it when:

- `./certi-easy preflight` reports `environment: loopback-blocked`
- `./pitch preflight` reports `environment: docker-blocked`
- you need stable real-runtime evidence rather than repo-green coverage
- you are configuring CI runners for vendor runtime proof

The key split is simple:

- `./scripts/ci/repo_green.sh`: repo-green, vendor preflight mandatory, blocked
  vendor runtime prerequisites skip cleanly
- `./scripts/ci/vendor_green.sh ...`: vendor-green, vendor preflight mandatory,
  blocked prerequisites fail immediately

## Supported Execution Surfaces

### 1. Unsandboxed local terminal

Use this when you want a direct local rerun on the same machine that owns the
vendor installs or Docker state.

Minimum expectation:

- loopback bind/connect is permitted for CERTI
- Docker Desktop or equivalent Docker daemon access is permitted for Pitch
- the repo-managed `.venv` is available

### 2. Dedicated CI runner

Use this when you want stable repeatable vendor runtime proof in automation.

Minimum expectation:

- fixed CERTI upstream/patched prefixes are already provisioned
- Pitch uses the repo Docker-backed route, not mixed host/runtime variants
- Java is installed
- Python 3.12 and the repo test extras are installed

## Local Sequence

### Repo-green

Use this for the default full verification lane:

```bash
./bootstrap python
source .venv/bin/activate
./scripts/ci/repo_green.sh
```

Expected behavior:

- pure-Python and repo-owned checks run normally
- vendor runtime routes still preflight first
- blocked vendor prerequisites do not fail the whole lane

### CERTI vendor-green

```bash
./bootstrap python
source .venv/bin/activate

./certi-easy preflight
./certi-easy install
./scripts/ci/vendor_green.sh certi
./scripts/ci/vendor_green.sh certi-compare
```

Use `./certi-easy smoke compare` when you want the top-level operator route for
patched-vs-upstream attribution.

### Pitch vendor-green

```bash
./bootstrap python
source .venv/bin/activate

./pitch preflight
./pitch install
./scripts/ci/vendor_green.sh pitch
```

Use `./pitch smoke` and `./pitch verify` for the top-level operator path.

## Required State

### CERTI

The supported state is machine-readable fixed prefixes/build roots, for example:

- `HLA2010_CERTI_PREFIX`
- `HLA2010_CERTI_BUILD_ROOT`
- `HLA2010_CERTI_UPSTREAM_PREFIX`
- `HLA2010_CERTI_UPSTREAM_BUILD_ROOT`

Prefer repo-managed local state over ad hoc shell-session paths.

### Pitch

The supported state is the repo Docker-backed route:

- `HLA2010_PITCH_HOME`
- `HLA2010_PITCH_USER_HOME`
- Docker daemon reachable
- required ports available or already owned by the managed container

Do not treat mixed host-only and Docker-backed Pitch setups as the supported
baseline.

## Preflight Artifacts

Archive the preflight JSON on every vendor-green run.

Minimum useful artifact set:

- loopback availability
- Docker availability
- vendor home/prefix presence
- required port status

Commands:

```bash
mkdir -p analysis/preflight_artifacts

./certi-easy preflight --json-file analysis/preflight_artifacts/certi-preflight.json
./pitch preflight --json-file analysis/preflight_artifacts/pitch-preflight.json
```

Or let the vendor-green path emit the same files automatically:

```bash
./scripts/ci/vendor_green.sh matrix
```

## CI Mapping

The repo workflows use the same split:

- `repo-green` job -> `./scripts/ci/repo_green.sh`
- vendor runtime jobs -> `./scripts/ci/vendor_green.sh ...`

That is the supported contract. Treat
`./scripts/ci/vendor_runtime_smoke.sh ...` as the shared implementation behind
the vendor-green lane, not the preferred top-level job interface.

## What This Does Not Solve

This guide improves repeatability. It does not change current vendor/runtime
conformance limits.

Known remaining non-repo gaps include:

- CERTI real-runtime proof outside the promoted slices
- Pitch negotiated ownership parity
- non-Python save/restore gaps
- non-Python DDM gaps

Those should be treated as vendor/runtime coverage limits unless new executable
evidence proves otherwise.
