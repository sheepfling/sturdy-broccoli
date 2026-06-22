# 2025 Python RTI Backend Audit

This note is the explicit architecture-and-evidence audit for the current IEEE
1516.1-2025 Python implementation lane.

Use it to answer one concrete question:

Is the repo currently proving a real Python 2025 RTI, or only fleshing out a
legacy package seam?

## Short Answer

The repo is currently proving a real executable Python 2025 RTI surface, and
that main full runtime now executes from `hla-backend-python2025`.

That means:

- `hla-backend-python2025` is now the main full Python runtime package used for
  `rti1516_2025`
- `hla-backend-shim` remains only as temporary import-compatibility
  scaffolding and wrapper-only compatibility support
- the repo is no longer relying on a shim-named package as the source of truth
- the architecture should still preserve a clean enough seam that the shim can
  continue shrinking toward wrapper-only responsibilities

## Current Repo Reality

The repo is not building two duplicate Python 2025 RTIs.

The actual lanes are:

- `hla-backend-inmemory`: the 2010 pure-Python RTI backend
- `hla-backend-python2025`: the main full Python 2025 RTI implementation lane
- `hla-backend-shim`: temporary import-compatibility scaffolding and a
  wrapper-only compatibility package over that live runtime
- `python-2025-fedpro-grpc`: a hosted route variant over the 2025 lane, not a
  separate RTI family
- `hla-bridge-java-common`: Java 2025 binding-surface and artifact/intake
  evidence lane, not the Python 2025 RTI
- `hla-backend-cpp-shim`: C++ 2025 binding-surface and artifact/runtime-capability
  lane, not the Python 2025 RTI

So the practical 2025 story is:

- the repo does have a working Python 2025 RTI lane
- the repo now has a main full `hla-backend-python2025` backend package
- the legacy `hla-backend-shim` package is being retained as temporary
  import-compatibility scaffolding rather than as the implementation owner
- Java and C++ are segregated supporting binding lanes, not alternate Python
  2025 RTIs
- the important architectural question is whether the remaining shim-facing
  compatibility surface can keep shrinking without obscuring runtime proof

The implementation layout matters here too. The current 2025 lane is not just
`hla-backend-python2025/backend.py` pretending to be a package. The public
shell now fronts extracted runtime/state/surface modules such as:

- `backend_factory_runtime.py`
- `runtime_state.py`
- `federation_management_runtime.py`
- `time_management_runtime.py`
- `support_services_runtime.py`
- `*_surface_mixin.py`

That split is part of the evidence story: core RTI semantics now land in the
main `hla-backend-python2025` package-owned runtime modules, while
`hla-backend-shim` keeps only temporary import-compatibility scaffolding,
wrapper-only compatibility, and forwarder concerns.

## Audit Snapshot

- Main 2025 RTI package: `hla-backend-python2025`
- Wrapper-only compatibility package: `hla-backend-shim`
- 2010 pure Python RTI package: `hla-backend-inmemory`
- Python 2025 route count: `2`
- Hosted Python 2025 route: `python-2025-fedpro-grpc`
- Non-Python binding lanes kept segregated: `2`
- Recent combined 2025 verification slice: `targeted finish-line/backend-owner audit slice ran green on current tree`
- Recent hosted 2025 FedPro transport suite: `252 passed in current-tree hosted FedPro transport suite`
- Shared hosted FedPro scenarios represented: `36 / 36`
- Trial Pitch-safe time-window routes: `2`

## What The Current Evidence Proves

The strongest current repo claim is a bounded working-surface claim, not a full
unqualified IEEE 1516.1-2025 conformance claim.

More specifically, the current Python 2025 lane is a best-attempt bounded
working surface, not a final full-fledged RTI conformance certification.

Current evidence proves that the Python-centered 2025 lane is a coherent,
executable RTI surface across:

- federation management
- object and interaction management
- ownership and DDM behavior
- time management, including GALT/LITS queries and bounded lookahead proofs
- support services and callback flows
- OMT parsing, validation, and explicit unsupported-boundary handling
- direct and hosted Python 2025 route variants

The direct in-process proof is important here, not just the hosted route:

- `tests/test_rti1516_2025_python2025_runtime.py` now includes direct
  `create_rti_ambassador(backend="python2025")` proof for support-service
  handle factories and decode helpers without routing through the compatibility
  wrapper
- that same direct-lane slice also proves the raw `python2025` runtime accepts
  the snake-case aliases that the repo expects on the primary Python RTI
  surface, without reclassifying the runtime as shim-owned behavior
