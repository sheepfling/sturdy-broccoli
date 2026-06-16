# Pitch Py4J Backend Migration Inventory

The generic Py4J Java RTI adapter implementation now lives under
`hla.bridges.java.py4j`. The Pitch package owns only the Pitch-specific plugin
descriptor and compatibility facades.

Canonical implementation areas:

- `hla.bridges.java.py4j.adapter`
- `hla.bridges.java.py4j.factory`
- `hla.bridges.java.py4j.runtime`
- `hla.vendors.pitch.py4j.plugin`

Compatibility facades retained:

- `hla.vendors.pitch.py4j.adapter`
- `hla.vendors.pitch.py4j.factory`
- `hla.vendors.pitch.py4j.runtime`

Removed root compatibility facades:

- `hla.rti1516e.backends.py4j`

Remaining work:

- Keep the compatibility facades until downstream users can migrate directly to
  `hla.bridges.java.py4j` and `hla.bridges.java.common`.
