# Java Bridge Overload Resolution

Use this page when the question is not just "how do I start JPype or Py4J?"
but "how does the repo make the right Java call when the standard HLA Java API
has multiple overloads with similar names and awkward parameter families?"

This document belongs to the backend and route wrapping surface described in
[`work_surfaces.md`](work_surfaces.md).

## Why This Matters

The Java HLA APIs are not a clean one-method-one-shape surface.

Several services rely on overload families that differ by:

- arity
- parameter ordering
- Java collection/interface type
- `String` versus `URL` or `URL[]`
- handle-set versus handle-value-map shapes
- `byte[]` payload forms
- logical-time and logical-time-interval types

If the repo left overload choice entirely to JPype or Py4J, the behavior would
be harder to reason about and harder to keep aligned across both bridge routes.

The bridge layer therefore resolves overload intent in Python first and treats
JPype and Py4J mainly as execution mechanisms after the call shape is already
known.

## Short Version

Outbound Java calls work like this:

1. the Python-facing RTI surface records an `Invocation`
2. the shared bridge layer loads Java overload metadata for that method
3. Python matches candidate overloads by arity and keyword names
4. Python scores ambiguous overloads by expected Java parameter types
5. Python converts arguments to the chosen Java shapes
6. JPype or Py4J executes the already-resolved Java call

Inbound callbacks work similarly:

1. Java invokes a standard `FederateAmbassador` callback
2. the shared dispatcher looks up the expected Java callback signature
3. callback arguments are converted to the matching Python-side shapes
4. the normalized Python callback method is invoked

The important point is that overload selection is a shared Python policy, not
an incidental side effect of one bridge route.

## The Core Files

The main implementation files behind this policy are:

- [`../packages/hla-backend-common/src/hla/backends/common/invocation.py`](../packages/hla-backend-common/src/hla/backends/common/invocation.py)
- [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py)
- [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_binding_profile.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_binding_profile.py)
- [`../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py`](../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py)
- [`../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py`](../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py)

The most useful tests are:

- [`../tests/backends/test_backends.py`](../tests/backends/test_backends.py)
- [`../tests/backends/test_java_factory_selection_helpers.py`](../tests/backends/test_java_factory_selection_helpers.py)
- [`../tests/backends/test_standard_java_shim_routes.py`](../tests/backends/test_standard_java_shim_routes.py)

## Outbound Call Resolution

The shared resolver lives in
[`invocation.py`](../packages/hla-backend-common/src/hla/backends/common/invocation.py).

The main steps are:

1. filter the method's overload metadata to Java overloads
2. map Python kwargs onto Java parameter names
3. reject candidates whose total parameter count does not match
4. score remaining candidates using expected Java parameter types
5. return one resolved overload plus an ordered argument tuple

This means the bridge can accept Python-facing calls such as:

- positional only
- mixed positional and keyword
- snake-case keyword names that correspond to lowerCamel Java names

without leaving the final choice to route-local reflection behavior.

## What Gets Scored

When multiple overloads survive the arity/name pass, the resolver uses Java
type hints from metadata to score the candidates.

Important special cases include:

- `String`
- `URL`
- `URL[]`
- HLA handle-set interfaces
- HLA handle-value-map interfaces
- `AttributeSetRegionSetPairList`
- `byte[]`
- `LogicalTime`
- `LogicalTimeInterval`

That is the main reason the shared bridge layer exists as a policy layer
instead of a thin `getattr(...)(*args)` wrapper.

## Callback Resolution

Inbound callbacks are handled by
[`PythonFederateAmbassadorDispatcher`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py).

The dispatcher does not just forward raw Java objects blindly.

It first asks the binding profile for the expected Java callback parameter
types for the callback method and arity, then converts the values accordingly.

That matters because vendor RTIs frequently return implementation classes
instead of the public Java interface names used in the standard metadata.

## JPype Vs Py4J

The repo tries to keep their semantics aligned, but they are not identical
tools and they should not be described as equivalent at the raw overload level.

### What Is Shared

These are intentionally shared:

- overload metadata source
- arity and keyword matching rules
- candidate scoring rules
- Python-to-Java value-conversion policy
- Java-to-Python callback conversion policy
- normalized Python-facing RTI surface

That shared policy is why the project can talk about one Java adaptation model
instead of two unrelated wrappers.

### What JPype Is Better At

JPype is the stronger direct-Java route when the question is raw API fidelity.

Reasons:

- it runs in-process
- it exposes Java classes directly through `JClass(...)`
- it can create true Java proxies with `JProxy(...)`
- once the repo has shaped the arguments correctly, JVM-side overload dispatch
  is usually easier to reason about

In practice, JPype is the clearest route for:

- debugging overload mismatches
- checking class and interface identities
- understanding exact JVM-side type expectations

### What Py4J Is Better At

Py4J is better when process isolation or external JVM ownership matters.

Reasons:

- the JVM can live separately from Python
- the bridge can attach to an existing Java process shape
- deployment and runtime ownership can be cleaner in some vendor setups

But Py4J is a more indirect object model, so relying on implicit overload
selection there is a worse idea than in JPype.

That is exactly why the repo resolves overload intent in Python first.

### Practical Contrast

The repo's policy can be summarized like this:

- JPype is the preferred inspection and explanation route
- Py4J is a supported transport boundary with the same logical adaptation model
- neither route should be trusted to define overload policy by accident
- the shared resolver must decide the call shape before either route executes it

## Common Failure Modes

When a Java bridge call goes wrong, the problem is usually one of these:

1. the overload metadata does not match the vendor or standard jar actually in use
2. a Python keyword does not map to the expected Java parameter name
3. a Python value is ambiguous across multiple Java overload families
4. a collection-like argument was not converted into the RTI-owned Java factory type
5. a callback arrived through a vendor implementation class that needs the expected signature hint

Those are bridge-policy problems first, not just "JPype broke" or "Py4J broke".

## Concrete Example Categories

The awkward classes of calls this policy exists to protect include:

- federation creation/destruction calls with `String` and module-list overloads
- connect-style calls that gain route-local settings designators
- attribute-handle-set and parameter-handle-value-map calls
- time-management calls that require RTI-owned logical-time objects
- callback families with multiple Java signatures but one normalized Python callback surface

## Reading Order

If you want the shortest path through this topic:

1. [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
2. [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md)
3. this page
4. [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md)
5. [`language_shim_routes.md`](language_shim_routes.md)

If you want the implementation path:

1. [`../packages/hla-backend-common/src/hla/backends/common/invocation.py`](../packages/hla-backend-common/src/hla/backends/common/invocation.py)
2. [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py)
3. [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_binding_profile.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_binding_profile.py)
4. [`../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py`](../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py)
5. [`../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py`](../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py)
