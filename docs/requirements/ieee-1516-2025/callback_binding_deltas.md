# Callback, Configuration, and Binding Delta Requirements

Source: IEEE 1516.1-2025 callback/configuration/binding delta backlog rows.

These rows remain `duplicate/umbrella` in the canonical 2025 requirement
catalog. They are
not standalone runtime claims. Each row closes only through the linked child
FI/binding rows plus executable evidence on the main `hla-backend-python1516-2025`
runtime lane and the bounded route artifacts that sit above it.

## Owner Surface

- canonical owner doc: `docs/requirements/ieee-1516-2025/callback_binding_deltas.md`
- primary shard: `unit-shim-tooling`
- widen to: `./tools/python verify-routes-2025` only when an umbrella row is
  being converted into a route-backed proof claim
- typical view tags: `2025-core`, `java-shim`, `cpp-shim`, `transport`

## Final Claim Rule

- these rows stay `duplicate/umbrella`, not standalone runtime proof rows
- the real requirement closure lives in the linked child FI, callback-control,
  auth, configuration, binding, and route rows
- do not treat wrapper or route evidence here as proof of an alternate RTI owner
- if a future change needs a standalone callback or binding claim, split it
  into a narrower executable child row instead of widening this umbrella layer

Default final stance:

- this bucket is already in its intended final repo-owned state as a
  non-standalone delta or normalization surface
- no additional runtime proof is required to keep these rows out of standalone
  `covered` status
- future work is optional and should happen only if the repo deliberately
  introduces narrower executable child claims that justify changing the
  umbrella structure

Use `Evidence anchors` and `Bounded claim reading` here as owner-facing proof
vocabulary. They describe umbrella-row evidence scope, not canonical child-row
disposition.

| ID | Summary | Linked child rows | Evidence anchors | Bounded claim reading |
| --- | --- | --- | --- | --- |
| HLA2025-FI-CB-001 | Callback model selection | `HLA2025-FI-005`, `HLA2025-MOD-001` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/test_hla_factory_composition.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through connect/auth/configuration coverage that proves IMMEDIATE and EVOKED model selection on the direct `python1516_2025` lane and the hosted FedPro route. |
| HLA2025-FI-CB-002 | Evoke Callback | `HLA2025-FI-SVC-193` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/backends/test_python_backend_support_services.py`, `docs/evidence/shim_routes/java-standard-2025.json` | Closed through explicit EVOKED callback dispatch behavior on the runtime lane plus bounded route-surface evidence for Java/C++ wrapper methods. |
| HLA2025-FI-CB-003 | Evoke Multiple Callbacks | `HLA2025-FI-SVC-194` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/backends/test_python_backend_support_services.py`, `docs/evidence/shim_routes/java-standard-2025.json` | Closed through queue-drain timing behavior on the runtime lane plus route-surface evidence for wrapper parity. |
| HLA2025-FI-CB-004 | Enable/Disable Callbacks | `HLA2025-FI-SVC-195`, `HLA2025-FI-SVC-196` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/backends/test_python_backend_support_services.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through callback-control service behavior on the runtime lane and explicit hosted FedPro transport calls for enable/disable semantics. |
| HLA2025-FI-CB-005 | Federate Resigned callback | `HLA2025-FI-SVC-012` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through forced/automatic resign coverage and the corresponding federate callback/reporting behavior on the direct `python1516_2025` lane plus hosted FedPro replay. |
| HLA2025-FI-CB-006 | Federation execution member reporting | `HLA2025-FI-SVC-008`, `HLA2025-FI-SVC-009` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through explicit `reportFederationExecutions` and `reportFederationExecutionMembers` callback proof on the runtime lane and hosted FedPro replay. |
| HLA2025-FI-CB-007 | Directed interaction callback parameterization | `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`, `HLA2025-BND-003` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py` | Closed through distinct directed send/receive runtime semantics and bounded FedPro route parity, not by reusing ordinary interaction proof alone. |
| HLA2025-FI-CB-008 | Flush Queue Grant callback | `HLA2025-FI-SVC-112` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through explicit `flushQueueGrant` callback behavior on the runtime lane and hosted transport callback decoding, separate from ordinary timeAdvanceGrant proof. |
| HLA2025-FI-CFG-001 | Configuration and additional settings result | `HLA2025-FI-005`, `HLA2025-MOD-001`, `HLA2025-BND-003` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/test_hla_factory_composition.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through connect-time configuration/result semantics on the direct lane plus hosted/local-settings route coverage. |
| HLA2025-FI-AUTH-001 | Authorization credentials | `HLA2025-FI-005`, `HLA2025-MOD-001`, `HLA2025-BND-003` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/test_hla_factory_composition.py`, `packages/hla-rti-core/src/hla/rti/factory.py` | Closed through explicit `HLAnoCredentials` and `HLAplainTextPassword` authorization validation on the main `python1516_2025` lane. |
| HLA2025-BIND-FEDPRO-001 | FedPro protocol split | `HLA2025-BND-003`, `HLA2025-FI-004` | `tests/transport/test_grpc_transport_2025.py`, `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`, `packages/hla-transport-grpc/proto/rti1516_2025/fedpro` | Closed as a bounded wire-surface row: it proves hosted FedPro request/response/callback parity over `hla-backend-python1516-2025`, not an independent RTI implementation lane. |
| HLA2025-BIND-JAVA-CPP-001 | Java/C++ binding split | `HLA2025-BND-001`, `HLA2025-BND-002`, `HLA2025-FI-003`, `HLA2025-FI-004` | `tests/requirements/test_2025_route_parity_matrix.py`, `tests/backends/test_standard_shim_artifacts.py`, `docs/evidence/shim_routes/route_traces` | Closed as a bounded binding-capability row: it proves adapter/runtime-capability and route-trace parity over the `python1516_2025` runtime, not full independent Java/C++ RTI semantics. |

