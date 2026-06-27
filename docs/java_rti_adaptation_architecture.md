# Java RTI Adaptation Architecture

Use this document when the question is not just "which example do I run?" but
"how do we wrap a Java RTI into the Python HLA surface for both editions and
both bridge routes?"

This is the architecture-level explanation behind:

- `examples/jpype_java_rti.py`
- `examples/py4j_java_rti.py`
- `examples/jpype_java_rti_2025.py`
- `examples/py4j_java_rti_2025.py`
- `examples/java_shim_federate.py`

This document belongs to the backend and route wrapping surface described in
[`work_surfaces.md`](work_surfaces.md).

## One-Page Summary

This repository wraps standard Java HLA RTI implementations into one normalized
Python-facing RTI surface.

The same wrapping model is used for:

- both supported editions: `2010` and `2025`
- both supported Java routes: `jpype` and `py4j`

The key idea is simple:

1. choose the HLA edition
2. choose the Java bridge route
3. load the Java `RtiFactoryFactory` for that edition
4. obtain the Java `RTIambassador`
5. adapt it into the repository's Python RTI surface

What changes by edition:

- the Java package root
- the binding profile
- the available spec surface
- for `2025`, the additional authentication-capable runtime composition

What changes by route:

- how Python reaches Java
- how Python callback objects are exposed back to Java

What does not change:

- the normalized Python-facing RTI contract
- the shared callback dispatch policy
- the shared Java/Python value conversion layer
- the shared overload-resolution policy
- the top-level wrapping strategy

Management-level takeaway:

- JPype is the clearest primary route because it is in-process, easier to
  reason about, and easiest to demonstrate
- Py4J is the same adaptation contract with a different transport/process
  boundary
- the repo is not maintaining four independent wrappers; it is maintaining one
  shared adaptation policy with two route implementations and two edition
  profiles

Recommended explanation order for a non-implementer:

1. JPype 2010 as the baseline
2. show that 2025 is the same shape with a different package/profile
3. show that Py4J is the same shape with a different connection/callback
   transport
4. show that shared conversion, overload resolution, and dispatch logic keep
   the behavior aligned

## Short Version

The adaptation strategy is the same in all four cases:

1. choose an HLA edition: `2010` or `2025`
2. choose a bridge route: `jpype` or `py4j`
3. load the edition-specific Java `RtiFactoryFactory`
4. obtain a Java `RTIambassador`
5. wrap that Java ambassador in a Python `DelegatingRTIAmbassador`
6. resolve Java overload intent in Python
7. convert Python arguments to Java values on call-in
8. convert Java callback arguments, return values, and exceptions back to
   Python on call-out

The important design point is that edition selection and route selection happen
at the edge. After the backend is created, the Python-facing RTI surface is
intentionally normalized.

## Why JPype Is The Primary Story

JPype is the most direct route to explain because it keeps everything in one
Python-owned process:

- Python starts or attaches to the JVM
- Python can load Java classes directly with `JClass(...)`
- Python can implement a Java `FederateAmbassador` interface with `JProxy(...)`
- the adaptation boundary is explicit and easy to inspect in one place

That makes JPype the most salient route when explaining the wrapping model to a
new reader or to management.

Py4J uses the same logical adaptation contract, but the object transport is
different because Java lives behind a gateway rather than in the same process.

## The Four Supported Shapes

| Edition | Route | Java package root | Main config type | Main bridge class |
| --- | --- | --- | --- | --- |
| 2010 | JPype | `hla.rti1516e` | `JPypeConfig` | `JPypeBridge` |
| 2010 | Py4J | `hla.rti1516e` | `Py4JConfig` | `Py4JBridge` |
| 2025 | JPype | `hla.rti1516_2025` | `JPypeConfig` | `JPypeBridge` |
| 2025 | Py4J | `hla.rti1516_2025` | `Py4JConfig` | `Py4JBridge` |

The edition changes the binding profile and Java class names.

The route changes the bridge mechanics.

## Maintainer Routing

When extending or debugging the Java-to-Python bridge, use this ownership map:

