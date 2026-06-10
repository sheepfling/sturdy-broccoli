# Preflight Artifacts

The `./certi-easy preflight` and `./pitch preflight` commands can emit either
human-readable output or machine-readable JSON.

The CI/operator wrapper `./scripts/ci/vendor_runtime_smoke.sh` now emits the
same standard JSON files by default under `analysis/preflight_artifacts/`
before it decides whether a vendor profile should run or skip. Use
`./scripts/ci/vendor_green.sh` when blocked prerequisites should fail the run
instead of short-circuiting cleanly.

Use the JSON form when you want to:

- branch in scripts or CI
- archive the preflight state as a file
- compare preflight results between machines or sessions

## Copy-Paste Workflow

If you just want the shortest repeatable path, use this:

```bash
mkdir -p analysis/preflight_artifacts

./certi-easy preflight --json-file analysis/preflight_artifacts/certi-preflight.json
python3 -m json.tool analysis/preflight_artifacts/certi-preflight.json

./pitch preflight --json-file analysis/preflight_artifacts/pitch-preflight.json
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
./certi-easy preflight --json-file certi-preflight.json
```

Print JSON to stdout:

```bash
./certi-easy preflight --json
```

Inspect the file:

```bash
python3 -m json.tool certi-preflight.json
jq . certi-preflight.json
```

## Pitch

Write a JSON options file:

```bash
./pitch preflight --json-file=pitch-preflight.json
```

Print JSON to stdout:

```bash
./pitch preflight --json
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
- `next_steps`
- `exit_code`

Pitch JSON includes:

- `tool`
- `platform`
- `environment`
- `result`
- `checks`
- `runtime`
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
