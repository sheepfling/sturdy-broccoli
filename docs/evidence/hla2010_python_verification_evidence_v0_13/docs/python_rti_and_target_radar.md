# Python RTI + Java RTI backend symmetry

This update adds a dependency-free Python RTI backend while preserving the Java
RTI adapter path through JPype and Py4J. Application federates use the same
`RTIambassador` / `FederateAmbassador` calls regardless of backend.

## Backend choices

```python
from hla.rti1516e.rti import create_rti_ambassador
from hla.rti1516e.backends.python_rti import InMemoryRTIEngine

# Multiple federates in the same local Python RTI share one engine.
engine = InMemoryRTIEngine()
target_rti = create_rti_ambassador("python", engine=engine)
radar_rti = create_rti_ambassador("python", engine=engine)

# Real Java RTI through JPype.
java_rti = create_rti_ambassador(
    "jpype",
    classpath=["/path/to/vendor-rti.jar"],
)

# Real Java RTI through Py4J.
py4j_rti = create_rti_ambassador(
    "py4j",
    gateway_parameters={"address": "127.0.0.1", "port": 25333},
    callback_server_parameters={"port": 0},
)
```

The Python backend is a practical subset for development and local testing. It
implements connection/join/resign/destroy, object and interaction publish /
subscribe, object registration, attribute reflection, interaction delivery,
`requestAttributeValueUpdate`, callback draining, basic logical-time grants,
basic DDM region handles, and common support-service handle/name lookups.

The Java backends still use the same `DelegatingRTIAmbassador` facade, but pass
calls to a vendor Java `hla.rti1516e.RTIambassador` through JPype or Py4J. For
CI and local proof, `java-shim-jpype` and `java-shim-py4j` use a shared
Java-shaped in-process shim that exercises the same Java conversion path without
requiring a vendor RTI.

## Target/Radar scenario

The new scenario has two federates:

| Federate | Publishes | Subscribes | Behavior |
|---|---|---|---|
| `TargetFederate` | `HLAobjectRoot.Target` attributes: `Position`, `Velocity`, `RCS` | attribute-value-update requests | Moves a single target and answers RCS requests through `provideAttributeValueUpdate`. |
| `RadarFederate` | `HLAobjectRoot.Track` and `HLAinteractionRoot.TrackReport` | target attributes | Discovers targets, receives position/velocity, requests RCS, computes range/bearing, updates a Track object, and sends TrackReport interactions. |

Run it with the Python RTI:

```bash
PYTHONPATH=. python examples/target_radar_simulation.py --backend python --steps 5 --dt 1.0
```

Run the same federate code through the Java adapter path using the in-process
JPype/Py4J-profile shims:

```bash
PYTHONPATH=. python examples/target_radar_simulation.py --backend java-shim-jpype --steps 3
PYTHONPATH=. python examples/target_radar_simulation.py --backend java-shim-py4j --steps 3
```

Programmatic use:

```python
from hla.rti1516e.scenarios.target_radar import run_target_radar_scenario

result = run_target_radar_scenario(steps=5, dt=1.0)
for report in result.track_reports:
    print(report.track_id, report.range_m, report.rcs_square_meters)
```

A draft FOM module for vendor Java RTI experiments is included at
`examples/target_radar/TargetRadarFOMmodule.xml`. Real Java RTI integration may
need a vendor-specific startup wrapper for FOM-module URL arrays, logical-time
factories, or handle-set/map factories; those hooks belong in `JavaBridge`,
`JavaValueConverter`, or a `JavaRTIBackend` subclass, not in the scenario
federate code.

## Validation

The package test suite covers:

* backend-neutral delegation;
* Java-shaped JPype/Py4J shim smoke tests;
* the in-memory Python RTI with two federates sharing one engine;
* the target/radar scenario producing track data on the Python RTI;
* the same target/radar scenario through the shared JPype-profile and
  Py4J-profile Java shim paths.

Current result: `16 passed, 2 skipped` in this sandbox.
