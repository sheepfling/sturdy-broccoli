# Vendor Runtime Runner Guide

This guide is the supported path for running real CERTI and Pitch runtime
checks when the host matters.

Use it when:

- `./tools/certi-easy preflight` reports `environment: loopback-blocked`
- `./tools/pitch preflight` reports `environment: docker-blocked`
- you need stable real-runtime evidence rather than repo-green coverage
- you are configuring CI runners for vendor runtime proof

If you need the explicit variable and marker checklist for those runners, use
[vendor_runner_provisioning.md](vendor_runner_provisioning.md).

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

The dedicated jobs now validate that runtime state explicitly before
`vendor-green` runs. That validation is not advisory; treat it as the supported
runner provisioning contract.

## Local Sequence

### Repo-green

Use this for the default full verification lane:

```bash
./scripts/bootstrap_profile.sh python
source .venv/bin/activate
./scripts/ci/repo_green.sh
```

Expected behavior:

- pure-Python and repo-owned checks run normally
- vendor runtime routes still preflight first
- blocked vendor prerequisites do not fail the whole lane

Direct real-runtime pytest invocation is not the supported first step anymore.
Use the vendor operator path so preflight is confirmed before the runtime tests
start:

- CERTI: `./tools/certi-easy ...`
- Pitch: `./tools/pitch ...`

### CERTI vendor-green

```bash
./scripts/bootstrap_profile.sh python
source .venv/bin/activate

./tools/certi-easy preflight
./tools/certi-easy install
./scripts/ci/vendor_green.sh certi
./scripts/ci/vendor_green.sh certi-compare
```

Use `./tools/certi-easy smoke compare` when you want the top-level operator route for
patched-vs-upstream attribution.

### Pitch vendor-green

```bash
./scripts/bootstrap_profile.sh python
source .venv/bin/activate

./tools/pitch preflight
./tools/pitch install
./tools/pitch smoke
./tools/pitch verify
```

Underlying shared strict profiles:

```bash
./scripts/ci/vendor_green.sh pitch-smoke
./scripts/ci/vendor_green.sh pitch-verify
./scripts/ci/vendor_green.sh pitch
```

## Required State

### CERTI

The supported state is machine-readable fixed prefixes/build roots, for example:

- `HLA2010_CERTI_PATCHED_PREFIX`
- `HLA2010_CERTI_PATCHED_BUILD_ROOT`
- `HLA2010_CERTI_UPSTREAM_PREFIX`
- `HLA2010_CERTI_UPSTREAM_BUILD_ROOT`

Prefer repo-managed local state over ad hoc shell-session paths.

Required markers on dedicated runners:

- patched prefix: `bin/rtig`
- patched build root: `libRTI/ieee1516-2010`
- upstream prefix: `bin/rtig`
- upstream build root: `libRTI/ieee1516-2010`

The dedicated CI jobs map `HLA2010_CERTI_PREFIX` /
`HLA2010_CERTI_BUILD_ROOT` to the patched baseline for compatibility, but the
provisioning contract is the explicit patched/upstream variable set above.

### Pitch

The supported state is the repo Docker-backed route:

- `HLA2010_PITCH_HOME`
- `HLA2010_PITCH_USER_HOME`
- Docker daemon reachable
- required ports available or already owned by the managed container

Do not treat mixed host-only and Docker-backed Pitch setups as the supported
baseline.

Required marker on dedicated runners:

- `HLA2010_PITCH_HOME/lib/prtifull.jar`

Pitch preflight now treats that jar as the required runtime-home marker, not
just the presence of the runtime directory.

`HLA2010_PITCH_USER_HOME` should point at the persistent user-home location
that the dedicated runner owns for the Docker-backed Pitch flow.

## Dedicated CI Provisioning

Use the validator directly when you are bringing up or repairing dedicated
vendor runners:

```bash
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile certi --json
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile pitch --json
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile matrix --json
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile vendor-edge --json
```

Profiles:

- `certi`: patched CERTI-only runner state
- `pitch`: Pitch-only runner state
- `matrix`: patched + upstream CERTI plus Pitch state
- `vendor-edge`: the same explicit state as `matrix`

Artifacts emitted by that validator:

- `analysis/vendor_runtime_ci_state/<profile>/vendor_runtime_ci_state_summary.json`
- `analysis/vendor_runtime_ci_state/<profile>/vendor_runtime_ci_state_report.md`

Those artifacts are now uploaded by the dedicated GitHub Actions vendor jobs
alongside the existing preflight, runtime-status, and parity artifacts.

The strict wrapper now also defends itself when it runs under CI:

- `./scripts/ci/vendor_green.sh ...` auto-runs `check_vendor_runtime_ci_state.py`
  for the profile it needs before it tries the real runtime lane
- if the dedicated runner contract is broken, the wrapper fails before it
  touches the vendor runtime delegate path
- this keeps misconfigured CI jobs from looking like runtime/test failures when
  the real issue is missing vendor state

The dedicated `vendor-edge` job now runs these explicit profiles rather than
one broad catch-all path:

- `time-query`
- `negotiated-ownership`
- `save-restore`
- `ddm`

