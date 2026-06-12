# Target/Radar Simulation Proof

- suite: `target-radar-proof`
- proof backend: `python/in-memory`
- target truth samples: `4`
- radar events: `18`
- track reports: `4`

## Backend Matrix

| Backend | Status | Track reports | Reason |
| --- | --- | ---: | --- |
| python | passed | 4 |  |

## Simulation Trace

| Step | Time | Target Position (x, y, z) |
| ---: | ---: | --- |
| 1 | 1.0 | (10250.0, 1030.0, 2000.0) |
| 2 | 2.0 | (10500.0, 1060.0, 2000.0) |
| 3 | 3.0 | (10750.0, 1090.0, 2000.0) |
| 4 | 4.0 | (11000.0, 1120.0, 2000.0) |

## Track Reports

| Track | Target | Range (m) | Bearing (rad) | Time |
| --- | --- | ---: | ---: | ---: |
| TRK-001 | Target-1 | 10493.969696925944 | 0.10015160425502397 | 1.0 |
| TRK-002 | Target-1 | 10741.210360103743 | 0.10061151474240683 | 2.0 |
| TRK-003 | Target-1 | 10988.657788829352 | 0.10104999427765002 | 3.0 |
| TRK-004 | Target-1 | 11236.298322846364 | 0.10146850655915136 | 4.0 |

## Visuals

- Backend overview PNG: `target_radar_proof_overview.png`
- Event timeline PNG: `target_radar_proof_timeline.png`
- Truth trajectory PNG: `target_radar_proof_trajectory.png`
- RCS exchange PNG: `target_radar_proof_rcs_exchange.png`
- Backend overview: `target_radar_proof_overview.svg`
- Event timeline: `target_radar_proof_timeline.svg`
- Truth trajectory: `target_radar_proof_trajectory.svg`

## Re-run

`./tools/target-radar proof`
