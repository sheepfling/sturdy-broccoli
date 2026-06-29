# 2025 Python RTI Umbrella Decomposition Worklist

Use this note when the question is:

- what exactly would it take to convert the remaining `2025`
  `duplicate/umbrella` rows into narrower direct claims?
- which child rows already carry the current proof?
- which shard, view, and owner doc should move if leadership wants literal
  `691 / 691 covered` instead of the current honest `645 / 645` active-row
  metric?

This note is the concrete umbrella-row execution companion to:

- [`PLN-004_python_rti_100_percent_compliance_plan.md`](PLN-004_python_rti_100_percent_compliance_plan.md)
- [`2025_python_rti_100_percent_worklist.md`](2025_python_rti_100_percent_worklist.md)

## Current Truth

The current canonical 2025 requirement catalog has:

- `22` rows in `duplicate/umbrella`
- `10` framework umbrella rows
- `12` callback/configuration/binding delta umbrella rows

Those rows are already dispositioned honestly.
They are not missing-owner rows.
They are non-standalone parent or normalization rows whose normative force is
already carried by linked child rows and owner docs.

Use the current metric split:

1. `100% dispositioned` across all `691` tracked rows
2. `100% covered` across the `645` active normative non-retired
   non-umbrella rows

Do not promote the `22` umbrella rows to direct `covered` unless the repo
deliberately funds narrower standalone executable child claims.

## Decomposition Rule

For each umbrella row, choose one of two paths:

1. keep it as an umbrella row
2. replace it with one or more narrower direct claims

### Keep-As-Umbrella Rule

Keep the row `duplicate/umbrella` when all of these remain true:

1. the child rows already carry the executable proof
2. the umbrella row adds organizational or standards-structure value
3. promoting the umbrella row would double-count child proof

### Convert-To-Direct Rule

Only convert an umbrella row into a direct `covered` claim when all of these
are true:

1. the new claim is narrower than the current umbrella wording
2. the exact child-proof target is named
3. the narrowest owning shard is named
4. at least one executable anchor and one owner-doc anchor are recorded
5. the canonical requirement row and the owner doc are updated together

## Common Column Meanings

| Column | Meaning |
| --- | --- |
| `Primary owner doc` | current canonical umbrella owner |
| `Child rows` | rows that currently carry the normative force |
| `Primary shard now` | current narrowest proof owner |
| `Primary views` | overlapping audit or focused rerun slices |
| `Backend resolution now` | which backend or route currently owns the real child proof |
| `Current disposition` | current honest row role |
| `Stay umbrella when` | condition for leaving the row as-is |
| `Convert only if` | minimum condition for direct `covered` promotion |

## Framework Umbrella Rows

Primary owner:
[`../requirements/ieee-1516-2025/framework_rules.md`](../requirements/ieee-1516-2025/framework_rules.md)

Typical shard and views:

- primary shard now: `unit-python-2025-core`
- widen to: `python1516_2025-main` or `python1516_2025-routes` only if a new
  direct claim materially crosses that boundary
- primary views: `2025-core`, `finish-line`, `scenarios`

