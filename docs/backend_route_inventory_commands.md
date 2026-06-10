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
```

### Pitch

```bash
./tools/pitch preflight
./tools/pitch smoke
```

Simplest operator path:

```bash
./tools/pitch install
./tools/pitch start
./tools/pitch smoke
```

### Green lanes

```bash
./scripts/ci/repo_green.sh
./scripts/ci/vendor_green.sh matrix
```

Quickstart:

- [pitch_docker_quickstart.md](../packages/hla2010-rti-pitch-common/docs/pitch_docker_quickstart.md)

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
