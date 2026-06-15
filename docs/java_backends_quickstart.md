# Java Backends Quickstart

Start with the Python RTI first.

This repo supports Java-adjacent routes, but they are not the first-run path.
Bootstrap Python, run a pure-Python example, and only then add Java bridge or
vendor runtime pieces.

## Start With Python RTI

Use this order:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
python examples/target_radar_simulation.py --backend python --steps 5
```

If that path does not work yet, stop there and fix it before touching JPype,
Py4J, CERTI, Pitch, or Portico.

## What "Java Shim" Means

The `java-shim-jpype` and `java-shim-py4j` routes are bridge-mechanics proofs.

They are useful when you need:

- callback-shape parity
- adapter plumbing checks
- factory or bridge debugging without a real vendor RTI

They are not a real vendor runtime.

## What JPype Means

JPype loads a JVM in-process and uses the generic bridge package:

```python
from hla2010_rti_java_jpype import JPypeConfig, rti_ambassador
```

Minimal shape:

```python
from hla2010_rti_java_jpype import JPypeConfig, rti_ambassador

config = JPypeConfig(
    classpath=["/path/to/vendor.jar"],
    rti_factory_name=None,
)
rti = rti_ambassador(config)
```

Install path:

```bash
HLA2010_BOOTSTRAP_EXTRAS=jpype ./tools/bootstrap python
```

Use JPype when you want:

- one process
- direct in-process JVM attachment
- no separate gateway process to manage

## What Py4J Means

Py4J talks to a separate JVM gateway and uses the generic bridge package:

```python
from hla2010_rti_java_py4j import Py4JConfig, rti_ambassador
```

Minimal shape:

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

Install path:

```bash
HLA2010_BOOTSTRAP_EXTRAS=py4j ./tools/bootstrap python
```

Use Py4J when you want:

- a separate JVM process
- an explicit gateway lifecycle
- easier process-boundary debugging than in-process JPype

## What CERTI, Pitch, And Portico Mean

- `certi`: real CERTI runtime with the native helper path
- `pitch-jpype` and `pitch-py4j`: Pitch pRTI plus a Java bridge layer
- `portico-jpype` and `portico-py4j`: Portico plus a Java bridge layer

Those are real-runtime or vendor-runtime routes, not first-run routes.

## Which Paths Require Real Vendor Installs

These routes need more than bridge dependencies:

- `certi`
- `pitch-jpype`, `pitch-py4j`
- `portico-jpype`, `portico-py4j`

Use the repo operator wrappers for vendor preflight:

```bash
./tools/certi-easy preflight
./tools/pitch preflight
```

For install order and backend-family mapping, see
[install_matrix.md](install_matrix.md).

For the full route inventory, see
[backend_route_inventory.md](backend_route_inventory.md).

## Common Failure Messages

The bridge packages already expose honest local failure modes.

Typical examples:

- `JPype backend requested, but jpype is not installed`
- `Py4J backend requested, but py4j is not installed`
- `Pitch pRTI runtime not found; set HLA2010_PITCH_HOME to the extracted runtime`
- `Portico runtime at ... does not contain RTI jars`

Operational interpretation:

- missing `jpype1` or `py4j`: rerun bootstrap with the matching extras
- no usable Java runtime: set `JAVA_HOME` or `JDK_HOME`, or install a local JDK
- missing classpath or jars: the bridge exists, but the real RTI runtime is not configured yet
- no Py4J gateway listener: the gateway process or port setup is incomplete

## How To Fall Back To Python RTI

If the Java route is blocked, go back to the supported baseline:

```bash
python examples/target_radar_simulation.py --backend python --steps 5
```

That keeps API, scenario, and traceability work moving while bridge or vendor
setup is still incomplete.

## Read Next

1. [backend_decision_tree.md](backend_decision_tree.md)
2. [install_matrix.md](install_matrix.md)
3. [backend_route_inventory.md](backend_route_inventory.md)
