# PLN-005 Requirements Shards, Views, and Verification Plan

## Purpose

Turn the current closeout guidance into a stable execution model that is easy
to run, easy to audit, and hard to misread.

This plan covers three connected problems:

1. shard ownership for runnable proof
2. view ownership for overlapping audit and reporting slices
3. requirement and backend-resolution surfaces that must stay separate

The intent is to make requirement closure, repo-green, and manager-facing
reporting all agree without overloading one table or one status field.

## Goal Statement

Establish one canonical requirements verification model for `2010 / 1516e` and
`2025 / 1516_2025` in which every requirement row and every grouped closeout
surface points to a stable runnable shard, every overlapping audit slice is
published as a view rather than a second ownership model, backend divergence is
kept in explicit backend-resolution columns or companion artifacts, and the
full documentation flow from top-level README to owner docs to commands to
exports is simple enough for a new engineer to follow without guessing.

## Why This Plan Exists

The repo has already improved the closeout surface, but several risks still
need a formal operating model:

- juniors can still confuse a view with a runnable shard
- closeout tables can still drift back toward one ambiguous `status` field
- backend support can still be accidentally merged into canonical requirement
  closure
- repo-green can become unclear if overlapping slices are treated as equal CI
  owners
- boss-facing spreadsheet packets can look more precise than the underlying
  owner model if the denominator and backend columns are not explicit

## Canonical Model

### Shards

`Shards` are the independent runnable proof units.

Rules:

1. every shard has a stable command
2. every shard has a pass/fail meaning
3. every shard is allowed to own canonical requirement proof
4. shards may share tests or code, but their execution contract must remain
   independently understandable
5. CI and repo-green are defined in terms of shards, not views

### Views

`Views` are overlapping reporting or audit slices.

Rules:

1. views may overlap freely
2. views may aggregate multiple shards
3. views may answer audit questions such as `ownership`, `transport`,
   `setup-preflight`, `save-restore`, `fom-omt`, or `finish-line`
4. views must never replace shard ownership
5. views may be convenient rerun surfaces, but they are not the canonical
   proof primitive

### Requirement Status Versus Backend Resolution

These are separate concepts and must stay separate everywhere.

Rules:

1. canonical requirement status answers whether the requirement claim is closed
2. backend resolution answers which backend actually supports that claim and at
   what scope
3. do not compress both concepts into one `status`-like field
4. if `python` supports a row and `Pitch`, `CERTI`, or a binding lane does
   not, say that directly in backend-specific columns or companion artifacts
5. if all backends agree, that agreement may still be recorded explicitly

## Deliverables

This plan is complete only when all of these exist and agree:

1. a canonical shard inventory with stable names, commands, and CI ownership
2. a canonical view inventory with explicit overlap semantics
3. top-level testing docs that explain:
   - all lanes
   - all shards
   - all major views
   - which ones gate repo-green
4. requirement closeout tables that use:
   - canonical status columns
   - separate backend-resolution columns or linked backend-resolution artifacts
5. requirement owner docs for both editions that point to the right shard or
   view without ambiguity
6. spreadsheet exports that preserve the same separation of:
   - requirement disposition
   - backend resolution
   - denominator
7. restart and junior runbooks that use the same shard aliases and names as
   the top-level testing docs

## Workstreams

### Workstream 1: Canonical Shard Registry

Define and maintain a single shard registry that answers:

- shard name
- purpose
- owner command
- CI lane or test shard
- edition coverage
- backend coverage
- whether the shard is repo-green gating

Exit condition:

- a junior engineer can pick a shard from docs and run it without needing to
  infer a hidden alias or search the repo

### Workstream 2: Canonical View Registry

Define and maintain a single view registry that answers:

- view name
- question the view answers
- underlying shards
- overlapping tags
- whether the view is only diagnostic or also a convenient aggregate runner

Exit condition:

- no documentation surface treats a view as if it were the canonical proof
  owner

### Workstream 3: Top-Level Testing Flow

Upgrade the testing front door so it clearly explains:

- the full matrix of lanes
- which lanes are editions versus transports versus bindings versus tooling
- which units are shards
- which units are views
- which ones are independent
- which ones overlap intentionally
- which ones gate repository green

Exit condition:

- a new reader can start at the top-level testing page and navigate down to the
  exact command they need

### Workstream 4: Requirements Verification Flow

