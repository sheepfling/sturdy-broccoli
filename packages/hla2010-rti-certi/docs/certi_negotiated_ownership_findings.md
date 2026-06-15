# CERTI Negotiated Ownership Findings

Investigation notes for the local CERTI IEEE 1516.1-2010 runtime on negotiated
ownership services.

## Current repo status

As of June 7, 2026, the current `hla-2010` vendor matrix result is:

- plain CERTI ownership passes on:
  - `certi`
- negotiated CERTI ownership is still vendor-divergent on:
  - `certi`

The observable runtime failure is that the negotiated ownership scenario never
reaches the expected release/acquisition handshake. In the current matrix this
surfaces at
[scenario_ownership.py](../../hla2010-verification-harness/src/hla2010_verification_harness/scenario_ownership.py)
as a missing `attributeOwnershipAcquisitionNotification`/handoff outcome rather
than as a Python adapter crash.

That means the current matrix should describe negotiated ownership as a vendor
divergence, not as an environment skip and not as a completed patched-CERTI
success path.

Decision for the compliance matrix:

- do not patch around this in the `hla-2010` adapter/helper layer
- record it as a real CERTI vendor limitation until the runtime itself proves
  the negotiated release/acquisition handshake

Reason:

- the same failure reproduces on native CERTI and the patched local build
  profile
- that makes this a runtime/vendor behavior gap, not a Python bridge-only bug

## Scope

This note covers the negotiated ownership path behind:

- `negotiatedAttributeOwnershipDivestiture`
- `attributeOwnershipAcquisition`
- `attributeOwnershipDivestitureIfWanted`
- `cancelAttributeOwnershipAcquisition`

The goal was to determine whether the current failures should be patched around
in the Python adapter/helper layer or treated as a vendor/runtime limitation.

## Source Findings

### Explicit gaps in the 2010 client implementation

- [RTIambassadorImplementation.cpp](../../../CERTI/libRTI/ieee1516-2010/RTIambassadorImplementation.cpp)
  marks `confirmDivestiture` as `Not yet implemented`.
- [RTIambassadorImplementation.cpp](../../../CERTI/libRTI/ieee1516-2010/RTIambassadorImplementation.cpp)
  marks `attributeOwnershipReleaseDenied` as `Not Implemented`.

Those are hard evidence that the 2010 ownership surface is incomplete on the
client side.

### Server-side ownership logic does exist

- [MessageProcessor.cc](../../../CERTI/RTIG/MessageProcessor.cc)
  routes negotiated divestiture, acquisition, release response, and cancel
  messages into federation logic.
- [Federation.cc](../../../CERTI/RTIG/Federation.cc)
  forwards those requests into object-class ownership code.
- [ObjectClass.cc](../../../CERTI/libCERTI/ObjectClass.cc)
  contains a coherent state machine:
  - negotiated divestiture marks attributes as divesting when there are no candidates
  - acquisition on divesting attributes grants immediately and notifies the old owner
  - acquisition on non-divesting owned attributes requests release from the current owner
  - release response transfers ownership to a candidate
  - cancellation removes pending candidates

So the codebase is not simply missing the feature at every layer.

### The available CERTI tests do not give end-to-end ownership proof

- [tests/RTIG/CMakeLists.txt](../../../CERTI/tests/RTIG/CMakeLists.txt)
  defines a `TestRTIG` gtest target that would include
  `messageprocessor_test.cpp` and `federation_test.cpp`.
- The current local build tree does not expose that target:
  - `cmake --build hla-2010/.local/certi/patched/build --target TestRTIG`
    fails with `No rule to make target 'TestRTIG'`.
- The ownership-specific source tests that do exist in
  [messageprocessor_test.cpp](../../../CERTI/tests/RTIG/messageprocessor_test.cpp)
  are only empty-message dispatch checks. They assert that malformed ownership
  request messages throw, not that negotiated ownership completes across a
  running RTIA/RTIG pair.

That means there is no local built CERTI test harness here that already proves
the negotiated ownership path. Reproducing and fixing the issue inside CERTI
would require source-level work in the 2010 client/runtime itself, not merely a
wrapper adjustment.

### Local patch feasibility split

- A narrow client-side patch for `confirmDivestiture` is realistic because
  CERTI already has a release-response message path:
  - `M_Attribute_Ownership_Release_Response`
  - `NM_Attribute_Ownership_Release_Response`
  - `OwnershipManagement::attributeOwnershipRealeaseResponse(...)`
  - `MessageProcessor::process(NM_Attribute_Ownership_Release_Response&&)`
- In the local CERTI branch `codex/ieee1516e-confirm-divestiture`, the 2010
  `confirmDivestiture` client service was patched to reuse that path and the
  `RTI1516e` target rebuilt successfully.
- `attributeOwnershipReleaseDenied` is materially different:
  - there is no corresponding `NM_...Release_Denied` network message in the
    protocol definitions
  - there is no `OwnershipManagement` service for it
  - there is no `MessageProcessor` / `Federation` / `ObjectClass` path that
    handles an explicit denial from the current owner

