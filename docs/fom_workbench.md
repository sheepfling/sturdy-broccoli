# FOM Workbench

This page defines the intended UI/UX front door for displaying, inspecting,
joining, overlaying, editing, and searching FOM XML content.

This page is part of the FOM surface. If you are still deciding whether the
problem is mostly backend, transport, or FOM, start at
[`work_surfaces.md`](work_surfaces.md). For the FOM front door, start at
[`fom_tooling_front_door.md`](fom_tooling_front_door.md).

The repo does not yet ship a full browser application. The current first slice
is a stable JSON snapshot that a future UI can consume.

## Scope

The workbench needs to support:

- display:
  - family catalog
  - edition and baseline classification
  - per-family parse/load status
- inspect:
  - module membership
  - default load/join sets
  - merged object/interaction/datatype counts
  - dimension list
- search:
  - by module id
  - by path
  - by scenario family
  - by edition class
- join:
  - precomputed default load sets for:
    - `standalone`
    - `base-plus-extension`
    - `ordered-family`
- overlay:
  - precomputed comparison view over generated family and named load-set pairs
  - highlights added/removed objects, interactions, datatypes, and dimensions
- edit:
  - guarded repo-owned metadata edit flow
  - supported simple-datatype repair staging for repo-owned merge conflicts

## Current Operator Path

- generate the snapshot:
  - `./tools/fom-workbench`
- generate snapshot plus local HTML workbench:
  - `./tools/fom-workbench --html`
- generate named custom load sets and compare them:
  - `./tools/fom-workbench --html --custom-load-set custom-a=repo-cross-target-radar,repo-2010-demo --custom-load-set custom-b=repo-2025-proto-base,repo-2025-proto-message-test --diff custom-a:custom-b`
- write a guarded edited copy of a repo-owned XML:
  - `./tools/fom-workbench --edit-entry repo-2010-demo --set-description "Updated description" --add-keyword workbench --add-note "N9: note"`
- output artifact:
  - `artifacts/fom_workbench/fom_workbench_snapshot.json`
  - `artifacts/fom_workbench/fom_workbench.html`

## Data Contract

The snapshot is generated from:

- [`fom-examples/fom_inventory.json`](fom-examples/fom_inventory.json)
- repo parse/merge helpers in `hla.fom`

Each family row includes:

- `scenario_family`
- `edition_classes`
- `baseline_kinds`
- `load_mode`
- `member_ids`
- `member_paths`
- `default_load_set_ids`
- `default_load_set_paths`
- `parse_status`
- `parse_error`
- `module_names`
- `object_class_count`
- `interaction_class_count`
- `datatype_count`
- `dimensions`

Each custom load-set row includes:

- `name`
- `member_ids`
- `member_paths`
- `parse_status`
- `module_names`
- merged object/interaction/datatype counts and name sets

Each search row includes:

- `source_name`
- `source_kind`
- `kind`
- `name`
- `parent_name`
- `lineage`
- `is_leaf`

Each diff row includes:

- `left_family`
- `right_family`
- `left_kind`
- `right_kind`
- `left_member_ids`
- `right_member_ids`
- shared and left/right-only sets for dimensions, objects, interactions, and datatypes

## UX Shape

The intended workbench should have five panes:

1. catalog
   - left rail of FOM families
   - filter chips for `2010`, `2025`, `cross-edition`, `repo-owned`,
     `third-party`
2. inspect
   - selected family summary
   - parsed module names
   - merged counts and dimensions
3. join-set builder
   - visible default load set
   - optional add/remove for comparison or custom test runs
4. overlay/diff
   - compare two families or two merged sets
   - highlight added/removed classes, interactions, datatypes, and dimensions
5. search
   - fast search over module ids, names, paths, and merged class trees

The current HTML slice implements:

- family catalog
- direct inspect-pane browsing for named custom load sets
- browser-side custom load-set builder/save flow backed by local storage
- browser-side export/import for saved custom load sets
- family inspect panel
- per-family precomputed validation packet links
- per-custom-load-set precomputed validation packet links
- merged-name search over object, interaction, and datatype names
- pairwise family overlay/diff over precomputed default load sets
- hierarchy-aware object/interaction drill-down
- guarded edit command generation for repo-owned XML only
- symbol jump paths across conflict, validation, diff, search, and tree views
- repo-owned repair suggestions for supported simple datatype conflicts
- copyable command bundles and clearer operator empty states

Browser-saved custom load sets are intentionally lightweight:

- they persist in the browser without editing the repo
- they can be exported/imported as JSON for reuse across machines or snapshots
- they generate exact rerun commands for `./tools/fom-workbench --html --custom-load-set ...`
- they do not claim parsed trees, validation packets, or diff rows until the tool is rerun and materializes them

The generated workbench packet now also materializes:

- `validation_packets/<family>/fom_validation_report.json`
- `validation_packets/<family>/fom_validation_report.md`
- `validation_packets/<family>/fom_validation_report.html`
- `validation_packets/<custom-load-set>/fom_validation_report.json`
- `validation_packets/<custom-load-set>/fom_validation_report.md`
- `validation_packets/<custom-load-set>/fom_validation_report.html`

Those packets are linked directly from the inspect pane.
Custom load-set packets are linked from the overlay/diff pane when the selected
comparison uses named custom load sets.

## Boundaries

- third-party XMLs are read-only baseline material
- repo-owned XMLs are candidates for future editing support
- ordered-family and base-plus-extension sets must be treated as first-class
  load modes, not special cases hidden in code

## Validation Handoff

The workbench now connects directly to the validator surface:

- family inspect panel shows the exact `./tools/fom-validate --family ... --html` command
- generated workbench artifacts include precomputed validation packets per family
- generated workbench artifacts include precomputed validation packets per named custom load set
- validation HTML supports side-by-side hierarchy-aware member tree diffing for multi-module load sets, including:
  - declared-vs-total member deltas on shared nodes
  - datatype-hint deltas on shared nodes
  - dimension-usage deltas on shared nodes

## Completion Status

The planned workbench finish-line slices are complete and the supporting FOM
test gates are green. Ongoing changes should be treated as normal feature
evolution rather than unfinished baseline work.

## Execution Plan

The active implementation backlog for turning the current HTML packet into a
real operator-facing console lives in:

- [`docs/plans/fom_ui_work_plan.md`](plans/fom_ui_work_plan.md)

The follow-on polish plan for taking that console to a product-grade
application experience lives in:

- [`docs/plans/fom_ui_polish_plan.md`](plans/fom_ui_polish_plan.md)