| Change area | Primary module | Notes |
| --- | --- | --- |
| route-neutral Java bridge primitive behavior | `java_bridge_base.py` | base Java object helpers and shared bridge hooks |
| generic Java conversion | `java_value_adapter.py` | `GenericJavaValueAdapter` owns generic containers, bytes, and enums |
| HLA semantic conversion | `java_value_adapter.py` | `HLAJavaValueAdapter` owns handles, logical time, auth/config, and typed HLA containers |
| callback wrapping and callback parameter expectations | `java_callbacks.py` | shared for both JPype and Py4J |
| encoder-factory and vendor encoding behavior | `java_encoding.py` | separate from generic/HLA value adaptation on purpose |
| backend composition and exception translation | `java_common.py` | `JavaRTIBackend` lives here |
| JPype route mechanics | `packages/hla-bridge-java-jpype/.../runtime.py` | in-process JVM route |
| Py4J route mechanics | `packages/hla-bridge-java-py4j/.../runtime.py` | gateway-backed route |
| overload routing policy | `packages/hla-backend-common/.../invocation.py` | weighted and deterministic resolvers |

The adaptation contract stays the same.

## Troubleshooting Summary

Use this one-page routing table when somebody reports "the Java bridge is
wrong" but has not yet isolated the layer.

| Reported problem | Primary owner | Next check |
| --- | --- | --- |
| wrong RTI method overload or ambiguous call path | `invocation.py` | `java_bridge_overload_resolution.md` |
| wrong Python-to-Java container materialization | `java_value_adapter.py` via `GenericJavaValueAdapter` | `java_bridge_overload_resolution.md` |
| wrong HLA handle/time/auth/config wrapping | `java_value_adapter.py` via `HLAJavaValueAdapter` | `java_binding_profile.py` |
| wrong callback signature, callback argument shape, or callback normalization | `java_callbacks.py` | route runtime module |
| bytes or encoder outputs differ between JPype and Py4J | `java_encoding.py` | `java_bridge_encoding_and_bytes.md` |
| JPype-only behavior differs | `packages/hla-bridge-java-jpype/.../runtime.py` | `java_bridge_base.py` |
| Py4J-only behavior differs | `packages/hla-bridge-java-py4j/.../runtime.py` | `java_bridge_base.py` |
| backend composition, exception mapping, or Java RTI backend behavior differs | `java_common.py` | `java_bridge_base.py` |

Management reading rule:

- shared-layer problems affect both routes and are usually cheaper to fix once
- route-local problems are narrower and should stay narrow
- the repo is structured so generic conversion, HLA conversion, callback
  dispatch, and route mechanics can be debugged independently

## The Main Entry Points

The highest-level explicit selector is:

```python
from hla.bridges.java.jpype import JavaRTIImplementation

implementation = JavaRTIImplementation(
    "com.vendor.hla.RtiFactory",
    bridge="jpype",
    edition="2025",
    classpath=["/path/to/vendor.jar"],
)
rti = implementation.create_rti_ambassador()
```

That facade lives in:

- `packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/implementation.py`

Bridge-neutral creation lives in:

- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_factory_selection.py`

Route-local creation lives in:

- `packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/factory.py`
- `packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/factory.py`

## Layering

Think of the stack like this:

```text
Python federate code
    ->
DelegatingRTIAmbassador
    ->
Java RTI backend adapter
    ->
JavaBridge + HLAJavaValueAdapter
    ->
JPypeBridge or Py4JBridge
    ->
Java RTIambassador
    ->
