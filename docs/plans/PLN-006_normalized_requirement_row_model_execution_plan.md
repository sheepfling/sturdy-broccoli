# PLN-006 Normalized Requirement Row Model Execution Plan

## Purpose

Replace the current pattern of repeated CSV-by-CSV normalization with one
shared typed requirements model that both `2010 / 1516e` and
`2025 / 1516_2025` can project into stable ledgers, traceability packets,
backend-resolution views, and spreadsheet exports.

This plan is about execution, not just schema discussion. It defines the
delivery order, migration boundaries, and acceptance gates needed to move the
repo from ad hoc row-shape repair to one standard requirements data model.

## Goal Statement

Establish one canonical typed requirements data model for both `2010` and
`2025` such that requirement status, backend resolution, shard ownership,
owner documents, and evidence traceability are represented through shared
validated row types, legacy CSV and JSON artifacts become generated or
validated projections of that model, and requirement tests stop re-inventing
per-file normalization logic.

## Why This Plan Exists

The current repo already has the right conceptual split in many places:

- imported source packets
- repo-native harmonized requirement rows
- backend-resolution companion surfaces
- executable verification rows
- generated export packets

The problem is that those concepts are still expressed through too many
slightly different CSV shapes and too much test-local normalization logic.

The main execution risks are:

1. the same concept appears under different column names in different files
2. tests normalize raw CSV cells differently from export scripts
3. `status`-like fields drift toward mixing canonical closure and backend
   support
4. new requirement surfaces copy an existing CSV shape instead of a standard
   typed model
5. boss-facing exports can diverge from the actual repo-owned truth surface

## Non-Goals

This plan does not require:

1. deleting every existing CSV immediately
2. collapsing all requirement artifacts into one giant spreadsheet
3. replacing every historical intake packet with repo-native JSON
4. forcing backend-resolution artifacts into the canonical requirement row
5. changing canonical requirement judgments just because the storage format
   changes

## Canonical Model

The normalized program should use a small set of shared row families rather
than many unrelated CSV shapes.

### 1. Canonical Requirement Row

This is the primary row whose claim the repo is defending.

Required fields:

- `edition`
- `requirement_id`
- `source_document`
- `clause`
- `page`
- `area`
- `service_group`
- `service_or_check`
- `requirement_text`
- `normative_level`
- `row_kind`
- `parent_requirement_id`
- `canonical_status`
- `canonical_status_reason`
- `owner_doc`
- `primary_test_shard`
- `primary_command`
- `evidence_refs`
- `boundary_note`
- `source_trace_strength`
- `repo_evidence_status`
- `tags`

### 2. Requirement Mapping Row

This row maps imported or source-side requirements into repo-native canonical
rows.

Required fields:

- `edition`
- `source_requirement_id`
- `canonical_requirement_id`
- `mapping_kind`
- `mapping_notes`
- `source_packet_file`
- `owner_doc`
- `evidence_refs`

### 3. Backend Resolution Row

This row expresses backend- or route-specific support without changing the
canonical requirement judgment.

Required fields:

- `edition`
- `canonical_requirement_id`
- `backend_id`
- `route_id`
- `resolution_status`
- `resolution_kind`
- `owner_doc`
- `primary_test_shard`
- `primary_command`
- `evidence_refs`
- `scope_note`

### 4. Executable Verification Row

This row ties canonical requirements to runnable or generated verification
surfaces.

Required fields:

- `edition`
- `verification_id`
- `canonical_requirement_id`
- `test_kind`
- `test_level`
- `pytest_candidate`
- `cli_candidate`
- `scenario`
- `route_targets`
- `expected_result`
- `evidence_artifact`
- `implementation_target`
- `status`

### 5. Grouped View Row

This row exists only for generated grouped worklists, exports, and manager
packets.

Required fields:

- `edition`
- `group_id`
- `area`
- `service_group`
- `canonical_disposition_summary`
- `row_count`
- `owner_doc`
- `primary_test_shard`
- `backend_resolution_refs`
- `acceptance_gate`

Rule:

- grouped rows are projections
- they are not the canonical requirement truth surface

## Execution Principles

The migration must preserve the current proof rules.

### Principle 1: Canonical Status Is Separate

Never store backend support inside canonical requirement status.

### Principle 2: Owner And Shard Are Mandatory

Every canonical requirement row must resolve to:

- one owner doc
- one narrowest primary shard

### Principle 3: Legacy Files Can Survive Temporarily

Legacy CSV and JSON files may remain in place during migration, but they
should become either:

- validated inputs
- generated projections

not independently edited truth surfaces.

### Principle 4: Tests Must Consume Shared Models

Tests should stop normalizing raw `DictReader` rows ad hoc when a shared row
loader can do that once.

### Principle 5: 2010 And 2025 Share The Model

The two editions may keep different projections, but they should not require
different concepts for:

- canonical requirement identity
- backend resolution
- shard ownership
- evidence traceability

## Workstreams

### Workstream 1: Survey And Taxonomy Lock

Create an explicit inventory of current requirement artifact shapes and map
each file into one normalized row family.

Deliverables:

