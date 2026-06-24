# upstream_reference Compliance Boundary

`upstream_reference` is the canonical standards-contract authority. This workspace is a
upstream_reference-compatible implementation and integration workspace.

Frozen upstream basis:

- `upstream_reference` tag: `v0.1.1`
- full commit: `ed39b02e4c6e7813fce9e0e183b184c8513d4dd6`
- contract snapshots:
  - `compat/upstream_contract/v0.1.1/ieee1516e.json`
  - `compat/upstream_contract/v0.1.1/ieee1516_2025.json`

The standard-facing packages are:

- `hla.rti1516e`
- `hla.rti1516_2025`

Those packages expose IEEE-facing types, protocols, enums, exceptions, handles,
datatypes, logical time, time, and encoding surfaces. They must not own runtime
discovery, backend loading, transport setup, vendor integration, FOM loading,
validation, resource lookup, or traceability tooling.

Implementation responsibilities live outside the standard facades:

- `hla.runtime`: RTI creation, provider selection, plugin descriptors, runtime glue.
- `hla.fom`: FOM/MIM loading, packaged FOM resources, OMT parsing, validation.
- `hla.spec`: standards references, source traceability, inventory tooling.
- `hla.backends.*`: backend implementations.
- `hla.transports.*`: transport layers.
- `hla.vendors.*`: vendor adapters.
- `hla.bridges.*`: bridge integrations.

Default compliance tests compare local standard facades against frozen JSON
snapshots under `compat/upstream_contract`. These tests do not import `upstream_reference`.
Updating to a newer upstream_reference release is a deliberate snapshot refresh with visible
JSON diffs.

Confirmed `upstream_reference v0.1.1` facts:

- `ieee1516e.RTIambassador`: 162 methods
- `ieee1516e.FederateAmbassador`: 51 methods
- `ieee1516_2025.RTIambassador`: 188 methods
- `ieee1516_2025.FederateAmbassador`: 56 methods
- canonical exception spelling: `RTIexception`
- sturdy-only exception alias, if retained: `RTIException`
- canonical range fields: `RangeBounds.lower`, `RangeBounds.upper`
- sturdy-only range aliases, if retained: `lower_bound`, `upper_bound`
- canonical 1516e handle method: `HandleValueMap.getValueReference`
- sturdy-only handle alias, if retained: `get_value_reference`
- `rti_factory.py` is strict standard-facing contract for both standards
- `_byte_wrapper.py` is private but contract-sensitive through encoding

## Hard Layout Rules

These rules are non-negotiable architecture constraints:

1. `hla` is a PEP 420 namespace package. No distribution may ship
   `src/hla/__init__.py`.
2. Distribution names may use hyphens. Python import names must not.
3. Standard packages may contain only IEEE-facing types, protocols, standard
   factory interfaces, compatibility aliases, contract metadata, and root
   convenience facades.
4. Runtime, plugin, backend, transport, vendor, bridge, FOM, validation, and
   spec-tooling code must live outside `hla.rti1516e` and `hla.rti1516_2025`.
5. Old imports may survive only as thin compatibility forwarders with tests.
   A forwarder may import and re-export; it may not contain business logic.
6. Package data must live under `resources/` and be loaded with
   `importlib.resources`.
7. FOM, MIM, schema, XML, JSON metadata, and bundled vendor resources belong
   under `hla.fom.resources` or another dedicated resource package, not under
   `hla.rti1516e` or `hla.rti1516_2025`.
8. Frozen upstream_reference snapshots belong under `compat/upstream_contract/v<version>/` and
   are not runtime assets.
9. Default CI must not require live `upstream_reference`.
10. Public typed packages must include `py.typed`; shipped `.pyi` files must
    agree with runtime Python files.
11. Dependency direction is one-way: runtime/FOM/backend/vendor/transport
    packages may depend on standard facades; standard facades may not depend on
    runtime/FOM/backend/vendor/transport packages.
12. Public facade modules define intent with `__all__`. Contract tests compare
    concrete standard modules, not root facade convenience exports.

## Contract Snapshot Rules

Contract snapshots are development and CI assets, not runtime API. Runtime
packages must not import files from `compat/upstream_contract`, and default runtime
packages must not require `upstream_reference` to be installed.

Generated JSON snapshots must be deterministic, use sorted keys, and include
metadata describing the schema and upstream_reference source release. Generated snapshots
must not include upstream_reference implementation source or docstrings as contract
requirements.