- the direct in-process suite now also proves raw callback-control services on
  the main lane: `disableCallbacks`, `enableCallbacks`, `evokeCallback`, and
  `evokeMultipleCallbacks` execute against `hla-backend-python2025` itself and
  release queued discovery/reflection callbacks only after callback delivery is
  re-enabled
- `tests/test_rti1516_2025_python2025_runtime.py` now includes an explicit
  partial-delivery TSO retraction proof on the main `python2025` lane
- that route verifies one constrained subscriber can receive a timestamped
  interaction, the publisher can retract it, and a lagging subscriber later
  granted to the same logical time does not receive the retracted interaction
- the hosted FedPro route replays that partial-delivery retraction invariant
  too: a delivered subscriber receives `REQUEST_RETRACTION`, while a lagging
  subscriber later advanced to the same logical time does not receive the
  retracted interaction
- the same in-process suite also proves that if an already-delivered target is
  disconnected before retraction, the runtime clears that delivered-target
  state and does not emit a stale `requestRetraction` callback afterward
- the hosted FedPro route replays that disconnect-before-retraction invariant
  too: delivered-target retraction state is cleared when the delivered member
  disconnects, and no stale `REQUEST_RETRACTION` callback is emitted
- the same in-process suite now also proves plain timestamped retraction
  fanout across multiple already-delivered subscribers, so callback fanout for
  that invariant is anchored to the direct `hla-backend-python2025` lane too
- the hosted FedPro route also replays that post-delivery retraction fanout
  invariant: both already-delivered subscribers receive `REQUEST_RETRACTION`
  for the same handle
- the direct suite now also proves stale timed-remove cleanup across restore,
  so pre-restore timestamped delete callbacks do not leak into the restored
  branch while fresh post-restore timed removes still route correctly
- the hosted FedPro route replays that stale timed-remove restore invariant
  too: the pre-restore timed remove is cleared from queued and delivered
  retraction bookkeeping after restore, and a fresh post-restore timed remove
  still routes only to the intended observer
- the direct suite now also proves restore recovers locally deleted
  object-known-state: a federate that locally deletes a discovered object
  regains the saved known-state after restore, and fresh post-restore
  reflections resume against that restored object handle
- the hosted FedPro route now replays the same local-delete restore invariant:
  after `LOCAL_DELETE_OBJECT_INSTANCE`, restore returns the subscriber's saved
  known-object state and a fresh post-restore `REFLECT` callback resumes on
  the restored handle
- the direct suite already proves stale plain-callback cleanup across restore
  too: dirty post-save plain interaction callbacks do not replay after
  restore, while fresh post-restore plain callbacks still route under the
  restored callback policy
- the hosted FedPro route replays that callback-policy restore invariant as
  well: a dirty post-save plain interaction does not replay after restore, and
  a fresh post-restore plain callback still routes once callback delivery is
  re-enabled
- the direct suite already proves per-federate time-state restore and
  flush-queue grant targeting as well: restored logical times and lookaheads
  snap back to the saved per-federate values, GALT/LITS recover accordingly,
  and flush grants stay targeted to the requesting federate
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
  persistence as well, so transport/order metadata restoration is not just a
  direct-lane claim
- the direct suite already proves ownership-specific restore recovery too:
  in-flight ownership negotiations resume from the saved state, and
  cross-federate owner-visibility queries reflect the restored ownership graph
- the hosted FedPro route now replays that ownership restore surface too:
  one route restores in-flight ownership negotiation state, and another proves
  cross-federate owner-visibility queries return the restored ownership graph
- this keeps a real time/retraction safety claim anchored to
  `hla-backend-python2025` itself instead of leaving that behavior proven only
  on the hosted FedPro route

For OMT specifically, the current claim is still a bounded OMT working surface:
parser/validator and metadata round-trip evidence are strong, but arbitrary
third-party extension execution semantics are still outside the repo-native
runtime claim.

Primary evidence anchors:

- [python_rti_backend.md](../python_rti_backend.md)
- [2025_requirements_finish_line.md](2025_requirements_finish_line.md)
- [../requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md](../requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md)
- [../requirements/ieee-1516-2025/lookahead_window_bounded_proof.md](../requirements/ieee-1516-2025/lookahead_window_bounded_proof.md)
- [../requirements/ieee-1516-2025/python2025_direct_bounded_proof.md](../requirements/ieee-1516-2025/python2025_direct_bounded_proof.md)
- [../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md](../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md)
- [../packages/hla-backend-python2025/README.md](../../packages/hla-backend-python2025/README.md)
- [../packages/hla-backend-shim/README.md](../../packages/hla-backend-shim/README.md)
- [../examples/target_radar_simulation.py](../../examples/target_radar_simulation.py)
- [../tests/scenarios/test_target_radar_scenario.py](../../tests/scenarios/test_target_radar_scenario.py)
- [../tests/test_fom_target_radar_split_package.py](../../tests/test_fom_target_radar_split_package.py)
- [../tests/test_python2025_split_package.py](../../tests/test_python2025_split_package.py)
- [../tests/test_package_import_isolation.py](../../tests/test_package_import_isolation.py)
- [../tests/test_root_facade_policy.py](../../tests/test_root_facade_policy.py)
- [../tests/test_rti1516_2025_python2025_runtime.py](../../tests/test_rti1516_2025_python2025_runtime.py)
- [../tests/transport/test_grpc_transport_2025.py](../../tests/transport/test_grpc_transport_2025.py)
- [../tests/requirements/test_2025_finish_line_snapshot.py](../../tests/requirements/test_2025_finish_line_snapshot.py)
- [../tests/requirements/test_2025_route_parity_matrix.py](../../tests/requirements/test_2025_route_parity_matrix.py)

For the compact excluded-area inventory behind this bounded claim, use
[`../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md`](../requirements/ieee-1516-2025/python2025_exclusion_boundaries.md).
That requirement-facing note keeps the shim-alias, Java/C++, hosted-route,
umbrella-row, retired-row, and OMT-extension boundaries explicit without
forcing readers to mine the full generated finish-line bundle.

For the tracked example/FOM-backed scenario boundary behind the same bounded
claim, use
[`../requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md`](../requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md).
That note makes the repo-owned Proto2025 and Target/Radar suite explicit
without implying that every possible example FOM composition is proven.

For the explicit Target/Radar lookahead ladder behind the same bounded claim,
use
[`../requirements/ieee-1516-2025/lookahead_window_bounded_proof.md`](../requirements/ieee-1516-2025/lookahead_window_bounded_proof.md).
That note makes the current closure, future-exclusion, output-delivery,
consumer-order, pipeline, negative-oracle, and Pitch-safe vendor-credence
boundaries auditable without pretending the repo has a blanket time-policy
conformance proof.

## Current Proof Contract

The operator-facing 2025 proof contract should now be read as a named
proof-family contract for the main `hla-backend-python2025` lane, not as one
undifferentiated "bounded working surface" bucket.

The current families are:

- package-boundary and runtime-identity guards that keep `python2025` as the
  owned RTI lane and `shim` as wrapper-only
- federation, object, and DDM runtime proofs across lifecycle, listing,
  exchange, region gating, scope relevance, and directed routing
- support-service, callback-control, ownership, and MOM runtime proofs
- Target/Radar time-window and lookahead proofs, including future-exclusion,
  output ordering, pipeline, and restore-window ladders
- save/restore lifecycle, rollback, replay-guard, and gauntlet proofs
- OMT validation/parsing evidence

Those families matter because they separate:

- core runtime proof that belongs to `hla-backend-python2025`
- hosted transport-seam proof that belongs to the bounded FedPro route
- binding/adaptation-seam proof that belongs to Java/C++ wrapper lanes

So when the repo says the current 2025 lane is a substantively validated
working Python RTI surface, the strongest bounded claim is now:

- the main `hla-backend-python2025` runtime clears those named proof families
  across direct and hosted Python 2025 routes
- `hla-backend-shim` remains a compatibility wrapper and should not be treated
  as an implementation-owner proof bucket
- Java/C++ and other wrapper lanes remain supporting seam evidence over the
  main Python 2025 runtime rather than alternate owners of the core 2025 RTI

Recent evidence run already recorded in this worktree:

- dedicated `hla-backend-python2025` split-package surface:
  `71 passed in 0.67s`
- python2025 import-boundary guardrails:
  `163 passed in 40.34s`
- combined 2025 verification slice:
  `targeted finish-line/backend-owner audit slice ran green on current tree`
- full hosted 2025 FedPro transport suite:
  `252 passed in current-tree hosted FedPro transport suite`

Canonical operator proof lanes also ran green on the current tree:

- `./tools/python verify-main-2025`:
  `324 passed across wrapper subcommands plus Target/Radar example`
