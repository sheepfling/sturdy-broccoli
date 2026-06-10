# CERTI Spec Traceability

Real CERTI coverage in this workspace is intentionally backend-neutral at the
Python federate surface: federates call the same `RTIambassador` methods they
use against the pure Python RTI or the Java-profile shims. This note records
which IEEE 1516.1-2010 services are currently exercised through the real CERTI
backend path and where the evidence lives.

## Scope

- Runtime paths covered:
  - `certi`
  - `certi-jpype`
  - `certi-py4j`
- Baseline:
  - default evidence is against the active runtime selected by
    `discover_certi_runtime()`; in this workspace that is normally the
    repo-local vendored/patched CERTI build
  - upstream/original CERTI evidence must use the named `certi-upstream`
    selector with `HLA2010_CERTI_UPSTREAM_PREFIX` or
    `HLA2010_CERTI_ORIGINAL_PREFIX`
  - repo-local modified CERTI evidence must use the named `certi-patched`
    selector or the repo-local default
  - do not record upstream and patched results in the same matrix cell when
    they differ
- Evidence types:
  - real multi-federate runtime tests
  - backend callback-dispatch unit tests
  - Java-profile callback adapter unit tests

See [certi_runtime_limitations.md](certi_runtime_limitations.md)
for the current runtime shortfalls and patched-vs-upstream baseline policy.

Operational note:

- The named compare route is `./certi-easy smoke compare`.
- If loopback TCP bind/connect is not permitted for `127.0.0.1`, the route
  skips before collecting runtime evidence. That is an environment limitation,
  not a CERTI protocol result.
- In the current unsandboxed local run, the compare route showed:
  - `certi-upstream`: create/join succeeds, then the first `queryGALT` tears
    down the RTIA path; the negotiated-ownership compare probe also fails with
    an RTI internal error before the patched branch semantics can be observed;
    the release-request `deny` / `confirm` / `ifwanted` probes fail the same
    way before stable branch semantics are reached
  - `certi-patched`: the same scenario reaches later time-query and
    regulation/constraint assertions, `queryGALT` / `queryLITS` now return the
    current lookahead after regulation/constraint is enabled,
    `timeAdvanceRequestAvailable` now has a real fail-fast available-grant
    proof, `nextMessageRequest` now has a real fail-fast earliest-queued grant
    proof, `nextMessageRequestAvailable` now has the same real fail-fast
    earliest-queued grant proof after fixing the RTIA
    `nextEventRequestAvailable(...)` success-path guard, and
    `flushQueueRequest` now reaches a real grant in the promoted no-queued
    baseline; the queued-FQR compare probe now matches the promoted
    Python/spec ordering and earliest-timestamp grant behavior for the
    exercised attribute path;
    negotiated-ownership compare probe completes end to end; the release-request
    `deny` / `confirm` / `ifwanted` probes also complete, with release-request
    `confirm` now rejected unless negotiated divestiture is already active

## Federation Management

| Service | Clause | Real CERTI status | Evidence |
|---|---:|---|---|
| `registerFederationSynchronizationPoint` | 4.11 | implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `announceSynchronizationPoint` | 4.13 | callback implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py), [test_certi_java_profile_callbacks.py](tests/backends/test_certi_java_profile_callbacks.py) |
| `synchronizationPointAchieved` | 4.14 | implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `federationSynchronized` | 4.15 | callback implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py), [test_certi_java_profile_callbacks.py](tests/backends/test_certi_java_profile_callbacks.py) |

## Time Management

