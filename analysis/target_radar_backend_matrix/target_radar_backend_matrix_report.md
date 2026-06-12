# Target/Radar Backend Matrix

- suite: `target-radar-backend-matrix`
- target radar FOM: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/resources/foms/TargetRadarFOMmodule.xml`
- steps: `4`
- dt: `1.0`
- passed: `1`
- skipped: `0`
- failed: `0`

## Results

| Backend | Status | Track reports | Final range (m) | Final time | Reason |
| --- | --- | ---: | ---: | ---: | --- |
| python | passed | 4 | 11236.298322846364 | 4.0 |  |

## How To Re-run

`./tools/target-radar matrix --output-dir /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/target_radar_backend_matrix`

If a backend is skipped or failed, the reason above should point to the missing runtime, jar, classpath, or loopback/socket configuration that needs to be fixed.
