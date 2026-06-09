# Java Common Package Migration

Implementation moved into:

- `hla2010_rti_java_common.java_common`

Compatibility facades retained:

- `hla2010.backends.java_common`

Remaining cleanup:

- Keep the compatibility facade until downstream users can migrate directly to
  `hla2010_rti_java_common` and `hla2010_rti_backend_common`.
