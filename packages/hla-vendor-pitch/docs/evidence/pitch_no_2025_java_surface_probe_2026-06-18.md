# Pitch no-2025 Java surface probe

Date: `2026-06-18`

Scope:
- Vendor: `Pitch pRTI Free 5.5.10 build 9905`
- Runtime mode exercised:
  - direct JVM class probe on the vendor classpath
  - direct Py4J gateway launch on the vendor classpath
  - existing Docker-backed CRC/FedPro runtime verified separately on the promoted 2010 path
- Question answered:
  - whether Pitch exposes actual Java `hla.rti1516_2025` classes, independent of this repo's Python backend registry and factory guardrails

## Summary

This probe intentionally bypassed the repo's top-level `rti1516_2025` backend-selection guardrails and asked the vendor JVM directly which Java API surface exists on the Pitch classpath.

Result:
- `hla.rti1516e.RtiFactoryFactory` loads
- `hla.rti1516e.RTIambassador` loads
- `hla.rti1516_2025.RtiFactoryFactory` does not load
- `hla.rti1516_2025.RTIambassador` does not load

Conclusion:
- the current Pitch vendor bundle exposes the Java 2010 API surface only
- the absence of a `2025` route is not only a local Python registry decision
- forcing `rti1516_2025` through Pitch would overclaim vendor capability because the `hla.rti1516_2025` classes are not present in the vendor jars

## Why this probe was needed

The repo already rejects:
- `create_rti_ambassador("pitch-jpype", spec="rti1516_2025")`
- `create_rti_ambassador("pitch-py4j", spec="rti1516_2025")`

Those rejections come from repo-owned plugin metadata and bridge factories:
- `packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/plugin.py`
- `packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/plugin.py`
- `packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/factory.py`
- `packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/factory.py`

This note records the deeper check so future work does not need to repeat it.

## Probe method

Two direct checks were performed against the vendor bundle under:
- `third_party/pitch/PITCH-prti1516e-manual/lib`

### 1. Jar-content scan

The vendor jars were inspected directly for canonical entry points.

Observed:
- multiple jars contained:
  - `hla/rti1516e/RTIambassador.class`
  - `hla/rti1516e/RtiFactoryFactory.class`
- no jar contained:
  - `hla/rti1516_2025/RTIambassador.class`
  - `hla/rti1516_2025/RtiFactoryFactory.class`

### 2. Direct JVM class loading

A Py4J gateway JVM was launched on the raw Pitch classpath using the vendor-bundled Java runtime from `discover_pitch_runtime()`. The probe then called:

```python
java.lang.Class.forName("hla.rti1516e.RtiFactoryFactory")
java.lang.Class.forName("hla.rti1516e.RTIambassador")
java.lang.Class.forName("hla.rti1516_2025.RtiFactoryFactory")
java.lang.Class.forName("hla.rti1516_2025.RTIambassador")
```

Observed:
- `hla.rti1516e.RtiFactoryFactory`: load success
- `hla.rti1516e.RTIambassador`: load success
- `hla.rti1516_2025.RtiFactoryFactory`: `ClassNotFoundException`
- `hla.rti1516_2025.RTIambassador`: `ClassNotFoundException`

Representative failure shape:

```text
java.lang.ClassNotFoundException: hla.rti1516_2025.RtiFactoryFactory
java.lang.ClassNotFoundException: hla.rti1516_2025.RTIambassador
```

## Additional runtime note

The existing Docker-backed Pitch route was also exercised on the promoted 2010 path during the same investigation by attaching tests to the managed container rather than launching a second competing CRC container.

That confirms:
- Pitch works here as a real 2010 Docker/FedPro runtime
- this probe does not indicate a general Pitch failure
- the negative result is specifically about the absence of a Java `2025` API surface

## Operational implication

Do not reopen the question "maybe Pitch secretly exposes `hla.rti1516_2025` classes in the jar" unless the vendor bundle changes.

For the current bundled Pitch version, the answer is already established:
- no `hla.rti1516_2025` Java surface is present
- any future `2025` claim for Pitch would require a new vendor bundle and a fresh direct JVM probe
