# Test Surface

This page defines the canonical verification lanes for the repo.

Use it when you want the shortest answer to:

- what can I run here?
- what should I run first?
- what lane is safe for a user or agent without real vendor runtime setup?

The supported front door is [`../tools/test-surface`](../tools/test-surface).

## Canonical Lanes

Use these seven lanes and treat lower-level scripts as implementation detail:

1. `./tools/python verify-fast`
2. `./tools/python verify`
3. `./tools/python verify-main-2025`
4. `./tools/python verify-routes`
5. `./tools/python verify-routes-2025`
6. `./tools/vendor-green matrix`
7. `./tools/test-surface run matrix`

The matching discovery commands are:

```bash
./tools/test-surface inventory
./tools/test-surface recommend
./tools/test-surface preflight
./tools/test-surface preflight --lane vendor --json
```

## What Each Lane Means

| Lane | Primary command | Purpose |
|---|---|---|
| `fast` | `./tools/python verify-fast` | low-cost operator, docs, Python matrix, and 2025 requirements-evidence index checks |
| `repo-green` | `./tools/python verify` | full supported local repo-green lane |
| `python-main-2025` | `./tools/python verify-main-2025` | primary `python2025` main-surface proof lane for package-boundary guards, raw support/decode plus callback-control proofs on the direct runtime surface, explicit federation/object/DDM runtime proofs, explicit support/ownership/MOM runtime proofs, the explicit Target/Radar time-window gauntlet and restore-window ladder, the explicit save/restore gauntlet and rollback ladder, broader direct runtime slices, and OMT evidence |
| `python-routes` | `./tools/python verify-routes` | hosted 2010 Python RTI parity, transport-route semantics, and hosted example checks |
| `python-routes-2025` | `./tools/python verify-routes-2025` | bounded `python2025` plus hosted FedPro 2025 route checks, explicit hosted federation/object/DDM runtime proofs, explicit hosted support/ownership/MOM runtime proofs, explicit hosted Target/Radar time-window ladder replay, explicit hosted save/restore gauntlet and rollback replay, direct time-window, save/restore, ownership, callback, support-service, and MOM proofs, the checked-in 2025 finish-line bundle, and the README-advertised `python2025` Target/Radar example path |
| `vendor` | `./tools/vendor-green matrix` | strict real-runtime lane after vendor preflight |
| `matrix` | `./tools/test-surface run matrix` | regenerate compliance artifacts, refresh the checked-in 2025 finish-line bundle, and rerun matrix gates |

## Python 2025 Main Surface

Use `./tools/python verify-main-2025` as the normal main-implementation lane
when you change:

- direct `python2025` runtime semantics
- save/restore, ownership, callback, support-service, or MOM behavior on the
  main in-process lane
- the Target/Radar shared scenario path as executable in-process evidence
- OMT parsing, validation, or round-trip behavior that supports the 2025
  backend claim

This lane is intentionally broader than hosted-route hygiene and intentionally
separate from it. It is the shortest operator path that combines the direct
`python2025` runtime slices, the package/runtime boundary guardrails that keep
`shim` wrapper-only, the requirement-facing bounded proof-note registry, and
the dedicated OMT evidence surface.

It also now includes the explicit raw `python2025` proofs for:

- support-service handle-factory and decode-helper behavior without routing
  through the compatibility wrapper
- snake-case alias acceptance on the direct `python2025` runtime surface
- callback-control behavior on `hla-backend-python2025` itself:
  `disableCallbacks`, `enableCallbacks`, `evokeCallback`, and
  `evokeMultipleCallbacks`

## Hosted Python Hygiene

Use `./tools/python verify-routes` as the normal hygiene lane when you change:

- `hla.backends.inmemory` backend behavior that should remain identical over the hosted route
- hosted transport client/server wiring for Python RTI
- Target/Radar hosted Python example selection
- Python route parity fixtures, matrices, or artifacts

For the 2025 lane specifically, use `./tools/python verify-routes-2025` as the
normal route-level hygiene lane for the main `python2025` RTI plus the bounded
`python-2025-fedpro-grpc` route. That lane covers the hosted 2025 transport
suite, explicit in-process `python2025` time-window, save/restore, ownership,
callback, support-service, and MOM proof selectors, the checked-in 2025
route-parity ledger, the 2025 requirements-registry/bounded-proof-note
surface, regeneration of the checked-in 2025 finish-line bundle (including the
route-parity artifacts), and the README-advertised `python2025` Target/Radar
example path.
Pair it with:

- [`python_rti_backend.md`](python_rti_backend.md)
- [`verification/time_model_compliance.md`](verification/time_model_compliance.md)
- [`requirements/ieee-1516-2025/python2025_exclusion_boundaries.md`](requirements/ieee-1516-2025/python2025_exclusion_boundaries.md)
- [`plans/spec2025_route_parity_matrix.md`](plans/spec2025_route_parity_matrix.md)

That exclusion note is the operator-facing non-claim map for legacy aliases,
Java/C++ bindings, hosted transport boundaries, duplicate/umbrella rows,
retired rows, and out-of-scope OMT extension semantics around the main
`python2025` lane.

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

That keeps lane selection machine-readable and avoids guessing from scattered
docs, ad hoc pytest selectors, or CI plumbing.

## Artifacts

`./tools/test-surface run <lane>` writes normalized run summaries to:

- `analysis/test_surface_status/<lane>.json`
- `analysis/test_surface_status/<lane>.md`

Use those artifacts to see what the lane ran and whether it passed, failed, or
was only planned through `--dry-run`.
