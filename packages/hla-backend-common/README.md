# hla-backend-common

## What This Is

`hla-backend-common` is shared backend-support code.

It owns backend-neutral conversion helpers, adapter contracts, handle
registries, and shared support logic that multiple backend families use.

## What This Is Not

It is not:

- a standard HLA API package
- a concrete runtime backend
- a transport package
- a vendor-specific integration layer

## When To Open It

Open this package when logic is:

- shared by multiple backend families
- about backend-neutral conversion or adapter behavior
- support code that should not belong to one runtime family

If the code defines actual HLA service semantics, it probably belongs in a
backend package instead.

## Key Imports

The canonical import surface is:

- `hla.backends.common`

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/package_layout.md`](../../docs/package_layout.md)
- [`../../docs/import_boundary_rules.md`](../../docs/import_boundary_rules.md)
- [`docs/README.md`](docs/README.md)

This package does not own human operator entrypoints; those live under
`./tools/`.

Guard coverage lives in:

- `tests/test_rti_backend_common_split_package.py`
- `tests/test_package_boundary.py`
