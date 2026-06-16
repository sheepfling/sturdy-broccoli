# hla-rti1516e Migration

This package is the installable root for the clean HLA 2010 Python spec
surface.

Canonical implementation remains in:

- `src/hla2010/`

Canonical public entrypoints include:

- `hla.rti1516e.spec`
- `hla.rti1516e.runtime_api`
- `hla.rti1516e.rti` only as a temporary workspace compatibility facade

This package owns the abstract API, spec-facing support modules, and backend
registry contract. It must not depend on concrete backend families, vendor
runtime launchers, or repo-internal verification helpers.
