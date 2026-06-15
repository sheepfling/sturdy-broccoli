# Vendor Runtime Status

- lane: `vendor-green`
- overall classification: `environment-blocked`
- exit code: `1`
- artifact dir: `<tmp>/pytest-of-rick/pytest-2006/test_vendor_green_fails_strict0/preflight`

## Vendors

| Vendor | Classification | Environment | Exit | Blocked Reason | Artifact | Note |
| --- | --- | --- | ---: | --- | --- | --- |
| pitch | environment-blocked | docker-blocked | 1 | docker | <tmp>/pytest-of-rick/pytest-2006/test_vendor_green_fails_strict0/preflight/pitch-preflight.json | host/runtime prerequisites are blocked on this surface |

Blocked checks for `pitch`:
- `docker`: blocked: Docker CLI exists but the daemon is not reachable
- `pitch_bundle`: blocked: archive exists at <repo>/third_party/pitch/HLA_PITCH_linux.zip but extraction failed
- `pitch_user_home`: missing user.home

Required ports for `pitch`:
- `crc`: `127.0.0.1:8989` [ok]
- `fedpro`: `127.0.0.1:15164` [ok]

Next steps for `pitch`:
- `fix the blocked prerequisite(s) above and rerun`
