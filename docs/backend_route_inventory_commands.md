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
./tools/vendor-green matrix
```

Quickstart:

- [pitch_docker_quickstart.md](../packages/hla-vendor-pitch/docs/pitch_docker_quickstart.md)

### Transport-hosted Python RTI

```bash
python3 -m pytest -q tests/transport/test_grpc_transport_python_server.py
python3 -m pytest -q tests/transport/test_rest_transport.py
```

### Transport-hosted CERTI

```bash
python3 -m pytest -q tests/transport/test_grpc_transport_certi_server.py
python3 -m pytest -q tests/backends/test_certi_backend_transport.py
```

Use this page when you want the runnable command set.