| Row | Service/check | Child rows | Primary shard now | Primary views | Backend resolution now | Current disposition | Stay umbrella when | Convert only if |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `HLA2025-FR-001` | `Federation FOM` | `HLA2025-REQ-001`, `HLA2025-OMT-001`, `HLA2025-OMT-005`, `HLA2025-OMT-006` | `unit-fom-tooling` | `2025-core`, `fom-omt`, `finish-line` | direct `python1516_2025` runtime plus FOM/OMT tooling; no alternate backend owner | `duplicate/umbrella` | OMT validation and FOM packaging remain the real proof units | a narrower direct FOM-documented runtime claim is created and tied to explicit OMT and executable anchors |
| `HLA2025-FR-002` | `Federate-held object state` | `HLA2025-FI-001`, `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-060`, `HLA2025-FI-SVC-065`, `HLA2025-FI-SVC-066` | `unit-python-2025-core` | `2025-core`, `scenarios` | direct `python1516_2025` runtime owner; hosted route evidence only where linked child rows use it | `duplicate/umbrella` | object exchange, deletion, and rollback child rows remain the real proof owners | a narrower direct object-state boundary claim is created with isolated executable proof beyond the current child rows |
| `HLA2025-FR-003` | `RTI-mediated FOM data exchange` | `HLA2025-FI-001`, `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-060`, `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064` | `unit-transport-local` | `2025-core`, `transport`, `scenarios` | direct `python1516_2025` runtime plus bounded hosted FedPro route proof; not a second RTI lane | `duplicate/umbrella` | object and interaction exchange rows remain the real proof units | a narrower direct route-mediated exchange claim is created with isolated direct-lane proof plus hosted FedPro route proof |
| `HLA2025-FR-004` | `FI-conformant RTI interaction` | `HLA2025-FI-001`, `HLA2025-FI-002`, `HLA2025-FI-003`, `HLA2025-FI-004`, `HLA2025-FI-005`, `HLA2025-FI-006`, `HLA2025-FI-009` | `unit-python-2025-core` | `2025-core`, `java-shim`, `cpp-shim` | direct `python1516_2025` runtime owner plus wrapper-only Java/C++ binding surfaces | `duplicate/umbrella` | the linked FI and binding rows remain the real proof owners | a narrower direct surface claim is created that does not collapse direct runtime, bindings, and hosted routes into one umbrella |
| `HLA2025-FR-005` | `Single-owner instance attributes` | `HLA2025-FI-001`, `HLA2025-FI-SVC-082`, `HLA2025-FI-SVC-083`, `HLA2025-FI-SVC-089`, `HLA2025-FI-SVC-090`, `HLA2025-FI-SVC-095` | `unit-python-2025-core` | `2025-core`, `ownership`, `scenarios` | direct `python1516_2025` runtime owner; other backends remain separate vendor-resolution questions | `duplicate/umbrella` | ownership acquisition/divestiture/query child rows remain the real proof owners | a narrower direct one-owner-at-a-time claim is created with isolated ownership-only executable proof |
| `HLA2025-FR-006` | `Federate SOM` | `HLA2025-REQ-001`, `HLA2025-FR-001`, SOM/FOM service-usage rows in `hla_2025_requirement_depth_expansion.csv` | `unit-fom-tooling` | `2025-core`, `fom-omt`, `finish-line` | documentation and tooling owner over the main `python1516_2025` lane; no standalone backend claim | `duplicate/umbrella` | SOM/FOM documentation remains a traceability-owned claim rather than a runtime-owned claim | a narrower direct SOM documentation claim is created with explicit source and executable linkage instead of broad umbrella wording |
| `HLA2025-FR-007` | `SOM-declared data exchange capability` | `HLA2025-FI-001`, `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-060`, `HLA2025-FI-SVC-061`, `HLA2025-FI-SVC-063` | `unit-scenarios-light` | `2025-core`, `scenarios` | direct `python1516_2025` runtime plus scenario proof; no alternate backend owner | `duplicate/umbrella` | data-exchange child rows and scenario proof remain the real owners | a narrower direct SOM-usage claim is created with isolated scenario-backed proof |
| `HLA2025-FR-008` | `SOM-declared ownership capability` | `HLA2025-FI-001`, `HLA2025-FI-SVC-082`, `HLA2025-FI-SVC-083`, `HLA2025-FI-SVC-084`, `HLA2025-FI-SVC-085`, `HLA2025-FI-SVC-095` | `unit-python-2025-core` | `2025-core`, `ownership`, `scenarios` | direct `python1516_2025` runtime owner; hosted replay only where child ownership rows cite it | `duplicate/umbrella` | ownership transfer child rows remain the real proof owners | a narrower direct SOM-ownership claim is created with isolated ownership negotiation proof |
| `HLA2025-FR-009` | `SOM-declared update conditions` | `HLA2025-FI-SVC-068`, `HLA2025-FI-SVC-069`, `HLA2025-FI-SVC-070`, `HLA2025-FI-SVC-071`, `HLA2025-FI-SVC-155`, `HLA2025-FI-SVC-156` | `unit-python-2025-core` | `2025-core`, `scenarios` | direct `python1516_2025` runtime owner; wrapper or hosted evidence is only secondary if linked child rows require it | `duplicate/umbrella` | update-condition child rows remain the real owners | a narrower direct threshold or advisory-condition claim is created with isolated update-condition proof |
| `HLA2025-FR-010` | `Local time management` | `HLA2025-FI-009`, `HLA2025-MOD-006`, `HLA2025-FI-SVC-101`, `HLA2025-FI-SVC-107`, `HLA2025-FI-SVC-112`, `HLA2025-FI-SVC-121` | `unit-python-2025-core` | `2025-core`, `time`, `finish-line` | direct `python1516_2025` runtime plus bounded hosted FedPro replay; not an alternate backend owner | `duplicate/umbrella` | time-management child rows and lookahead-window proof remain the real owners | a narrower direct local-time-management claim is created with isolated time-only proof that does more than summarize child rows |

