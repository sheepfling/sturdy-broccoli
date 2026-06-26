# Requirements Finish Line

This note is the handoff point for the requirements program in this repo.

Use it when you return later and want the shortest route back to a clean,
honest finish.

For the concrete remaining `2010` and `2025` closeout buckets, use
[`requirements_remaining_closure.md`](requirements_remaining_closure.md).

## What is already in place

- a harmonized `2010` requirements catalog in `requirements/2010/*.csv`
- a bounded `2025` requirements surface in `requirements/2025/`
- generated compliance artifacts under `analysis/compliance/`
- requirement-to-test traceability
- vendor and backend discovery artifacts
- explicit broad-spec versus supported-subset policy language
- an honest-test rule that prevents overclaiming mapped rows

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

## Recommended finish order

1. Start from the generated backlog in `analysis/compliance/vendor_discovery_backlog.*`
2. Open the requirement row in the correct edition surface:
   `requirements/2010/*.csv` for the 2010 standards or
   `requirements/2025/` for the 2025 surface
3. Add or tighten the exact focused test
4. Update the traceability row with the evidence anchor
5. Regenerate compliance artifacts
6. Re-read the backlog and confirm the row moved to a defensible state

## Stop condition

The requirements work is finished when the remaining backlog is reduced to:

- explicit planned work that is intentionally out of scope, or
- partial rows whose narrower scope is fully documented and tested

Anything else means the requirements catalog still contains claims that are too
strong for the evidence we have.
