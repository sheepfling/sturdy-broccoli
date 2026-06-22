# hla-transport-grpc docs

This package owns the installable gRPC transport implementation for the HLA
1516e-2010 FedPro-style protobuf profile, plus the bounded 2025 FedPro hosted
route surface used in the current Python 2025 evidence ladder.

Key owned surfaces:
- `hla.transports.grpc.transport`: the client transport implementation.
- `hla.transports.grpc.python_server`: Python and CERTI hosted gRPC
  server adapters.
- `hla.transports.grpc.python_server_2025`: the bounded hosted FedPro 2025
  route server used for the typed 2025 transport slice.
- `hla.transports.grpc.fedpro2010`: generated 2010 FedPro-style protobuf
  messages and gRPC gateway bindings shipped with the package.
- `hla.transports.grpc.fedpro2025`: generated 2025 FedPro protobuf messages
  and gateway bindings shipped with the package.
- `packages/hla-transport-grpc/proto/rti1516e/fedpro/`: authoritative proto
  source copied from the supplied 2010 bundle plus the repo-owned service
  binding.
- `tests/test_rti_transport_grpc_split_package.py`: import and boundary guard
  coverage for the gRPC transport package.
- `tests/test_package_boundary.py`: subprocess import-isolation coverage for the
  installable gRPC transport boundary.
- `tests/test_backend_wrapper_policy.py`: guard coverage that transport runtime
  tests stay thin wrappers over shared harness entrypoints.

Human operator entrypoints remain in `./tools/`; this package owns the code
surface, not the operator command surface.

Boundary note:
- the 2025 FedPro route is a hosted transport variant over the promoted Python
  2025 RTI lane
- it is bounded runtime evidence, not a separate RTI family and not an
  unconditional full-semantics conformance surface

For a concrete usage guide, read
[`../../../docs/networked_rti_python.md`](../../../docs/networked_rti_python.md).