## Callback, Configuration, and Binding Umbrella Rows

Primary owner:
[`../requirements/ieee-1516-2025/callback_binding_deltas.md`](../requirements/ieee-1516-2025/callback_binding_deltas.md)

Typical shard and views:

- primary shard now: varies by row; use the narrowest child-proof owner first
- widen to: `python1516_2025-routes` or binding-specific evidence only when the
  narrower row truly crosses that boundary
- primary views: `2025-core`, `transport`, `java-shim`, `cpp-shim`

| Row | Service/check | Child rows | Primary shard now | Primary views | Backend resolution now | Current disposition | Stay umbrella when | Convert only if |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `HLA2025-FI-CB-001` | `Callback model selection` | `HLA2025-FI-005`, `HLA2025-MOD-001` | `unit-python-2025-core` | `2025-core`, `transport` | direct `python1516_2025` runtime owner plus bounded hosted route replay | `duplicate/umbrella` | connect/config/model-selection child rows remain the real proof owners | a narrower callback-model claim is created with direct IMMEDIATE versus EVOKED executable proof |
| `HLA2025-FI-CB-002` | `Evoke Callback` | `HLA2025-FI-SVC-193` | `unit-python-2025-core` | `2025-core`, `java-shim`, `cpp-shim` | direct `python1516_2025` runtime owner; Java/C++ are wrapper-only route surfaces | `duplicate/umbrella` | the service row already carries explicit EVOKED callback proof | a narrower direct evoke-callback claim is created with positive, empty-queue, disabled, and exception-path proof |
| `HLA2025-FI-CB-003` | `Evoke Multiple Callbacks` | `HLA2025-FI-SVC-194` | `unit-python-2025-core` | `2025-core`, `java-shim`, `cpp-shim` | direct `python1516_2025` runtime owner; Java/C++ are wrapper-only route surfaces | `duplicate/umbrella` | the service row already carries queue-drain proof | a narrower direct evoke-multiple-callbacks claim is created with bounded timing and no-callback-path proof |
| `HLA2025-FI-CB-004` | `Enable/Disable Callbacks` | `HLA2025-FI-SVC-195`, `HLA2025-FI-SVC-196` | `unit-python-2025-core` | `2025-core`, `transport` | direct `python1516_2025` runtime owner plus bounded hosted route replay | `duplicate/umbrella` | callback-control child rows remain the real proof owners | a narrower direct callback-control claim is created with stateful enable/disable proof across callback classes |
| `HLA2025-FI-CB-005` | `Federate Resigned callback` | `HLA2025-FI-SVC-012` | `unit-python-2025-core` | `2025-core`, `transport`, `scenarios` | direct `python1516_2025` runtime owner plus hosted replay where linked child proof uses it | `duplicate/umbrella` | resign callback child proof remains sufficient | a narrower direct resigned-callback claim is created with forced/automatic resign plus post-resign rejection proof |
| `HLA2025-FI-CB-006` | `Federation execution member reporting` | `HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-009` | `unit-python-2025-core` | `2025-core`, `transport` | direct `python1516_2025` runtime owner plus hosted replay where linked child proof uses it | `duplicate/umbrella` | reporting service child rows remain the real owners | a narrower direct member-reporting claim is created with positive and nonexistent-federation proof |
| `HLA2025-FI-CB-007` | `Directed interaction callback parameterization` | `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`, `HLA2025-BND-003` | `unit-transport-local` | `2025-core`, `transport`, `finish-line` | direct `python1516_2025` runtime plus bounded hosted FedPro route parity; not a second backend owner | `duplicate/umbrella` | directed interaction child rows and route parity remain the real owners | a narrower direct directed-routing callback claim is created with target, unauthorized, unsubscribed, and invalid-parameter proof |
| `HLA2025-FI-CB-008` | `Flush Queue Grant callback` | `HLA2025-FI-SVC-112` | `unit-python-2025-core` | `2025-core`, `time`, `transport` | direct `python1516_2025` runtime owner plus hosted replay where linked child proof uses it | `duplicate/umbrella` | the time callback child row remains the real proof owner | a narrower direct flush-queue-grant claim is created with time-regulating and time-constrained proof |
| `HLA2025-FI-CFG-001` | `Configuration and additional settings result` | `HLA2025-FI-005`, `HLA2025-MOD-001`, `HLA2025-BND-003` | `unit-python-2025-core` | `2025-core`, `transport` | direct `python1516_2025` runtime owner; hosted route only carries bounded request-shape replay | `duplicate/umbrella` | connect/configuration child rows remain the real owners | a narrower direct configuration-result claim is created with absent, named, invalid, and applied-settings proof |
| `HLA2025-FI-AUTH-001` | `Authorization credentials` | `HLA2025-FI-005`, `HLA2025-MOD-001`, `HLA2025-BND-003` | `unit-python-2025-core` | `2025-core`, `transport` | direct `python1516_2025` runtime owner; hosted route only carries bounded request-shape replay | `duplicate/umbrella` | connect/auth child rows remain the real owners | a narrower direct authorization-credentials claim is created with no-credentials, plaintext-password, invalid, and unauthorized proof |
| `HLA2025-BIND-FEDPRO-001` | `FedPro protocol split` | `HLA2025-BND-003`, `HLA2025-FI-004` | `unit-transport-local` | `transport`, `finish-line` | bounded hosted FedPro route over `hla-backend-python1516-2025`; not an independent RTI owner | `duplicate/umbrella` | FedPro route parity remains a bounded hosted-route claim over the main runtime | a narrower direct FedPro protocol capability claim is created with explicit proto, serialization, callback, and error-mapping proof |
| `HLA2025-BIND-JAVA-CPP-001` | `Java/C++ binding split` | `HLA2025-BND-001`, `HLA2025-BND-002`, `HLA2025-FI-003`, `HLA2025-FI-004` | `unit-shim-tooling` | `java-shim`, `cpp-shim`, `finish-line` | wrapper-only Java/C++ binding surfaces over the direct `python1516_2025` runtime; no alternate RTI owner | `duplicate/umbrella` | binding-capability child rows and route traces remain the real owners | a narrower direct Java/C++ binding capability claim is created with explicit package/header/factory/exception-name parity proof |

