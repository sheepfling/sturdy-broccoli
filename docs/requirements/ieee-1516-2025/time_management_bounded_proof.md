# Time Management Bounded Proof

Source: IEEE 1516.1-2025 time-management service rows and the repo's current
time-window proof families.

This note records the repo's current requirement-facing time-management claim
as a bounded proof statement for the main `hla-backend-python1516-2025` runtime
lane. It covers service-by-service runtime traceability for the 25 time
management service rows together with the direct-lane and hosted FedPro replay
proof families for lookahead, GALT/LITS, timestamp-order delivery, retraction,
and restore rollback. It does not claim final clause-by-clause 2025 conformance or
exhaustive cross-binding equivalence.

## Service Families

Use `Evidence anchors` and `Bounded claim reading` here as owner-facing proof
vocabulary. They describe bounded evidence scope, not canonical requirement
disposition.

| Family | Rows | Evidence anchors | Bounded claim reading |
| --- | --- | --- | --- |
| Time mode enable/disable | `HLA2025-FI-SVC-101`, `HLA2025-FI-SVC-102`, `HLA2025-FI-SVC-103`, `HLA2025-FI-SVC-104`, `HLA2025-FI-SVC-105`, `HLA2025-FI-SVC-106` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py` | Closed as bounded runtime proof for regulation/constrained enablement and disablement, selected logical-time factory handling, and the corresponding callbacks on the direct `python1516_2025` lane plus hosted FedPro replay. |
| Advance request modes | `HLA2025-FI-SVC-107`, `HLA2025-FI-SVC-108`, `HLA2025-FI-SVC-109`, `HLA2025-FI-SVC-110`, `HLA2025-FI-SVC-111` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py` | Closed as bounded runtime proof for time-advance request state, next-message request stepping, flush-queue request behavior, queued timestamp-order delivery, and hosted FedPro replay of the same request surfaces. |
| Grants and async delivery control | `HLA2025-FI-SVC-112`, `HLA2025-FI-SVC-113`, `HLA2025-FI-SVC-114`, `HLA2025-FI-SVC-115` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py` | Closed as bounded runtime proof for `flushQueueGrant`, `timeAdvanceGrant`, and callback-delivery control through both the in-process lane and hosted FedPro replay. |
| Time queries and lookahead control | `HLA2025-FI-SVC-116`, `HLA2025-FI-SVC-117`, `HLA2025-FI-SVC-118`, `HLA2025-FI-SVC-119`, `HLA2025-FI-SVC-120` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py`, `tests/backends/test_shim_route_trace_evidence.py` | Closed as bounded runtime proof for `queryGALT`, `queryLogicalTime`, `queryLITS`, `modifyLookahead`, and `queryLookahead`, including live lookahead changes and route-backed GALT/LITS observability. |
| Retraction, order, and time-window safety | `HLA2025-FI-SVC-121`, `HLA2025-FI-SVC-122`, `HLA2025-FI-SVC-123`, `HLA2025-FI-SVC-124`, `HLA2025-FI-SVC-125` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/backends/test_shim_route_trace_evidence.py`, `packages/hla-rti1516-2025/src/hla/rti1516_2025/time.py` | Closed as bounded runtime proof for retraction, request-retraction callbacks, attribute/interaction order control, queued TSO routing, lookahead-window closure, future-exclusion, and restore rollback of dirty time state on the main `python1516_2025` lane plus hosted replay. |

## Owner Row Scope

- The canonical time-management owner rows carried by this note are the Clause
  8 service rows `HLA2025-FI-SVC-101` through `HLA2025-FI-SVC-125`.
- `HLA2025-FI-009` and `HLA2025-MOD-006` are intentionally linked helper rows
  for logical-time factory and model selection context, but they do not become
  canonical time-service owner rows just because they share the same bounded
  proof families.
- Read this note as the bounded time-management proof owner for the Clause 8
  rows plus explicit logical-time helper links, not as a license to relabel
  broader interface-model rows as time-service closure.

## Time-Window and Logical-Time Closure Notes

- The maintained focused rerun view for this bounded family is
  `./tools/test-focus run python-2025-time`.
- The direct aggregate proof lane is `./tools/python verify-main-2025`, and
  the paired hosted replay lane is `./tools/python verify-routes-2025`.
- `HLA2025-FI-009` and `HLA2025-MOD-006` are carried by the same bounded time
  proof families above: selected federation-wide logical-time factories,
  lookahead queries and modification, GALT/LITS observability, and the
  Target/Radar time-window gauntlet.
- The direct `python1516_2025` lane and hosted FedPro replay both exercise the
  repo's time-window core, output-delivery, consumer-order, pipeline,
  receive-order-poison, future-exclusion, and save/restore rollback scenarios.
- The claim remains bounded: Java and C++ bindings still rely on
  artifact/runtime-capability evidence rather than exhaustive behavior
  equivalence, and hosted FedPro remains a bounded runtime slice rather than a
  full cross-binding conformance route.
- The primary runtime owner behind the executable anchors above is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner for
  these time-management rows.

## Vendor-Credence Boundary

- The main executable evidence for these rows remains the direct
  `python1516_2025` lane plus the hosted `python1516_2025-fedpro-grpc` replay.
- For Pitch specifically, the current trial-safe operator probes are:
  `./tools/pitch time-window-probe` for the two-federate
  `time-window-future-exclusion` route and
  `./tools/pitch time-window-restore-state-probe` for the two-federate
  `time-window-save-restore-window-state` route.
- Those Pitch probes are useful vendor credence because they reuse the same
  bounded time-window closure and rollback claims with a vendor runtime small
  enough to fit the practical two-federate constraint.
- They do not replace the broader `hla-backend-python1516-2025` proof for
  output-delivery, consumer-order, pipeline overlap, or save/restore output
  replay, and they do not upgrade Pitch into the main 2025 Python RTI owner.
