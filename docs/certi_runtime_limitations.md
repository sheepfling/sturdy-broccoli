# CERTI Runtime Limitations

This note records known gaps and divergences in the CERTI-backed runtime path
used by this repository.

## Easy Path

If you want the simplest operator flow:

```bash
./certi-easy install
./certi-easy doctor
./certi-easy smoke compare
```

That one wrapper handles:

- Python bootstrap
- patched local CERTI build/install
- pristine upstream CERTI clone/build/install
- the promoted upstream-vs-patched compare run

## Which CERTI Are We Comparing?

There are now three distinct CERTI meanings in this repository. Do not collapse
them when recording evidence.

| Name | Meaning | Intended use |
|---|---|---|
| `certi` / active default | Whatever `discover_certi_runtime()` resolves from the normal environment and repo-local install paths | local development and existing smoke tests |
| `certi-upstream` | An unmodified upstream/original CERTI install selected by `HLA2010_CERTI_UPSTREAM_PREFIX` or `HLA2010_CERTI_ORIGINAL_PREFIX` | vendor baseline; answers "does original CERTI do this?" |
| `certi-patched` | The repo-local vendored/patched CERTI build, or an explicit patched install selected by `HLA2010_CERTI_PATCHED_PREFIX` | answers "did our CERTI source modifications change this?" |

The default `hla-2010` real-runtime tests still compare the Python RTI reference
path against the active default runtime. In this workspace that usually means
the repo-local vendored CERTI build, not a pristine upstream install.

Default discovery order:

- `HLA2010_CERTI_PREFIX`, if set
- repo-local `CERTI-install/`
- libraries from `HLA2010_CERTI_BUILD_ROOT`, if set
- repo-local `CERTI-build/` as a build-overlay library source

The normal local rebuild path is:

```bash
./scripts/rebuild_certi.sh
```

That script builds from `CERTI/` by default. Since `CERTI/` is vendored source
in this repository, parity rows marked as CERTI evidence should be read as
"current repo-local CERTI build evidence" unless the test command explicitly
sets `HLA2010_CERTI_SOURCE`, `HLA2010_CERTI_PREFIX`, or
`HLA2010_CERTI_BUILD_ROOT` to an external pristine install.

For upstream-baseline comparison, run the dedicated baseline probe or the same
real-runtime matrix with upstream variables pointed at an unmodified CERTI
checkout/build/install and record the result separately. Do not mix upstream
baseline results with repo-local patched-build results in the same matrix row.

```bash
HLA2010_CERTI_UPSTREAM_PREFIX=/path/to/original/certi-install \
HLA2010_ENABLE_REAL_RTI_SMOKE=1 \
python3 -m pytest -q tests/vendors/test_certi_real_backend_matrix.py -k upstream_vs_patched
```

The upstream selector intentionally does not fall back to repo-local
`CERTI-build/` libraries. If upstream needs a build overlay, set
`HLA2010_CERTI_UPSTREAM_BUILD_ROOT` explicitly.

For the patched baseline, either use the repo-local default or set:

```bash
HLA2010_CERTI_PATCHED_PREFIX=/path/to/patched/certi-install \
HLA2010_CERTI_PATCHED_BUILD_ROOT=/path/to/patched/certi-build
```

The current upstream GitHub baseline was cloned from
`https://github.com/etopzone/CERTI.git` at commit
`d6b48f36d8116703affd4163b5bed95864377d5e`.

## Runnable Routes

Use these as the standard operator commands for CERTI evidence:

```bash
./scripts/rebuild_certi.sh
./scripts/rebuild_certi_upstream.sh
./scripts/ci/vendor_runtime_smoke.sh certi-patched
./scripts/ci/vendor_runtime_smoke.sh certi-upstream
./scripts/ci/vendor_runtime_smoke.sh certi-compare
```

Route meaning:

- `certi-patched` runs the repo-local vendored/patched CERTI build and the
  broader patched runtime matrix.
- `certi-upstream` runs the pristine upstream baseline slice only.
- `certi-compare` runs the same promoted baseline slices against both named
  baselines so failures can be attributed to original CERTI versus repo-local
  source changes. The current promoted slices are:
  - time-query / `flushQueueRequest`
  - negotiated ownership end-to-end
  - release-request branch separation for `deny`, `confirm`, and `ifwanted`

Session prerequisite:

- These commands only produce real runtime evidence when local loopback TCP
  bind/connect is permitted for `127.0.0.1`.
- In sessions where that preflight fails, the compare route skips with:
  `Local socket bind is not permitted for 127.0.0.1. Run python3 scripts/check_certi_preflight.py to verify local CERTI prerequisites.`
- That skip is an execution-environment limitation, not a CERTI baseline result.

Current named-baseline outcome from the runnable compare route
`./scripts/ci/vendor_runtime_smoke.sh certi-compare`:

- `certi-upstream`:
  - federation create/join succeeds, but the first `queryGALT` tears down the
    RTIA path with `Network Read Error waiting RTI reply` or
    `LAST message type should not be used!!`, depending on the logical-time
    profile
  - the negotiated-ownership compare probe does not complete successfully; the
    upstream baseline still fails on the ownership path with an RTI internal
    error instead of reaching the patched branch semantics
  - the release-request `deny`, `confirm`, and `ifwanted` compare probes also
    fail before stable branch semantics can be observed
- `certi-patched`: the same two-federate baseline reaches `queryGALT`,
  `queryLITS`, `enableTimeRegulation`, and `enableTimeConstrained`; after that
  the runtime now accepts `flushQueueRequest`, returns the current lookahead in
  the promoted no-queued baseline, and in the queued-FQR slice now delivers
  queued updates in timestamp order and grants at the earliest queued
  timestamp.
