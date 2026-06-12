# Vendor Runtime Status

- lane: `repo-green`
- overall classification: `repo-green`
- exit code: `0`
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
| pitch | environment-blocked | docker-blocked | 1 | docker | /Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/analysis/preflight_artifacts/pitch-preflight.json | host/runtime prerequisites are blocked on this surface |

Blocked checks for `pitch`:
- `docker`: blocked: Docker CLI exists but the daemon is not reachable
- `crc_port`: blocked: 127.0.0.1:8989 is not available: [Errno 1] Operation not permitted
- `fedpro_port`: blocked: 127.0.0.1:15164 is not available: [Errno 1] Operation not permitted

Required markers for `pitch`:
- `runtime_home`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/third_party/pitch/PITCH-prti1516e-manual/lib/prtifull.jar`

Required ports for `pitch`:
- `crc`: `127.0.0.1:8989` [blocked]
- `fedpro`: `127.0.0.1:15164` [blocked]

Next steps for `pitch`:
- `fix the blocked prerequisite(s) above and rerun`
