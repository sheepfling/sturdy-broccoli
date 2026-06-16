# hla-transport-grpc docs

This package owns the installable gRPC transport implementation for HLA 2010
backend adapters.

Key owned surfaces:
- `hla.transports.grpc.transport`: the client transport implementation.
- `hla.transports.grpc.python_server`: Python and CERTI hosted gRPC
  server adapters.
- `hla.transports.grpc.rti_transport_pb2*`: generated protocol types
  shipped with the package.
- `tests/test_rti_transport_grpc_split_package.py`: split-package guard
  coverage for the gRPC transport package.
- `tests/test_package_boundary.py`: subprocess import-isolation coverage for the
  installable gRPC transport boundary.
- `tests/test_backend_wrapper_policy.py`: guard coverage that transport runtime
  tests stay thin wrappers over shared harness entrypoints.

Human operator entrypoints remain in `./tools/`; this package owns the code
surface, not the operator command surface.

For a concrete usage guide, read
[`../../../docs/networked_rti_python.md`](../../../docs/networked_rti_python.md).
