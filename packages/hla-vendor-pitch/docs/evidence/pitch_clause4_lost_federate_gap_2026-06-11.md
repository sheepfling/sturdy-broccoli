# Pitch Clause 4.1.5 Lost-Federate Gap

Date: 2026-06-11

Scope:
- `HLA1516.1-FM-4.1.5-001`
- `HLA1516.1-FM-4.1.5-002`

Current state:
- The shared harness now contains an explicit lost-federate observer scenario:
  - `packages/hla-verification/src/hla/verification/scenario_lost_federate.py`
- The Python backend can execute that scenario with a test-only injected non-orderly loss path:
  - `packages/hla-backend-python1516e/src/hla/backends/python1516e/backend.py::force_federate_loss`
  - `tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_lost_federate_mom_matrix`
- Pitch now also has a smoke-gated real-runtime wrapper for the `pitch-py4j` profile:
  - `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix`
  - the wrapper terminates the victim federate's dedicated Py4J gateway JVM rather than the shared CRC/FedPro runtime
- Pitch `pitch-jpype` now has a smoke-gated child-process probe path built on a shared external-victim harness wrapper:
  - `packages/hla-verification/src/hla/verification/scenario_lost_federate.py::run_external_lost_federate_observer_scenario`
  - `tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_backend_lost_federate_mom_matrix`
  - `tests/vendors/pitch_jpype_lost_federate_child.py`
- The split-package tests now encode the structural bridge difference directly:
  - `tests/test_rti_pitch_split_packages.py::test_pitch_jpype_factory_uses_inprocess_runtime_without_gateway_process`
  - `tests/test_rti_pitch_split_packages.py::test_pitch_py4j_factory_attaches_gateway_process`

Why the family row remains blocked:
- `pitch-py4j` has an executable shared-harness proof path because the plugin retains the launched gateway process handle and the matrix wrapper can terminate that victim-local JVM.
- `pitch-jpype` has a dedicated child-process trigger through the shared external-victim harness wrapper.
- Executed real-runtime evidence from `./tools/pitch lost-federate-probe` still does not produce observer-visible `HLAreportFederateLost` or automatic-resign cleanup on either Pitch bridge.
- After enabling aggressive loss-detection timeouts for the probe lane, the `pitch-jpype` run shows repeated FedPro session-drop and auto-resume cycles instead of a stable lost-federate report, and the `pitch-py4j` run still does not deliver the observer-visible report.
- Enabling `se.pitch.prti1516e.peerHeartbeatIntervalMillis=1000` alongside `CRC.heartbeat.enable=true`, `CRC.heartbeat.interval=1`, and `CRC.heartbeat.action=resign` did not change that result.
- The smoke-gated JPype child-process probe now reports when the child itself emits stderr, and current runs show no child-side diagnostics before death; the only observable failure evidence remains the observer-side FedPro resume loop.
- A current `2026-06-11` run of `./tools/pitch lost-federate-probe` on this Codex surface does not reach the runtime probe at all: `analysis/preflight_artifacts/pitch-preflight.json` reports `environment: docker-blocked`, with Docker unreachable and both required loopback ports (`127.0.0.1:8989`, `127.0.0.1:15164`) blocked as `Operation not permitted`; the paired lane summary/report in `analysis/vendor_runtime_status/vendor_green_pitch_lost_federate_probe/` classify the canonical operator path as `environment-blocked`.
- Because the repo still lacks executed evidence that either real-runtime Pitch bridge produces the lost-federate report and cleanup sequence under the current fault injectors, the family-level Pitch disposition for Clause 4.1.5 remains blocked.

What would unblock promotion:
1. Disable or bypass the Pitch session-resume path for the `pitch-jpype` child-process probe so a killed victim process becomes an unrecoverable federate loss.
2. Confirm whether terminating the `pitch-py4j` gateway JVM is the correct unrecoverable loss trigger for FedPro-backed Pitch, or replace it with a stronger per-federate failure injection.
3. Re-run the combined lost-federate probe until both Pitch profiles produce observer-visible `HLAreportFederateLost` plus the configured automatic-resign consequences.

Current operator hook for that investigation:
- The prepared Pitch user-home now accepts `HLA2010_PITCH_LRC_EXTRA_SETTINGS`
  and `HLA2010_PITCH_FEDPRO_EXTRA_SETTINGS` as newline- or semicolon-separated
  `key=value` overrides, so session-resume or peer-drop candidate settings can
  flow through `./tools/pitch lost-federate-probe` without hand-editing the
  seeded runtime files.

Disposition impact:
- Keep the family-level Clause 4.1.5 Pitch rows as `blocked` until both Pitch profiles have trustworthy lost-federate evidence.
- Keep the `pitch-jpype` profile rows as `blocked` until the subprocess probe stops auto-resuming and emits observer-visible lost-federate evidence.
- Keep the `pitch-py4j` profile rows as `blocked` until the gateway-process fault injector yields observer-visible lost-federate evidence under the real-runtime smoke gate.
