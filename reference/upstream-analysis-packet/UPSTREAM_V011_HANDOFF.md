# upstream_reference v0.1.1 Handoff Packet

Source basis:
- Tag: `v0.1.1`
- Full commit: `ed39b02e4c6e7813fce9e0e183b184c8513d4dd6`
- Export basis: detached worktree at `/tmp/upstream_reference-v011`
- Exported snapshots:
  - `compat/upstream_contract/v0.1.1/ieee1516e.json`
  - `compat/upstream_contract/v0.1.1/ieee1516_2025.json`

Important scope note:
- This packet answers what can be proven from `upstream_reference v0.1.1` itself.
- Sturdy-specific package/layout/CI policy questions that cannot be derived from `upstream_reference` are marked as such.
- No local `sturdy-broccoli` checkout was found under `/home/rick/GIT/ado-clones`, so sturdy-side questions were not directly inspected here.

## Highest-priority answers

### 1. Exact full commit hash for `upstream_reference v0.1.1`
- `ed39b02e4c6e7813fce9e0e183b184c8513d4dd6`

### 2. Real exported contract snapshots
- Yes. They were exported into this packet at:
  - `compat/upstream_contract/v0.1.1/ieee1516e.json`
  - `compat/upstream_contract/v0.1.1/ieee1516_2025.json`
- These JSON files capture module public symbols, enums, exceptions, dataclass fields, NamedTuple fields, public class methods, and ambassador method counts from the tagged `v0.1.1` source tree.

### 3. Whether `upstream-reference-package` may be a sturdy runtime dependency
- This is not a `upstream_reference` fact. It is a sturdy policy decision.
- Recommended decision:
  - sturdy runtime: no `upstream-reference-package` dependency required
  - contract refresh/export tooling: `upstream-reference-package` allowed/required
- Rationale: keeps sturdy usable standalone while still allowing exact contract refresh against live `upstream_reference` when needed.

### 4. Public contract vs implementation detail
- `encoding.pyi`: treat as contract. It is shipped in package data for both standards.
- `federate_ambassador.pyi`: treat as contract. It is shipped in package data for both standards.
- `rti_ambassador.pyi`: treat as contract. It is shipped in package data for both standards.
- `py.typed` inside `upstream_reference.ieee1516e` and `upstream_reference.ieee1516_2025`: treat as contract. Those files are explicitly listed in package data.
- top-level `src/upstream_reference/py.typed`: present in the repo, but not explicitly listed in `tool.setuptools.package-data` in `v0.1.1`; do not rely on it as the primary packaging contract signal.
- `_byte_wrapper.py`: do **not** treat as a canonical user-facing public API surface. However, it is not safely disposable either:
  - both `encoding.py` and `encoding.pyi` import `ByteWrapper` from `._byte_wrapper`
  - that makes `_byte_wrapper.py` a typing/runtime support surface
  - recommended contract stance: private implementation module, but contract-sensitive because renaming/removing it breaks typed/runtime encoding surfaces

### 5. Whether `rti_factory.py` is strict standard-facing contract
- Yes for both standards.
- `upstream_reference.ieee1516e.rti_factory` is part of the tagged tree and exports `RtiFactory`, `RtiFactoryFactory`, `RTIambassador`, and entry-point group constants.
- `upstream_reference.ieee1516_2025.rti_factory` is likewise standard-facing and additionally re-exports `EncoderFactory`.
- Caution for sturdy: do not conflate sturdy runtime/plugin internals with `upstream_reference`’s standard contract. Compatibility checks should compare against `upstream_reference.*.rti_factory`, not against sturdy-specific `factory.py` or plugin modules.

## Questions 6-10: symbol and type facts captured from `v0.1.1`

### 6. Full public symbol list per requested module
The full lists are in the JSON snapshots. Summary module coverage exported:

- `upstream_reference.ieee1516e`
  - `datatypes`, `handles`, `enums`, `exceptions`, `logical_time`, `time`, `encoding`, `handle_factory`, `rti_factory`, `rti_ambassador`, `federate_ambassador`
- `upstream_reference.ieee1516_2025`
  - `datatypes`, `handles`, `enums`, `exceptions`, `logical_time`, `time`, `encoding`, `handle_factory`, `rti_factory`, `rti_ambassador`, `federate_ambassador`, `auth`

