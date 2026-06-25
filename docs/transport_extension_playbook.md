# Transport Extension Playbook

Use this page when the question is:

"We have a transport that is close to the current `grpc` or `rest` route, but
not identical. How do we adapt it without rewriting the RTI?"

This is the concrete implementation guide for transport changes that are likely
to happen next:

- a vendor-specific gRPC surface that is close to FedPro but not identical
- a gRPC layer with different service names or metadata rules
- a new HTTP or message-bus route
- a new hosted route that should still preserve the same ambassador semantics

## One-Page Gameplay

If your RTI speaks a slightly different gRPC language, this should be the
default approach.

### The Goal

Keep the route-specific differences boring and local.

That means:

- Python federate code should not care that the gRPC wire is vendor-specific
- backend/runtime semantics should remain unchanged
- route-specific quirks should live in one transport adapter layer

### The Quick Decision Rule

Use the lightweight variant-gRPC path if all of these are true:

- the route is still request/response
- callbacks are still exposed through explicit polling
- the logical RTI commands are still the same
- the differences are mostly message names, service names, metadata, or payload
  wrapping

Do not use the lightweight path if either of these is true:

- callback delivery becomes stream or push based
- the route changes what RTI services mean rather than how they are encoded

### The Operator Recipe

1. write down the exact wire differences
2. keep `TransportRequest` and `TransportResponse` fixed
3. create a route-local wire adapter
4. create a route-local `RTITransport`
5. register a distinct transport kind such as `vendor-grpc`
6. prove the route with focused tests before wiring it into broader scenarios
7. document it as a transport variant, not a new RTI family

### The Four Things To Capture First

Before coding, write down:

1. request RPC name differences
2. response payload shape differences
3. callback polling RPC differences
4. extra metadata, auth, or header requirements

If those four items fit on one page, the route is probably a good candidate
for the lightweight adapter path.

## The Main Rule

Do not change the HLA ambassador semantics because the wire changed.

Keep these layers separate:

- backend/runtime: HLA behavior
- transport: wire format and connection mechanics
- bridge/adapter: value conversion between the wire and the normalized transport
  request model

If the change is "how bytes move," it belongs in the transport seam.

If the change is "what `RTIambassador` means," it belongs in the backend or
runtime seam.

## What Already Exists

The repo already has the right low-level seams:

- `TransportRequest` and `TransportResponse`
  - [`../packages/hla-transport-common/src/hla/transports/common/transport.py`](../packages/hla-transport-common/src/hla/transports/common/transport.py)
- `RTITransport`
  - [`../packages/hla-transport-common/src/hla/transports/common/transport.py`](../packages/hla-transport-common/src/hla/transports/common/transport.py)
- `register_transport_factory(...)` and `coerce_transport_spec(...)`
  - [`../packages/hla-transport-common/src/hla/transports/common/transport_registry.py`](../packages/hla-transport-common/src/hla/transports/common/transport_registry.py)
- backend-neutral hosted request processor
  - [`../packages/hla-transport-common/src/hla/transports/common/hosted_server.py`](../packages/hla-transport-common/src/hla/transports/common/hosted_server.py)
- concrete route examples
  - [`../packages/hla-transport-grpc/src/hla/transports/grpc/transport.py`](../packages/hla-transport-grpc/src/hla/transports/grpc/transport.py)
  - [`../packages/hla-transport-rest/src/hla/transports/rest/__init__.py`](../packages/hla-transport-rest/src/hla/transports/rest/__init__.py)
  - [`../packages/hla-transport-rest/src/hla/transports/rest/client.py`](../packages/hla-transport-rest/src/hla/transports/rest/client.py)

That means a new route does not need a new ambassador API. It needs a new
transport adapter.

## Choose The Smallest Change

There are four common cases.

### Case 1: Same Logical Commands, Slightly Different gRPC Wire

Examples:

- different protobuf message names
- different service name
- extra metadata headers
- a vendor field wrapped around the same payload

Recommended approach:

