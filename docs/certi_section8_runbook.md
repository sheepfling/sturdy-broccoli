# CERTI Section 8 Runbook

This runbook is for executing the real CERTI `§8` time-management matrix on a host that can start `rtig`, bind loopback sockets, and launch the configured CERTI runtime profiles.

## Preconditions

The host must satisfy all of these:

- local loopback bind/connect is allowed
- `rtig` is launchable
- the CERTI runtime profile is discoverable
- the Vendor Smoke FOM is present
- Python can start local REST/gRPC helper servers when needed

Run the preflight first:

```bash
python3 scripts/check_certi_preflight.py
```

Expected result on a runnable host:

- `CERTI install: available`
- `CERTI smoke FOM: available`
- `loopback bind: available`
- final result: `real CERTI runnable`

If the preflight reports `real CERTI will skip`, the matrix will not produce real-vendor evidence on that host.

## Environment

Enable the real-vendor suite:

```bash
export HLA2010_ENABLE_REAL_RTI_SMOKE=1
```

Optional profile-specific overrides:

```bash
export HLA2010_CERTI_BUILD_ROOT=/path/to/certi/build
export HLA2010_CERTI_PATCHED_BUILD_ROOT=/path/to/patched/build
export HLA2010_CERTI_UPSTREAM_BUILD_ROOT=/path/to/upstream/build
```

## Core Commands

Dedicated CERTI `§8` slice:

```bash
python3 -m pytest -q tests/vendors/test_certi_real_backend_matrix.py -k 'time_query_and_fqr_matrix or time_query_and_fqr_baseline or queued_fqr_baseline or time_semantic_profile_matches_across_native_and_java_facades'
```

Full CERTI backend matrix:

```bash
python3 -m pytest -q tests/vendors/test_certi_real_backend_matrix.py
```

Hosted Python `§8` matrix, for comparison:

```bash
python3 -m pytest -q tests/time/test_section8_backend_matrix.py
```

Regenerate compliance artifacts after the run:

```bash
python3 scripts/generate_compliance_artifacts.py
```

## Expected Outcomes

On a capable host:

- native CERTI rows should execute rather than skip
- `certi-jpype` and `certi-py4j` facade rows should execute if their bridge environments are configured
- `analysis/compliance/section8_backend_matrix.json` should continue to show CERTI rows as `env-gated-positive` unless you later promote the artifact model to session-aware pass/fail states

In a restricted host or sandbox:

- the real-vendor tests should skip cleanly
- the skip should be caused by backend unavailability or loopback bind restrictions, not a failure wall

## Troubleshooting

### Loopback bind is blocked

Symptom:

- preflight says `loopback bind: blocked`
- real CERTI tests skip immediately

Cause:

- the host cannot bind local TCP sockets needed by `rtig`

Action:

- rerun on a host/session with loopback socket permission

### CERTI runtime is not discoverable

Symptom:

- preflight cannot find the install or runtime profile

Action:

- set the appropriate `HLA2010_CERTI_*_BUILD_ROOT` or runtime-path environment variables
- verify the profile with the existing CERTI discovery tooling

### Upstream and patched profiles diverge

Symptom:

- one profile passes and the other raises `RTIinternalError`, transport errors, or ordering differences

Action:

- preserve both results
- treat the difference as vendor/profile evidence, not as a Python reference-backend regression

## Evidence Capture

After a successful real-vendor run, capture:

1. pytest output for the CERTI `§8` slice
2. regenerated [section8_backend_matrix.json](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/compliance/section8_backend_matrix.json)
3. regenerated [negative_path_completeness.json](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/compliance/negative_path_completeness.json)
4. any upstream/patched divergence notes

That set is the minimum evidence package for claiming real-vendor `§8` verification on a specific host.
