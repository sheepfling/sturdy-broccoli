# Federation Orchestration

This is the operator-facing map for how this repo starts small federations,
coordinates startup, and processes callbacks.

Use it when you want to:

- understand the actual startup order used in tests and showcases
- build a similar federation without inventing your own orchestration layer
- know where callback pumping happens and what "multi-federate" means here
- understand what is and is not parallel today
- know where performance limits come from before changing the route or runtime

## Short Version

The current local proof lanes are intentionally conservative:

- startup is explicit: `connect -> create -> join -> publish/subscribe -> run`
- startup synchronization is explicit: register `ReadyToRun`, drain callbacks,
  achieve, drain again
- callback delivery is usually explicit polling, not a hidden worker thread
- multi-federate does not automatically mean multi-process

For the local 2010 showcase lane, two ambassadors usually share one in-memory
engine. For the local 2025 showcase lane, two in-process ambassadors each keep
their own local state and callback queue, while federation state is shared by
the backend runtime. In both cases, the scenario drives progress by explicitly
calling `evokeMultipleCallbacks(...)`.

Management-level summary:

- the default local proof lanes are deterministic before they are fast
- callback progress is usually driven by explicit polling, not by a hidden
  background dispatcher
- multiple federates does not imply multiple processes or parallel execution
- the main performance cost is often orchestration style, not an unavoidable
  HLA limitation

## The Reusable Startup Helper

The main helper lives in
[`packages/hla-verification/src/hla/verification/startup.py`](../packages/hla-verification/src/hla/verification/startup.py).

It provides:

- `FederationStartupConfig`
- `connect_create_join(...)`
- `register_startup_sync_point(...)`
- `achieve_startup_sync_point(...)`
- `synchronize_ready_to_run(...)`
- `drain_callbacks(...)`

This helper is intentionally thin. It does not hide HLA semantics. It wraps the
normal RTI service order so tests and demos stay readable while preserving the
actual orchestration boundary.

## Startup Sequence

The normal startup sequence in this repo is:

1. `connect`
2. `create federation execution`
3. `join federation execution`
4. publish and subscribe
5. register objects if needed
6. drain callbacks
7. send updates and interactions
8. drain callbacks again
9. resign, destroy, disconnect

`connect_create_join(...)` covers steps 1 through 3.

Important behavior:

- `create` is allowed to race
- `FederationExecutionAlreadyExists` is treated as normal
- the second federate usually joins the already-created federation

That behavior is implemented in
[`packages/hla-verification/src/hla/verification/startup.py`](../packages/hla-verification/src/hla/verification/startup.py).

The startup helper is exercised directly in
[`tests/scenarios/test_startup_sync_fom_java_translation_v09.py`](../tests/scenarios/test_startup_sync_fom_java_translation_v09.py).

## Startup Synchronization

The repo standard startup sync point is `ReadyToRun`.

The helper sequence is:

1. one federate registers `ReadyToRun`
2. all participating RTIs drain callbacks until the announcement is observed
3. each federate calls `synchronizationPointAchieved`
4. all RTIs drain callbacks again until `federationSynchronized` is delivered

That exact pattern is implemented by `synchronize_ready_to_run(...)` in
[`packages/hla-verification/src/hla/verification/startup.py`](../packages/hla-verification/src/hla/verification/startup.py).

This matters because the repo does not assume that join completion implies
scenario readiness. Publication, subscription, object discovery, and some
callback-visible lifecycle state still need a clean barrier.

Useful proof references:

- late join behavior:
  [`tests/scenarios/test_startup_sync_fom_java_translation_v09.py`](../tests/scenarios/test_startup_sync_fom_java_translation_v09.py)
- failed participant synchronization:
  [`tests/scenarios/test_startup_sync_fom_java_translation_v09.py`](../tests/scenarios/test_startup_sync_fom_java_translation_v09.py)

## Callback Processing Model

The default model used by these local tests and showcases is `HLA_EVOKED`.

That means callbacks are not assumed to arrive because a background thread is
secretly pumping the RTI. The scenario or helper explicitly calls:

- `evokeMultipleCallbacks(...)` for the 2010 façade
- `evokeMultipleCallbacks(...)` for the 2025 façade

The repo standard helper for this is bounded deterministic draining, not open-
ended waiting. See:

- [`packages/hla-verification/src/hla/verification/startup.py`](../packages/hla-verification/src/hla/verification/startup.py)
- [`packages/hla-verification/src/hla/verification/scenario_support.py`](../packages/hla-verification/src/hla/verification/scenario_support.py)

Why this matters:

- tests stay deterministic
- callback ownership remains obvious
- orchestration bugs show up as missing drains or missing barriers

