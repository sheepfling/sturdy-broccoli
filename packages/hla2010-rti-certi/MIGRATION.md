# CERTI RTI Backend Migration Inventory

The CERTI backend implementation now lives under `hla2010_rti_certi`.

Moved implementation areas:

- `hla2010_rti_certi.certi`
- `hla2010_rti_certi.certi_java`
- `hla2010_rti_certi.real_rti_certi`

Current import boundary:

- Normal repo tests import CERTI-specific implementation APIs from
  `hla2010_rti_certi`.

Remaining work:

- Decide whether shared Java bridge code remains in core or moves to a future
  `hla2010-rti-java-common` package.
