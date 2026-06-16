# Migration

Status: `implementation-moved`

Canonical gRPC transport implementation now lives under:

- `packages/hla-transport-grpc/src/hla.transports.grpc/`

Legacy compatibility imports have been removed. These paths must stay absent:

- `src/hla2010/backends/grpc_transport/__init__.py`
- `src/hla2010/backends/grpc_transport/client.py`
- `src/hla2010/backends/grpc_transport/transport.py`
- `src/hla2010/backends/grpc_transport/python_server.py`
- `src/hla2010/backends/grpc_transport/rti_transport_pb2.py`
- `src/hla2010/backends/grpc_transport/rti_transport_pb2_grpc.py`

Use `hla.transports.grpc` and its concrete submodules directly.
