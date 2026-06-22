# Python RTI Backend

This page is the architecture and evidence note for the Python RTI lanes in
this repository, with the 2025 lane treated as a real Python RTI
implementation rather than a shim-owned surface.

It answers four questions:

1. what the repo is actually building
2. how the 2010 and 2025 Python lanes differ
3. what is already proven about the current 2025 lane
4. what evidence would still justify further wrapper-boundary cleanup or
   extraction work

## Current Lanes

The repo does not currently contain two identical Python RTIs for the same
standard surface.

It contains:

- a 2010 pure Python RTI backend: `hla-backend-inmemory`
- a primary 2025 Python RTI backend: `hla-backend-python2025`
- a legacy 2025 compatibility-wrapper package: `hla-backend-shim`
- hosted 2025 transport routes, such as `python-2025-fedpro-grpc`, that are
  route variants over the 2025 lane rather than a separate RTI

Relevant package anchors:

- `packages/hla-backend-inmemory`
- `packages/hla-backend-python2025`
- `packages/hla-backend-shim`
- `packages/hla-rti1516-2025`
- `packages/hla-transport-grpc`
- `packages/hla-verification`

The important distinction is architectural, not naming-based:

- the 2010 lane is a direct pure-Python backend for `rti1516e`
- the 2025 lane is now owned in practice by `hla-backend-python2025`, which is
  the repo's real Python RTI implementation lane for `rti1516_2025`
- the main full runtime now executes from `hla-backend-python2025`
- `hla-backend-shim` remains as a compatibility wrapper so legacy provider
  names and wrapper-facing normalization do not get confused with core RTI
  ownership

## Why `shim` Still Exists

The wrapper package name reflects repository history, not current runtime
ownership.

`hla-backend-shim` still exists for shim-shaped compatibility reasons:

- preserving the legacy `shim` provider name
- preserving compatibility imports and wrapper-facing symbols
- keeping explicit `Shim2025*` wrapper entry points available where older
  routes still opt into them
- carrying only thin compatibility indirection while the executable runtime
  stays in `hla-backend-python2025`

But the repo no longer treats it as the implementation owner. The verification
surface now exercises the primary runtime in `hla-backend-python2025`, while
retaining `hla-backend-shim` as a compatibility surface.

That separation applies to hosted operator paths too: the maintained 2025
transport-hosted lane is named and evidenced as `python2025`, while `shim`
stays a compatibility-wrapper alias rather than the canonical hosted runtime
surface.

That means the practical repo stance is:

- current reality: `hla-backend-python2025` is the main full Python 2025 RTI implementation lane
- compatibility reality: `hla-backend-shim` is a legacy wrapper over that lane
- architectural caution: do not collapse shim concerns and RTI concerns so
  tightly that a later extraction becomes impossible

In repo terms, `python2025` is the RTI lane. `shim` is not.

The important clarification is that the dedicated runtime already exists. The
remaining architectural question is how narrow the compatibility wrapper should
be, not whether the repo still needs to create a real Python 2025 RTI backend.

For day-to-day implementation work, use `python2025` as the 2025 backend lane
and treat `shim` as compatibility-only. Do not describe new 2025 runtime work
as if the shim package were still the implementation owner.

## Routine Proof Commands

Use these two commands as the normal operator-facing proof lanes behind the
current 2025 claim:

- `./tools/python verify-main-2025` for the direct main-surface `python2025`
  proof lane over `hla-backend-python2025`
- `./tools/python verify-routes-2025` when you also need the bounded hosted
  `python-2025-fedpro-grpc` hygiene lane over that same runtime

Treat `verify-main-2025` as the default 2025 proof path. Reach for
`verify-routes-2025` when the change touches hosted transport behavior,
route-parity alignment, or the shared direct-plus-hosted Target/Radar proof
surfaces.

Those two commands now name the current proof families explicitly instead of
leaving them buried inside broad keyword slices:

- package-boundary and runtime-identity guards that keep `python2025` as the
  owned RTI lane and `shim` as wrapper-only
- federation, object, and DDM runtime proofs across lifecycle, listing,
  exchange, region gating, scope relevance, and directed routing
- support-service, callback-control, ownership, and MOM runtime proofs
- Target/Radar time-window and lookahead proofs, including future-exclusion,
  output ordering, pipeline, and restore-window ladders
- save/restore lifecycle, rollback, replay-guard, and gauntlet proofs
- OMT validation/parsing evidence

In repo terms, the operator-facing 2025 proof contract is now organized around
those families, not just around historical test-file names.

## What Is Proven Today

The strongest current evidence is split across the 2025 finish-line inventory,
the main 2025 spec suite, and the route-parity ledgers.

Primary evidence anchors:

- `docs/plans/2025_requirements_finish_line.md`
- `docs/plans/2025_python_rti_backend_audit.md`
- `packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py`
- `packages/hla-verification/src/hla/verification/repo_internal/verification/spec2025_route_parity_matrix.py`
- `examples/target_radar_simulation.py`
- `tests/scenarios/test_target_radar_scenario.py`
- `tests/test_fom_target_radar_split_package.py`
- `tests/test_rti1516_2025_spec_and_shim.py` (historical filename; main in-process python2025 proof suite)
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
  plus restore recovery of in-flight ownership negotiations and cross-federate
  owner-visibility state
- DDM region filtering and region-driven callback behavior
- logical-time selection, time regulation/constrained mode, queued TSO
  delivery, partial-delivery retraction against lagging subscribers, GALT/LITS
  query evidence, disconnected-target retraction cleanup, post-delivery plain
  retraction fanout, per-federate time-state restore, flush-queue grant
  targeting, retraction, and bounded lookahead-window proofs
- support-service lookups, handle normalization, switch inquiry/set flows, and
  name reservation flows
- raw `python2025` support-service handle-factory and decode-helper proof
  without routing through the compatibility wrapper
- snake-case alias acceptance on the primary direct `python2025` runtime
  surface
- raw callback-control proof on the main lane:
  `disableCallbacks`, `enableCallbacks`, `evokeCallback`, and
  `evokeMultipleCallbacks` execute against `hla-backend-python2025` itself and
  release queued discovery/reflection callbacks only after callback delivery is
  re-enabled
- OMT parser, serializer, validation, and explicit unsupported-boundary rows
- the backend-neutral Target/Radar example route as a package-owned shared
  scenario path: `examples/target_radar_simulation.py --backend python2025 --steps 5`
  now runs through `hla.foms.target_radar._internal.TargetRadar2025RTIAdapter`,
  which is owned by `hla-fom-target-radar` and wraps both `python2025` and the
  wrapper-only `shim` alias without moving runtime ownership back into
  `hla-backend-shim`; the same package-owned adapter now also runs the shared
  future-exclusion time-window proof and restore-state save/restore proof over
  the factory-hosted `create_rti_ambassador("python2025", transport=...)`
  FedPro route
- hosted FedPro route behavior as a bounded runtime slice

Recent 2025 suite state:

- `tests/test_rti1516_2025_spec_and_shim.py`: full green; despite the historical filename, this is the main executable in-process proof suite for `hla-backend-python2025`
- the direct in-process 2025 suite now explicitly proves partial-delivery TSO
  retraction semantics on the main `python2025` lane: an interaction can be
  delivered to one constrained subscriber, retracted, and withheld from a
  lagging subscriber that later advances to the same timestamp
- the hosted FedPro route now replays that partial-delivery retraction
  invariant too: a delivered subscriber receives `REQUEST_RETRACTION`, while a
  lagging subscriber later advanced to the same logical time does not receive
  the retracted interaction
- the factory-hosted `create_rti_ambassador("python2025", transport=...)`
  route now also proves direct MOM federation-management save/restore service
  interactions on the hosted 2025 ambassador surface, and the hosted FedPro
  2025 ambassador now accepts camelCase 2025 API entrypoints as aliases over
  its snake_case transport implementation methods
- that same factory-hosted route now also proves direct MOM time-management
  service interactions on the hosted 2025 ambassador surface: regulation and
  constrained mode enable/disable, lookahead modification/query, TAR/TARA,
  NMR/NMRA, flushQueueRequest, and async-delivery toggles all execute through
  the direct `python2025` hosted ambassador with the expected 2025 exception
  surface
- that same factory-hosted route now also proves a direct MOM request/report
  slice on the hosted 2025 ambassador surface: publication/subscription
  reports, interaction publication/subscription reports, object-instance
  information reports, and basic activity-count reports now execute through the
  direct `python2025` hosted ambassador rather than only through lower-level
  transport-only FedPro tests
- that same factory-hosted route now also proves a direct MOM
  object/ownership-service slice on the hosted 2025 ambassador surface:
  transportation-type change requests, unconditional ownership divestiture,
  hosted delete-object service routing, and hosted local-delete service routing
  now execute through the direct `python2025` hosted ambassador rather than
  only through lower-level transport-only FedPro tests
- that same factory-hosted route now also proves a direct federation
  listing/member-report slice on the hosted 2025 ambassador surface:
  `listFederationExecutions`, `listFederationExecutionMembers`, and
  missing-federation reporting now execute through the direct `python2025`
  hosted ambassador with real 2025 callback datatypes rather than raw transport
  payload dicts
