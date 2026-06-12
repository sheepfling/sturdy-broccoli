# hla2010-rti-transport-grpc

Canonical gRPC transport package for HLA 2010 RTI backend adapters.

This package owns:

- the typed gRPC transport client/runtime
- the protobuf schema and checked-in Python stubs
- hosted Python and CERTI gRPC transport servers

The legacy `hla2010.backends.grpc_transport.*` modules have been removed.
Import `hla2010_rti_transport_grpc` and its submodules directly.
Boundary, import-isolation, and thin-wrapper guard coverage lives in
`tests/test_rti_transport_grpc_split_package.py`,
`tests/test_package_boundary.py`, and `tests/test_backend_wrapper_policy.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
