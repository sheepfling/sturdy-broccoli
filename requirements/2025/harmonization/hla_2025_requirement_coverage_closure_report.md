# HLA 1516-2025 requirement coverage disposition pass

This packet is a provisional harmonization layer over the 691-row
requirement-depth packet. It separates source and binding surface accounting
from implementation-proof claims.

## Result

- Total rows dispositioned: 691
- Disposition counts: duplicate/umbrella=22, partial=516, planned=129, retired/legacy-only=24
- Priority counts: P0=89, P1=430, P2=172
- Covered rows promoted in this pass: 0

The zero-covered result is deliberate. This pass does not claim implementation
proof. Each row instead has a closure wave, priority, source trace strength,
suggested evidence path, promotion rule, and explicit closure task.

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

## Coverage Risks Addressed

| Coverage risk | What changed in this pass | Remaining gate |
|---|---|---|
| Imported rows are only candidates | Every row now has `harmonization_disposition`, `priority`, `closure_wave`, `repo_evidence_status`, and `promotion_rule`. | Import into the repo and replace provisional evidence paths with actual anchors. |
| FI service depth needs service-level accounting | All 196 FI rows now carry Java/C++/FedPro surface status and service-level closure tasks. | Map each service to Python shim route, vendor route, callback path, and executable tests. |
| OMT component depth is not proof | OMT component rows are separated from validator-negative rows and assigned fixture-level closure tasks. | Add positive/negative XML fixtures and parser/import-export assertions per row/group. |
| Delta hints are not authoritative | Delta rows remain `duplicate/umbrella` or `planned`; none are promoted to coverage without child-row links. | Review 2010/2025 source traces and bind each delta to concrete service/schema rows. |
| Retired mappings can pollute 2025 coverage | Legacy-only rows are isolated as `retired/legacy-only` with explicit exclusion rules. | Decide compatibility/migration support and add migration fixtures only where intentional. |

## Promotion Rule

A row should be promoted to `covered` only when it has a concrete repo evidence
anchor, an executable service test or XML fixture test anchor, a reviewed
unsupported-boundary decision where applicable, and child-row links for umbrella
rows.