| Service | Clause | Real CERTI status | Evidence |
|---|---:|---|---|
| `enableTimeRegulation` | 8.2 | implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `timeRegulationEnabled` | 8.3 | callback implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `enableTimeConstrained` | 8.5 | implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `timeConstrainedEnabled` | 8.6 | callback implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `timeAdvanceRequest` | 8.8 | implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `timeAdvanceRequestAvailable` | 8.9 | patched CERTI is now exercised through a subprocess timeout harness and the real matrix proves a prompt equal-GALT available-grant on the Python-facing federate surface | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [certi_runtime_limitations.md](certi_runtime_limitations.md) |
| `nextMessageRequest` | 8.10 | patched CERTI is now exercised through the same fail-fast harness and the real matrix proves earliest-queued grants with timestamp-ordered delivery on the promoted timestamped object slice | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [certi_runtime_limitations.md](certi_runtime_limitations.md) |
| `nextMessageRequestAvailable` | 8.11 | patched CERTI is now exercised through the subprocess timeout harness and the real matrix proves earliest-queued grants with timestamp-ordered delivery on the promoted timestamped object slice after fixing the RTIA `nextEventRequestAvailable(...)` success-path guard | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [certi_runtime_limitations.md](certi_runtime_limitations.md) |
| `flushQueueRequest` | 8.12 | service is exposed by the adapter; patched CERTI now reaches a real grant in the promoted no-queued baseline and the queued real-runtime slice proves timestamp-ordered delivery with an earliest-queued grant for the exercised attribute path, while the Python-facing adapter normalizes integer-time callback typing for the promoted federate surface; pristine upstream does not stay alive long enough to finish queued-FQR setup | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [certi_runtime_limitations.md](certi_runtime_limitations.md) |
| `timeAdvanceGrant` | 8.13 | callback implemented and exercised for TAR/TARA/NMR/FQR paths on the promoted patched slices | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `queryGALT` | 8.16 | patched CERTI is exercised and returns valid infinity before regulation, then the current lookahead after the current two-federate regulation/constraint setup; pristine upstream tears down the RTIA path on the first `queryGALT` | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [certi_runtime_limitations.md](certi_runtime_limitations.md) |
| `queryLITS` | 8.18 | patched CERTI is exercised and returns valid infinity before regulation, then the current lookahead after the current two-federate regulation/constraint setup; pristine upstream does not reach a stable `queryLITS` observation because the baseline collapses earlier at `queryGALT` | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [certi_runtime_limitations.md](certi_runtime_limitations.md) |

## Ownership Management

