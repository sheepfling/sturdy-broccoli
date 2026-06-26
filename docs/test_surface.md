# Test Surface

This page defines the canonical verification lanes for the repo.

Use it when you want the shortest answer to:

- what can I run here?
- what should I run first?
- what lane is safe for a user or agent without real vendor runtime setup?

The supported front door is [`../tools/test-surface`](../tools/test-surface).
For named focused reruns and restartable submodule work, use
[`../tools/test-focus`](../tools/test-focus).

## Canonical Lanes

Use these repo lanes and treat lower-level scripts as implementation detail:

1. `./tools/python verify-smoke`
2. `./tools/test-surface validate`
3. `./tools/python verify-fast`
4. `./tools/python verify`
5. `./tools/test-surface run repo-green-units`
6. `./tools/python verify-main-2025`
7. `./tools/python verify-routes`
8. `./tools/python verify-routes-2025`
9. `./tools/vendor-green matrix`
10. `./tools/test-surface run matrix`

The matching discovery commands are:

```bash
./tools/test-surface validate
./tools/test-surface inventory
./tools/test-surface recommend
./tools/test-surface preflight
./tools/test-surface preflight --lane vendor --json
```

For junior-friendly reruns, `./tools/test-surface run` also accepts a few
intent aliases:

```bash
./tools/test-surface run foundation
./tools/test-surface run onboarding
./tools/test-surface run shim-tooling
./tools/test-surface run transport
./tools/test-surface run scenarios
```

## What Each Lane Means

| Lane | Primary command | Purpose |
|---|---|---|
| `smoke` | `./tools/python verify-smoke` | fast-fail repo smoke lane for operator wrappers, package-boundary policy, portability, and top-level vendor wrapper contracts before expensive depth |
| `fast` | `./tools/python verify-fast` | low-cost operator, docs, Python matrix, and 2025 requirements-evidence index checks |
| `repo-green` | `./tools/python verify` | full supported local repo-green lane |
| `repo-green-units` | `./tools/test-surface run repo-green-units` | composite repo-green unit sweep; edit this lane to add, remove, or reorder unit shards |
| `unit-foundation` | `./tools/test-surface run unit-foundation` | cheap policy, package-boundary, import-hygiene, and operator-wrapper shard |
| `unit-python-core` | `./tools/test-surface run unit-python-core` | direct Python example and RTI-core shard |
| `unit-federate-examples` | `./tools/test-surface run unit-federate-examples` | interactive federate CLI, walkthrough, TUI, and change-map shard for the examples/help surface |
| `unit-vendor-onboarding` | `./tools/test-surface run unit-vendor-onboarding` | Pitch/CERTI onboarding docs, preflight/report contracts, and vendor wrapper front-door shard |
| `unit-shim-tooling` | `./tools/test-surface run unit-shim-tooling` | Java/C++ shim route docs, doctor/preflight wrappers, and standard-shim artifact surface shard |
| `unit-fom-tooling` | `./tools/test-surface run unit-fom-tooling` | FOM parsing, validation, workbench, and packaged-factory shard |
| `unit-python-2025-core` | `./tools/test-surface run unit-python-2025-core` | primary `python1516_2025` unit shard for direct runtime semantics and validation |
| `unit-transport-local` | `./tools/test-surface run unit-transport-local` | hosted transport shard for gRPC and REST tests without vendor-runtime lanes |
| `unit-scenarios-light` | `./tools/test-surface run unit-scenarios-light` | repo-owned backend and Target/Radar scenario-light shard |
| `python1516_2025-main` | `./tools/python verify-main-2025` | primary `python1516_2025` main-surface proof lane for package-boundary guards, raw support/decode plus callback-control proofs on the direct runtime surface, explicit federation/object/DDM runtime proofs, explicit support/ownership/MOM runtime proofs, the explicit Target/Radar time-window gauntlet and restore-window ladder, the explicit save/restore gauntlet and rollback ladder, broader direct runtime slices, and OMT evidence |
| `python-routes` | `./tools/python verify-routes` | hosted 2010 Python RTI parity, transport-route semantics, and hosted example checks |
| `python1516_2025-routes` | `./tools/python verify-routes-2025` | bounded `python1516_2025` plus hosted FedPro 2025 route checks, explicit hosted federation/object/DDM runtime proofs, explicit hosted support/ownership/MOM runtime proofs, explicit hosted Target/Radar time-window ladder replay, explicit hosted save/restore gauntlet and rollback replay, direct time-window, save/restore, ownership, callback, support-service, and MOM proofs, the checked-in 2025 finish-line bundle, and the README-advertised `python1516_2025` Target/Radar example path |
| `vendor` | `./tools/vendor-green matrix` | strict real-runtime lane after vendor preflight |
| `matrix` | `./tools/test-surface run matrix` | regenerate compliance artifacts, refresh the checked-in 2025 finish-line bundle, and rerun matrix gates |

## Which Shard To Run

Use this table when you want one small rerun instead of `repo-green-units`.

