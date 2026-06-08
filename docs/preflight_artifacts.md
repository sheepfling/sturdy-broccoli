# Preflight Artifacts

The `./certi-easy preflight` and `./pitch preflight` commands can emit either
human-readable output or machine-readable JSON.

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
- `next_steps`
- `exit_code`

Pitch JSON includes:

- `tool`
- `platform`
- `environment`
- `result`
- `checks`
- `next_step`
- `exit_code`

## What To Look For

- `environment: loopback-ok` means the local CERTI socket bind passed.
- `environment: loopback-blocked` means the host/session blocked loopback and
  CERTI smoke should be skipped.
- `environment: docker-blocked` means Pitch Docker is not ready yet.
- `environment: bundle-blocked` means the Pitch runtime bundle is missing or
  not extracted where the wrapper expects it.

If you want to understand the operator flow first, read:

- [Pitch Decision Tree](pitch_decision_tree.md)
- [CERTI Operator Runbook](certi_section8_runbook.md)
