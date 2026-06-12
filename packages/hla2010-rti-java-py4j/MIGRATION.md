# Java Py4J Package Migration

Implementation moved into:

- `hla2010_rti_java_py4j.runtime`
- `hla2010_rti_java_py4j.adapter`
- `hla2010_rti_java_py4j.factory`
- `hla2010_rti_java_py4j.plugin`

Compatibility facades retained:

- `hla2010_rti_pitch_py4j.runtime`
- `hla2010_rti_pitch_py4j.adapter`
- `hla2010_rti_pitch_py4j.factory`

Removed root compatibility facades:

- `hla2010.backends.py4j`

Remaining cleanup:

- Keep the Pitch-named facades until downstream users can migrate to
  `hla2010_rti_java_py4j` for generic Java bridge imports.