## Latest Investigated Decision

The framework umbrella slice was re-audited on `2026-06-26` against the
current owner doc, canonical requirement catalog, child-row map, runtime tests,
scenario suites, and traceability anchors for:

- `HLA2025-FR-001` through `HLA2025-FR-010`

Decision:

- keep these rows as `duplicate/umbrella`
- do not promote them to standalone `covered`

Reason:

1. the linked FI, OMT, traceability, ownership, scenario, and time rows
   already carry the real executable or bounded documentation semantics for
   the framework rules
2. the current framework owner doc already expresses the narrow honest reading
   for each rule without creating a second proof bucket over the child rows
3. no narrower standalone framework claim was identified that would do more
   than restate the linked child proof
4. converting the framework rows now would double-count child proof instead of
   tightening it

Current evidence reviewed for this decision included:

- `tests/test_rti1516_2025_python1516_2025_runtime.py`
- `tests/transport/test_grpc_transport_2025.py`
- `tests/scenarios/test_proto2025_fom_showcase.py`
- `tests/scenarios/test_target_radar_scenario.py`
- `tests/scenarios/test_ownership_management_backend_matrix.py`
- `tests/test_rti1516_2025_validation.py`
- `docs/requirements/ieee-1516-2025/traceability_matrix.md`
- `requirements/2025/canonical_requirements.json`

