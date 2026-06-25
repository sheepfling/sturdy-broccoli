# Extending Ambassador Transports

Use this page when the question is:

"How do ambassador connections and wire formats work here, and where do I add a
new one without turning transport choices into a second RTI API?"

This is the consolidated extension guide for:

- in-process routes
- remote transport-hosted routes
- Java bridge routes
- wire-format extension points

If you have not already classified the problem, start one step higher at
[`work_surfaces.md`](work_surfaces.md).

## One-Page Summary

The repo has one main rule:

- keep HLA ambassador semantics in the RTI/backend layer
- keep connection and wire-format mechanics at the route/transport edge

That means:

- `RTIambassador` behavior belongs in backend/runtime packages
- `grpc`, `rest`, JPype, and Py4J belong in transport or bridge packages
- a new connection route should reuse the same normalized Python-facing RTI
  contract instead of inventing a new ambassador API

If the problem is not mostly transport, branch early:

- mostly backend or route selection:
  [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)
- mostly Java RTI wrapping through JPype or Py4J:
  [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
- mostly FOM shape or authoring:
  [`fom_tooling_front_door.md`](fom_tooling_front_door.md)

If you are deciding where code belongs:

- new HLA service semantics: backend/runtime package
- new remote protocol or envelope: transport package
- new Java process/bridge route: Java bridge package
- vendor-specific startup or quirks: vendor package

## Current Ways To Reach An Ambassador

There are three practical connection shapes in the repo today.

Here, terms like `in-process` and `separate process` describe connection
topology, not canonical backend names.

### 1. Direct Python RTI Routes

This is the simplest runtime path.

- `python1516e`
- `python1516_2025`

Here the Python federate calls a Python RTI implementation directly. There is
no network wire format between the federate and the RTI.

Use this path when:

- you are changing RTI semantics
- you want the fastest local test loop
- you need the clearest debugging surface

### 2. Java Bridge Routes

These adapt a Java RTI into the same Python-facing RTI surface.

- `jpype`: in-process JVM
- `py4j`: separate Java gateway process

Here the ambassador contract is still the standard HLA surface. What changes is
how Python reaches Java and how callbacks are exposed back to Java.

Use this path when:

- the RTI implementation is Java-owned
- you need to wrap a standard Java RTI with minimal Python-specific policy
- you want the same Python federate code to work over JPype or Py4J

### 3. Remote Hosted Transport Routes

These put a transport boundary between the Python federate and a hosted RTI.

- `grpc`
- `rest` / `http-json`

Here the ambassador contract is projected over a request/response transport.

The repo's current hosted story is:

- 2010 Python RTI over `grpc`
- 2010 Python RTI over `rest`
- CERTI over `grpc`
- CERTI over `rest`
- bounded 2025 FedPro hosted route over `grpc`

## Current Route Table

| Route family | In-process | Separate process | Current wire format |
| --- | --- | --- | --- |
| Python RTI 2010 | yes | optional hosted | none directly, `grpc`, `rest` |
| Python RTI 2025 | yes | bounded hosted | none directly, bounded `grpc` |
| Java bridge JPype | yes | no | JPype object bridge |
| Java bridge Py4J | no | yes | Py4J gateway object bridge |
| CERTI hosted | no | yes | subprocess-line, `grpc`, `rest` |

Canonical backend names for the direct Python routes are:

- `python1516e` for IEEE 1516.1-2010
- `python1516_2025` for IEEE 1516.1-2025

Legacy aliases may still exist in parts of the repo for compatibility, but the
documentation should prefer those two names.

Management-level summary:

- JPype is the primary in-process Java story
- Py4J is the alternate process-separated Java story
- `grpc` and `rest` are transport seams, not separate RTI APIs
- the 2025 hosted route is currently the bounded `grpc` FedPro route

## Extension Principle

The lightest protocol approach in this repo is:

1. keep the ambassador API stable
2. adapt calls and callbacks at the edge
3. convert values once in the route-specific adapter
4. avoid transport-specific logic in the backend semantic layer

If a design requires changing normal HLA ambassador method names, callback
shape, or service semantics just because a new wire format was added, it is
probably in the wrong layer.

## Where To Extend

### Add A New Remote Wire Format

Put it in a transport package.

Current reference packages:

- [`../packages/hla-transport-grpc/README.md`](../packages/hla-transport-grpc/README.md)
- [`../packages/hla-transport-rest/README.md`](../packages/hla-transport-rest/README.md)

Use this pattern:

1. define the request/response envelope and codec
2. implement a client transport
3. implement a hosted server adapter
4. map transport requests onto existing backend/runtime operations
5. preserve the existing callback contract or explicitly document the new one

Good fit:

- new protobuf schema family
- alternate HTTP representation
- message framing or serialization change

Bad fit:

- adding backend semantics directly to a transport client
- duplicating RTI service logic inside the server adapter

### Add A New Java Connection Route

Put it parallel to JPype and Py4J and reuse the shared Java common layer.

Current reference packages:

- [`../packages/hla-bridge-java-common/README.md`](../packages/hla-bridge-java-common/README.md)
- [`../packages/hla-bridge-java-jpype/README.md`](../packages/hla-bridge-java-jpype/README.md)
- [`../packages/hla-bridge-java-py4j/README.md`](../packages/hla-bridge-java-py4j/README.md)

Use this pattern:

1. keep edition selection in the shared binding profile layer
2. implement route-local bridge mechanics
3. reuse the shared adapter/value-conversion policy
4. expose the same normalized Python-facing ambassador

Good fit:

- new JVM access mechanism
- new callback exposure mechanism
- new route-local discovery/bootstrap rules

Bad fit:

- reimplementing the full wrapping policy in a vendor package
- making bridge route differences visible to normal federate code

### Add Vendor-Specific Connection Logic

Put vendor quirks in a vendor package, not in the generic bridge or transport
packages.

Good fit:

- runtime discovery
- launch/bootstrap commands
- implementation string selection
- vendor-specific environment checks

Bad fit:

- forking the generic ambassador adaptation contract unnecessarily

## In-Process Vs Remote Decision

Use this decision rule:

- choose the direct Python RTI routes when you are changing or proving RTI
  semantics
- choose JPype when you need the clearest Java wrapping path
- choose Py4J when you need Java process isolation
- choose `grpc` or `rest` when you are testing or deploying a hosted route

If the goal is "extend the wire format", you are in transport territory.

If the goal is "extend how Python wraps a Java RTI", you are in bridge
territory.

If the goal is "extend what the RTI means", you are in backend/runtime
territory.

## Current Callback Contract

For the remote transport routes documented today, the callback contract is:

- unary request/response service calls
- callback polling through `evokeCallback` / `evokeMultipleCallbacks`
- no streaming callback channel today

That contract is called out in:

- [`backend_capability_matrix.md`](backend_capability_matrix.md)
- [`backend_route_inventory_remote.md`](backend_route_inventory_remote.md)

If you introduce streaming callbacks or another callback delivery model, that
is a meaningful architectural change and should be documented as such rather
than treated as an invisible wire swap.

## Recommended Minimal Extension Path

For a lightweight extension:

1. start from the existing normalized ambassador contract
2. copy the closest route family, not the whole runtime
3. keep serialization, connection, and callback plumbing in the edge package
4. prove the route with focused transport or bridge tests
5. leave backend semantics owned by the existing runtime lane

This is the same principle already used for:

- JPype vs Py4J
- `grpc` vs `rest`
- direct 2025 in-process vs bounded 2025 hosted `grpc`

## Best Existing Entry Points

Open these in order depending on the question.

For route inventory:

1. [`backend_route_inventory.md`](backend_route_inventory.md)
2. [`backend_route_inventory_remote.md`](backend_route_inventory_remote.md)
3. [`backend_capability_matrix.md`](backend_capability_matrix.md)

For Java wrapping:

1. [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
2. [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md)
3. [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md)

For hosted transports:

1. [`networked_rti_python.md`](networked_rti_python.md)
2. [`../packages/hla-transport-grpc/README.md`](../packages/hla-transport-grpc/README.md)
3. [`../packages/hla-transport-rest/README.md`](../packages/hla-transport-rest/README.md)

## Read Next

1. [`transport_extension_playbook.md`](transport_extension_playbook.md)
2. [`networked_rti_python.md`](networked_rti_python.md)
3. [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md) if the question broadens back out to backend plus transport plus FOM choice

## Do Not Do This

- do not create a second ambassador API just because the transport is new
- do not move backend semantics into transport clients or transport hosts
- do not let vendor bootstrap code become the generic bridge policy
- do not describe transport routes as separate RTI families unless they really
  own distinct runtime semantics

## Short Answer

Yes, the repo supports extension.

The intended low-coupling seams are:

- backend/runtime for semantics
- bridge packages for Java connection shape
- transport packages for wire format
- vendor packages for vendor quirks

That is the lightest protocol model this repo is aiming for.
