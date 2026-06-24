# hla-backend-python1516-2025

## What This Is

`hla-backend-python1516-2025` owns the main full Python 2025 RTI runtime.

It is the main full Python RTI backend for IEEE 1516.1-2025.

This is the promoted Python-owned 2025 RTI implementation lane where 2025
runtime semantics actually execute.

## What This Is Not

It is not:

- the 2025 standard API package
- a compatibility shim
- a transport package
- an alternate route family beside itself

`hla-rti1516-2025` owns the standard-facing API surface.
`hla-backend-shim` is compatibility scaffolding and should stay wrapper-only.

## When To Open It

Open this package when you need to:

- change executable 2025 RTI behavior
- trace the main repo-owned 2025 runtime lane
- understand the runtime/state/surface split behind the 2025 backend

If you only need the public API shape, do not start here.

## Key Entrypoints

The main implementation root is:

- `hla.backends.python1516_2025`

The public `hla.backends.python1516_2025.backend` shell now fronts a split
package layout.

That shell fronts focused modules such as:

- `backend_factory_runtime.py`
- `runtime_state.py`
- `federation_management_runtime.py`
- `time_management_runtime.py`
- `support_services_runtime.py`
- `*_surface_mixin.py`

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/python_rti_backend.md`](../../docs/python_rti_backend.md)
- [`../../docs/python_rti_reading_map.md`](../../docs/python_rti_reading_map.md)
- [`../../docs/networked_rti_python.md`](../../docs/networked_rti_python.md)

Current status:

- discoverable as backend `python1516_2025`
- executes the main 2025 runtime directly
- is the sole repo-owned IEEE 1516.1-2025 Python RTI implementation lane
- must not delegate runtime ownership back to `hla-backend-shim`
- must not delegate back to `hla.backends.shim.backend.create_shim_backend`
