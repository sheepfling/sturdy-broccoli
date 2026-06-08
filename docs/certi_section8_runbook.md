# CERTI Operator Runbook

This is the one-page operator guide for CERTI in this workspace.

Use it when you want the shortest path from a fresh checkout to a runnable
pristine-vs-patched comparison, and when you need to understand the main
runtime quirks without reading the deeper parity notes first.

## The Short Version

Run these commands first:

```bash
./certi-easy preflight
./certi-easy install
./certi-easy doctor
./certi-easy smoke compare
```

Meaning:

- `install` bootstraps Python, builds the repo-local patched CERTI, and clones
  plus builds pristine upstream CERTI.
- `doctor` prints the active paths and tells you whether real CERTI smoke can
  run on this host.
- `smoke compare` runs the stable upstream-vs-patched CERTI comparison slices.

If those commands work, the basic CERTI path is good.

## The Two Baselines

There are two CERTI baselines you should keep separate:

- `certi-upstream`
  pristine/original CERTI cloned from GitHub
- `certi-patched`
  the repo-local vendored CERTI with the current local fixes

Use `certi-upstream` when you want to answer "does original CERTI do this?"
Use `certi-patched` when you want to answer "did our local CERTI changes alter
the result?"

The smoke compare route intentionally compares both baselines on the same
stable slices.

## What Is Easy

These are the easy, junior-friendly entrypoints:

```bash
./certi-easy preflight
./certi-easy install
./certi-easy doctor
./certi-easy smoke compare
./certi-easy smoke patched
./certi-easy smoke upstream
./certi-easy run patched rtig -v 0
./certi-easy run upstream rtig -v 0
```

If you only remember one thing, remember `./certi-easy`.

`./certi-easy doctor` is the same path shape as `preflight`, but with the
installed paths printed first so you can see what it is about to use.

## What Is Secondary

The lower-level scripts still exist, but they are for targeted debugging and
matrix work:

- `scripts/rebuild_certi.sh`
- `scripts/rebuild_certi_upstream.sh`
- `scripts/ci/vendor_runtime_smoke.sh`

Use those when you are drilling into one baseline or one clause family.

## Interface And Transport Shape

The real CERTI surface in this repo is still the native HLA 1516.1-2010 RTI
path.

- `certi` is the native smoke backend
- `certi-jpype` and `certi-py4j` are Java-profile adapters over the same native
  CERTI runtime
- `rest` and `grpc` are transport surfaces used for proving hosted Python RTI
  behavior, not separate vendor RTIs

The current remote callback contract is polling-based, not streaming-based.
Callbacks are drained through the ordinary `evokeCallback` and
`evokeMultipleCallbacks` style services.

## Known Quirks

These are the runtime facts that matter most for day-to-day use:

- upstream CERTI still fails earlier than patched CERTI on the promoted time
  and ownership compare slices
- patched CERTI is good enough for the stable smoke contract, but negotiated
  ownership still has a known non-smoke matrix gap
- `confirmDivestiture` and `attributeOwnershipDivestitureIfWanted` are not the
  same thing at the 2010 surface, but the patched branch still shares some
  release-response machinery under the hood
- real CERTI runs require loopback socket permission on `127.0.0.1`

## If Smoke Fails

Run the preflight first:

```bash
./certi-easy preflight
```

If the result says `real CERTI will skip`, the problem is the host/session, not
the tests.

If `./certi-easy preflight` reports `environment: loopback-blocked`, this is a
Codex/session restriction rather than a repo bug. Use an unrestricted local
terminal or an approved unsandboxed command to retest.

For scripts or CI, `./certi-easy preflight --json` emits machine-readable
status with `environment`, `result`, and per-check records. To write a file
you can inspect or archive, use `./certi-easy preflight --json-file ...`.

For file output and inspection examples, see
[Preflight Artifacts](preflight_artifacts.md).

If the result says `real CERTI runnable` but `smoke compare` still fails:

1. check whether the failure is on `certi-upstream` or `certi-patched`
2. compare it against [docs/certi_runtime_limitations.md](docs/certi_runtime_limitations.md)
3. use [docs/certi_spec_traceability.md](docs/certi_spec_traceability.md)
   for the clause-level evidence trail

## Deeper Matrix Work

When you need the full Section 8 and ownership evidence, use the deeper
matrices instead of the easy path:

```bash
python3 -m pytest -q tests/time/test_section8_backend_matrix.py
python3 -m pytest -q tests/vendors/test_certi_real_backend_matrix.py
python3 -m pytest -q tests/vendors/test_certi_real_backend_ownership_matrix.py
./scripts/ci/section8_backend_matrix_gate.sh
```

Those are not the first commands a junior should start with.
