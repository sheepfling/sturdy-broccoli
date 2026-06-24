# hla-rti-core

## What This Is

`hla-rti-core` is the shared runtime-support package behind `hla.rti`.

It owns cross-version backend discovery, ambassador creation, and shared
runtime-process helpers used by installed backend and vendor packages.

## What This Is Not

It is not:

- a standard HLA API package
- a concrete RTI backend
- a transport package
- a human operator command surface

Those roles live elsewhere.

## When To Open It

Open this package when you need to:

- create RTI ambassadors from installed backend plugins
- discover backend plugins without importing concrete backends directly
- understand shared runtime launch or process lifecycle behavior

If you are editing HLA service behavior, you probably want a backend package
instead.

## Key Imports

The canonical import surface is:

- `hla.rti`

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/package_layout.md`](../../docs/package_layout.md)
- [`../../docs/import_boundary_rules.md`](../../docs/import_boundary_rules.md)
- [`docs/README.md`](docs/README.md)

This package does not own human operator entrypoints; those live under
`./tools/`.

Boundary and import-isolation guard coverage lives in:

- `tests/test_rti_runtime_common_split_package.py`
- `tests/test_package_boundary.py`
