# Networked Python RTI

Use this guide when you want a Python-backed RTI surface to run behind a
transport host instead of directly in-process.

This repo currently has two different hosted Python stories:

- the 2010 hosted Python RTI route over gRPC
- the bounded 2025 hosted FedPro gRPC route over the current 2025 lane

Those routes are related, but they are not identical claims.

- the 2010 route is the familiar hosted form of the pure Python in-memory RTI
- the 2025 route is a typed FedPro transport-hosted slice over the current
  `hla-backend-shim` implementation lane

If you need the architecture and evidence posture for that 2025 lane, read
[`python_rti_backend.md`](python_rti_backend.md) and
[`plans/2025_requirements_finish_line.md`](plans/2025_requirements_finish_line.md)
and
[`plans/2025_python_rti_backend_audit.md`](plans/2025_python_rti_backend_audit.md)
alongside this page.

## Hosted 2010 Python Route

This is the classic hosted Python RTI path:

- `hla.backends.inmemory` for the in-memory RTI implementation
- `hla.transports.grpc` for the transport host and client wiring
- `hla.rti.create_rti_ambassador(...)` for backend selection

Use it when you want:

- the Python RTI semantics you already use locally
- a separate process boundary for testing or deployment
- the same federate code to work with direct and hosted 2010 routes

Start a hosted Python RTI server:

```python
from hla.backends.inmemory import InMemoryRTIEngine
from hla.transports.grpc import start_python_grpc_server

engine = InMemoryRTIEngine()
server = start_python_grpc_server(engine=engine)
print(server.target)
```

Connect a federate to that host:

```python
from hla.rti import create_rti_ambassador

rti = create_rti_ambassador(
    "python",
    transport={"kind": "grpc", "target": server.target},
)
```

That route is the documented Python RTI over gRPC path in
[`backend_route_inventory_routes.md`](backend_route_inventory_routes.md).

## Hosted 2025 FedPro Route

The 2025 hosted path is narrower and more explicit.

It is not documented as a generic "remote Python RTI" abstraction. It is the
current transport-hosted FedPro route over the live Python 2025 lane.

The relevant pieces are:

- `packages/hla-backend-shim` for the current executable 2025 backend lane
- `hla.transports.grpc.python_server_2025.start_2025_grpc_server(...)` for the
  hosted server helper
- `GrpcTransport(GrpcTransportConfig(..., schema="rti1516_2025"))` for the
  typed FedPro 2025 client path

Minimal server shape:

```python
from hla.transports.grpc.python_server_2025 import start_2025_grpc_server

server = start_2025_grpc_server()
print(server.target)
```

Minimal typed transport shape:

```python
from hla.transports.common.transport import TransportRequest
from hla.transports.grpc import GrpcTransport, GrpcTransportConfig

transport = GrpcTransport(
    GrpcTransportConfig(target=server.target, schema="rti1516_2025")
).start()

response = transport.request(TransportRequest(command="CONNECT", fields=("EVOKED", "")))
```

This is the path exercised directly in
[`../tests/transport/test_grpc_transport_2025.py`](../tests/transport/test_grpc_transport_2025.py).

Treat the 2025 hosted route as:

- real executable runtime evidence
- parity-covered against the tracked Python 2025 milestones
- still a bounded FedPro runtime slice rather than a blanket full-semantics or
  full-MOM conformance claim

## Operator Lane

The maintained verification lane for these hosted surfaces is:

```bash
./tools/python verify-routes-preflight
./tools/python verify-routes
```

That lane runs the shared direct-versus-hosted Python parity suite, the hosted
Python gRPC transport tests, regenerates the route parity matrix artifact, and
reruns the tracked route scenarios over the supported hosted paths.

Treat it as regular hygiene after changes to:

- Python RTI backend semantics that should survive the transport boundary
- hosted transport client or server wiring
- route-parity fixtures, docs, or operator wrappers
- hosted Python example or Target/Radar route selection
- the bounded 2025 FedPro hosted lane

## Typical Example Flow

For a full runnable example on the shared scenario side, start with:

- [`../examples/target_radar_simulation.py`](../examples/target_radar_simulation.py)
- [`../packages/hla-fom-target-radar/README.md`](../packages/hla-fom-target-radar/README.md)

The Target/Radar package owns the repo-internal scenario helpers:

- `target_radar_fom_path()`
- `make_target_radar_factory(...)`
- `run_target_radar_scenario(...)`

If you want to write your own runner, keep the shape simple:

1. choose the backend or hosted route
2. create the RTI ambassador
3. load the owning package's FOM path
4. call the reusable scenario helper

## Extending The Example

If you are adding a new Target/Radar variation, keep the reusable logic in
`hla.foms.target_radar._internal` and keep the CLI wrapper thin.

Good extension points are:

- a new scenario factory function in `packages/hla-fom-target-radar/src/hla/foms/target_radar/_internal/`
- a new example script under `examples/`
- a new backend or transport test that reuses the same scenario helper

Do not duplicate the FOM XML under `examples/`; keep reusable assets in the
owning package root.

## Related Docs

- [`README.md`](../README.md)
- [`python_rti_backend.md`](python_rti_backend.md)
- [`python_environment.md`](python_environment.md)
- [`package_layout.md`](package_layout.md)
- [`import_boundary_rules.md`](import_boundary_rules.md)
- [`plans/2025_requirements_finish_line.md`](plans/2025_requirements_finish_line.md)
- [`backend_route_inventory_remote.md`](backend_route_inventory_remote.md)
- [`../packages/hla-transport-grpc/README.md`](../packages/hla-transport-grpc/README.md)