Operational effect:

- the framework slice remains a maintained umbrella boundary
- the active decomposition queue should advance only if leadership wants
  literal `691 / 691 covered` or if the repo deliberately introduces narrower
  framework child claims

The first queued callback-control umbrella slice was re-audited on `2026-06-26`
against the current owner doc, canonical requirement catalog, and executable
anchors for:

- `HLA2025-FI-CB-002`
- `HLA2025-FI-CB-003`
- `HLA2025-FI-CB-004`

Decision:

- keep these rows as `duplicate/umbrella`
- do not promote them to standalone `covered`

Reason:

1. `HLA2025-FI-SVC-193` through `HLA2025-FI-SVC-196` already carry the direct
   FI service semantics for `evokeCallback`, `evokeMultipleCallbacks`,
   `enableCallbacks`, and `disableCallbacks`
2. current runtime and transport tests already prove the positive, empty-queue,
   queue-drain, and enable/disable behavior as child-row evidence
3. no narrower standalone callback-control claim was identified that would do
   more than restate the child service rows
4. converting the umbrella rows now would double-count the existing child proof
   instead of tightening it

Current evidence reviewed for this decision included:

- `tests/test_rti1516_2025_python1516_2025_runtime.py`
- `tests/backends/test_python_backend_support_services.py`
- `tests/scenarios/test_support_services_backend_matrix.py`
- `tests/transport/test_grpc_transport_2025.py`
- `requirements/2025/canonical_requirements.json`
- `../requirements/ieee-1516-2025/callback_binding_deltas.md`

Operational effect:

- the callback-control slice remains a maintained boundary surface
- the active decomposition queue should advance to the next unresolved
  candidate instead of trying to force literal `691 / 691 covered` through
  duplicate callback-service claims

The FedPro protocol umbrella slice was also re-audited on `2026-06-26`
against the current owner docs, harmonization artifacts, route-parity matrix,
transport proof, and FedPro proto surfaces for:

- `HLA2025-BIND-FEDPRO-001`

Decision:

- keep this row as `duplicate/umbrella`
- do not promote it to standalone `covered`

Reason:

1. `HLA2025-BND-003` already carries the bounded hosted FedPro/protobuf child
   surface
2. the current owner docs already capture the real claim as bounded hosted
   request/response/callback parity over `hla-backend-python1516-2025`
3. current transport and route-parity evidence already prove the real wire
   surface without turning it into a second RTI implementation claim
4. no narrower standalone protocol-capability claim was identified that would
   do more than restate the bounded route-parity child proof

Current evidence reviewed for this decision included:

