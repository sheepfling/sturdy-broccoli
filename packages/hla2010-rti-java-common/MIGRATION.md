# Java Common Package Migration

Implementation moved into:

- `hla2010_rti_java_common.java_common`

Removed root compatibility facades:

- `hla2010.backends.java_common`

Remaining cleanup:

- Keep downstream callers on the canonical
  `hla2010_rti_java_common` and `hla2010_rti_backend_common` imports; the
  removed root facade must not be reintroduced.
