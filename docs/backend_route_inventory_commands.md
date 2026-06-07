# Backend Route Inventory: Commands

These are the commands that exercise the current backend routes.

### Patched CERTI

```bash
./scripts/ci/vendor_runtime_smoke.sh certi-patched
```

### Upstream vs patched CERTI attribution

```bash
./scripts/ci/vendor_runtime_smoke.sh certi-compare
```

### Pitch

```bash
./scripts/ci/vendor_runtime_smoke.sh pitch
```

Simplest operator path:

```bash
./scripts/pitch_docker_easy.sh install
./scripts/pitch_docker_easy.sh start
./scripts/pitch_docker_easy.sh smoke
```

Quickstart:

- [pitch_docker_quickstart.md](pitch_docker_quickstart.md)

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
