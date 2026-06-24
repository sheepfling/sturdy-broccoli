# hla-transport-common

## What This Is

`hla-transport-common` is shared transport-support code.

It owns backend-neutral hosted request-processing logic reused by the gRPC and
REST transport packages.

## What This Is Not

It is not:

- a concrete wire protocol package
- a backend package
- a standard HLA API package

Transport-common is the shared support layer underneath specific transport
families.

## When To Open It

Open this package when logic is:

- shared by multiple transport protocols
- about request shaping, dispatch, or common codec behavior
- still backend-neutral

If the code is protocol-specific, it probably belongs in `hla-transport-grpc`
or `hla-transport-rest` instead.

## Key Imports

The canonical import surface is:

- `hla.transports.common`

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/package_layout.md`](../../docs/package_layout.md)
- [`../../docs/import_boundary_rules.md`](../../docs/import_boundary_rules.md)
- [`docs/README.md`](docs/README.md)

This package does not own human operator entrypoints; those live under
`./tools/`.

Guard coverage lives in:

- `tests/test_rti_transport_common_split_package.py`
- `tests/test_package_boundary.py`
