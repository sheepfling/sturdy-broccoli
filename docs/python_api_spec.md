# Python API Spec

Use this page when you want the clean public Python surface for the HLA 2010
interface without reading the full workspace layout first.

## Front Door

If you only need the supported import ladder, use:

- `from hla.spec import RTIambassadorSpec, FederateAmbassadorSpec`
- `import hla; hla.select_edition("2010")`
- `from hla.runtime_api import RTIambassador, FederateAmbassador`
- `from hla2010.spec import RTIambassadorSpec, FederateAmbassadorSpec`
- `from hla2010.runtime_api import RTIambassador, FederateAmbassador`
- `from hla2010_rti_python import rti_ambassador`
- `from hla2010_fom_target_radar.scenarios import run_target_radar_scenario`

## Package Reality

- installable root: `hla2010-spec`
- neutral source root: `packages/hla2010-spec/src/hla/`
- 2010 compatibility source root: `packages/hla2010-spec/src/hla2010/`
- package-owned implementations: `packages/*/src/...`

The installable root owns the abstract API surface and spec-facing support
modules. The package-owned spec source root keeps stable imports and only narrow documented
temporary compatibility routing across the split packages.

## Canonical Files

- [`../packages/hla2010-spec/README.md`](../packages/hla2010-spec/README.md): installable root package role
- [`../packages/hla2010-spec/src/hla2010/spec/__init__.py`](../packages/hla2010-spec/src/hla2010/spec/__init__.py): clean abstract/prototype spec surface
- [`../packages/hla2010-spec/src/hla2010/runtime_api.py`](../packages/hla2010-spec/src/hla2010/runtime_api.py): runtime-facing convenience facade
- [`../packages/hla2010-spec/src/hla2010/api.py`](../packages/hla2010-spec/src/hla2010/api.py): compatibility shim that re-exports the runtime layer
- [`../packages/hla2010-spec/src/hla2010/spec_inventory.py`](../packages/hla2010-spec/src/hla2010/spec_inventory.py): plain-text method inventory used by the spec layer
- [`../packages/hla2010-spec/src/hla2010/spec_sources.py`](../packages/hla2010-spec/src/hla2010/spec_sources.py): readable Java/C++ source locations surfaced in docstrings
- [`../packages/hla2010-spec/src/hla2010/spec_refs.py`](../packages/hla2010-spec/src/hla2010/spec_refs.py): clause and service references used for traceability
- [`../packages/hla2010-spec/src/hla2010/rti.py`](../packages/hla2010-spec/src/hla2010/rti.py): temporary backend-discovery and ambassador-factory compatibility facade over the split runtime-common package

## Import Table

| Use case | Import |
|---|---|
| Neutral spec contracts | `from hla.spec import RTIambassadorSpec, FederateAmbassadorSpec` |
| Neutral runtime convenience facade | `from hla.runtime_api import RTIambassador, FederateAmbassador` |
| Explicit edition selection | `import hla; hla.select_edition("2010")` |
| Abstract spec contracts | `from hla2010.spec import RTIambassadorSpec, FederateAmbassadorSpec` |
| Runtime convenience facade | `from hla2010.runtime_api import RTIambassador, FederateAmbassador` |
| Scenario / FOM entrypoint | `from hla2010_fom_target_radar.scenarios import run_target_radar_scenario` |
| Verification harness | `from hla2010_verification_harness import run_basic_federate_scenario` |

## Recommended Imports

For new Python code, prefer the neutral spec module:

```python
from hla.spec import RTIambassadorSpec, FederateAmbassadorSpec
```

If you want the neutral namespace to state the edition explicitly:

```python
import hla

hla.select_edition("2010")
from hla.spec import RTIambassadorSpec, FederateAmbassadorSpec
```

The legacy 2010 compatibility path remains:

```python
from hla2010.spec import RTIambassadorSpec, FederateAmbassadorSpec
```

Use `RTIambassadorSpec` as the abstract contract for RTI implementations.
Use `FederateAmbassadorSpec` as the no-op prototype base for callback handlers.

If you want the runtime convenience layer instead of the pure contract layer:

```python
from hla2010.runtime_api import RTIambassador, FederateAmbassador
```

## Why This Split Exists

- `hla2010-spec` is the installable root package for the clean spec surface.
- `packages/hla2010-spec/src/hla2010/spec/__init__.py` exposes the abstract base classes and prototypes.
- `packages/hla2010-spec/src/hla2010/runtime_api.py` keeps the runtime adapters working without forcing callers onto raw source-derived names.
- `packages/hla2010-spec/src/hla2010/api.py` remains as a compatibility shim for older imports.
- `packages/hla2010-spec/src/hla2010/rti.py` remains only as a temporary documented compatibility facade for backend discovery, backend selection, and ambassador creation while backend contracts and runtime internals live in split packages.
- For human-friendly backend selection, prefer `iter_rti_factories()` to list installed factories and `get_rti_factory(name)` to resolve one by canonical name or alias before calling `factory.create_rti_ambassador(...)`.
- `packages/hla2010-spec/src/hla2010/spec_inventory.py`, `packages/hla2010-spec/src/hla2010/spec_sources.py`, and `packages/hla2010-spec/src/hla2010/spec_refs.py` keep source mappings readable rather than hiding them in opaque blobs.

That keeps the spec-like surface clean while still preserving the source
mapping needed for traceability.

## Minimal Pattern

```python
from hla2010.spec import FederateAmbassadorSpec


class MyFederate(FederateAmbassadorSpec):
    def time_advance_grant(self, logical_time):
        print("granted", logical_time)
```

The camelCase callback names remain available for compatibility, but the
snake_case overrides are the intended Python style.

## Read Next

1. [`package_dependency_tree.md`](package_dependency_tree.md)
2. [`package_layout.md`](package_layout.md)
3. [`../packages/hla2010-spec/README.md`](../packages/hla2010-spec/README.md)
