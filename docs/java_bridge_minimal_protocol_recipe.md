# Java Bridge Minimal Protocol Recipe

Use this document when the question is:

"What is the lightest possible way to wrap a standard Java RTI through JPype or
Py4J without getting lost in the full architecture?"

This is the shortest teaching version of the wrapping model.

This document belongs to the backend and route wrapping surface described in
[`work_surfaces.md`](work_surfaces.md).

If your real question is overload choice rather than bootstrap shape, read
[`java_bridge_overload_resolution.md`](java_bridge_overload_resolution.md)
after this page.

## The Core Idea

For both JPype and Py4J, the minimum protocol shape is:

1. import the edition-local callback base and `CallbackModel`
2. subclass `NullFederateAmbassador`
3. implement Java-standard lowerCamelCase callback names
4. build the route config
5. call `rti_ambassador(...)`
6. call `connect(...)`

Everything else is detail.

One of those details matters a lot for this project: the repo does not rely on
JPype or Py4J alone to guess which Java overload to call. It resolves that
policy in Python first.

## The Minimum JPype Shape

2010:

```python
from hla.bridges.java.jpype import JPypeConfig, rti_ambassador
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.enums import CallbackModel


class MyFederate(NullFederateAmbassador):
    def announceSynchronizationPoint(self, synchronizationPointLabel, userSuppliedTag):
        print("sync point", synchronizationPointLabel, bytes(userSuppliedTag))


config = JPypeConfig(
    classpath=["/path/to/vendor-rti.jar"],
)

rti = rti_ambassador(config)
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
```

What JPype is doing:

- Python owns the JVM
- Python loads Java classes directly
- Python exposes callbacks back to Java through an in-process proxy

## The Minimum Py4J Shape

2010:

```python
from hla.bridges.java.py4j import Py4JConfig, rti_ambassador
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.enums import CallbackModel


class MyFederate(NullFederateAmbassador):
    def timeAdvanceGrant(self, logicalTime):
        print("granted", logicalTime)


config = Py4JConfig(
    gateway_parameters={"address": "127.0.0.1", "port": 25333},
)

rti = rti_ambassador(config)
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
```

What Py4J is doing:

- Java lives behind a gateway
- Python reaches Java through that gateway
- Python exposes callbacks through a Py4J callback object

## The 2025 Delta

The 2025 shape is intentionally the same.

Only three things change:

1. the package root changes from `hla.rti1516e` to `hla.rti1516_2025`
2. the callback base import changes
3. the config sets `java_api_profile="2025"`

Minimal JPype 2025:

```python
from hla.bridges.java.jpype import JPypeConfig, rti_ambassador
from hla.rti1516_2025.enums import CallbackModel
from hla.rti1516_2025.federate_ambassador import NullFederateAmbassador


class MyFederate(NullFederateAmbassador):
    def announceSynchronizationPoint(self, synchronizationPointLabel, userSuppliedTag):
        print("sync point", synchronizationPointLabel, bytes(userSuppliedTag))


config = JPypeConfig(
    classpath=["/path/to/vendor-rti-2025.jar"],
    java_api_profile="2025",
)

rti = rti_ambassador(config)
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
```

Minimal Py4J 2025:

```python
from hla.bridges.java.py4j import Py4JConfig, rti_ambassador
from hla.rti1516_2025.enums import CallbackModel
from hla.rti1516_2025.federate_ambassador import NullFederateAmbassador


class MyFederate(NullFederateAmbassador):
    def timeAdvanceGrant(self, logicalTime):
        print("granted", logicalTime)


config = Py4JConfig(
    gateway_parameters={"address": "127.0.0.1", "port": 25333},
    java_api_profile="2025",
)

rti = rti_ambassador(config)
rti.connect(MyFederate(), CallbackModel.HLA_EVOKED)
```

## What Actually Changes

| Question | 2010 | 2025 | JPype | Py4J |
| --- | --- | --- | --- | --- |
| Java package family | `hla.rti1516e` | `hla.rti1516_2025` | same edition rule | same edition rule |
| Callback base | `hla.rti1516e.NullFederateAmbassador` | `hla.rti1516_2025.federate_ambassador.NullFederateAmbassador` | same | same |
| Config type | edition-local surface unchanged | edition-local surface unchanged | `JPypeConfig` | `Py4JConfig` |
| Extra config field | none | `java_api_profile="2025"` | classpath/JVM-oriented | gateway-oriented |
| Process shape | same HLA callback contract | same HLA callback contract | in-process JVM | separate Java gateway |

## What Does Not Change

These stay the same across both routes and both editions:

- subclass `NullFederateAmbassador`
- use lowerCamelCase callback names
- create `rti = rti_ambassador(config)`
- call `rti.connect(...)`

That is the whole minimal protocol story.

## If You Are Choosing One Route First

Choose JPype first when the goal is to explain or prototype the wrapper.

Reason:

- fewer moving parts
- direct class loading
- easier callback story
- easier to debug the adaptation boundary

Choose Py4J when you specifically need:

- process separation
- an already-running Java process
- gateway-based deployment shape

## Recommended Read Order

1. `examples/jpype_java_rti.py`
2. `examples/py4j_java_rti.py`
3. `examples/jpype_java_rti_2025.py`
4. `examples/py4j_java_rti_2025.py`
5. `docs/java_bridge_wrapping_guide.md`
6. `docs/java_bridge_overload_resolution.md`
7. `docs/java_rti_adaptation_architecture.md`
