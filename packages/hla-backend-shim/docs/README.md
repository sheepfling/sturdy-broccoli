# hla-backend-shim docs

The legacy-named `hla-backend-shim` package is deprecated temporary
import-compatibility scaffolding and a compatibility wrapper over the main full
Python 2025 RTI lane for `rti1516_2025`.

The executable runtime now lives in `hla-backend-python2025`. This package
retains temporary import-compatibility scaffolding, import-level
wrapper-facing normalization, and compatibility aliases used by older routes
and tests.

At the package root, only the `Shim2025*` names represent the wrapper-only
lane. If compatibility code still needs runtime aliases, use the explicit
module path `hla.backends.shim.runtime_aliases`, where `Python2025Backend`,
`Python2025RTIAmbassador`, and `create_python2025_backend` still point through
to the real runtime package.

The other `hla.backends.shim.*` helper modules are intentionally thin
forwarders into `hla.backends.python2025.*`. They remain only as temporary,
test-backed legacy import compatibility scaffolding and should not become the
normal import path for new runtime code. They are kept only for test-backed
legacy import compatibility, and they are also a test-backed legacy
compatibility surface. They are deprecated and should be removed after
migration.

The architectural intent remains explicit. The real Python 2025 RTI backend
already lives in `hla-backend-python2025`; this package is the wrapper-only
compatibility lane and temporary scaffolding seam. Future work is about
keeping that wrapper narrow, not about deciding whether a dedicated 2025
backend should exist, and the package should be removed after migration.

Current working stance: implement new 2025 runtime behavior in
`hla-backend-python2025`, and reserve `hla-backend-shim` only for deprecated
compatibility-only scaffolding concerns until it can be removed.