1. a survey script that inspects current CSV and JSON requirement artifacts
2. a machine-readable mapping from existing file to normalized row family
3. a short reader-facing doc that records the canonical row families

Exit condition:

- every current requirements artifact is classified as canonical, mapping,
  backend-resolution, executable-verification, grouped-view, or historical

### Workstream 2: Shared Typed Model Module

Introduce one shared Python module for requirement row types, validation, and
loading.

Deliverables:

1. shared dataclasses or validated model classes
2. enums or constants for canonical statuses, row kinds, and shard IDs
3. parsing helpers for lists, tags, commands, and evidence references
4. validation errors that fail loudly on column drift

Preferred location:

- `hla/verification/repo_internal/requirements/models.py`
- `hla/verification/repo_internal/requirements/loaders.py`

Exit condition:

- tests and scripts can load typed rows from at least one 2010 artifact and
  one 2025 artifact without per-call custom normalization

### Workstream 3: Canonical Normalized Exports

Generate one normalized canonical artifact per edition from the shared model.

Deliverables:

1. `requirements/2010/canonical_requirements.json`
2. `requirements/2025/canonical_requirements.json`
3. optional CSV projections if operator workflows still benefit from them

Rules:

1. JSON should be the primary normalized artifact because it carries list-like
   fields cleanly
2. CSV may remain as a presentation or compatibility projection

Exit condition:

- both editions have one edition-level normalized artifact that can drive
  tests and exports

### Workstream 4: Projection Generators

Refactor generation scripts so spreadsheet exports, grouped worklists, and
traceability packets are produced from shared typed rows rather than edition-
specific ad hoc reshaping.

Targets:

- `scripts/generate_requirement_compliance_spreadsheets.py`
- 2025 traceability generation
- compliance rollup generators
- grouped worklist or closeout export generators

Exit condition:

- the main export scripts read shared typed rows or normalized canonical JSON,
  not raw ledger-specific CSV assumptions

### Workstream 5: Test Harness Normalization

Move requirement verification tests to shared row loaders and shared invariant
checks.

Deliverables:

1. shared test helpers for canonical rows and backend-resolution rows
2. edition-specific tests that verify content, not raw shape accidents
3. guardrails that stop new requirement tests from becoming CSV-shape police

Exit condition:

- the majority of requirement tests no longer parse raw CSVs directly

### Workstream 6: 2010 Migration

Normalize the 2010 requirement surface first where multiple detailed
reconciliation files currently encode the same concepts with minor field
differences.

Priority targets:

1. detailed reconciliation files
2. traceability matrix
3. backend-resolution file
4. compliance spreadsheet export inputs

Exit condition:

- the 2010 closeout and export path can be explained from shared typed rows
  without bespoke per-family normalization rules

### Workstream 7: 2025 Migration

Normalize the 2025 surface second, especially where the row ledger, grouped
worklist, traceability matrix, executable tests, and backend-resolution
companions overlap.

Priority targets:

1. disposition ledger
2. grouped harmonization worklist
3. traceability matrix JSON
4. Pitch proto HLA 4 / `202X` backend-resolution companions
5. executable test requirement rows

Exit condition:

- the 2025 closeout and export path can be generated from the same shared row
  concepts used by the 2010 surface

### Workstream 8: Documentation And Operator Flow

Update the reader-facing docs so they point to the normalized truth model.

Targets:

- `docs/verification/requirements_structure_packet.md`
- `docs/verification/requirements_verification_flow.md`
- edition requirement READMEs
- export docs and spreadsheet handoff docs

Exit condition:

- a reader can follow one coherent path from source requirement to canonical
  row to owner doc to shard to backend-resolution companion to export

## Delivery Order

Use this order:

1. survey and taxonomy lock
2. shared typed model module
3. normalized canonical JSON export for one edition
4. shared test helpers and one migrated test slice
5. spreadsheet export generator migration
6. 2010 migration completion
7. 2025 migration completion
8. docs and operator-path cleanup

This order keeps risk low because:

- the repo gains a typed core before broad artifact rewrites
- tests start benefiting early
- exports switch after the underlying canonical model exists

## Acceptance Gates

This plan is complete only when all of the following are true:

1. both editions load through shared typed row models
2. canonical requirement rows carry owner doc, primary shard, and evidence
   traceability consistently
3. backend resolution is stored separately from canonical status
4. spreadsheet exports and grouped worklists are generated from normalized
   rows
5. requirement tests primarily use shared loaders instead of raw `DictReader`
   parsing
6. docs explain the normalized model clearly enough for a new engineer to
   follow

## Initial Tactical Slice

The first implementation slice should be intentionally small:

1. add the shared row-model module
2. add a survey script that classifies current requirement artifacts
3. generate one normalized canonical JSON for `2025`
4. move one export script and one requirement test file onto the shared model

Reason:

- `2025` already has a strong row-ledger center of gravity
- that lets the repo prove the model on one edition before finishing `2010`
  bridge migration

## Related Docs

- `docs/verification/requirements_structure_packet.md`
- `docs/verification/requirements_verification_flow.md`
- `docs/plans/PLN-005_requirements_shards_views_and_verification_plan.md`
- `docs/verification/requirement_compliance_exports.md`