- keep the route as a gRPC-family transport
- add a new client adapter for that wire
- add a route-local transport class or config variant
- keep the backend-facing request model as `TransportRequest`

This is the cheapest and cleanest change.

### Case 2: Same Hosted RTI Semantics, Different Remote Protocol

Examples:

- HTTP+JSON variant
- WebSocket request channel
- ZeroMQ or message-bus envelope

Recommended approach:

- implement a new `RTITransport`
- encode/decode `TransportRequest` and `TransportResponse`
- reuse `HostedRTICommandProcessor` on the server side if the command model is
  still request/response

This keeps the transport swap below the backend semantic layer.

### Case 3: Same Transport Family, Different Callback Delivery Model

Examples:

- callback stream instead of `evokeCallback` polling
- server-push notifications
- multiplexed callback channel

Recommended approach:

- treat this as a bigger architectural change
- keep the ambassador semantics fixed
- make the callback delivery contract explicit in docs and tests

This is not just a wire tweak. It changes the transport interaction model.

### Case 4: Totally New Route Family

Examples:

- external brokered transport
- custom vendor gateway
- a transport that does not resemble current `grpc` or `rest`

Recommended approach:

- create a new `hla-transport-*` package
- keep the same transport registry and `RTITransport` contract
- reuse backend/runtime packages instead of cloning them

## Exact Extension Points

### 1. The Transport Contract

Every route should reduce to:

```python
from hla.transports.common import RTITransport, TransportRequest, TransportResponse
```

Implement:

- `start()`
- `request(request: TransportRequest) -> TransportResponse`
- `close()`

That is the stable seam.

### 2. Transport Registration

Register the route so normal backend creation can discover it:

```python
from hla.transports.common import register_transport_factory

register_transport_factory("vendor-grpc", lambda spec: create_vendor_grpc_transport(...))
```

Or, from the higher-level API:

```python
from hla.rti import register_transport_factory

register_transport_factory("vendor-grpc", factory, aliases=("vendor-grpc-v2",))
```

Relevant code:

- [`../packages/hla-transport-common/src/hla/transports/common/transport_registry.py`](../packages/hla-transport-common/src/hla/transports/common/transport_registry.py)
- [`../packages/hla-rti-core/src/hla/rti/factory.py`](../packages/hla-rti-core/src/hla/rti/factory.py)

### 3. The Hosted Server Processor

If your route is a hosted RTI route, do not reimplement RTI semantics in the
server. Reuse:

- [`../packages/hla-transport-common/src/hla/transports/common/hosted_server.py`](../packages/hla-transport-common/src/hla/transports/common/hosted_server.py)

That processor already maps command requests onto the RTI surface.

### 4. Route-Local Wire Adapters

Use a route-local adapter class for DTO or protobuf conversion.

Current pattern:

- REST has `RestTransportClientAdapter`
- gRPC has edition-local client adapters under the gRPC package

This is where field reshaping should live.

## Recommended Patterns

### Pattern A: Variant gRPC Adapter

Use this when the vendor wire is "FedPro-like but not exactly FedPro."

Implementation shape:

1. create `VendorGrpcTransportConfig`
2. create `VendorGrpcWireAdapter`
3. create `VendorGrpcTransport(RTITransport)`
4. register `vendor-grpc`

Minimal skeleton:

```python
from dataclasses import dataclass

from hla.transports.common import RTITransport, TransportRequest, TransportResponse, register_transport_factory


@dataclass(frozen=True)
class VendorGrpcTransportConfig:
    target: str
    timeout: float = 30.0
    metadata: dict[str, str] | None = None


class VendorGrpcWireAdapter:
    def encode_request(self, request: TransportRequest):
        ...

    def decode_response(self, request: TransportRequest, response) -> TransportResponse:
        ...

    def encode_callback_poll(self):
        ...

    def decode_callback_request(self, response) -> TransportResponse:
        ...


class VendorGrpcTransport(RTITransport):
    def __init__(self, config: VendorGrpcTransportConfig):
        self.config = config
        self.adapter = VendorGrpcWireAdapter()
        self._channel = None
        self._stub = None

    def start(self) -> "VendorGrpcTransport":
        ...
        return self

    def request(self, request: TransportRequest) -> TransportResponse:
        ...

    def close(self) -> None:
        ...


register_transport_factory(
    "vendor-grpc",
    lambda spec: VendorGrpcTransport(VendorGrpcTransportConfig(**dict(spec.options))),
)
```

