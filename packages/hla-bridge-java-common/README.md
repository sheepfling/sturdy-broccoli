# hla-bridge-java-common

Shared Java RTI support package for `hla-rti1516e`.

This package owns the bridge-independent Java adapter policy used by JPype,
Py4J, CERTI Java-profile code, and the in-process Java shim: callback
dispatching, overload resolution, Java value conversion, and the shared
`JavaRTIBackend` base.
Import the canonical implementation from `hla.bridges.java.common`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_java_common_split_package.py`,
`tests/test_rti_java_runtime_split_package.py`, and
`tests/test_package_boundary.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.

## Bridge-neutral factory selection

Use `create_java_rti_ambassador` when caller code should choose the Java bridge
and vendor RTI implementation at runtime:

```python
from hla.bridges.java.common import create_java_rti_ambassador, discover_java_rti

rti = create_java_rti_ambassador(
    bridge="jpype",
    implementation="com.vendor.hla.RtiFactory",
    classpath=("vendor-rti.jar",),
    connect_local_settings_designator="crcHost=localhost",
)

report = discover_java_rti(
    bridge="jpype",
    implementation="com.vendor.hla.RtiFactory",
    classpath=("vendor-rti.jar",),
)
```

The `implementation` string is forwarded to
`hla.rti1516e.RtiFactoryFactory.getRtiFactory(implementation)` by the selected
bridge package. Use `bridge="py4j"` with Py4J gateway options to select the
Py4J-backed adapter instead. `discover_java_rti` returns a
`JavaRTIDiscoveryReport` with factory name/version, reported HLA version,
runtime class name, visible Java interface names, warnings, and any bridge
failure details.

For the in-process Java-shaped 2010 shim, use the same entry point with the
reserved shim implementation name:

```python
rti = create_java_rti_ambassador(
    bridge="jpype",  # or "py4j"
    implementation="java-shim",
)
```

The shorthand bridge names `java-shim-jpype` and `java-shim-py4j` select the
same shim profiles without requiring a separate vendor factory string.

The Rosetta `java-standard-*` names are reserved for future standard-backed
shim jars that compile against the official IEEE Java API bundles. They are not
aliases for the in-process Java-shaped test shim.
