# Binding and Hosted Route Boundaries

Source: IEEE 1516.1-2025 binding and hosted-route proof rows.

This note records the repo's current requirement-facing reading for the three
binding rows. It does not introduce a second Python RTI lane. The main 2025
Python RTI implementation lane is `hla-backend-python1516-2025`; the Java and C++
packages remain adapter/binding surfaces over that runtime, and the hosted
FedPro route remains a transport-facing runtime slice over the same lane.

## Owner Surface

- canonical owner doc:
  `docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md`
- primary shard: `unit-transport-local`
- widen to: `./tools/python verify-routes-2025` when binding or hosted claims
  need the broader route-parity bundle
- typical view tags: `2025-core`, `transport`, `closeout-reporting`

## Final Claim Rule

- these rows are bounded route or binding claims, not alternate RTI-owner claims
- count them as adaptation, route-parity, and runtime-capability evidence over
  `hla-backend-python1516-2025`
- do not read `covered` here as “full Java conformance,” “full C++ conformance,”
  or “second hosted RTI implementation lane”
- only widen these rows beyond bounded status when exhaustive behavior-equivalence
  evidence exists for the exact broader claim

Default final stance:

- this bucket is already in its intended final repo-owned state as a bounded
  adaptation and hosted-route owner surface
- no additional proof is required to keep these rows out of alternate-RTI or
  full cross-binding conformance claims
- future work is optional and should happen only if the repo deliberately opens
  a broader Java, C++, or hosted behavior-equivalence program with its own
  bounded claim and tests

Use `Evidence anchors` and `Bounded claim reading` here as owner-facing proof
vocabulary. They describe bounded route or binding evidence scope, not
canonical requirement disposition.

| ID | Summary | Evidence anchors | Bounded claim reading |
| --- | --- | --- | --- |
| HLA2025-BND-001 | Java binding surface | `tests/requirements/test_2025_tail_backlog_evidence.py`, `tests/requirements/test_2025_route_parity_matrix.py`, `tests/backends/test_standard_shim_artifacts.py`, `requirements/2025/STRICT_DOC_INVENTORY.json`, `requirements/2025/SOURCE_TRACE.md`, `docs/evidence/shim_routes/java-standard-2025.json` | Closed as bounded Java binding traceability: it proves source-surface accounting and scenario/runtime-capability parity over `hla-backend-python1516-2025`, not an independent Java RTI or full cross-binding behavior conformance pass. |
| HLA2025-BND-002 | C++ binding surface | `tests/requirements/test_2025_tail_backlog_evidence.py`, `tests/requirements/test_2025_route_parity_matrix.py`, `tests/backends/test_standard_shim_artifacts.py`, `requirements/2025/SOURCE_TRACE.md`, `docs/evidence/shim_routes/cpp-standard-2025.json`, `docs/evidence/cpp-intake/cpp-standard-2025-2025-pybind.json` | Closed as bounded C++ binding traceability: it proves header/API source trace plus scenario/runtime-capability parity over `hla-backend-python1516-2025`, not an independent C++ RTI or full cross-binding behavior conformance pass. |
| HLA2025-BND-003 | Hosted FedPro/protobuf surface | `tests/requirements/test_2025_tail_backlog_evidence.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`, `packages/hla-transport-grpc/proto/rti1516_2025/fedpro/HLA2025RTITransport.proto`, `packages/hla-transport-grpc/proto/rti1516_2025/fedpro/RTIambassador_2025.proto`, `packages/hla-transport-grpc/proto/rti1516_2025/fedpro/FederateAmbassador_2025.proto` | Closed as bounded hosted-route traceability: it proves typed request/response/callback transport parity and hosted replay over `hla-backend-python1516-2025`, not a second RTI implementation lane and not a full RTI semantics or exhaustive cross-binding conformance pass. |

## Boundary Notes

- `hla-backend-python1516-2025` is the only main 2025 Python RTI implementation lane
  behind these rows.
- `hla-backend-shim` remains a compatibility wrapper and is not a runtime owner
  for the binding rows above.
- Java bridge packages and `hla-backend-cpp-shim` remain wrapper/binding
  surfaces over the main Python 2025 runtime rather than alternate 2025 RTIs.
- Pitch's vendor-facing Java surface for this family is currently branded as
  proto HLA 4 / `202X` in jar and namespace naming. Treat that as vendor
  packaging terminology, not as automatic proof that the entire 2025 repo claim
  or every grouped FI bucket has Pitch-parity closure.
- When the repo needs the concrete bounded Pitch 202X comparison packet for this
  family, use:
  `artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_summary.json`,
  `artifacts/pitch_202x_micro_certification/pitch_202x_micro_certification_report.md`,
  and `packages/hla-vendor-pitch/docs/pitch_vs_python_baseline.md`.
- Hosted FedPro is a bounded transport/runtime slice over
  `hla-backend-python1516-2025`; its remaining proof burden is transport-seam and
  cross-binding evidence, not evidence that the core 2025 Python RTI lane is
  owned somewhere else.
- The repo should not promote these rows to full binding or hosted conformance
  claims unless it gains exhaustive behavior-equivalence evidence beyond the
  current route-parity and runtime-capability traces.

## Exit Condition

Treat this bucket as closed for current closeout purposes when all of these are
true:

1. all three binding rows remain anchored to this owner doc and the linked
   route-parity and FI-binding artifacts
2. the final claim language keeps them explicit as bounded adaptation or
   hosted-route rows rather than alternate RTI owners
3. any future widening must happen through canonical requirement rows or the
   backend-resolution companion, never through grouped worklists, audit notes,
   or other downstream reporting views

Only reopen this bucket if the repo intentionally starts a broader
behavior-equivalence program for one or more of these rows.