So `confirmDivestiture` is a plausible local CERTI client patch. `attributeOwnershipReleaseDenied`
is a larger protocol/runtime extension and should not be described as a quick
client-side fix.

### Result of the patched local build

- `hla-2010` now supports a build-overlay mode via `HLA2010_CERTI_BUILD_ROOT`
  so the real smoke can load rebuilt CERTI libraries ahead of the installed
  ones.
- Using that overlay with the local CERTI branch:
  - `confirmDivestiture` client mapping compiled successfully
  - the initial `attributeOwnershipReleaseDenied` protocol path compiled
    successfully through `libCERTI`, `RTI1516e`, and `rtig`
- The real negotiated ownership smoke still skips with the same runtime error:
  - `rti1516e::RTIinternalError: libRTI: Network Read Error waiting RTI reply`

So the current source work is real progress on the missing 2010 ownership
surface, but it has not yet changed the end-to-end negotiated ownership outcome
in this workspace.

### Direct CERTI-side harness result

- A dedicated CERTI-side ownership probe now exists on the patch branch:
  - [ownershipProbe-IEEE1516_2010.cc](../../../CERTI/test/testFederate/ownershipProbe-IEEE1516_2010.cc)
  - [run_ownership_probe.sh](../../../CERTI/test/testFederate/run_ownership_probe.sh)
  - [rtia_verbose_wrapper.sh](../../../CERTI/test/testFederate/rtia_verbose_wrapper.sh)
- The probe runs below `hla-2010` and talks directly to the patched CERTI
  `RTI1516e` client/runtime path.
- Current outcome for both owner and acquirer paths:
  - `M_Open_Connexion` succeeds
  - `M_Create_Federation_Execution_V4` or `M_Join_Federation_Execution_V4`
    send and receive complete successfully at the client socket layer
  - `processException(...)` then reports `Exception::Type::RTIinternalError`
    with an empty reason string
- The local RTIA logs for those runs show only:
  - `OPEN_CONNEXION`
  - `CLOSE_CONNEXION`
- That means the direct failure is now isolated to the CERTI 1516-2010
  client/runtime reply path itself, not the `hla-2010` adapter layer and not a
  socket write/read failure in the helper path.

### Updated direct 1516-2010 findings after RTIA/RTIG instrumentation

- The spawned RTIA `-f` path is now instrumented in:
  - [RTIA.cc](../../../CERTI/RTIA/RTIA.cc)
  - [Communications.cc](../../../CERTI/RTIA/Communications.cc)
  - [RTIA_federate.cc](../../../CERTI/RTIA/RTIA_federate.cc)
  - [FederationManagement.cc](../../../CERTI/RTIA/FederationManagement.cc)
  - [Federation_fom.cc](../../../CERTI/RTIG/Federation_fom.cc)
- That instrumentation showed the original empty `RTIinternalError` at
  create/join was actually a FOM-module rejection from RTIG, not a blind
  transport failure.
- CERTI's FOM-module merge rule in
  [RootObject.cc](../../../CERTI/libCERTI/RootObject.cc)
  rejected normal 2010 modules because it required an existing class from the
  MIM, especially `HLAobjectRoot`, to repeat the full MIM-owned attribute set.
- A local patch now treats empty repeated class definitions as scaffolding,
  which is enough for the direct 1516-2010 path to accept CERTI's own shipped
  [RestaurantFOMmodule.xml](../../../CERTI/xml/ieee1516-2010/1516_2-2010/RestaurantFOMmodule.xml).
- With that patch in place, direct 1516-2010 `createFederationExecution(...)`
  and `joinFederationExecution(...)` complete successfully in the dedicated
  ownership harness.
- The failure has therefore moved downstream into negotiated ownership itself:
  - owner reaches `negotiatedAttributeOwnershipDivestiture`
  - acquirer reaches `attributeOwnershipAcquisition`
  - the owner side then receives `RTIinternalError: Connection closed by client`
  - RTIA/RTIG terminate or collapse immediately afterward
- This reproduces below `hla-2010` and is therefore a direct CERTI runtime
  failure in negotiated ownership processing, not merely a create/join or FOM
  intake problem.

### RTIG ownership-path narrowing

- RTIG ownership instrumentation now exists in:
  - [MessageProcessor.cc](../../../CERTI/RTIG/MessageProcessor.cc)
  - [Federation.cc](../../../CERTI/RTIG/Federation.cc)
  - [ObjectClass.cc](../../../CERTI/libCERTI/ObjectClass.cc)
- The latest direct `deny` probe with a two-phase harness barrier shows RTIG
  progresses through:
  - `MessageProcessor::process(NM_Negotiated_Attribute_Ownership_Divestiture)`
  - `Federation::negotiateDivestiture(...)`
  - `ObjectClass::negotiatedAttributeOwnershipDivestiture(...)`
  - attribute state change to `divesting=true`
  - start of `broadcastClassMessage(...)` for
    `NM_Request_Attribute_Ownership_Assumption`
