# Federate CLI Change Map

Use this page when the question is:

- "Where do I change the FOM-facing shape?"
- "Where do I change the transport route?"
- "Where do I adapt a slightly different gRPC dialect?"

This is a tiny routing map, not a full architecture document.

## FOM Shape Changes

What this means:

- object class names
- interaction class names
- attribute or parameter names
- datatype names
- packaged scenario FOM selection

Primary files:

- `packages/hla-rti-core/src/hla/fom/resources/proto2025/foms/Proto2025_MessageTest.xml`
- `packages/hla-rti-core/src/hla/fom/resources/`
- `scripts/tools_federate_cli.py`

Primary commands:

- `inspect-class`
- `inspect-interaction`
- `inspect-datatype`
- `list-classes`
- `list-interactions`
- `list-datatypes`

Walkthroughs:

- `message-test-tour`
- `two-federate-callback-tour`

Operator entrypoint:

- `./tools/federate-cli`

## Transport Changes

What this means:

- direct vs hosted route selection
- `grpc` target configuration
- `rest` base URL configuration
- server startup and hosted transport wiring

Primary files:

- `packages/hla-transport-grpc/src/hla/transports/grpc/python_server.py`
- `packages/hla-transport-grpc/src/hla/transports/grpc/python_server_2025.py`
- `packages/hla-transport-rest/src/hla/transports/rest/rest_transport_host.py`
- `scripts/tools_federate_cli.py`

Primary route boundaries:

- 2025 hosted route: gRPC-backed
- 2010 hosted transport substitution example: gRPC and REST

Walkthroughs:

- `route-variation-tour`
- `transport-substitution-tour`

Operator entrypoint:

- `./tools/federate-cli`

Related docs:

- `docs/extending_ambassador_transports.md`
- `docs/transport_extension_playbook.md`

## Adapter Dialect Changes

What this means:

- a remote RTI speaks a slightly different gRPC envelope
- callback poll payloads differ
- RPC names differ
- request/response field wrapping differs
- you need a thin protocol adapter without changing RTI semantics

Primary files:

- `packages/hla-transport-grpc/src/hla/transports/grpc/client_2025.py`
- `packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/hosted_fedpro.py`
- `packages/hla-transport-grpc/src/hla/transports/grpc/vendor_variant.py`
- `packages/hla-transport-common/src/hla/transports/common/transport.py`

Primary swap points:

- `encode_request`
- `decode_response`
- `encode_callback_poll`
- `decode_callback_request`
- helper callback dispatch

Walkthrough:

- `adapter-boundary-tour`

Direct inspection commands:

- `inspect-adapter grpc-fedpro-2025`
- `inspect-adapter grpc-quirky-vendor`

Operator entrypoint:

- `./tools/federate-cli`

## Short Rule

- FOM meaning changed: start with `inspect-class` and `message-test-tour`
- transport lane changed: start with `route-variation-tour` or `transport-substitution-tour`
- wire dialect changed: start with `inspect-adapter` and `adapter-boundary-tour`
