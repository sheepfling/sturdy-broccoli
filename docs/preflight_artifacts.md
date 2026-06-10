# Preflight Artifacts

The `./scripts/certi_easy.sh preflight` and `./scripts/pitch_docker_easy.sh preflight` commands can emit either
human-readable output or machine-readable JSON.

The CI/operator wrapper `./scripts/ci/vendor_runtime_smoke.sh` now emits the
same standard JSON files by default under `analysis/preflight_artifacts/`
before it decides whether a vendor profile should run or skip. Use
`./scripts/ci/vendor_green.sh` when blocked prerequisites should fail the run
instead of short-circuiting cleanly.

Those persisted files are now also the cross-command proof that preflight
already succeeded for direct real-runtime pytest diagnostics. The wrapper path
still remains the supported first step.

That proof is intentionally strict now: direct vendor pytest only accepts a
recent artifact whose `tool`, `environment`, `result`, and `exit_code` all
match a successful supported preflight outcome. By default the artifact must be
no more than 12 hours old. Override that age window with
`HLA2010_PREFLIGHT_MAX_AGE_SECONDS` if an operator or CI lane needs a different
retention policy.

Use the JSON form when you want to:

- branch in scripts or CI
- archive the preflight state as a file
- compare preflight results between machines or sessions

## Copy-Paste Workflow

If you just want the shortest repeatable path, use this:

```bash
mkdir -p analysis/preflight_artifacts

./scripts/certi_easy.sh preflight --json-file analysis/preflight_artifacts/certi-preflight.json
python3 -m json.tool analysis/preflight_artifacts/certi-preflight.json

./scripts/pitch_docker_easy.sh preflight --json-file analysis/preflight_artifacts/pitch-preflight.json
python3 -m json.tool analysis/preflight_artifacts/pitch-preflight.json
```

If `jq` is installed, it can inspect the same files too:

```bash
jq . analysis/preflight_artifacts/certi-preflight.json
jq . analysis/preflight_artifacts/pitch-preflight.json
```

If you want to keep a dated snapshot, copy the files into a timestamped
folder:

```bash
stamp="$(date +%Y%m%d-%H%M%S)"
mkdir -p "analysis/preflight_artifacts/$stamp"
cp analysis/preflight_artifacts/certi-preflight.json "analysis/preflight_artifacts/$stamp/"
cp analysis/preflight_artifacts/pitch-preflight.json "analysis/preflight_artifacts/$stamp/"
```

## CERTI

Write a JSON options file:

```bash
./scripts/certi_easy.sh preflight --json-file certi-preflight.json
```

Print JSON to stdout:

```bash
./scripts/certi_easy.sh preflight --json
```

Inspect the file:

```bash
python3 -m json.tool certi-preflight.json
jq . certi-preflight.json
```

## Pitch

Write a JSON options file:

```bash
./scripts/pitch_docker_easy.sh preflight --json-file=pitch-preflight.json
```

Print JSON to stdout:

```bash
./scripts/pitch_docker_easy.sh preflight --json
```

Inspect the file:

```bash
python3 -m json.tool pitch-preflight.json
jq . pitch-preflight.json
```

## Expected Fields

CERTI JSON includes:

- `tool`
- `environment`
- `result`
- `checks`
- `runtime_profiles`
- `required_markers`
- `next_steps`
- `exit_code`

Pitch JSON includes:

- `tool`
- `platform`
- `environment`
- `result`
- `checks`
- `runtime`
- `required_markers`
- `ports`
- `next_step`
- `exit_code`

## What To Look For

- `environment: loopback-ok` means the local CERTI socket bind passed.
- `environment: loopback-blocked` means the host/session blocked loopback and
  CERTI smoke should be skipped.
- `environment: docker-blocked` means Pitch Docker is not ready yet.
- `environment: bundle-blocked` means the Pitch runtime bundle is missing or
  not extracted where the wrapper expects it.
- `environment: ports-blocked` means one or more required local Pitch ports are
  already occupied by another process.

The richer payloads also make the selected runtime state explicit:

- CERTI `runtime_profiles` records the active, patched, and upstream path roots
  plus whether the expected markers exist.
- Pitch `runtime` records the selected runtime home, user-home, image name, and
  container name.
- Pitch `ports` records the expected local CRC and FedPro bindings and whether
  they are available, blocked, or already managed by the expected container.

If you want to understand the operator flow first, read:

- [Pitch Decision Tree](../packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md)
- [CERTI Operator Runbook](../packages/hla2010-rti-certi/docs/certi_section8_runbook.md)

## Classifying The Artifacts

Use the shared classifier when you want the repo to distinguish:

- `repo-green`: blocked vendor prerequisites are nonfatal
- `vendor-green`: blocked vendor prerequisites fail immediately

Examples:

```bash
python3 scripts/classify_vendor_runtime.py --lane repo-green --json
python3 scripts/classify_vendor_runtime.py --lane vendor-green --vendor certi --json
python3 scripts/classify_vendor_runtime.py --lane vendor-green --vendor pitch --json
```

By default the script reads:

- `analysis/preflight_artifacts/certi-preflight.json`
- `analysis/preflight_artifacts/pitch-preflight.json`

and writes:

- `analysis/vendor_runtime_status/vendor_runtime_status_summary.json`
- `analysis/vendor_runtime_status/vendor_runtime_status_report.md`

The classifier normalizes each vendor into one of:

- `ready`
- `environment-blocked`
- `missing-artifact`
- `unexpected-preflight-failure`

The normalized status artifact now also carries:

- `blocked_reason`: primary failed prerequisite name, when one is known
- `blocked_checks`: failed check records copied into a stable shared shape
- `recommended_next_steps`: per-vendor next actions extracted from the raw preflight payload

That gives CI and local scripts one machine-readable answer about whether the
next step is:

- proceed with vendor runtime work
- rerun on a host with the required runtime surface
- or fix a broken preflight path

For dedicated vendor CI runners, pair that with:

```bash
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile certi --json
python3 scripts/ci/check_vendor_runtime_ci_state.py --profile pitch --json
```

Those dedicated-runner artifacts live under:

- `analysis/vendor_runtime_ci_state/...`
