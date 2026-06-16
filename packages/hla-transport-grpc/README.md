# hla-transport-grpc

Canonical gRPC transport package for the HLA 1516e-2010 FedPro-style
protobuf profile.

This package owns:

- the typed gRPC transport client/runtime
- the supplied 2010 FedPro-style protobuf schema and checked-in Python stubs
- hosted Python and CERTI gRPC transport servers

The legacy `hla.rti1516e.backends.grpc_transport.*` modules have been removed.
Import `hla.transports.grpc` and its submodules directly.

Use this package when you need the networked RTI route:

- `start_python_grpc_server(...)` to host the in-memory Python RTI behind gRPC
- `start_certi_grpc_server(...)` to host CERTI behind the same transport route
- `GrpcTransportConfig` and `create_grpc_transport(...)` for client-side transport wiring

Schema imports are under `hla.transports.grpc.fedpro2010`.

Regenerate stubs with:

```bash
python packages/hla-transport-grpc/scripts/generate_fedpro2010_stubs.py
```

Boundary, import-isolation, and thin-wrapper guard coverage lives in
`tests/test_rti_transport_grpc_split_package.py`,
`tests/test_package_boundary.py`, and `tests/test_backend_wrapper_policy.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
