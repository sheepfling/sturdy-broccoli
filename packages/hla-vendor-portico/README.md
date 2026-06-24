# hla-vendor-portico

## What This Is

`hla-vendor-portico` is Portico vendor-runtime support.

It owns Portico runtime discovery plus the JPype and Py4J plugin descriptors
for Portico-backed RTI ambassadors.

## What This Is Not

It is not:

- a standard HLA API package
- a concrete backend semantics package
- a generic Java bridge package

This package is about Portico integration specifically.

## When To Open It

Open this package when you need:

- Portico runtime discovery
- Portico-specific preflight or test policy
- Portico JPype or Py4J plugin descriptors

## Key Imports

The canonical import surface is:

- `src/hla.vendors.portico/testing_policy.py`
- `hla.vendors.portico`

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/vendor_runtime_runner_guide.md`](../../docs/vendor_runtime_runner_guide.md)
- [`docs/README.md`](docs/README.md)

The human operator surface stays under `./tools/vendor-green`.

Use `./tools/vendor-green` as the package-local command surface.

Guard coverage lives in:

- `tests/test_rti_portico_split_package.py`
- `tests/vendors/test_portico_real_backend_matrix.py`
