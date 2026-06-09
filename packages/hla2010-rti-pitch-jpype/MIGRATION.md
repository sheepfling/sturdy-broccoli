# Pitch JPype Backend Migration Inventory

The generic JPype Java RTI adapter implementation now lives under
`hla2010_rti_java_jpype`. The Pitch package owns only the Pitch-specific plugin
descriptor and compatibility facades.

Canonical implementation areas:

- `hla2010_rti_java_jpype.adapter`
- `hla2010_rti_java_jpype.factory`
- `hla2010_rti_java_jpype.runtime`
- `hla2010_rti_pitch_jpype.plugin`

Compatibility facades retained:

- `hla2010_rti_pitch_jpype.adapter`
- `hla2010_rti_pitch_jpype.factory`
- `hla2010_rti_pitch_jpype.runtime`
- `hla2010.backends.jpype`

Remaining work:

- Keep the compatibility facades until downstream users can migrate directly to
  `hla2010_rti_java_jpype` and `hla2010_rti_java_common`.