Why this is preferred:

- transport-specific differences stay isolated
- backend semantics do not move
- Python federate code still sees the same RTI behavior

### Generic Vs Quirky Example

The repo now carries both a generic variant seam and a deliberately awkward
concrete example under
[`../packages/hla-transport-grpc/src/hla/transports/grpc/vendor_variant.py`](../packages/hla-transport-grpc/src/hla/transports/grpc/vendor_variant.py).

Use them like this:

| Route | Purpose | Wire shape | When to copy |
| --- | --- | --- | --- |
| `vendor-grpc` | minimal near-FedPro variant seam | direct `rpc` + `payload.fields` + simple callback fields | when the vendor route is only mildly different |
| `quirky-vendor-grpc` | concrete odd-envelope example | `capsule.items`, `result.values`, `callbackEnvelope.arguments` | when the vendor route has an awkward wrapper or naming style |

Practical rule:

- start from `vendor-grpc` if the differences are small
- start from `quirky-vendor-grpc` if you need to prove that odd envelopes can
  still stay isolated at the transport edge

What both examples keep fixed:

- `TransportRequest`
- `TransportResponse`
- `RTITransport`
- Python-facing RTI semantics

### Pattern A Gameplay Checklist

Use this checklist when the vendor wire is "FedPro-like but not exactly
FedPro."

#### 1. Classify The Difference

Put each difference in one bucket:

- service naming
- protobuf field naming
- wrapper or envelope shape
- metadata or header rules
- callback polling naming
- auth or bootstrap rules

If you discover a callback stream or a semantic service change, stop and widen
the design discussion. That is no longer a thin gRPC variant.

#### 2. Keep The Stable Surface Fixed

Do not change:

- `RTITransport`
- `TransportRequest`
- `TransportResponse`
- Python-facing `RTIambassador` method names

Those are the stable compatibility surfaces.

#### 3. Create The Smallest Route Artifact

Start with one of these package shapes:

- small variant module under `hla.transports.grpc.vendor_variant`
- separate installable package such as `hla-transport-vendor-grpc` only if the
  route is materially distinct

Default recommendation:

- same family, small differences: stay under `hla-transport-grpc`
- new family or large divergence: separate package

#### 4. Put The Weirdness In The Adapter

The adapter should own:

- request encoding
- response decoding
- callback poll request encoding
- callback poll response decoding
- metadata injection and route-local header policy

The adapter should not own:

- HLA service semantics
- RTI state transitions
- scenario orchestration policy

#### 5. Register The Transport Explicitly

Use a clear transport kind such as:

- `vendor-grpc`
- `vendor-grpc-v2`
- `acme-grpc`

That keeps route selection explicit in tests and operator commands.

#### 6. Prove It In Layers

Use this proof order:

1. adapter unit tests
2. transport request/response tests
3. callback-polling integration tests
4. one shared two-federate scenario over the new transport kind

Suggested questions:

- does one command encode correctly
- does one response decode correctly
- does callback polling still work
- does a shared scenario pass without route-specific scenario logic

#### 7. Document The Boundary

Write down:

- what is different on the wire
- what remains identical semantically
- whether callbacks are still explicit polling
- what auth or bootstrap metadata the route requires

That turns the route into a maintainable pattern instead of tribal knowledge.

### Pattern B: New Non-gRPC Hosted Route

Use this when the hosted route is real, but the protocol is not close enough to
FedPro to pretend it is gRPC.

Implementation shape:

