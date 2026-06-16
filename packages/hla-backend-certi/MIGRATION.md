# CERTI RTI Backend Migration Inventory

The CERTI backend implementation now lives under `hla.backends.certi`.

Moved implementation areas:

- `hla.backends.certi.certi`
- `hla.backends.certi.real_rti_certi`

Current import boundary:

- Normal repo tests import CERTI-specific implementation APIs from
  `hla.backends.certi`.

CERTI owns only native CERTI runtime discovery, launch, transport, and service
adapter code. Java bridge code belongs under `hla.bridges.java.*` or vendor
packages, not this backend.
