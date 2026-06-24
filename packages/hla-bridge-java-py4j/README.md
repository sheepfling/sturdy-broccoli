# hla-bridge-java-py4j

Generic Py4J-backed Java RTI bridge package for `hla-rti1516e` and
`hla-rti1516_2025`.

This package owns the reusable Java gateway bridge mechanics and the generic
`py4j` backend plugin used by vendor-specific RTI plugins such as Pitch and
Portico. Vendor plugins provide runtime discovery and RTI factory options; this
package provides the Py4J adapter, runtime, factory, and generic plugin
descriptor for both `hla.rti1516e` and `hla.rti1516_2025` Java API profiles.
Import the canonical implementation from `hla.bridges.java.py4j`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_java_plugin_split_packages.py` and
`tests/test_package_boundary.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.

Minimal 2025 shape:

```python
from hla.bridges.java.py4j import Py4JConfig, rti_ambassador

config = Py4JConfig(
    gateway_parameters={"address": "127.0.0.1", "port": 25333},
    java_api_profile="2025",
    rti_factory_name="com.vendor.hla.RtiFactory",
)
rti = rti_ambassador(config)
```

See `examples/py4j_java_rti_2025.py` for a callback skeleton.
See [`../../docs/java_bridge_wrapping_guide.md`](../../docs/java_bridge_wrapping_guide.md)
for the cross-edition, cross-route wrapping guide.
