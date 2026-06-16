# hla1516_2025 Python spec model

This package is a curated union of the initial modular Python draft and the newer
monolithic Python model package. It is an abstract interface/typing layer for the
IEEE 1516.1-2025 HLA Java and C++ API surfaces, not an RTI implementation.

## Merge policy

Kept from the initial draft:

- modular package layout
- strict `RTIambassador` and `FederateAmbassador` signatures
- explicit `IntEnum` values
- fuller Java-like `ByteWrapper`
- `RtiFactoryFactory`
- `UnimplementedRTIambassador`

Added from the newer model:

- `auth.py`
- `encoding.py`
- `AuthorizationResultCode`
- C++-only advisory-switch exceptions plus `InternalError`
- `HLAtransportationTypeHandle` encoding protocol
- Java/C++ naming fix: `logicalTimeImplementationName`
- Java-style `RtiConfiguration` getter methods
- Java-style logical-time methods alongside Pythonic operators

## Notes

The package intentionally preserves HLA camelCase names for direct comparison
with Java and C++ spec documents. Concrete RTI vendors can implement these ABCs
and protocols or use them as type-checking stubs.


## Strict typing and source trace

This build includes `.pyi` stub files for `rti_ambassador`, `federate_ambassador`, and `encoding`.
Those stubs carry the strict overload sets derived from the Java/C++ 1516.1-2025 APIs while the `.py` files remain runtime-importable abstract/protocol surfaces.

See `SOURCE_TRACE.md` for per-method Java/C++ source linkage, service section numbers, overload counts, and Java throws summaries.


## Notice and source attribution

See `NOTICE.md`. Source trace and overload provenance are in `SOURCE_TRACE.md`.
