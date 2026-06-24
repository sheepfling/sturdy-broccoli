# FOM-Backed Scenario Bounded Proof

Source: IEEE 1516-2025 Framework and Rules rows plus the repo's tracked
Proto2025 and Target/Radar scenario suite.

This note records the repo's current requirement-facing claim for tracked
example and FOM-backed scenario execution on the main
`hla-backend-python1516-2025` runtime lane.

It is a bounded scenario-suite claim, not a universal statement that every
possible FOM composition or every conceivable example federation is proven.

## Tracked Suite

The tracked repo-owned scenario suite currently consists of:

- `message-test`
- `space-lite`
- `time-mgmt-test`
- `target-radar`

Those scenarios are exercised through the packaged Proto2025 v0.1 FOM showcase
plus the package-owned Target/Radar route.

## Route Coverage

| Route | Current repo evidence anchors | Current bounded reading |
| --- | --- | --- |
| `python1516_2025-inprocess` | `tests/scenarios/test_proto2025_fom_showcase.py`, `tests/test_rti1516_2025_python1516_2025_runtime.py`, `tests/scenarios/test_target_radar_scenario.py` | The direct `python1516_2025` lane executes the tracked repo example/FOM-backed scenarios, including MessageTest, SpaceLite, TimeMgmtTest, object exchange, and Target/Radar-backed rollback paths. |
| `python1516_2025-fedpro-grpc` | `tests/transport/test_grpc_transport_2025.py`, `tests/scenarios/test_python_route_parity.py`, `packages/hla-verification/src/hla/verification/repo_internal/spec2025_finish_line.py` | The hosted FedPro route replays the tracked FOM-backed runtime scenarios through the package-owned Proto2025 example/FOM showcase and shared Target/Radar path rather than relying only on indirect object, MOM, and save/restore route slices. |

## Scenario Inventory Notes

- `message-test` uses `Proto2025_Base.xml` plus `Proto2025_MessageTest.xml`
- `space-lite` uses `Proto2025_Base.xml` plus `Proto2025_SpaceLite.xml`
- `time-mgmt-test` uses `Proto2025_Base.xml` plus
  `Proto2025_TimeMgmtTest.xml`
- `target-radar` remains the package-owned shared scenario route over the
  existing Target/Radar FOM module and the same `python1516_2025` runtime family

## Boundary

- This note proves the tracked repo example/FOM-backed suite only.
- It does not yet prove every conceivable example FOM scenario outside the
  tracked suite.
- It does not turn hosted FedPro replay into a universal claim for every
  possible FOM composition.
- The primary runtime owner behind these tracked scenario claims is
  `hla-backend-python1516-2025`. `hla-backend-shim` is not an implementation owner
  for this milestone.
