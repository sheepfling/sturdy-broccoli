# hla2010-rti-java-py4j

Generic Py4J-backed Java RTI bridge package for `hla2010-spec`.

This package owns the reusable Java gateway bridge mechanics and the generic
`py4j` backend plugin used by vendor-specific RTI plugins such as Pitch and
Portico. Vendor plugins provide runtime discovery and RTI factory options; this
package provides the Py4J adapter, runtime, factory, and generic plugin
descriptor.