| If you changed or broke... | Run this | Alias | Why this shard exists | Common failure meaning | Not for |
|---|---|---|---|---|---|
| wrapper inventory, doc links, manifest structure, or top-level policy | `./tools/test-surface run unit-foundation` | `./tools/test-surface run foundation` | cheapest structural first signal | operator surface, path policy, or manifest drift | runtime semantics |
| pure Python examples or shared RTI core helpers | `./tools/test-surface run unit-python-core` | `./tools/test-surface run python-core` | core Python behavior before broader scenario depth | example wiring or shared RTI core regression | vendor setup or transport |
| federate CLI, walkthrough help, or TUI flows | `./tools/test-surface run unit-federate-examples` | `./tools/test-surface run examples` | interactive operator surface for examples | CLI contract or walkthrough drift | deep backend/runtime proof |
| Pitch/CERTI first-run docs, vendor preflight contracts, or onboarding guidance | `./tools/test-surface run unit-vendor-onboarding` | `./tools/test-surface run onboarding` | newcomer vendor setup front door | onboarding docs or preflight contract drift | standard shim or core Python runtime |
| Java/C++ shim route setup, doctors, or standard-shim wrapper surface | `./tools/test-surface run unit-shim-tooling` | `./tools/test-surface run shim-tooling` | language-binding setup and artifact readiness | Java/C++ preflight, toolchain, or shim route drift | vendor runtime provisioning |
| FOM parsing, validation, packaged factories, or workbench surface | `./tools/test-surface run unit-fom-tooling` | `./tools/test-surface run fom` | FOM tooling isolation | parser, validation, or workbench regression | transport or vendor setup |
| direct `python1516_2025` runtime semantics or validation helpers | `./tools/test-surface run unit-python-2025-core` | `./tools/test-surface run python-2025` | main 2025 runtime unit slice | direct 2025 runtime regression | onboarding/docs-only changes |
| hosted gRPC/REST route plumbing without vendor runtime | `./tools/test-surface run unit-transport-local` | `./tools/test-surface run transport` | hosted route boundary checks | transport adapter or hosted route regression | direct runtime-only behavior |
| Target/Radar or higher-level backend scenario behavior | `./tools/test-surface run unit-scenarios-light` | `./tools/test-surface run scenarios` | scenario-level signal before vendor lanes | scenario composition or backend integration regression | simple policy/docs failures |

Current shape guidance:

- keep `unit-foundation`, `unit-vendor-onboarding`, and `unit-shim-tooling` separate because they serve different newcomer/debug stories
- keep `unit-python-core` and `unit-python-2025-core` separate because they protect different runtime ownership lanes
- review `unit-federate-examples` and `unit-scenarios-light` together when future shard simplification comes up, because they are the closest overlap point today

## Python 2025 Main Surface

Use `./tools/python verify-main-2025` as the normal main-implementation lane
when you change:

- direct `python1516_2025` runtime semantics
- save/restore, ownership, callback, support-service, or MOM behavior on the
  main in-process lane
- the Target/Radar shared scenario path as executable in-process evidence
- OMT parsing, validation, or round-trip behavior that supports the 2025
  backend claim

This lane is intentionally broader than hosted-route hygiene and intentionally
separate from it. It is the shortest operator path that combines the direct
`python1516_2025` runtime slices, the package/runtime boundary guardrails that keep
`shim` wrapper-only, the requirement-facing bounded proof-note registry, and
the dedicated OMT evidence surface.

It also now includes the explicit raw `python1516_2025` proofs for:

- support-service handle-factory and decode-helper behavior without routing
  through the compatibility wrapper
- snake-case alias acceptance on the direct `python1516_2025` runtime surface
- callback-control behavior on `hla-backend-python1516-2025` itself:
  `disableCallbacks`, `enableCallbacks`, `evokeCallback`, and
  `evokeMultipleCallbacks`

## Hosted Python Hygiene

Use `./tools/python verify-routes` as the normal hygiene lane when you change:

- `hla.backends.python1516e` backend behavior that should remain identical over the hosted route
- hosted transport client/server wiring for Python RTI
- Target/Radar hosted Python example selection
- Python route parity fixtures, matrices, or artifacts

For the 2025 lane specifically, use `./tools/python verify-routes-2025` as the
normal route-level hygiene lane for the main `python1516_2025` RTI plus the bounded
`python1516_2025-fedpro-grpc` route. That lane covers the hosted 2025 transport
suite, explicit in-process `python1516_2025` time-window, save/restore, ownership,
callback, support-service, and MOM proof selectors, the checked-in 2025
route-parity ledger, the 2025 requirements-registry/bounded-proof-note
surface, regeneration of the checked-in 2025 finish-line bundle (including the
route-parity artifacts), and the README-advertised `python1516_2025` Target/Radar
example path.
Pair it with:

