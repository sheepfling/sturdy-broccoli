# Perfect Correspondence Status

We have **not** proven perfect correspondence to the IEEE 1516.1-2010 Java and C++ implications.

What we do have:

- Parsed Java/C++ API inventories and comparison artifacts.
- A service-by-service conformance matrix for 162 `RTIambassador` methods and 55 `FederateAmbassador` callbacks.
- Section anchors for the generated API surface.
- Executable pytest coverage for the reference Python RTI, FOM/MIM loading, MOM catalog derivation, generated MOM negative-path rows, service conformance metadata, time-management slices, startup/synchronization, and Target/Radar smoke behavior.
- Java-shim tests that exercise the JPype/Py4J adapter abstraction layer without requiring a vendor RTI in the sandbox.

Known limits:

- No external HLA certification suite has been run.
- Optional real JPype/Py4J vendor-RTI tests are still skipped unless the bridge packages and a vendor RTI are installed.
- Several matrix rows are group-level or slice-level evidence rather than complete service-by-service semantic proofs.
- 32 MOM `HLAservice` semantic negative rows remain planned in v0.13.
- Full equivalence to every Java/C++ overload edge case, exception precondition, and vendor-specific handle/time factory behavior requires additional parity tests against real Java and C++ RTIs.
