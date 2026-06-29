# RTI Factory Reading Map

Use this page when you want to understand how the repo chooses an RTI
implementation from `hla.rti.create_rti_ambassador(...)` or the version-local
factory helpers.

This page is part of the backend and route-wrapping surface. If you are still
deciding whether the problem is mostly backend, transport, or FOM, start at
[`work_surfaces.md`](work_surfaces.md). For the combined backend decision
guide, start at
[`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md).

## Start Here

Read these first:

1. [python_api_spec.md](python_api_spec.md)
2. [python_rti_backend.md](python_rti_backend.md)
3. [../packages/hla-rti-core/src/hla/rti/factory.py](../packages/hla-rti-core/src/hla/rti/factory.py)

That path explains the public API, the current backend-lane reality, and the
cross-version factory entrypoint.

Routine proof commands behind that selection story:

- `./tools/python verify-main-2025` for the normal direct `python1516_2025`
  factory/runtime proof lane
- `./tools/python verify-routes-2025` when factory or route changes must stay
  aligned with the bounded hosted `python1516_2025-fedpro-grpc` lane

## Core Factory Files

Cross-version factory and registry logic lives in:

- [../packages/hla-rti-core/src/hla/rti/factory.py](../packages/hla-rti-core/src/hla/rti/factory.py)
- [../packages/hla-rti-core/src/hla/rti/standard_shims.py](../packages/hla-rti-core/src/hla/rti/standard_shims.py)

Version-local helpers live in:

- [../packages/hla-rti-core/src/hla/runtime/rti1516e.py](../packages/hla-rti-core/src/hla/runtime/rti1516e.py)
- [../packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_factory.py](../packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_factory.py)
- [../packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_factory.py](../packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_factory.py)

Plugin registration entrypoints live in:

- [../packages/hla-backend-python1516e/src/hla/backends/python1516e/plugin.py](../packages/hla-backend-python1516e/src/hla/backends/python1516e/plugin.py)
- [../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/plugin.py](../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/plugin.py)

For the main 2025 runtime-construction path behind that plugin, the public
shell now fans out into focused package-owned modules rather than one giant
backend file. The most useful follow-on files are:

- [../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py](../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py)
- [../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend_factory_runtime.py](../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend_factory_runtime.py)
- [../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/runtime_state.py](../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/runtime_state.py)

## What To Read By Question

If you want to know how the 2010 backend is selected:

1. `packages/hla-rti-core/src/hla/runtime/rti1516e.py`
2. `packages/hla-rti-core/src/hla/rti/factory.py`
3. `packages/hla-backend-python1516e/src/hla/backends/python1516e/plugin.py`

If you want to know how the 2025 backend is selected:

1. `packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_factory.py`
2. `packages/hla-rti-core/src/hla/rti/factory.py`
3. `packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/plugin.py`

If you want to know why `python1516_2025` is the selected 2025 provider today and
why `hla.backends.shim` is now compatibility-only:

1. [python_rti_backend.md](python_rti_backend.md)
2. [../packages/hla-backend-python1516-2025/README.md](../packages/hla-backend-python1516-2025/README.md)
3. [../packages/hla-backend-shim/README.md](../packages/hla-backend-shim/README.md)
4. [../requirements/2025/canonical_requirements.json](../requirements/2025/canonical_requirements.json)
5. [../requirements/2025/backend_resolution.json](../requirements/2025/backend_resolution.json)

## Current Practical Selection Story

Today the repo's practical Python RTI selection story is:

- `inmemory` is the real pure-Python backend for `rti1516e`
- `python1516_2025` is the main full executable backend lane for `rti1516_2025`
- `hla.backends.shim` is import-level compatibility code over that runtime rather than the implementation owner
- hosted routes such as the 2025 FedPro gRPC path are route variants layered
  over the selected backend/factory surface, not independent RTI families

That means new 2025 runtime work should select `backend="python1516_2025"`. The
legacy `shim` spelling is intentionally rejected on the public factory surface.

So if you create a 2025 RTI ambassador through the current factory stack, you
should expect to land on the `hla-backend-python1516-2025` lane by default. The
legacy shim provider spelling is no longer part of the supported public
factory surface. The main `python1516_2025` factory path now does accept hosted
2025 creation through `transport=...`. The same hosted FedPro route can therefore be reached
either through the explicit FedPro server plus typed `GrpcTransport` surface
or through `create_rti_ambassador(backend="python1516_2025", transport=...)`.

For evidence that this is not just naming policy, follow the default-selection
proof first and only then inspect the wrapper alias:

1. `tests/test_hla_factory_composition.py`
2. `tests/test_rti1516_2025_python1516_2025_runtime.py` (main in-process `python1516_2025` proof suite)
3. `requirements/2025/canonical_requirements.json`
4. `requirements/2025/backend_resolution.json`
5. `tests/requirements/test_2025_finish_line_snapshot.py` (downstream closeout-reporting verification)

In practice, `./tools/python verify-main-2025` is the normal proof command for
that direct factory-selection path, while `./tools/python verify-routes-2025`
is the follow-on lane when hosted factory transport ownership must stay green.

## Verification Anchors

The main tests that prove the current factory composition and 2025 selection
behavior are:

- [../tests/test_hla_factory_composition.py](../tests/test_hla_factory_composition.py)
- [../tests/test_rti1516_2025_python1516_2025_runtime.py](../tests/test_rti1516_2025_python1516_2025_runtime.py) (main in-process `python1516_2025` proof suite)
- [../requirements/2025/canonical_requirements.json](../requirements/2025/canonical_requirements.json)
- [../requirements/2025/backend_resolution.json](../requirements/2025/backend_resolution.json)
- [../tests/requirements/test_2025_finish_line_snapshot.py](../tests/requirements/test_2025_finish_line_snapshot.py) (downstream closeout-reporting verification)

Use those when changing:

- provider registration
- version-to-backend selection
- 2025 factory composition
- route selection metadata

## Read Next

1. [python_rti_reading_map.md](python_rti_reading_map.md)
2. [package_dependency_tree.md](package_dependency_tree.md)
3. [backend_route_inventory.md](backend_route_inventory.md)
