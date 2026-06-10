# Java Shims

`java_shims/` is a top-level Java bridge verification fixture area.

It exists to hold:

- shim source used to exercise JPype and Py4J bridge behavior
- fixture build tooling for those shim artifacts
- bridge-verification support material that is not installable runtime code

It does not exist to hold:

- production Python implementation code
- vendor runtime state or machine-local build/install artifacts
- unrelated experiments or scratch files

The canonical runtime and backend implementations remain under `src/` and
`packages/`. Machine-local runtime/build state remains under `.local/`.
