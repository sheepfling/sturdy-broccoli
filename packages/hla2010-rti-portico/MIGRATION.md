# Portico RTI Package Migration

Implementation moved into:

- `hla2010_rti_portico.real_rti_portico`
- `hla2010_rti_portico.plugin`

Compatibility facades retained:

- `hla2010.real_rti_portico`
- `hla2010.real_rti`
- `hla2010.backends.java_plugins.portico_*_plugin`

Remaining cleanup:

- Decide whether generic Java bridge adapters should be renamed out of the
  Pitch package names.
- Keep compatibility facade tests until downstream users have migrated to
  `hla2010_rti_portico`.
