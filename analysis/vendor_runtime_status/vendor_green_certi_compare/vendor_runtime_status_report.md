# Vendor Runtime Status

- lane: `vendor-green`
- overall classification: `environment-blocked`
- exit code: `1`
- artifact dir: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/preflight_artifacts`

## Vendors

| Vendor | Classification | Environment | Exit | Blocked Reason | Artifact | Note |
| --- | --- | --- | ---: | --- | --- | --- |
| certi | environment-blocked | loopback-blocked | 1 | loopback_bind | /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/preflight_artifacts/certi-preflight.json | host/runtime prerequisites are blocked on this surface |

Blocked checks for `certi`:
- `loopback_bind`: loopback_bind: blocked: Local socket bind is not permitted for 127.0.0.1. Run `./tools/certi-easy preflight` to verify local CERTI prerequisites. Real RTI smoke needs loopback TCP bind/connect permission for 127.0.0.1.

Required markers for `certi`:
- `active_build_root`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/patched/build/libRTI/ieee1516-2010`
- `active_prefix`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/patched/install/bin/rtig`
- `patched_build_root`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/patched/build/libRTI/ieee1516-2010`
- `patched_prefix`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/patched/install/bin/rtig`
- `upstream_build_root`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/upstream/build/libRTI/ieee1516-2010`
- `upstream_prefix`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/.local/certi/upstream/install/bin/rtig`

Next steps for `certi`:
- `fix the blocked prerequisite above`
- `./tools/certi-easy preflight`
