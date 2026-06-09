# Pitch Common Migration Inventory

The Pitch runtime helper implementation now lives under
`hla2010_rti_pitch_common`.

Moved implementation:

- `hla2010_rti_pitch_common.real_rti_pitch`

Compatibility facade retained:

- `hla2010.real_rti_pitch`

Remaining work:

- Move normal Pitch runtime tests/imports to `hla2010_rti_pitch_common`.
- Keep `hla2010.real_rti_pitch` and `hla2010.real_rti` as compatibility
  facades until the monolithic package is retired.
