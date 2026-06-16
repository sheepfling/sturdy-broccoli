# Java Common Package Migration

Implementation moved into:

- `hla.bridges.java.common.java_common`

Removed root compatibility facades:

- `hla.rti1516e.backends.java_common`

Remaining cleanup:

- Keep downstream callers on the canonical
  `hla.bridges.java.common` and `hla.backends.common` imports; the
  removed root facade must not be reintroduced.
