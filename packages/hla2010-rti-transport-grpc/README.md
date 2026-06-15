# hla2010-rti-transport-grpc

Canonical gRPC transport package for HLA 2010 RTI backend adapters.

This package owns:

- the typed gRPC transport client/runtime
- the protobuf schema and checked-in Python stubs
- the wire-adapter seam that maps transport envelopes onto the current protobuf contract
- hosted Python and CERTI gRPC transport servers

The legacy `hla2010.backends.grpc_transport.*` modules have been removed.
Import `hla2010_rti_transport_grpc` and its submodules directly.

Use this package when you need the networked RTI route:

- `start_python_grpc_server(...)` to host the in-memory Python RTI behind gRPC
- `start_certi_grpc_server(...)` to host CERTI behind the same transport seam
- `GrpcTransportConfig` and `create_grpc_transport(...)` for client-side transport wiring

If you are preparing a protocol change, keep the transport envelope and hosted
RTI semantics stable first. The intended schema-evolution seam is the
`TransportWireAdapter` contract in
`hla2010_rti_transport_grpc.wire_adapter`, not the hosted backend logic.

Boundary, import-isolation, and thin-wrapper guard coverage lives in
`tests/test_rti_transport_grpc_split_package.py`,
`tests/test_package_boundary.py`, and `tests/test_backend_wrapper_policy.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
