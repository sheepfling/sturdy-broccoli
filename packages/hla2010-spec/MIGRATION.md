# hla2010-spec Migration

This package is the installable root for the clean HLA 2010 Python spec
surface.

Canonical implementation remains in:

- `src/hla2010/`

Canonical public entrypoints include:

- `hla2010.spec`
- `hla2010.runtime_api`
- `hla2010.rti`

This package owns the abstract API, spec-facing support modules, and backend
registry contract. It must not depend on concrete backend families, vendor
runtime launchers, or repo-internal verification helpers.
