# Java Bridge Wrapping Guide

Use this guide when you want one place that shows how Python wraps the HLA
surface for both Java bridge routes and both supported editions.

## What To Open

For minimal direct bridge skeletons:

- `examples/jpype_java_rti.py`
- `examples/py4j_java_rti.py`
- `examples/jpype_java_rti_2025.py`
- `examples/py4j_java_rti_2025.py`

For one runnable backend-neutral scenario across both bridges and both editions:

- `examples/java_shim_federate.py`

## Route Matrix

| Edition | JPype | Py4J | Notes |
| --- | --- | --- | --- |
| 2010 | `examples/jpype_java_rti.py` | `examples/py4j_java_rti.py` | Standard Java package root is `hla.rti1516e` |
| 2025 | `examples/jpype_java_rti_2025.py` | `examples/py4j_java_rti_2025.py` | Standard Java package root is `hla.rti1516_2025` |

The runnable shim scenario covers the same matrix with flags:

```bash
python examples/java_shim_federate.py --edition 2010 --bridge jpype
python examples/java_shim_federate.py --edition 2010 --bridge py4j
python examples/java_shim_federate.py --edition 2025 --bridge jpype
python examples/java_shim_federate.py --edition 2025 --bridge py4j
```

## Wrapping Pattern

The wrapping shape is intentionally the same in all four minimal examples:

1. import the edition-specific HLA callback base and enums
2. subclass `NullFederateAmbassador`
3. implement standard lowerCamelCase callback methods
4. build a route config object
5. create `rti_ambassador(...)`
6. call `connect(...)`

The edition difference is the Python package root:

```python
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.enums import CallbackModel
```

```python
from hla.rti1516_2025.federate_ambassador import NullFederateAmbassador
from hla.rti1516_2025.enums import CallbackModel
```

The bridge difference is only the config object and process shape:

```python
from hla.bridges.java.jpype import JPypeConfig
```

```python
from hla.bridges.java.py4j import Py4JConfig
```

## JPype Vs Py4J

Use JPype when Python should own the JVM lifecycle and in-process callbacks are
acceptable.

Use Py4J when Java should stay in a separate JVM or when you want process
isolation between Python and Java.

The normalized wrapper surface on the Python side is the same:

- `rti.connect(...)`
- `rti.create_federation_execution(...)`
- `rti.join_federation_execution(...)`
- `rti.publish_object_class_attributes(...)`
- `rti.send_interaction(...)`

## Edition Differences

2010 and 2025 share the same wrapper strategy, but 2025 adds a broader spec
surface including auth, richer datatypes, and the dedicated Python runtime lane.

The practical difference for bridge examples is:

- 2010 defaults to the `hla.rti1516e` package family
- 2025 sets `java_api_profile="2025"` or `edition="2025"` and imports
  `hla.rti1516_2025`

For direct factory creation, this is the most compact edition-aware shape:

```python
from hla.bridges.java.jpype import JavaRTIImplementation

implementation = JavaRTIImplementation(
    "com.vendor.hla.RtiFactory",
    bridge="jpype",
    edition="2025",
    classpath=["/path/to/vendor.jar"],
)
rti = implementation.create_rti_ambassador()
```

## Recommended Reading Order

1. `examples/java_shim_federate.py`
2. one of the four minimal bridge skeletons
3. `packages/hla-bridge-java-jpype/README.md`
4. `packages/hla-bridge-java-py4j/README.md`
5. `docs/language_shim_routes.md`
