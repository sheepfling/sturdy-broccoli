# hla2010-rti-java-jpype

Generic JPype-backed Java RTI bridge package for `hla2010-spec`.

This package owns the reusable Java bridge mechanics and the generic `jpype`
backend plugin used by vendor-specific RTI plugins such as Pitch and Portico.
Vendor plugins provide runtime discovery and RTI factory options; this package
provides the JPype adapter, runtime, factory, and generic plugin descriptor.
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

Minimal import shape:

```python
from hla2010_rti_java_jpype import JPypeConfig, rti_ambassador

config = JPypeConfig(
    classpath=["/path/to/vendor.jar"],
    rti_factory_name=None,
)
rti = rti_ambassador(config)
```

Operational notes:

- JPype runs the JVM in-process.
- `classpath` must point at a real RTI jar set before `rti_ambassador(...)`
  can construct `hla.rti1516e.RtiFactoryFactory`.
- `rti_factory_name` is optional and only matters when the RTI vendor exposes
  multiple factory names.

Expected not-configured-yet behavior:

- `JPype backend requested, but jpype is not installed`
- a Java/classpath/factory failure if the bridge loads but the real RTI jars are
  not present

Use this package for generic bridge mechanics. For the broader route choice and
install order, see:

- [`../../docs/java_backends_quickstart.md`](../../docs/java_backends_quickstart.md)
- [`../../docs/install_matrix.md`](../../docs/install_matrix.md)
- [`../../docs/backend_decision_tree.md`](../../docs/backend_decision_tree.md)
