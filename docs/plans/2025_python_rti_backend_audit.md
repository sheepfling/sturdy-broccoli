# 2025 Python RTI Backend Audit

This note is the explicit architecture-and-evidence audit for the current IEEE
1516.1-2025 Python implementation lane.

Use it to answer one concrete question:

Is the repo currently proving a real Python 2025 RTI, or only fleshing out a
shim?

## Short Answer

The repo is currently proving a real executable Python 2025 RTI surface, but
that surface still lives inside the package named `hla-backend-shim`.

That means:

- `hla-backend-shim` is no longer just a thin placeholder
- the current 2025 lane is already the live Python runtime used for
  `rti1516_2025`
- the package name still reflects origin history, not the full current role
- the architecture should still preserve a clean enough seam that a future
  dedicated 2025 backend can be extracted if the evidence later demands it

## Current Repo Reality

The repo is not building two duplicate Python 2025 RTIs.

The actual lanes are:

- `hla-backend-inmemory`: the 2010 pure-Python RTI backend
- `hla-backend-shim`: the current executable 2025 Python implementation lane
- `python-2025-fedpro-grpc`: a hosted route variant over the 2025 lane, not a
  separate RTI family

So the practical 2025 story is:

- the repo does have a working Python 2025 RTI lane
- it is presently hosted inside the package still named `shim`
- the important architectural question is whether that lane should stay there
  permanently or later be extracted into a dedicated backend

## What The Current Evidence Proves

The strongest current repo claim is a bounded working-surface claim, not a full
unqualified IEEE 1516.1-2025 conformance claim.

Current evidence proves that the Python-centered 2025 lane is a coherent,
executable RTI surface across:

- federation management
- object and interaction management
- ownership and DDM behavior
- time management, including GALT/LITS queries and bounded lookahead proofs
- support services and callback flows
- OMT parsing, validation, and explicit unsupported-boundary handling
- direct and hosted Python 2025 route variants

Primary evidence anchors:

- [python_rti_backend.md](../python_rti_backend.md)
- [2025_requirements_finish_line.md](2025_requirements_finish_line.md)
- [../packages/hla-backend-shim/README.md](../../packages/hla-backend-shim/README.md)
- [../tests/test_rti1516_2025_spec_and_shim.py](../../tests/test_rti1516_2025_spec_and_shim.py)
- [../tests/transport/test_grpc_transport_2025.py](../../tests/transport/test_grpc_transport_2025.py)
- [../tests/requirements/test_2025_finish_line_snapshot.py](../../tests/requirements/test_2025_finish_line_snapshot.py)
- [../tests/requirements/test_2025_route_parity_matrix.py](../../tests/requirements/test_2025_route_parity_matrix.py)

Recent evidence run already recorded in this worktree:

- combined 2025 verification slice:
  `467 passed in 78.98s`
- full hosted 2025 FedPro transport suite:
  `168 passed in 38.01s`

Those results are meaningful because the hosted route proof now includes:

- strict local FOM/MIM resolution and create-time error taxonomy over the
  typed FedPro request families
- callback routing normalization over the transport seam
- stepwise `nextMessageRequest` / `nextMessageRequestAvailable` behavior
- time-window proof-ladder routes
- save/restore rollback of bounded time-window state
- directed TSO stale-queue cleanup on restore without replaying discarded
  timeline callbacks
- consumer-order and future-exclusion proofs over the hosted 2025 lane

## What The Current Evidence Does Not Prove

The repo does not yet prove that the current 2025 lane is a fully complete,
requirement-by-requirement IEEE 1516.1-2025 backend.

The important current limits are:

- the repo now has a row-level requirement-by-requirement disposition audit
  across all 691 tracked rows, but that audit is still bounded rather than an
  all-covered conformance pass
- many rows are still proven through bounded executable slices rather than one
  final SHALL proof per requirement
- hosted FedPro is still a bounded runtime slice, not a full RTI semantics or
  full MOM action/request conformance pass
- Java and C++ binding evidence remains artifact/runtime-capability bounded
- OMT support intentionally includes explicit unsupported-boundary rows
- unsupported, retired, and legacy-only rows are named boundaries, not
  delivered support

So the correct statement today is:

- yes: substantively validated working Python 2025 RTI surface
- no: not yet a final unconditional 2025 conformance claim

## Promotion Decision

The repo can already justify promoting the current lane as the working Python
2025 RTI surface.

That promotion is justified when the claim is phrased carefully:

- `hla-backend-shim` is the current executable Python 2025 RTI lane
- it is the live backend for bounded working-surface claims
- it should continue to carry runtime proof until evidence demands a split

This is not the same as saying:

- the architecture is final forever
- the package name is ideal
- a dedicated 2025 backend will never be needed

## Extraction Decision Boundary

The repo should extract a dedicated 2025 backend beside a narrower shim only if
the evidence starts showing that the current packaging is obstructing the RTI.

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
2. introduce a dedicated 2025 backend beside the shim
3. move only the runtime semantics that need extraction
4. keep the shim focused on API adaptation and route-facing normalization

## Present Working Conclusion

The current repo is working toward a real Python RTI 2025 outcome.

It is not merely polishing a fake shim. It is proving a real executable 2025
runtime lane that happens to live in a package with shim-origin naming.

The honest current working conclusion is:

- promote the current lane as the repo's working Python 2025 RTI surface
- keep the architectural seam clear enough for a future extraction
- continue the remaining work as runtime-proof expansion and final audit
  closure, not as a naming argument

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
