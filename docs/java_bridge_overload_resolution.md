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

For the adjacent question of how raw `byte[]` payloads and encoder outputs are
preserved once the overload is chosen, read
[`java_bridge_encoding_and_bytes.md`](java_bridge_encoding_and_bytes.md).

## Short Version

Outbound Java calls work like this:

1. the Python-facing RTI surface records an `Invocation`
2. the shared bridge layer loads Java overload metadata for that method
3. Python matches candidate overloads by arity and keyword names
4. if that shape pass leaves one overload, Python routes it directly
5. only true same-shape ambiguity is scored by expected Java parameter types
6. Python converts arguments to the chosen Java shapes
7. JPype or Py4J executes the already-resolved Java call

Inbound callbacks work similarly:

1. Java invokes a standard `FederateAmbassador` callback
2. the shared dispatcher looks up the expected Java callback signature
3. callback arguments are converted to the matching Python-side shapes
4. the normalized Python callback method is invoked

The important point is that overload selection is a shared Python policy, not
an incidental side effect of one bridge route.

## Two Routes

The document is about two different execution routes over one shared Java
adaptation policy:

- `JPype`: Python starts or attaches to a JVM in-process and calls Java
  objects directly.
- `Py4J`: Python talks to a separate Java process through a gateway and exposes
  callback proxies back to Java.

Both routes use the same Python-side invocation metadata, argument ordering
rules, overload policy, and callback-signature policy.

The practical split is:

- shared layer decides what Java call shape is intended
- route layer decides how that chosen call is materialized and executed

That means the repo has one overload-resolution model, not one JPype model and
another Py4J model.

## The Core Files

The main implementation files behind this policy are:

- [`../packages/hla-backend-common/src/hla/backends/common/invocation.py`](../packages/hla-backend-common/src/hla/backends/common/invocation.py)
- [`../packages/hla-backend-common/src/hla/backends/common/java_invocation_policy.py`](../packages/hla-backend-common/src/hla/backends/common/java_invocation_policy.py)
- [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_bridge_base.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_bridge_base.py)
- [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_value_adapter.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_value_adapter.py)
- [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_callbacks.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_callbacks.py)
- [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_encoding.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_encoding.py)
- [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py)
- [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_binding_profile.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_binding_profile.py)
- [`../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py`](../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py)
- [`../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py`](../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py)

## Module Layout

The resolver split is now explicit:

- `invocation.py` owns the backend-neutral resolver framework and swappable hook
- `java_invocation_policy.py` is the stable facade for Java invocation policy
- `java_invocation_metadata.py` owns Java overload metadata parsing
- `java_invocation_scoring.py` owns Java type-shape scoring
- `java_invocation_routes.py` owns weighted and deterministic Java route policy

The shared Java adaptation layer is now intentionally split into these modules:

| Module | Responsibility |
| --- | --- |
| `invocation.py` | backend-neutral resolver framework and active-resolver hook |
| `java_invocation_policy.py` | stable public facade for Java invocation policy |
| `java_invocation_metadata.py` | Java overload metadata parsing and ordered argument shaping |
| `java_invocation_scoring.py` | Java type-shape scoring helpers and Java container-family markers |
| `java_invocation_routes.py` | weighted and deterministic Java route policy |
| `java_bridge_base.py` | route-neutral `JavaBridge` base abstraction and low-level Java object helpers |
| `java_value_adapter.py` | generic Java runtime adaptation plus HLA semantic adaptation |
| `java_callbacks.py` | callback signature lookup and `PythonFederateAmbassadorDispatcher` |
| `java_encoding.py` | `JavaEncoderOracle` and `JavaVendorEncoding` |
| `java_common.py` | backend composition, invocation execution, and exception translation |

ASCII view:

```text
JPype | Py4J runtime
  -> JavaBridge implementations
  -> HLAJavaValueAdapter / GenericJavaValueAdapter
  -> PythonFederateAmbassadorDispatcher
  -> JavaEncoderOracle / JavaVendorEncoding
  -> JavaRTIBackend
```

### Maintainer Map

Use this when you know what behavior you want to change but not which module
owns it.

| If you are changing... | Primary module | Typical secondary module |
| --- | --- | --- |
| low-level JPype/Py4J-independent Java object helpers | `java_bridge_base.py` | route runtime module |
| JPype-only Java object construction/call mechanics | `jpype/runtime.py` | `java_bridge_base.py` |
| Py4J-only gateway/proxy/call mechanics | `py4j/runtime.py` | `java_bridge_base.py` |
| generic Python `list/set/dict/bytes/enum` conversion | `java_value_adapter.py` via `GenericJavaValueAdapter` | `java_bridge_base.py` |
| HLA handle/time/config/auth/container conversion | `java_value_adapter.py` via `HLAJavaValueAdapter` | `java_binding_profile.py` |
| callback argument normalization or callback signature expectations | `java_callbacks.py` | `java_value_adapter.py` |
| HLA encoder-factory materialization or vendor byte encoding | `java_encoding.py` | `java_value_adapter.py` |
| backend invocation composition or Java exception translation | `java_common.py` | `invocation.py` |
| overload scoring or deterministic routing | `java_invocation_policy.py` | `invocation.py` |

