# hla2010-rti-transport-common

Shared hosted transport request-processing helpers for `hla2010`.

This package owns backend-neutral hosted server logic that is reused by both
the gRPC and REST transport packages. It is not a backend family and it is not
itself a wire protocol package.

Use this package when logic is:

- shared by multiple transport protocols
- about transport request shaping, dispatch, or codec behavior
- still backend-neutral

Import the canonical implementation from `hla2010_rti_transport_common`.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_transport_common_split_package.py` and
`tests/test_package_boundary.py`.
