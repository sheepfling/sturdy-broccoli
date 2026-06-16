# HLA 1516.1-2010 Python spec package merge/build report

This build follows the layout of the supplied 2025 Python spec package but derives the API surface from the supplied 2010 Java and C++ API archives.

## Merge policy

- Java `hla.rti1516e` is the primary source for overload spelling, parameter names, return records, and Java throws summaries.
- C++ `rti1516e` is used to add API surface that is absent from Java, including `createFederationExecutionWithMIM`, direct handle decode helpers, `TransportationType`, and `RTIambassadorFactory`.
- Shared Java/C++ services are represented once and traced with both Java and C++ overload counts.
- 2010 naming is preserved: FDD-oriented exceptions (`InconsistentFDD`, `CouldNotOpenFDD`, `ErrorReadingFDD`) are not renamed to 2025 FOM names.

## Deliberate 2010 differences from the 2025 package

- No 2025 authorization/RtiConfiguration/Credentials surface is emitted because it is not present in the 2010 Java/C++ inputs.
- 2010 encoding omits 2025 unsigned integer and encoded-handle/time helper factory families that are not in the 2010 encoding sources.
- Supplemental callback information records are included because they are present in 2010 Java nested callback interfaces and C++ typedef structs.