## Closure Notes

- `HLA2025-FI-CB-001` through `HLA2025-BIND-JAVA-CPP-001` remain umbrella
  rows because their normative force is already carried by the linked child FI,
  callback-control, time, auth, configuration, and binding rows above.
- The repo should not promote these rows to standalone `covered` runtime claims
  unless they gain narrower executable proof than the child rows already carry.
- The primary runtime owner behind the executable anchors above is
  `hla-backend-python1516-2025`.
- `hla-backend-shim`, `hla-backend-cpp-shim`, and the Java bridge packages are
  wrapper/binding surfaces over that runtime lane; they are not alternate 2025
  Python RTI implementations.
- Where Pitch appears in this family, the vendor may label the surface as proto
  HLA 4 / `202X` in jar names or namespaces. Keep that naming explicit in
  backend-resolution notes, but do not use the vendor label by itself as a
  substitute for row-level 2025 closure or parity evidence.
- The concrete bounded Pitch 202X comparison packet for these rows currently
  lives in `artifacts/pitch_202x_micro_certification/`, with operator-facing
  interpretation in `packages/hla-vendor-pitch/docs/pitch_vs_python_baseline.md`.

## Latest Investigated Decision

The configuration and authorization umbrella slice was re-audited on
`2026-06-26` against the current owner doc, canonical requirement rows, connect
runtime tests, factory composition tests, hosted FedPro request mapping, and
factory/auth implementation anchors for:

- `HLA2025-FI-CFG-001`
- `HLA2025-FI-AUTH-001`

Decision:

- keep these rows as `duplicate/umbrella`
- do not promote them to standalone `covered`

Reason:

1. `HLA2025-FI-005`, `HLA2025-MOD-001`, and `HLA2025-BND-003` already carry
   the real connect-time callback-model, configuration-result, credentials,
   and hosted-request semantics
2. the current runtime lane already proves unsupported callback-model
   rejection, invalid plaintext password rejection, rejected-password
   rejection, and successful typed-credential connect on
   `hla-backend-python1516-2025`