- The last emitted RTIG line is:
  - `"[objectclass-ownership] negotiatedDivestiture broadcast assumptions count=1"`
- After that, RTIG/RTIA terminate and the owner receives
  `RTIinternalError: Connection closed by client`.
- The acquirer-side barrier now proves the owner never reaches the point where
  branch-specific `confirmDivestiture`, `attributeOwnershipReleaseDenied`, or
  `attributeOwnershipDivestitureIfWanted` could matter:
  - the `owner-divesting` marker is never written
  - the acquirer exits waiting for the owner to enter divesting state

That specific broadcast-path crash is now fixed. The root cause was a bad
message accessor in
[ObjectClass.cc](../../../CERTI/libCERTI/ObjectClass.cc):

- the `REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION` branch in
  `broadcastClassMessage(...)` read `getMsgRAV()->getAttributesSize()`
  instead of `getMsgRAOA()->getAttributesSize()`

After that patch, the direct 1516-2010 negotiated-divestiture path no longer
tears down RTIG/RTIA during assumption fanout.

### Direct release-request branch separation

The ownership probe was then adjusted so it no longer used
`negotiatedAttributeOwnershipDivestiture(...)` to try to distinguish
`deny` / `confirm` / `ifwanted`.

That matters because CERTI's current ownership state machine takes
`negotiatedAttributeOwnershipDivestiture(...)` with no pending candidates down
the assumption path by design:

- owner marks the attribute `divesting=true`
- RTIG broadcasts `REQUEST_ATTRIBUTE_OWNERSHIP_ASSUMPTION`
- the owner never receives `requestAttributeOwnershipRelease`

To force the release-request branch, the probe now:

- leaves the owner in the normal owned, non-divesting state
- has the acquirer call `attributeOwnershipAcquisition(...)`
- waits for the owner-side `requestAttributeOwnershipRelease` callback
- only then invokes:
  - `attributeOwnershipReleaseDenied`
  - `confirmDivestiture`
  - `attributeOwnershipDivestitureIfWanted`

With that corrected scenario, all three direct CERTI 1516-2010 runs complete:

- `deny`
  - owner receives `requestAttributeOwnershipRelease`
  - owner calls `attributeOwnershipReleaseDenied`
  - RTIG clears the candidate and no acquisition notification reaches the
    acquirer before timeout
- `confirm`
  - owner receives `requestAttributeOwnershipRelease`
  - owner calls `confirmDivestiture`
  - the acquirer receives
    `attributeOwnershipAcquisitionNotification`
- `ifwanted`
  - owner receives `requestAttributeOwnershipRelease`
  - owner calls `attributeOwnershipDivestitureIfWanted`
  - the acquirer receives
    `attributeOwnershipAcquisitionNotification`

This also makes the current CERTI mapping explicit:

- `confirmDivestiture` and `attributeOwnershipDivestitureIfWanted` still reuse
  the same underlying release-response transfer machinery
- but they are no longer equivalent at the 2010 surface in the patched local
  branch:
  - release-request `confirm` is rejected as
    `AttributeDivestitureWasNotRequested`
  - negotiated `confirm` now succeeds only after a real
    `requestDivestitureConfirmation` callback
  - negotiated `confirm` now propagates the owner-supplied confirm tag through
    the resulting acquisition notification
- `deny` remains distinct because it clears candidates instead of granting
  transfer

## Runtime Findings

The real probe in
[tests/vendors/README.md](../../../tests/vendors/README.md)
shows:

- exchange, time, synchronization, unconditional divestiture, acquisition-if-available, and ownership query all pass
- the earlier negotiated ownership crash has been fixed in the local CERTI
  branch
- the remaining question is now behavioral parity, not transport stability

That means the current issue is no longer raw runtime instability. It is now
about documenting and testing the exact negotiated-ownership semantics that the
patched local CERTI 2010 branch actually exposes.

## Decision

Treat this as a **vendor/runtime limitation** for the current workspace, not as
something to patch around in the Python adapter/helper layer.

Reasoning:

- A helper-side workaround would fabricate ownership behavior outside the RTI,
  which would hide real backend differences instead of exposing them.
- The pure Python RTI is the right place to model the intended contract.
- The currently configured CERTI build does not provide an end-to-end ownership
  regression target we can lean on while patching.
- The CERTI runtime should remain classified according to what it can actually
  do end to end, not what the wrapper could pretend it did.

## Practical Outcome

- The pure Python RTI should continue to evolve toward the coherent ownership
  state machine visible in the CERTI source.
- The CERTI negotiated path should move from `probe-fails` toward clause-level
  classification based on the now-stable direct probe:
  - `deny` path works
  - `confirm` path works via release-response mapping
  - `ifwanted` path works via the same release-response mapping
  - `confirm` and `ifwanted` are not yet distinct in CERTI's 2010 service
    implementation