1. create a transport client class
2. create a route-local server host
3. server host decodes the wire into `TransportRequest`
4. server host passes requests to `HostedRTICommandProcessor`
5. encode the `TransportResponse` back onto the wire

Minimal server sketch:

```python
from hla.transports.common.hosted_server import HostedRTICommandProcessor


class VendorHostedServer:
    def __init__(self, processor: HostedRTICommandProcessor):
        self.processor = processor

    def handle_wire_request(self, payload: bytes) -> bytes:
        request = decode_vendor_request(payload)
        response = self.processor.handle_request(request)
        return encode_vendor_response(response)
```

### Pattern C: Compatibility Shim Over Existing gRPC

Use this when the only real differences are:

- extra metadata
- different schema alias spelling
- different target discovery

In that case, do not create a whole new package first.

Instead:

- wrap `GrpcTransportConfig`
- inject metadata or service selection in a thin route-local class
- reuse as much of the current gRPC transport as possible

## Recommended Package Shapes

If the route is small and variant-only:

- add a route-local module under the owning transport family package

Examples:

- `hla.transports.grpc.vendor_variant`
- `hla.transports.rest.vendor_variant`

If the route is a new transport family:

- create a new installable package such as `hla-transport-vendor-grpc`
  or `hla-transport-websocket`

Rule of thumb:

- one more DTO or service-name variant: stay in the existing family package
- materially different protocol surface: create a new transport package

## What Not To Do

- do not fork `RTIambassador` or `FederateAmbassador`
- do not reimplement RTI semantics in the transport host
- do not put vendor runtime meaning into protobuf or JSON conversion layers
- do not treat a transport variant as a separate RTI family unless it actually
  owns different semantics

## Testing Expectations

For a new route or transport variant, prove it at four levels.

### 1. Transport Unit Tests

Test:

- request encoding
- response decoding
- error mapping
- callback polling or callback delivery conversion

### 2. Hosted Route Integration Tests

Test:

- one or two core lifecycle calls
- callback round trip
- at least one object or interaction delivery path

### 3. Route-Parity Scenario Tests

Reuse existing shared scenarios when possible.

That is how the route proves it did not silently change semantics.

### 4. Documentation Anchors

Update:

- route inventory
- capability matrix
- this playbook if the new route introduces a genuinely new adaptation pattern

## Recommended Immediate Improvement For This Repo

If the credible near-term scenario is "slightly different gRPC," the most
pragmatic next step is:

1. keep `TransportRequest` and `HostedRTICommandProcessor` as the fixed center
2. create a dedicated variant-gRPC adapter pattern
3. document that pattern as the default answer for near-FedPro vendor routes
4. add one thin custom-route example or test fixture when the first real variant
   arrives

That gives us a stable policy:

- same RTI semantics
- variant wire adapters
- route registration through the shared transport registry

## Copyable Delivery Plan

If you need to hand this off, use this plan:

1. create a short route note listing the wire deltas
2. implement `VendorGrpcWireAdapter`
3. implement `VendorGrpcTransport`
4. register `vendor-grpc`
5. add adapter tests with fixed payload fixtures
6. add one focused callback-polling route test
7. add one two-federate scenario smoke using the new transport kind
8. add a short README note saying the route is a transport variant, not a new
   RTI

## The Easy Answer

When this question comes up again, the default answer should be:

"If the RTI speaks a slightly different gRPC language, keep the RTI surface
stable and write a thin transport adapter. Treat it as a route variant, not a
new RTI."

If the vendor wire is awkward enough that people doubt this can stay thin, show
them `quirky-vendor-grpc` as the maintained proof that even an odd envelope can
still fit the same transport seam.

## Read Next

1. [`extending_ambassador_transports.md`](extending_ambassador_transports.md)
2. [`networked_rti_python.md`](networked_rti_python.md)
3. [`../packages/hla-transport-grpc/README.md`](../packages/hla-transport-grpc/README.md)
4. [`../packages/hla-transport-rest/README.md`](../packages/hla-transport-rest/README.md)
