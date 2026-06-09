# hla2010-rti-transport-grpc

Canonical gRPC transport package for HLA 2010 RTI backend adapters.

This package owns:

- the typed gRPC transport client/runtime
- the protobuf schema and checked-in Python stubs
- hosted Python and CERTI gRPC transport servers

The legacy `hla2010.backends.grpc_transport.*` modules remain as compatibility
facades during the migration.
