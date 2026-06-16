# v0.11 Compliance Slice: MOM service actions, service reports, time coordination, save/restore, and DDM/TSO

This slice continues the pure-Python RTI toward HLA 1516.1-2010 conformance while keeping the Java JPype/Py4J adapter path backend-neutral.

## Scope

| Work item | Primary section anchors | Implemented in v0.11 |
|---|---:|---|
| MOM adjust/service-action semantics | IEEE 1516.1-2010 §11.4 and §11.5 | `HLAadjust.HLAsetSwitches`, `HLAadjust.HLAsetTiming`, `HLAadjust.HLAmodifyAttributeState`, and a first set of `HLAservice.*` action interactions now drive the same underlying RTI service methods used by normal federates. |
| Service-report file behavior | IEEE 1516.1-2010 §11.5 and §11.5.2 | Added a structured JSONL service-report sink and MOM-controlled per-federate report files with an initial record plus service records containing section anchors, arguments, return values, success state, and exception name. |
| Dedicated time-management module | IEEE 1516.1-2010 §8.1.4-§8.1.6 and §8.8-§8.13 | Moved grant-decision, GALT, LITS, LBTS, eligible-message, FQR, and scheduled-save time logic into `hla.rti1516e.time_management`. |
| Save/restore and temporal state coordination | IEEE 1516.1-2010 §4.16-§4.26 and §8 | Timed federation save now waits for constrained federates to reach the save time, snapshots logical-time state and object state, cancels pending time advances during restore, and reinstates saved time/object state after successful restore. |
| DDM plus TSO interaction coverage | IEEE 1516.1-2010 §9.2-§9.13 and §6.12 | Region subscriptions and update/send regions now participate in filtering before RO/TSO delivery. Region-filtered TSO interactions are released by time-advance services in timestamp order. |
| Fuller distributed GALT/LITS algorithm | IEEE 1516.1-2010 §8.16 and §8.18 | GALT now uses other regulating federates' lower-bound-on-timestamp contributions, including pending advance requests plus lookahead. LITS combines GALT with the recipient's queued incoming TSO messages. |

## MOM/service-action details

The RTI now treats MOM interactions as RTI-consumed control messages when their class name is in `HLAinteractionRoot.HLAmanager`:

- `HLArequest.*` still produces matching `HLAreport.*` interactions.
- `HLAadjust.HLAsetSwitches` updates the target federate's MOM switches, including service reporting, exception reporting, region-designator conveyance, producing-federate conveyance, and service-report-file output.
- `HLAadjust.HLAsetTiming` records the target MOM reporting period.
- `HLAadjust.HLAmodifyAttributeState` records per-MOM-attribute reporting state.
- `HLAservice.*` can drive service methods such as time-constrained enable/disable, time-regulation enable/disable, time-advance requests, asynchronous-delivery toggles, lookahead changes, synchronization-point-achieved, save complete, and restore complete.

The §11.5 conflict rule is now represented in both directions:

1. A parameter-specific request to enable MOM service reporting is rejected when the federate is already subscribed to `HLAreportServiceInvocation`; the RTI reports `FederateServiceInvocationsAreBeingReportedViaMOM` through `HLAreportMOMexception`.
2. A federate with service reporting already enabled cannot subscribe to `HLAreportServiceInvocation` through the normal `Subscribe Interaction Class` service.

A compatibility shortcut remains for older smoke tests: an empty `HLAsetSwitches` parameter set enables the observable development switches. Parameter-specific use follows the stricter MOM rule above.

## Service-report files

There are now two report-file paths:

1. `PythonRTIConfig.service_report_file`: a backend-wide audit sink using `hla.rti1516e.service_reporting.ServiceReportSink` and `ServiceReportRecord`.
2. MOM-controlled per-federate files: enabled by `HLAsendServiceReportsToFile` or by the development shortcut above.

Per-federate files contain:

- `ServiceReportInitialRecord` with federation, federate, MIM/FOM, and connect metadata.
- `ServiceReportRecord` entries for each RTI service invocation with section label, timestamp, success flag, exception name, arguments, and return value summary.

The file format is JSON Lines to keep it simple to append, test, and feed into later conformance tooling.

## Time management module

`hla.rti1516e.time_management` is the new home for distributed time logic:

- `compute_galt(...)` implements the current GALT calculation using regulating federates' lower-bound-on-timestamp contributions.
- `compute_lits(...)` combines GALT and queued incoming TSO timestamps.
- `compute_grant_decision(...)` handles TAR, TARA, NMR, NMRA, and FQR boundary rules.
- `deliverable_messages_for_request(...)` selects TSO messages to release for a pending advance request.
- `scheduled_save_time_reached(...)` captures the scheduled-save/time coordination rule used by the backend.

The pure-Python RTI still retains federation/object plumbing in `python_rti.py`, but the time algorithm is now isolated enough to test directly in later compliance slices.

## Save/restore coordination

The save/restore path now coordinates with temporal state:

- `Request Federation Save(label, time)` stores a scheduled save and waits until constrained federates reach the save time.
- Starting the save invokes `initiateFederateSave` for the federation.
- Successful save completion stores time state, lookahead, regulation/constrained state, asynchronous-delivery state, zero-lookahead restriction state, and object-state snapshots.
- `Request Federation Restore(label)` cancels pending advances and invokes restore callbacks.
- Successful restore reinstates the stored time state and object snapshot for the saved label.

## DDM and TSO coverage

DDM region state now affects callback delivery:

- `Create Region`, `Set Range Bounds`, and `Commit Region Modifications` maintain region/dimension bounds.
- `Subscribe Object Class Attributes With Regions` stores region filters per object class and attribute.
- `Register Object Instance With Regions` and `Associate Regions For Updates` store producing-region state for later reflections.
- `Subscribe Interaction Class With Regions` stores region filters per interaction class.
- `Send Interaction With Regions` applies overlap filtering before enqueueing RO or TSO delivery.
- TSO messages that pass DDM filtering are queued and released by NMR/NMRA/TAR/TARA/FQR according to the time-management module.

## Validation added

`tests/test_compliance_slice_v011.py` covers:

- global and MOM-controlled service-report JSONL files;
- `HLAsetSwitches` service-reporting conflict handling;
- a MOM `HLAservice` action driving `Enable Time Constrained`;
- scheduled save delayed until logical time and restore reinstating time state;
- DDM region filtering before timestamp-order interaction delivery;
- GALT based on pending regulator LBTS rather than only current logical time.

Current validation result: `60 passed, 2 skipped`.

The skipped tests are optional real JPype/Py4J bridge tests because this runtime does not include those bridge packages or a vendor RTI.