Vendor RTI or test shim
```

The adaptation is not hard-coded separately for every Java RTI method. The repo
centralizes most of the policy in the shared Java bridge layer.

## Where Overload Resolution Happens

This is a major part of the bridge design.

The Java HLA APIs contain overload families where the correct call cannot be
described by method name alone. The repo therefore does not rely on JPype or
Py4J to infer the intended overload from raw Python arguments.

Instead, the shared layer resolves the Java call in Python first:

1. the Python-facing RTI facade records an `Invocation`
2. Java overload metadata is loaded for that method
3. candidate overloads are filtered by arity and parameter names
4. ambiguous candidates are scored by expected Java parameter types
5. arguments are converted for the chosen overload
6. the concrete JPype or Py4J route executes the already-resolved call

The main files behind that policy are:

- `packages/hla-backend-common/src/hla/backends/common/invocation.py`
- `packages/hla-backend-common/src/hla/backends/common/java_invocation_policy.py`
- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`
- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_binding_profile.py`

Inbound callbacks use the same general idea in reverse: the shared dispatcher
looks up the expected Java callback signature and converts values before
calling the normalized Python callback method.

Read [`java_bridge_overload_resolution.md`](java_bridge_overload_resolution.md)
for the concrete JPype versus Py4J comparison at that boundary.

Read [`java_bridge_encoding_and_bytes.md`](java_bridge_encoding_and_bytes.md)
for the byte-preservation and Java encoder proof story across both routes.

## Target Package Boundaries

The current package split is already much better than a monolithic Java
adapter, but the intended long-term boundary is more specific than "Java stuff
over here."

The correct reusable split is:

1. HLA spec surfaces
2. backend/runtime-neutral support
3. generic Java bridge runtime support
4. HLA-on-Java adaptation
5. route mechanics
6. vendor overlays

That gives the repo two kinds of reuse:

- reuse across JPype and Py4J
- reuse across multiple HLA Java RTIs

It also keeps a third reuse option open:

- reuse of the generic Java bridge layer for non-HLA Java integration work

### Package Ownership Model

| Package family | Owns | Should not own |
| --- | --- | --- |
| `hla-rti1516e` and `hla-rti1516_2025` | strict Python HLA spec surfaces, value types, exceptions, and edition-local API metadata | bridge mechanics, backend execution, vendor quirks |
| `hla-backend-common` | backend-neutral invocation model, plugin contracts, general conversion helpers, and backend support interfaces | JPype/Py4J runtime logic, Java RTI vendor logic, HLA Java binding specifics where avoidable |
| `hla-bridge-java-common` | shared Java bridge support, Java object helpers, shared Java callback plumbing, shared container/encoding helpers, shared HLA-on-Java adaptation | vendor launch policy, route-specific JVM/gateway lifecycle, Python RTI semantics |
| `hla-bridge-java-jpype` | JPype-only runtime mechanics | generic Java adaptation policy, vendor policy |
| `hla-bridge-java-py4j` | Py4J-only gateway/proxy mechanics | generic Java adaptation policy, vendor policy |
| `hla-vendor-*` | vendor discovery, classpath/runtime defaults, launch policy, vendor quirks, vendor packaging | re-owning generic bridge logic or shared HLA adaptation logic |

### What Should Stay Generic

These pieces should remain reusable across vendors and across both Java bridge
routes:

- Java bridge primitives in `java_bridge_base.py`
- route-local mechanics in `jpype/runtime.py` and `py4j/runtime.py`
- generic Python container to Java container conversion
- generic Java collection and map inspection
- generic `byte[]` round-trip helpers
- resolver hook infrastructure that allows overload routing to be swapped

If a maintainer could plausibly reuse the code for a non-HLA Java API, it is
probably in the generic layer.

### What Should Stay HLA-Specific

These pieces should remain clearly HLA-specific:

- HLA handle conversion
- logical-time and logical-time-interval conversion
- HLA callback signature expectations
- HLA binding-profile selection for `rti1516e` versus `rti1516_2025`
- HLA authentication and configuration composition
- HLA encoder-factory conventions
- HLA deterministic route tables for ambiguous standard Java API families

Those are adaptation concerns, not general Java bridge concerns.

### Recommended Internal Split

Even without creating another distribution, maintainers should think in three
internal layers inside the Java bridge family:

```text
generic Java bridge
  -> HLA Java adaptation
  -> JPype | Py4J route mechanics
