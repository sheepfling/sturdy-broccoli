# Pitch JPype Backend Migration Inventory

The generic JPype Java RTI adapter implementation now lives under
`hla.bridges.java.jpype`. The Pitch package owns only the Pitch-specific plugin
descriptor and compatibility facades.

Canonical implementation areas:

- `hla.bridges.java.jpype.adapter`
- `hla.bridges.java.jpype.factory`
- `hla.bridges.java.jpype.runtime`
- `hla.vendors.pitch.jpype.plugin`

Compatibility facades retained:

- `hla.vendors.pitch.jpype.adapter`
- `hla.vendors.pitch.jpype.factory`
- `hla.vendors.pitch.jpype.runtime`

Removed root compatibility facades:

- `hla.rti1516e.backends.jpype`

Remaining work:

- Keep the compatibility facades until downstream users can migrate directly to
  `hla.bridges.java.jpype` and `hla.bridges.java.common`.
