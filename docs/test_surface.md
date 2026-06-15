# Test Surface

This page defines the canonical verification lanes for the repo.

Use it when you want the shortest answer to:

- what can I run here?
- what should I run first?
- what lane is safe for a user or agent without real vendor runtime setup?

The supported front door is [`../tools/test-surface`](../tools/test-surface).

## Canonical Lanes

Use these five lanes and treat lower-level scripts as implementation detail:

1. `./tools/python verify-fast`
2. `./tools/python verify`
3. `./tools/python verify-routes`
4. `./tools/vendor-green matrix`
5. `./tools/test-surface run matrix`

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
| `fast` | `./tools/python verify-fast` | low-cost operator, docs, and Python matrix checks |
| `repo-green` | `./tools/python verify` | full supported local repo-green lane |
| `python-routes` | `./tools/python verify-routes` | hosted Python RTI parity, transport-route semantics, and hosted example checks |
| `vendor` | `./tools/vendor-green matrix` | strict real-runtime lane after vendor preflight |
| `matrix` | `./tools/test-surface run matrix` | regenerate compliance/matrix artifacts and rerun matrix gates |

## Hosted Python Hygiene

Use `./tools/python verify-routes` as the normal hygiene lane when you change:

- `hla2010_rti_python` backend behavior that should remain identical over the hosted route
- hosted transport client/server wiring for Python RTI
- Target/Radar hosted Python example selection
- Python route parity fixtures, matrices, or artifacts

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