```

Mapped to current modules, that means:

| Layer | Current modules |
| --- | --- |
| generic Java bridge | `java_bridge_base.py`, generic parts of `java_value_adapter.py`, route runtime modules |
| HLA Java adaptation | `java_binding_profile.py`, HLA parts of `java_value_adapter.py`, `java_callbacks.py`, `java_encoding.py`, `java_common.py` |
| route mechanics | `jpype/runtime.py`, `jpype/factory.py`, `py4j/runtime.py`, `py4j/factory.py` |

This is the right mental model even where the code is still physically adjacent
inside one package.

### One Boundary Still Worth Tightening

The main remaining blur is overload resolution ownership.

Today, the active Java invocation hook lives in:

- `packages/hla-backend-common/src/hla/backends/common/invocation.py`

The Java-specific route policy now lives in:

- `packages/hla-backend-common/src/hla/backends/common/java_invocation_policy.py`

That policy is now internally split into:

- `packages/hla-backend-common/src/hla/backends/common/java_invocation_metadata.py`
- `packages/hla-backend-common/src/hla/backends/common/java_invocation_scoring.py`
- `packages/hla-backend-common/src/hla/backends/common/java_invocation_routes.py`

That is much cleaner than the earlier monolith, but there are still two ideas
to keep separate:

- backend-neutral invocation plumbing
- Java-specific, HLA-shaped overload policy

The cleaner target boundary is:

- keep `Invocation`, resolver interfaces, and generic swappable hook mechanics
  in `hla-backend-common`
- move Java overload parsing, Java type scoring, and Java deterministic route
  tables toward the Java bridge layer over time

That would make the ownership line easier to explain:

- backend-common owns the invocation framework
- Java bridge owns Java overload policy

### Practical Rule For Reusability

When deciding where a new helper belongs, ask:

1. could this helper work for both JPype and Py4J?
2. could this helper work for more than one Java RTI vendor?
3. could this helper work outside HLA entirely?

Route it like this:

- yes to 3 -> generic Java bridge layer
- yes to 1 and 2 but no to 3 -> HLA Java adaptation layer
- no to 1 -> route-local package
- vendor-only -> vendor package

That rule is stricter and more reusable than treating every Java-related helper
as one undifferentiated bridge concern.

### Refactor Checklist For Invocation Ownership

Use this checklist when the team is ready to tighten the remaining boundary
around Java invocation resolution.

#### Keep In `hla-backend-common`

These pieces are still appropriately backend-common:

- `Invocation`
- `ResolvedJavaInvocation`
- `JavaInvocationResolver`
- `JavaInvocationResolverName`
- `get_java_invocation_resolver(...)`
- `set_java_invocation_resolver(...)`
- `reset_java_invocation_resolver()`
- `java_invocation_resolver_name(...)`

Reason:

- these are framework-level invocation and resolver-hook concepts
- they are useful even if the concrete resolver policy changes

#### Candidate To Move Toward The Java Bridge Layer

These pieces are Java-policy-heavy and are the best candidates to migrate over
time:

- Java overload parameter parsing helpers
  - `_split_java_params(...)`
  - `_param_name(...)`
  - `_param_type(...)`
  - `_parsed_java_params(...)`
  - `java_parameter_names(...)`
  - `java_parameter_types(...)`
- Java overload argument ordering helpers
  - `_keyword_matches(...)`
  - `_ordered_args_for_overload(...)`
- Java type-shape scoring helpers
  - `_looks_like_time_factory_name(...)`
  - `_is_mapping(...)`
  - `_is_sequence_not_text(...)`
  - `_looks_like_python_data_element(...)`
  - `_score_value_for_java_type(...)`
- Java deterministic route policy
  - `DeterministicJavaRoute`
  - `DeterministicJavaInvocationRouter`
  - `_DETERMINISTIC_JAVA_ROUTES`
  - `get_deterministic_java_invocation_router()`
  - `resolve_java_invocation_deterministic(...)`
  - `install_deterministic_java_invocation_router()`
- Java weighted resolver implementation
  - `_resolve_java_invocation_weighted(...)`
  - `resolve_java_invocation(...)`
  - `resolve_java_arguments(...)`
  - `java_invocation_resolver(...)`

Reason:

- these are not generic invocation concepts
- these are Java overload and HLA Java route-policy concepts

#### Recommended Target Homes

If the team performs the split, the target shape should look like this:

| Concern | Recommended home |
| --- | --- |
| resolver hook types and current-resolver registration | `hla.backends.common.invocation` |
| Java overload metadata parsing | `hla.backends.common.java_invocation_policy` today, then `hla.bridges.java.common` if package boundaries are tightened further |
| Java type-shape scoring | `hla.backends.common.java_invocation_policy` today, then `hla.bridges.java.common` if package boundaries are tightened further |
| deterministic HLA Java route table | `hla.backends.common.java_invocation_policy` today, then `hla.bridges.java.common` if package boundaries are tightened further |
| weighted Java resolver implementation | `hla.backends.common.java_invocation_policy` today, then `hla.bridges.java.common` if package boundaries are tightened further |

Suggested module naming if the split gets deeper:

- `java_invocation_policy.py`
- `java_overload_metadata.py`
- `java_overload_routes.py`

The exact filenames matter less than keeping backend-common free of
Java-specific route policy.

#### Safe Execution Order

Do the cleanup in this order so JPype and Py4J stay stable:

1. keep the public resolver-hook API names stable
2. extract Java overload parsing helpers first
3. extract Java scoring helpers second
4. extract deterministic route tables third
5. move weighted Java resolver implementation last
6. leave thin compatibility imports behind until all callers are updated

Practical rule:

- move internals first
- preserve public import surfaces until tests, docs, and factories are all cut over

#### Stop Conditions

Do not move code just because it mentions Java.

Leave it where it is if:

- it is truly backend-framework API rather than Java policy
- moving it would create circular imports between backend-common and bridge packages
- the extracted layer would become thinner but less understandable

The goal is cleaner ownership, not motion for its own sake.

## Where Edition Selection Happens

Edition selection is carried as one explicit field:

- `edition="2010"` or `edition="2025"` on `JavaRTIImplementation`
- `java_api_profile="2010"` or `java_api_profile="2025"` on `JPypeConfig` and
  `Py4JConfig`

That feeds the Java binding profile loader in the shared layer:

- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`
- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_binding_profile.py`

The binding profile controls:

- which Java package root to use
- which Java `RtiFactoryFactory` class to load
- which Java `FederateAmbassador` interface to implement
- which Python callback and datatype families to map to

In practice:

- `2010` maps to `hla.rti1516e`
- `2025` maps to `hla.rti1516_2025`

## Where Route Selection Happens

Route selection is also explicit:

- `bridge="jpype"` or `bridge="py4j"`

The shared factory selection code resolves that into the right route-local
factory module:

- JPype: `hla.bridges.java.jpype.factory`
- Py4J: `hla.bridges.java.py4j.factory`

That selection logic lives in:

- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_factory_selection.py`

