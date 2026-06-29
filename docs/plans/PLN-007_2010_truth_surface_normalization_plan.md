# PLN-007 2010 Truth Surface Normalization Plan

## Purpose

Normalize the `2010 / 1516e` requirements-facing machine-readable surfaces so
the repo has one canonical requirement list, one canonical backend-resolution
companion, and a clear demotion path for the older reconciliation, bridge,
matrix, and packet-derived CSV drift that currently reads too much like peer
truth.

This plan is about execution to completion. It defines how to move the current
mixed `2010` requirement corpus from a mature but heterogeneous reconciliation
surface into one tighter canonical surface comparable to the current `2025`
discipline.

## Goal Statement

Bring the `2010 / 1516e` requirement surface to a single-source normalized
state by reducing `requirements/2010/canonical_requirements.{json,csv}` to one
leaf-oriented canonical requirement list, keeping
`requirements/2010/backend_resolution.{json,csv}` as the only backend-specific
companion truth, and demoting every remaining legacy matrix, clause bridge,
reconciliation, and closeout packet into explicitly generated projection,
mapping-bridge, import-history, or owner-note status so no old drift surface
can be mistaken for canonical requirement truth.

## Why This Plan Exists

The repo now has the right structure for `2025`:

- one canonical requirement catalog
- one canonical backend-resolution catalog
- generated grouped and export projections downstream

The `2010` side is closer than it used to be, but it still mixes multiple
concepts inside the canonical denominator:

- extracted requirement rows
- service decomposition rows
- verification slice rows
- area or section rollup rows
- clause bridge and imported-packet reconciliation artifacts

That mixture makes counts harder to compare, lets older surfaces keep reading
like requirement truth, and keeps exports and audits tied to older bridges
longer than necessary.

## Non-Goals

This plan does not require:

1. deleting every historical `2010` CSV immediately
2. rewriting the imported packet archive
3. changing honest requirement judgments just to make counts look better
4. forcing backend-resolution facts back into canonical status
5. pretending every existing `2010` bridge row should survive as a canonical
   requirement row

## Desired End State

At completion, the `2010` source side should have:

1. one canonical requirement truth surface:
   - `requirements/2010/canonical_requirements.json`
   - `requirements/2010/canonical_requirements.csv`
2. one canonical backend-resolution truth surface:
   - `requirements/2010/backend_resolution.json`
   - `requirements/2010/backend_resolution.csv`
3. one explicit classification for every other requirements-facing artifact:
   - `projection`
   - `mapping-bridge`
   - `import-history`
   - `owner-note`
4. no manager-facing export, verification rule, or closeout doc that treats an
   older matrix or bridge file as peer truth
5. a leaf-row denominator that can be explained honestly and compared to
   `2025` without mixing rollups into requirement counts

## Current Drift To Remove

The current `2010` canonical catalog still carries multiple semantic row
classes together:

- `extracted-requirement`
- `service-requirement`
- `verification-slice`
- `omt-area`
- `section-area`

The normalization rule for this plan is:

- canonical requirement truth should be leaf claims only
- backend-resolution truth should be a companion surface keyed to canonical
  requirement rows
- verification slices, area rows, section rows, and other rollups should live
  outside the canonical denominator

The core question to answer row by row is:

- is this row a defended requirement claim?
- or is it a bridge, grouping, decomposition aid, or review packet?

Only the first category belongs in canonical truth.

## Canonical 2010 Row Rule

The normalized `2010` canonical catalog should keep only rows that represent
one requirement-level claim the repo is defending.

Each canonical row must resolve to:

- one stable `requirement_id`
- one `source_document`
- one `clause`
- one `requirement_text` or equivalent leaf claim text
- one `canonical_status`
- one `owner_doc`
- one `primary_test_shard`
- one `primary_command`
- concrete `evidence_refs`
- one honest `boundary_note` when the claim is narrower than the standard text

Rows that fail this rule should move out of canonical truth unless they can be
rewritten into a narrower leaf claim.

## Artifact Classification Rule

Every `2010` requirements-facing CSV or JSON should end in exactly one class:

### Canonical

The repo-owned requirement truth or backend-resolution truth.

Allowed:

- `canonical_requirements.{json,csv}`
- `backend_resolution.{json,csv}`

### Mapping-Bridge

Files that map imported packet rows or clause decompositions onto canonical
rows.

Examples:

- detailed reconciliation ledgers
- clause bridge CSVs

### Projection

Files generated downstream for rollup, export, grouped review, or historical
inspection.

Examples:

- `traceability_matrix.csv`
- special narrowed backend ledgers
- manager-facing export packets

### Import-History

Versioned imported packet material that should remain auditable but never act
as the live truth surface.

### Owner-Note

Human-facing bounded-family docs that explain how to read a claim surface
honestly without pretending they are the row owner data themselves.

