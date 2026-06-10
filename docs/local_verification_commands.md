# Local Verification Commands

These are the commands captured in the latest local verification note.

```bash
bash ./scripts/ci/lint.sh
bash ./scripts/ci/test.sh
bash ./scripts/ci/repo_green.sh
bash ./scripts/ci/vendor_green.sh matrix
python3 scripts/run_two_federate_suite.py --output-dir analysis/python_two_federate_suite_2026-06-07
python3 -m pytest -q tests/runtime/test_real_rti.py
./scripts/pitch_docker_easy.sh preflight
./scripts/pitch_docker_easy.sh verify
./scripts/pitch_docker_easy.sh smoke
```

Use this page when you want the exact local commands, not the broader status.

Direct real-runtime pytest paths are now secondary diagnostics. Use the vendor
operator path first so preflight is confirmed before the runtime tests start.