This is the point where the repo decides whether to build:

- a real JPype-backed Java backend
- a real Py4J-backed Java backend
- an in-process Java-shaped shim backend for bridge-proof/testing flows

## JPype Sequence Diagram

This is the simplest end-to-end mental model for how the JPype route works.

```text
Python Federate
    |
    | 1. create JavaRTIImplementation(..., bridge="jpype", edition="2010|2025")
    v
JavaRTIImplementation
    |
    | 2. create_java_rti_ambassador(...)
    v
Bridge-Neutral Factory Selection
    |
    | 3. resolve JPypeConfig + JPype factory path
    v
JPypeBridge
    |
    | 4. start/attach JVM
    | 5. load edition-specific RtiFactoryFactory
    | 6. call getRtiFactory(...).getRtiAmbassador()
    v
Java RTIambassador
    ^
    | 7. wrap in DelegatingRTIAmbassador + HLAJavaValueAdapter
    |
DelegatingRTIAmbassador
    |
    | 8. connect(python_federate, callback_model)
    v
PythonFederateAmbassadorDispatcher
    |
    | 9. expose dispatcher to Java as JProxy(FederateAmbassador)
    v
Java RTI calls standard Java callbacks
    |
    | 10. dispatcher converts Java values to Python values
    v
Python Federate callback methods
```

The same basic sequence holds for service calls in the other direction:

1. Python calls a normalized RTI method
2. the delegating wrapper resolves the Java invocation
3. `HLAJavaValueAdapter` converts Python values to Java values
4. the bridge invokes the Java method
5. results or exceptions are converted back to the Python binding surface

## JPype Adaptation Flow

JPype is the cleanest route to explain end-to-end.

### 1. Build `JPypeConfig`

`JPypeConfig` carries the JVM-facing settings:

- `classpath`
- `jvm_args`
- `rti_factory_name`
- `connect_local_settings_designator`
- `start_jvm`
- `shutdown_jvm_on_close`
- `java_api_profile`

Definition:

- `packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py`

### 2. Start or attach to the JVM

`JPypeBridge`:

- ensures Java is available
- imports `jpype`
- starts the JVM if requested
- binds the selected edition profile

### 3. Load the edition-specific factory class

`create_jpype_backend(...)` does:

- `bridge.JClass(bridge.api_profile.factory_factory_class)`
- `getRtiFactory(...)`
- `getRtiAmbassador()`

Definition:

- `packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/factory.py`

### 4. Wrap the Java RTI ambassador

The backend is turned into a normalized Python-facing RTI via:

- `make_rti_ambassador(...)`

