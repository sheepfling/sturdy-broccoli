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

## What still needs to happen

Finish the remaining requirement work by closing the rows that still fall into
one of these buckets:

- `planned` rows with no executable proof yet
- `partial` rows that are intentionally narrower than the standard wording
- vendor-divergent rows that need an explicit supported-boundary test

## Finish rule

Do not treat this as done until each remaining row has one of these outcomes:

1. a positive test that proves the claimed behavior
2. a negative test that proves the unsupported boundary
3. an explicit supported-subset row that is documented and traceable

If a row cannot be finished without changing scope, keep the broad row partial
and document the narrower behavior rather than inflating the claim.

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

The requirements work is finished when the remaining backlog is reduced to:

- explicit planned work that is intentionally out of scope, or
- partial rows whose narrower scope is fully documented and tested

Anything else means the requirements catalog still contains claims that are too
strong for the evidence we have.
