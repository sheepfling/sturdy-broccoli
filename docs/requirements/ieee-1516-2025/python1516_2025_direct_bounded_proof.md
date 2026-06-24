# Direct Python2025 Bounded Proof

Source: IEEE 1516.1-2025 direct-runtime evidence over the repo-owned
`hla-backend-python1516-2025` implementation lane.

This note records the repo's current direct-lane claim for `python1516_2025`.
The direct lane is the main executable bounded proof surface for the current
2025 Python RTI. It is requirement-facing runtime evidence over
`hla-backend-python1516-2025`, not a wrapper-owned surface and not a full
unqualified conformance claim.

## Current Bounded Claim

- `python1516_2025` is the direct main-surface runtime lane for
  `hla-backend-python1516-2025`.
- `hla-backend-python1516-2025` is the sole repo-owned IEEE 1516.1-2025 Python RTI
  implementation lane behind this direct proof surface.
- The direct lane has executable proof across the tracked runtime families used
  by the current finish-line inventory.
- The direct lane carries the main package-boundary, runtime-identity, time,
  save/restore, ownership, callback-control, MOM, support-service, and OMT
  proof load for the current 2025 claim.
- The remaining proof limits on this lane are requirement-granularity and
  broader conformance-boundary limits, not uncertainty about whether
  `hla-backend-python1516-2025` is the repo-owned runtime owner.

## Tracked Direct Scenario Families

| Scenario family | Status | Evidence anchors | Current direct reading |
| --- | --- | --- | --- |
| `federation_lifecycle` | `direct-runtime-covered` | `tests/test_rti1516_2025_python1516_2025_runtime.py` | Direct lifecycle covers connect/create/join/list/resign/destroy/disconnect, synchronization, and save/restore control over the primary `python1516_2025` lane. |
| `object_exchange` | `direct-runtime-covered` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_target_radar_scenario.py` | Direct object exchange covers discovery, reflection, interaction delivery, directed routing, and package-owned FOM-backed scenario replay. |
| `ownership` | `direct-runtime-covered` | `tests/test_rti1516_2025_python1516_2025_runtime.py` | Direct ownership covers acquisition/divestiture/query callback flow, owner visibility, resign policy, and bounded save/restore ownership rollback. |
| `ddm` | `direct-runtime-covered` | `tests/test_rti1516_2025_python1516_2025_runtime.py` | Direct DDM covers region overlap filtering, scope advisories, passive routing, directed DDM routing, and restore/disconnect cleanup. |
| `time_management` | `direct-runtime-covered` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_target_radar_scenario.py` | Direct time management covers regulation/constrained mode, grants, queued TSO delivery, GALT/LITS/lookahead queries, and the Target/Radar proof ladder. |
| `save_restore` | `direct-runtime-covered` | `tests/test_rti1516_2025_python1516_2025_runtime.py` | Direct save/restore covers lifecycle callbacks, rollback hygiene, stale queued-state cleanup, callback-policy restore, and bounded gauntlet replay. |
| `mom` | `direct-runtime-covered` | `tests/test_rti1516_2025_python1516_2025_runtime.py` | Direct MOM covers service-report callbacks, MIM/FOM reporting, synchronization/time-management service interactions, and observable manager actions. |
| `support_services` | `direct-runtime-covered` | `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/test_fom_target_radar_split_package.py` | Direct support services cover handle/name round trips, decode helpers, callback-control, switch inquiry/control, and package-owned example/FOM support helpers. |
| `omt_validation` | `direct-runtime-covered` | `tests/test_rti1516_2025_validation.py` | Direct OMT validation covers parser, serializer, schema, metadata round-trip, and bounded `xs:any` tolerance evidence on the main Python lane. |

## Primary Evidence Anchors

- `tests/test_rti1516_2025_python1516_2025_runtime.py`
- `tests/scenarios/test_target_radar_scenario.py`
- `tests/test_fom_target_radar_split_package.py`
- `tests/test_rti1516_2025_validation.py`
- `docs/test_surface.md`
- `docs/python_rti_backend.md`
- `docs/requirements/ieee-1516-2025/hosted_fedpro_bounded_proof.md`
- `docs/requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`

## Reading of the Evidence

- `tests/test_rti1516_2025_python1516_2025_runtime.py` is the main direct runtime
  anchor. It proves the package-owned `python1516_2025` lane directly rather than
  routing the claim through `hla-backend-shim`.
- `tests/scenarios/test_target_radar_scenario.py` is the shared-scenario time
  and exchange anchor. It proves the package-owned Target/Radar path runs on
  the direct `python1516_2025` lane, including the bounded lookahead-window ladder.
- `tests/test_fom_target_radar_split_package.py` is the package-ownership
  anchor for the direct example/FOM lane. It keeps the shared Target/Radar
  adapter under the FOM package while preserving `hla-backend-python1516-2025` as
  the runtime owner.
- `tests/test_rti1516_2025_validation.py` is the direct OMT anchor. It proves
  parser/serializer/schema and bounded `xs:any` tolerance behavior over the
  repo-native Python surface.
- `docs/test_surface.md` captures the operator-facing boundary:
  `verify-main-2025` is the normal main-surface proof lane for the direct
  `python1516_2025` runtime.
- `docs/requirements/ieee-1516-2025/hosted_fedpro_bounded_proof.md` is the
  hosted companion note. It replays these runtime families over
  `python1516_2025-fedpro-grpc` without turning the hosted route into a second RTI
  owner.

## Operator Lanes

- `./tools/python verify-main-2025` is the default direct proof lane for this
  note's claim.
- `./tools/python verify-routes-2025` is the companion hosted hygiene lane
  when the same bounded families must also remain green on
  `python1516_2025-fedpro-grpc`.

## Explicit Non-Claim

- The repo does not claim full unqualified IEEE 1516.1-2025 conformance from
  the direct lane alone.
- The repo does not treat `hla-backend-shim` as part of the implementation
  owner claim for this lane.
- The repo does not use the direct-lane bounded proof to erase the separate
  hosted-route, Java/C++, duplicate/umbrella, retired-row, or OMT-extension
  boundaries documented elsewhere.
