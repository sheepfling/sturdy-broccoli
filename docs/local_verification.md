# Local Verification Note

Date: 2026-06-07

This note records the current local verification state for the thin-wrapper CI
stack and the real runtime matrix.

## Commands Run

```bash
bash ./scripts/ci/lint.sh
bash ./scripts/ci/test.sh
bash ./scripts/ci/vendor_runtime_smoke.sh matrix
python3 scripts/run_two_federate_suite.py --output-dir analysis/python_two_federate_suite_2026-06-07
python3 -m pytest -q tests/runtime/test_real_rti.py
HLA2010_ENABLE_REAL_RTI_SMOKE=1 HLA2010_PITCH_CRC_MODE=docker HLA2010_PITCH_DOCKER_BUILD=0 python3 -m pytest -q tests/vendors/test_pitch_real_backend_matrix.py -rs
HLA2010_ENABLE_REAL_RTI_SMOKE=1 HLA2010_PITCH_CRC_MODE=docker HLA2010_PITCH_DOCKER_BUILD=0 python3 -m pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k pitch -rs
```

## Results

- `lint.sh`: passed
- `test.sh`: `641 passed, 39 skipped`
- `vendor_runtime_smoke.sh matrix`: `14 passed in 79.15s`
- Python two-federate suite: passed and artifacts written under `analysis/python_two_federate_suite_2026-06-07/`
- `tests/runtime/test_real_rti.py`: `21 passed in 0.88s`
- `tests/vendors/test_pitch_real_backend_matrix.py`: `7 passed, 1 warning in 104.99s`
- `tests/vendors/test_real_vendor_runtime_smoke.py -k pitch`: `4 passed, 6 deselected in 54.99s`

## Notes

- The combined `seed_suite.sh` wrapper now retries a transient `SIGKILL` once
  for each stage before failing.
- The real runtime matrix was verified locally with:
  - `HLA2010_CERTI_PREFIX=/private/tmp/hla-2010/CERTI-install`
  - `HLA2010_CERTI_BUILD_ROOT=/private/tmp/hla-2010/CERTI-build`
  - `HLA2010_PITCH_HOME=/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/third_party/pitch/PITCH-prti1516e-manual`
  - `HLA2010_PITCH_USER_HOME=/private/tmp/hla-2010/pitch-user-home`
- The sandbox initially blocked local socket binds for CERTI; rerunning with
  escalated permissions allowed the matrix to complete successfully.
- The sandbox also blocked access to the Docker Desktop socket for the
  Docker-backed Pitch route; rerunning with escalated permissions allowed the
  vendor matrix to complete successfully.
