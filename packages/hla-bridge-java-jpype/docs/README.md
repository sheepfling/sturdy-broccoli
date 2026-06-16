# hla-bridge-java-jpype docs

This package owns the installable generic JPype Java bridge used by vendor
backend packages.

Key owned surfaces:
- `hla.bridges.java.jpype.runtime`: JPype runtime and JVM attachment helpers.
- `hla.bridges.java.jpype.adapter`: the generic JPype-backed RTI backend
  adapter.
- `hla.bridges.java.jpype.factory` and `.plugin`: bridge factory and generic
  backend plugin descriptors.
- `tests/test_rti_java_plugin_split_packages.py`: split-package guard coverage
  for the generic JPype bridge package.
- `tests/test_package_boundary.py`: subprocess import-isolation coverage for the
  installable generic JPype bridge boundary.

This package is generic bridge support, not a vendor-specific RTI package or
operator entrypoint.
