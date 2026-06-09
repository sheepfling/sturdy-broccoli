# CERTI RTI Backend Migration Inventory

The CERTI backend implementation now lives under `hla2010_rti_certi`.

Moved implementation areas:

- `hla2010_rti_certi.certi`
- `hla2010_rti_certi.certi_java`
- `hla2010_rti_certi.real_rti_certi`

Compatibility facades retained:

- `hla2010.backends.certi`
- `hla2010.backends.certi_java`
- `hla2010.real_rti_certi`

Current import boundary:

- Normal repo tests import CERTI-specific implementation APIs from
  `hla2010_rti_certi`.
- The remaining old-path imports are explicit compatibility assertions in
  `tests/test_rti_certi_split_package.py`.

Remaining work:

- Decide whether shared Java bridge code remains in core or moves to a future
  `hla2010-rti-java-common` package.
