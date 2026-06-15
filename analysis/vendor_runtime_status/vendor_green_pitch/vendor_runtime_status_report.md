# Vendor Runtime Status

- lane: `vendor-green`
- overall classification: `environment-blocked`
- exit code: `1`
- artifact dir: `<tmp>/pytest-of-rick/pytest-1682/test_vendor_green_fails_strict0/preflight`

## Vendors

| Vendor | Classification | Environment | Exit | Blocked Reason | Artifact | Note |
| --- | --- | --- | ---: | --- | --- | --- |
| pitch | environment-blocked | ports-blocked | 1 | crc_port | <tmp>/pytest-of-rick/pytest-1682/test_vendor_green_fails_strict0/preflight/pitch-preflight.json | host/runtime prerequisites are blocked on this surface |

Blocked checks for `pitch`:
- `crc_port`: blocked: 127.0.0.1:8989 is not available: [Errno 48] Address already in use
- `fedpro_port`: blocked: 127.0.0.1:15164 is not available: [Errno 48] Address already in use

Required markers for `pitch`:
- `runtime_home`: `third_party/pitch/PITCH-prti1516e-manual/lib/prtifull.jar`

Required ports for `pitch`:
- `crc`: `127.0.0.1:8989` [blocked]
- `fedpro`: `127.0.0.1:15164` [blocked]

Next steps for `pitch`:
- `fix the blocked prerequisite(s) above and rerun`
