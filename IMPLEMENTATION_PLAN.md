# sturdy-broccoli upstream_reference update plan, final handoff

This handoff consolidates the planning discussion and the `upstream_reference v0.1.1` analysis packet into a concrete update plan for `sturdy-broccoli`.

## Closed upstream facts

The upstream information cutoff is now sufficiently covered by the packet.

```text
upstream_reference tag: v0.1.1
upstream_reference full commit: ed39b02e4c6e7813fce9e0e183b184c8513d4dd6
```

Included snapshots:

```text
compat/upstream_contract/v0.1.1/ieee1516e.json
compat/upstream_contract/v0.1.1/ieee1516_2025.json
```

Confirmed counts:

```text
ieee1516e.RTIambassador: 162 methods
ieee1516e.FederateAmbassador: 51 methods
ieee1516_2025.RTIambassador: 188 methods
ieee1516_2025.FederateAmbassador: 56 methods
```

Confirmed naming facts:

```text
canonical exception: RTIexception
not in upstream_reference: RTIException
canonical fields: lower, upper, federationExecutionName, logicalTimeImplementationName, timeIsValid, ahset, rhset
ieee1516e canonical handle method: HandleValueMap.getValueReference
not in upstream_reference: HandleValueMap.get_value_reference
```

Confirmed policy-sensitive facts:

```text
_byte_wrapper.py is private but contract-sensitive.
rti_factory.py is strict standard-facing contract for both standards.
upstream_reference.ieee1516_2025.handles does not expose public HandleValueMap in v0.1.1.
```

## Core architecture

```text
upstream_reference
  canonical standards-contract authority

sturdy-broccoli
  implementation and integration workspace that exposes upstream_reference-compatible standard facades
```

Do not make `sturdy-broccoli` copy `upstream_reference`'s exact repo shape. Split by responsibility.

## First implementation milestone

Add these files to sturdy:

```text
docs/upstream_compliance.md
docs/package_responsibilities.md
docs/migration/upstream_contract_snapshot.md
compat/upstream_contract/README.md
compat/upstream_contract/schema-v1.json
compat/upstream_contract/allowed_differences.json
compat/upstream_contract/v0.1.1/ieee1516e.json
compat/upstream_contract/v0.1.1/ieee1516_2025.json
```

Then add:

```text
scripts/check_upstream_contract.py
tests/compat/test_upstream_contract.py
tests/compat/test_import_boundaries.py
```

The checker and tests should use the checked-in snapshots and must not import live `upstream_reference` in default CI.

## Package split target

```text
hla.rti1516e
hla.rti1516_2025
  standard-facing compatibility facades

hla.runtime / hla-rti-core
  RTI creation, plugins, runtime glue

hla.fom / hla-fom-common
  FOM/MIM loading, validation, resources

hla.spec / hla-spec-tools
  spec refs, source traceability, inventory tooling

hla-backend-*
  backend implementations

hla-transport-*
  transport layers

hla-vendor-*
  vendor adapters

hla-bridge-*
  bridge integrations
```

## Migration order

1. Add docs and frozen snapshot assets.
2. Add local compliance checker and pytest wrapper.
3. Enforce ambassador protocol compatibility first.
4. Enforce enum and exception compatibility.
5. Enforce datatype and handle compatibility.
6. Enforce time, logical_time, encoding, handle_factory, and rti_factory compatibility.
7. Create clearer namespaces: `hla.runtime`, `hla.fom`, `hla.spec`.
8. Move non-standard modules out of standard packages behind compatibility forwarders.
9. Audit backend/vendor/transport imports.
10. Add import-boundary tests.
11. Add CI gates.

## Hard decision rules

```text
If it is IEEE-facing type/protocol surface, it belongs in hla.rti1516e or hla.rti1516_2025.
If it creates, discovers, validates, transports, bridges, adapts, loads FOMs, or runs backends, it belongs outside the standard package.
If it only exists to preserve old imports, keep it as a thin compatibility forwarder with tests.
```

## Runtime dependency policy

Recommended:

```text
sturdy runtime: no required upstream-reference-package dependency
contract refresh/export tooling: may require upstream-reference-package
```

## Definition of done

`sturdy-broccoli` is updated correctly when:

1. `hla.rti1516e` and `hla.rti1516_2025` are standard-facing compatibility facades.
2. The frozen `upstream_reference v0.1.1` snapshots are checked in.
3. Default compliance tests do not import `upstream_reference`.
4. Ambassador method and parameter shapes match the snapshots.
5. Standard enums, exceptions, datatypes, handles, time, logical_time, encoding, handle_factory, and rti_factory match or have documented allowed differences.
6. `_byte_wrapper.py` is protected as private-but-contract-sensitive through encoding surface checks.
7. Runtime/plugin/FOM/backend/transport/vendor/bridge modules are outside the standard contract.
8. Sturdy-only aliases are documented as facade extras in `allowed_differences.json`.
9. Old public imports work through thin forwarders during the transition window.
10. CI fails on unreviewed drift.
11. Updating to a newer `upstream_reference` release is a deliberate snapshot refresh with visible JSON diffs.
