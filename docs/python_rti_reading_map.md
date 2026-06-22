# Python RTI Reading Map

Use this page when you want the shortest reading path through the repo's Python
RTI implementation story.

It is organized by question:

1. where the public API lives
2. where the active backend lanes live
3. where the current 2025 proof surface lives
4. where to read next when editing behavior

## Fast Path

If you only need the shortest practical route, read these in order:

1. [python_rti_backend.md](python_rti_backend.md)
2. [package_dependency_tree.md](package_dependency_tree.md)
3. [../packages/hla-rti1516-2025/README.md](../packages/hla-rti1516-2025/README.md)
4. [../packages/hla-backend-python2025/README.md](../packages/hla-backend-python2025/README.md)
5. [plans/spec2025_finish_line.md](plans/spec2025_finish_line.md)
6. [verification/time_model_compliance.md](verification/time_model_compliance.md)
7. [../tests/test_rti1516_2025_spec_and_shim.py](../tests/test_rti1516_2025_spec_and_shim.py)
8. [../packages/hla-backend-shim/README.md](../packages/hla-backend-shim/README.md)

That sequence gets you from architecture to the current 2025 runtime proof with
minimal detours.

Item 7 has a historical filename. Read it as the main in-process executable
proof suite for `hla-backend-python2025`, with only limited wrapper-specific
compatibility coverage.

Use the shim README only when you are checking legacy provider spelling,
wrapper-only imports, or compatibility-surface behavior.

Routine proof commands behind that reading order:

- `./tools/python verify-main-2025` for the normal direct `python2025`
  main-surface proof lane
- `./tools/python verify-routes-2025` when you also need the bounded hosted
  `python-2025-fedpro-grpc` hygiene lane

## Public API Roots

The versioned public Python API packages are:

- `packages/hla-rti1516e/src/hla/rti1516e/`
- `packages/hla-rti1516-2025/src/hla/rti1516_2025/`

Key files:

- [../packages/hla-rti1516e/src/hla/rti1516e/rti_ambassador.py](../packages/hla-rti1516e/src/hla/rti1516e/rti_ambassador.py)
- [../packages/hla-rti1516e/src/hla/rti1516e/federate_ambassador.py](../packages/hla-rti1516e/src/hla/rti1516e/federate_ambassador.py)
- [../packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py](../packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py)
- [../packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py](../packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py)

Read those first if you need the strict versioned API contracts before looking
at any backend code.

## Backend Lanes

The repo currently has two Python implementation lanes:

- 2010 pure-Python backend:
  [../packages/hla-backend-inmemory/README.md](../packages/hla-backend-inmemory/README.md)
- 2025 primary Python RTI backend:
  [../packages/hla-backend-python2025/README.md](../packages/hla-backend-python2025/README.md)
- 2025 compatibility-wrapper alias:
  [../packages/hla-backend-shim/README.md](../packages/hla-backend-shim/README.md)

Important distinction:

- `hla-backend-inmemory` is the 2010 backend implementation lane
- `hla-backend-python2025` is the main full 2025 Python RTI implementation lane
- `hla-backend-shim` is a wrapper-only compatibility alias over that runtime

## 2025 Runtime Proof Surface

When you care about the current 2025 backend reality, the most important files
are:

- [python_rti_backend.md](python_rti_backend.md): architecture and
  promotion-versus-split note
- [plans/2025_python_rti_backend_audit.md](plans/2025_python_rti_backend_audit.md):
  explicit promotion-versus-extraction audit for the current 2025 lane
- [plans/2025_requirements_finish_line.md](plans/2025_requirements_finish_line.md):
  generated finish-line and blocker snapshot
- [../packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py](../packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py):
  source of truth for the finish-line snapshot
- [../tests/test_rti1516_2025_spec_and_shim.py](../tests/test_rti1516_2025_spec_and_shim.py):
  historical filename; main in-process `python2025` runtime suite
- [../tests/transport/test_grpc_transport_2025.py](../tests/transport/test_grpc_transport_2025.py):
  hosted 2025 FedPro route coverage
- [../packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py](../packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py):
  tracked 2025 route parity

Use that set when the question is:

- what is the current 2025 backend
- what does it actually prove
- what still remains bounded

For time-management, lookahead, and save/restore-window questions, treat
`verification/time_model_compliance.md` and
`tests/test_rti1516_2025_spec_and_shim.py` as the main proof front doors before
looking at any wrapper-only compatibility surface.

## Editing By Concern

If you are changing API-surface or type behavior:

- start in `packages/hla-rti1516-2025/src/hla/rti1516_2025/`

If you are changing runtime semantics for the 2025 lane:

- start in
  [../packages/hla-backend-python2025/src/hla/backends/python2025/backend.py](../packages/hla-backend-python2025/src/hla/backends/python2025/backend.py)

If you are changing shared scenario proof:

- start in `packages/hla-verification/src/hla/verification/`

If you are changing hosted 2025 transport behavior:

- start in `packages/hla-transport-grpc/src/hla/transports/grpc/`

## Typical Read Orders

For a 2025 runtime bug:

1. `tests/test_rti1516_2025_spec_and_shim.py` (historical filename; main `python2025` proof suite)
2. `packages/hla-backend-python2025/src/hla/backends/python2025/backend.py`
3. `packages/hla-backend-shim/src/hla/backends/shim/backend.py` when the issue is wrapper-only compatibility behavior
4. `packages/hla-rti1516-2025/src/hla/rti1516_2025/*`

Run `./tools/python verify-main-2025` as the default proof command after
changes in that path.

For a 2025 route-parity question:

1. `plans/2025_requirements_finish_line.md`
2. `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`
3. `tests/requirements/test_2025_route_parity_matrix.py`

Run `./tools/python verify-routes-2025` when the change must stay aligned with
the bounded hosted `python-2025-fedpro-grpc` route.

For a time-management or lookahead question:

1. `tests/test_rti1516_2025_spec_and_shim.py` (historical filename; main `python2025` proof suite)
2. `packages/hla-verification/src/hla/verification/scenario_target_radar_time.py`
3. `packages/hla-backend-python2025/src/hla/backends/python2025/backend.py`

## Read Next

1. [rti_factory_reading_map.md](rti_factory_reading_map.md)
2. [python_api_spec.md](python_api_spec.md)
3. [networked_rti_python.md](networked_rti_python.md)
