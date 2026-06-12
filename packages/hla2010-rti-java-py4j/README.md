# hla2010-rti-java-py4j

Generic Py4J-backed Java RTI bridge package for `hla2010-spec`.

This package owns the reusable Java gateway bridge mechanics and the generic
`py4j` backend plugin used by vendor-specific RTI plugins such as Pitch and
Portico. Vendor plugins provide runtime discovery and RTI factory options; this
package provides the Py4J adapter, runtime, factory, and generic plugin
descriptor.
Import the canonical implementation from `hla2010_rti_java_py4j`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_java_plugin_split_packages.py` and
`tests/test_package_boundary.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
