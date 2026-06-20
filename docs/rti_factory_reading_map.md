# RTI Factory Reading Map

Use this page when you want to understand how the repo chooses an RTI
implementation from `hla.rti.create_rti_ambassador(...)` or the version-local
factory helpers.

## Start Here

Read these first:

1. [python_api_spec.md](python_api_spec.md)
2. [python_rti_backend.md](python_rti_backend.md)
3. [../packages/hla-rti-core/src/hla/rti/factory.py](../packages/hla-rti-core/src/hla/rti/factory.py)

That path explains the public API, the current backend-lane reality, and the
cross-version factory entrypoint.

## Core Factory Files

Cross-version factory and registry logic lives in:

- [../packages/hla-rti-core/src/hla/rti/factory.py](../packages/hla-rti-core/src/hla/rti/factory.py)
- [../packages/hla-rti-core/src/hla/rti/standard_shims.py](../packages/hla-rti-core/src/hla/rti/standard_shims.py)

Version-local helpers live in:

- [../packages/hla-rti1516e/src/hla/rti1516e/rti.py](../packages/hla-rti1516e/src/hla/rti1516e/rti.py)
- [../packages/hla-rti1516-2025/src/hla/rti1516_2025/factory.py](../packages/hla-rti1516-2025/src/hla/rti1516_2025/factory.py)
- [../packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_factory.py](../packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_factory.py)

Plugin registration entrypoints live in:

- [../packages/hla-backend-inmemory/src/hla/backends/inmemory/plugin.py](../packages/hla-backend-inmemory/src/hla/backends/inmemory/plugin.py)
- [../packages/hla-backend-shim/src/hla/backends/shim/plugin.py](../packages/hla-backend-shim/src/hla/backends/shim/plugin.py)

## What To Read By Question

If you want to know how the 2010 backend is selected:

1. `packages/hla-rti1516e/src/hla/rti1516e/rti.py`
2. `packages/hla-rti-core/src/hla/rti/factory.py`
3. `packages/hla-backend-inmemory/src/hla/backends/inmemory/plugin.py`

If you want to know how the 2025 backend is selected:

1. `packages/hla-rti1516-2025/src/hla/rti1516_2025/factory.py`
2. `packages/hla-rti-core/src/hla/rti/factory.py`
3. `packages/hla-backend-shim/src/hla/backends/shim/plugin.py`

If you want to know why `shim` is the selected 2025 provider today:

1. [python_rti_backend.md](python_rti_backend.md)
2. [../packages/hla-backend-shim/README.md](../packages/hla-backend-shim/README.md)
3. [plans/2025_requirements_finish_line.md](plans/2025_requirements_finish_line.md)

## Current Practical Selection Story

Today the repo's practical Python RTI selection story is:

- `inmemory` is the real pure-Python backend for `rti1516e`
- `shim` is the current executable backend lane for `rti1516_2025`
- hosted routes such as the 2025 FedPro gRPC path are route variants layered
  over the selected backend/factory surface, not independent RTI families

So if you create a 2025 RTI ambassador through the current factory stack, you
should expect to land on the `hla-backend-shim` lane unless you are explicitly
using a hosted route variant.

## Verification Anchors

The main tests that prove the current factory composition and 2025 selection
behavior are:

- [../tests/test_hla_factory_composition.py](../tests/test_hla_factory_composition.py)
- [../tests/test_rti1516_2025_spec_and_shim.py](../tests/test_rti1516_2025_spec_and_shim.py)
- [../tests/requirements/test_2025_finish_line_snapshot.py](../tests/requirements/test_2025_finish_line_snapshot.py)

Use those when changing:

- provider registration
- version-to-backend selection
- 2025 factory composition
- route selection metadata

## Read Next

1. [python_rti_reading_map.md](python_rti_reading_map.md)
2. [package_dependency_tree.md](package_dependency_tree.md)
3. [backend_route_inventory.md](backend_route_inventory.md)
