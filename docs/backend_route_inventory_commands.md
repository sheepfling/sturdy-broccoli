# Backend Route Inventory: Commands

These are the commands that exercise the current backend routes.

### Patched CERTI

```bash
./tools/certi-easy preflight
./tools/certi-easy smoke patched
```

### Upstream vs patched CERTI attribution

```bash
./tools/certi-easy preflight
./tools/certi-easy smoke compare
./tools/certi-easy verify-best-effort
```

### Pitch

```bash
./tools/pitch preflight
./tools/pitch smoke
./tools/pitch smoke-best-effort
./tools/pitch verify-best-effort
```

Simplest operator path:

```bash
./tools/pitch install
./tools/pitch start
./tools/pitch smoke
./tools/pitch verify-best-effort
```

### Green lanes

```bash
./tools/python verify
./tools/python verify-routes-2025
./tools/vendor-green matrix
```

Quickstart:

- [pitch_docker_quickstart.md](../packages/hla-vendor-pitch/docs/pitch_docker_quickstart.md)

For IEEE 1516.1-2025 specifically, `./tools/python verify-routes-2025` is the
normal route-level hygiene lane for the direct `python1516_2025` runtime plus the
bounded hosted `python1516_2025-fedpro-grpc` route over
`hla-backend-python2025`.

### Transport-hosted Python RTI

```bash
python3 -m pytest -q tests/transport/test_grpc_transport_python_server.py
python3 -m pytest -q tests/transport/test_rest_transport.py
```

### Transport-hosted CERTI

```bash
./tools/vendor-green certi-patched
python3 -m pytest -q tests/transport/test_grpc_transport_certi_server.py::test_grpc_transport_can_host_certi_exchange_end_to_end
python3 -m pytest -q tests/backends/test_certi_backend_transport.py
```

`./tools/vendor-green certi-patched` promotes only the CERTI-hosted gRPC
exchange scenario into the working baseline. Run the full
`tests/transport/test_grpc_transport_certi_server.py` file only as a probe while
CERTI gRPC synchronization and ownership remain unstable.

Use this page when you want the runnable command set.