## Troubleshooting Map

Use this table when the symptom is clear but the owning module is not.

| Symptom | Start in | Why |
| --- | --- | --- |
| wrong Java overload chosen | `java_invocation_policy.py` | overload filtering, scoring, and deterministic route selection live there |
| deterministic route rejects an ambiguous shape | `java_invocation_policy.py` | fail-closed route entries are intentionally explicit there |
| Python `list`, `set`, `frozenset`, or `dict` lands in the wrong Java container family | `java_value_adapter.py` via `GenericJavaValueAdapter` | generic container materialization and normalization live there |
| handle sets, handle maps, logical time, auth, or config values wrap incorrectly | `java_value_adapter.py` via `HLAJavaValueAdapter` | HLA semantic conversion is separate from generic container conversion |
| callback arguments arrive with the wrong Python shape | `java_callbacks.py` | callback signature expectations and callback dispatch live there |
| `byte[]`, `userSuppliedTag`, or encoder payloads do not round-trip cleanly | `java_encoding.py` | byte-preservation and encoder materialization are isolated there |
| JPype-only bridge behavior differs from Py4J | `jpype/runtime.py` | route-local in-process materialization belongs there after shared resolution |
| Py4J-only bridge behavior differs from JPype | `py4j/runtime.py` | gateway/proxy materialization belongs there after shared resolution |
| Java object helper behavior is wrong across both routes | `java_bridge_base.py` | route-neutral bridge primitives live there |
| Java exception translation or backend call composition is wrong | `java_common.py` | backend execution and exception mapping live there |

Practical rule:

- if both JPype and Py4J fail the same way, start in the shared layer
- if only one route fails, start in the route runtime module
- if the issue is bytes or encoders, do not start in overload logic
- if the issue is container shape, do not start in callback dispatch

The most useful tests are:

- [`../tests/backends/test_backends.py`](../tests/backends/test_backends.py)
- [`../tests/backends/test_java_factory_selection_helpers.py`](../tests/backends/test_java_factory_selection_helpers.py)
- [`../tests/backends/test_standard_java_shim_routes.py`](../tests/backends/test_standard_java_shim_routes.py)
- [`../tests/factories/test_fom_time_factories.py`](../tests/factories/test_fom_time_factories.py)
- [`../tests/factories/test_java_overload_audit.py`](../tests/factories/test_java_overload_audit.py)
- [`../tests/factories/test_java_overload_negative_inputs.py`](../tests/factories/test_java_overload_negative_inputs.py)
- [`../tests/vendors/test_java_bridge_vendor_overloads.py`](../tests/vendors/test_java_bridge_vendor_overloads.py)

The human-readable audit packet is:

- [`../artifacts/java_overload_audit/java_overload_audit.json`](../artifacts/java_overload_audit/java_overload_audit.json)
- [`../artifacts/java_overload_audit/java_overload_audit.md`](../artifacts/java_overload_audit/java_overload_audit.md)

The full method-by-method interface mapping reference is:

- [`reference/java_interface_spec_mapping.md`](reference/java_interface_spec_mapping.md)

## Outbound Call Resolution

The active resolver hook lives in
[`invocation.py`](../packages/hla-backend-common/src/hla/backends/common/invocation.py).

The Java-specific resolver policy lives in
[`java_invocation_policy.py`](../packages/hla-backend-common/src/hla/backends/common/java_invocation_policy.py).

Important implementation detail: the repo now routes overload choice through a
swappable resolver hook rather than baking the current scorer directly into
every caller.

There are now two resolver variants:

- weighted resolver: flexible, metadata-driven, still the default
- deterministic router: explicit method-by-method routing for the ambiguous HLA
  Java families, intended for teams that want auditable overload policy

The current default implementation is the weighted Java resolver in
[`java_invocation_policy.py`](../packages/hla-backend-common/src/hla/backends/common/java_invocation_policy.py):

- `_resolve_java_invocation_weighted(...)`

The public hook surface is:

- `resolve_java_invocation(...)`
- `get_java_invocation_resolver()`
- `set_java_invocation_resolver(...)`
- `reset_java_invocation_resolver()`
- `resolve_java_invocation_deterministic(...)`
- `install_deterministic_java_invocation_router()`
- `get_deterministic_java_invocation_router()`
- `java_invocation_resolver("weighted" | "deterministic")`
- `java_invocation_resolver_name(...)`

The regression proof that the hook is actually swappable lives in:

- [`../tests/factories/test_java_overload_negative_inputs.py`](../tests/factories/test_java_overload_negative_inputs.py)