## Workstreams

### Workstream 1: 2010 Artifact Survey And Taxonomy Lock

Create a definitive inventory of all `2010` requirements-facing machine-readable
artifacts and classify them.

Deliverables:

1. a complete `2010` artifact inventory in the normalized survey output
2. a per-file class for canonical, mapping-bridge, projection, or
   import-history
3. a short reader-facing explanation in the `2010` front-door docs

Exit condition:

- every `2010` CSV or JSON that looks requirements-facing has a locked class

### Workstream 2: Canonical Row-Kind Triage

Take the current `2010` canonical rows and sort them into:

1. `keep_in_canonical`
2. `move_to_projection`
3. `needs_manual_decision`

Rules:

- `verification-slice`, `omt-area`, and `section-area` rows should not survive
  in the canonical denominator
- `service-requirement` rows must be reviewed individually to determine
  whether they are true leaf claims or decomposition helpers
- `extracted-requirement` rows remain canonical unless they are discovered to
  be parent rollups masquerading as leaf rows

Deliverables:

1. machine-readable classification output for all current `2010` canonical rows
2. a tracked exception list for manual decisions

Exit condition:

- every current `2010` canonical row has an explicit disposition

### Workstream 3: Leaf-Only Canonical Generator

Refactor the `2010` canonical generator so it emits only the approved
leaf-oriented canonical rows.

Deliverables:

1. a revised `2010` canonical generator path
2. regenerated `canonical_requirements.{json,csv}`
3. updated row counts and row-kind counts
4. tests that fail if demoted row kinds return to canonical truth

Exit condition:

- the `2010` canonical catalog is leaf-oriented and free of rollup-only row
  kinds

### Workstream 4: Backend-Resolution Companion Tightening

Make the `2010` backend-resolution surface a strict companion to canonical
rows.

Rules:

- every backend-resolution row must resolve to a canonical requirement row
- special ledgers such as priority or mixed-backend packets become generated
  projections, not peer truth
- exports and docs should prefer `backend_resolution.{json,csv}` first

Deliverables:

1. a canonical-keyed backend-resolution catalog
2. projection-only status for narrower special backend ledgers
3. tests that prevent special ledgers from re-entering the truth chain

Exit condition:

- `backend_resolution.{json,csv}` is the only `2010` backend truth surface

### Workstream 5: Legacy Projection Demotion

Demote older `2010` drift surfaces so they stay useful without reading as
truth.

Targets include:

- `traceability_matrix.csv`
- `hla1516_1_priority_backend_resolution.csv`
- clause and family reconciliation CSVs
- imported master harmonization views when used in closeout docs

Deliverables:

1. doc wording that calls these files projections or mapping-bridges
2. loader or generator updates so they are produced from canonical truth where
   practical
3. verification guardrails banning them from requirement-truth claims

Exit condition:

- no front-door doc or requirement test treats legacy projections as peer
  truth

### Workstream 6: Export And Verification Cutover

Switch boss-facing exports, closeout summaries, and verification tests onto the
normalized `2010` canonical leaf surface.

Deliverables:

1. spreadsheet and packet generators that read canonical surfaces first
2. updated denominator and summary wording
3. removal of stale count assumptions tied to mixed row kinds
4. repo-green verification for the normalized `2010` truth flow

Exit condition:

- manager-facing outputs and repo verification agree on the same `2010`
  canonical denominator

## Acceptance Gates

The plan is complete only when all of these are true:

1. `requirements/2010/canonical_requirements.{json,csv}` contain no
   rollup-only row kinds
2. `requirements/2010/backend_resolution.{json,csv}` are the only backend
   truth surfaces referenced as canonical
3. `traceability_matrix.csv` and special backend ledgers are documented and
   tested as downstream projections only
4. every `2010` requirement-facing export uses the normalized canonical
   surfaces as primary inputs
5. row-count explanations for `2010` no longer depend on mixed leaf plus
   rollup semantics
6. the `2010` front-door docs are simple enough that a new reader can identify
   the owner surfaces without opening historical bridges first

## Completion Checklist

Use this list when deciding whether the work is actually done:

1. classify every `2010` requirements artifact
2. classify every current `2010` canonical row as keep, move, or manual
3. rebuild the `2010` canonical generator around leaf-only rules
4. rebuild the `2010` backend-resolution generator around canonical row keys
5. demote legacy `2010` drift surfaces in docs and tests
6. cut over exports and closeout views
7. rerun repo-green verification for the affected requirement, export, and
   verification lanes

## Practical First Move

The first executable slice should be:

1. generate a machine-readable `2010` row triage artifact from the current
   canonical catalog
2. lock the allowed canonical row kinds
3. produce the first candidate leaf-only `2010` canonical export

That creates the hard cut list before any denominator or export claims change.
