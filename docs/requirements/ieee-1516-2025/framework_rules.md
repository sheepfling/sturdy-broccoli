# Framework and Rules Requirements

Source: IEEE 1516-2025 Framework and Rules.

These rows remain `duplicate/umbrella` in the harmonization ledger. They are
not claimed as standalone runtime slices. Each rule closes only through linked
child FI, OMT, and runtime evidence that already carries the executable proof.

## Owner Surface

- canonical owner doc: `docs/requirements/ieee-1516-2025/framework_rules.md`
- primary shard: `unit-python-2025-core`
- widen to: `./tools/python verify-routes-2025` only when a framework umbrella
  row is being restated as a hosted-route-backed claim
- typical view tags: `2025-core`, `finish-line`, `scenarios`

## Final Claim Rule

- these rows stay `duplicate/umbrella`, not standalone runtime proof rows
- a framework row is only as strong as the linked child FI, OMT, or runtime
  owner rows beneath it
- do not count a framework umbrella row as a separate covered implementation
  bucket on top of the child evidence it summarizes
- if a future change needs a standalone framework claim, split that claim into
  a narrower executable child row rather than silently widening the umbrella row

Default final stance:

- this bucket is already in its intended final repo-owned state as a
  non-standalone parent or normalization surface
- no additional runtime proof is required to keep these rows out of standalone
  `covered` status
- future work is optional and should happen only if the repo deliberately
  introduces narrower executable child claims that justify changing the
  umbrella structure

Use `Evidence anchors` and `Bounded claim reading` here as owner-facing proof
vocabulary. They describe umbrella-row evidence scope, not canonical child-row
disposition.

| ID | Clause | Page | Summary | Linked child rows | Evidence anchors | Bounded claim reading |
| --- | ---: | ---: | --- | --- | --- | --- |
| HLA2025-FR-001 | 5.1 | 31 | A federation shall have an HLA FOM documented according to the OMT. | `HLA2025-REQ-001`, `HLA2025-OMT-001`, `HLA2025-OMT-005`, `HLA2025-OMT-006` | `tests/test_rti1516_2025_validation.py`, `tests/factories/test_proto2025_fom_resources.py`, `tests/scenarios/test_proto2025_fom_showcase.py` | Closed through OMT validation, FOM resource packaging, and FOM-backed scenario proof rather than as a separate runtime rule. |
| HLA2025-FR-002 | 5.2 | 32 | Simulation-associated object instance representation shall be in federates, not in the RTI. | `HLA2025-FI-001`, `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-060`, `HLA2025-FI-SVC-065`, `HLA2025-FI-SVC-066` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `docs/plans/spec2025_finish_line.md` | Closed through object-exchange, delete/remove, and save/restore rollback evidence showing that RTI state is routing state while semantic object state remains federate-owned. |
| HLA2025-FR-003 | 5.3 | 32 | All exchange of FOM data among joined federates shall occur via the RTI. | `HLA2025-FI-001`, `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-060`, `HLA2025-FI-SVC-063`, `HLA2025-FI-SVC-064` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/backends/test_shim_route_trace_evidence.py` | Closed through direct-lane and hosted FedPro route traces that show object and interaction exchange flowing through the selected RTI lane and callback path. |
| HLA2025-FR-004 | 5.4 | 32 | Joined federates shall interact with the RTI according to the HLA interface specification. | `HLA2025-FI-001`, `HLA2025-FI-002`, `HLA2025-FI-003`, `HLA2025-FI-004`, `HLA2025-FI-005`, `HLA2025-FI-006`, `HLA2025-FI-009` | `tests/test_hla_factory_composition.py`, `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py` | Closed through the direct `python1516_2025` API surface plus hosted FedPro route replay; Java/C++ remain binding-capability evidence rather than full behavior equivalence. |
| HLA2025-FR-005 | 5.5 | 33 | An instance attribute shall be owned by at most one joined federate at a time. | `HLA2025-FI-001`, `HLA2025-FI-SVC-082`, `HLA2025-FI-SVC-083`, `HLA2025-FI-SVC-089`, `HLA2025-FI-SVC-090`, `HLA2025-FI-SVC-095` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_ownership_management_backend_matrix.py` | Closed through ownership acquisition/divestiture/query/restore evidence proving one-owner-at-a-time behavior on the main `python1516_2025` lane. |
| HLA2025-FR-006 | 6.1 | 33 | Federates shall have a SOM documented according to the OMT. | `HLA2025-REQ-001`, `HLA2025-FR-001`, SOM/FOM service-usage rows in `hla_2025_requirement_depth_expansion.csv` | `docs/evidence/spec2025/traceability_matrix.json`, `requirements/2025/depth/hla_2025_requirement_depth_expansion.csv`, `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv` | Still a bounded documentation/evidence rule. The repo tracks SOM/SOM-usage closure through the imported depth and harmonization packets rather than a native runtime-only claim. |
| HLA2025-FR-007 | 6.2 | 33 | Federates shall be able to update/reflect attributes and send/receive interactions as documented. | `HLA2025-FI-001`, `HLA2025-FI-SVC-057`, `HLA2025-FI-SVC-059`, `HLA2025-FI-SVC-060`, `HLA2025-FI-SVC-061`, `HLA2025-FI-SVC-063` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_target_radar_scenario.py` | Closed through object and interaction exchange scenario families plus the FOM-backed Target/Radar route; still bounded to the executable surfaces actually tracked in the repo. |
| HLA2025-FR-008 | 6.3 | 34 | Federates shall be able to transfer and accept ownership dynamically. | `HLA2025-FI-001`, `HLA2025-FI-SVC-082`, `HLA2025-FI-SVC-083`, `HLA2025-FI-SVC-084`, `HLA2025-FI-SVC-085`, `HLA2025-FI-SVC-095` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_ownership_management_backend_matrix.py` | Closed through dynamic ownership transfer scenario coverage on the main `python1516_2025` lane and hosted replay, not by treating the umbrella row as its own proof bucket. |
| HLA2025-FR-009 | 6.4 | 34 | Federates shall be able to vary update conditions such as thresholds. | `HLA2025-FI-SVC-068`, `HLA2025-FI-SVC-069`, `HLA2025-FI-SVC-070`, `HLA2025-FI-SVC-071`, `HLA2025-FI-SVC-155`, `HLA2025-FI-SVC-156` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_object_management_backend_matrix.py`, `tests/backends/test_python_backend_support_services.py` | Closed through update-rate/advisory/control evidence where present; threshold semantics remain bounded to the tracked update-condition surfaces rather than a blanket federate-claim pass. |
| HLA2025-FR-010 | 6.5 | 34 | Federates shall manage local time to coordinate data exchange. | `HLA2025-FI-009`, `HLA2025-MOD-006`, `HLA2025-FI-SVC-101`, `HLA2025-FI-SVC-107`, `HLA2025-FI-SVC-112`, `HLA2025-FI-SVC-121` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/transport/test_grpc_transport_2025.py`, `tests/backends/test_shim_route_trace_evidence.py` | Closed through the decomposed time-management and Target/Radar lookahead proof families, including bounded GALT/LITS, retraction, and time-window evidence. |

