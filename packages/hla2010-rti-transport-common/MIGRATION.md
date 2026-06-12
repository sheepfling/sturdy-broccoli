# Migration

Status: `implementation-moved`

Canonical shared hosted transport support now lives under:

- `packages/hla2010-rti-transport-common/src/hla2010_rti_transport_common/`

This package owns backend-neutral hosted transport request processing and no
longer depends on CERTI-specific helper code.

Canonical transport wire codecs now also live here:

- `packages/hla2010-rti-transport-common/src/hla2010_rti_transport_common/transport_codecs.py`