Notable examples:
- `upstream_reference.ieee1516e.rti_factory` public symbols: ['IMPLEMENTATION_ENTRY_POINT_GROUP', 'RTI_FACTORY_ENTRY_POINT_GROUP', 'RTIambassador', 'RtiFactory', 'RtiFactoryFactory']
- `upstream_reference.ieee1516_2025.rti_factory` public symbols: ['EncoderFactory', 'IMPLEMENTATION_ENTRY_POINT_GROUP', 'RTI_FACTORY_ENTRY_POINT_GROUP', 'RTIambassador', 'RtiFactory', 'RtiFactoryFactory']
- `upstream_reference.ieee1516e.handles` public symbols include `HandleValueMap`, `AttributeHandleValueMap`, `ParameterHandleValueMap`, `BytesLike`
- `upstream_reference.ieee1516_2025.handles` public symbols include `AttributeHandleValueMap`, `ParameterHandleValueMap`, `BytesLike`, but **not** `HandleValueMap`

### 7. Enum names, members, and values
- Yes. Exact enum names, members, and wire values are captured in both JSON snapshots.
- Enum counts:
  - `ieee1516e`: 10
  - `ieee1516_2025`: 12
- Examples from the snapshot:
  - `ieee1516e.CallbackModel`: `HLA_IMMEDIATE=1`, `HLA_EVOKED=2`
  - `ieee1516_2025.CallbackModel`: `HLA_IMMEDIATE=0`, `HLA_EVOKED=1`
  - `ieee1516_2025.AdditionalSettingsResultCode`: `SETTINGS_IGNORED=0`, `SETTINGS_FAILED_TO_PARSE=1`, `SETTINGS_APPLIED=2`

### 8. Exception class spelling/capitalization
- Yes. Exact exception class names are captured in the snapshots.
- `RTIexception` is present in both standards.
- `RTIException` is **not** present in either standard and is not canonical in `upstream_reference v0.1.1`.
- Exception counts:
  - `ieee1516e`: 110
  - `ieee1516_2025`: 110

### 9. Dataclass and NamedTuple field names
Canonical `upstream_reference v0.1.1` field names relevant to sturdy alias cleanup:

- `ieee1516e.RangeBounds`: ['lower', 'upper']
- `ieee1516_2025.RangeBounds`: ['lower', 'upper']
- `ieee1516e.FederationExecutionInformation`: ['federationExecutionName', 'logicalTimeImplementationName']
- `ieee1516_2025.FederationExecutionInformation`: ['federationExecutionName', 'logicalTimeImplementationName']
- `ieee1516e.TimeQueryReturn`: ['timeIsValid', 'time']
- `ieee1516_2025.TimeQueryReturn`: ['timeIsValid', 'time']
- `ieee1516e.AttributeRegionAssociation`: ['ahset', 'rhset']
- `ieee1516_2025.AttributeRegionAssociation`: ['ahset', 'rhset']

Implication:
- canonical `upstream_reference` names are `lower`, `upper`, `federationExecutionName`, `logicalTimeImplementationName`, `timeIsValid`, `ahset`, `rhset`
- sturdy spellings like `lower_bound`, `upper_bound`, `federation_execution_name`, `logical_time_implementation_name`, `time_is_valid`, `attributes`, `regions` are sturdy-side aliases, not `upstream_reference` canon

### 10. Handle class methods
- Yes. Exact public methods per handle class are captured in the JSON snapshots.
- Critical fact:
  - `upstream_reference.ieee1516e.handles.HandleValueMap` methods: ['clone', 'getValueReference', 'key_type', 'update']
  - `getValueReference` exists in `ieee1516e`
  - `get_value_reference` does **not** exist in `ieee1516e`
- For `ieee1516_2025`, there is no public `HandleValueMap` symbol in `handles`; the package exposes typed maps such as `AttributeHandleValueMap` and `ParameterHandleValueMap` instead.

## Questions 11-13: ambassador protocol facts

### 11. Final ambassador method counts for `v0.1.1`
The remembered counts are correct for the `v0.1.1` tag:

- `ieee1516e.RTIambassador`: 162 methods
- `ieee1516e.FederateAmbassador`: 51 methods
- `ieee1516_2025.RTIambassador`: 188 methods
- `ieee1516_2025.FederateAmbassador`: 56 methods

### 12. What ambassador comparisons should check
- This is a checker-policy decision, not a `upstream_reference` fact.
- Recommended v1 strictness:
  - strict: method names, parameter names, parameter kind, required/default status
  - non-strict initially: type annotations, return annotations
