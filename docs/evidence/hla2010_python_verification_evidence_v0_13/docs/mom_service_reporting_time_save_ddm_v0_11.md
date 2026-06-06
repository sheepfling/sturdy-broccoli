# v0.11 compliance slice: MOM, service-reporting, time, save/restore, and DDM

This pass advances the pure-Python RTI from a smoke-test/reference RTI toward a more conformance-oriented implementation.  It is still not a certified RTI, but the behavior is now organized around the relevant IEEE 1516.1 section anchors and is covered by executable tests.

## 1. MOM adjust and service-action semantics

Section anchors: IEEE 1516.1-2010 §11.3-§11.5, with service action links back to the invoked RTI services.

The Python RTI now treats MOM management interactions as first-class control messages instead of only diagnostic events.  The federate-level `HLAadjust.HLAsetSwitches` path supports switch changes for:

- convey region designator sets;
- convey producing federate;
- service reporting;
- exception reporting;
- send service reports to file.

The federate-level `HLAadjust.HLAsetTiming` path updates MOM reporting period state.  The federation-level adjust path updates federation MOM auto-provide behavior.

MOM service-action interactions now dispatch to normal RTI service handlers where possible, including time management, asynchronous-delivery toggles, synchronization-point achievement, and save/restore completion.  This keeps service-action behavior observable through the same state transitions and callbacks as direct RTIambassador calls.

The service-reporting conflict rule is represented: a federate already subscribed to the service-invocation report stream cannot enable direct service reporting through `HLAserviceReporting=True`; the RTI reports a MOM exception.  Conversely, a federate already using direct service reporting cannot subscribe to the service-invocation report stream.

## 2. Service-report file behavior

Section anchors: IEEE 1516.1-2010 §11.5.1-§11.5.2.

A new `hla2010.service_reporting` module provides the shared JSON-safe service-report file sink.  The pure-Python RTI now supports two sinks:

- a global audit sink configured by `PythonRTIConfig.service_report_file`; and
- per-federate service-report files enabled by the MOM `HLAsendServiceReportsToFile` switch or by `service_report_file_on_by_default`.

Per-federate files begin with a `ServiceReportInitialRecord` containing connection, federation, FDD/MIM/FOM, and federate identity data.  Service call records include a serial number, service name, success indicator, exception name, normalized arguments, returned values, UTC timestamp, and a section reference such as `1516.1-2010 §8.17` for `queryLogicalTime`.

Service-report file output is an audit sink, not a substitute for normal MOM visibility in this development RTI: when a federate is also subscribed to the service-invocation report stream, it can still receive the corresponding MOM report.  The MOM `HLAreportServiceFile` attribute is refreshed with the implementation-selected path.

## 3. Dedicated time-management module

Section anchors: IEEE 1516.1-2010 §8.1, §8.8-§8.21.

The time logic is now consolidated in `hla2010.time_management`.  The backend still owns federation state and callback delivery, but the temporal calculations are isolated behind explicit functions:

- `compute_galt` calculates the current GALT bound from the temporal state of other regulating federates, including pending advance requests and lookahead.
- `compute_lits` combines GALT and queued TSO-message timestamps.
- `compute_grant_decision` applies strict versus inclusive grant boundaries for TAR/NMR versus TARA/NMRA/FQR.
- `eligible_tso_messages`, `grant_time_for_request`, and compatibility wrappers keep the backend and tests small while the algorithm evolves.

The Non-Regulated-Grant behavior is represented through `PythonRTIConfig.non_regulated_grant_enabled`: when there are no applicable regulators, undefined GALT can either permit unregulated advancement or hold the constrained federate at its current logical time.

## 4. Save/restore and time-state coordination

Section anchors: IEEE 1516.1-2010 §4.19-§4.31 and §8.

Scheduled federation save now coordinates with time state.  If a save timestamp is supplied, the RTI waits until time-constrained joined federates have advanced far enough to be eligible before it invokes `initiateFederateSave`.  This gives the save path the same kind of temporal boundary used by timestamp-order message delivery.

The Python RTI snapshots time state and object state when the save completes.  Federation restore reinstates the saved logical time, lookahead, regulating/constrained flags, queued state, and object snapshot, and it clears in-progress advance flags so the restored federation can continue from the saved boundary.

## 5. DDM plus timestamp-order coverage

Section anchors: IEEE 1516.1-2010 §9 and §8.

Region-overlap checks now participate in both receive-order and timestamp-order paths.  Region filtering is applied before a TSO interaction is queued for a time-constrained receiver, so a non-overlapping region message never becomes a future deliverable TSO event for that receiver.

The object path tracks update regions per object/attribute and compares those regions against the subscribing federate's attribute-region subscriptions before reflecting values.  The interaction path similarly uses subscribed interaction regions before queueing or delivering timestamped interactions.

## 6. Fuller GALT/LITS algorithm

Section anchors: IEEE 1516.1-2010 §8.1.6.

The previous implementation treated GALT conservatively and mostly from current times.  v0.11 uses a distributed-time approximation that considers:

- other regulating federates only;
- each regulator's current logical time;
- each regulator's pending requested time, when time advancing;
- each regulator's lookahead; and
- queued incoming TSO messages when computing LITS.

This supports the important distinction that a pending regulating federate can raise the safe lower-bound contribution seen by another constrained federate.  The result is still intentionally local-process and deterministic; a production RTI would need additional distributed-fault and transport coordination.

## Executable evidence

The v0.11 tests cover:

- service-report global and per-federate files;
- section-aware service-report records;
- MOM service-reporting conflict behavior;
- MOM service actions driving time management;
- scheduled save and restore of time state;
- DDM region filtering before timestamp-order interaction queueing; and
- GALT/LITS calculations based on pending regulator LBTS.

Current validation: `60 passed, 2 skipped`.
