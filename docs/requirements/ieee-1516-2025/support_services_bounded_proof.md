# Support Services Bounded Proof

Source: IEEE 1516.1-2025 Federate Interface support services rows.

This note records the repo's current support-services claim as a bounded,
requirement-facing proof statement. The repo has per-service runtime
traceability across the Python 2025 lanes and complete actionable negative-path
coverage inside those Python routes. It does not claim exhaustive cross-binding
behavior conformance or a full support-service conformance pass over every
binding and hosted seam.

## Current Bounded Claim

- The primary `hla-backend-python1516-2025` lane has explicit executable support
  service proof across the tracked support-service rows.
- The hosted FedPro route replays those support-service families as a bounded
  transport seam over the same runtime owner.
- The REST-hosted Python route is not yet promoted to these support-service
  proof families; current checked-in REST evidence in this closeout program
  covers the hosted transport seam, 2025 execution-membership control, and
  selected lifecycle/control-flow witnesses rather than family-by-family 2025
  support-service replay.
- Support-service proof is decomposed into named proof families instead of
  resting only on one large service ledger.
- The claim is still bounded: Java and C++ routes remain capability-oriented,
  and hosted FedPro remains a bounded runtime slice rather than a full
  support-service conformance route.

## Primary Evidence Anchors

- `requirements/2025/canonical_requirements.json`
- `requirements/2025/backend_resolution.json`
- `tests/test_rti1516_2025_python1516_2025_runtime.py`
- `tests/scenarios/test_support_services_backend_matrix.py`
- `tests/backends/test_python_backend_support_services.py`
- `tests/transport/test_grpc_transport_2025.py`
- `packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_services_runtime.py`

## Owner Row Scope

- The canonical support-service owner rows carried by this note are the true
  Clause 10 support-service rows:
  `HLA2025-FI-SVC-138` through `HLA2025-FI-SVC-156`,
  `HLA2025-FI-SVC-158`, `HLA2025-FI-SVC-162` through
  `HLA2025-FI-SVC-196`.
- A few proof families intentionally rely on linked helper flows from adjacent
  owners, but those helpers do not become canonical support-service owner rows
  just because they appear in this bounded note.
- In particular, `name-reservation-and-release-flows` is backed by linked
  object-management rows rather than Clause 10 owner rows, and the
  dimension/range helper edges that depend on
  `HLA2025-FI-SVC-157`, `HLA2025-FI-SVC-159`, `HLA2025-FI-SVC-160`,
  `HLA2025-FI-SVC-161`, or `HLA2025-FI-SVC-164` stay owned by the DDM note.
- Read this note as the bounded support-service proof owner for the actual
  support rows plus explicit helper links, not as a license to relabel OM or
  DDM rows as support-service closure.

## Proof Families

| Family | Focus | Direct-backed | FedPro-hosted-backed | REST-hosted-backed |
| --- | --- | ---: | ---: | ---: |
| `name-reservation-and-release-flows` | Single and multi-name reservation success/failure callbacks, release flows, handoff behavior, and reservation-state preconditions. | Yes | Yes | No |
| `identity-catalog-and-handle-normalization-lookups` | Federate, object, interaction, parameter, and service-group lookup/normalization flows across joined runtime state and loaded catalog metadata. | Yes | Yes | No |
| `transport-order-update-dimension-and-range-lookups` | Transportation, order type, update-rate, dimension, and range-bound lookups plus requester-only transport query callback routing. | Yes | Yes | No |
| `switch-inquiry-and-control-model` | 2025 set/get support switch model for advisory, reporting, and runtime policy state, including automatic resign. | Yes | Yes | No |
| `factory-decode-and-hosted-support-seam` | Support handle factories, decode helpers, hosted direct support-route execution, callback-backlog control, and transport-preserved support surfaces. | Yes | Yes | No |

## Reading of the Evidence

- The maintained focused rerun view for support-service and callback-control
  behavior is `./tools/test-focus run python-2025-mom-callbacks`.
- The direct aggregate proof lane is `./tools/python verify-main-2025`, and
  the paired hosted replay lane is `./tools/python verify-routes-2025`.
- The direct Python runtime tests prove that support-service behavior exists on
  the main `python1516_2025` implementation lane without routing through the wrapper
  lane.
- The hosted FedPro tests prove that the same support-service families survive
  the typed transport seam, including callback-backlog and reconnect-sensitive
  cases.
- The repo does not currently maintain matching REST-hosted family replay for
  these support-service proof buckets, so the route split above stays explicit
  instead of collapsing all hosted transport variants into one `Yes`.
- The proof is strong enough for per-service traceability and bounded working
  surface claims, but not for exhaustive full conformance wording across every
  binding lane.

## Explicit Non-Claim

- This note does not promote hosted FedPro to a full support-service
  conformance route.
- This note does not promote the REST-hosted Python route to the named
  support-service proof families above.
- This note does not promote Java or C++ capability traces to exhaustive
  behavior-conformance proof.
