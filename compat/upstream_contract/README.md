# Frozen upstream_reference contract snapshots

This directory stores the frozen `upstream_reference` standards-contract snapshots used to validate `sturdy-broccoli` without requiring live access to `upstream_reference` during normal CI.

Current target:

- `upstream_reference` tag: `v0.1.1`
- full commit: `ed39b02e4c6e7813fce9e0e183b184c8513d4dd6`
- snapshot directory: `compat/upstream_contract/v0.1.1/`

Default sturdy-broccoli CI should use these checked-in JSON files and must not import `upstream_reference`.

Live `upstream_reference` is only needed for explicit contract refresh tooling.

## Files

```text
compat/upstream_contract/
  README.md
  schema-v1.json
  allowed_differences.json
  v0.1.1/
    ieee1516e.json
    ieee1516_2025.json
```

## Confirmed contract stance

- `RTIexception` is canonical; `RTIException` is not in `upstream_reference v0.1.1`.
- Ambassador method counts are final for this snapshot: `162/51` for `ieee1516e`, `188/56` for `ieee1516_2025`.
- `rti_factory.py` is strict standard-facing contract for both standards.
- `_byte_wrapper.py` is private, but contract-sensitive because encoding runtime/types depend on it.
- `HandleValueMap.getValueReference` exists in `ieee1516e`; `get_value_reference` does not.
- `ieee1516_2025.handles` does not expose public `HandleValueMap` in this snapshot.
