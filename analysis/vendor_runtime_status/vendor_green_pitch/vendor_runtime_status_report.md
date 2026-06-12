# Vendor Runtime Status

- lane: `vendor-green`
- overall classification: `environment-blocked`
- exit code: `1`
- artifact dir: `/private/var/folders/v8/h5gvd6pd54x7vhtkwqh5s34w0000gn/T/pytest-of-rick/pytest-1370/test_vendor_green_fails_strict0/preflight`

## Vendors

| Vendor | Classification | Environment | Exit | Blocked Reason | Artifact | Note |
| --- | --- | --- | ---: | --- | --- | --- |
| pitch | environment-blocked | docker-blocked | 1 | docker | /private/var/folders/v8/h5gvd6pd54x7vhtkwqh5s34w0000gn/T/pytest-of-rick/pytest-1370/test_vendor_green_fails_strict0/preflight/pitch-preflight.json | host/runtime prerequisites are blocked on this surface |

Blocked checks for `pitch`:
- `docker`: missing: install Docker Desktop or Docker Engine first
- `crc_port`: blocked: 127.0.0.1:8989 is not available: [Errno 1] Operation not permitted
- `fedpro_port`: blocked: 127.0.0.1:15164 is not available: [Errno 1] Operation not permitted

Required markers for `pitch`:
- `runtime_home`: `/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/third_party/pitch/PITCH-prti1516e-manual/lib/prtifull.jar`

Required ports for `pitch`:
- `crc`: `127.0.0.1:8989` [blocked]
- `fedpro`: `127.0.0.1:15164` [blocked]

Next steps for `pitch`:
- `fix the blocked prerequisite(s) above and rerun`
