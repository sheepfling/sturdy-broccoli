# Python API Spec

Use this page when you want the clean public Python surface for the HLA 2010
interface without reading the full workspace layout first.

## Front Door

If you only need the supported import ladder, use:

- `from hla.rti1516e.spec import RTIambassadorSpec, FederateAmbassadorSpec`
- `from hla.rti1516e.runtime_api import RTIambassador, FederateAmbassador`
- `from hla.backends.inmemory import rti_ambassador`
- `from hla.foms.target_radar.scenarios import run_target_radar_scenario`

## Package Reality

- installable root: `hla-rti1516e`
- versioned API root: `packages/hla-rti1516e/src/hla/rti1516e/`
- package-owned implementations: `packages/*/src/...`

The installable root owns the 2010 API surface and spec-facing support modules.
cross-version discovery and factory selection live under `hla.rti`.

## Canonical Files

- [`../packages/hla-rti1516e/README.md`](../packages/hla-rti1516e/README.md): installable root package role
- [`../packages/hla-rti1516e/src/hla/rti1516e/spec/__init__.py`](../packages/hla-rti1516e/src/hla/rti1516e/spec/__init__.py): clean abstract/prototype spec surface
- [`../packages/hla-rti1516e/src/hla/rti1516e/runtime_api.py`](../packages/hla-rti1516e/src/hla/rti1516e/runtime_api.py): runtime-facing convenience facade
- [`../packages/hla-rti1516e/src/hla/rti1516e/api.py`](../packages/hla-rti1516e/src/hla/rti1516e/api.py): compatibility shim that re-exports the runtime layer
- [`../packages/hla-rti1516e/src/hla/rti1516e/spec_inventory.py`](../packages/hla-rti1516e/src/hla/rti1516e/spec_inventory.py): plain-text method inventory used by the spec layer
- [`../packages/hla-rti1516e/src/hla/rti1516e/spec_sources.py`](../packages/hla-rti1516e/src/hla/rti1516e/spec_sources.py): readable Java/C++ source locations surfaced in docstrings
- [`../packages/hla-rti1516e/src/hla/rti1516e/spec_refs.py`](../packages/hla-rti1516e/src/hla/rti1516e/spec_refs.py): clause and service references used for traceability
- [`../packages/hla-rti1516e/src/hla/rti1516e/rti.py`](../packages/hla-rti1516e/src/hla/rti1516e/rti.py): version-local backend-discovery and ambassador-factory helper

## Import Table

| Use case | Import |
|---|---|
| Abstract spec contracts | `from hla.rti1516e.spec import RTIambassadorSpec, FederateAmbassadorSpec` |
| Runtime convenience facade | `from hla.rti1516e.runtime_api import RTIambassador, FederateAmbassador` |
| Scenario / FOM entrypoint | `from hla.foms.target_radar.scenarios import run_target_radar_scenario` |
| Verification harness | `from hla.verification import run_basic_federate_scenario` |

## Recommended Imports

For new Python code, prefer the spec module:

```python
from hla.rti1516e.spec import RTIambassadorSpec, FederateAmbassadorSpec
```

Use `RTIambassadorSpec` as the abstract contract for RTI implementations.
Use `FederateAmbassadorSpec` as the no-op prototype base for callback handlers.

If you want the runtime convenience layer instead of the pure contract layer:

```python
from hla.rti1516e.runtime_api import RTIambassador, FederateAmbassador
```

## Why This Split Exists

- `hla-rti1516e` is the installable root package for the clean spec surface.
- `packages/hla-rti1516e/src/hla/rti1516e/spec/__init__.py` exposes the abstract base classes and prototypes.
- `packages/hla-rti1516e/src/hla/rti1516e/runtime_api.py` keeps runtime adapters working without forcing callers onto raw source-derived names.
- `packages/hla-rti1516e/src/hla/rti1516e/api.py` re-exports the runtime layer inside the versioned package.
- `packages/hla-rti1516e/src/hla/rti1516e/spec_inventory.py`, `spec_sources.py`, and `spec_refs.py` keep source mappings readable rather than hiding them in opaque blobs.

That keeps the spec-like surface clean while still preserving the source
mapping needed for traceability.

## Minimal Pattern

```python
from hla.rti1516e.spec import FederateAmbassadorSpec


class MyFederate(FederateAmbassadorSpec):
    def time_advance_grant(self, logical_time):
        print("granted", logical_time)
```

The camelCase callback names remain available for compatibility, but the
snake_case overrides are the intended Python style.

## Read Next

1. [`package_dependency_tree.md`](package_dependency_tree.md)
2. [`package_layout.md`](package_layout.md)
3. [`../packages/hla-rti1516e/README.md`](../packages/hla-rti1516e/README.md)
