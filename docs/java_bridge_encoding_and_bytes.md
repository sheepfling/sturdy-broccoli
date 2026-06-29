# Java Bridge Encoding And Bytes

Use this page when the question is not just "how do I wrap a Java RTI?" but:

- how do Python `bytes` become Java `byte[]`?
- how do encoded HLA data elements cross the JPype or Py4J boundary?
- how do we verify that raw bytes are preserved exactly?
- what is different between JPype and Py4J at that boundary?

This document belongs to the backend and route wrapping surface described in
[`work_surfaces.md`](work_surfaces.md).

Read this after:

- [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
- [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md)

Keep [`java_bridge_adaptation_policy.md`](java_bridge_adaptation_policy.md)
next to this page when debugging overloads that involve `byte[]`,
`LogicalTime`, handle-value maps, or credentials.

## The Short Version

The repository treats byte preservation as a contract, not a convenience.

The invariant is:

1. Python `bytes` go into the bridge as exact octets.
2. The bridge materializes a Java `byte[]` without changing byte values.
3. Java encoder output comes back to Python as exact `bytes`.
4. Callback payloads such as `userSuppliedTag` stay byte-exact across the
   boundary.

That rule applies to:

- standard HLA encoder payloads
- `userSuppliedTag`
- handle-value-map payload bytes
- 2025 authentication credential bytes

## Where The Boundary Lives

The core bridge contract lives in
[`../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py`](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_common.py).

The key hooks are:

- `JavaBridge.byte_array(data: bytes) -> Java byte[]`
- `JavaBridge.is_byte_array(value) -> bool`
- `JavaBridge.to_python_bytes(value) -> bytes`

Those methods define the byte handoff that JPype and Py4J must honor.

Route-local implementations live in:

- [`../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py`](../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py)
- [`../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py`](../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py)

## Canonical Invariants

These are the rules to preserve when editing the bridge.

1. Python-facing binary payloads are `bytes`.
2. The bridge may use route-local machinery to create Java `byte[]`.
3. Signed Java byte representation must not change the underlying octet values.
4. Inbound Java `byte[]` must normalize back to immutable Python `bytes`.
5. The bridge must prefer Java-side encoding when a live Java encoder or
   factory exists.
6. Python helper objects must not silently substitute their own
   `toByteArray()` behavior when the Java encoder path is supposed to own the
   encoding.

That last point matters because it protects the repo from accidentally proving
"our Python helper encodes like Java" when the real requirement is "the live
Java surface encodes and returns the same bytes we expect."

## End-To-End Flow

The most important byte paths look like this:

```text
Python bytes / Python data element
    ->
shared bridge conversion policy
    ->
JPypeBridge.byte_array(...) or Py4JBridge.byte_array(...)
    ->
Java byte[] / Java encoder object / Java Credentials object
    ->
vendor RTI or shim class
    ->
Java byte[]
    ->
JavaBridge.to_python_bytes(...)
    ->
Python bytes
```

For callbacks such as `announceSynchronizationPoint(..., userSuppliedTag)`, the
same rule applies in reverse: the callback dispatcher receives the Java-side
value and normalizes the payload into Python-side byte-safe shapes before the
standard callback surface sees it.

## JPype Quirks

JPype is the more direct route.

Useful properties:

- it exposes Java classes directly
- it can build a real Java `byte[]` through `JArray(JByte)`
- it is easier to inspect exact Java class identities
- it is the clearest route for debugging encoding fidelity

Important byte-specific quirk:

- Java bytes are signed, Python bytes are unsigned

The JPype route therefore explicitly maps octets above `127` into signed Java
byte values by subtracting `256` during array creation, then maps them back on
return through `to_python_bytes(...)`.

That behavior is implemented in
[`../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py`](../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py).

## Py4J Quirks

Py4J uses a gateway object model instead of direct JVM objects in the Python
process.

Useful properties:

- it supports process separation
- it can attach to an already-running Java process shape
- it still honors the same shared byte and overload policy

Important byte-specific quirks:

- Java arrays are created indirectly through the gateway
- callback objects are Python proxies exposed to Java
- falling back to implicit or route-local conversion is riskier than in JPype

The Py4J route therefore explicitly allocates `Byte.TYPE` arrays when possible
and relies on the shared `to_python_bytes(...)` normalization on return.

That behavior is implemented in
[`../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py`](../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py).

## What We Verify

The current verification story is stronger than the docs previously made
obvious.

### 1. Live Java encoder oracle proof

The most direct proof lives in
[`../tests/runtime/test_optional_real_java_bridges.py`](../tests/runtime/test_optional_real_java_bridges.py).

Those tests verify, for both JPype and Py4J:

- Java encoder materialization of `HLAASCIIstring`
- Java encoder materialization of `HLAunicodeString`
- Java encoder materialization of `HLAfixedRecord`
- exact byte output returned from live Java classes
- that Python-side `toByteArray()` is not incorrectly used when the Java route
  should own encoding

This is the strongest proof point because it checks live Java classes rather
than only Python shims.

### 2. Real vendor encoder proof

Real vendor proof lives in
[`../tests/vendors/test_real_vendor_runtime_smoke.py`](../tests/vendors/test_real_vendor_runtime_smoke.py).

Those tests verify the same byte-preservation story against real vendor bridge
lanes such as:

- `pitch-jpype`
- `pitch-py4j`

They also prove that vendor-created Java encoder objects round-trip back to the
expected Python `bytes`.

### 3. 2025 authentication byte proof

The 2025 auth surface is byte-sensitive.

The Python-side credential definitions live in
[`../packages/hla-rti1516-2025/src/hla/rti1516_2025/auth.py`](../packages/hla-rti1516-2025/src/hla/rti1516_2025/auth.py).

Important rules:

- `HLAnoCredentials` must encode to empty bytes
- `HLAplainTextPassword` must preserve its standard byte encoding
- the bridge must materialize the matching Java credentials class where the
  route supports it

The optional live Java bridge tests verify that those credential objects come
back with the expected Java class names, type names, and byte payloads.

## What This Means For `userSuppliedTag`

`userSuppliedTag` is not "just a random argument." It is part of the
byte-preservation contract.

When a service or callback carries `userSuppliedTag`, the bridge must treat it
as raw binary payload:

- no implicit text decoding
- no path-dependent transformation between JPype and Py4J
- no convenience rewriting for one vendor route

If a route cannot preserve the bytes exactly, that is a bridge bug.

The minimal bridge examples in
[`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
already show the right reading pattern:

```python
def announceSynchronizationPoint(self, synchronizationPointLabel, userSuppliedTag):
    print("sync point", synchronizationPointLabel, bytes(userSuppliedTag))
```

That is not stylistic. It is acknowledging that the payload is binary.

## What This Means For Encoder Objects

When a Python HLA data element crosses into a Java-backed route, the preferred
proof path is:

1. materialize a live Java encoder object
2. ask Java for its byte representation
3. normalize that value back to Python bytes
4. compare against the expected standard encoding bytes

This is better than trusting only Python-side `encode()` helpers because it
checks the actual bridge boundary and Java runtime behavior.

## Failure Modes To Watch

Most byte bugs here come from one of these:

1. signed-byte conversion mistakes above `0x7F`
2. accidental use of text strings where raw bytes are required
3. route-local fallback behavior masking a live Java encoder issue
4. Python-side `toByteArray()` accidentally running when the Java oracle should
   have been the source of truth
5. Py4J gateway object conversion behaving differently from direct JPype class
   handling

When investigating these, read this page together with
[`java_bridge_adaptation_policy.md`](java_bridge_adaptation_policy.md),
because some apparent byte bugs are really overload-selection bugs involving
`byte[]`.

## Recommended Reading Order

1. [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
2. [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md)
3. [`java_bridge_encoding_and_bytes.md`](java_bridge_encoding_and_bytes.md)
4. [`java_bridge_adaptation_policy.md`](java_bridge_adaptation_policy.md)
5. [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md)
