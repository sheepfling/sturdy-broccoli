# Runtime Surface Naming And Backlog

This page exists to solve two problems:

1. the repo has three adjacent browser/API surfaces that are hard to name consistently
2. the feature backlog for those surfaces is spread across code, tests, and ad hoc notes

Use this page as the operator-facing naming source and the product backlog seed.

Tracked execution now lives in:

- [`plans/hla_studio_surface_worklist.md`](plans/hla_studio_surface_worklist.md)

## Recommended Names

Use these names in docs, demos, tickets, and verbal discussion.

| Current name(s) | Recommended name | Short description | Keep as alias? |
| --- | --- | --- | --- |
| `FOM Workbench`, `FOM UI`, `workbench` | `FOM Explorer` | inspect, compare, validate, and author FOM load sets and merged views | yes |
| `Federation Visualizer`, `federation subscriber`, `runtime observer` | `Federation Visualizer` | live execution observer with roster, events, object/interaction inspectors, and scenario panels | yes |
| `federate-service`, `federate bridge thing`, `RTIambassador FastAPI` | `RTI Bridge API` | bounded API surface that exposes canonical RTIambassador-style operations over HTTP | yes |

## Practical Rule

When talking about the three surfaces together, use:

- `FOM Explorer`
- `Federation Visualizer`
- `RTI Bridge API`

When talking about the combined story, use:

- `HLA Studio surfaces`

That gives one umbrella phrase without forcing a code rename today.

## Naming Guidance

### 1. FOM Explorer

Why this is clearer:

- `explorer` describes the main operator job better than `workbench`
- it is easier to say out loud
- it still leaves room for editing, validation, diffing, and authoring

Keep these code/tool aliases for now:

- `./tools/fom-workbench`
- `fom_workbench.py`
- `fom_workbench.md`

Operator wording should gradually prefer:

- `FOM Explorer`

### 2. Federation Visualizer

Why this is clearer:

- `visualizer` is what people expect when they want to watch a running federation
- `subscriber` is accurate internally but weak as a demo/operator name
- `runtime observer` is a useful implementation term, not the primary UI name

Keep these aliases for now:

- `federation subscriber`
- `runtime observer`

Operator wording should gradually prefer:

- `Federation Visualizer`

### 3. RTI Bridge API

Why this is clearer:

- `federate-service` sounds generic and does not tell the operator what it bridges
- `RTI Bridge API` says exactly what it is: a bounded bridge into RTIambassador-style operations
- it also distinguishes this surface from the visualizer

Keep these aliases for now:

- `federate-service`
- `federate-service-api`

Operator wording should gradually prefer:

- `RTI Bridge API`

## Surface Map

| Surface | Primary tool | Primary job |
| --- | --- | --- |
| `FOM Explorer` | `./tools/fom-workbench` | inspect FOMs, compare merged sets, validate structure, and navigate family metadata |
| `Federation Visualizer` | `./tools/federation-subscriber-api` and `./tools/fom-siso-runtime-observer` | observe live or launched federations through normalized events and scenario-aware panels |
| `RTI Bridge API` | `./tools/federate-service-api` | drive bounded RTIambassador-style operations over a typed HTTP surface |

## Backlog

Priorities below are product-facing, not code-order promises.

### FOM Explorer

#### High priority

- add a clearer top header that says `FOM Explorer` while preserving `FOM Workbench` as an alias in docs and URLs
- add one-click scenario presets for `Link 16`, `RPR 3.0`, `Space FOM`, and repo-owned small examples
- add a class tree deep-link format that can open exact classes, interactions, and datatypes directly
- add better merged-load-set storytelling: which files are base, add-on, annex, or support-only
- add a stronger validation summary rail with issue counts by severity and by source file
- add round-trip and parser-stress badges directly in the explorer cards

#### Medium priority

- add a side-by-side compare mode for two exact load sets with synchronized tree focus
- add edition overlays that explain `2010 only`, `2025 only`, `both`, and `cross-edition / ambiguous`
- add an operator-friendly export panel for snapshot JSON, validation packets, and scenario manifests
- add a `why this merged set exists` note field for curated showcase and stress packets
- add a compact mode optimized for screenshots and demo packets

