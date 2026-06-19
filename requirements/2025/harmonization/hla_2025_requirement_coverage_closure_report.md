# HLA 1516-2025 requirement coverage disposition pass

This packet is the repo-reconciled harmonization layer over the 691-row
requirement-depth packet. It still separates source and binding surface
accounting from blanket implementation-proof claims, but it now promotes rows
to `covered` where direct repo evidence and executable anchors are present.

## Result

- Total rows dispositioned: 691
- Disposition counts: covered=225, duplicate/umbrella=22, partial=420, planned=0, retired/legacy-only=24
- Priority counts: P0=89, P1=430, P2=172
- Covered rows promoted in this pass: 225

The covered subset is deliberate and limited. This pass does not claim blanket
implementation proof. Each row still carries a closure wave, priority, source
trace strength, suggested evidence path, promotion rule, and explicit closure
task.

## FI Binding Surface

- FI rows: 196
- Java official API surface present: 196 / 196
- C++ official API surface present: 196 / 196
- FedPro present directly: 191 / 196
- FedPro present via alias/split route: 0 / 196
- FedPro route-boundary or missing-review rows: 0 / 196

The route-boundary set is called out explicitly: callback pump controls such as
Evoke Callback, Evoke Multiple Callbacks, Enable Callbacks, and Disable
Callbacks appear to be local callback-dispatch controls rather than ordinary
FedPro request messages in the provided protocol packet.

## Coverage Risks Addressed

| Coverage risk | What changed in this pass | Remaining gate |
|---|---|---|
| Imported rows are only candidates | Every row now has `harmonization_disposition`, `priority`, `closure_wave`, `repo_evidence_status`, and `promotion_rule`, and a subset is promoted where repo evidence is reconciled. | Keep non-covered rows tied to direct anchors before promotion. |
| FI service depth needs service-level accounting | All 196 FI rows now carry Java/C++/FedPro surface status and service-level closure tasks, and the full FI catalog now points at direct executable Python evidence. | Keep future FI behavior changes synchronized with finish-line slices and executable anchors. |
| Declaration and advisory callback tails lacked harmonized promotion | Registration-availability, turn-interactions, and turn-updates callbacks now point at direct declaration and update-advisory scenario evidence. | Keep callback-only rows gated on executable delivery assertions when behavior changes. |
| Time-management callback coverage had one last gap | `requestRetraction` is now promoted with direct callback-order evidence alongside the existing logical-time slice. | Keep retraction-order behavior aligned with future transport/runtime changes. |
| Ownership release/confirm tails lacked harmonized promotion | `confirmDivestiture` and `attributeOwnershipReleaseDenied` now point at direct Python ownership behavior tests. | Keep pending-acquisition and negotiated-transfer behavior synchronized with the ownership slice. |
| DDM region-lifecycle rows lacked harmonized promotion | Region delete/register/unassociate/unsubscribe/request-update rows now point at direct Python DDM lifecycle assertions. | Add equally direct evidence before promoting any remaining region rows not covered here. |
| Support/query surface rows lacked harmonized promotion | Federate, object-instance, order, update-rate, available-dimension, dimension-set, and range-bounds support lookups now point at direct support-service evidence. | Keep support lookup slices aligned with future factory or handle-surface changes. |
| OMT component depth is not proof | OMT component rows are separated from validator-negative rows and assigned fixture-level closure tasks. | Add positive/negative XML fixtures and parser/import-export assertions per row/group. |
| Delta hints are not authoritative | Delta rows remain `duplicate/umbrella`; none are promoted to coverage without child-row links. | Review 2010/2025 source traces and bind each delta to concrete service/schema rows. |
| Retired mappings can pollute 2025 coverage | Legacy-only rows are isolated as `retired/legacy-only` with explicit exclusion rules. | Decide compatibility/migration support and add migration fixtures only where intentional. |

## Promotion Rule

A row should be promoted to `covered` only when it has a concrete repo evidence
anchor, an executable service test or XML fixture test anchor, a reviewed
unsupported-boundary decision where applicable, and child-row links for umbrella
rows.
