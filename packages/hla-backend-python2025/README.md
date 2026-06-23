# hla-backend-python2025

Main full Python RTI backend package for IEEE 1516.1-2025.

This package now owns the main full Python 2025 RTI runtime and is the sole
repo-owned IEEE 1516.1-2025 Python RTI implementation lane. Core 2025 backend
semantics execute from `hla.backends.python2025`, and the legacy
`hla-backend-shim` package is deprecated compatibility scaffolding for older
route and provider names that should be removed after migration.

The runtime is no longer one monolithic backend module. The public
`hla.backends.python2025.backend` shell now fronts a split package layout with
focused runtime/state/surface modules such as:

- `backend_factory_runtime.py`
- `runtime_state.py`
- `federation_management_runtime.py`
- `time_management_runtime.py`
- `support_services_runtime.py`
- `*_surface_mixin.py`

That split is intentional: new executable RTI semantics should keep landing in
the main `hla-backend-python2025` lane, while the public shell stays a stable
front door and the shim package stays wrapper-only.

Current status:

- discoverable as backend `python2025`
- executes the main full 2025 runtime directly
- is the sole repo-owned IEEE 1516.1-2025 Python RTI implementation lane
- must not delegate back to `hla.backends.shim.backend.create_shim_backend`
- is the promoted Python-owned 2025 RTI implementation lane in the repo

The remaining architectural work is to remove `hla-backend-shim` after callers
migrate, while preserving proof parity across the direct and hosted 2025
routes.
