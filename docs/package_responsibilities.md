# Package Responsibilities

Use this rule for every module:

- If it is IEEE-facing type/protocol surface, it belongs in `hla.rti1516e` or
  `hla.rti1516_2025`.
- If it creates, discovers, validates, transports, bridges, adapts, loads FOMs,
  or runs backends, it belongs outside the standard package.
- If a path exists only to preserve an old import, remove it and update the
  downstream import. This repository does not add legacy adapter shims for this
  cleanup.

Current ownership:

| Package namespace | Responsibility |
| --- | --- |
| `hla.rti1516e` | IEEE 1516.1-2010 standard facade |
| `hla.rti1516_2025` | IEEE 1516.1-2025 standard facade |
| `hla.runtime` | RTI creation, runtime composition, spec plugins |
| `hla.rti` | shared runtime registry and plugin API |
| `hla.fom` | FOM/MIM parsing, validation, packaged resources |
| `hla.spec` | spec references and inventory tooling |
| `hla.backends.*` | backend implementations |
| `hla.transports.*` | transport implementations |
| `hla.vendors.*` | vendor integration |
| `hla.bridges.*` | bridge integration |

The final consolidated handoff lives in `IMPLEMENTATION_PLAN.md`; the upstream
packet summary lives under `reference/upstream-analysis-packet/`.

## Distribution And Import Names

Distribution names are hyphenated. Import names are ordinary Python names:

| Distribution | Import package |
| --- | --- |
| `hla-rti1516e` | `hla.rti1516e` |
| `hla-rti1516-2025` | `hla.rti1516_2025` |
| `hla-rti-core` | `hla.runtime`, `hla.rti`, `hla.fom`, `hla.spec` |
| `hla-backend-common` | `hla.backends.common` |
| `hla-backend-python1516e` | `hla.backends.python1516e` |
| `hla-backend-certi` | `hla.backends.certi` |
| `hla-backend-cpp-shim` | `hla.backends.cpp_shim` |
| `hla-transport-common` | `hla.transports.common` |
| `hla-transport-grpc` | `hla.transports.grpc` |
| `hla-transport-rest` | `hla.transports.rest` |
| `hla-vendor-portico` | `hla.vendors.portico` |
| `hla-vendor-pitch-py4j` | `hla.vendors.pitch.py4j` |
| `hla-bridge-java-py4j` | `hla.bridges.java.py4j` |

Long-term singular import roots such as `hla.backend.*`, `hla.transport.*`,
`hla.vendor.*`, and `hla.bridge.*` may be introduced only by deliberate package
renames. They must not coexist ambiguously with plural roots.

## Standard Package Allowlist

Allowed in `hla.rti1516e`:

- `__init__.py`
- `py.typed`
- `datatypes.py`
- `handles.py`
- `enums.py`
- `exceptions.py`
- `rti_ambassador.py`
- `federate_ambassador.py`
- `logical_time.py`
- `time.py`
- `encoding.py`
- `encoding.pyi`
- `handle_factory.py`
- `rti_factory.py`
- `_compat.py`
- `_contract.py`

Allowed in `hla.rti1516_2025`:

- all `hla.rti1516e` standard files
- `auth.py`

Not allowed long-term in standard packages:

- `api.py`
- `ambassadors.py`
- `factory.py`
- `plugin.py`
- `fom.py`
- `foms.py`
- `mom.py`
- `raw_api.py`
- `rti.py`
- `spec_inventory.py`
- `spec_refs.py`
- `spec_sources.py`
- `validation.py`

## Resource Ownership

All package data must live under a `resources/` directory. FOM, MIM, schema,
XML, JSON metadata, and bundled vendor resources must not live under
`hla.rti1516e` or `hla.rti1516_2025`.

Preferred access pattern:

```python
from importlib.resources import files

schema_path = files("hla.fom.resources.schemas").joinpath("HLAstandardMIM.xsd")
```

Code must not assume resources exist relative to the current working directory.
Avoid `__file__` path walking unless there is no reasonable alternative.

## Dependency Direction

Allowed examples:

- `hla.runtime -> hla.rti1516e`
- `hla.runtime -> hla.rti1516_2025`
- `hla.fom -> hla.rti1516e`
- `hla.fom -> hla.rti1516_2025`
- `hla.backends.common -> hla.rti1516e`
- `hla.backends.python1516e -> hla.backends.common`
- `hla.vendors.portico -> hla.backends.common`
- `hla.transports.grpc -> hla.transports.common`

Forbidden examples:

- `hla.rti1516e -> hla.runtime`
- `hla.rti1516e -> hla.fom`
- `hla.rti1516e -> hla.backends`
- `hla.rti1516e -> hla.transports`
- `hla.rti1516e -> hla.vendors`
- `hla.rti1516_2025 -> hla.runtime`
- `hla.rti1516_2025 -> hla.fom`
- `hla.rti1516_2025 -> hla.backends`
- `hla.rti1516_2025 -> hla.transports`
- `hla.rti1516_2025 -> hla.vendors`

Temporary compatibility forwarders are the only exception. They must be
explicitly listed, import-tested, and removed on schedule.
