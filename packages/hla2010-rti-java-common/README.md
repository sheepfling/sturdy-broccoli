# hla2010-rti-java-common

Shared Java RTI support package for `hla2010-spec`.

This package owns the bridge-independent Java adapter policy used by JPype,
Py4J, CERTI Java-profile code, and the in-process Java shim: callback
dispatching, overload resolution, Java value conversion, and the shared
`JavaRTIBackend` base.
Import the canonical implementation from `hla2010_rti_java_common`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_java_common_split_package.py`,
`tests/test_rti_java_runtime_split_package.py`, and
`tests/test_package_boundary.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
