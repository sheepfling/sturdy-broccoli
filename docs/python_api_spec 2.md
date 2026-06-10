# Python API Spec

If you want the cleanest Python surface for this workspace, start here:

- [`src/hla2010/spec/`](../src/hla2010/spec/): standalone clean Python spec package
- [`src/hla2010/spec_inventory.py`](../src/hla2010/spec_inventory.py): plain-text method inventory used by the clean spec layer
- [`src/hla2010/spec_sources.py`](../src/hla2010/spec_sources.py): readable Java/C++ source locations surfaced in the spec docstrings
- [`src/hla2010/runtime_api.py`](../src/hla2010/runtime_api.py): explicit runtime-facing convenience layer
- [`src/hla2010/api.py`](../src/hla2010/api.py): compatibility shim that re-exports the runtime layer
- [`src/hla2010/spec_refs.py`](../src/hla2010/spec_refs.py): clause and service references used for traceability

## Recommended Imports

For new Python code, prefer the spec module:

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

- `spec_inventory.py` keeps the method names in a small plain-text module.
- `spec_sources.py` keeps the Java and C++ source locations readable and lets the spec package surface them in docstrings.
- `_spec_impl.py` is the implementation module behind `hla2010.spec`.
- `runtime_api.py` keeps the current runtime adapters working without forcing consumers to read the raw scaffold.
- `api.py` remains as a compatibility shim for older imports.

That keeps the spec-like surface clean while still preserving the source mapping needed for traceability.

## Minimal Pattern

```python
from hla2010.spec import FederateAmbassadorSpec


class MyFederate(FederateAmbassadorSpec):
    def time_advance_grant(self, logical_time):
        print("granted", logical_time)
```

The camelCase callback names remain available for compatibility, but the snake_case overrides are the intended Python style.
