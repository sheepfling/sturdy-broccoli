# Python RTI refinement: FOM URLs, logical time, and collection factories

This iteration moves the in-house RTI from a permissive name registry toward a clean FOM-backed runtime while keeping the same federate-facing API used by Java RTI adapters.

## Design goals

A federate should not care whether it is running against:

- the pure Python in-memory RTI,
- a Java RTI loaded through JPype,
- a Java RTI reached through Py4J, or
- the Java-shaped shim used by tests.

The RTI adapter boundary therefore exposes the same service names and the same factory-style support services across all profiles.

## FOM URL handling

`hla2010.fom` now owns FOM/MIM source normalization and parsing.

Supported source forms:

- local `str` paths,
- `pathlib.Path` values,
- `file:` URLs,
- `http:` and `https:` URLs,
- Java URL/URI-like objects exposed through JPype or Py4J.

The parser builds a compact `FOMCatalog` containing:

- object class names and parent relationships,
- object attributes and data types,
- interaction class names and parent relationships,
- interaction parameters and data types,
- dimensions,
- transportation names,
- the FOM time-stamp and lookahead data types.

When a federation is created with FOM modules, the Python RTI marks the catalog as strict. That means `getObjectClassHandle`, `getAttributeHandle`, `getInteractionClassHandle`, and `getParameterHandle` now reject unknown names with `NameNotFound`. When no FOM modules are supplied, the previous dynamic/test-friendly behavior is preserved.

## Logical-time factory handling

`hla2010.time` now has a simple registry:

```python
from hla2010.time import get_time_factory

factory = get_time_factory("HLAfloat64Time")
time = factory.make_time(1.5)
interval = factory.make_interval(0.1)
```

Built-in factories:

- `HLAinteger64TimeFactory`
- `HLAfloat64TimeFactory`

Common aliases are accepted, such as `HLAinteger64BE`, `HLAfloat64BE`, `int64`, and `double`.

When `createFederationExecution` receives an explicit logical-time implementation name, that name wins. Otherwise the Python RTI uses the loaded FOM catalog's `<time><timeStamp><dataType>...` value. If neither is available, the runtime falls back to `HLAinteger64Time`.

Factories provide both Pythonic and Java-style methods:

```python
factory.make_initial()
factory.makeInitial()
factory.decode_time(encoded)
factory.decodeTime(encoded)
```

## Handle set and map factories

`hla2010.handles` now includes typed containers and factories matching the Java API model:

```python
attribute_set = rti.get_attribute_handle_set_factory().create()
value_map = rti.get_attribute_handle_value_map_factory().create()
```

The Python RTI returns typed Python containers:

- `AttributeHandleSet`
- `DimensionHandleSet`
- `FederateHandleSet`
- `RegionHandleSet`
- `InteractionClassHandleSet`
- `AttributeHandleValueMap`
- `ParameterHandleValueMap`
- `AttributeSetRegionSetPairList`

The containers validate handle types at insertion time. This catches common mistakes early and also mirrors the stricter type behavior federates will see through Java RTIs.

## Java adapter implications

The JPype/Py4J path now has the right extension points for vendor-specific behavior:

- FOM paths can be converted to Java `URL` or `URL[]` values at the bridge layer.
- Python `set`/`dict` values can be converted using RTI-provided Java set/map factories when the resolved Java overload expects those factory-owned types.
- Native Java factory objects returned by `get*Factory` can be passed through or converted into Python equivalents where that is more useful.

This keeps vendor quirks isolated inside `JavaBridge`, `JavaValueConverter`, or a vendor-specific `JavaRTIBackend` subclass.

## Validation

The tests now cover:

- local path and `file:` URL normalization,
- FOM catalog extraction from the Target/Radar FOM,
- strict Python RTI name lookup when FOM modules are supplied,
- FOM-selected `HLAfloat64Time` factory behavior,
- logical-time advance grants using `HLAfloat64Time`,
- typed handle set/map factories,
- the Target/Radar scenario on Python, Java-shim-JPype, and Java-shim-Py4J profiles.
