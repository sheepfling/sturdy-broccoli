# hla2010-rti-java-jpype

Generic JPype-backed Java RTI bridge package for `hla2010-spec`.

This package owns the reusable Java bridge mechanics and the generic `jpype`
backend plugin used by vendor-specific RTI plugins such as Pitch and Portico.
Vendor plugins provide runtime discovery and RTI factory options; this package
provides the JPype adapter, runtime, factory, and generic plugin descriptor.
Import the canonical implementation from `hla2010_rti_java_jpype`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_java_plugin_split_packages.py` and
`tests/test_package_boundary.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