- `tests/transport/test_grpc_transport_2025.py`
- `tests/requirements/test_2025_route_parity_matrix.py`
- `tests/requirements/test_2025_tail_backlog_evidence.py`
- `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`
- `packages/hla-transport-grpc/proto/rti1516_2025/fedpro`
- `../requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md`
- `../requirements/ieee-1516-2025/hosted_fedpro_bounded_proof.md`
- `../requirements/ieee-1516-2025/callback_binding_deltas.md`

Operational effect:

- the FedPro protocol slice remains a maintained bounded hosted-route surface
- the active decomposition queue should advance to the next real tightening
  bucket instead of relabeling bounded route traceability as a direct runtime
  claim

The configuration and authorization umbrella slice was also re-audited on
`2026-06-26` against the current owner doc, canonical requirement catalog, connect
runtime tests, factory composition tests, hosted FedPro request mapping, and
factory/auth implementation anchors for:

- `HLA2025-FI-CFG-001`
- `HLA2025-FI-AUTH-001`

Decision:

- keep these rows as `duplicate/umbrella`
- do not promote them to standalone `covered`

Reason:

1. `HLA2025-FI-005`, `HLA2025-MOD-001`, and `HLA2025-BND-003` already carry
   the real callback-model, configuration-result, credentials, and hosted
   connect semantics
2. current runtime proof already covers unsupported callback-model rejection,
   invalid plaintext password rejection, rejected-password rejection, and
   successful typed-credential connect on the direct runtime lane
3. current factory and transport evidence already cover default
   `HLAnoCredentials` composition and hosted FedPro request-shape mapping for
   the configuration and credentials overload family
4. no narrower standalone configuration-result or authorization-credentials
   claim was identified that would do more than restate the linked child
   connect rows

Current evidence reviewed for this decision included:

- `tests/test_rti1516_2025_python1516_2025_runtime.py`
- `tests/test_hla_factory_composition.py`
- `tests/transport/test_grpc_transport_2025.py`
- `packages/hla-rti-core/src/hla/rti/factory.py`
- `packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/federation_bootstrap_runtime.py`
- `requirements/2025/canonical_requirements.json`
- `../requirements/ieee-1516-2025/callback_binding_deltas.md`

Operational effect:

- the configuration and authorization slice remains a maintained umbrella
  boundary over the child connect rows
- the active decomposition queue should advance to the next unresolved
  candidate instead of relabeling connect-child proof as a second standalone
  implementation claim

The directed-interaction callback umbrella slice was also re-audited on
`2026-06-26` against the current owner doc, canonical requirement catalog,
direct runtime tests, hosted FedPro transport tests, and route-parity artifacts
for:

- `HLA2025-FI-CB-007`

Decision:

- keep this row as `duplicate/umbrella`
- do not promote it to standalone `covered`

Reason:

1. `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`, and `HLA2025-BND-003` already
   carry the real directed send/receive service semantics plus the bounded
   hosted-route claim
2. current direct runtime proof already covers directed callback delivery,
   subscriber-only routing, DDM overlap filtering, timestamped
   delivery/retraction, disconnect cleanup, and selective unsubscribe/unpublish
   behavior
3. current hosted FedPro transport tests and route-parity artifacts already
   cover the bounded route-side callback/request/response surface for the same
   directed-interaction family
4. no narrower standalone directed-interaction callback-parameterization claim
   was identified that would do more than restate the linked child FI and
   binding rows

Current evidence reviewed for this decision included:

- `tests/test_rti1516_2025_python1516_2025_runtime.py`
- `tests/transport/test_grpc_transport_2025.py`
- `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`
- `requirements/2025/backend_resolution.json`
- `../requirements/ieee-1516-2025/callback_binding_deltas.md`

Operational effect:

- the directed-interaction callback slice remains a maintained umbrella
  boundary over the child directed-interaction rows
- the active decomposition queue should advance to the next unresolved
  candidate instead of relabeling directed child-row proof as a second
  standalone implementation claim