- that same factory-hosted route now also proves a direct support-service slice
  on the hosted 2025 ambassador surface: automatic-resign get/set, multiple
  object-instance name reservation callbacks, object-instance name lookup, and
  queued reflection release after callbacks are re-enabled
- that same factory-hosted route now also proves a direct callback-backlog
  disconnect/rejoin slice on the hosted 2025 ambassador surface: if a hosted
  subscriber disables callbacks, accumulates queued traffic, then suffers
  abrupt hosted transport loss, that stale callback backlog does not leak into
  a later hosted joiner while fresh post-rejoin traffic still routes normally
- that same factory-hosted route now also proves a direct restore-control
  negative slice on the hosted 2025 ambassador surface: missing-label restore
  failure, restore-not-requested rejection, save abort, and restore abort all
  execute through the direct hosted `python2025` ambassador rather than being
  left only to lower-level FedPro control-path tests
- that same factory-hosted route now also proves a direct local-delete restore
  slice on the hosted 2025 ambassador surface: after a subscriber locally
  deletes a discovered object, restore returns the saved known-object state and
  a fresh post-restore reflection routes again on the restored handle through
  the direct hosted `python2025` ambassador
- that same factory-hosted route now also proves a direct object-exchange slice
  on the hosted 2025 ambassador surface: publish/subscribe wiring, object
  discovery, attribute reflection, and interaction receipt all execute through
  the direct `python2025` hosted ambassador on the package-owned Target/Radar
  FOM rather than only through broader hosted scenario replay
- that same factory-hosted route now also proves a direct timestamped
  delivery/retraction slice on the hosted 2025 ambassador surface:
  timestamped updates and interactions now return retraction handles on the
  direct hosted `python2025` ambassador, a delivered constrained subscriber can
  observe the timestamped callbacks and later receive `requestRetraction`, and
  a lagging constrained subscriber advanced afterward does not receive the
  retracted timestamped traffic
- that same factory-hosted route now also proves a direct directed-interaction
  slice on the hosted 2025 ambassador surface: plain directed routing reaches
  only object-class directed subscribers, non-subscribing observers do not
  receive the callback, and timestamped directed interactions now execute with
  direct hosted delivery plus later retraction against a delivered constrained
  subscriber while a lagging constrained subscriber advanced afterward does not
  receive the retracted directed traffic
- that same factory-hosted route now also proves a direct ownership slice on
  the hosted 2025 ambassador surface: owned-attribute reacquisition rejection,
  non-owner divestiture rejection, unavailable acquisition while another
  federate owns the attribute, unconditional divestiture to unowned state,
  acquisition notification after claim, and ownership query callbacks with the
  expected 2025 attribute-set callback shape
- the same direct suite now also proves that retraction callbacks are dropped
  for a delivered target that disconnects before the publisher retracts the
  interaction, so stale delivered-target callback state does not survive
- the hosted FedPro route now replays that disconnect-before-retraction
  invariant too: delivered-target retraction state is cleared when the
  delivered member disconnects, and no stale `REQUEST_RETRACTION` callback is
  emitted
- the same direct suite also proves plain timestamped post-delivery retraction
  fanout: when multiple constrained subscribers have already received the same
  interaction, a later retract fans out `requestRetraction` coherently to each
  delivered subscriber
- the hosted FedPro route now replays that post-delivery retraction fanout
  invariant too: both already-delivered subscribers receive
  `REQUEST_RETRACTION` for the same handle
- the direct suite now also proves stale timed-remove cleanup across restore:
  a pre-restore timestamped delete consumed on one branch does not leak into
  the restored branch, while a fresh post-restore timed remove is still routed
  correctly
- the hosted FedPro route now replays that stale timed-remove restore
  invariant too: the pre-restore timed remove is cleared from queued and
  delivered retraction bookkeeping after restore, and a fresh post-restore
  timed remove still routes only to the intended observer
- the direct suite now also proves restore recovers locally deleted
  object-known-state: a subscriber that locally deletes a discovered object
  regains the saved known-state after restore, and fresh post-restore
  reflections route again against that restored handle
- the hosted FedPro route now replays that same local-delete restore invariant:
  after `LOCAL_DELETE_OBJECT_INSTANCE`, restore returns the subscriber's saved
  known-object state and a fresh post-restore `REFLECT` callback routes again
  on the restored handle
- the direct suite also proves stale plain-callback cleanup across restore:
  dirty post-save plain interaction callbacks do not replay after restore, and
  fresh post-restore plain callbacks still route under the restored callback
  policy
- the hosted FedPro route now replays that callback-policy restore invariant
  too: a dirty post-save plain interaction does not replay after restore, and
  a fresh post-restore plain callback still routes once callback delivery is
  re-enabled
