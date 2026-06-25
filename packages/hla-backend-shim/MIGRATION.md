# hla-backend-shim migration note

`hla-backend-shim` is deprecated. It remains available only as temporary
legacy import-level compatibility scaffolding for `rti1516_2025`, but it no
longer owns the live Python 2025 RTI implementation, is not part of the
repo-owned implementation claim, and should be removed after callers migrate.

The executable runtime now lives in:

- `packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py`

This package exists to preserve temporary compatibility-facing entry points
while the main 2025 RTI implementation is carried by
`hla-backend-python1516-2025`, the sole repo-owned IEEE 1516.1-2025 Python RTI
implementation lane.

Legacy shim helper modules have been removed. The shim package should not
regain ownership of core RTI semantics and should be removed once the
remaining legacy import paths are no longer needed. The surviving wrapper
surface is retained only for explicit legacy import compatibility coverage and
temporary scaffolding. `runtime_aliases.py` remains as the explicit hatch for
the few compatibility aliases that still point into
`hla.backends.python1516_2025.backend`.

If existing code imports `Python2025Backend`, `Python2025RTIAmbassador`, or
`create_python2025_backend` through `hla.backends.shim`, update that code to
use `hla.backends.shim.runtime_aliases` explicitly. The package root and
`hla.backends.shim.backend` are now reserved for the wrapper-only `Shim2025*`
surface and shim-routing helpers. Use the explicit `Shim2025*` symbols when
you intentionally want the compatibility-wrapper lane.

Use `python1516_2025` when you want the direct 2025 backend lane.
Use `hla.backends.shim` only when you need the temporary
import-compatibility scaffolding or legacy compatibility-wrapper imports.
