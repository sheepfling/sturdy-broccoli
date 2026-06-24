# hla-rti1516e Migration

This package is the installable root for the strict HLA 2010 Python spec
surface.

Canonical implementation remains in:

- `packages/hla-rti1516e/src/hla/rti1516e/`

Canonical public entrypoints include:

- `hla.rti1516e`
- `hla.runtime.rti1516e_ambassador`
- `hla.rti1516e.federate_ambassador`
- `hla.runtime.rti1516e` only as a temporary workspace compatibility facade

This package owns the abstract API, spec-facing support modules, and backend
registry contract. It must not depend on concrete backend families, vendor
runtime launchers, or repo-internal verification helpers.

## HLA package TODOs

### Byte wrapper parity

- [ ] Align `BytesLike` handling across 2010 and 2025 byte wrappers.
  - 2025 already defines `BytesLike = bytes | bytearray | memoryview`.
  - 2010 should define the same alias for parity.
  - `put(...)` overloads should accept `BytesLike`, not only `bytes`.
  - Keep mutable-buffer operations stricter:
    - `reassign(...)`
    - `get(dest)`
    - `array()`
  - These should continue to use/return `bytearray` where mutability is required.
- [ ] Verify abstract `put(...)` signatures match overload intent.
  - `put(value: int | BytesLike, offset: int | None = None, count: int | None = None) -> None`
  - Confirm concrete wrappers accept:
    - single byte/int value
    - `bytes`
    - `bytearray`
    - `memoryview`
    - source + offset + count

### Stringified annotation cleanup

- [ ] Audit the package for stringified type annotations.
  - Search for patterns like:
    - `"SomeType"`
    - `'SomeType'`
    - `typing.TYPE_CHECKING` imports that may no longer be needed
    - quoted return annotations
  - Prefer `from __future__ import annotations` instead.
- [ ] Add or enforce a rule:
  - every Python module in `upstream_reference` should use:
    ```python
    from __future__ import annotations
    ```
  - then remove unnecessary stringified annotations unless they are truly required.
- [ ] Add a regression check for annotation hygiene.
  - Fail if public package modules contain avoidable quoted annotations.
  - Exempt generated files only if needed.

### Follow-up tests

- [ ] Add parity tests for 2010 vs 2025 byte wrapper typing/runtime behavior.
- [ ] Add tests proving `memoryview` works for `put(...)`.
- [ ] Add tests proving mutable-buffer paths still require/return `bytearray`.
- [ ] Run static typing over both namespaces to catch overload drift.
