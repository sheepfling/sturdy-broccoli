# Requirements Verification Flow

Use this rule when writing or reviewing requirement verification:

`requirements -> traceability row -> live shard/test evidence -> code/runtime surface`

Do not reverse that flow into:

`requirements -> plans/worklists/finish-line prose -> test`

## Canonical Truth Sources

Use these as the source of truth for requirement verification:

1. one canonical requirement catalog per edition:
   - `requirements/2010/canonical_requirements.json`
   - `requirements/2025/canonical_requirements.json`
2. one backend-resolution companion per edition when backend divergence matters:
   - `requirements/2010/backend_resolution.json`
   - `requirements/2025/backend_resolution.json`
3. bounded proof notes that name the exact requirement family and boundary
4. live executable evidence:
   - pytest anchors
   - shard commands
   - route evidence artifacts
   - runtime/package/code paths

Old requirement ledgers, worklists, and reconciliation CSVs are no longer
requirement truth sources. They may remain as generated projections,
compatibility artifacts, or historical bridges, but requirement verification
should resolve through the canonical edition catalog first.

Management and sequencing docs are not truth sources for requirement status:

- `docs/plans/*`
- closeout audits
- worklists
- finish-line prose
- denominator programs

Those documents may summarize the state of the repo, but they do not prove a
requirement.

## What Requirement Tests Should Check

Good requirement tests:

- verify that a requirement row maps to live pytest anchors
- verify that claimed evidence files exist
- verify that a route row keeps backend ownership and boundary fields honest
- verify that blocker rows remain classified as boundary-only when they do not
  count against runtime completeness
- verify that a shard or command named by the requirement surface is real

Bad requirement tests:

- asserting that a plan says a bucket is closed
- asserting that a worklist still lists the same rows
- asserting that a finish-line narrative still contains favored prose
- asserting that a checked-in generated markdown packet matches a writer byte
  for byte as part of requirement verification
- asserting that a README preserves date-stamped re-audit language

## Test Placement Rule

Place tests according to what they verify:

- `tests/requirements/*`
  - requirement rows
  - traceability mappings
  - bounded proof boundaries
  - live evidence anchors and route ownership
- `tests/verification/*`
  - generator structure
  - packet export shape
  - matrix/disposition invariants
- tool or artifact regeneration checks
  - should not gate requirement truth unless they validate live evidence
    mapping rather than checked-in prose

## Review Rule

When a requirement status changes:

1. update the requirement or harmonization row
2. update the owning proof note only if the claim boundary changed
3. add or tighten the executable test or shard evidence
4. point the row to that live evidence
5. update plans or worklists only as downstream reporting

If a proposed test would still pass after deleting `docs/plans/*`, it is
probably verifying the right thing.