3. the current factory and transport evidence already prove default
   `HLAnoCredentials` composition and hosted FedPro request-shape coverage for
   the configuration and credentials overload family
4. no narrower standalone configuration-result or authorization-credentials
   claim was identified that would do more than restate the linked child connect
   rows

Current evidence reviewed for this decision included:

- `tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_is_first_green_runtime_path`
- `tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_validates_callback_model_and_credentials_at_connect`
- `tests/test_hla_factory_composition.py`
- `tests/transport/test_grpc_transport_2025.py`
- `packages/hla-rti-core/src/hla/rti/factory.py`
- `packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/federation_bootstrap_runtime.py`
- `requirements/2025/canonical_requirements.json`

Operational effect:

- the configuration and authorization slice remains a maintained
  callback/configuration/binding umbrella surface
- the active closeout queue should advance to the next real tightening bucket
  instead of relabeling connect-child proof as a second standalone umbrella-row
  implementation claim

The callback-control umbrella slice was also re-audited on `2026-06-26`
against the current owner doc, canonical requirement rows, direct runtime tests,
support-services backend tests, Java route evidence, and hosted FedPro
transport coverage for:

- `HLA2025-FI-CB-002`
- `HLA2025-FI-CB-003`
- `HLA2025-FI-CB-004`

Decision:

- keep these rows as `duplicate/umbrella`
- do not promote them to standalone `covered`

Reason:

1. `HLA2025-FI-SVC-193`, `HLA2025-FI-SVC-194`, `HLA2025-FI-SVC-195`, and
   `HLA2025-FI-SVC-196` already carry the real EVOKED callback dispatch,
   queue-drain timing, and enable/disable callback-control semantics
2. the current direct runtime lane already proves single-dispatch,
   bounded-multi-dispatch, disabled-callback suppression, and callback
   exception handling on `hla-backend-python1516-2025`
3. the current support-services backend tests, Java route evidence, and hosted
   FedPro transport checks already prove the bounded route-surface replay for
   the same callback-control family
4. no narrower standalone callback-control claim was identified that would do
   more than restate the linked child FI rows

Current evidence reviewed for this decision included:

- `tests/test_rti1516_2025_python1516_2025_runtime.py`
- `tests/backends/test_python_backend_support_services.py`
- `tests/transport/test_grpc_transport_2025.py`
- `docs/evidence/shim_routes/java-standard-2025.json`
- `requirements/2025/canonical_requirements.json`

Operational effect:

- the callback-control slice remains a maintained
  callback/configuration/binding umbrella surface
- the active closeout queue should advance to the next real tightening bucket
  instead of relabeling callback-control child proof as a second standalone
  umbrella-row implementation claim

The directed-interaction callback umbrella slice was also re-audited on
`2026-06-26` against the current owner doc, canonical requirement rows, direct
runtime tests, hosted FedPro transport tests, and route-parity artifacts for:

- `HLA2025-FI-CB-007`

Decision:

- keep this row as `duplicate/umbrella`
- do not promote it to standalone `covered`

Reason:

1. `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064`, and `HLA2025-BND-003` already
   carry the real directed send/receive service semantics and the bounded
   hosted-route claim
2. the current direct runtime lane already proves directed-interaction
   callback delivery, subscriber-only routing, DDM overlap filtering,
   timestamped delivery/retraction, disconnect cleanup, and selective
   unsubscribe/unpublish behavior
3. the current hosted FedPro tests and route-parity artifacts already prove
   the bounded route-side callback/request/response surface for the same
   directed-interaction family
4. no narrower standalone directed-interaction callback-parameterization claim
   was identified that would do more than restate the linked child FI and
   binding rows

Current evidence reviewed for this decision included:

- `tests/test_rti1516_2025_python1516_2025_runtime.py`
- `tests/transport/test_grpc_transport_2025.py`
- `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`
- `requirements/2025/canonical_requirements.json`