#### Longer term

- add inline editing for curated metadata without implying arbitrary FOM XML authoring is fully safe
- add semantic lint checks for common SISO integration mistakes and custom datatype quirks
- add visual dependency graphs for multi-module load sets

### Federation Visualizer

#### High priority

- add a clearer product header that says `Federation Visualizer`
- add a visible execution summary strip: scenario, edition, backend, federate count, phase, event rate
- add stronger late-join state hydration so the object and interaction inspectors always feel populated quickly
- add richer timeline filters for family, federate, event type, class, and scenario phase
- add operator-friendly bookmarks for interesting rows in `Link 16`, `RPR`, and `Space` showcase lanes
- add first-class screenshot-friendly layouts for hydrated scenario panels
- add a top-level artifact drawer linking listener summary, trace, state snapshot, and gallery outputs

#### Medium priority

- add a true timeline view with phase bands and event clustering
- add object lifetime views: discovered, updated, deleted, ownership changed
- add interaction burst summaries for high-traffic scenarios
- add federate roster deltas and readiness/synchronization panels
- add a replay mode from retained state and event history without rerunning the scenario
- add a small minimap or activity heat strip for large 10-federate runs

#### Showcase-specific features

- Link 16:
  - semantic message lane summaries
  - network/group participation views
  - transmit/receive activity rollups
- RPR:
  - entity lifecycle and engagement summaries
  - attribute update burst views
  - weapon fire / detonation / observer correlation
- Space:
  - constellation roster and orbital-state update summaries
  - platform grouping and reference-frame views
  - higher-density object inspector presets for 10-federate rows

### RTI Bridge API

#### High priority

- rename operator-facing docs toward `RTI Bridge API`
- add a simpler landing page that explains the bridge purpose before dumping raw contract detail
- add grouped contract docs by RTIambassador service family
- add session lifecycle examples that match the Java mapping names exactly
- add better error payload examples and status code guidance
- add a bridge demo panel that shows a few canonical calls and responses

#### Medium priority

- add request/response history per session
- add generated client snippets for Python and Java
- add a contract diff artifact when the generated interface metadata changes
- add a bridge readiness panel that explains backend, route, and session constraints

#### Longer term

- add safe bounded command macros for create, join, publish, register, update, send, and resign
- add a bridge parity packet that compares direct runtime results versus bridge-driven results on selected scenarios

## Cross-Surface Backlog

These should be planned as one shared story across all three surfaces.

### High priority

- standardize naming in headers, docs, screenshot packets, and artifact indexes
- add cross-links:
  - `FOM Explorer` -> exact family/class in `Federation Visualizer`
  - `Federation Visualizer` -> exact FOM entity in `FOM Explorer`
  - `Federation Visualizer` -> `RTI Bridge API` examples for relevant operations
- add one aggregate `HLA Studio` index page that links the three surfaces plus their generated artifacts
- make screenshot packets and surface-matrix packets use the same labels the docs use

### Medium priority

- add stable screenshot scene ids so demos can regenerate the same panels deterministically
- add shared search terms and chips for family, edition, topology, and scenario
- add a single surface glossary for `family`, `edition`, `topology`, `scenario`, `provider`, `backend`, and `bridge`

## Suggested Rollout

Phase 1:

- adopt the recommended names in docs
- keep tool names and module names unchanged
- update UI headers where cheap and low-risk

Phase 2:

- add alias notes in the tools and front-door docs
- update screenshot packets and runtime surface matrix labels
- add the aggregate cross-surface index

Phase 3:

- decide whether tool renames are worth the migration cost
- only rename wrappers if the operator benefit clearly beats the churn

## Short Script

If you need a clean verbal summary, use this:

- `FOM Explorer` is the FOM inspection and comparison surface
- `Federation Visualizer` is the live execution observer surface
- `RTI Bridge API` is the bounded HTTP bridge into RTIambassador-style operations
