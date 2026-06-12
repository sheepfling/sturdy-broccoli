# hla2010-rti-java-common docs

This package owns bridge-independent Java support code reused by installable
Java-backed RTI packages.

Key owned surfaces:
- `hla2010_rti_java_common.java_common`: Java bridge abstractions, Java RTI
  backend base classes, and overload-resolution helpers.
- `hla2010_rti_java_common.java_runtime`: Java home/tool discovery helpers.
- `hla2010_rti_java_common.java_shim_*`: the shared in-process Java shim
  support used for generic Java-backed testing and adapter flows.
- `tests/test_rti_java_common_split_package.py` and
  `tests/test_rti_java_runtime_split_package.py`: split-package guard coverage
  for shared Java support code.
- `tests/test_package_boundary.py`: subprocess import-isolation coverage for the
  installable Java-support package boundary.

This package is shared support code, not a vendor backend or operator
entrypoint.
