# FOM UI Polish Plan

This document is the execution plan for turning the current FOM workbench from
"capable operator console" into a polished application experience. The target
is not feature growth. The target is a calmer, clearer, more trustworthy UI
with fewer competing surfaces and stronger task flow.

Minimal and well-tested is the standard. Less is better than more.

## Objective

The polish pass is complete when the workbench feels like one intentional
application instead of a generated report with tools attached.

An operator should be able to:

1. understand the current selection in one scan
2. see the most important problem immediately
3. move into the right workspace without hunting
4. keep context while switching between investigation, comparison, and repair
5. act without reading raw command blocks first

## Product Standard

The standard for this pass is "awesome as a polished application experience."
In concrete terms, that means:

1. calm visual hierarchy
2. one dominant task surface at a time
3. explicit next action
4. minimal but complete controls
5. no noisy duplication
6. no obvious "generated HTML" feel

## Scope

In scope:

- layout recomposition
- information hierarchy
- action-first interaction
- persistent investigation context
- browser-level ergonomics
- focused UI regression coverage

Out of scope:

- browser-side XML parsing
- replacing Python-generated truth with client-side logic
- broad new feature families unrelated to the operator path
- speculative collaboration features
- heavy visual ornament

## Non-Negotiable Rules

1. The page stays snapshot-driven. No browser-side XML parsing.
2. Python remains the source of truth for merge, validation, and repair data.
3. The UI must privilege one active workspace over many simultaneous panels.
4. Commands remain available, but they are secondary to direct actions.
5. Repo-owned versus third-party boundaries must stay explicit.
6. Empty states, blocked states, and warning states must explain the next step.
7. New UI complexity must justify itself. If a control does not improve the
   operator path, it should not exist.

## Baseline

The workbench already provides:

- catalog and filters
- saved browser load sets and import/export
- inspect, diff, conflict, validation, and repair surfaces
- hierarchy-aware symbol drill-down
- symbol jump paths across major surfaces
- guarded repo-owned repair previews for supported cases
- copyable command blocks
- focused workbench and broader FOM test coverage

The gap is product quality, not missing core capability.

## Core UX Direction

The UI should shift from "many panes visible at once" to "one active workspace
with supporting context."

### Target Layout

1. Left rail:
   - catalog
   - lightweight filters
   - custom load set builder
2. Center:
   - persistent selection summary
   - one active workspace mode
3. Right rail:
   - symbol investigation
   - search
   - active context

### Target Workspace Modes

The center surface should expose a small explicit mode set:

- `Overview`
- `Conflict`
- `Validation`
- `Diff`
- `Repair`

Only one is active at a time. Selection and symbol context persist while the
operator moves between them.

### Target Interaction Model

The UI should guide the main path:

1. select a family or load set
2. assess status
3. investigate symbol or issue
4. compare or validate
5. repair or regenerate

Commands support reproducibility, but they should not dominate the workflow.

## Work Plan

Implement the polish pass in this order.

### Phase 1: Workflow Recomposition

Goal:

- make the app read as one guided tool instead of adjacent capability panes

Tasks:

1. Create a persistent selection summary at the top of the main workspace.
2. Introduce explicit workspace mode tabs or segmented controls.
3. Recompose the center column so only one workspace is active at a time.
4. Pin active symbol and active investigation context outside the mode panes.
5. Auto-suggest a useful default mode from the selected item state.
6. Keep catalog selection, search focus, and symbol focus stable across mode
   changes.

Do not add:

- extra global navigation
- extra status banners
- duplicate summaries in multiple panes

Acceptance criteria:

1. the operator can identify current selection, current state, and next action
   without scanning the entire page
2. mode changes preserve selection and symbol context
3. the active workspace is visually dominant

Verification:

- HTML assertions for workspace controls and summary region
- browser tests for mode switching with preserved context

### Phase 2: Information Design And Visual Hierarchy

Goal:

- make summary, evidence, and action visually distinct

Tasks:

1. Turn top-level status into compact summary cards or stat boxes.
2. Strengthen severity treatment for:
   - healthy
   - warning
   - blocked
   - repairable
3. Rework conflict evidence so the important field-level deltas read first.
4. Rework validation sections so issue type, impacted symbol, and next step
   appear before long details.
5. Make diff summaries count-first and list-second.
6. Strengthen visual distinction for:
   - repo-generated families
   - browser-saved load sets
   - repo-owned assets
   - third-party assets
7. Tighten spacing, panel rhythm, and typography so the page feels calmer.

Do not add:

- decorative cards for every section
- large explanatory copy blocks
- excessive color

Acceptance criteria:

1. warning and failure states are obvious within two seconds
2. the operator can distinguish summary, evidence, and action immediately
3. the page no longer reads like a dense report dump

Verification:

- focused HTML assertions for revised labels and summaries
- browser review across desktop and mobile-width layouts

### Phase 3: Action-First Interaction

Goal:

- replace command-first reading with direct action surfaces

Tasks:

1. Add clear primary actions for common operator next steps.
2. Keep commands behind reveal, copy, or secondary action affordances.
3. Restructure validation, diff, and repair sections so actions appear before
   raw command text.
4. Normalize button language so actions use consistent verbs.
5. Make unsupported actions explicit instead of silently absent.

Primary action candidates:

- `Investigate Symbol`
- `Open Validation Report`
- `Compare Against`
- `Prepare Repair`
- `Regenerate`

Acceptance criteria:

1. an operator can progress through common flows without reading raw commands
2. commands remain easy to copy when needed
3. blocked actions explain why they are blocked

Verification:

- browser tests for action controls and command reveal/copy behavior
- focused HTML assertions for action sections

### Phase 4: Richer Investigation State

Goal:

