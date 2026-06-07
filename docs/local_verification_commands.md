# Local Verification Commands

These are the commands captured in the latest local verification note.

```bash
bash ./scripts/ci/lint.sh
bash ./scripts/ci/test.sh
bash ./scripts/ci/vendor_runtime_smoke.sh matrix
python3 scripts/run_two_federate_suite.py --output-dir analysis/python_two_federate_suite_2026-06-07
python3 -m pytest -q tests/runtime/test_real_rti.py
HLA2010_ENABLE_REAL_RTI_SMOKE=1 HLA2010_PITCH_CRC_MODE=docker HLA2010_PITCH_DOCKER_BUILD=0 python3 -m pytest -q tests/vendors/test_pitch_real_backend_matrix.py -rs
HLA2010_ENABLE_REAL_RTI_SMOKE=1 HLA2010_PITCH_CRC_MODE=docker HLA2010_PITCH_DOCKER_BUILD=0 python3 -m pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k pitch -rs
```

Use this page when you want the exact local commands, not the broader status.
