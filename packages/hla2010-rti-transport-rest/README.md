# hla2010-rti-transport-rest

Canonical REST/HTTP JSON transport package for HLA 2010 RTI backend adapters.

This package owns:

- the typed REST transport client/runtime
- hosted Python and CERTI REST transport servers

The legacy `hla2010.backends.rest_transport*` modules have been removed and do
not remain available.
Import `hla2010_rti_transport_rest` and its submodules directly.
Boundary and import-isolation guard coverage lives in
`tests/test_rti_transport_rest_split_package.py` and
`tests/test_package_boundary.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