That returns a `DelegatingRTIAmbassador`, which is the common Python surface
the rest of the repo uses.

### 5. Adapt Python callbacks into a Java `FederateAmbassador`

When Python calls `rti.connect(federate, ...)`, the bridge creates a Java-side
callback object from the Python federate ambassador.

For JPype this uses:

- `JProxy(...)`

The object behind that proxy is a shared dispatcher:

- `PythonFederateAmbassadorDispatcher`

This dispatcher is bridge-neutral policy. JPype just exposes it as a Java
interface implementation.

## Encoding Adaptation Across 2010/2025 and JPype/Py4J

Encoding is a cross-edition concern, which means it needs to be explained
separately from bridge mechanics.

The important architectural point is:

- encoding is not owned by JPype
- encoding is not owned by Py4J
- encoding is not reimplemented separately for each wrapped Java RTI method

Instead, encoding adaptation is handled through shared conversion policy plus
edition-local datatype and binding profiles.

### What stays the same

Across both editions and both routes, the wrapper still has to solve the same
practical problems:

- convert Python `bytes` to Java `byte[]`
- convert Java `byte[]` back to Python `bytes`
- convert Python enums to Java enums
- convert Java enums back to Python-side names or objects
- convert Python handle sets and handle-value maps to Java collections or
  RTI-owned factories
- convert logical-time and interval values to the Java form expected by the RTI
- convert FOM module references into Java URL-like values

Those rules live primarily in:

- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`

The central object is:

- `HLAJavaValueAdapter`

### What changes by edition

The edition changes:

- the Java package root
- the active Python binding profile
- the edition-local datatype families
- the edition-local encoder surface exposed to the rest of the runtime

For `2010`, the adaptation is limited to the 1516e datatype and callback
surface.

For `2025`, the adaptation has to line up with the richer 2025 encoding model,
including the modern encoder factory and packaged FOM datatype repository
surface.

That is why `2025` encoding discussion belongs with:

- edition-local encoding factory work
- FOM type repository work
- runtime composition work

not with JPype or Py4J themselves.

### What changes by route

The route only changes how encoded values cross the Python/Java boundary.

JPype:

- can create Java values directly in-process
- can allocate Java arrays and collections directly
- can use Java classes immediately with `JClass(...)`

Py4J:

- must move values through the gateway boundary
- uses gateway-created arrays and Java collection objects
- exposes Java callback types through a Python proxy object with a declared
  Java interface

The conversion policy is still intended to yield the same Python-facing result.

### Practical interpretation

If someone asks "do we have separate encoding logic for JPype and Py4J?" the
correct answer is:

- only at the lowest transport/object-construction layer
- not at the conceptual HLA encoding layer

The conceptual model is shared. The bridge-specific code only handles how to
materialize the Java-side objects.

### 2025-specific encoding surface

The clearest proof that encoding is treated as an edition capability rather
than a bridge quirk is the dedicated 2025 coverage around:

- built-in codec registry behavior
- primitive codec vectors
- arrays, fixed records, and variant records
- byte-wrapper alignment
- FOM type repository loading

Primary references:

- `tests/test_rti1516_2025_encoding_factory.py`
- `tests/test_rti1516_2025_encoding_auth_contexts.py`

Management-level takeaway:

- the bridge gets values across the boundary
- the edition determines what those values mean
- the shared conversion layer keeps the behavior aligned across JPype and Py4J

## Py4J Adaptation Flow

Py4J follows the same logical pipeline with a different transport boundary.

### 1. Build `Py4JConfig`

`Py4JConfig` carries:

- an existing gateway or gateway parameters
- callback server parameters
- `rti_factory_name`
- `connect_local_settings_designator`
- `shutdown_gateway_on_close`
- `java_api_profile`

Definition:

- `packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py`

### 2. Connect to the Java gateway

`Py4JBridge` either:

- uses the provided `JavaGateway`, or
- constructs one from the config

### 3. Resolve `RtiFactoryFactory` through the gateway JVM

`create_py4j_backend(...)` walks:

- `gateway.jvm.<package>.<class>`

and then calls:

- `getRtiFactory(...)`
- `getRtiAmbassador()`

Definition:

- `packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/factory.py`

### 4. Expose Python callbacks as a Java-implemented object

Py4J cannot use `JProxy(...)`, so it defines a Python callback object with a
declared Java interface:

- `Py4JFederateAmbassadorProxy`

That proxy forwards every Java callback name into the same shared dispatcher:

- `PythonFederateAmbassadorDispatcher`

This is why the route mechanics differ, but the callback policy stays aligned.

## The Shared Policy Layer

Most of the real adaptation logic is route-neutral and lives in:

- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`

