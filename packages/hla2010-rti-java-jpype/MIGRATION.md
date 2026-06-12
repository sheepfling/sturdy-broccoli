# Java JPype Package Migration

Implementation moved into:

- `hla2010_rti_java_jpype.runtime`
- `hla2010_rti_java_jpype.adapter`
- `hla2010_rti_java_jpype.factory`
- `hla2010_rti_java_jpype.plugin`

Compatibility facades retained:

- `hla2010_rti_pitch_jpype.runtime`
- `hla2010_rti_pitch_jpype.adapter`
- `hla2010_rti_pitch_jpype.factory`

Removed root compatibility facades:

- `hla2010.backends.jpype`

Remaining cleanup:

- Keep the Pitch-named facades until downstream users can migrate to
  `hla2010_rti_java_jpype` for generic Java bridge imports.