## What "Callback Pumping" Means

In this repo, "callback pumping" means user code, scenario code, or a thin
helper explicitly asks the RTI to deliver queued callbacks.

In practice that means:

- a service call causes callback work to become pending
- the callback is stored in a queue or pending state
- progress becomes visible only after the scenario calls
  `evokeCallback(...)` or `evokeMultipleCallbacks(...)`

This is the opposite of assuming there is always a worker thread quietly
draining callback traffic in the background.

For the standard local proof lanes, callback pumping is deliberate because it:

- makes delivery boundaries easy to reason about
- keeps tests repeatable
- avoids hiding orchestration bugs behind timing luck

## 2010 Local Lane

The main local 2010 two-federate pattern is:

- create two ambassadors with `create_python_pair()`
- both ambassadors share one `InMemoryRTIEngine`
- one process drives both ambassadors

The shared-engine factory lives in
[`packages/hla-backend-python1516e/src/hla/backends/python1516e/factory.py`](../packages/hla-backend-python1516e/src/hla/backends/python1516e/factory.py).

The engine lives in
[`packages/hla-backend-python1516e/src/hla/backends/python1516e/engine.py`](../packages/hla-backend-python1516e/src/hla/backends/python1516e/engine.py).

Important implementation detail:

- `InMemoryRTIEngine` owns shared federation state
- it protects state changes with `threading.RLock`

That lock means the engine is thread-safe enough for coordinated access, but
the standard showcase pattern is still same-process and explicitly driven. The
repo is not claiming a high-concurrency distributed scheduler here.

## 2025 Local Lane

The local 2025 showcase lane creates separate ambassadors with
`create_rti_ambassador(backend="python1516_2025")`.

The key callback behavior is:

- each ambassador has an `_evoked_callback_queue`
- if the callback model is `HLA_EVOKED`, callbacks are queued
- `evokeMultipleCallbacks(...)` drains the queued callbacks

That queue behavior lives in:

- [`packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ambassador_core_surface_mixin.py`](../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ambassador_core_surface_mixin.py)
- [`packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/callback_runtime.py`](../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/callback_runtime.py)

The backend also exposes `enable_asynchronous_delivery()` and
`disable_asynchronous_delivery()`, but that is not the same thing as the repo
spawning a general-purpose worker thread for you. In the local showcase lane,
we still drive scenario progress explicitly through callback invocation points.

## What "Multi-Threading" Means Here

There are three different things people often collapse together:

1. multiple federates
2. multiple OS threads
3. asynchronous callback delivery

They are not the same.

In this repo's local showcase and verification lanes:

- multiple federates are common
- multiple OS threads are not the default orchestration story
- asynchronous callback delivery exists as an RTI behavior switch, but the
  standard proofs still prefer explicit callback pumping

There are really four execution shapes to keep separate:

1. multiple federates in one process
2. multiple federates across multiple processes
3. multiple threads inside the RTI host or transport server
4. asynchronous callback delivery semantics

The repo uses all four ideas in different places, but not as one single model.

Examples:

- local `python1516e` showcase:
  usually one process, two ambassadors, one shared in-memory engine
- local `python1516_2025` showcase:
  usually one process, multiple ambassadors, per-ambassador callback queues
- hosted `grpc` and `rest` routes:
  transport servers may use threads, but the Python-facing callback contract is
  still explicit polling
- JPype and Py4J:
  the bridge topology changes, but the orchestrated RTI-facing behavior can
  still remain explicit and callback-polled

If you want a federation that uses separate processes, remote transports, or a
real scheduling fabric, that is a different route from the local in-process
showcase lane.

For those boundaries, read:

- [`docs/networked_rti_python.md`](networked_rti_python.md)
- [`docs/extending_ambassador_transports.md`](extending_ambassador_transports.md)

## SISO Runtime Showcase Orchestration

The current executable SISO showcase lives in
[`packages/hla-verification/src/hla/verification/repo_internal/verification/siso_runtime_showcase.py`](../packages/hla-verification/src/hla/verification/repo_internal/verification/siso_runtime_showcase.py).

It now demonstrates the orchestration pattern as a matrix:

- families: `Link 16`, `RPR`, `Space`
- editions: `2010`, `2025`
- topologies: `micro-2`, `squad-5`, `constellation-10`

Representative rows:

- `link16-rpr2-integrated-2010-micro-2`
  - one sender, one observer/listener, shared local orchestration
- `rpr-runtime-2025-squad-5`
  - one bridge owner, multiple shooters, multiple observers
- `space-fom-core-2025-constellation-10`
  - one frame authority, multiple entity publishers, multiple observers

That file is useful because it shows the orchestration in a copyable form
without hiding it behind too much framework code.

