# v0.9 startup, synchronization, FOM loading, and Java translation work

This release moves the project closer to a compliant HLA 1516.1-2010 shape while keeping the pure Python RTI clearly marked as a local development/reference RTI.

## Section anchors

| Area | HLA 1516.1-2010 section anchors | Implementation |
|---|---|---|
| Connect/disconnect startup | §4.2, §4.3 | `hla2010.startup.connect_create_join`, `PythonRTIBackend._svc_connect`, `_svc_disconnect` |
| Federation creation and FDD loading | §4.1.4, §4.1.4.1, §4.1.4.2, §4.5 | `hla2010.fom.FOMResolver`, `merge_fom_modules`, `PythonRTIBackend._svc_createFederationExecution` |
| Join and FOM module extension | §4.9 | `PythonRTIBackend._svc_joinFederationExecution` |
| Synchronization points | §4.11-§4.15 | `SynchronizationPointState`, register/announce/achieve/federation-synchronized paths |
| Java API FOM designators | Java binding uses `URL` / `URL[]` FOM designators | `module_uri`, `JavaBridge.fom_url`, `JavaValueConverter.to_backend(... expected_type_name="URL[]")` |
| Handle set/map factories | Support service factory area in the Java binding | `hla2010.handles` factories and `JavaBridge.new_handle_set/new_handle_value_map` |
| Java callback translation | RTI-initiated FederateAmbassador services | `PythonFederateAmbassadorDispatcher`, `expected_java_callback_parameter_types` |

## Startup helper

`hla2010.startup` now provides a single readable startup path for examples and tests:

```python
from hla2010.ambassadors import RecordingFederateAmbassador
from hla2010.rti import create_rti_ambassador
from hla2010.startup import FederationStartupConfig, connect_create_join, synchronize_ready_to_run

rti = create_rti_ambassador("python")
fed = RecordingFederateAmbassador()
config = FederationStartupConfig.target_radar(
    federation_name="TargetRadarFederation",
    federate_name="Radar",
    federate_type="RadarFederate",
)

connect_create_join(rti, fed, config)
```

The helper is deliberately a thin wrapper. It still calls `connect`, `createFederationExecution`, `joinFederationExecution`, `registerFederationSynchronizationPoint`, `synchronizationPointAchieved`, and callback-evoke services on the same backend-neutral ambassador.

## Synchronization behavior

The pure Python RTI now tracks each synchronization point with an explicit `SynchronizationPointState` containing:

- label and tag
- registering federate
- target synchronization set
- announced set
- achieved set
- failed set
- whole-federation/late-joiner flag

For whole-federation synchronization points, federates that join after registration but before completion are now announced the open point and added to the completion condition. The RTI does not emit `federationSynchronized` until every current member of the synchronization set has reported achieved or failed. The callback carries a typed `FederateHandleSet` for failures.

## FOM discovery and loading

`hla2010.fom` now supports these FOM/MIM designator forms:

- absolute and relative filesystem paths
- `file:` URLs
- remote URL-like values such as `http:` and `https:` for Java pass-through
- package resources using `hla2010:TargetRadarFOMmodule.xml`
- explicit `FOMModule` objects
- built-in `HLAstandardMIM` placeholder for local startup

The Python RTI resolves local FOMs into a merged `FOMCatalog`; Java RTI backends receive normalized URL strings/arrays. `FOMCatalog.as_summary()` now exposes module URIs so tests and tools can show exactly what FDD input was loaded.

Strict modes are opt-in:

```python
from hla2010.backends.python_rti import PythonRTIConfig

config = PythonRTIConfig(
    strict_fom_loading=True,   # fail when a local FOM cannot be parsed
    strict_fom_lookup=True,    # reject object/interaction/attribute/parameter names absent from the FDD
    require_fom_modules=True,  # require at least one non-MIM FOM on creation
)
```

Default mode remains permissive so local experiments and earlier tests can create minimal federations without a FOM.

## Java translation hardening

The Java adapter now handles more vendor-realistic return and callback objects:

- vendor implementation class names such as `VendorObjectInstanceHandleImpl` map back to the correct Python handle type
- callback arguments are converted using Java FederateAmbassador parameter metadata, so maps and sets are converted into typed Python collections
- `AttributeHandleValueMap`, `ParameterHandleValueMap`, and `FederateHandleSet` are reconstructed from Java-like maps/sets
- bytes, Java enum constants, logical times, and native handles continue to round-trip through the shared converter

This is important for JPype/Py4J because a real vendor RTI often returns concrete implementation objects instead of exactly named `hla.rti1516e.*` interface proxies.

## Validation added

New tests cover:

- late joiner announcement for an open whole-federation synchronization point
- strict FOM loading from the bundled Target/Radar FOM
- startup helper create/join/synchronize flow
- Java converter recognition of vendor-style handle implementation names and typed handle maps/sets

Current result in this runtime:

```text
36 passed, 2 skipped
```

The skipped tests remain the optional real JPype/Py4J integration tests because those packages and a vendor RTI are not installed in this sandbox.