The key responsibilities are:

- argument normalization
- Java/Python value conversion
- callback dispatch
- Java collection and map conversion
- logical-time conversion
- exception translation
- handle registration and reconstruction

This is what lets the repo support both bridges and both editions without
re-implementing the HLA surface four times.

## Callback Adaptation

The core callback idea is:

1. Java invokes a standard Java callback name such as
   `announceSynchronizationPoint` or `timeAdvanceGrant`
2. the route-local proxy forwards that method name into
   `PythonFederateAmbassadorDispatcher`
3. the dispatcher resolves the Python-side callback target
4. payloads are converted from Java values into Python binding values
5. the user federate receives a normalized Python callback

This is why the examples intentionally use the standard lowerCamelCase callback
names. Those are the native Java callback names and they map directly through
the bridge.

## Value Conversion

The conversion rules are centralized in `HLAJavaValueAdapter`.

Examples of what it handles:

- `bytes` <-> Java `byte[]`
- Python enums <-> Java enum constants
- Python handle sets/maps <-> Java handle factories or collections
- Python logical time/interval values <-> Java logical-time objects
- Python FOM module paths <-> Java `URL` or `URL[]`

This is one of the main reasons the wrapping approach scales. The per-method
adapter code can stay small because type adaptation is centralized.

## Exception Translation

Java RTI exceptions do not leak through as raw bridge exceptions by design.

The bridge layer translates them into the Python binding’s exception family for
the selected edition where possible, using the active binding profile. That
keeps Python federate code closer to the standard Python surface instead of
forcing users to reason about raw JPype or Py4J exception objects.

## Authentication Composition For 2025

Authentication needs to be treated differently from encoding.

The important architectural point is:

- authentication for `2025` is a composed runtime capability
- it is not a separate Java bridge route
- it is not something JPype or Py4J should own independently

This is the correct mental model:

```text
2025 runtime composition
    =
edition-local RTI surface
  + encoding context
  + authentication context
  + optional authorizer policy
  + selected provider/bridge transport
```

### Why auth is different

Encoding is needed whenever values move across the HLA surface.

Authentication is narrower:

- it is capability-gated
- it is edition-sensitive
- it is provider-sensitive
- it influences connection and authorization policy more than ordinary data
  conversion

So the repo correctly treats it as a factory/runtime composition concern.

### Where the composition lives

The main composition logic lives in:

- `packages/hla-rti-core/src/hla/rti/factory.py`

That layer creates:

- an encoding context
- an authentication context
- a runtime context

For `2025`, that context can include:

- `HLAnoCredentials`
- `HLAplainTextPassword`
- custom typed credential bytes
- optional authorizer-provider behavior

For `2010`, the same layer explicitly does not promote the 2025 auth surface.

### What the bridge should and should not do

The Java bridge should do:

- pass normalized auth-related values when the selected runtime/provider expects
  them
- preserve the selected edition's exception and credential surface
- avoid leaking raw bridge mechanics into auth policy

The Java bridge should not do:

- invent a second authentication model
- treat auth as a route-local feature of JPype or Py4J
- blur the boundary between connection policy and ordinary value conversion

This is especially important for management discussions. If the design is
presented as "JPype auth" or "Py4J auth", the abstraction boundary is wrong.

The correct statement is:

- `2025` may compose authentication into the runtime
- JPype and Py4J are just transport/adaptation routes for that runtime surface

### What changes across 2010 and 2025

For `2010`:

- no promoted 2025-style auth credential family
- no 2025 authorizer-provider story
- no expectation that the bridge surface exposes 2025 auth semantics

For `2025`:

- auth is part of the runtime/factory capability surface
- standard and custom credentials can be represented
- authorizer decisions can be mapped into 2025 exception/decision semantics

### Why this matters for `java_rti_adapter`

For `java_rti_adapter`, this means the implementation should not model
authentication as a bridge package feature.

Instead:

