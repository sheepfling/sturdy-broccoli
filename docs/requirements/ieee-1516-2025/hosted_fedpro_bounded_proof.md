# Hosted FedPro 2025 Bounded Proof

Source: IEEE 1516.1-2025 hosted-route and FedPro/protobuf transport evidence.

This note records the repo's current hosted-route claim for
`python1516_2025-fedpro-grpc`. The hosted FedPro lane is real executable evidence
over the main `hla-backend-python2025` runtime, but it remains a bounded
transport/runtime slice rather than a second RTI implementation family or a
full remote-RTI semantics claim.

## Current Bounded Claim

- `python1516_2025-fedpro-grpc` is a hosted route variant over
  `hla-backend-python2025`, not a separate 2025 RTI owner.
- `hla-backend-python2025` remains the sole repo-owned IEEE 1516.1-2025
  Python RTI implementation lane behind this hosted replay surface.
- The hosted route is parity-covered across the tracked scenario families used
  by the current finish-line inventory.
- The hosted route preserves direct `python1516_2025` RTI identity through the
  hosted ambassador, server, and client path.
- The remaining proof burden on this lane is transport-seam and cross-binding
  evidence, not missing ownership of core RTI semantics.

## Tracked Hosted Scenario Families

| Scenario family | Status | Evidence anchors | Current hosted reading |
| --- | --- | --- | --- |
| `federation_lifecycle` | `parity-covered` | `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Hosted lifecycle covers connect/create/join/list/resign/destroy/disconnect and typed callback replay over the main `python1516_2025` lane. |
| `object_exchange` | `parity-covered` | `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Hosted object exchange covers discovery, reflection, interaction delivery, callback backlog hygiene, and FOM-backed object/interaction replay. |
| `ownership` | `parity-covered` | `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Hosted ownership covers acquisition/divestiture/query callback flow, owner visibility, and bounded save/restore ownership rollback. |
| `ddm` | `parity-covered` | `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Hosted DDM covers region overlap filtering, directed interaction gating, passive routing, and cleanup of disconnected subscriptions. |
| `time_management` | `parity-covered` | `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Hosted time management covers regulation/constrained mode, grants, queued TSO delivery, GALT/LITS/lookahead queries, the shared Target/Radar example path, and the bounded Target/Radar window proofs. |
| `save_restore` | `parity-covered` | `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Hosted save/restore covers lifecycle callbacks, checkpoint replay, stale queued-state cleanup, and restore-path route hygiene. |
| `mom` | `parity-covered` | `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Hosted MOM covers service-report callbacks, MIM/FOM data reporting, routed manager adjust actions, and bounded federation/time-management MOM replay. |
| `support_services` | `parity-covered` | `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py` | Hosted support services cover handle/name round trips, query helpers, callback-delivery control, switch inquiry, and reservation/release callback flows. |

## Primary Evidence Anchors

- `tests/transport/test_grpc_transport_2025.py`
- `tests/scenarios/test_python_route_parity.py`
- `docs/backend_route_inventory_remote.md`
- `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`
- `docs/requirements/ieee-1516-2025/python2025_direct_bounded_proof.md`
- `docs/requirements/ieee-1516-2025/python2025_exclusion_boundaries.md`

## Reading of the Evidence

- The route-parity matrix is the requirement-facing ledger for the hosted FedPro
  route. It records that all eight tracked scenario families are
  `parity-covered` on `python1516_2025-fedpro-grpc`.
- `tests/transport/test_grpc_transport_2025.py` is the executable hosted-route
  anchor. It proves the transport-facing request/response/callback behavior and
  the direct hosted `python1516_2025` ambassador path, including the factory-hosted
  shared Target/Radar example scenario and the package-owned Target/Radar time
  window/save-restore proofs.
- `tests/scenarios/test_python_route_parity.py` is the shared-scenario replay
  anchor. It proves the hosted route replays the same bounded scenario families
  as the direct `python1516_2025` lane.
- `docs/backend_route_inventory_remote.md` captures the operator-facing
  boundary: the hosted FedPro route is real runtime evidence, but it is still a
  bounded runtime slice over `hla-backend-python2025`.
- `docs/requirements/ieee-1516-2025/python2025_direct_bounded_proof.md` is
  the direct companion note. It keeps the implementation-owner claim anchored
  to the in-process `python1516_2025` lane while this note records the hosted
  replay.

## Operator Lane

- `./tools/python verify-routes-2025` is the maintained hosted hygiene lane
  for this bounded route claim.
- `./tools/python verify-main-2025` remains the paired direct proof lane for
  the same runtime families on the in-process `python1516_2025` surface.

## Explicit Non-Claim

- The repo does not claim that `python1516_2025-fedpro-grpc` is a second full RTI
  implementation lane.
- The repo does not claim full remote-RTI semantics or exhaustive cross-binding
  conformance from the hosted route alone.
- The repo does not use hosted-route proof to dilute the architectural boundary
  that keeps `hla-backend-shim` wrapper-only and `hla-backend-python2025` as
  the main 2025 Python RTI implementation lane.
