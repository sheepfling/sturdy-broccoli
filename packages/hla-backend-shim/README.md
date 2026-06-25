# hla-backend-shim

## What This Is

`hla-backend-shim` is the legacy compatibility shim for the 2025 Python RTI
lane.

It exists to preserve older imports and wrapper-facing aliases while the real
implementation lives in `hla-backend-python1516-2025`.

It is not part of the repo-owned 2025 Python RTI implementation claim.
It is not the main 2025 runtime.
It should remain wrapper-only.

The important split is already in place:

- `hla-backend-python1516-2025` owns the real 2025 runtime
- `hla-backend-shim` is the legacy compatibility layer in front of it

## What This Is Not

It is not:

- the main 2025 Python RTI implementation
- a standard API package
- a vendor adapter
- a preferred place for new runtime work

## When To Open It

Open this package only when you explicitly need to:

- preserve legacy imports
- remove the final compatibility scaffolding

If you are changing 2025 runtime behavior, do not start here.

## Key Entrypoints

The package root no longer exposes a backend or plugin surface.

Older compatibility aliases still exist under:

- `hla.backends.shim.runtime_aliases`

No shim helper modules remain beyond `hla.backends.shim.runtime_aliases`.
The package root and `backend.py` stay reserved for the wrapper-only surface
and the routed-leaf compatibility constants.
They should be removed once no callers depend on the legacy import paths.

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/python_rti_backend.md`](../../docs/python_rti_backend.md)
- [`../../docs/plans/2025_python_rti_backend_audit.md`](../../docs/plans/2025_python_rti_backend_audit.md)

Future work here is boundary cleanup and removal, not new runtime ownership.