The runtime showcase now also promotes the final observer into an explicit
listener federate artifact lane. That listener still uses the same startup
sync-point and explicit callback-pumping model described here; it is not a
hidden background monitor.

## Where Parallelism Exists Today

The short answer is: less in the local proof lanes than people often assume.

Current practical model:

- local 2010 proof lane:
  shared in-memory federation state with lock-protected mutation
- local 2025 proof lane:
  separate ambassador shells with queued callback delivery
- hosted transport lanes:
  server-side threading may exist in transport implementations
- external vendor or bridge routes:
  separate processes may exist because the route itself introduces that
  boundary

What is usually not happening in the standard examples:

- a pool of worker threads per federate
- automatic callback drain threads for every local ambassador
- aggressive parallel stepping of all federates for throughput

That is why the examples are easy to follow but not tuned for maximum
throughput.

## Performance Model

For the standard local proof lanes, runtime cost usually comes from one or more
of these:

1. frequent callback drain loops
2. small-grain "do one thing, then drain" orchestration
3. explicit synchronization barriers such as `ReadyToRun`
4. bridge or transport conversion overhead on non-direct routes
5. process boundaries on remote, hosted, or external-runtime routes

This means a slow scenario is not automatically proving "the RTI is slow".
Often it is proving that the scenario is using a very conservative correctness-
first orchestration style.

## Is This An RTI Limitation

Not by itself.

Some limits do come from RTI semantics:

- ordering rules
- time-management rules
- callback safety rules
- delivery visibility only after the route/runtime makes callbacks observable

But the dominant local-proof-lane limit in this repo is usually architectural
choice:

- explicit `HLA_EVOKED`
- deterministic bounded drain loops
- clarity-first scenario orchestration

That is intentional for verification. It should not be confused with a claim
that high-throughput execution is impossible.

## How To Make It More Performant

Use this order of operations.

### 1. Reduce Over-Pumping

Avoid draining after every tiny state change when the scenario does not require
that visibility boundary.

Prefer:

- publish several things
- subscribe several things
- register several instances
- send several updates
- then drain

### 2. Batch Work Between Visibility Boundaries

Think in terms of semantic checkpoints, not line-by-line callback delivery.

Good boundaries:

- after startup sync
- after object registration bursts
- after a burst of attribute updates
- after a burst of interactions
- after time-advance requests that should become externally visible

### 3. Keep Correctness Lanes And Throughput Lanes Separate

Use conservative explicit draining for:

- conformance tests
- debugging
- route parity work
- bridge adaptation proofs

Use a more throughput-oriented harness for:

- load experiments
- batch update exercises
- transport sizing work
- vendor runtime comparison

### 4. Change Topology Only When Needed

Move beyond the default in-process proof lane only when there is a concrete
reason.

Typical reasons:

- JVM or vendor process isolation
- remote deployment
- alternate transport requirements
- scaling experiments that need separate host or process boundaries

Changing topology adds its own costs:

- serialization
- transport latency
- process lifecycle management
- more moving parts during diagnosis

### 5. Be Deliberate About Callback Model Choice

If a route supports a less explicit callback style, treat that as an execution
policy choice, not a default assumption.

For this repo, the normal recommendation remains:

- use explicit callback pumping for proof and debugging
- widen delivery behavior only when the scenario has a demonstrated need

## Recommended Performance Lanes

Use this decision table.

- proof, debugging, and easy reasoning:
  local in-process lane with explicit callback pumping
- bridge adaptation work:
  JPype first, Py4J when process separation matters
- transport extension work:
  hosted `grpc` or `rest` lane with explicit callback polling preserved
- scaling or throughput experiments:
  separate harness, larger batches, fewer visibility barriers, and topology
  chosen for the specific measurement

## Copyable Recipe

For a small federation, use this pattern:

1. create the RTIs and federate ambassadors
2. call `connect_create_join(...)` for each participant
3. call `synchronize_ready_to_run(...)`
4. set up publication and subscription
5. register instances and send traffic
6. call `drain_callbacks(...)` after each meaningful lifecycle phase
7. resign and disconnect explicitly

Practical rule:

- drain after anything that should cause visible remote state
- add a sync point when "everyone must be ready before traffic starts" is a
  correctness requirement

## When To Add More Orchestration

You should add a stronger orchestration layer only when the scenario needs it.

Add more structure when you need:

- late joiners with explicit role handoff
- save/restore windows
- time-managed progression barriers
- hosted or remote RTI routes
- separate-process federates with external lifecycle control

Do not add more orchestration just because there are two federates. The current
repo norm is to keep the proof lane simple until a scenario proves it needs more.