- the hosted FedPro route now also proves reconnect-safe callback backlog
  hygiene: when a disabled peer disconnects with queued callbacks, that stale
  backlog is discarded before a later reconnecting federate joins, while fresh
  post-reconnect callbacks still route normally
- the direct suite already proves per-federate time-state restore and
  flush-queue targeting behavior too: logical time, lookahead, and GALT/LITS
  bounds recover correctly after restore, and flush grants remain targeted to
  the federate that issued the flush request
- the hosted FedPro route now replays that time-state restore surface too:
  the shared restore-local-state scenario restores saved lookahead plus
  transport/order policy state and routes fresh post-restore traffic under the
  restored settings, while the FedPro flush-queue restore path keeps grants
  targeted to the requesting federate
- the direct suite already proves restore-control negative paths too: missing
  save-label failure, restore abort, restore precondition rejection,
  restore-participant exception handling, and restore-status exception handling
  are all exercised directly on `hla-backend-python2025`
- the hosted FedPro route now replays that restore-control negative surface
  too: request-precondition, missing-label failure, restore abort,
  participant-exception, and status-exception control flow are all exercised
  over the transport seam as parity evidence rather than left as direct-only
  proof
- the direct suite already proves transportation-type restore persistence too:
  attribute and interaction transportation metadata survive save/restore and
  resume with the restored transport semantics after rollback
- the hosted FedPro route now replays that transportation-type restore
  persistence too: transport/order metadata restoration is proven over the
  FedPro route, not just in-process
- the direct suite already proves ownership-specific restore recovery too:
  in-flight ownership negotiations resume from the saved state, and
  cross-federate owner-visibility queries reflect the restored ownership graph
- the hosted FedPro route now replays that ownership restore surface too: one
  route restores in-flight ownership negotiation state, and another proves
  cross-federate owner-visibility queries return the restored ownership graph
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

Those remaining limits should be described carefully:

- hosted FedPro gaps are mostly transport-seam proof gaps, not evidence that
  `hla-backend-python2025` lacks the underlying runtime semantics
- Java/C++ gaps are binding/adaptation proof gaps, not alternate Python RTI
  implementation ownership questions

So the honest statement is:

- proven: coherent bounded working RTI surface
- not proven: full requirement-by-requirement 2025 conformance

## Promotion And Boundary Discipline

The repo should not decide this by package name alone.

The decision should be evidence-driven.

### Promote The Current 2025 Lane If

The existing `hla-backend-python2025` implementation lane continues to satisfy
all of these:

- the `hla-backend-python2025` runtime suites remain green across the main in-process and hosted
  route evidence surfaces
- shim-shaped adapter code remains a thin layer over real backend semantics,
  rather than becoming the place where core RTI state is tangled together
- new capability work lands primarily as reusable runtime semantics plus shared
  verification, not one-off adapter patches
- the remaining requirement-by-requirement audit can be completed without
  needing a deeper internal backend split

If those continue to hold, promotion is justified by implementation reality:
`hla-backend-python2025` is already acting as the repo's main full Python RTI
2025 backend, while `hla-backend-shim` stays as the compatibility layer in front of
that runtime where needed.

### Narrow Or Extract More Later If

Additional wrapper narrowing or deeper internal extraction becomes the better
design only if at least one of these becomes true:

- adapter concerns begin to obscure or distort the real backend semantics
- callback normalization and route adaptation become more complex than the RTI
  logic they are wrapping
- the repo needs a thinner stable shim in front of a cleaner reusable 2025
  RTI runtime core
- future 2025 features are materially harder to implement or reason about
  because the current package mixes API adaptation and RTI state management too
  tightly

If that happens, the right move is not to create the real backend from scratch;
that part is already done in `hla-backend-python2025`. The shared verification
and requirement ledgers should instead carry forward and validate a cleaner
runtime/module boundary around that existing backend plus a narrower shim
layer.

## Present Recommendation

Based on the current repo evidence, the practical recommendation is:

- treat `hla-backend-python2025` as the repo's main full executable Python 2025 RTI implementation
- keep `hla-backend-shim` as a compatibility-wrapper provider name
- continue proving behavior against the live backend while keeping wrapper and RTI ownership separate
- preserve a clean enough internal boundary that later wrapper narrowing or
  extraction remains possible
- do not claim full 2025 conformance until the remaining requirement-level
  blockers are closed

Put more bluntly: stop using shim language for the primary 2025 runtime lane.

For the explicit promotion-versus-extraction audit, read
[`plans/2025_python_rti_backend_audit.md`](plans/2025_python_rti_backend_audit.md).

That is the current best-fit interpretation of the codebase:

- not just a compatibility facade
- not yet a final unqualified conformance claim
- yes, a substantively validated working Python 2025 RTI surface