## Deterministic Router Variant

For boss-review or adapter-review work, the deterministic router is the clearer
surface.

Instead of scoring candidate overloads generically, it contains explicit route
entries for the real same-arity HLA Java collision families:

- `createFederationExecution`
- `joinFederationExecution`
- `requestAttributeValueUpdate`

The implementation lives in:

- [`../packages/hla-backend-common/src/hla/backends/common/java_invocation_policy.py`](../packages/hla-backend-common/src/hla/backends/common/java_invocation_policy.py)

The route table documents each decision with:

- method name
- arity
- exact Java parameter-name tuple
- rationale text
- predicate over the normalized Python argument tuple

Current examples:

- `createFederationExecution(name, [fom], "HLAfloat64Time")` -> route to
  `URL[] + String`
- `createFederationExecution(name, [fom], mim_path)` -> route to
  `URL[] + URL`
- `joinFederationExecution(type, federation, [fom])` -> route to
  `additionalFomModules`
- `joinFederationExecution(name, type, federation)` -> route to
  `federateName + federateType + federationExecutionName`
- `requestAttributeValueUpdate(object_handle, attrs, tag)` -> route to
  `theObject`
- `requestAttributeValueUpdate(class_handle, attrs, tag)` -> route to
  `theClass`

The route table now also documents neighboring non-ambiguous high-traffic
shapes so the adapter surface is easier to review end to end:

- `connect`
- `createFederationExecution` arity 4
- `joinFederationExecution` arity 2 and 4
- `subscribeObjectClassAttributes`
- `subscribeObjectClassAttributesPassively`
- `subscribeObjectClassAttributesWithRegions`
- `subscribeObjectClassAttributesPassivelyWithRegions`
- `requestAttributeValueUpdateWithRegions`

If an ambiguous family does not have one explicit matching route, the
deterministic router fails closed. It does not silently score and guess.

That behavior is deliberate. It gives the wrapping layer a documented
adaptation boundary that is easier to review and safer to extend when:

- adding 2025-specific bridge coverage
- onboarding a new vendor Java RTI
- adapting a slightly different Java surface or transport dialect

The focused tests for this path are:

- [`../tests/factories/test_java_overload_negative_inputs.py`](../tests/factories/test_java_overload_negative_inputs.py)
- [`../tests/factories/test_fom_time_factories.py`](../tests/factories/test_fom_time_factories.py)

## Per-Route Config Selection

The deterministic router is no longer only a global test hook.

JPype and Py4J configs now accept:

- `invocation_router="weighted"`
- `invocation_router="deterministic"`

That means one Java route can remain weighted while another route in the same
process opts into deterministic routing.

Operator audit:

- `./tools/java invocation-router-audit`
- `./tools/java invocation-router-audit --router deterministic --json`

The main steps are:

1. filter the method's overload metadata to Java overloads
2. map Python kwargs onto Java parameter names
3. reject candidates whose total parameter count does not match
4. if exactly one Java overload exists, route it directly
5. if multiple overloads exist but only one survives the arity and keyword
   shape pass, route that one directly
6. only when multiple same-shape candidates remain, score them using expected
   Java parameter types
7. reject the call if multiple candidates tie for top score
8. return one resolved overload plus an ordered argument tuple

This means the bridge can accept Python-facing calls such as:

- positional only
- mixed positional and keyword
- snake-case keyword names that correspond to lowerCamel Java names

without leaving the final choice to route-local reflection behavior.

## Outbound Route Comparison

The outbound path is the easiest place to separate what is shared from what is
route-local.

### Shared Outbound Steps

For both JPype and Py4J:

1. Python-facing RTI call records an `Invocation`
2. shared resolver chooses Java overload shape
3. shared converter materializes Java-oriented argument values
4. route-local bridge executes the chosen Java call

### JPype Outbound Route

JPype outbound execution is:

1. `JavaRTIBackend.invoke(...)` resolves the overload
2. `HLAJavaValueAdapter.to_backend_args(...)` converts values
3. `JPypeBridge.call(...)` runs `getattr(java_obj, method_name)(*args)`
4. JPype itself dispatches the already-chosen Java signature

Important characteristics:

- direct in-process Java object access
- easier class-identity inspection
- easier debugging of exact Java implementation classes
- less gateway indirection once the overload is chosen

### Py4J Outbound Route

Py4J outbound execution is:

1. `JavaRTIBackend.invoke(...)` resolves the overload
2. `HLAJavaValueAdapter.to_backend_args(...)` converts values
3. `Py4JBridge.call(...)` runs the gateway-backed Java method call
4. Py4J marshals the chosen call across the gateway boundary

Important characteristics:

- separate Java process shape
- gateway marshalling between Python and Java
- more indirection when debugging returned implementation classes
- same chosen overload policy, different transport mechanics

