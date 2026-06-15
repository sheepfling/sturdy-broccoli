# CERTI RTI Backend Migration Inventory

The CERTI backend implementation now lives under `hla2010_rti_certi`.

Moved implementation areas:

- `hla2010_rti_certi.certi`
- `hla2010_rti_certi.real_rti_certi`

Current import boundary:

- Normal repo tests import CERTI-specific implementation APIs from
  `hla2010_rti_certi`.

Remaining work:

- Keep CERTI-specific runtime work on the native `certi` backend path. Java
  bridge code belongs in the vendor Java packages.