Operational effect:

- the directed-interaction callback slice remains a maintained
  callback/configuration/binding umbrella surface
- the active closeout queue should advance to the next real tightening bucket
  instead of relabeling directed child-row proof as a second standalone
  umbrella-row implementation claim

The FedPro protocol umbrella slice was also re-audited on `2026-06-26`
against the current owner doc, canonical requirement rows, hosted-route transport
tests, route-parity artifacts, and the tracked FedPro protobuf surface for:

- `HLA2025-BIND-FEDPRO-001`

Decision:

- keep this row as `duplicate/umbrella`
- do not promote it to standalone `covered`

Reason:

1. `HLA2025-BND-003` and `HLA2025-FI-004` already carry the real hosted-route
   binding and bounded protocol-surface semantics
2. the current hosted FedPro transport tests already prove request/response,
   callback decoding, and error-mapping behavior over
   `hla-backend-python1516-2025`
3. the current route-parity artifacts and tracked protobuf definitions already
   keep the wire-surface claim explicit without implying a second RTI owner
4. no narrower standalone FedPro protocol-capability claim was identified that
   would do more than restate the linked child binding and route rows

Current evidence reviewed for this decision included:

- `tests/transport/test_grpc_transport_2025.py`
- `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`
- `packages/hla-transport-grpc/proto/rti1516_2025/fedpro`
- `requirements/2025/canonical_requirements.json`

Operational effect:

- the FedPro protocol slice remains a maintained
  callback/configuration/binding umbrella surface
- the active closeout queue should advance to the next real tightening bucket
  instead of relabeling bounded hosted-route child proof as a second
  standalone umbrella-row implementation claim

The Java/C++ binding umbrella slice was also re-audited on `2026-06-26`
against the current owner doc, canonical requirement rows, standard-shim artifact
tests, route-parity matrix, shim-route evidence packets, and route traces for:

- `HLA2025-BIND-JAVA-CPP-001`

Decision:

- keep this row as `duplicate/umbrella`
- do not promote it to standalone `covered`

Reason:

1. `HLA2025-BND-001`, `HLA2025-BND-002`, `HLA2025-FI-003`, and
   `HLA2025-FI-004` already carry the real Java/C++ binding-capability and
   wrapper-surface semantics
2. the current standard-shim artifact tests, shim-route evidence packets, and
   route traces already prove the bounded Java/C++ adapter/runtime-capability
   story over the main `python1516_2025` runtime lane
3. the current route-parity matrix already keeps those routes explicit as
   bounded binding-capability surfaces rather than alternate RTI owners
4. no narrower standalone Java/C++ binding-capability claim was identified
   that would do more than restate the linked child binding and FI rows

Current evidence reviewed for this decision included:

- `tests/backends/test_standard_shim_artifacts.py`
- `tests/requirements/test_2025_route_parity_matrix.py`
- `docs/evidence/shim_routes/java-standard-2025.json`
- `docs/evidence/shim_routes/cpp-standard-2025.json`
- `docs/evidence/shim_routes/route_traces/`
- `requirements/2025/canonical_requirements.json`

Operational effect:

- the Java/C++ binding slice remains a maintained
  callback/configuration/binding umbrella surface
- the active closeout queue should advance to the next real tightening bucket
  instead of relabeling bounded binding-capability proof as a second
  standalone umbrella-row implementation claim

## Exit Condition

Treat this bucket as closed for current closeout purposes when all of these are
true:

1. all callback/configuration/binding umbrella rows remain anchored to this
   owner doc and the canonical row-level requirement catalog
2. the final claim language keeps them explicit as parent or normalization rows
   rather than accidental standalone runtime proof
3. any future widening must happen through canonical requirement rows or the
   backend-resolution companion, never through grouped worklists, audit notes,
   or other downstream reporting views

Only reopen this bucket if the repo intentionally introduces narrower child
claims or changes the callback or binding ownership map.
