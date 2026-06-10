# Vendor Runner Provisioning

This page is the explicit setup contract for dedicated vendor-runtime runners.

Use it when you are:

- bringing up a new GitHub Actions runner or equivalent host
- configuring repository or organization variables for real-runtime jobs
- debugging why `vendor_green` fails before the runtime starts

This document is narrower than
[vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md).
That guide explains the execution lanes. This page explains the runner state
they require.

For a copyable machine-readable template, see
[vendor_runner_provisioning_template.yaml](vendor_runner_provisioning_template.yaml).

## Scope

These jobs rely on dedicated real-runtime state:

- `certi-runtime-required`
- `pitch-runtime-required`
- `real-profile-matrix-required`
- `vendor-edge-matrix-required`
- `vendor-probe-stability-required`
- `vendor-runtime-smoke`

All of them now validate their state with:

```bash
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile ...
```

If that validator fails, treat it as runner provisioning drift, not as a
backend conformance result.

The template file mirrors the same profiles:

- `certi`
- `pitch`
- `matrix`
- `vendor-edge`
- `all`

The `vendor-edge-matrix-required` workflow currently fans out across these
explicit profile names:

- `time-query`
- `negotiated-ownership`
- `save-restore`
- `ddm`

The standalone `vendor-runtime-smoke` workflow currently fans out across these
explicit vendor-green profiles:

- `all`
- `./tools/certi-easy save-restore-probe`
- `./tools/certi-easy ddm-probe`
- `./tools/pitch save-restore-probe`
- `./tools/pitch ddm-probe`
- `./tools/pitch negotiated-probe`

Those rows do not all validate the same runner-state profile:

- `all` validates `--profile all`
- `./tools/certi-easy ...` rows validate `--profile certi`
- `./tools/pitch ...` rows validate `--profile pitch`

The `vendor-probe-stability-required` workflow currently fans out across these
repeated-run probe profiles:

- `certi-save-restore-probe`
- `pitch-negotiated-probe`
- `pitch-save-restore-probe`
- `pitch-ddm-probe`
- `certi-ddm-probe`

## CERTI

### Required Variables

Patched baseline:

- `HLA2010_CERTI_PATCHED_PREFIX`
- `HLA2010_CERTI_PATCHED_BUILD_ROOT`

Upstream baseline, when the profile compares baselines:

- `HLA2010_CERTI_UPSTREAM_PREFIX`
- `HLA2010_CERTI_UPSTREAM_BUILD_ROOT`

Compatibility mapping:

- the workflows also map `HLA2010_CERTI_PREFIX` to
  `HLA2010_CERTI_PATCHED_PREFIX`
- the workflows also map `HLA2010_CERTI_BUILD_ROOT` to
  `HLA2010_CERTI_PATCHED_BUILD_ROOT`

Do not provision only the compatibility variables. Provision the explicit
patched/upstream variables.

### Required Markers

Patched install:

- `${HLA2010_CERTI_PATCHED_PREFIX}/bin/rtig`

Patched build root:

- `${HLA2010_CERTI_PATCHED_BUILD_ROOT}/libRTI/ieee1516-2010`

Upstream install:

- `${HLA2010_CERTI_UPSTREAM_PREFIX}/bin/rtig`

Upstream build root:

- `${HLA2010_CERTI_UPSTREAM_BUILD_ROOT}/libRTI/ieee1516-2010`

### Minimum Validation

Patched-only runner:

```bash
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile certi --json
```

Matrix / vendor-edge runner:

```bash
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile matrix --json
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile vendor-edge --json
```

### Operational Expectation

- loopback socket bind/connect must be permitted for `127.0.0.1`
- patched and upstream installs must stay fixed between runs
- do not point these variables at ad hoc per-shell scratch paths

## Pitch

### Required Variables

- `HLA2010_PITCH_HOME`
- `HLA2010_PITCH_USER_HOME`

### Required Marker

- `${HLA2010_PITCH_HOME}/lib/prtifull.jar`

`HLA2010_PITCH_USER_HOME` should point at the persistent user-home owned by
the runner for the Docker-backed Pitch path.

### Minimum Validation

Pitch-only runner:

```bash
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile pitch --json
```

Shared matrix runner:

```bash
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile matrix --json
```

### Operational Expectation

- Docker daemon must be reachable
- the runner should use the repo Docker-backed path, not a mixed host-only setup
- the user-home path should be stable across runs

## GitHub Variables

The dedicated workflows currently read these GitHub Actions variables:

- `HLA2010_CERTI_PATCHED_PREFIX`
- `HLA2010_CERTI_PATCHED_BUILD_ROOT`
- `HLA2010_CERTI_UPSTREAM_PREFIX`
- `HLA2010_CERTI_UPSTREAM_BUILD_ROOT`
- `HLA2010_PITCH_HOME`
- `HLA2010_PITCH_USER_HOME`

If one of those is unset, the dedicated CI-state validator should fail before
`vendor_green` starts.

## Artifact Contract

Dedicated runner validation writes:

- `analysis/vendor_runtime_ci_state/<profile>/vendor_runtime_ci_state_summary.json`
- `analysis/vendor_runtime_ci_state/<profile>/vendor_runtime_ci_state_report.md`

Those artifacts now also restate the executable contract for the chosen
profile:

- required variables
- compatibility-variable mappings
- required marker paths

Treat that as the machine-readable runner-state contract for the profile, not
just as a pass/fail note.

Vendor preflight and status then continue with:

- `analysis/preflight_artifacts/`
- `analysis/vendor_runtime_status/`
- `analysis/vendor_parity_artifacts/`

Read those in this order:

1. CI state
2. preflight artifact
3. normalized runtime status
4. parity packet

That keeps runner misconfiguration separate from blocked host prerequisites and
separate again from actual vendor/runtime conformance failures.

## Recommended Bring-Up Order

1. Set the GitHub runner variables.
2. Confirm the required marker paths exist on the runner host.
3. Run `python3 scripts/ci/check_vendor_runtime_ci_state.py --profile ... --json`.
4. Run the matching preflight command:
   - `./tools/certi-easy preflight`
   - `./tools/pitch preflight`
5. Only then run the dedicated vendor job or `vendor_green` profile.
