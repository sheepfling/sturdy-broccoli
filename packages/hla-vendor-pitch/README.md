# hla-vendor-pitch

## What This Is

`hla-vendor-pitch` is shared Pitch vendor-runtime support.

It owns Pitch-specific runtime discovery, launch helpers, local-settings
handling, license inspection, and other Pitch runtime concerns.

## What This Is Not

It is not:

- a standard HLA API package
- a concrete backend semantics package
- a generic Java bridge package

This package is about one vendor family: Pitch.

## When To Open It

Open this package when you need:

- Pitch runtime discovery or launch behavior
- Pitch-specific preflight logic
- vendor-owned support code shared by Pitch bridge variants

## Key Imports

The canonical import surface is:

- `src/hla.vendors.pitch/testing_policy.py`
- `hla.vendors.pitch`

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/vendor_runtime_runner_guide.md`](../../docs/vendor_runtime_runner_guide.md)
- [`docs/README.md`](docs/README.md)

The human operator surface stays under `./tools/pitch`.

Use `./tools/pitch` as the package-local command surface.

Guard coverage lives in:

- `tests/test_rti_pitch_split_packages.py`
- `tests/vendors/test_pitch_real_backend_matrix.py`
