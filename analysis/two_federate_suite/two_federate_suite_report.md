# Two-Federate Suite

- suite: `two-federate-suite`
- version: `0.2`
- scenarios: `7`
- track reports: `4`

## Profiles

| Profile | Status | Reason | Scenario rows |
| --- | --- | --- | ---: |
| python | passed |  | 7 |
| certi | failed | rti1516e::FederationExecutionDoesNotExist:  | 0 |
| pitch-jpype | failed | Command '['/usr/libexec/java_home']' returned non-zero exit status 1. | 0 |
| pitch-py4j | failed | invalid literal for int() with base 10: b'' | 0 |

## Coverage

| Scenario | Backend | Callbacks | Key outcome |
| --- | --- | ---: | --- |
| exchange_time | python/in-memory | 13 | receive + timestamp object and interaction delivery |
| synchronization | python/in-memory | 5 | announce and federationSynchronized callbacks |
| ownership | python/in-memory | 6 | divestiture and acquisition if available |
| negotiated_ownership | python/in-memory | 13 | release, cancellation, and reacquisition flow |
| save_restore | python/in-memory | 17 | federationSaved and restore callbacks with restored logical time |
| ddm | python/in-memory | 3 | region-filtered timestamped delivery |
| target_radar | python/in-memory,python/in-memory | 26 | 4 track reports |

## Artifacts

- JSON summary: `two_federate_suite_summary.json`
- Track CSV: `two_federate_track_reports.csv`
- Callback CSV: `two_federate_callbacks.csv`
- SVG summary: `two_federate_suite_summary.svg`
- SVG timeline: `two_federate_suite_timeline.svg`

## Assessment

- A two-federate verification suite exercising exchange, timestamped delivery, synchronization, ownership transfer, negotiated ownership, save/restore, DDM region filtering, and a realistic target/radar flow.
- The default profile runs the Python reference RTI; CERTI and Pitch profiles will record skipped or failed status when their runtimes are unavailable or incomplete.
- The same scenario structure is reused across the python, CERTI, and Pitch runtime profiles.
