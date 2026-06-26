# HLA 1516-2025 requirement coverage disposition pass

This packet is the repo-reconciled harmonization layer over the 691-row
requirement-depth packet. It still separates source and binding surface
accounting from blanket implementation-proof claims, but it now summarizes the
current committed row-level disposition ledger rather than an older
intermediate unsupported-boundary pass.

## Result

- Total rows dispositioned: 691
- Disposition counts: covered=645, duplicate/umbrella=22, partial=0, planned=0, retired/legacy-only=24, unsupported-boundary=0
- Priority counts: P0=89, P1=430, P2=172
- Covered rows with evidence paths: 645
- Rows remaining as explicit unsupported-boundary dispositions: 0

The covered subset is deliberate and limited. This pass does not claim blanket
implementation proof. Each row still carries a closure wave, priority, source
trace strength, suggested evidence path, promotion rule, and explicit closure
task.

Historical note:

- earlier harmonization passes used `unsupported-boundary` as an explicit
  intermediate disposition for rows that had not yet been promoted into
  `covered`, `duplicate/umbrella`, or `retired/legacy-only`
- the current committed row-level ledger no longer uses that disposition
- if an older packet still reports `unsupported-boundary=81`, treat it as
  historical intermediate evidence rather than the current closeout state

## Canonical Owner Surfaces

Read this packet together with the 2025 requirement front door:

- `docs/requirements/ieee-1516-2025/README.md`

Use these canonical owner docs when a row family is a boundary, umbrella, or
other non-leaf bucket rather than a direct executable service claim:

| Bucket | Canonical owner doc |
| --- | --- |
| framework umbrella rows | `docs/requirements/ieee-1516-2025/framework_rules.md` |
| callback/configuration/binding delta umbrellas | `docs/requirements/ieee-1516-2025/callback_binding_deltas.md` |
| binding and hosted-route boundary rows | `docs/requirements/ieee-1516-2025/binding_and_hosted_route_boundaries.md` |
| Pitch proto HLA 4 / `202X` backend-resolution lane | `docs/requirements/ieee-1516-2025/pitch_202x_bounded_comparison.md` |
| legacy-alias and non-claim perimeter around the main runtime lane | `docs/requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md` |
| retired and legacy-only mapping rows | `docs/requirements/ieee-1516-2025/retired_legacy_mapping.md` |
| OMT `xs:any` extension-tolerance boundary | `docs/requirements/ieee-1516-2025/omt_xs_any_extension_tolerance.md` |

This report should agree with those owner docs.
If a future harmonization pass changes one of these bucket families, update the
owner doc first, then reflect the change here and in the finish-line packet.

## FI Binding Surface

- FI rows: 196
- Java official API surface present: 196 / 196
- C++ official API surface present: 196 / 196
- FedPro present directly: 191 / 196
- FedPro present via alias/split route: 1 / 196
- FedPro route-boundary or missing-review rows: 4 / 196

The route-boundary set is called out explicitly: callback pump controls such as
Evoke Callback, Evoke Multiple Callbacks, Enable Callbacks, and Disable
Callbacks appear to be local callback-dispatch controls rather than ordinary
FedPro request messages in the provided protocol packet.

## Current Row-Level Closure Reading

The current ledger-backed row-level reading is:

- `645` covered rows
- `22` duplicate/umbrella rows
- `24` retired/legacy-only rows
- `0` unsupported-boundary rows

This means:

- the repo now has an explicit row-level disposition for all 691 tracked rows
- the remaining 2025 closeout debt is no longer a hidden unsupported bucket
- the remaining blocker is bounded-claim discipline, umbrella-row hygiene,
  retired-row exclusion discipline, and bounded route or binding scope honesty
  rather than stale row-level review debt

Read the current backend-resolution posture separately from those
dispositions:

- the direct `python1516_2025` lane is the primary runtime owner behind the
  covered row set
- Java/C++ standard-shim surfaces remain wrapper or capability layers over
  that lane rather than alternate RTI owners
- hosted FedPro evidence remains a bounded hosted-route surface over
  `hla-backend-python1516-2025`, not a second implementation lane
- any Pitch proto HLA 4 / `202X` overlap remains explicit vendor-resolution
  context and must stay in linked owner docs or backend-resolution artifacts
  instead of being inferred from grouped coverage counts

## Coverage Risks Addressed

| Coverage risk | What changed in this pass | Remaining gate |
|---|---|---|
| Imported rows are only candidates | Every row now has `harmonization_disposition`, `priority`, `closure_wave`, `repo_evidence_status`, and `promotion_rule`, and the current ledger assigns every tracked row to `covered`, `duplicate/umbrella`, or `retired/legacy-only`. | Keep future row changes synchronized with the row-level ledger, worklist, owner docs, and finish-line packet. |
| FI service depth needs service-level accounting | All 196 FI rows now carry Java/C++/FedPro surface status and service-level closure tasks, and the full FI catalog now points at direct executable Python evidence. | Keep future FI behavior changes synchronized with finish-line slices and executable anchors. |
| SOM/FOM service-utilization rows lacked reconciled closure | All 196 service-utilization rows now point at direct parser/roundtrip evidence plus renumbered-differential checks and the covered FI catalog they mirror. | Keep serviceUtilization parser semantics and FI cross-checks synchronized when object-model handling changes. |
| OMT component depth is not proof | The remaining OMT component rows are now either promoted into the supported shared parser/serializer subset or normalized into explicit bounded owner-doc readings instead of being left partial. | Keep narrowing broad claims, add direct fixtures when support expands, and replace bounded owner-doc language only when parser/serializer/runtime evidence exists. |
| Delta hints are not standalone proof | Delta rows remain `duplicate/umbrella`, but each current delta row is now tied to concrete child FI/binding evidence and its canonical owner doc rather than left in evidence-anchor debt. | Keep the child-row maps, owner docs, and binding-specific evidence anchors synchronized when the delta families change. |
| Framework rules are not standalone proof | Framework rows remain `duplicate/umbrella`, but each current framework row is now tied to concrete child FI/OMT/runtime evidence and its canonical owner doc rather than left in evidence-anchor debt. | Keep the child-row maps, owner docs, and linked FI/OMT/runtime evidence anchors synchronized when the framework family changes. |
| Retired mappings can pollute 2025 coverage | Legacy-only rows are isolated as `retired/legacy-only` with explicit exclusion rules. | Decide compatibility/migration support and add migration fixtures only where intentional. |

## Promotion Rule

A row should be promoted to `covered` only when it has a concrete repo evidence
anchor, an executable service test or XML fixture test anchor, a reviewed
unsupported-boundary decision where applicable, and child-row links for umbrella
rows.

Under the current ledger state, that rule has already been applied to the 645
rows that remain `covered`.
