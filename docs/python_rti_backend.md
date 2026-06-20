# Python RTI Backend

This page is the architecture and evidence note for the Python RTI lanes in
this repository.

It answers four questions:

1. what the repo is actually building
2. how the 2010 and 2025 Python lanes differ
3. what is already proven about the current 2025 lane
4. what evidence would still justify a future split between shim concerns and
   RTI concerns

## Current Lanes

The repo does not currently contain two identical Python RTIs for the same
standard surface.

It contains:

- a 2010 pure Python RTI backend: `hla-backend-inmemory`
- a 2025 Python implementation lane: `hla-backend-shim`
- hosted 2025 transport routes, such as `python-2025-fedpro-grpc`, that are
  route variants over the 2025 lane rather than a separate RTI

Relevant package anchors:

- `packages/hla-backend-inmemory`
- `packages/hla-backend-shim`
- `packages/hla-rti1516-2025`
- `packages/hla-transport-grpc`
- `packages/hla-verification`

The important distinction is architectural, not naming-based:

- the 2010 lane is a direct pure-Python backend for `rti1516e`
- the 2025 lane began as a spec-shaped shim, but in the current repo it is the
  executable Python backend used for the `rti1516_2025` runtime proof surface

## Why The 2025 Lane Is Still Called `shim`

The package name reflects how the lane started, not the current evidence
surface.

`hla-backend-shim` still contains shim-shaped responsibilities:

- 2025 API adaptation
- callback and datatype normalization
- route-facing surface alignment
- explicit unsupported-boundary handling

But the repo no longer treats it as a trivial stub. The verification surface
now exercises it as the active Python 2025 implementation lane.

That means the practical repo stance is:

- current reality: `hla-backend-shim` is the live Python 2025 RTI lane
- architectural caution: do not collapse shim concerns and RTI concerns so
  tightly that a later extraction becomes impossible

## What Is Proven Today

The strongest current evidence is split across the 2025 finish-line inventory,
the main 2025 spec suite, and the route-parity ledgers.

Primary evidence anchors:

- `docs/plans/2025_requirements_finish_line.md`
- `docs/plans/2025_python_rti_backend_audit.md`
- `packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py`
- `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`
- `tests/test_rti1516_2025_spec_and_shim.py`
- `tests/requirements/test_2025_finish_line_snapshot.py`
- `tests/requirements/test_2025_route_parity_matrix.py`
- `tests/backends/test_shim_route_trace_evidence.py`
- `tests/transport/test_grpc_transport_2025.py`

The current bounded claim is:

- the Python-centered 2025 surface is validated as a bounded working RTI
  surface across federation management, object management, time management,
  support services, callbacks, OMT handling, and binding routes

What that currently includes:

- federation lifecycle, synchronization, save/restore, and membership behavior
- object discovery, reflection, interaction delivery, deletion, and directed
  interaction handling
- ownership flows and resign-time ownership policies
- DDM region filtering and region-driven callback behavior
- logical-time selection, time regulation/constrained mode, queued TSO
  delivery, GALT/LITS query evidence, retraction, and bounded lookahead-window
  proofs
- support-service lookups, handle normalization, switch inquiry/set flows, and
  name reservation flows
- OMT parser, serializer, validation, and explicit unsupported-boundary rows
- hosted FedPro route behavior as a bounded runtime slice

Recent 2025 suite state:

- `tests/test_rti1516_2025_spec_and_shim.py`: full green
- `tests/requirements/test_2025_finish_line_snapshot.py`: green
- `tests/requirements/test_2025_route_parity_matrix.py`: green
- `tests/backends/test_shim_route_trace_evidence.py`: green

## What Is Not Proven

The repo does not yet have evidence strong enough to claim unconditional IEEE
1516-2025 conformance for the current lane.

Current blockers are explicit in the finish-line snapshot:

- many requirement claims are still represented by bounded multi-requirement
  slices rather than one-row final SHALL proof
- Java and C++ 2025 bindings are still artifact-gated/runtime-capability
  evidence, not exhaustive behavior-conformance evidence
- the hosted FedPro route is a bounded runtime slice, not a full RTI semantics
  or full MOM action/request conformance pass
- OMT proof intentionally mixes supported-subset coverage with explicit
  unsupported-boundary rows
- unsupported-boundary and legacy-only rows are named exclusions, not delivered
  support

So the honest statement is:

- proven: coherent bounded working RTI surface
- not proven: full requirement-by-requirement 2025 conformance

## Promotion Vs Split Decision

The repo should not decide this by package name alone.

The decision should be evidence-driven.

### Promote The Current 2025 Lane If

The existing `hla-backend-shim` lane continues to satisfy all of these:

- the 2025 runtime suites remain green across the main in-process and hosted
  route evidence surfaces
- shim-shaped adapter code remains a thin layer over real backend semantics,
  rather than becoming the place where core RTI state is tangled together
- new capability work lands primarily as reusable runtime semantics plus shared
  verification, not one-off adapter patches
- the remaining requirement-by-requirement audit can be completed without
  needing a deeper internal backend split

If those continue to hold, promotion is justified by implementation reality:
the current lane is already acting as the real Python RTI 2025 backend.

### Split The Lane Later If

A future dedicated 2025 RTI backend becomes the better design only if at least
one of these becomes true:

- adapter concerns begin to obscure or distort the real backend semantics
- callback normalization and route adaptation become more complex than the RTI
  logic they are wrapping
- the repo needs a thinner stable shim in front of a cleaner reusable 2025
  runtime core
- future 2025 features are materially harder to implement or reason about
  because the current package mixes API adaptation and RTI state management too
  tightly

If that happens, the right move is not to discard the current evidence. The
shared verification and requirement ledgers should carry forward and validate a
new dedicated backend beside a narrower shim layer.

## Present Recommendation

Based on the current repo evidence, the practical recommendation is:

- treat `hla-backend-shim` as the current executable Python 2025 RTI lane
- continue proving behavior against it as the live backend
- preserve a clean enough internal boundary that a later extraction remains
  possible
- do not claim full 2025 conformance until the remaining requirement-level
  blockers are closed

For the explicit promotion-versus-extraction audit, read
[`plans/2025_python_rti_backend_audit.md`](plans/2025_python_rti_backend_audit.md).

That is the current best-fit interpretation of the codebase:

- not just a stub shim
- not yet a final unqualified conformance claim
- yes, a substantively validated working Python 2025 RTI surface