- `./tools/python verify-routes-2025`:
  `434 passed across direct-plus-hosted wrapper subcommands plus finish-line bundle and Target/Radar example`

Hosted shared-scenario coverage audit:

- Shared hosted FedPro scenarios: 36
- Shared hosted scenarios represented in conformance evidence: 36
- Ready for full shared-scenario representation claim: True
- Every shared hosted FedPro 2025 scenario is now represented in the
  conformance evidence ledger, so the hosted route summary is no longer
  silently under-counting the main python2025 runtime surface

Those results are meaningful because the hosted route proof now includes:

- strict local FOM/MIM resolution and create-time error taxonomy over the
  typed FedPro request families
- callback routing normalization over the transport seam
- reconnect-safe queued-callback cleanup over the transport seam: a
  disconnected peer's disabled callback backlog is discarded before a later
  reconnecting federate joins, while fresh post-reconnect callbacks still
  route normally
- stepwise `nextMessageRequest` / `nextMessageRequestAvailable` behavior
- time-window proof-ladder routes
- save/restore rollback of bounded time-window state
- directed TSO stale-queue cleanup on restore without replaying discarded
  timeline callbacks
- consumer-order and future-exclusion proofs over the hosted 2025 lane

The remaining hosted-heavy evidence is increasingly transport-specific rather
than core-runtime-owned:

- typed FedPro command-envelope coverage and error-taxonomy normalization
- callback polling fairness and broader queue-drain orchestration across the
  explicit transport seam
- broader per-peer reconnect/process-lifecycle bookkeeping inside the hosted
  server process
- bounded remote-route operator coverage for the current explicit
  `start_2025_grpc_server(...)` plus `GrpcTransport(..., schema="rti1516_2025")`
  path

That distinction matters. Those proofs still belong in the repo, but they are
no longer the strongest evidence for whether `hla-backend-python2025` itself
is a real 2025 RTI implementation lane.

The same boundary applies to the remaining non-Python binding evidence too:

- Java and C++ route work is binding/adaptation-seam proof
- it is not evidence that the main Python 2025 runtime is still missing core
  RTI semantics
- those lanes should stay segregated as supporting adapter surfaces over the
  main `hla-backend-python2025` lane

And because the package boundary is now enforced, not merely described:

- `hla-backend-python2025` is treated as its own owned package root in the
  import-isolation guardrail
- `hla-backend-shim` is allowed to depend on that main runtime package
- the main `python2025` runtime package is explicitly tested to ensure it does
  not import back through `hla.backends.shim.*`
- the README-advertised `python examples/target_radar_simulation.py --backend
  python2025 --steps 5` path now executes through a package-owned
  `hla-fom-target-radar` compatibility adapter rather than through
  `hla-backend-shim`
- that shared Target/Radar adapter wraps both `python2025` and the wrapper-only
  `shim` alias while still recording `hla-backend-python2025` as the real
  implementation lane, which keeps the example proof on the main RTI side of
  the architecture boundary

## What The Current Evidence Does Not Prove

The repo does not yet prove that the current 2025 lane is a fully complete,
requirement-by-requirement IEEE 1516.1-2025 backend.

The important current limits are:

- the repo now has a row-level requirement-by-requirement disposition audit
  across all 691 tracked 2025 rows, with covered rows with evidence paths
  called out in the finish-line ledger, but that audit is still bounded rather
  than an all-covered conformance pass
- many rows are still proven through bounded executable slices rather than one
  final SHALL proof per requirement
- hosted FedPro is still a bounded runtime slice, not a full RTI semantics or
  full MOM action/request conformance pass
- Java and C++ binding evidence remains artifact/runtime-capability bounded
- OMT support intentionally includes explicit unsupported-boundary rows
- unsupported, retired, and legacy-only rows are named boundaries, not
  delivered support

The repo's closure rule should stay explicit here too:

- each future or reopened row needs a positive test, a negative
  unsupported-boundary test, or an explicit supported-subset or
  unsupported-boundary disposition before it can be counted as closed

So the correct statement today is:

- yes: substantively validated working Python 2025 RTI surface
- no: not yet a final unconditional 2025 conformance claim

The newer finish-line partition audits make one more thing explicit:

- the remaining full-claim blockers are now partitioned as external ownership
  boundaries rather than hidden direct-runtime incompleteness inside
  `hla-backend-python2025`
- the broader closeout blockers are also partitioned as requirement-granularity,
  hosted-route, cross-binding, OMT-extension-scope, or legacy-exclusion limits
  rather than missing core executable behavior in the main Python 2025 runtime
  lane
