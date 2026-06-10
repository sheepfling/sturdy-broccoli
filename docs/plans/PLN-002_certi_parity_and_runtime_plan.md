# PLN-002 CERTI Parity And Runtime Plan

## Purpose

Drive CERTI work from executable parity evidence instead of ad hoc runtime
patching.

This plan treats the pure Python RTI as the semantic reference path and uses
the named CERTI baselines:

- `certi-upstream`: pristine/original CERTI
- `certi-patched`: repo-local vendored/patched CERTI

The standard comparison entrypoint is:

```bash
./tools/certi-easy smoke compare
```

That compare route currently exercises:

1. `§8` time-query and `flushQueueRequest`
2. negotiated ownership end to end
3. release-request ownership branches: `deny`, `confirm`, `ifwanted`

## Current Evidence

### Upstream CERTI

- federation create/join succeeds
- `queryGALT` collapses the RTIA path before stable `§8` query semantics can be
  observed
- negotiated ownership does not complete end to end
- release-request `deny` / `confirm` / `ifwanted` branches do not reach stable
  branch semantics

### Patched CERTI

- reaches stable `queryGALT` / `queryLITS` observations
- `timeAdvanceRequestAvailable` now has a fail-fast real available-grant proof
- `nextMessageRequest` now has a fail-fast real earliest-queued grant proof
- `nextMessageRequestAvailable` now has the same fail-fast real
  earliest-queued grant proof after fixing the RTIA
  `nextEventRequestAvailable(...)` success-path guard
- `flushQueueRequest` no longer throws, now reaches a real grant in the
  promoted no-queued / invalid-GALT baseline, and the Python-facing adapter
  now normalizes integer-time callback typing for the promoted federate
  surface
- the queued-FQR compare slice now matches the promoted ordering/grant
  semantics for the exercised attribute path
- negotiated ownership completes end to end
- release-request branch split is now executable:
  - `deny`: owner retains ownership and no acquisition notification is sent
  - `confirm`: rejected on the release-request path
  - `ifwanted`: transfer succeeds
- negotiated `confirmDivestiture` is now a distinct end-to-end path with
  owner-side precondition enforcement and confirm-tag callback propagation
- the remaining parity caveat is implementation-level rather than
  surface-level: negotiated `confirm` and `ifwanted` still reuse the same
  release-response transfer machinery once transfer is granted

## Decision Rule

Patch CERTI only when all of the following are true:

1. the Python RTI already defines the intended semantics clearly
2. an executable upstream-vs-patched compare proves the gap
3. the gap sits in a promoted clause area we care about

If any of those are false, document the limitation and stop.

## Work Buckets

### Bucket 1: Promoted `§8` Parity

Completed targets:

- `flushQueueRequest`
- `timeAdvanceRequestAvailable`
- `nextMessageRequest`
- `nextMessageRequestAvailable`

What changed:

- `flushQueueRequest` is now promoted cleanly on the patched Python-facing
  surface
- queued FQR ordering and grant computation now match the promoted Python
  reference slice for the exercised attribute path
- integer-time callback typing is normalized on the adapter path
- `timeAdvanceRequestAvailable`, `nextMessageRequest`, and
  `nextMessageRequestAvailable` now have real fail-fast executable evidence on
  the patched runtime
- the `nextMessageRequestAvailable` closure required a real CERTI patch:
  `TimeManagement::nextEventRequestAvailable(...)` returned immediately on the
  success path because the exception guard was inverted

Exit criteria:

- patched CERTI proves stable `§8.9` through `§8.12` semantics on the promoted
  proof slices

Next `§8` follow-up:

- widen upstream-vs-patched attribution only if we decide those additional
  `§8` rows need named-baseline evidence beyond the current patched proofs

### Bucket 2: Ownership Semantic Parity

Primary target:

- distinguish `confirmDivestiture` from
  `attributeOwnershipDivestitureIfWanted`

Current status:

- patched CERTI proves both branches run
- direct compare proves same effective transfer behavior today
- this is a real clause-level parity gap, not a transport issue

Execution sequence:

1. preserve the current compare assertion proving same effective behavior
2. inspect 2010 ownership service mapping for `confirmDivestiture`
3. patch only if the goal is distinct clause semantics rather than merely
   usable runtime behavior
4. replace the equality-style compare with an explicit difference assertion if
   the runtime is corrected

Exit criteria:

- `confirm` and `ifwanted` differ for a reason consistent with the Python
  reference semantics
- docs and matrix reflect the new branch split with executable evidence

### Bucket 3: Upstream Attribution

Primary target:

- determine why pristine upstream collapses before usable `§8` and `§7`
  semantics can be observed

Why this is not first:

- it improves vendor-attribution clarity
- it does not immediately improve the promoted parity path as much as
  `flushQueueRequest`
- patched CERTI already gives us a usable compare surface

Execution sequence:

1. keep upstream untouched
2. use the named compare slices only for attribution
3. investigate upstream failure points separately from patched development

Exit criteria:

- upstream failure reason is explicit enough to classify as vendor limitation
  or an upstream-fix candidate

## What Not To Do

- do not patch the Python adapter/helper layer to fake missing CERTI behavior
- do not collapse upstream and patched evidence into the same conformance claim
- do not keep adding broad CERTI surgery without a promoted compare slice

## Immediate Next Steps

1. shift from promoted `§8` parity back to ownership semantic parity
2. keep the patched `§8.9` / `§8.10` / `§8.11` / `§8.12` proofs in the
   required runtime gate
3. keep the ownership compare slices in the required runtime gate
4. use the Python RTI as the reference for all clause-level semantics

## Success Definition

This plan is succeeding when:

- every promoted CERTI patch target comes from a failing compare row
- every promoted row is attributable as upstream vs patched
- the Python RTI remains the source of truth for intended semantics
- CERTI work either closes a documented parity gap or stops with a precise
  vendor/runtime limitation note
