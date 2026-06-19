# FOM Workbench

This page defines the intended UI/UX front door for displaying, inspecting,
joining, overlaying, editing, and searching FOM XML content.

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
  - not implemented yet
  - planned as a comparison view over two or more family snapshots
- edit:
  - not implemented yet
  - planned as a guarded edit surface over repo-owned XML only

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
  - `analysis/fom_workbench/fom_workbench_snapshot.json`
  - `analysis/fom_workbench/fom_workbench.html`

## Data Contract

The snapshot is generated from:

- [`fom-examples/fom_inventory.json`](fom-examples/fom_inventory.json)
- repo parse/merge helpers in `hla.rti1516e.fom`

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
- family inspect panel
- per-family precomputed validation packet links
- per-custom-load-set precomputed validation packet links
- merged-name search over object, interaction, and datatype names
- pairwise family overlay/diff over precomputed default load sets
- hierarchy-aware object/interaction drill-down
- guarded edit command generation for repo-owned XML only

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
- validation HTML supports side-by-side hierarchy-aware member tree diffing for multi-module load sets, including declared-vs-total member deltas on shared nodes

## Next Implementation Slices

1. surface custom load-set builders and saved sets directly from the browser UI
2. expand hierarchy-aware diffing into datatype-hint deltas and dimension usage deltas on shared nodes
3. expand guarded repo-owned edit flows into selected safe structural edits
