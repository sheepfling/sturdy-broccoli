# hla-backend-shim migration note

`hla-backend-shim` remains available as the legacy `shim` backend name for
`rti1516_2025`, but it no longer owns the live Python 2025 RTI implementation.

The executable runtime now lives in:

- `packages/hla-backend-python2025/src/hla/backends/python2025/backend.py`

This package exists to preserve compatibility-facing entry points while the
main 2025 RTI implementation is carried by `hla-backend-python2025`.

In the current layout, most shim helper modules are intentionally thin
re-exports of `hla.backends.python2025.*` runtime modules. The shim package
should not regain ownership of core RTI semantics.

If existing code imports `Python2025Backend`, `Python2025RTIAmbassador`, or
`create_python2025_backend` through `hla.backends.shim`, update that code to
use `hla.backends.shim.runtime_aliases` explicitly. The package root and
`hla.backends.shim.backend` are now reserved for the wrapper-only `Shim2025*`
surface and shim-routing helpers. Use the explicit `Shim2025*` symbols when
you intentionally want the compatibility-wrapper lane.

Use `python2025` when you want the direct 2025 backend lane.
Use `shim` only when you need the legacy compatibility-wrapper provider name.
