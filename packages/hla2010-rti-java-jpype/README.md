# hla2010-rti-java-jpype

Generic JPype-backed Java RTI bridge package for `hla2010-spec`.

This package owns the reusable Java bridge mechanics and the generic `jpype`
backend plugin used by vendor-specific RTI plugins such as Pitch and Portico.
Vendor plugins provide runtime discovery and RTI factory options; this package
provides the JPype adapter, runtime, factory, and generic plugin descriptor.
