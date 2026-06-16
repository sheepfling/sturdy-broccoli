# Migration

Status: `implementation-moved`

Canonical gRPC transport implementation now lives under:

- `packages/hla-transport-grpc/src/hla.transports.grpc/`
- `packages/hla-transport-grpc/proto/rti1516e/fedpro/`

The wire contract is the 2010 FedPro-style protobuf profile:

- `datatypes.proto`
- `RTIambassador.proto`
- `FederateAmbassador.proto`
- `HLA2010RTITransport.proto`

Generated Python imports live under `hla.transports.grpc.fedpro2010`.
The 2025 FedPro-compatible schema lives beside it under
`hla.transports.grpc.fedpro2025`.

Legacy compatibility imports have been removed. These paths must stay absent:

- `src/hla2010/backends/grpc_transport/__init__.py`
- `src/hla2010/backends/grpc_transport/client.py`
- `src/hla2010/backends/grpc_transport/transport.py`
- `src/hla2010/backends/grpc_transport/python_server.py`

Use `hla.transports.grpc` and its concrete submodules directly.