The Java/C++ binding umbrella slice was also re-audited on `2026-06-26`
against the current owner doc, backend-resolution companion, standard-shim
artifact tests, route-parity matrix, shim-route evidence packets, and route
traces for:

- `HLA2025-BIND-JAVA-CPP-001`

Decision:

- keep this row as `duplicate/umbrella`
- do not promote it to standalone `covered`

Reason:

1. `HLA2025-BND-001`, `HLA2025-BND-002`, `HLA2025-FI-003`, and
   `HLA2025-FI-004` already carry the real binding-capability and wrapper
   surface semantics
2. current standard-shim artifact tests, shim-route evidence packets, and
   route traces already cover the bounded Java/C++ adapter/runtime-capability
   story over the main `python1516_2025` runtime lane
3. current route-parity matrix already keeps those routes explicit as bounded
   binding-capability surfaces rather than alternate RTI owners
4. no narrower standalone Java/C++ binding-capability claim was identified
   that would do more than restate the linked child binding and FI rows

Current evidence reviewed for this decision included:

- `tests/backends/test_standard_shim_artifacts.py`
- `tests/requirements/test_2025_route_parity_matrix.py`
- `docs/evidence/shim_routes/java-standard-2025.json`
- `docs/evidence/shim_routes/cpp-standard-2025.json`
- `docs/evidence/shim_routes/route_traces/`
- `requirements/2025/backend_resolution.json`
- `../requirements/ieee-1516-2025/callback_binding_deltas.md`

Operational effect:

- the Java/C++ binding slice remains a maintained umbrella boundary over the
  child binding rows
- the active decomposition queue should advance to the next unresolved
  candidate instead of relabeling bounded binding-capability proof as a second
  standalone implementation claim

## Recommended Execution Order

If leadership wants the strongest next-step decomposition without widening
scope recklessly, use this order:

1. `HLA2025-FI-CB-007`
2. `HLA2025-FI-CFG-001` and `HLA2025-FI-AUTH-001`
3. `HLA2025-BIND-JAVA-CPP-001`
4. `HLA2025-FR-001` through `HLA2025-FR-010`
5. revisit `HLA2025-FI-CB-002` through `HLA2025-FI-CB-004` only if the repo
   later introduces a genuinely narrower standalone callback-control claim
6. revisit `HLA2025-BIND-FEDPRO-001` only if the repo introduces a genuinely
   narrower protocol-capability claim that does more than restate the bounded
   hosted-route child proof

Reason:

- callback and route umbrellas already have the tightest executable child
  anchors
- framework rows are the broadest summaries and the least attractive direct
  `covered` candidates unless the repo wants new narrower standards-structure
  claims

## Work Rules

When changing any row in this worklist:

1. update the canonical requirement catalog first
2. update the owning umbrella doc or replace it with narrower child claims
3. record the narrowest owning shard from
   [`../verification/shard_registry.md`](../verification/shard_registry.md)
4. keep backend divergence in explicit backend-resolution surfaces
5. refresh affected finish-line, route-parity, and spreadsheet export artifacts
   when the direct Python proof changes their honest status

## Related Docs

- [PLN-004_python_rti_100_percent_compliance_plan.md](PLN-004_python_rti_100_percent_compliance_plan.md)
- [2025_python_rti_100_percent_worklist.md](2025_python_rti_100_percent_worklist.md)
- [2025_requirement_by_requirement_audit.md](2025_requirement_by_requirement_audit.md)
- [../requirements/ieee-1516-2025/framework_rules.md](../requirements/ieee-1516-2025/framework_rules.md)
- [../requirements/ieee-1516-2025/callback_binding_deltas.md](../requirements/ieee-1516-2025/callback_binding_deltas.md)
- [../verification/shard_registry.md](../verification/shard_registry.md)
- [../verification/view_registry.md](../verification/view_registry.md)