The standalone `vendor-runtime-smoke` workflow also now fans out across the
explicit probe packet instead of only running one broad `all` command:

- `all`
- `./tools/certi-easy save-restore-probe`
- `./tools/certi-easy ddm-probe`
- `./tools/pitch save-restore-probe`
- `./tools/pitch ddm-probe`
- `./tools/pitch negotiated-probe`

Each row now validates only the runtime-state profile it actually needs before
running:

- `all` -> `check_vendor_runtime_ci_state.py --profile all`
- `./tools/certi-easy ...` rows -> `--profile certi`
- `./tools/pitch ...` rows -> `--profile pitch`

The dedicated repeated-run stability workflow currently fans out across:

- `certi-save-restore-probe`
- `pitch-negotiated-probe`
- `pitch-save-restore-probe`
- `pitch-ddm-probe`
- `certi-ddm-probe`

When a probe looks promising and you need promotion-quality repetition
evidence, use the repeated-run harness on the dedicated runner:

```bash
./tools/pitch negotiated-review 5
./tools/pitch ddm-review 5
./tools/certi-easy ddm-review 5
```

Underlying shared wrapper:

```bash
./scripts/ci/vendor_probe_review.sh <profile> 5
```

Under CI, the repeated-run path now validates the dedicated runner contract
once before it starts the repetition loop. If the runner is missing explicit
CERTI or Pitch state, the wrapper fails before it spends time collecting
misleading repeated-run artifacts. The inner `vendor_green` calls in that loop
then run with redundant CI-state validation disabled for that one process tree.

Artifacts:

- `analysis/vendor_probe_stability/<profile>/vendor_probe_stability_summary.json`
- `analysis/vendor_probe_stability/<profile>/vendor_probe_stability_report.md`

Those artifacts now include a small promotion-readiness assessment:

- `unstable`: at least one attempt failed
- `needs-more-runs`: the slice stayed green, but below the current five-run floor
- `candidate`: repeated-run stability evidence is present; parity promotion still needs clause-level review

To compare those repeated-run results against the repo’s current documented
conformance stance, generate the promotion-review artifact:

```bash
python3 scripts/ci/write_vendor_probe_promotion_review.py
```

Artifacts:

- `analysis/vendor_probe_promotion_review/vendor_probe_promotion_review_summary.json`
- `analysis/vendor_probe_promotion_review/vendor_probe_promotion_review_report.md`

The dedicated repeated-run CI job now writes and uploads that promotion-review
artifact automatically after the stability packet refresh.

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

./tools/certi-easy preflight --json-file analysis/preflight_artifacts/certi-preflight.json
./tools/pitch preflight --json-file analysis/preflight_artifacts/pitch-preflight.json
```

Or let the vendor-green path emit the same files automatically:

```bash
./scripts/ci/vendor_green.sh matrix
```

After the artifacts exist, classify them explicitly:

```bash
python3 scripts/classify_vendor_runtime.py --lane repo-green --json
python3 scripts/classify_vendor_runtime.py --lane vendor-green --vendor certi --json
python3 scripts/classify_vendor_runtime.py --lane vendor-green --vendor pitch --json
```

Use that output to separate:

- blocked host/runtime prerequisites
- missing or broken preflight artifacts
- ready vendors that should proceed into runtime smoke or matrix slices

The normalized status summary now also records:

- the primary blocked prerequisite name
- the failed check details for each vendor
- the next recommended operator steps copied from the vendor preflight payload

## Teardown Expectations

The supported real-runtime smoke/probe paths now treat cleanup as part of the
contract, not as a best-effort afterthought.

At minimum, a supported vendor path should leave behind:

- closed RTI client handles
- terminated runtime processes
- no remaining listener on the runtime TCP port that the probe started

Current smoke/probe tests now assert that runtime teardown actually completes
for the launched CERTI `rtig` and Pitch runtime processes. If a probe passes
its service assertions but leaves the runtime process or listener alive, treat
that as a runtime-reliability failure and fix it before promoting the slice.

The green-lane wrappers also emit these report directories automatically:

- `analysis/vendor_runtime_ci_state/...` on dedicated vendor CI jobs
- `analysis/vendor_runtime_status/...`
- `analysis/vendor_parity_artifacts/...`

So a normal `./scripts/ci/repo_green.sh` or `./scripts/ci/vendor_green.sh ...`
run now leaves behind both the raw preflight JSON and a normalized status view.
The supported top-level operator routes such as `./tools/certi-easy ...` and
`./tools/pitch ...` are expected to leave behind the same diagnostic bundle through
their delegated `vendor_green` paths, even when preflight blocks the real
runtime from running.

## CI Mapping

The repo workflows use the same split:

- `repo-green` job -> `./scripts/ci/repo_green.sh`
- vendor runtime jobs -> `./scripts/ci/vendor_green.sh ...`

Those jobs also upload:

- `analysis/preflight_artifacts/`
- `analysis/vendor_runtime_ci_state/`
- `analysis/vendor_runtime_status/`
- `analysis/vendor_parity_artifacts/`

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

For a compact promoted-vs-blocked-vs-conformance map, see
[vendor_runtime_gap_map.md](vendor_runtime_gap_map.md).
