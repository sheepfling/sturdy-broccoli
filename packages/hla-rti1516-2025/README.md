# hla-rti1516-2025

## What This Is

`hla-rti1516-2025` is the IEEE 1516.1-2025 standard-facing Python spec
package.

It is a typing and abstract-interface layer for the 2025 HLA surface. It owns
the public API shape, not runtime execution.

## What This Is Not

It is not:

- a concrete RTI backend
- the main 2025 Python runtime lane
- a compatibility shim
- a transport or vendor integration package

If you need executable 2025 behavior, open `hla-backend-python1516-2025` instead.

## When To Open It

Open this package when you need:

- the 2025 standard API surface
- strict ambassador signatures
- enums, exceptions, handles, datatypes, time, encoding, and auth types
- typing artifacts and source-trace-backed contract files

## Key Imports

The main import root is:

- `hla.rti1516_2025`

Notable owned modules include:

- `auth.py`
- `encoding.py`
- `rti_ambassador.py`
- `federate_ambassador.py`
- `enums.py`
- `exceptions.py`
- `handles.py`
- `datatypes.py`
- `logical_time.py`
- `time.py`

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/package_layout.md`](../../docs/package_layout.md)
- [`../../docs/python_rti_backend.md`](../../docs/python_rti_backend.md)
- [`../../requirements/2025/SOURCE_TRACE.md`](../../requirements/2025/SOURCE_TRACE.md)
- [`../../requirements/2025/NOTICE.md`](../../requirements/2025/NOTICE.md)

This package intentionally preserves HLA camelCase names where the standard
surface requires them.

It also ships strict typing artifacts, including `.pyi` files for
`rti_ambassador`, `federate_ambassador`, and `encoding`.
