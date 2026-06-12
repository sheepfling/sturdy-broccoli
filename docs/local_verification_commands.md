# Local Verification Commands

These are the commands captured in the latest local verification note.

```bash
./tools/lint
./tools/test
./tools/python verify
./tools/vendor-green matrix
./tools/two-federate --output-dir analysis/python_two_federate_suite_2026-06-07
python3 -m pytest -q tests/runtime/test_real_rti.py
./tools/certi-easy verify-best-effort
./tools/pitch preflight
./tools/pitch verify
./tools/pitch verify-best-effort
./tools/pitch smoke
./tools/pitch smoke-best-effort
```

Use this page when you want the exact local commands, not the broader status.

Direct real-runtime pytest paths are now secondary diagnostics. Use the vendor
operator path first so preflight is confirmed before the runtime tests start.
Use `./tools/certi-easy verify-best-effort` or the `*-best-effort` Pitch routes
when you need the same normalized artifacts in a sandboxed or local
environment that cannot satisfy the strict vendor runtime prerequisites.
