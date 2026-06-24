# Python API Spec

Use this page when you want the clean public Python surface for the HLA 2010
interface without reading the full workspace layout first.

## Front Door

If you only need the supported import ladder, use:

- `from hla.rti1516e import RTIambassador, FederateAmbassador, NullFederateAmbassador`
- `from hla.runtime.rti1516e_ambassador import RTIambassador`
- `from hla.rti1516e.federate_ambassador import FederateAmbassador`
- `from hla.backends.inmemory import rti_ambassador`
- `python examples/target_radar_simulation.py --backend python1516e --steps 5`

## Package Reality

- installable root: `hla-rti1516e`
- versioned API root: `packages/hla-rti1516e/src/hla/rti1516e/`
- package-owned implementations: `packages/*/src/...`

The installable root owns the 2010 strict API surface and spec-facing support
modules. Cross-version discovery and factory selection live under `hla.rti`.

## Canonical Files

- [`../packages/hla-rti1516e/README.md`](../packages/hla-rti1516e/README.md): installable root package role
- [`../packages/hla-rti1516e/src/hla/rti1516e/rti_ambassador.py`](../packages/hla-rti1516e/src/hla/rti1516e/rti_ambassador.py): strict source-shaped `RTIambassador` protocol
- [`../packages/hla-rti1516e/src/hla/rti1516e/federate_ambassador.py`](../packages/hla-rti1516e/src/hla/rti1516e/federate_ambassador.py): strict source-shaped `FederateAmbassador` protocol and no-op callback sink
- [`../packages/hla-rti1516e/src/hla/rti1516e/api.py`](../packages/hla-rti1516e/src/hla/rti1516e/api.py): convenience re-export module for the strict surface
- [`../packages/hla-rti-core/src/hla/spec/inventory.py`](../packages/hla-rti-core/src/hla/spec/inventory.py): plain-text method inventory used by the spec layer
- [`../packages/hla-rti-core/src/hla/spec/sources.py`](../packages/hla-rti-core/src/hla/spec/sources.py): readable Java/C++ source locations surfaced in docstrings
- [`../packages/hla-rti-core/src/hla/spec/refs.py`](../packages/hla-rti-core/src/hla/spec/refs.py): clause and service references used for traceability
- [`../packages/hla-rti-core/src/hla/runtime/rti1516e.py`](../packages/hla-rti-core/src/hla/runtime/rti1516e.py): version-local backend-discovery and ambassador-factory helper

## Import Table

| Use case | Import |
|---|---|
| Canonical 2010 spec contracts | `from hla.rti1516e import RTIambassador, FederateAmbassador` |
| No-op callback base | `from hla.rti1516e import NullFederateAmbassador` |
| Target/Radar example flow | `./tools/target-radar matrix --backend python1516e` |
| Verification harness | `from hla.verification import run_basic_federate_scenario` |

## Recommended Imports

For new Python code, prefer the versioned package root:

```python
from hla.rti1516e import FederateAmbassador, RTIambassador
```

Use `RTIambassador` as the protocol contract for RTI implementations.
Use `FederateAmbassador` as the protocol contract for callback handlers.

If you need an instantiable no-op callback sink:

```python
from hla.rti1516e import NullFederateAmbassador
```

## Why This Layout Exists

- `hla-rti1516e` is the installable root package for the strict spec surface.
- `packages/hla-rti1516e/src/hla/rti1516e/rti_ambassador.py` and `federate_ambassador.py` expose source-shaped protocols.
- `packages/hla-rti1516e/src/hla/rti1516e/api.py` re-exports the strict surface inside the versioned package.
- `packages/hla-rti-core/src/hla/spec/inventory.py`, `sources.py`, and `refs.py` keep source mappings readable rather than hiding them in opaque blobs.

That keeps the spec surface aligned with Java/C++ names while still preserving the source
mapping needed for traceability.

## Minimal Pattern

```python
from hla.rti1516e import FederateAmbassador


class MyFederate(FederateAmbassador):
    def timeAdvanceGrant(self, logical_time):
        print("granted", logical_time)
```

The canonical callback names are the standard lowerCamelCase service names.

## Read Next

1. [`package_dependency_tree.md`](package_dependency_tree.md)
2. [`package_layout.md`](package_layout.md)
3. [`../packages/hla-rti1516e/README.md`](../packages/hla-rti1516e/README.md)
