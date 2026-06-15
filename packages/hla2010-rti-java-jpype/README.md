# hla2010-rti-java-jpype

Generic JPype-backed Java RTI bridge package for `hla2010-spec`.

This package owns the reusable Java bridge mechanics and the JPype-first
standard Java HLA 1516-2010 implementation facade. For a Java RTI that follows
the standard `hla.rti1516e` API, pass the vendor implementation string here and
let the shared adapter wrap the standard classes once. Vendor-specific packages
are only needed for vendor-specific runtime discovery, launch behavior, or API
quirks.
Import the canonical implementation from `hla2010_rti_java_jpype`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_java_plugin_split_packages.py` and
`tests/test_package_boundary.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.

Start with the Python RTI first:

```bash
./tools/bootstrap python
source .venv/bin/activate
python examples/target_radar_simulation.py --backend python --steps 5
```

Then add the JPype bridge extras:

```bash
HLA2010_BOOTSTRAP_EXTRAS=jpype ./tools/bootstrap python
```

Minimal standard-Java RTI import shape:

```python
from hla2010_rti_java import java_2010_rti_ambassador

rti = java_2010_rti_ambassador(
    "com.vendor.hla.RtiFactory",
    classpath=["/path/to/vendor.jar"],
    connect_local_settings_designator="crcHost=localhost",
)
```

Easy configurable shape:

```python
from hla2010_rti_java import JavaRTIImplementation

implementation = JavaRTIImplementation(
    "com.vendor.hla.RtiFactory",
    bridge="jpype",  # or "py4j" when a Py4J gateway is the right process shape
    edition="2010",
    classpath=["/path/to/vendor.jar"],
)

report = implementation.discover()
rti = implementation.create_rti_ambassador()
```

Debug/discovery-only shape:

```python
from hla2010_rti_java import debug_java_rti_implementation

report = debug_java_rti_implementation(
    "com.vendor.hla.RtiFactory",
    bridge="jpype",
    edition="2010",
    classpath=["/path/to/vendor.jar"],
)
assert report.available
print(report.factory_name, report.factory_version, report.hla_version)
print(report.rti_class_name, report.interface_names)
```

Operational notes:

- JPype runs the JVM in-process.
- `classpath` must point at a real RTI jar set before the wrapper can construct
  `hla.rti1516e.RtiFactoryFactory`.
- the first argument is forwarded to
  `RtiFactoryFactory.getRtiFactory(implementation)`.
- `JavaRTIImplementation` carries an `edition` field so newer HLA editions can
  be added without changing the caller-facing shape. Backend construction
  currently accepts `2010`; debug discovery can still report future-edition
  requests with warnings.
- `java_2010_rti_ambassador("java-shim")` selects the in-process Java-shaped
  2010 shim for local test-tool development without a vendor RTI.

Expected not-configured-yet behavior:

- `JPype backend requested, but jpype is not installed`
- a Java/classpath/factory failure if the bridge loads but the real RTI jars are
  not present

Use `hla2010-rti-java-jpype` for generic JPype bridge mechanics. Use
`hla2010-rti-java` for standard Java RTI implementation selection. For the
broader route choice and install order, see:

- [`../../docs/java_backends_quickstart.md`](../../docs/java_backends_quickstart.md)
- [`../../docs/install_matrix.md`](../../docs/install_matrix.md)
- [`../../docs/backend_decision_tree.md`](../../docs/backend_decision_tree.md)
