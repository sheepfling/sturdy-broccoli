# Java JPype Package Migration

Implementation moved into:

- `hla.bridges.java.jpype.runtime`
- `hla.bridges.java.jpype.adapter`
- `hla.bridges.java.jpype.factory`
- `hla.bridges.java.jpype.plugin`

Compatibility facades retained:

- `hla.vendors.pitch.jpype.runtime`
- `hla.vendors.pitch.jpype.adapter`
- `hla.vendors.pitch.jpype.factory`

Removed root compatibility facades:

- `hla.rti1516e.backends.jpype`

Remaining cleanup:

- Keep the Pitch-named facades until downstream users can migrate to
  `hla.bridges.java.jpype` for generic Java bridge imports.
