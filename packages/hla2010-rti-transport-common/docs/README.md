# hla2010-rti-transport-common docs

This package owns backend-neutral transport primitives shared by installable
wire-protocol packages.

Key owned surfaces:
- `hla2010_rti_transport_common.transport`: request/response transport types
  and the subprocess-line transport implementation.
- `hla2010_rti_transport_common.transport_registry`: lazy transport selection
  and factory registration.
- `hla2010_rti_transport_common.transport_codecs`: shared handle and payload
  encoding helpers used by transport adapters.
- `tests/test_rti_transport_common_split_package.py`: split-package guard
  coverage for the shared transport layer.
- `tests/test_package_boundary.py`: subprocess import-isolation coverage for the
  installable transport-support package boundary.

This package is not a backend, operator entrypoint, or protocol-specific
transport implementation.
