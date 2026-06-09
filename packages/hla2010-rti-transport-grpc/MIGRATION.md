# Migration

Status: `implementation-moved`

Canonical gRPC transport implementation now lives under:

- `packages/hla2010-rti-transport-grpc/src/hla2010_rti_transport_grpc/`

Legacy compatibility imports remain available through:

- `src/hla2010/backends/grpc_transport/__init__.py`
- `src/hla2010/backends/grpc_transport/client.py`
- `src/hla2010/backends/grpc_transport/transport.py`
- `src/hla2010/backends/grpc_transport/python_server.py`
- `src/hla2010/backends/grpc_transport/rti_transport_pb2.py`
- `src/hla2010/backends/grpc_transport/rti_transport_pb2_grpc.py`
