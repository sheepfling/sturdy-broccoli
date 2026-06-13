# hla2010-rti-java-py4j

Generic Py4J-backed Java RTI bridge package for `hla2010-spec`.

This package owns the reusable Java gateway bridge mechanics and the generic
`py4j` backend plugin used by vendor-specific RTI plugins such as Pitch and
Portico. Vendor plugins provide runtime discovery and RTI factory options; this
package provides the Py4J adapter, runtime, factory, and generic plugin
descriptor.
Import the canonical implementation from `hla2010_rti_java_py4j`.
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

Then add the Py4J bridge extras:

```bash
HLA2010_BOOTSTRAP_EXTRAS=py4j ./tools/bootstrap python
```

Minimal import shape:

```python
from py4j.java_gateway import CallbackServerParameters, GatewayParameters, JavaGateway
from hla2010_rti_java_py4j import Py4JConfig, rti_ambassador

gateway = JavaGateway(
    gateway_parameters=GatewayParameters(address="127.0.0.1", port=25333, auto_convert=True),
    callback_server_parameters=CallbackServerParameters(port=0),
)
gateway.start_callback_server()
rti = rti_ambassador(Py4JConfig(gateway=gateway))
```

Operational notes:

- Py4J uses a separate JVM gateway process.
- `gateway_parameters` and `callback_server_parameters` must match the actual
  running gateway.
- this package does not launch a vendor gateway for you; vendor packages such as
  Pitch or Portico own that runtime-specific step.

Expected not-configured-yet behavior:

- `Py4J backend requested, but py4j is not installed`
- a gateway-connection or JVM-side factory failure if the gateway exists but no
  real RTI classes are on its classpath

Use this package for generic bridge mechanics. For the broader route choice and
install order, see:

- [`../../docs/java_backends_quickstart.md`](../../docs/java_backends_quickstart.md)
- [`../../docs/install_matrix.md`](../../docs/install_matrix.md)
- [`../../docs/backend_decision_tree.md`](../../docs/backend_decision_tree.md)
