# Vendor Runtime Status

- lane: `vendor-green`
- overall classification: `vendor-green`
- exit code: `0`
- artifact dir: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/preflight_artifacts`

## Vendors

| Vendor | Classification | Environment | Exit | Blocked Reason | Artifact | Note |
| --- | --- | --- | ---: | --- | --- | --- |
| certi | ready | loopback-ok | 0 |  | /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/preflight_artifacts/certi-preflight.json | vendor runtime prerequisites are ready |

Required markers for `certi`:
- `active_build_root`: `<repo>/.local/certi/patched/build/libRTI/ieee1516-2010`
- `active_prefix`: `<repo>/.local/certi/patched/install/bin/rtig`
- `patched_build_root`: `<repo>/.local/certi/patched/build/libRTI/ieee1516-2010`
- `patched_prefix`: `<repo>/.local/certi/patched/install/bin/rtig`
- `upstream_build_root`: `<repo>/.local/certi/upstream/build/libRTI/ieee1516-2010`
- `upstream_prefix`: `<repo>/.local/certi/upstream/install/bin/rtig`

Next steps for `certi`:
- `./tools/certi-easy smoke compare`
- `HLA2010_ENABLE_REAL_RTI_SMOKE=1 python3 -m pytest -q tests/vendors/test_certi_real_backend_exchange_matrix.py tests/vendors/test_certi_real_backend_time_matrix.py tests/vendors/test_certi_real_backend_ownership_matrix.py`