### Compare And Contrast

| Concern | Shared Policy | JPype Route | Py4J Route |
| --- | --- | --- | --- |
| overload selection | Python resolver chooses the Java shape first | direct JVM object call after resolution | gateway call after resolution |
| keyword / snake-case mapping | shared | same | same |
| handle-set / map conversion | shared converter policy | materialize direct Java collections or RTI factories | materialize gateway-backed Java collections or RTI factories |
| logical time conversion | shared expected type names | direct class construction or RTI time factory use | gateway-backed class construction or RTI time factory use |
| failure mode if shape is ambiguous | fail closed in shared resolver | same | same |

## Helper: How Python Values Are Wrapped To Java

Overload resolution and value wrapping are connected, but they are not the same
step.

The resolver answers:

- which Java overload row is intended
- what Java parameter types that overload expects

The converter then answers:

- how each Python value must be materialized for that expected Java type

That split is important. The deterministic router does not itself build Java
`HashSet`, `HashMap`, RTI-owned handle sets, or Java `byte[]`. It only chooses
the overload shape that gives the converter the right target types.

The shared conversion logic lives in
[`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py),
mainly in `HLAJavaValueAdapter.to_backend(...)`.

### Strong Typed Wrapping Families

When the chosen Java overload provides an exact expected type, the converter
wraps Python values deliberately rather than relying on JPype or Py4J to guess.

The main typed families are:

- `byte[]`
- `URL`
- `URL[]`
- `AttributeHandleSet`
- `DimensionHandleSet`
- `FederateHandleSet`
- `RegionHandleSet`
- `AttributeHandleValueMap`
- `ParameterHandleValueMap`
- `AttributeSetRegionSetPairList`
- `LogicalTime`
- `LogicalTimeInterval`
- `RangeBounds`
- `RtiConfiguration`
- `Credentials`
- Java enum constants

Typical examples:

- Python `bytes` -> Java `byte[]`
- Python iterable of handles -> RTI-owned handle set when the RTI factory is
  available, otherwise a generic Java set
- Python mapping of handle -> `bytes` -> RTI-owned handle-value map when the
  RTI factory is available, otherwise a generic Java map
- Python logical-time wrapper -> RTI time-factory object when possible,
  otherwise the standard Java logical-time class

### Generic Collection Fallbacks

If the chosen overload does not provide one of the explicit typed HLA
collection families, generic Python containers fall back to generic Java
collections:

- Python `list` -> Java `ArrayList`
- Python `set` -> Java `HashSet`
- Python `frozenset` -> Java `HashSet`
- Python `dict` / `Mapping` -> Java `HashMap`

That fallback is structurally useful, but it is weaker semantically than the
typed HLA families.

Important current boundary:

- `set` and `frozenset` are treated the same on the Java boundary
- generic mappings do not preserve a stronger Java map interface than
  `HashMap`
- generic collections are less self-describing than typed handle sets/maps

So "deterministic overload routing" is not automatically the same thing as
"fully explicit Java container typing." The typing is strongest when the
selected overload row carries an exact target type and the converter has an
explicit rule for that type family.

## Helper: How Java Values Are Unwrapped Back To Python

The reverse conversion path is also shared policy rather than route-local
guesswork.

Inbound conversion lives in the same file, mainly in
`HLAJavaValueAdapter.from_backend(...)`.

### Strong Typed Unwrapping Families

The repo explicitly normalizes these Java-side values back into Python-side
types:

- Java `byte[]` -> Python `bytes`
- Java handle implementation objects -> Python handle wrappers through the
  shared native-handle registry
- Java handle sets -> Python handle-set classes
- Java handle-value maps -> Python handle-value-map classes
- Java enum constants -> Python enums
- Java logical time / interval objects -> Python logical-time wrappers
- Java composite return types such as:
  - `TimeQueryReturn`
  - `MessageRetractionReturn`
  - `FederateHandleSaveStatusPair`
  - `FederateRestoreStatus`
  - `SupplementalReflectInfo`
  - `SupplementalReceiveInfo`
  - `SupplementalRemoveInfo`

### Generic Collection Reverse Fallbacks

Generic Java collections are normalized conservatively:

- Java map-like objects -> Python `dict`
- Java collection-like objects -> Python collection values, usually normalized
  as plain Python sets in the generic fallback path

That means the current bridge is strongest for explicit HLA container families
and weaker for generic vendor-private or metadata-light collection shapes.

The shared wrapper still owns the public Python contract, though. The repo does
not treat "whatever JPype returned" or "whatever Py4J returned" as the
intended public surface.

## One-Page Container Conversion Matrix

This is the practical matrix for the container families that matter most at the
bridge boundary.

| Python input shape | Expected Java type | JPype materialization | Py4J materialization | Python return normalization | Notes |
| --- | --- | --- | --- | --- | --- |
| `bytes` | `byte[]` | real Java `byte[]` via `JArray(JByte)` | real Java `byte[]` via gateway array creation | Python `bytes` | signed Java byte handling is explicit on both routes |
| URL-like scalar | `URL` | Java `URL` | Java `URL` | URL-like Java values usually stay scalar unless a stronger Python model is expected | used for single FOM/MIM module paths |
| iterable of URL-like values | `URL[]` | Java `URL[]` | Java `URL[]` | list/array-like values normalize through the converter path that consumes them | strong typed array family, not generic list fallback |
| `set[Handle]` or `frozenset[Handle]` | standard handle-set family such as `AttributeHandleSet` | RTI-owned handle set when factory is available, else Java `HashSet` | RTI-owned handle set when factory is available, else Java `HashSet` | typed Python handle-set class when the expected family is known | `set` and `frozenset` are not distinguished on the Java side |
| `dict[Handle, bytes]` | standard handle-value-map family such as `AttributeHandleValueMap` | RTI-owned handle-value map when factory is available, else Java `HashMap` | RTI-owned handle-value map when factory is available, else Java `HashMap` | typed Python handle-value-map class when the expected family is known | bytes payloads are normalized entry-by-entry |
| iterable of `AttributeRegionAssociation` | `AttributeSetRegionSetPairList` | RTI-owned pair-list when factory is available, else Java `ArrayList` | RTI-owned pair-list when factory is available, else Java `ArrayList` | normalized through the explicit pair-list conversion path | this is a standard HLA container family |
| `list[...]` | no explicit standard family | Java `ArrayList` | Java `ArrayList` | generic Java collections usually normalize conservatively, often as plain Python collections | listed fallback case |
| `set[...]` | no explicit standard family | Java `HashSet` | Java `HashSet` | generic Java collections usually normalize conservatively, often as plain Python sets | listed fallback case |
| `frozenset[...]` | no explicit standard family | Java `HashSet` | Java `HashSet` | generic Java collections usually normalize conservatively, often as plain Python sets | immutability is not preserved |
| `dict[...]` / `Mapping[...]` | no explicit standard family | Java `HashMap` | Java `HashMap` | Python `dict` | listed fallback case |

### Standard Explicit Families

The current shared bridge treats these as explicit standard Java container
families rather than generic collection guesses:

- `URL[]`
- `AttributeHandleSet`
- `DimensionHandleSet`
- `FederateHandleSet`
- `InteractionClassHandleSet`
- `RegionHandleSet`
- `AttributeHandleValueMap`
- `ParameterHandleValueMap`
- `AttributeSetRegionSetPairList`

### Generic Fallback Cases

The current generic fallback cases are intentionally narrow and easy to name:

- Python `list` -> Java `ArrayList`
- Python `set` -> Java `HashSet`
- Python `frozenset` -> Java `HashSet`
- Python `dict` / `Mapping` -> Java `HashMap`

### Deterministic-Route Strictness

When the deterministic router resolves a Java call through metadata-backed
parameter types, the bridge now marks that call as strict for container
shapes.

That means:

- explicit standard container families continue to work
- generic container fallback is rejected for that deterministic route

Examples of fail-closed strict-route behavior:

- Python `list` with only a generic `java.util.List` expectation
- Python `set` or `frozenset` with only a generic `java.util.Set` expectation
- Python `dict` with only a generic `java.util.Map` expectation

This is deliberate. On deterministic routes, the repo now prefers one of two
outcomes:

- use an explicit standard HLA container family
- fail closed and require a documented conversion rule

## Current Resolver Boundary

The current implementation is intentionally stronger before it is smarter.

That means:

- `one Java overload total` -> route it
- `multiple overloads, one surviving shape` -> route it
- `multiple overloads, multiple surviving same-shape candidates` -> score them
- `multiple top-score candidates` -> fail closed with
  `BackendConversionError`
- `no surviving shape` -> fail closed with `BackendConversionError`

The repo does this on purpose because many negative-path tests intentionally
pass placeholder values such as `None`, `object()`, or empty handle sets while
expecting the backend to raise state-driven exceptions like:

- `NotConnected`
- `FederateNotExecutionMember`
- later semantic exceptions after connection or join state is established

If the resolver rejected those unique-shape calls early, the bridge would hide
the real backend behavior behind a conversion error. The current rule avoids
that for unique-shape calls while staying strict on true ambiguity.

Regression coverage for this rule lives in:

- [`../tests/factories/test_java_overload_negative_inputs.py`](../tests/factories/test_java_overload_negative_inputs.py)
- [`../tests/backends/test_python_backend_object_ownership_extended.py`](../tests/backends/test_python_backend_object_ownership_extended.py)

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

Important detail: the resolver now fails closed on true ambiguity.

If two Java overloads survive arity/name matching and receive the same top
score, the call raises an explicit `BackendConversionError` instead of picking
the first metadata row by accident.

That protects the repo from silent overload drift when:

- new overloads are added to the API metadata
- a bridge route exposes a value shape that matches multiple families
- a caller passes a value that is underspecified for the Java surface

## Callback Resolution

Inbound callbacks are handled by
[`PythonFederateAmbassadorDispatcher`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py).

The dispatcher does not just forward raw Java objects blindly.

It first asks the binding profile for the expected Java callback parameter
types for the callback method and arity, then converts the values accordingly.

That matters because vendor RTIs frequently return implementation classes
instead of the public Java interface names used in the standard metadata.

## Inbound Route Comparison

Inbound callback handling is also one shared policy executed through two
different mechanics.

### Shared Inbound Steps

For both JPype and Py4J:

1. Java calls a standard `FederateAmbassador` method
2. route-local callback proxy reaches the shared dispatcher
3. dispatcher looks up the callback signature metadata
4. converter normalizes arguments into Python-side values
5. Python callback method is invoked on the federate ambassador

### JPype Inbound Route

JPype uses:

- `JProxy(...)` for the callback object
- direct callback entry from the JVM into Python
- shared dispatcher for signature-aware conversion

This is the lighter callback path mechanically because the proxy lives in the
same process as the JVM.

### Py4J Inbound Route

Py4J uses:

- a Python callback object that advertises Java interfaces to the gateway
- callback-server mechanics inside Py4J
- shared dispatcher for signature-aware conversion once the callback arrives

This is heavier mechanically because Java reaches Python through the gateway
callback channel, not a same-process proxy.

### Why The Wrapping Still Matters

Even inbound, the repo does not rely on "whatever JPype returned" or
"whatever Py4J returned" as the public surface.

The shared wrapper still owns:

- handle-family normalization
- byte normalization
- logical-time normalization
- collection normalization
- callback-name compatibility

## Helper: What We Did To Keep The Type Checker Happy

The Java bridge boundary is intentionally split between:

- a typed Python-facing HLA surface
- a dynamic Java-object boundary

That split is what keeps Pyright manageable without pretending JPype or Py4J
objects are statically knowable Python classes.

### Where Typing Is Strong

The repo keeps typing explicit in these places:

- the Python-facing RTI contract and callback names
- the generated interface-contract docs and method inventories
- binding-profile lookups for known Python-side enum, handle, and helper types
- converter inputs that are standard Python abstractions such as:
  - `Mapping`
  - `Sequence`
  - `Iterable`
- explicit helper protocols for small Java concepts such as map entries and
  iterators

Examples in the shared bridge layer include:

- `Mapping[str, Any]` for overload metadata rows
- `Sequence[Any]` for Java collection builders
- narrow `Protocol` types for Java iterator and map-entry access

### Where Typing Is Intentionally Soft

The repo deliberately uses `Any` at the actual bridge edge for:

- JPype proxy objects
- Py4J gateway objects
- Java implementation-class instances returned by vendor RTIs
- dynamically selected overload argument tuples

That is not an accident. It is the honest type boundary.

Trying to model all JPype and Py4J runtime objects as precise Python generic
types would create fake certainty and a much noisier type-checking story.

### Practical Typing Rules

The current typing strategy is:

1. keep the Python-facing API names and helper models typed
2. keep overload metadata rows and conversion helpers typed enough to be
   auditable
3. use `Any` exactly at the live Java object boundary
4. immediately normalize returned Java values back into typed Python-side
   handles, enums, bytes, logical-time wrappers, and known composite models
5. avoid pretending generic Java collections carry stronger static guarantees
   than the runtime can actually prove

### Converter Layering

The shared converter stack is now intentionally split:

- `GenericJavaValueAdapter`: bridge-neutral Java runtime adaptation for bytes,
  enums, generic list/set/map materialization, and Java collection traversal
- `HLAJavaValueAdapter`: HLA semantic adaptation for handles, logical time,
  typed RTI container families, configuration/authentication models, and other
  standard-owned shapes
- `HLAJavaValueAdapter`: HLA semantic conversion surface used by the Java RTI
  backend and callback dispatch paths

This is why the bridge layer uses typed helper abstractions such as
`Mapping`, `Sequence`, `Protocol`, and explicit converter classes, while still
allowing route-local Java objects themselves to remain `Any`.

For the container path specifically, the repo now also uses generic helper
shapes where they are honest:

- Java iterator and map-entry protocols are generic in the shared bridge layer
- fake JPype/Py4J collection shims used by tests are generic, so the round-trip
  contract stays type-reviewable
- the live vendor object itself still remains `Any` until it is normalized
  through the shared converter

### What "Pyright Happy" Means Here

In this repo, Pyright happiness does not mean:

- every JPype object has a perfect Python generic type
- every Py4J return value is statically proven before normalization

It does mean:

- the public Python API surface remains typed and reviewable
- conversion policy is centralized instead of scattered through ad hoc casts
- Java runtime opacity is contained at one boundary
- route-local bridge code does not leak arbitrary dynamic objects through the
  public API without normalization where the repo has a standard model

That is a pragmatic static-typing strategy, not a fantasy one.

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

### JPype Characteristics

JPype is stronger when the goal is direct wrapping clarity.

Useful properties:

- same-process execution shape
- direct Java class access through `JClass`
- `JProxy` callback wrapping
- easier inspection of Java class identity and overload-adjacent behavior
- easier debugging when the question is "what exact Java object did I get?"

Tradeoffs:

- JVM lifecycle is inside the Python process
- signed-byte handling in `byte[]` creation must be explicit
- classpath and JVM options are process-local concerns

### Py4J Characteristics

Py4J is stronger when the goal is process separation or an already-running
Java side.

Useful properties:

- separate Java process shape
- attachable gateway model
- clearer fit for hosted or externally-managed Java runtime layouts
- callback path matches a real cross-process deployment shape more closely

Tradeoffs:

- more indirection in returned objects
- callback server setup matters
- byte-array and collection materialization happen through gateway machinery
- debugging class identity is usually less direct than in JPype

## Byte Quirks Between JPype And Py4J

The shared policy says `byte[]` is part of overload resolution and callback
normalization. The route mechanics are different enough that this deserves an
explicit compare/contrast summary here.

### Shared Byte Rules

For both routes:

- Python-facing binary payloads are normalized as `bytes`
- `byte[]` overloads are selected by the shared resolver
- outbound `byte[]` values are materialized deliberately, not left to implicit
  bridge guessing
- inbound Java `byte[]` values are normalized back to immutable Python
  `bytes`

### JPype Byte Quirks

JPype materializes a real Java `byte[]` through `JArray(JByte)`.

Important quirk:

- Java bytes are signed, Python bytes are unsigned

So the JPype route explicitly remaps octets above `127` into signed Java byte
values during array creation.

Why that matters for invocation resolution:

- when the selected overload expects `byte[]`, JPype gets an already-typed Java
  array rather than a route-implicit conversion guess
- this reduces ambiguity between payload-bearing overloads and nearby non-byte
  shapes

### Py4J Byte Quirks

Py4J materializes `byte[]` through gateway array allocation with
`gateway.jvm.Byte.TYPE`.

Important quirks:

- array creation is indirect through the gateway
- fallback behavior is riskier if conversion is not explicit
- callback-returned byte arrays must be normalized after gateway transport

Why that matters for invocation resolution:

- the shared resolver still chooses the `byte[]` overload first
- Py4J then has to marshal that chosen `byte[]` shape correctly over the
  gateway boundary
- when debugging mismatches, the bug may be post-resolution marshalling rather
  than overload choice itself

### Practical Byte Difference Summary

| Concern | JPype | Py4J |
| --- | --- | --- |
| outbound `byte[]` creation | `JArray(JByte)` | gateway `new_array(Byte.TYPE, ...)` |
| signed-byte quirk | explicit and visible in-process | explicit but mediated through gateway arrays |
| callback byte path | direct proxy callback back into Python | callback-server path back into Python |
| easiest byte debugging path | usually JPype | usually slower to inspect because of gateway indirection |

For the full byte contract and live proof story, keep
[`java_bridge_encoding_and_bytes.md`](java_bridge_encoding_and_bytes.md) next
to this document.

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

Another current failure mode is worth naming explicitly:

6. a negative-path test or boundary probe can look like a "bad type" call even
   though the real intent is to reach backend state checks first

The implementation rule above is why unique-shape calls still route through the
backend, while ambiguous same-shape calls still fail at the resolver.

## Concrete Example Categories

The awkward classes of calls this policy exists to protect include:

- federation creation/destruction calls with `String` and module-list overloads
- connect-style calls that gain route-local settings designators
- attribute-handle-set and parameter-handle-value-map calls
- time-management calls that require RTI-owned logical-time objects
- callback families with multiple Java signatures but one normalized Python callback surface

The currently known same-arity outbound RTI collision groups are:

- `createFederationExecution` arity 2
  - `String federationExecutionName, URL[] fomModules`
  - `String federationExecutionName, URL fomModule`
- `createFederationExecution` arity 3
  - `String federationExecutionName, URL[] fomModules, String logicalTimeImplementationName`
  - `String federationExecutionName, URL[] fomModules, URL mimModule`
- `joinFederationExecution` arity 3
  - `String federateType, String federationExecutionName, URL[] additionalFomModules`
  - `String federateName, String federateType, String federationExecutionName`
- `requestAttributeValueUpdate` arity 3
  - `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag`
  - `ObjectClassHandle theClass, AttributeHandleSet theAttributes, byte[] userSuppliedTag`

These are now explicitly audited and regression-tested.

## Caching

The repo does cache the static parts of overload resolution, but it does not
cache resolved call outcomes.

Cached:

- Python/Java binding profile loading via `@lru_cache`
- parsed Java overload parameter strings
  - parameter-name tuples
  - parameter-type tuples

Not cached:

- chosen overload for a specific runtime call
- scored call result for a specific argument tuple

That split is intentional.

Caching immutable metadata makes the hot path cheap without risking stale or
incorrect overload choices for dynamic Python values.

## Swappable Resolver

The resolver entry point is intentionally replaceable.

The current hook surface lives in
[`../packages/hla-backend-common/src/hla/backends/common/invocation.py`](../packages/hla-backend-common/src/hla/backends/common/invocation.py):

- `resolve_java_invocation(...)`
- `get_java_invocation_resolver()`
- `set_java_invocation_resolver(...)`
- `reset_java_invocation_resolver()`

That keeps the current bridge code stable while allowing future resolver work
to swap in a different implementation behind one shared seam.

The current regression proof for that seam is:

- [`../tests/factories/test_java_overload_negative_inputs.py`](../tests/factories/test_java_overload_negative_inputs.py)

## Candidate Replacement Schemes

If the current weighted resolver becomes too hard to maintain or explain, these
are the preferred upgrade paths.

### Semantic-Kind Resolver

Classify Python inputs into explicit semantic kinds first, then match overloads
against those kinds.

Examples:

- `exact-string`
- `url-like`
- `url-list`
- `bytes-like`
- `logical-time`
- `handle:ObjectInstanceHandle`
- `handle:ObjectClassHandle`

This is the clearest likely replacement because it is easier to explain, test,
and fail closed than a larger weighted heuristic set.

### Rule-Table Resolver

Define explicit resolution rules for only the risky overload families.

This is attractive when a small number of RTI services carry most of the
ambiguity risk:

- `createFederationExecution`
- `joinFederationExecution`
- `requestAttributeValueUpdate`

This is maximally deterministic but more manual.

### Profile-Driven Resolver

Store resolution policy in generated profile data keyed by API profile or
vendor route.

That would allow future differences between:

- 2010 standard Java routes
- 2025 standard Java routes
- vendor-specific Java surfaces

This is the strongest long-term architecture if the repo needs different
resolver policies across editions or vendor families.

### Explicit Adapter Methods

Bypass generic overload resolution for the small set of dangerous methods and
implement those routes directly in adapter code.

This is less elegant, but it is straightforward and sometimes the easiest route
to prove against real vendor runtimes.

## Current Recommendation

If the repo needs to replace the current resolver later, prefer this order:

1. semantic-kind resolver
2. rule-table resolver for only the risky families
3. profile-driven resolver if vendor/profile divergence becomes real
4. explicit adapter methods as a bounded fallback

The repo should avoid moving toward broader scalar duck typing or more
complicated score tuning unless a concrete real-runtime need forces it.

## Live Vendor Proof

The optional live vendor lane now also checks bridge-boundary argument shapes on
real JPype and Py4J vendor routes.

That proof is intentionally narrower than the generated shim audit:

- it does not introspect vendor-private overload tables
- it does verify the real backend argument families emitted by the Python bridge
- it exercises the exact overloaded call families that have caused drift risk

The current live vendor proof covers:

- `createFederationExecution`
  - verifies the live vendor call uses the URL-array create path for FOM-module lists
- `joinFederationExecution`
  - verifies the normal named join path stays on the three-string route
- `requestAttributeValueUpdate`
  - verifies object-instance and object-class requests emit distinct handle families on the real vendor bridge path

## Negative Policy

The resolver and converter intentionally fail closed for off-shape inputs.

That includes cases such as:

- string-like impostors that are not exact `str`
- wrong handle families for overloaded handle routes
- non-URL-like values passed to `URL` or `URL[]` targets
- non-bytes-like values passed to `byte[]` targets
- non-mapping values passed to handle-value-map targets

The current negative-path regression coverage is:

- [`../tests/factories/test_java_overload_negative_inputs.py`](../tests/factories/test_java_overload_negative_inputs.py)

Those tests assert on message quality as well as exception type, so the repo
keeps useful diagnostics when callers or agents pass bad shapes into the Java
bridge.

## Reading Order

If you want the shortest path through this topic:

1. [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
2. [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md)
3. [`java_bridge_encoding_and_bytes.md`](java_bridge_encoding_and_bytes.md)
4. this page
5. [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md)
6. [`language_shim_routes.md`](language_shim_routes.md)

If you want the implementation path:

1. [`../packages/hla-backend-common/src/hla/backends/common/invocation.py`](../packages/hla-backend-common/src/hla/backends/common/invocation.py)
2. [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py)
3. [`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_binding_profile.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_binding_profile.py)
4. [`../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py`](../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py)
5. [`../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py`](../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py)
