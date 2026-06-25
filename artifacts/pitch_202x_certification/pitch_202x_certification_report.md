# Pitch 202X Certification Packet

- certification state: `vendor-credence-candidate`
- scope: Pitch vendor 202X surface plus trial-safe real-runtime vendor-credence packet; this is not an IEEE 1516-2025 conformance claim.
- surface readiness: `surface-close-bridge-blocked`
- trial-safe route count: `2`

## Executed Runs

| Run | Exit | Duration (s) | Command |
| --- | ---: | ---: | --- |
| preflight | 0 | 0.05 | `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /private/var/folders/v8/h5gvd6pd54x7vhtkwqh5s34w0000gn/T/pytest-of-rick/pytest-532/test_pitch_top_level_wrapper_r0/success_stub.py` |
| surface audit | 0 | 0.057 | `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /private/var/folders/v8/h5gvd6pd54x7vhtkwqh5s34w0000gn/T/pytest-of-rick/pytest-532/test_pitch_top_level_wrapper_r0/success_stub.py` |
| smoke | 0 | 0.057 | `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /private/var/folders/v8/h5gvd6pd54x7vhtkwqh5s34w0000gn/T/pytest-of-rick/pytest-532/test_pitch_top_level_wrapper_r0/success_stub.py` |
| time window future exclusion | 0 | 0.054 | `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /private/var/folders/v8/h5gvd6pd54x7vhtkwqh5s34w0000gn/T/pytest-of-rick/pytest-532/test_pitch_top_level_wrapper_r0/success_stub.py` |
| time window restore state | 0 | 0.049 | `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /private/var/folders/v8/h5gvd6pd54x7vhtkwqh5s34w0000gn/T/pytest-of-rick/pytest-532/test_pitch_top_level_wrapper_r0/success_stub.py` |

## Trial-Safe Scenario Allowlist

| Scenario | Safe | Federates | Operator Route | Vendor Test |
| --- | --- | ---: | --- | --- |
| exchange-smoke | True | 2 | ./tools/pitch smoke | tests/vendors/test_real_vendor_runtime_smoke.py::pitch_java_real_exchange_smoke |
| time-window-future-exclusion | True | 2 | ./tools/pitch time-window-probe | tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_time_window_future_exclusion_matrix |
| time-window-restore-state | True | 2 | ./tools/pitch time-window-restore-state-probe | tests/vendors/test_pitch_real_backend_matrix.py::test_pitch_time_window_restore_state_matrix |

## Known Boundaries

- `adapter-claim-boundary`: The checked-in pitch-202x backend routes still wrap the repo Python 2025 backend and do not count as real vendor-runtime evidence.
- `negotiated-ownership`: Negotiated ownership remains a documented bridge-divergent branch and is intentionally excluded from the 202x-certify promoted claim.
- `time-window-restore-output`: The restore-output Target/Radar proof needs three federates and is outside the current trial-safe Pitch route set.
- `save-restore-ddm-lost-federate`: Save/restore, DDM, and lost-federate remain explicit Pitch gap/probe families and are not part of this 202X certification packet.

## Next Steps

- `./tools/pitch time-window-review 5`
- `./tools/pitch time-window-restore-state-review 5`
- `./tools/pitch negotiated-probe`
