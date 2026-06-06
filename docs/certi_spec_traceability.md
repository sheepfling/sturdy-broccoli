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
- Evidence types:
  - real multi-federate runtime tests
  - backend callback-dispatch unit tests
  - Java-profile callback adapter unit tests

## Federation Management

| Service | Clause | Real CERTI status | Evidence |
|---|---:|---|---|
| `registerFederationSynchronizationPoint` | 4.11 | implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py) |
| `announceSynchronizationPoint` | 4.13 | callback implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_java_profile_callbacks.py) |
| `synchronizationPointAchieved` | 4.14 | implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py) |
| `federationSynchronized` | 4.15 | callback implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_java_profile_callbacks.py) |

## Ownership Management

| Service | Clause | Real CERTI status | Evidence |
|---|---:|---|---|
| `unconditionalAttributeOwnershipDivestiture` | 7.2 | implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py) |
| `negotiatedAttributeOwnershipDivestiture` | 7.3 | service wired; direct runtime assumption fanout is now stable after the broadcast fix | [certi_negotiated_ownership_findings.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/certi_negotiated_ownership_findings.md) |
| `requestAttributeOwnershipAssumption` | 7.4 | callback wired; assumption branch is now runtime-stable, but separate from the owner release-request branch | [test_certi_backend_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_java_profile_callbacks.py), [certi_negotiated_ownership_findings.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/certi_negotiated_ownership_findings.md) |
| `requestDivestitureConfirmation` | 7.5 | callback wired and unit-covered | [test_certi_backend_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_java_profile_callbacks.py) |
| `confirmDivestiture` | 7.6 | direct runtime path exercised through the patched release-response mapping; not distinct from `attributeOwnershipDivestitureIfWanted` in the local 2010 branch | [certi_negotiated_ownership_findings.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/certi_negotiated_ownership_findings.md) |
| `attributeOwnershipAcquisitionNotification` | 7.7 | callback implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_java_profile_callbacks.py) |
| `attributeOwnershipAcquisition` | 7.8 | implemented and exercised on the real owner release-request path | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py), [certi_negotiated_ownership_findings.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/certi_negotiated_ownership_findings.md) |
| `attributeOwnershipAcquisitionIfAvailable` | 7.9 | implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py) |
| `attributeOwnershipUnavailable` | 7.10 | callback wired and unit-covered | [test_certi_backend_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_java_profile_callbacks.py) |
| `requestAttributeOwnershipRelease` | 7.11 | callback wired, unit-covered, and exercised on the real owner release-request path | [test_certi_backend_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_java_profile_callbacks.py), [certi_negotiated_ownership_findings.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/certi_negotiated_ownership_findings.md) |
| `attributeOwnershipReleaseDenied` | 7.12 | direct deny path exercised successfully in the patched local 2010 branch | [certi_negotiated_ownership_findings.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/certi_negotiated_ownership_findings.md) |
| `attributeOwnershipDivestitureIfWanted` | 7.13 | direct runtime path exercised successfully, but currently shares the same release-response implementation as `confirmDivestiture` | [certi_negotiated_ownership_findings.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/certi_negotiated_ownership_findings.md) |
| `cancelNegotiatedAttributeOwnershipDivestiture` | 7.14 | service wired, not yet exercised end to end | [certi_backend.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/hla2010/backends/certi_backend.py), [certi_smoke_helper.cpp](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tools/certi_smoke_helper.cpp) |
| `cancelAttributeOwnershipAcquisition` | 7.15 | service wired; cancellation callback path unit-covered, but real runtime probe remains unstable | [test_certi_backend_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_java_profile_callbacks.py), [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py) |
| `confirmAttributeOwnershipAcquisitionCancellation` | 7.16 | callback wired and unit-covered | [test_certi_backend_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_backend_callbacks.py), [test_certi_java_profile_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_java_profile_callbacks.py) |
| `queryAttributeOwnership` | 7.17 | implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py) |
| `informAttributeOwnership` | 7.18 | callback implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py), [test_certi_backend_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_backend_callbacks.py) |
| `attributeIsNotOwned` | 7.18 | callback implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py), [test_certi_backend_callbacks.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_backend_callbacks.py) |
| `isAttributeOwnedByFederate` | 7.19 | implemented and exercised | [test_certi_real_backend_matrix.py](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/tests/test_certi_real_backend_matrix.py) |

## Parity Notes

- The pure Python RTI still provides the broadest local-process reference semantics.
- The real CERTI path now covers the same backend-neutral startup, exchange,
  synchronization, and core ownership acquisition/query flows.
- Negotiated ownership services are now stable enough in the patched local
  CERTI branch to distinguish the owner release-request paths for denial and
  transfer.
- The main remaining parity caveat is semantic, not transport-level:
  `confirmDivestiture` and `attributeOwnershipDivestitureIfWanted` currently
  share the same release-response implementation in the local CERTI 2010
  branch.
- The source-level rationale for that classification is captured in
  [certi_negotiated_ownership_findings.md](/Users/rick/Library/Mobile%20Documents/com~apple~CloudDocs/GIT/hla-2010/docs/certi_negotiated_ownership_findings.md).
- Some CERTI support-service lookups, notably peer `getFederateName()` and
  `getFederateHandle()`, are not implemented by the runtime used here. The real
  ownership tests therefore assert the portable spec-facing signals:
  ownership callbacks and `isAttributeOwnedByFederate(...)`.
- `certi-jpype` and `certi-py4j` reuse the same native CERTI transport, so the
  Java-profile parity story is primarily about adapter/callback conversion, not
  a separate vendor Java RTI implementation.
