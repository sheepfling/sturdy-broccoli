# Final best-of Python package for HLA 1516.1-2025

## Build decision

This package uses the **initial supplied zip as the base** because it had the better
Python package structure and more precise ambassador typing. It then merges the
newer package's broader spec coverage.

## Kept from the initial supplied zip

- Modular package layout.
- Strong `RTIambassador` and `FederateAmbassador` method signatures.
- Explicit `IntEnum` values for the shared HLA enums.
- Full Java-like `ByteWrapper` abstract API.
- `RtiFactoryFactory` and `UnimplementedRTIambassador`.
- Existing handle factories and logical-time Python operators.

## Merged from the newer package

- `auth.py` authorization model.
- `encoding.py` encoding model.
- `AuthorizationResultCode` / `AuthorizationCode`.
- Java/C++ auth classes: `AuthorizationResult`, `Authorizer`, `AuthorizerFactory`, `AuthorizerFactoryFactory`, `HLAnoCredentials`, `HLAplainTextPassword`.
- Encoding classes/protocols: `DataElement`, `DataElementFactory`, `EncoderFactory`, HLA scalar elements, HLA arrays/records/variants, opaque data, encoded handles, encoded logical time wrappers.
- `HLAtransportationTypeHandle` encoding protocol from the newer 1516.1-2025 Java bundle.
- 9 C++-only exception names, including advisory-switch exceptions and `InternalError`.

## Additional cleanup/fixes

- `FederationExecutionInformation.logicalTimeImplementationName` is now the spec-correct field name, with `logicalTimeImplementation` retained as a compatibility alias.
- `RtiConfiguration` now provides Java-style getter methods: `configurationName()`, `rtiAddress()`, and `additionalSettings()`.
- Timed/non-timed object-management calls now return `MessageRetractionReturn | None` instead of always `MessageRetractionReturn`.
- `sendInteractionWithRegions` now has typed `ParameterHandleValueMap`, optional `time`, and `MessageRetractionReturn | None` return typing in both the protocol and unimplemented base.
- `synchronizationPointAchieved(..., successfully=True)` now defaults to success, matching the normal Java overload intent.
- `setAutomaticResignDirective` is typed as returning `None`.
- `RtiFactoryFactory.getAvailableRtiFactories()` now uses the same entry-point groups as factory loading and returns instances.

## Coverage checks run

- Python compile/import checks passed.
- Java 1516.1-2025 class-name coverage: no missing Java class names in final Python class surface.
- Java/C++ `RTIambassador` unique method-name coverage: no missing names.
- Java/C++ `FederateAmbassador` unique callback-name coverage: no missing names.
- C++ RTI exception macro coverage: no missing exception classes.
- Java 1516.1-2025 encoding package coverage: no missing encoding class/protocol names.
- Java 1516.1-2025 auth package coverage: no missing auth class/protocol names.

## Remaining caveat

This is still a typing/model package, not an implementation. Concrete RTI vendors
would need to implement the ABCs/protocols and supply entry points.
