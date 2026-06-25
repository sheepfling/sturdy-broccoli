# hla-transport-grpc

## What This Is

`hla-transport-grpc` is the canonical gRPC transport package.

It owns client/server transport wiring, protobuf schemas, and hosted gRPC
runtime surfaces for the HLA transport routes in this repo.

The bounded FedPro hosted route lives here as transport wiring over the main
2025 runtime lane. It is not a separate RTI family and not the main in-process
implementation lane.
For IEEE 1516.1-2025 specifically, this package carries the bounded IEEE
1516.1-2025 FedPro hosted route variant.
That 2025 server is a bounded hosted route variant over the current Python 2025
lane.

## What This Is Not

It is not:

- a standard HLA API package
- a concrete RTI backend
- the main 2025 runtime lane
- the main in-process implementation lane

Transport is the wire layer. It is not the backend that executes HLA service
semantics.

## When To Open It

Open this package when you need:

- networked RTI routes
- gRPC client or hosted server wiring
- protobuf schema or stub generation work
- a thin vendor-specific gRPC variant over the same RTI semantics

If you are changing runtime semantics, you probably want a backend package
instead.

## Key Entrypoints

Use these when working on the gRPC route:

- `start_python_grpc_server(...)`
- `start_certi_grpc_server(...)`
- `start_2025_grpc_server(...)`
- `GrpcTransportConfig`
- `create_grpc_transport(...)`

Schema imports live under:

- `hla.transports.grpc.fedpro2010`
- `hla.transports.grpc.fedpro2025`

Variant-route scaffold lives under:

- `hla.transports.grpc.vendor_variant`

Use that module when the remote RTI speaks a gRPC dialect that is close to the
current route but not identical. It is the copyable seam for:

- service-name differences
- protobuf field-name differences
- metadata or header injection
- callback-poll RPC naming differences

It also now includes a maintained concrete example:

- `quirky-vendor-grpc`

That example intentionally uses a slightly awkward envelope shape so the repo
shows how to isolate odd wire choices without changing RTI semantics.

Quick comparison:

| Route | Copy this when | Notes |
| --- | --- | --- |
| `vendor-grpc` | the wire is only mildly different | simplest thin-adapter starting point |
| `quirky-vendor-grpc` | the wire has awkward wrappers or naming | maintained proof that odd envelopes can still stay at the transport edge |

## Related Docs

- [`../../docs/repo_mental_model.md`](../../docs/repo_mental_model.md)
- [`../../docs/networked_rti_python.md`](../../docs/networked_rti_python.md)
- [`../../docs/import_boundary_rules.md`](../../docs/import_boundary_rules.md)
- [`docs/README.md`](docs/README.md)

Regenerate stubs with:

```bash
python packages/hla-transport-grpc/scripts/generate_fedpro2010_stubs.py
```

This package does not own human operator entrypoints; those live under
`./tools/`.

Guard coverage lives in:

- `tests/test_rti_transport_grpc_split_package.py`
- `tests/test_package_boundary.py`
- `tests/test_backend_wrapper_policy.py`
