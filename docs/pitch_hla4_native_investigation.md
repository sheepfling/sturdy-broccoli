# Pitch HLA4 Native Investigation

Use this page when the question is:

"Can we test IEEE 1516.1-2025 against Pitch through a real HLA4 surface rather
than only through the current adapter wrappers?"

Short answer: yes, the bundled Pitch runtime strongly suggests that we can and
should separate two different 2025 routes.

## One-Page Summary

The Pitch bundle in `third_party/pitch/PITCH-prti1516e-manual` contains a real
HLA4 Java and FedPro surface:

- `lib/prti1516_202X.jar`
- `lib/fedpro-client-hla4.jar`
- `samples/chat-java-hla4/chat-java-hla4.jar`
- `samples/chat-java-hla4-fedpro/chat-java-hla4-fedpro.jar`

That means the repo should distinguish:

1. adapter 2025 route
   - current `pitch-202x-jpype`
   - current `pitch-202x-py4j`
   - wraps `python1516_2025`
   - behavior discovery only
2. native HLA4 route
   - proposed `pitch-native-202x-jpype`
   - proposed `pitch-native-202x-py4j`
   - binds directly to vendor `hla.rti1516_202X`
   - should count as actual vendor-runtime evidence if it works

## What The Bundle Proves

### Native Java HLA4 API Is Present

The vendor jar `lib/prti1516_202X.jar` contains:

- `hla/rti1516_202X/RTIambassador.class`
- `hla/rti1516_202X/RtiFactory.class`
- `hla/rti1516_202X/RtiFactoryFactory.class`
- `hla/rti1516_202X/auth/...`
- `hla/rti1516_202X/encoding/...`
- `hla/rti1516_202X/time/...`

This is not a repo-invented surface. It is a real vendor API surface.

### Native HLA4 FedPro Client Is Present

The vendor jar `lib/fedpro-client-hla4.jar` registers service entries for:

- `hla.rti1516_202X.RtiFactory`
- `hla.rti1516_202X.time.LogicalTimeFactory`

Resolved implementations:

- `se.pitch.oss.fedpro.client.hla.RtiFactoryImpl`
- `se.pitch.oss.fedpro.client.hla.time.HLAfloat64TimeFactoryImpl`
- `se.pitch.oss.fedpro.client.hla.time.HLAinteger64TimeFactoryImpl`

That is the strongest local evidence that a real HLA4 FedPro route exists.

### Native HLA4 Samples Are Present

The bundle ships sample launchers:

- `samples/chat-java-hla4/chat-java-hla4.sh`
- `samples/chat-java-hla4-fedpro/chat-java-hla4-fedpro.sh`

Jar manifests:

- `chat-java-hla4.jar`
  - `Main-Class: se.pitch.chat1516_4.Chat`
  - `Class-Path: ../../lib/prti1516e.jar`
- `chat-java-hla4-fedpro.jar`
  - `Main-Class: se.pitch.oss.chat1516_4.Chat`
  - `Class-Path: ../../lib/fedpro-client-hla4.jar`

The second one is especially important because it demonstrates a vendor-owned
HLA4 FedPro sample path.

### Native HLA4 Operator Path Is Visible

The shipped HLA4 samples show the exact client-side split:

- direct/native HLA4 sample
  - `RtiFactoryFactory.getRtiFactory()`
- FedPro/native HLA4 sample
  - `RtiFactoryFactory.getRtiFactory("Federate Protocol")`

Both then use the same connection object shape:

- `RtiConfiguration.createConfiguration().withRtiAddress(<host>)`
- `RTIambassador.connect(..., CallbackModel.HLA_IMMEDIATE, rtiConfiguration)`

That is important because it means the native HLA4 route is not hidden behind
some repo-specific abstraction. The vendor samples already expose the seam the
repo needs to wrap.

The shipped client settings also expose the HLA4 authorization seam:

- `user.home/prti1516e/prti1516eLRC.settings`
  - `LRC.overridePlainTextPasswordFlag`
  - `LRC.overridePlainTextPassword`

So the concrete native operator model is:

1. select the client jar family
2. select the factory path
3. pass the RTI address through `RtiConfiguration`
4. optionally layer HLA4 authorization through the LRC password settings

This is a much stronger signal than the earlier guess that there might be one
magic server-side "enable HLA4" flag.

## Why The Current Repo Route Is Not Enough

The current `pitch-202x-*` plugins are explicit adapter routes, not native
Pitch HLA4 routes.

They currently report:

- `adapter_status = "python1516_2025-wrapped"`
- `counts_as_vendor_runtime = False`

See:

- [../packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/plugin.py](../packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/plugin.py)
- [../packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/plugin.py](../packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/plugin.py)

So today the repo answers:

"Can we make Python 2025 look like Pitch HLA4?"

It does not yet answer:

"Can we drive Pitch's own HLA4 API and runtime natively from JPype or Py4J?"

## Two 2025 Routes We Should Test

### Route 1: Library-Scoop Direct

Goal:

- bind directly to vendor `hla.rti1516_202X`
- exercise client API, encoding, auth, and time factories
- do not require a claim that the full runtime path is proven yet

Bridge variants:

- JPype
- Py4J

First smoke goals:

1. load the HLA4 API jars
2. resolve `RtiFactoryFactory`
3. obtain a native HLA4 `RtiFactory`
4. obtain encoder and logical-time factories
5. create an RTI ambassador object successfully

### Route 2: Native Runtime Route

Goal:

- run the actual Pitch runtime path that accepts the HLA4/FedPro client
- prove connect, create, join, publish, subscribe, and one exchange

This is the route where a runtime-side mode or startup selection may matter.

## Most Likely Native HLA4 Classpath

For the direct Java bridge spike, the likely minimum classpath is:

- `third_party/pitch/PITCH-prti1516e-manual/lib/prti1516_202X.jar`

For the native HLA4 FedPro path, the likely minimum classpath is:

- `third_party/pitch/PITCH-prti1516e-manual/lib/fedpro-client-hla4.jar`

Possible supporting jars if required by the vendor runtime:

- `third_party/pitch/PITCH-prti1516e-manual/lib/fedpro-session.jar`
- `third_party/pitch/PITCH-prti1516e-manual/lib/protobuf-java-3.21.7.jar`
- `third_party/pitch/PITCH-prti1516e-manual/lib/protobuf.jar`
- `third_party/pitch/PITCH-prti1516e-manual/lib/slf4j-api-2.0.5.jar`
- `third_party/pitch/PITCH-prti1516e-manual/lib/slf4j-nop-2.0.5.jar`

The smallest spike should start with the sample-proven classpath first and add
support jars only if classloading proves they are needed.

## Likely Factory Entry Path

The repo's existing Java bridge stack already has the right seam:

- bridge config takes `classpath`
- bridge config takes `rti_factory_name`
- bridge config takes `connect_local_settings_designator`

Relevant code:

- [../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py](../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/runtime.py)
- [../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/factory.py](../packages/hla-bridge-java-jpype/src/hla/bridges/java/jpype/factory.py)
- [../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py](../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/runtime.py)
- [../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/factory.py](../packages/hla-bridge-java-py4j/src/hla/bridges/java/py4j/factory.py)
- [../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_intake_backend.py](../packages/hla-bridge-java-common/src/hla/bridges/java/common/java_intake_backend.py)

The first native spike should use the generic Java intake path rather than
reusing the current adapter plugin classes.

## Likely Native JPype Smoke

Proposed first spike sequence:

1. use JPype with classpath:
   - `prti1516_202X.jar`
2. resolve:
   - `hla.rti1516_202X.RtiFactoryFactory`
3. call:
   - `getRtiFactory()` or `getRtiFactory(<name>)`
4. verify:
   - encoder factory exists
   - logical time factory exists
   - RTI ambassador can be created