- `certi-patched` also now has fail-fast real-runtime probes for
  `timeAdvanceRequestAvailable`, `nextMessageRequest`, and
  `nextMessageRequestAvailable`:
  - `timeAdvanceRequestAvailable` returns a prompt grant in the equal-GALT
    available case
  - `nextMessageRequest` returns prompt earliest-queued grants in the promoted
    timestamp-ordered slice
  - `nextMessageRequestAvailable` now returns prompt earliest-queued grants in
    the same promoted timestamp-ordered slice after fixing the RTIA
    `nextEventRequestAvailable(...)` success-path guard
- `certi-patched` also completes the negotiated-ownership compare probe end to
  end, including assumption callback delivery, release request, cancellation
  confirmation, transfer via `attributeOwnershipDivestitureIfWanted`, and final
  ownership query callback.
- `certi-patched` release-request branch split:
  - `deny`: owner retains ownership and no acquisition notification is sent
  - `confirm`: rejected on the release-request path as
    `AttributeDivestitureWasNotRequested`
  - `ifwanted`: transfer succeeds through the release-response path
- `certi-patched` negotiated confirm path:
  - negotiated divestiture offer remains active until the owner confirms
  - `confirmDivestiture` now transfers only after a real
    `requestDivestitureConfirmation` callback
  - the resulting acquisition notification now carries the owner-supplied
    confirm tag end to end

## Current Shortfalls

| Area | Status | Evidence / Rationale |
|---|---|---|
| upstream `queryGALT` / `queryLITS` probe | Upstream runtime shortfall | The pristine upstream baseline creates and joins the two-federate smoke federation, but the first `queryGALT` tears down the RTIA path with either `libRTI: Network Read Error waiting RTI reply` or `LAST message type should not be used!!`, depending on the time profile. The patched baseline reaches later time-query/FQR assertions under the same Python helper scenario. |
| `flushQueueRequest` | Patched baseline matches promoted proof slice | Patched CERTI 1516-2010 no longer throws for this service, the promoted real-runtime baselines now prove queued ordering/grant semantics for the exercised attribute path, and the Python-facing adapter now normalizes integer-time callback typing so the promoted `§8.12` path reports the correct logical-time type to the federate surface. |
| `queryGALT` / `queryLITS` | Semantic divergence | Python reference returns invalid `TimeQueryReturn` when no regulating federate contributes. CERTI returns valid infinity before regulation is enabled, then the current lookahead after the current two-federate regulation/constraint setup. Matrix rows remain `partial` until this is normalized or explained clause-by-clause. |
| `timeAdvanceRequestAvailable` | Patched baseline proved | The helper command is now exercised behind a subprocess timeout harness. The patched real-runtime matrix proves a prompt equal-GALT available-grant and checks the logical-time type on the Python-facing callback path. |
| `nextMessageRequest` | Patched baseline proved | The helper command is exercised behind the same fail-fast harness. The patched real-runtime matrix proves earliest-queued grants with timestamp-ordered delivery on the promoted timestamped object slice and checks the logical-time type on the Python-facing callback path. |
| `nextMessageRequestAvailable` | Patched baseline proved | The helper command is now exercised behind the same fail-fast harness as `nextMessageRequest`. After fixing the RTIA `nextEventRequestAvailable(...)` success-path guard, the patched real-runtime matrix proves earliest-queued grants with timestamp-ordered delivery on the promoted timestamped object slice and checks the logical-time type on the Python-facing callback path. |
| `confirmDivestiture` | Patched local behavior, not clean upstream parity | The local patched branch now enforces negotiated-divestiture preconditions and preserves the confirm-tag callback surface, but it still reuses CERTI's release-response transfer machinery rather than adding a fully separate vendor-native implementation. |
| `attributeOwnershipReleaseDenied` | Patched local behavior | Upstream 2010 client code did not originally implement this service. The repo-local patched path can exercise the direct deny flow, but this should not be represented as upstream CERTI behavior. |
| `attributeOwnershipDivestitureIfWanted` | Partial semantic parity | Direct transfer works in the patched local branch and remains distinct from release-request `confirm`, but it still shares the same underlying release-response transfer machinery once the owner has chosen to grant transfer. |
| `cancelAttributeOwnershipAcquisition` / cancellation confirmation | Partial | Callback plumbing exists and unit coverage exists; real negotiated cancellation remains narrower than the Python reference path. |
| save/restore management | Not yet real-matrix proved | Python reference has executable save/restore coverage, but the CERTI real backend matrix does not yet cover the same clause family. |
| DDM region services | Not yet real-matrix proved | Python reference covers the current DDM rows; no equivalent CERTI real-runtime region matrix is wired yet. |

## Classification Rules

- Use `yes` only when an executable matrix test proves the behavior in the
  current workspace.
- Use `partial` when the runtime returns behavior but semantics diverge from the
  Python reference path or are narrower than the clause.
- Use `probe-fails` when the service is wired and an executable test proves a
  concrete runtime failure.
- Use `no` when no real backend-neutral runtime path is wired or exercised.
- Use `blocked` for runtime families that cannot currently be activated, such
  as Pitch in this workspace.

## Practical Direction

- Keep the pure Python RTI as the spec-reference implementation for clause
  semantics.
- Keep CERTI parity rows honest by separating current repo-local patched CERTI
  evidence from pristine upstream CERTI evidence.
- Prefer adding fail-fast real-runtime probes before promoting any CERTI row to
  `yes`.
- Treat Pitch as a separate vendor baseline once activation/runtime startup is
  reliable.