1. keep `auth.py` edition-local under the `2025` surface
2. let runtime/factory composition decide whether auth is in play
3. let the JPype or Py4J bridge carry the resulting values and exceptions
4. keep the 2010 route free of accidental 2025 auth surface bleed-through

That keeps the API shape coherent and avoids the common mistake of mixing:

- transport mechanics
- API edition semantics
- runtime authorization policy

### Proof coverage

The strongest current proof surface for this design is the 2025 auth context
test coverage around:

- no-auth defaults
- plaintext password credentials
- custom typed credentials
- fake authorizer decisions
- provider gating
- runtime connection failures mapped before federation lifecycle work
- redacted evidence output

Primary references:

- `tests/test_rti1516_2025_encoding_auth_contexts.py`
- `tests/test_hla_factory_composition.py`

Management-level takeaway:

- encoding is a universal adaptation concern
- authentication is a 2025 runtime composition concern
- the bridges should transport and normalize these capabilities, not redefine
  them

## The In-Process Java Shim

The repo also carries a local Java-shaped shim backend for testing and bridge
development:

- `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_shim_factory.py`

This is not a real vendor RTI. Its role is to prove:

- the route selection plumbing
- the callback adaptation shape
- the Python wrapper contract

That is why `examples/java_shim_federate.py` is useful for isolated smoke
coverage before involving a real vendor runtime.

## How To Explain This To A New Implementer

If someone asks "how do I add a wrapped Java RTI?" the shortest accurate answer
is:

1. pick JPype first unless you specifically need process separation
2. identify the Java factory implementation string and jar set
3. set `edition` to `2010` or `2025`
4. build `JPypeConfig` or `JavaRTIImplementation`
5. create the wrapped RTI ambassador
6. subclass the edition-specific `NullFederateAmbassador`
7. keep callbacks in standard lowerCamelCase names

The reason this works is that the repository already owns the hard parts:

- edition-aware Java binding profiles
- route-aware bridge construction
- shared callback dispatch
- shared value conversion
- normalized Python-facing RTI wrappers

## Recommended Implementation Approach For `java_rti_adapter`

For the `java_rti_adapter` work, the cleanest path is to treat JPype as the primary
implementation route and Py4J as a second route over the same surface contract.

Recommended approach:

1. define edition-local Python modules that mirror the standard Java package
   families
2. represent Java interface classes first as Python protocol/shape wrappers,
   not as vendor-specific concrete implementations
3. make edition selection explicit at the package edge
4. make bridge selection explicit at the runtime edge
5. keep callback names in standard lowerCamelCase so they map directly from the
   Java side
6. centralize conversion and dispatch policy instead of re-solving it per class

For `java_rti_adapter` specifically, that means:

- start with `jpype` for `2010`
- then add `jpype` for `2025`
- only after that, layer in the Py4J route using the same Python class shapes
- keep `RTIambassador`, `FederateAmbassador`, handles, enums, encoding helpers,
  and exception families edition-local
- keep bridge mechanics in a separate layer from the edition-local API shapes

A practical module split would look like:

```text
java_rti_adapter/
  java/
    hla/
      rti1516e/
        RTIambassador.py
        FederateAmbassador.py
        handles.py
        enums.py
        exceptions.py
      rti1516_2025/
        RTIambassador.py
        FederateAmbassador.py
        handles.py
        enums.py
        exceptions.py
        auth.py
        encoding.py
  bridges/
    jpype/
    py4j/
  common/
    conversion.py
    callback_dispatch.py
    binding_profiles.py
```

The critical architectural rule is:

- do not let JPype-specific or Py4J-specific details leak into the edition-local
  standard API shapes

If you keep that boundary clean, then:

- JPype becomes the fastest path to parity
- Py4J becomes an alternate transport layer, not a second API design
- 2025 auth and encoding additions stay edition-specific instead of infecting
  the 2010 surface

If the goal is early delivery with the least confusion, I would recommend this
order:

1. `2010 + JPype + callback skeletons`
2. `2025 + JPype + callback skeletons`
3. shared conversion/exception/handle adaptation
4. `2025` encoding/auth surface additions
5. Py4J support against the same edition-local shapes

## Recommended Reading Order

1. `docs/java_bridge_wrapping_guide.md`
2. `examples/java_shim_federate.py`
3. `packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/implementation.py`
4. `packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py`
5. `packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py`
6. `docs/java_bridge_encoding_and_bytes.md`
7. `packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`