If the plain HLA4 jar is not enough for a runnable RTI object, repeat with:

- `fedpro-client-hla4.jar`
- `connect_local_settings_designator`

## Likely Native Py4J Smoke

Proposed first spike sequence:

1. launch Py4J gateway with classpath:
   - `prti1516_202X.jar`
2. resolve:
   - `gateway.jvm.hla.rti1516_202X.RtiFactoryFactory`
3. obtain factory
4. create ambassador
5. verify encoder and logical-time helpers

Then repeat with:

- `fedpro-client-hla4.jar`
- local settings designator for the FedPro endpoint

## Runtime-Side Surface To Inspect

The likely runtime-side seam is not a single repo CLI flag. It is probably a
combination of:

- classpath selection
- HLA4 client jar selection
- FedPro local-settings designator
- FedPro server configuration

Useful local files:

- `third_party/pitch/PITCH-prti1516e-manual/bin/FederateProtocolServer`
- `third_party/pitch/PITCH-prti1516e-manual/bin/FederateProtocolServer.vmoptions`
- `third_party/pitch/PITCH-prti1516e-manual/user.home/prti1516e/FedProServer.properties`
- `third_party/pitch/PITCH-prti1516e-manual/user.home/prti1516e/FedProClient.logging`
- `third_party/pitch/PITCH-prti1516e-manual/api/fedpro/RTIambassador.proto`
- `third_party/pitch/PITCH-prti1516e-manual/api/fedpro/FederateAmbassador.proto`

Current local server properties are very generic:

- `server-address = all`
- `protocol = tcp`
- `interactive = false`

Nothing there yet proves or disproves a separate HLA4 enable flag. The stronger
signal still points to client jar and factory selection first, with the same
FedPro server process behind both the older and newer client surfaces.

## Current Repo Spike Status

The repo now has explicit native discovery/backend names for this split:

- `pitch-native-202x-jpype`
- `pitch-native-202x-py4j`

Each supports two surface modes:

- `surface="direct"`
- `surface="fedpro"`

Current intent:

- `direct`
  - prove the vendor HLA4 API and factory path can be driven natively
- `fedpro`
  - prove the vendor HLA4 client can talk through the normal Pitch runtime path

The new smoke target should stay narrow:

- start local Pitch runtime
- create native HLA4 RTI ambassador
- connect through `RtiConfiguration.withRtiAddress("localhost")`
- disconnect cleanly

That is enough to keep the route live while deeper federation-management proof
is still being built.

## Recommended Repo Shape

Do not overload the current adapter route names.

Keep:

- `pitch-202x-jpype`
- `pitch-202x-py4j`

Meaning:

- adapter-backed route over `python1516_2025`

Add:

- `pitch-native-202x-jpype`
- `pitch-native-202x-py4j`

Meaning:

- direct vendor HLA4 route

## First Test Ladder

### Step 1: Native API Discovery

Add tests that prove:

- HLA4 jar path exists
- HLA4 FedPro jar path exists
- factory class is resolvable
- logical-time factory service entries are present

### Step 2: Native Factory Smoke

Add tests that prove:

- JPype can instantiate HLA4 factory path
- Py4J can instantiate HLA4 factory path

### Step 3: Native Runtime Smoke

Add a two-federate smoke for:

- connect
- create federation
- join federation
- publish and subscribe
- one interaction or reflection
- resign and destroy

### Step 4: One 2025-Specific Capability

After the smoke works, test one feature that is meaningful for 2025:

- typed credentials
- authorizer surface
- HLA4-specific encoding type such as `HLAextendableVariantRecord`

## Current Practical Constraint

This repository snapshot does not yet prove the native HLA4 route because the
current checked-in Pitch `202x` backends are adapter-only and the local shell
session used during this investigation did not have a working Java runtime for
`jar`/`javap` deep inspection.

That does not block the spike design. It only limits how much of the vendor
Java bytecode surface can be interrogated from the shell.