Upgrade the top-level requirements surfaces so they clearly explain:

- the verification reading order
- where `2010` ownership lives
- where `2025` ownership lives
- where backend divergence lives
- where spreadsheet exports come from
- how denominators are defined for manager-facing percentages

Exit condition:

- a reader can start from the top-level requirements surface and follow a
  single coherent chain to owner docs, ledgers, commands, and exports

### Workstream 5: Closeout Table Normalization

Propagate the split between requirement closure and backend resolution into any
remaining tables that still mix the two concepts.

Preferred column shape:

| Column | Meaning |
| --- | --- |
| `Edition` | `2010` or `2025` |
| `Requirement family` | clause, grouped bucket, or owner family |
| `Requirement IDs` | exact IDs or grouped identifiers |
| `Canonical status` | `planned`, `partial`, `mapped`, `covered`, `duplicate/umbrella`, or `retired/legacy-only` |
| `Primary shard` | owning runnable proof unit |
| `View tags` | overlapping audit slices |
| `Backend resolution` | explicit backend columns or linked backend artifact |
| `Primary command` | stable operator command |
| `Evidence artifact` | owner doc, ledger, JSON, CSV, or generated packet |
| `Notes / boundary` | honest scope note |

Exit condition:

- remaining closeout tables no longer rely on one overloaded status-like field

### Workstream 6: CI and Repo-Green Alignment

Make the CI shape match the documentation model.

Rules:

1. shards should be independently runnable
2. repo-green should be explainable as a set of shard gates
3. views may aggregate shards for convenience, but should not obscure the
   canonical shard gates
4. tooling, environment verification, Java shim checks, C++ shim checks, and
   transport checks should each land in an intentional shard or shard family

Exit condition:

- the docs and CI tell the same story about what must pass and why

## Edition-Specific Focus

### 2025 / 1516_2025

Priorities:

1. keep the `691` tracked-row audit, the `645` active normative denominator,
   and backend-resolution surfaces mutually consistent
2. keep framework umbrella rows and callback/binding umbrella rows explicit as
   non-standalone requirement rows unless and until they are intentionally
   decomposed
3. keep `Pitch` proto HLA 4 / `202X`, hosted FedPro, and Java/C++ binding
   results in explicit backend-resolution lanes rather than in canonical status
4. keep grouped worklists and row-level ledgers linked, but not conflated

### 2010 / 1516e

Priorities:

1. keep bounded family notes, mixed-backend priority rows, and partial-family
   owner docs easy to scan and easy to verify later
2. keep Python RTI proof separate from vendor/backend divergence
3. make it obvious which `2010` surfaces are maintained bounded-owner notes
   versus active executable proof lanes
4. preserve the same shard versus view model used for `2025`

## Naming Rules

Use one naming rule set everywhere:

1. shard names must be stable and reused in:
   - top-level testing docs
   - restart docs
   - junior runbooks
   - CI documentation
2. view names must be stable and clearly labeled as views
3. backend-resolution fields must use explicit backend names such as:
   - `python`
   - `pitch`
   - `certi`
   - `portico`
   - `java_cpp_binding`
   - `hosted_fedpro`
   - `pitch_202x`
4. `Pitch` proto HLA 4 / `202X` naming must stay consistent between docs,
   generated artifacts, and export sheets

## Execution Order

1. finish the top-level testing matrix and shard-versus-view documentation
2. normalize any remaining closeout tables that still mix requirement status
   and backend resolution
3. add or tighten shard and view references in the `2010` and `2025` owner
   docs
4. confirm restart docs and junior runbooks use the same aliases and names
5. confirm CI shard names, documentation, and repo-green explanations align
6. regenerate spreadsheet handoff packets once the source docs and ledgers are
   stable

## Non-Goals

This plan does not, by itself:

- claim full cross-vendor conformance
- convert all bounded rows into direct covered rows
- make every view a separate CI requirement
- replace the canonical owner ledgers with spreadsheet packets

## Completion Criteria

This plan is complete when:

1. the top-level testing and requirements front doors explain shards, views,
   backend resolution, and verification flow clearly
2. both editions use the same conceptual model
3. the main closeout and audit tables keep requirement closure separate from
   backend support
4. restart and junior docs use the same runnable names as the top-level docs
5. repo-green can be described as a stable shard set rather than a collection
   of loosely defined overlapping slices

