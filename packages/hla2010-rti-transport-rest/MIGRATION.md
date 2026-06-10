# Migration

Status: `implementation-moved`

Canonical REST transport implementation now lives under:

- `packages/hla2010-rti-transport-rest/src/hla2010_rti_transport_rest/`

Legacy compatibility imports remain available through:

- `src/hla2010/backends/rest_transport/__init__.py` and
  `client.py` were removed after repo-internal imports migrated.
