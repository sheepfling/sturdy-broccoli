# Migration

Status: `implementation-moved`

Canonical REST transport implementation now lives under:

- `packages/hla-transport-rest/src/hla/transports/rest/`

Removed root compatibility facades:

- `src/hla2010/backends/rest_transport/__init__.py` and
  `client.py` were removed after repo-internal imports migrated.
