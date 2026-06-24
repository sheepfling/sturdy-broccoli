# upstream_reference contract snapshot migration

This migration adds a frozen `upstream_reference v0.1.1` contract snapshot to `sturdy-broccoli` and uses it to enforce standard-facing compatibility without requiring live `upstream_reference` access.

## Source basis

```text
upstream_reference tag: v0.1.1
upstream_reference commit: ed39b02e4c6e7813fce9e0e183b184c8513d4dd6
```

## Commit sequence

```text
1. docs: define upstream_reference compliance and package responsibility boundaries
2. compat: add frozen upstream_reference v0.1.1 contract snapshots
3. compat: add allowed upstream_reference contract differences
4. tools: add local upstream_reference contract checker
5. test: enforce upstream_reference ambassador contract
6. test: enforce upstream_reference enum and exception contract
7. test: enforce upstream_reference datatype and handle contract
8. test: enforce upstream_reference time, logical_time, encoding, and rti_factory contract
9. ci: run upstream_reference contract test without live upstream_reference
10. refactor: move sturdy runtime extras behind compatibility forwarders
```

## Default CI

```bash
python -m pytest tests/compat/test_upstream_contract.py
```

This must not import `upstream_reference`.

## Internal refresh only

```bash
python scripts/export_upstream_contract.py   --out compat/upstream_contract/v0.1.1   --upstream_reference-version v0.1.1
```

This may require `upstream-reference-package`.

## Checker strictness v1

Strict:

```text
method names
parameter names
parameter kind
required/default status
enum names, members, values
exception class names
dataclass fields
NamedTuple fields
public standard class names
selected public standard methods
```

Initially non-strict:

```text
type annotations
return annotations
docstrings
implementation bodies
private helper internals, except contract-sensitive support like _byte_wrapper behavior through encoding
```

## Known sturdy extras to allow in normal mode

```text
RTIException
RangeBounds.lower_bound
RangeBounds.upper_bound
MessageRetractionReturn.retraction_handle_is_valid
FederationExecutionInformation.federation_execution_name
FederationExecutionInformation.logical_time_implementation_name
FederateHandleSaveStatusPair.federate_handle
FederateHandleSaveStatusPair.save_status
FederateRestoreStatus.pre_restore_handle
FederateRestoreStatus.post_restore_handle
FederateRestoreStatus.restore_status
TimeQueryReturn.time_is_valid
AttributeRegionAssociation.attributes
AttributeRegionAssociation.regions
HandleValueMap.get_value_reference
```

These are sturdy facade extras, not canonical `upstream_reference` API.

## Definition of done

- Frozen snapshots are checked in under `compat/upstream_contract/v0.1.1/`.
- Default contract tests do not import `upstream_reference`.
- Ambassador protocols match the snapshot exactly for method and parameter shape.
- Standard modules match or have documented allowed differences.
- `rti_factory.py` is checked as strict standard-facing contract.
- `_byte_wrapper.py` is treated as private but contract-sensitive through encoding tests.
- Runtime/plugin/FOM/backend/transport/vendor/bridge modules are outside the standard contract.
- Updating to a new `upstream_reference` version is a deliberate snapshot refresh with visible JSON diffs.