## Closure Notes

- `HLA2025-FR-001` through `HLA2025-FR-010` remain umbrella rows in the
  harmonization packet because their normative force is already carried by the
  child FI, OMT, and runtime rows above.
- The repo should not promote these framework rows to standalone `covered`
  runtime claims unless they gain narrower child evidence than the current
  linked rows and artifacts already provide.
- The primary implementation lane behind the executable anchors above is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not a runtime owner for these
  framework rules.

## Latest Investigated Decision

The framework umbrella slice was re-audited on `2026-06-26` against the
current owner doc, harmonization ledger, child-row map, runtime tests,
scenario suites, and traceability anchors for:

- `HLA2025-FR-001` through `HLA2025-FR-010`

Decision:

- keep these rows as `duplicate/umbrella`
- do not promote them to standalone `covered`

Reason:

1. the current child FI, OMT, traceability, scenario, ownership, and time
   rows already carry the real executable or bounded documentation semantics
   for these framework rules
2. the current framework owner doc already records the narrow honest reading
   for each rule without pretending that the framework layer is a second proof
   bucket on top of the child rows
3. no narrower standalone framework claim was identified that would do more
   than restate the linked child-row proof
4. converting these rows now would double-count child proof instead of
   tightening it

Current evidence reviewed for this decision included:

- `tests/test_rti1516_2025_python1516_2025_runtime.py`
- `tests/transport/test_grpc_transport_2025.py`
- `tests/scenarios/test_proto2025_fom_showcase.py`
- `tests/scenarios/test_target_radar_scenario.py`
- `tests/scenarios/test_ownership_management_backend_matrix.py`
- `tests/test_rti1516_2025_validation.py`
- `docs/evidence/spec2025/traceability_matrix.json`
- `requirements/2025/harmonization/hla_2025_requirement_disposition_ledger.csv`

Operational effect:

- the framework slice remains a maintained umbrella boundary over linked child
  proof
- the active closeout queue should advance only when leadership wants literal
  `691 / 691 covered` or when new narrower framework child claims are
  intentionally introduced

## Exit Condition

Treat this bucket as closed for current closeout purposes when all of these are
true:

1. all framework umbrella rows remain anchored to this owner doc and the
   row-level disposition ledger
2. the final claim language keeps them explicit as parent or normalization rows
   rather than accidental standalone runtime proof
3. no generated packet, audit note, or grouped worklist reclassifies them as
   standalone `covered` implementation buckets

Only reopen this bucket if the repo intentionally introduces narrower child
claims or changes the framework-to-child ownership map.

## Cross-Standard Backlog

| ID | Source | Summary |
| --- | --- | --- |
| HLA2025-REQ-001 | IEEE 1516.1-2025 1.4 p. 17 | Treat HLA 2025 as a coordinated three-document product set and cross-link Framework rules, Federate Interface service behavior, and OMT/FOM data requirements. |
| HLA2025-REQ-002 | IEEE 1516.1-2025 13 p. 413; IEEE 1516.2-2025 6.1 p. 90 | Do not overclaim `HLA Conforming`; use scoped evidence vocabulary until certified conformance evidence exists. |
