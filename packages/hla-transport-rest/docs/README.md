# hla-transport-rest docs

This package owns the installable REST/HTTP JSON transport implementation for
HLA 2010 backend adapters.

Key owned surfaces:
- `hla.transports.rest`: the REST transport client and package exports.
- `hla.transports.rest.client`: JSON request/response encoding helpers.
- `hla.transports.rest.rest_transport_host`: Python and CERTI hosted
  REST server adapters.
- `tests/test_rti_transport_rest_split_package.py`: split-package guard
  coverage for the REST transport package.
- `tests/test_package_boundary.py`: subprocess import-isolation coverage for the
  installable REST transport boundary.

Human operator entrypoints remain in `./tools/`; this package owns the code
surface, not the operator command surface.