- [`python_rti_backend.md`](python_rti_backend.md)
- [`verification/time_model_compliance.md`](verification/time_model_compliance.md)
- [`requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md)
- [`plans/spec2025_route_parity_matrix.md`](plans/spec2025_route_parity_matrix.md)

That exclusion note is the operator-facing non-claim map for legacy aliases,
Java/C++ bindings, hosted transport boundaries, duplicate/umbrella rows,
retired rows, and out-of-scope OMT extension semantics around the main
`python1516_2025` lane.

If loopback availability is uncertain in the current session, run:

```bash
./tools/python verify-routes-preflight
```

before the lane itself.

## User Workflow

Start here:

```bash
./tools/test-surface recommend
```

Then run the recommended lane.

`./tools/test-surface` validates `testing/test_surface_manifest.json` before
inventory, recommend, preflight, or run, so broken shard composition fails at
the front door instead of inside later orchestration.

If you want the fastest structural failure signal before broader reruns, start with:

```bash
./tools/test-surface validate
./tools/python verify-smoke
./tools/test -x
```

`verify-smoke` validates `testing/test_surface_manifest.json` before running the
smoke pytest set, so shard wiring mistakes fail before the broader lane runs.

If the broad unit phase is too large, start with the composite unit sweep:

```bash
./tools/test-surface run repo-green-units
```

If you need a smaller bite than that, run the named shards directly:

```bash
./tools/test-surface run unit-foundation
./tools/test-surface run unit-python-core
./tools/test-surface run unit-federate-examples
./tools/test-surface run unit-vendor-onboarding
./tools/test-surface run unit-shim-tooling
./tools/test-surface run unit-fom-tooling
./tools/test-surface run unit-python-2025-core
./tools/test-surface run unit-transport-local
./tools/test-surface run unit-scenarios-light
```

If the canonical lane names are too much to remember, use the alias forms
instead:

```bash
./tools/test-surface run foundation
./tools/test-surface run onboarding
./tools/test-surface run shim-tooling
./tools/test-surface run transport
./tools/test-surface run scenarios
```

The junior rule is simple:

- change shard membership or order in `repo-green-units`
- change shard contents inside the individual `unit-*` lane
- do not edit `full_sequence.py` just to reshuffle unit slices

If the lane is too large, switch to a named focused target instead of guessing
raw pytest selectors:

```bash
./tools/test-focus inventory
./tools/test-focus run foundation
./tools/test-focus run python-examples
./tools/test-focus run java-bridges
./tools/test-focus run jpype
./tools/test-focus run py4j
./tools/test-focus run target-radar
./tools/test-focus run rti-core
./tools/test-focus run python-2025-time
./tools/test-focus run python-2025-save-restore
./tools/test-focus run python-2025-ownership
./tools/test-focus run python-2025-mom-callbacks
./tools/test-focus run routes-2025
./tools/test-focus run python-2025-runtime -- --maxfail=1
./tools/test-focus resume python-2025-runtime
```

That gives you two things the lane commands do not:

- a stable named target for a package/theme
- a restart path that reuses pytest last-failed state through `resume`

Aliases also work when the submodule name is easier to remember than the
canonical target id. Examples:

```bash
./tools/test-focus run fom-target-radar
./tools/test-focus run rti-factory
./tools/test-focus run bridge-jpype
./tools/test-focus run save-restore-2025
./tools/test-focus run finish-line-2025
```

If you need machine-readable output for automation or agent selection:

```bash
./tools/test-surface inventory --json
./tools/test-surface recommend --json
./tools/test-surface preflight --json
```

## Agent Workflow

Agents should prefer:

1. `./tools/test-surface inventory --json`
2. `./tools/test-surface preflight --json`
3. `./tools/test-surface recommend --json`
4. inspect `repo-green-units` when changing unit shard order or membership
5. inspect the matching `unit-*` lane when changing shard contents

That keeps lane selection machine-readable and avoids guessing from scattered
docs, ad hoc pytest selectors, or CI plumbing.

Agent maintenance rule:

- the authoritative shard inventory and shard order live in
  `testing/test_surface_manifest.json`
- `repo-green-units.include_lanes` is the only place an agent should edit to
  add, remove, or reorder repo-green unit shards
- the `commands` of each `unit-*` lane are the only place an agent should edit
  to change what one shard runs
- `scripts/ci/full_sequence.py` should change only when the top-level lifecycle
  changes, not when unit shards are reshuffled

## Artifacts

`./tools/test-surface run <lane>` writes normalized run summaries to:

- `artifacts/test_surface_status/<lane>.json`
- `artifacts/test_surface_status/<lane>.md`
- `artifacts/test_surface_status/validate_manifest.json`
- `artifacts/test_surface_status/validate_manifest.md`

Use those artifacts to see what the lane ran and whether it passed, failed, or
was only planned through `--dry-run`, plus whether the manifest itself was
structurally valid at the front door.

`./tools/test-focus run <target>` writes the same kind of summary for focused
work under:

- `artifacts/test_focus_status/<target>.json`
- `artifacts/test_focus_status/<target>.md`
