# Pitch 202X Surface Audit

- vendor: `Pitch pRTI Free`
- bundled runtime version: `Pitch pRTI Free v 5.5.10`
- bundled 202X API marker: `202X-240403`
- adapter readiness: `surface-close-bridge-blocked`

This report compares the bundled Pitch `hla.rti1516_202X` Java API source tree
against the repo-owned `hla.rti1516_2025` Python protocol surface.

## RTIambassador

- vendor overload total: `205`
- repo overload total: `215`
- shared method names: `178`
- vendor-only method names: `0`
- repo-only method names: `10`
- overload-count mismatches: `0`

### Vendor-only method names

- none

### Repo-only method names

- `decodeAttributeHandle`
- `decodeDimensionHandle`
- `decodeFederateHandle`
- `decodeInteractionClassHandle`
- `decodeMessageRetractionHandle`
- `decodeObjectClassHandle`
- `decodeObjectInstanceHandle`
- `decodeParameterHandle`
- `decodeRegionHandle`
- `getTimeFactory`

## FederateAmbassador

- vendor overload total: `62`
- repo overload total: `62`
- shared method names: `56`
- vendor-only method names: `0`
- repo-only method names: `0`
- overload-count mismatches: `0`

### Vendor-only method names

- none

### Repo-only method names

- none

## Bridge Blockers

- `packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/factory.py`: Factory selection is hardwired to hla.rti1516e.RtiFactoryFactory instead of a profile-driven package name.
- `packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/factory.py`: Factory selection is hardwired to hla.rti1516e.RtiFactoryFactory instead of a profile-driven package name.
- `packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py`: Federate ambassador proxy creation is hardwired to the 2010 Java interface package.
- `packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py`: Federate ambassador proxy creation is hardwired to the 2010 Java interface package.
- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`: Common conversion and callback dispatch code imports 2010 enums, exceptions, handles, time classes, and API metadata directly.
- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_factory_selection.py`: Generic Java RTI discovery is still implemented as a 2010-only factory probe.

## Conclusion

The method-set comparison is close enough to treat Pitch `202X` as a serious candidate
for a future adapter lane, but the current Java bridge stack is still 2010-shaped.
A safe vendor route needs profile-driven factory selection, proxy creation, and value conversion
before it can expose `202X` without overclaiming `2025` support.