- make the app feel persistent and efficient during a real investigation

Tasks:

1. Keep pinned symbol context visible while the operator changes workspaces.
2. Add a small recent-selection history for quick backtracking.
3. Add recent comparisons if this can be done without visual clutter.
4. Preserve useful expand/collapse state during the active session.
5. Add keyboard navigation for catalog and search if it can be implemented
   cleanly.
6. Add small filter chips only where they clearly reduce navigation time.

Hard constraint:

- this phase must stay restrained; do not turn the workbench into a state-heavy
  browser app

Acceptance criteria:

1. the operator does not lose context during a multi-step investigation
2. repeated inspection flows feel faster, not busier

Verification:

- browser tests for pinned context continuity
- browser tests for any keyboard navigation added

### Phase 5: Final Visual And Interaction Pass

Goal:

- remove the remaining rough edges and make the UI feel finished

Tasks:

1. Rewrite awkward labels, empty states, and helper text.
2. Remove duplicate or low-value wording.
3. Tune spacing, density, and button sizing across desktop and mobile widths.
4. Clean up remaining panel inconsistencies.
5. Review screenshots and fix any clipped, overlapping, or noisy layouts.

Acceptance criteria:

1. the interface feels deliberate and calm
2. there are no obviously awkward or placeholder-like states
3. the product looks internally consistent across supported widths

Verification:

- browser screenshot review
- final focused and broad test gates

## Detailed Sequence

Use this exact order. Do not collapse these into one giant pass.

### Step 1: Shell Recomposition

Files:

- [fom_workbench.py](../../packages/hla-verification/src/hla/verification/repo_internal/fom_workbench.py)
- [test_fom_workbench.py](../../tests/factories/test_fom_workbench.py)
- [test_fom_workbench_browser.py](../../tests/factories/test_fom_workbench_browser.py)

Deliver:

- center-stack workspace shell
- selection summary
- mode controls
- active symbol summary

Exit:

- the app has a stable structure worth refining

### Step 2: Severity And Summary Pass

Deliver:

- stat boxes
- stronger state labels
- cleaner conflict and validation summaries
- improved ownership and provenance visibility

Exit:

- the important information is obvious quickly

### Step 3: Action Pass

Deliver:

- primary action buttons
- secondary command reveal/copy treatment
- clearer blocked-action messaging

Exit:

- common paths are action-led instead of command-led

### Step 4: Investigation Persistence Pass

Deliver:

- pinned context continuity
- recent selection support
- any minimal keyboard support that survives review

Exit:

- multi-step investigation no longer feels stateless

### Step 5: Final Cleanup Pass

Deliver:

- wording cleanup
- spacing cleanup
- screenshot-driven fixes
- final regression pass

Exit:

- the UI feels cohesive and production-like

## PR Plan

Keep the work in narrow PRs with one dominant theme per PR.

### PR 1: Workspace Shell

Scope:

- layout recomposition
- selection summary
- workspace mode plumbing
- pinned active context

Must prove:

- selection and symbol state survive workspace changes

### PR 2: Hierarchy And Severity

Scope:

- status cards
- conflict and validation structure
- diff summary cleanup
- ownership and saved-set distinction

Must prove:

- failure states are visually clearer and easier to scan

### PR 3: Action Surfaces

Scope:

- primary actions
- command reveal/copy refinement
- blocked-action messaging

Must prove:

- common flows can proceed without reading raw commands first

### PR 4: Persistent Investigation State

Scope:

- recent selections
- recent comparisons if justified
- remembered session state
- keyboard support if justified

Must prove:

- added persistence improves speed without adding clutter

### PR 5: Final QA And Cleanup

Scope:

- wording pass
- spacing pass
- screenshot review fixes
- final regression

Must prove:

- the app feels finished rather than assembled

## Test Strategy

This work needs stronger evidence than static HTML generation alone.

### Required Test Gates

Keep these green throughout:

```bash
python3 -m pytest tests/factories/test_fom_workbench.py tests/factories/test_fom_workbench_browser.py -q
python3 -m pytest tests/factories/test_fom_validate.py tests/factories/test_fom_workbench.py tests/factories/test_fom_workbench_browser.py -q
python3 -m pytest tests/factories/test_fom_*.py -q
```

### Browser Checks To Add Or Tighten

1. workspace mode switching preserves selected family or load set
2. workspace mode switching preserves selected symbol context
3. the active workspace mode is visually reflected
4. diff defaults continue to follow the active catalog selection
5. repair actions stay explicit for supported cases
6. blocked repair states remain explicit for unsupported cases
7. browser-saved load sets remain visually distinct from repo-generated sets

### Manual Screenshot Review

Review at minimum:

1. desktop
2. narrow laptop
3. mobile-width

Look for:

- overlapping text
- clipped controls
- visually noisy command blocks
- state confusion between workspaces
- weak warning or blocked hierarchy

## Completion Checklist

The polish pass is done only when all of these are true:

1. the workbench reads like one application
2. the main operator path is obvious without documentation
3. warning and failure states dominate appropriately
4. common workflows are action-first
5. investigation context survives workspace changes
6. repo-owned and third-party boundaries remain explicit
7. the interface is calm on desktop and mobile-width layouts
8. focused and broad FOM test gates are green

## Risks And Guardrails

Primary risk:

- adding too many "nice" UI ideas and making the app busier

Guardrails:

1. prefer recomposition over expansion
2. remove duplication before adding controls
3. use one strong summary instead of many repeated summaries
4. keep visual styling restrained
5. add tests for preserved context whenever state handling changes

## Operating Rule

Do not confuse polish with ornamental redesign. Every change in this plan must
make the operator path faster, clearer, calmer, or more trustworthy.
