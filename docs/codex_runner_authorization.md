# Codex Runner Authorization Draft

This page is a draft request for Codex runner or sandbox owners.

Use it when:

- hosted Python gRPC checks report `python-grpc: blocked`
- `./tools/python verify-routes-preflight --json` reports `loopback: blocked`
- the machine itself is healthy, but the managed Codex session denies loopback sockets

This is not a repo-code change. It is an execution-policy change.

## Requested Capability

Allow Codex verification sessions to use local TCP loopback sockets on
`127.0.0.1` ephemeral ports.

Minimum operations required:

- `bind(("127.0.0.1", 0))`
- `listen()`
- `accept()`
- `connect()` back to the loopback listener

Scope:

- local host loopback only
- ephemeral ports only
- no external network access required
- no fixed port exposure required

## Why This Is Needed

The hosted Python gRPC RTI route runs the same backend semantics behind a
transport boundary. To verify parity honestly, the route must be allowed to:

1. start a local gRPC server
2. connect local clients back to that server
3. run the same semantic scenario suite as the in-process Python backend

Without loopback socket permission, the route is blocked before the transport
path starts, even though the backend itself is healthy.

## Commands That Need This Authorization

- `./tools/python verify-routes-preflight`
- `./tools/python verify-routes`
- `./tools/python verify-routes-2025`
- `python3 -m pytest -q tests/scenarios/test_python_route_parity.py -k grpc`
- `python3 -m pytest -q tests/transport/test_grpc_transport_2025.py`
- `./tools/target-radar matrix`

Route split:

- `./tools/python verify-routes` is the older 2010 hosted Python parity lane
- `./tools/python verify-routes-2025` is the bounded hosted IEEE 1516.1-2025
  lane over the main `hla-backend-python2025` runtime

## Preferred Implementation

### Option 1. Default runner capability

Grant the verification runner or Codex session profile permission to bind,
listen, accept, and connect on `127.0.0.1` ephemeral ports.

This is the preferred long-term fix.

### Option 2. Persistent unsandboxed approval path

If the managed sandbox cannot allow loopback sockets directly, route the
commands above through an unsandboxed execution path with a durable approval
rule.

This is an acceptable fallback.

## Draft Policy Shape

The exact platform syntax may differ. The intent should be equivalent to this:

```yaml
codex_runner_policy:
  profile: verification
  network:
    outbound_internet: deny
    local_loopback:
      allow: true
      hosts:
        - 127.0.0.1
      ports: ephemeral
      operations:
        - bind
        - listen
        - accept
        - connect
  command_overrides:
    - match:
        - ./tools/python verify-routes-preflight
        - ./tools/python verify-routes
        - ./tools/python verify-routes-2025
        - python3 -m pytest -q tests/scenarios/test_python_route_parity.py -k grpc
        - python3 -m pytest -q tests/transport/test_grpc_transport_2025.py
        - ./tools/target-radar matrix
      require_external_network: false
      require_loopback: true
```

If your platform cannot express loopback separately from broader networking,
the minimum acceptable equivalent is:

- allow local `127.0.0.1` TCP sockets
- continue denying arbitrary external network access

## Acceptance Checks

After the policy change, these commands should pass on the same Codex surface:

```bash
./tools/python verify-routes-preflight --json
python3 -m pytest -q tests/scenarios/test_python_route_parity.py -k grpc
./tools/python verify-routes
python3 -m pytest -q tests/transport/test_grpc_transport_2025.py
./tools/python verify-routes-2025
```

Expected preflight result:

- `loopback: ok`
- `grpc_import: ok`
- `python_grpc: runnable`

Expected parity result:

- the `python-grpc` route passes the same semantic assertions as `python-direct`
- the bounded `python1516_2025-fedpro-grpc` route passes the same hosted-route
  identity and parity assertions as the direct `python1516_2025` lane

## Copyable Change Request

Requested change:

Allow Codex verification sessions to open local TCP loopback listeners on
`127.0.0.1` ephemeral ports and connect back to them.

Required operations:

- `bind`
- `listen`
- `accept`
- `connect`

Rationale:

Hosted Python gRPC verification requires local loopback sockets to start a
transport host and connect local clients back to it. The current managed
sandbox blocks that with `PermissionError: [Errno 1] Operation not permitted`,
which prevents required parity testing. External network access is not needed.

## Related Repo Docs

- [python_environment.md](python_environment.md)
- [vendor_runtime_runner_guide.md](vendor_runtime_runner_guide.md)
- [vendor_runner_provisioning.md](vendor_runner_provisioning.md)
