# Pitch Py4J Backend Migration Inventory

The generic Py4J Java RTI adapter implementation now lives under
`hla2010_rti_java_py4j`. The Pitch package owns only the Pitch-specific plugin
descriptor and compatibility facades.

Canonical implementation areas:

- `hla2010_rti_java_py4j.adapter`
- `hla2010_rti_java_py4j.factory`
- `hla2010_rti_java_py4j.runtime`
- `hla2010_rti_pitch_py4j.plugin`

Compatibility facades retained:

- `hla2010_rti_pitch_py4j.adapter`
- `hla2010_rti_pitch_py4j.factory`
- `hla2010_rti_pitch_py4j.runtime`

Removed root compatibility facades:

- `hla2010.backends.py4j`

Remaining work:

- Keep the compatibility facades until downstream users can migrate directly to
  `hla2010_rti_java_py4j` and `hla2010_rti_java_common`.
