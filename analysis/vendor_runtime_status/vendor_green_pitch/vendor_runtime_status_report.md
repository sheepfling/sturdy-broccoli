# Vendor Runtime Status

- lane: `vendor-green`
- overall classification: `environment-blocked`
- exit code: `1`
- artifact dir: `/private/var/folders/v8/h5gvd6pd54x7vhtkwqh5s34w0000gn/T/pytest-of-rick/pytest-446/test_vendor_green_fails_strict0/preflight`

## Vendors

| Vendor | Classification | Environment | Exit | Blocked Reason | Artifact | Note |
| --- | --- | --- | ---: | --- | --- | --- |
| pitch | environment-blocked | docker-blocked | 1 | docker | /private/var/folders/v8/h5gvd6pd54x7vhtkwqh5s34w0000gn/T/pytest-of-rick/pytest-446/test_vendor_green_fails_strict0/preflight/pitch-preflight.json | host/runtime prerequisites are blocked on this surface |

Blocked checks for `pitch`:
- `docker`: missing: install Docker Desktop or Docker Engine first
- `pitch_bundle`: blocked: HLA2010_PITCH_HOME does not point at a Pitch runtime directory: /private/var/folders/v8/h5gvd6pd54x7vhtkwqh5s34w0000gn/T/pytest-of-rick/pytest-446/test_vendor_green_fails_strict0/missing-pitch-home
- `pitch_user_home`: missing user.home

Required ports for `pitch`:
- `crc`: `127.0.0.1:8989` [ok]
- `fedpro`: `127.0.0.1:15164` [ok]

Next steps for `pitch`:
- `fix the blocked prerequisite(s) above and rerun`
