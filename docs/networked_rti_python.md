# Networked Python RTI

Use this guide when you want the pure Python RTI to run behind a transport
host instead of directly in-process.

The supported hosted route is:

- `hla.backends.inmemory` for the in-memory RTI implementation
- `hla.transports.grpc` for the transport host and client wiring
- `hla.rti.create_rti_ambassador(...)` for backend selection

This is the cleanest networked path when you want:

- the Python RTI semantics you already use locally
- a separate process boundary for testing or deployment
- the same federate code to work with direct and hosted routes

## Minimal Shape

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

## Operator Lane

The maintained verification lane for this surface is:

```bash
./tools/python verify-routes-preflight
./tools/python verify-routes
```

That lane runs the shared direct-versus-hosted Python parity suite, the hosted
Python gRPC transport tests, regenerates the route parity matrix artifact, and
reruns the Target/Radar example over both direct and hosted Python routes.

Treat it as regular hygiene after changes to:

- Python RTI backend semantics that should survive the transport boundary
- hosted transport client or server wiring
- route-parity fixtures, docs, or operator wrappers
- hosted Python example or Target/Radar route selection

## Typical Example Flow

For a full runnable example, start with:

- [`../examples/target_radar_simulation.py`](../examples/target_radar_simulation.py)
- [`../packages/hla-fom-target-radar/README.md`](../packages/hla-fom-target-radar/README.md)

The Target/Radar package owns the reusable scenario helpers:

- `target_radar_fom_path()`
- `make_target_radar_factory(...)`
- `run_target_radar_scenario(...)`

If you want to write your own runner, keep the shape simple:

1. choose the backend route
2. create the RTI ambassador
3. load the owning package's FOM path
4. call the reusable scenario helper

## Extending The Example

If you are adding a new Target/Radar variation, keep the reusable logic in
`hla.foms.target_radar.scenarios` and keep the CLI wrapper thin.

Good extension points are:

- a new scenario factory function in `packages/hla-fom-target-radar/src/hla.foms.target_radar/scenarios/`
- a new example script under `examples/`
- a new backend or transport test that reuses the same scenario helper

Do not duplicate the FOM XML under `examples/`; keep reusable assets in the
owning package root.

## Related Docs

- [`README.md`](../README.md)
- [`python_environment.md`](python_environment.md)
- [`package_layout.md`](package_layout.md)
- [`import_boundary_rules.md`](import_boundary_rules.md)
- [`../packages/hla-transport-grpc/README.md`](../packages/hla-transport-grpc/README.md)