- that does not erase the remaining work, but it does make the ownership of the
  remaining work much clearer
- the main `python2025` lane is no longer being held back by vague blocker
  language that might be read as “the runtime is still missing core semantics”

Non-claims that must stay explicit:

- this does not upgrade Java or C++ bindings into exhaustive
  behavior-conformance lanes
- this does not turn the hosted FedPro route into a full RTI semantics or MOM
  action/request conformance pass

## Promotion Decision

The repo can already justify promoting the current lane as the working Python
2025 RTI surface.

That promotion is justified when the claim is phrased carefully:

- the main full Python 2025 RTI implementation now runs from
  `hla-backend-python2025`
- `hla-backend-shim` is retained only as temporary import-compatibility
  scaffolding and wrapper-only compatibility support over that runtime
- it is the main full backend for bounded working-surface claims
- direct and hosted proof should continue to stay green as the shim narrows

This is not the same as saying:

- the architecture is final forever
- the package name is ideal
- a dedicated 2025 backend will never be needed

## Extraction Decision Boundary

The repo should keep narrowing the shim only if the evidence starts showing
that compatibility or route normalization is still obstructing the RTI.

Concrete split triggers are:

- shim adaptation begins to obscure core RTI state and semantics
- callback or route normalization becomes more complex than the behavior it
  wraps
- new 2025 behavior becomes harder to implement because adaptation and runtime
  logic are too tightly mixed
- the row-level requirement-by-requirement audit cannot be promoted from
  bounded disposition evidence into cleaner all-covered runtime proof without a
  narrower shim boundary

If those triggers appear, the right move is:

1. keep the requirement ledgers and runtime verification as the continuity
   layer
2. keep the main full backend in `hla-backend-python2025`
3. move only the remaining compatibility-facing logic that still needs
   relocation
4. keep the shim focused on API adaptation and route-facing normalization

That work has now started in code, not just at the package-contract level:

- `hla-backend-python2025` is present and discoverable as backend
  `python2025`
- it owns directed-interaction target-selection, save/restore lifecycle, and
  DDM/default-policy semantics that the live Python 2025 RTI lane now consumes as shared
  runtime logic
- it is now executable as the standalone promoted RTI backend package
- it does not delegate back to `hla.backends.shim.backend.create_shim_backend`
- the shim package now wraps that runtime rather than owning it

## Present Working Conclusion

The current repo is working toward a real Python RTI 2025 outcome.

It is not merely polishing a fake adapter. It is proving a real executable
2025 runtime lane that now lives in the dedicated Python 2025 backend package.

The honest current working conclusion is:

- promote `hla-backend-python2025` as the repo's working Python 2025 RTI surface
- keep the architectural seam clear enough for continued shim narrowing
- continue the remaining work as runtime-proof expansion and final audit
  closure, not as a naming argument

## Pitch Trial Compatibility

The most credible near-term Pitch time-window route is the two-federate
`time-window-future-exclusion` proof.

That route is intentionally small:

- `SlowRegulatorFederate`
- `RadarFederate`

Why this matters:

- it is a real lookahead/future-message exclusion proof, not a watered-down
  smoke test
- it fits the practical two-federate constraint that matters for limited Pitch
  environments
- it is a better vendor-credence candidate than the larger multi-federate
  gauntlet

The current Pitch blocker is operational, not conceptual:

- [tests/vendors/test_pitch_real_backend_matrix.py](../../tests/vendors/test_pitch_real_backend_matrix.py)
  already carries
  `test_pitch_time_window_future_exclusion_matrix`
- that test is currently marked `xfail` because the managed Pitch runtime
  reports no available pRTI federate seats for this two-federate proof
- the repo should therefore treat the boundary as vendor/runtime seat
  availability, not as evidence that the scenario itself needs to be shrunk

The follow-on time-window routes split cleanly:

- `time-window-restore-state` is also two-federate-safe
- `time-window-restore-output` is three-federate and is therefore not a trial
  Pitch candidate

## Next Evidence Rungs

The next highest-value steps are:

1. continue converting bounded slices into tighter requirement-level proof
   where the finish-line inventory still aggregates multiple requirements
2. keep expanding direct-versus-hosted Python 2025 route parity where new
   runtime behavior lands
3. preserve explicit unsupported boundaries rather than silently over-claiming
   completion
4. use the row-level requirement-by-requirement audit plus the remaining
   executable proof gaps to decide whether the current
   lane remains clean enough to keep, or whether extraction has become the
   better design