- Rationale: method shape is the real interop contract; annotation strictness can be added later without blocking initial compatibility work.

### 13. Intentional ambassador differences allowlist
- No intentional differences are known from `upstream_reference` itself.
- Recommended compatibility stance: ambassador protocols should match strictly unless a concrete, documented sturdy divergence is found later.

## Questions 14-16: compatibility alias recommendations

### 14. `RTIException` alias in sturdy
- Not a `upstream_reference` fact; sturdy policy decision.
- Recommendation: keep `RTIException` as a facade alias for compatibility, but never treat it as canonical. Canonical `upstream_reference` spelling is `RTIexception`.

### 15. Pythonic snake_case datatype aliases in sturdy
- Not a `upstream_reference` fact; sturdy policy decision.
- Recommendation: keep only if existing sturdy consumers demonstrably depend on them. Otherwise deprecate/remove once contract tests are in place.

### 16. `HandleValueMap.get_value_reference`
- Not a `upstream_reference` fact; sturdy policy decision.
- Recommendation: allow as a sturdy convenience alias if needed, but contract tests must require canonical `getValueReference` wherever `upstream_reference` defines it.

## Questions 17-20: sturdy package layout and Python baseline

### 17. First refactor: namespaces vs distributions
- Not a `upstream_reference` fact; sturdy architecture decision.
- Recommendation: first create clearer namespaces, later split distributions only where dependency boundaries require it.
- Recommended direction: `hla.runtime`, `hla.fom`, `hla.spec`

### 18. Is `hla` already a namespace package in sturdy?
- Unanswered here. Requires sturdy repo inspection.

### 19. Which build backend is sturdy using?
- Unanswered here. Requires sturdy repo inspection.

### 20. What is sturdy’s minimum Python version?
- Unanswered here. Requires sturdy repo inspection.
- Relevant `upstream_reference` fact: `upstream-reference-package` declares `requires-python = ">=3.11"` in `v0.1.1`.

## Questions 21-23: assets and generated spec data

### 21. Asset bundling inside sturdy standard packages
- Unanswered here. Requires sturdy repo inspection.

### 22. Direct filesystem path reliance for bundled assets
- Unanswered here. Requires sturdy repo inspection.
- Recommendation if migration is needed: prefer `importlib.resources`.

### 23. `spec_refs`, `spec_sources`, `spec_inventory` generated vs hand-written
- Unanswered here. Requires sturdy repo inspection.

## Questions 24-26: CI and release policy recommendations

### 24. CI failure mode for extra sturdy symbols
- Not a `upstream_reference` fact; checker-policy decision.
- Recommendation:
  - normal mode: fail on missing/mismatched canonical `upstream_reference` symbols; allow documented sturdy extras
  - strict mode: also fail undocumented extras

### 25. Separate internal CI job to refresh snapshots from live `upstream_reference`
- Recommendation: yes.
- Suggested command shape:

```bash
python scripts/export_upstream_contract.py   --out compat/upstream_contract/v0.1.1   --upstream_reference-version v0.1.1
```

- Public/default CI should use frozen snapshots and not require live `upstream_reference` access.

### 26. Deprecation window for old sturdy imports
- Not a `upstream_reference` fact; release-policy decision.
- Recommendation: because sturdy is still pre-1.0 and these look internal/cleanup-driven, remove immediately only if you have high confidence they are not used; otherwise keep until `1.0` with explicit migration notes.
- Conservative default if uncertain: keep until `1.0`.

## The five answers that matter most

1. `upstream_reference v0.1.1` full commit is `ed39b02e4c6e7813fce9e0e183b184c8513d4dd6`.
2. Real snapshots are included in this packet for `ieee1516e` and `ieee1516_2025`.
3. `_byte_wrapper.py` is private-but-contract-sensitive; `rti_factory.py` is strict standard-facing contract for both standards.
4. Recommended sturdy policy: no runtime dependency on `upstream-reference-package`; allow it for contract refresh tooling.
5. Recommended sturdy alias policy: keep compatibility aliases only as non-canonical facades; contract tests must enforce `upstream_reference` canonical names.

## Packet contents

- `upstream_reference_V011_HANDOFF.md`
- `snapshot_summary.json`
- `compat/upstream_contract/v0.1.1/ieee1516e.json`
- `compat/upstream_contract/v0.1.1/ieee1516_2025.json`
