# hla-backend-shim

`hla-backend-shim` provides the legacy compatibility-wrapper package for the
IEEE 1516.1-2025 Python API surface.

The package name is historical. In the current repo the main full Python 2025
RTI implementation executes from `hla-backend-python2025`, while this package
retains import-level wrapper-facing normalization and legacy compatibility
aliases.

At the package root, the shim-specific surface is only
`Shim2025Backend`, `Shim2025RTIAmbassador`, and `create_shim_backend`.
If older code still needs runtime-class compatibility aliases, use the
explicit module path `hla.backends.shim.runtime_aliases`, where
`Python2025Backend`, `Python2025RTIAmbassador`, and
`create_python2025_backend` still point through to the real runtime lane.

It is not a 2010 backend and it is not a vendor adapter. The architectural
split that matters is already in place: `hla-backend-python2025` is the real
2025 RTI runtime owner, and `hla-backend-shim` stays narrow and
compatibility-focused.

Future work here is boundary cleanup, not deciding whether a dedicated Python
2025 backend should exist. That backend already exists in
`hla-backend-python2025`.

When adding or reviewing 2025 runtime behavior, default to the `python2025`
lane. Only use `hla.backends.shim` when you explicitly need the legacy
compatibility-wrapper surface.

For the current evidence-based decision point, see
[`docs/plans/2025_python_rti_backend_audit.md`](../../docs/plans/2025_python_rti_backend_audit.md)
and
[`docs/python_rti_backend.md`](../../docs/python_rti_backend.md).
