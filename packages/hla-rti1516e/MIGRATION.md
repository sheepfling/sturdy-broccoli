# hla-rti1516e Migration

This package is the installable root for the strict HLA 2010 Python spec
surface.

Canonical implementation remains in:

- `packages/hla-rti1516e/src/hla/rti1516e/`

Canonical public entrypoints include:

- `hla.rti1516e`
- `hla.rti1516e.rti_ambassador`
- `hla.rti1516e.federate_ambassador`
- `hla.rti1516e.rti` only as a temporary workspace compatibility facade

This package owns the abstract API, spec-facing support modules, and backend
registry contract. It must not depend on concrete backend families, vendor
runtime launchers, or repo-internal verification helpers.
