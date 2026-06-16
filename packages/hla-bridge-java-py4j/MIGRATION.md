# Java Py4J Package Migration

Implementation moved into:

- `hla.bridges.java.py4j.runtime`
- `hla.bridges.java.py4j.adapter`
- `hla.bridges.java.py4j.factory`
- `hla.bridges.java.py4j.plugin`

Compatibility facades retained:

- `hla.vendors.pitch.py4j.runtime`
- `hla.vendors.pitch.py4j.adapter`
- `hla.vendors.pitch.py4j.factory`

Removed root compatibility facades:

- `hla.rti1516e.backends.py4j`

Remaining cleanup:

- Keep the Pitch-named facades until downstream users can migrate to
  `hla.bridges.java.py4j` for generic Java bridge imports.
