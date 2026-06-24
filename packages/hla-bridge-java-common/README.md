# hla-bridge-java-common

## What This Is

`hla-bridge-java-common` is shared Java bridge support code.

It owns bridge-independent Java adapter policy used by JPype, Py4J, CERTI
Java-profile code, and the in-process Java shim.

## What This Is Not

It is not:

- a concrete backend
- a standard HLA API package
- a vendor-specific package
- a human operator command surface

## When To Open It

Open this package when you need:

- callback dispatching across Java bridge paths
- Java overload resolution or value conversion
- shared Java RTI bridge abstractions

If you are working on a specific bridge implementation, the JPype or Py4J
package may be the better starting point.

## Key Imports

The canonical import surface is:

- `hla.bridges.java.common`

Bridge-neutral factory selection uses:

- `create_java_rti_ambassador(...)`
- `discover_java_rti(...)`

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/language_shim_routes.md`](../../docs/language_shim_routes.md)
- [`../../docs/java_toolchain.md`](../../docs/java_toolchain.md)
- [`docs/README.md`](docs/README.md)

This package does not own human operator entrypoints; those live under
`./tools/`.

Guard coverage lives in:

- `tests/test_rti_java_common_split_package.py`
- `tests/test_rti_java_runtime_split_package.py`
- `tests/test_package_boundary.py`
