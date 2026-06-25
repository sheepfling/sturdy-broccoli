# HLA Interface Contracts

The canonical 2010 Python contract in this repo follows the Java-shaped HLA
surface: standard RTI services and federate callbacks are exposed with
lowerCamelCase names.

The contract authority for that surface is the standard-facing package code:

- [`packages/hla-rti1516e/src/hla/rti1516e/raw_api.py`](../../packages/hla-rti1516e/src/hla/rti1516e/raw_api.py)
- [`packages/hla-rti1516e/src/hla/rti1516e/rti_ambassador.py`](../../packages/hla-rti1516e/src/hla/rti1516e/rti_ambassador.py)
- [`packages/hla-rti1516e/src/hla/rti1516e/federate_ambassador.py`](../../packages/hla-rti1516e/src/hla/rti1516e/federate_ambassador.py)

Examples of canonical service names:

- `createFederationExecution(...)`
- `joinFederationExecution(...)`
- `evokeCallback(...)`
- `evokeMultipleCallbacks(...)`
- `enableCallbacks()`
- `disableCallbacks()`

Examples of canonical callback names:

- `announceSynchronizationPoint(...)`
- `federationSynchronized(...)`
- `timeRegulationEnabled(...)`
- `timeConstrainedEnabled(...)`
- `timeAdvanceGrant(...)`

Runtime compatibility aliases may still exist in some implementation layers
during migration, but they are not the public standard-facing contract.

## Minimal Canonical Example

```python
from hla.backends.python1516e import InMemoryRTIEngine, rti_ambassador
from hla.backends.common import RecordingFederateAmbassador
from hla.rti1516e.enums import CallbackModel

engine = InMemoryRTIEngine()
rti = rti_ambassador(engine=engine)
fed = RecordingFederateAmbassador()

rti.connect(fed, CallbackModel.HLA_EVOKED)
rti.createFederationExecution("example-fed", "TargetRadarFOMmodule.xml")
rti.joinFederationExecution("example", "producer", "example-fed")
rti.evokeMultipleCallbacks(0.0, 0.0)
```