| Service | Clause | Real CERTI status | Evidence |
|---|---:|---|---|
| `unconditionalAttributeOwnershipDivestiture` | 7.2 | implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `negotiatedAttributeOwnershipDivestiture` | 7.3 | patched CERTI completes the negotiated-ownership compare probe and delivers the assumption callback; pristine upstream does not reach a stable end-to-end negotiated flow | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [certi_negotiated_ownership_findings.md](certi_negotiated_ownership_findings.md) |
| `requestAttributeOwnershipAssumption` | 7.4 | patched CERTI callback path is now exercised end to end in the compare probe; pristine upstream does not reach a stable observation point | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [test_certi_backend_callbacks.py](../../../tests/backends/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](../../../tests/backends/test_certi_java_profile_callbacks.py), [certi_negotiated_ownership_findings.md](certi_negotiated_ownership_findings.md) |
| `requestDivestitureConfirmation` | 7.5 | callback wired and unit-covered | [test_certi_backend_callbacks.py](tests/backends/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](tests/backends/test_certi_java_profile_callbacks.py) |
| `confirmDivestiture` | 7.6 | direct runtime path exercised through the patched release-response mapping; negotiated confirm now enforces owner-side preconditions and propagates the confirm tag, while release-request `confirm` is rejected unless negotiated divestiture is active | [certi_negotiated_ownership_findings.md](certi_negotiated_ownership_findings.md), [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py) |
| `attributeOwnershipAcquisitionNotification` | 7.7 | callback implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py), [test_certi_java_profile_callbacks.py](tests/backends/test_certi_java_profile_callbacks.py) |
| `attributeOwnershipAcquisition` | 7.8 | implemented and exercised on the real owner release-request path | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [certi_negotiated_ownership_findings.md](certi_negotiated_ownership_findings.md) |
| `attributeOwnershipAcquisitionIfAvailable` | 7.9 | implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `attributeOwnershipUnavailable` | 7.10 | callback wired and unit-covered | [test_certi_backend_callbacks.py](tests/backends/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](tests/backends/test_certi_java_profile_callbacks.py) |
| `requestAttributeOwnershipRelease` | 7.11 | callback wired, unit-covered, and exercised on the real owner release-request path | [test_certi_backend_callbacks.py](../../../tests/backends/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](../../../tests/backends/test_certi_java_profile_callbacks.py), [certi_negotiated_ownership_findings.md](certi_negotiated_ownership_findings.md) |
| `attributeOwnershipReleaseDenied` | 7.12 | patched CERTI compare probe exercises the direct deny branch successfully; pristine upstream does not reach a stable direct-deny observation point | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [certi_negotiated_ownership_findings.md](certi_negotiated_ownership_findings.md) |
| `attributeOwnershipDivestitureIfWanted` | 7.13 | patched CERTI compare probe exercises the direct runtime transfer path successfully; it remains distinct from release-request `confirm`, but still uses the same underlying release-response transfer machinery once the owner grants transfer; pristine upstream does not reach this branch in the end-to-end compare slice | [test_certi_real_backend_matrix.py](../../../tests/vendors/test_certi_real_backend_matrix.py), [certi_negotiated_ownership_findings.md](certi_negotiated_ownership_findings.md) |
| `cancelNegotiatedAttributeOwnershipDivestiture` | 7.14 | service wired, not yet exercised end to end | [service_adapter.py](hla2010/backends/certi/service_adapter.py), [certi_smoke_helper.cpp](tools/certi_smoke_helper.cpp) |
| `cancelAttributeOwnershipAcquisition` | 7.15 | patched CERTI compare probe now exercises cancellation and the confirmation callback end to end; pristine upstream does not complete the same negotiated flow | [test_certi_backend_callbacks.py](tests/backends/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](tests/backends/test_certi_java_profile_callbacks.py), [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `confirmAttributeOwnershipAcquisitionCancellation` | 7.16 | callback wired and unit-covered | [test_certi_backend_callbacks.py](tests/backends/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](tests/backends/test_certi_java_profile_callbacks.py) |
| `queryAttributeOwnership` | 7.17 | implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |
| `informAttributeOwnership` | 7.18 | callback implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py), [test_certi_backend_callbacks.py](tests/backends/test_certi_backend_callbacks.py) |
| `attributeIsNotOwned` | 7.18 | callback implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py), [test_certi_backend_callbacks.py](tests/backends/test_certi_backend_callbacks.py) |
| `isAttributeOwnedByFederate` | 7.19 | implemented and exercised | [test_certi_real_backend_matrix.py](tests/vendors/test_certi_real_backend_matrix.py) |

## Parity Notes

- The pure Python RTI still provides the broadest local-process reference semantics.
- The real CERTI path now covers the same backend-neutral startup, exchange,
  synchronization, and core ownership acquisition/query flows.
- Negotiated ownership services are now stable enough in the patched local
  CERTI branch to distinguish the owner release-request paths for denial and
  transfer.
- The main remaining parity caveat is now narrower than before:
  `confirmDivestiture` and `attributeOwnershipDivestitureIfWanted` still share
  the same release-response implementation in the local CERTI 2010 branch once
  transfer is granted, but they are no longer equivalent at the 2010 surface
  because negotiated `confirm` now has stricter preconditions and
  release-request `confirm` is rejected.
- The source-level rationale for that classification is captured in
  [certi_negotiated_ownership_findings.md](certi_negotiated_ownership_findings.md).
- Some CERTI support-service lookups, notably peer `getFederateName()` and
  `getFederateHandle()`, are not implemented by the runtime used here. The real
  ownership tests therefore assert the portable spec-facing signals:
  ownership callbacks and `isAttributeOwnedByFederate(...)`.
- `certi-jpype` and `certi-py4j` reuse the same native CERTI transport, so the
  Java-profile parity story is primarily about adapter/callback conversion, not
  a separate vendor Java RTI implementation.
