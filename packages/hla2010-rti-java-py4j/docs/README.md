# hla2010-rti-java-py4j docs

This package owns the installable generic Py4J Java bridge used by vendor
backend packages.

Key owned surfaces:
- `hla2010_rti_java_py4j.runtime`: Py4J gateway runtime helpers.
- `hla2010_rti_java_py4j.adapter`: the generic Py4J-backed RTI backend
  adapter and proxy helpers.
- `hla2010_rti_java_py4j.factory` and `.plugin`: bridge factory and generic
  backend plugin descriptors.
- `tests/test_rti_java_plugin_split_packages.py`: split-package guard coverage
  for the generic Py4J bridge package.
- `tests/test_package_boundary.py`: subprocess import-isolation coverage for the
  installable generic Py4J bridge boundary.

This package is generic bridge support, not a vendor-specific RTI package or
operator entrypoint.
