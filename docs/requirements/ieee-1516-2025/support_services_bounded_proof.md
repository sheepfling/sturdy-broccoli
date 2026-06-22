# Support Services Bounded Proof

Source: IEEE 1516.1-2025 Federate Interface support services rows.

This note records the repo's current support-services claim as a bounded,
requirement-facing proof statement. The repo has per-service runtime
traceability across the Python 2025 lanes and complete actionable negative-path
coverage inside those Python routes. It does not claim exhaustive cross-binding
behavior conformance or a full support-service conformance pass over every
binding and hosted seam.

## Current Bounded Claim

- The primary `hla-backend-python2025` lane has explicit executable support
  service proof across the tracked support-service rows.
- The hosted FedPro route replays those support-service families as a bounded
  transport seam over the same runtime owner.
- Support-service proof is decomposed into named proof families instead of
  resting only on one large service ledger.
- The claim is still bounded: Java and C++ routes remain capability-oriented,
  and hosted FedPro remains a bounded runtime slice rather than a full
  support-service conformance route.

## Primary Evidence Anchors

- `tests/test_rti1516_2025_python2025_runtime.py`
- `tests/scenarios/test_support_services_backend_matrix.py`
- `tests/backends/test_python_backend_support_services.py`
- `tests/transport/test_grpc_transport_2025.py`
- `packages/hla-backend-python2025/src/hla/backends/python2025/support_services_runtime.py`
- `docs/plans/spec2025_finish_line.md`

## Proof Families

| Family | Focus | Direct-backed | Hosted-backed |
| --- | --- | ---: | ---: |
| `name-reservation-and-release-flows` | Single and multi-name reservation success/failure callbacks, release flows, handoff behavior, and reservation-state preconditions. | Yes | Yes |
| `identity-catalog-and-handle-normalization-lookups` | Federate, object, interaction, parameter, and service-group lookup/normalization flows across joined runtime state and loaded catalog metadata. | Yes | Yes |
| `transport-order-update-dimension-and-range-lookups` | Transportation, order type, update-rate, dimension, and range-bound lookups plus requester-only transport query callback routing. | Yes | Yes |
| `switch-inquiry-and-control-model` | 2025 set/get support switch model for advisory, reporting, and runtime policy state, including automatic resign. | Yes | Yes |
| `factory-decode-and-hosted-support-seam` | Support handle factories, decode helpers, hosted direct support-route execution, callback-backlog control, and transport-preserved support surfaces. | Yes | Yes |

## Reading of the Evidence

- The direct Python runtime tests prove that support-service behavior exists on
  the main `python2025` implementation lane without routing through the wrapper
  lane.
- The hosted FedPro tests prove that the same support-service families survive
  the typed transport seam, including callback-backlog and reconnect-sensitive
  cases.
- The proof is strong enough for per-service traceability and bounded working
  surface claims, but not for exhaustive full conformance wording across every
  binding lane.

## Explicit Non-Claim

- This note does not promote hosted FedPro to a full support-service
  conformance route.
- This note does not promote Java or C++ capability traces to exhaustive
  behavior-conformance proof.
