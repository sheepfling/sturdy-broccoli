# Requirements Finish Line

This note is the handoff point for the requirements program in this repo.

Use it when you return later and want the shortest route back to a clean,
honest finish.

For the concrete remaining `2010` and `2025` closeout buckets, use
[`requirements_remaining_closure.md`](requirements_remaining_closure.md).

For the current-state answer to "are we actually finished yet?", use
[`requirements_completion_audit.md`](requirements_completion_audit.md).

For boss-facing spreadsheet outputs generated from the canonical requirement
artifacts, use
[`../verification/requirement_compliance_exports.md`](../verification/requirement_compliance_exports.md).

For the canonical bucket owners behind the 2010 surface, use:

- [`../requirements/ieee-1516-2010/README.md`](../requirements/ieee-1516-2010/README.md)
- [`../../requirements/2010/README.md`](../../requirements/2010/README.md)
- [`2010_python_rti_bounded_family_execution_worklist.md`](2010_python_rti_bounded_family_execution_worklist.md)

For the canonical bucket owners behind the 2025 surface, use:

- [`../requirements/ieee-1516-2025/README.md`](../requirements/ieee-1516-2025/README.md)
- [`../../requirements/2025/README.md`](../../requirements/2025/README.md)

Reading rule:

1. use this page for the shortest return path into the closeout
2. use [`requirements_completion_audit.md`](requirements_completion_audit.md)
   for the truthful current answer to "are we done?"
3. use [`requirements_remaining_closure.md`](requirements_remaining_closure.md)
   for the concrete open-bucket shape
4. use [`requirements_gap_register.md`](requirements_gap_register.md) when you
   need the exact owner doc plus owner companion pair for one still-open bucket
5. use [`../verification/requirement_compliance_exports.md`](../verification/requirement_compliance_exports.md)
   only when you need the generated presentation packet, not canonical
   ownership

## What is already in place

- a harmonized `2010` requirements catalog in `requirements/2010/*.csv`
- a bounded `2025` requirements surface in `requirements/2025/`
- generated compliance artifacts under `analysis/compliance/`
- requirement-to-test traceability
- vendor and backend discovery artifacts
- explicit broad-spec versus supported-subset policy language
- an honest-test rule that prevents overclaiming mapped rows
- canonical owner docs now exist for the main 2010 bounded-family tails, the
  remaining mixed-backend 2010 priority rows, and the main 2025 umbrella,
  retired, binding-hosted, and Pitch proto HLA 4 / `202X` boundary buckets
- execution companions now exist for the remaining `2010` bounded-family class
  and the remaining `2025` umbrella-row class

## What still needs to happen

The repo no longer has active top-level `planned` bucket inventory in the
canonical `2010` or grouped `2025` closeout surfaces.

The remaining work is now about whether to preserve or deliberately tighten the
maintained bounded classes below:

- `2010` bounded partial families that already have explicit owner notes
- `2010` bounded mixed-backend priority rows with separate backend-resolution
  companions
- `2025` `duplicate/umbrella` rows that intentionally stay non-standalone
- `2025` `retired/legacy-only` rows that intentionally stay explicit
  exclusions
- bounded route, binding, backend-resolution, or tolerance-only claim surfaces
  that should not be overstated as unconditional conformance

Use this rule:

- if leadership wants the current honest bounded-closeout posture, preserve
  those owner readings and keep the linked companions synchronized
- if leadership wants a stronger all-covered or broader compatibility claim,
  fund narrower direct executable proof and update the owner docs, ledgers, and
  exports together

## Finish rule

Do not treat this as done until each remaining row has one of these outcomes:

1. a positive test that proves the claimed behavior
2. a negative test that proves the unsupported boundary
3. an explicit supported-subset row that is documented and traceable

If a row cannot be finished without changing scope, keep the broad row partial
and document the narrower behavior rather than inflating the claim.

For `2010`, the bounded-family tightening decisions now live in
[`2010_python_rti_bounded_family_execution_worklist.md`](2010_python_rti_bounded_family_execution_worklist.md).
For `2025`, the umbrella-row tightening decisions now live in
[`2025_python_rti_umbrella_decomposition_worklist.md`](2025_python_rti_umbrella_decomposition_worklist.md).

## Ownership Rule

Use the shard-versus-view model from
[`requirements_remaining_closure.md`](requirements_remaining_closure.md):

- `shards` own executable pass or fail proof
- `views` collect overlapping closeout, backend, or audit cuts
- every requirement status change should name the narrowest owning shard first
- presentation exports and broad closeout views must not replace canonical
  owner ledgers
- when a bucket has both a human-facing owner doc and a source or
  backend-resolution companion artifact, keep both explicit and update both
  together
- backend support must stay in separate resolution columns or companion
  artifacts instead of being compressed into one status field

Practical owner rule:

- owner docs explain the bounded or still-open claim honestly
- owner companions carry canonical row status, backend-resolution detail, or
  grouped-to-row-level synchronization
- spreadsheet packets stay downstream of those sources

## Recommended finish order

1. Start from the generated backlog in `analysis/compliance/vendor_discovery_backlog.*`
2. Open the requirement row in the correct edition surface:
   `requirements/2010/*.csv` for the 2010 standards or
   `requirements/2025/` for the 2025 surface
3. Open the matching owner doc and owner companion pair from
   `requirements_gap_register.md`
4. Add or tighten the exact focused test
5. Update the traceability row, owner companion, and owner doc with the
   evidence anchor
6. Regenerate compliance artifacts
7. Re-read the backlog and confirm the row moved to a defensible state

## Stop condition

For the current honest bounded-closeout program, the requirements work is
finished when:

- no active closeout buckets remain due to missing ownership, missing links, or
  stale grouped `planned` inventory
- every maintained bounded class has a canonical owner doc plus companion
  artifact and an explicit rerun surface
- every stronger-than-supported broad claim has either been narrowed honestly
  or replaced by direct executable proof

For a stronger all-covered or compatibility-expansion program, more work
remains until the maintained bounded classes themselves are converted into
narrower direct claims.
