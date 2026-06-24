# Vendor Runtime Status

- lane: `vendor-green`
- overall classification: `environment-blocked`
- exit code: `1`
- artifact dir: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/preflight_artifacts`

## Vendors

| Vendor | Classification | Environment | Exit | Blocked Reason | Artifact | Note |
| --- | --- | --- | ---: | --- | --- | --- |
| certi | ready | loopback-ok | 0 |  | /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/preflight_artifacts/certi-preflight.json | vendor runtime prerequisites are ready |

Required markers for `certi`:
- `active_build_root`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/patched/build/libRTI/ieee1516-2010`
- `active_prefix`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/patched/install/bin/rtig`
- `patched_build_root`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/patched/build/libRTI/ieee1516-2010`
- `patched_prefix`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/patched/install/bin/rtig`
- `upstream_build_root`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/upstream/build/libRTI/ieee1516-2010`
- `upstream_prefix`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/upstream/install/bin/rtig`

Next steps for `certi`:
- `./tools/certi-easy smoke compare`
- `HLA2010_ENABLE_REAL_RTI_SMOKE=1 python3 -m pytest -q tests/vendors/test_certi_real_backend_exchange_matrix.py tests/vendors/test_certi_real_backend_time_matrix.py tests/vendors/test_certi_real_backend_ownership_matrix.py`
| pitch | environment-blocked | docker-blocked | 1 | docker | /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/preflight_artifacts/pitch-preflight.json | host/runtime prerequisites are blocked on this surface |

Blocked checks for `pitch`:
- `docker`: blocked: Docker CLI exists but the daemon is not reachable

Required markers for `pitch`:
- `runtime_home`: `third_party/pitch/PITCH-prti1516e-manual/lib/prtifull.jar`

Required ports for `pitch`:
- `crc`: `127.0.0.1:8989` [ok]
- `fedpro`: `127.0.0.1:15164` [ok]

Next steps for `pitch`:
- `fix the blocked prerequisite(s) above and rerun`
