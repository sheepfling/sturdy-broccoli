# v0.10 MOM/MIM and time-management compliance slice

This release continues the pure-Python RTI toward IEEE HLA 1516.1-2010 conformance, focused on the **Management Object Model / standard MIM** and **time-management ordering**. It remains a development/reference RTI, not a certified RTI.

## Section traceability

| Area | Section anchor |
|---|---|
| MOM object classes | IEEE 1516.1-2010 §11.2 |
| MOM interaction classes | IEEE 1516.1-2010 §11.3 |
| Normal RTI MOM administration | IEEE 1516.1-2010 §11.4.1 |
| Service reporting | IEEE 1516.1-2010 §11.5 |
| MOM OMT tables | IEEE 1516.1-2010 §11.6 |
| Standard MIM | IEEE 1516.1-2010 Annex G |
| Time overview, logical time, regulating/constrained state, and message ordering | IEEE 1516.1-2010 §8.1.1-§8.1.6 |
| Enable/disable time regulation/constrained | IEEE 1516.1-2010 §8.2-§8.7 |
| Time advance services and grants | IEEE 1516.1-2010 §8.8-§8.13 |
| Asynchronous delivery | IEEE 1516.1-2010 §8.14-§8.15 |
| Query GALT, Query Logical Time, Query LITS, Query Lookahead | IEEE 1516.1-2010 §8.16-§8.20 |
| Retraction and order-type changes | IEEE 1516.1-2010 §8.21-§8.24 |
| OMT/FOM parsing and merging | IEEE 1516.2-2010 §4, §7, Annex D/E |

## MIM loading

The package now bundles and parses `HLAstandardMIM.xml` from the uploaded IEEE 1516.1-2010 downloads. `createFederationExecution` installs the standard MIM before user FOM modules, then merges the catalog into the local FDD. The parsed bundled MIM currently exposes the standard MOM/MIM object classes, interaction classes, parameters, attributes, and dimensions discovered from the XML.

The active FDD summary is still accessible through the Python convenience method:

```python
summary = rti.backend.current_fom_summary()
```

MOM and MIM names are also available through normal HLA handle services:

```python
federate_class = rti.get_object_class_handle("HLAobjectRoot.HLAmanager.HLAfederate")
name_attr = rti.get_attribute_handle(federate_class, "HLAfederateName")

request = rti.get_interaction_class_handle(
    "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"
)
report = rti.get_interaction_class_handle(
    "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"
)
```

## MOM object exposure

The RTI now registers RTI-owned local MOM object instances for the federation and each joined federate:

- `HLAobjectRoot.HLAmanager.HLAfederation`
- `HLAobjectRoot.HLAmanager.HLAfederate`

When a federate subscribes to those classes, the Python RTI can discover the MOM objects and reflect live attributes on `requestAttributeValueUpdate`. Attributes are refreshed from runtime state, including federation name, federates in federation, FOM/MIM designators, logical-time implementation, time constrained/regulating switches, logical time, lookahead, GALT/LITS, queue lengths, advisory switches, service-reporting switch, and basic counters.

## MOM interaction exposure

MOM request interactions are intercepted by the RTI rather than treated as ordinary federate-to-federate interactions. v0.10 routes common requests to reports for:

- MIM data
- FOM module data
- synchronization point listings and status
- object-class and interaction publication/subscription state
- sent/received/update/reflection counters
- object-instance information

For request/report pairs not yet specialized, the RTI still exposes the report interaction and populates known parameters with stable diagnostic values. That keeps the MOM surface discoverable while detailed parameter decoding continues to mature.

`HLAadjust.HLAsetSwitches` toggles visible management switches in the local RTI. When service reporting is on, RTI service calls emit `HLAreportServiceInvocation` reports to subscribed federates.

## Time-management ordering

The local RTI now uses queued timestamp-order delivery for timestamped update, interaction, and delete services when the sender is time-regulating and the receiver is time-constrained. Receive-order messages still deliver immediately or through the normal callback queue.

Implemented local semantics include:

- TSO queue ordering by logical time and stable send sequence.
- Timestamp lookahead validation for time-regulating senders.
- `timeAdvanceRequest`, `timeAdvanceRequestAvailable`, `nextMessageRequest`, `nextMessageRequestAvailable`, and `flushQueueRequest` grant processing.
- `timeAdvanceGrant` delivery only after eligible queued TSO messages are delivered.
- `queryGALT` and `queryLITS` values derived from regulating federates and queued TSO messages.
- GALT grant gating enabled by default in `PythonRTIConfig`.
- `retract` support for queued TSO messages before delivery.
- Basic `changeAttributeOrderType` and `changeInteractionOrderType` storage for preferred timestamp/receive ordering.

Example:

```python
tf = rti.get_time_factory()
rti.enable_time_regulation(tf.make_interval(1.0))
receiver.enable_time_constrained()

sender.update_attribute_values(obj, values, b"t3", tf.make_time(3.0))
receiver.next_message_request(tf.make_time(5.0))
```

## Java translation compatibility

These MOM and time-management improvements remain behind the backend-neutral Python ambassador surface. Java RTI adapters still normalize Java-created handles, sets, maps, callbacks, and logical-time objects through the same conversion layer; Python federate code does not need to branch on pure-Python vs JPype/Py4J RTI.

## Validation

Current validation:

```text
54 passed, 2 skipped
```

The skipped tests are optional real JPype/Py4J bridge tests because this runtime does not include bridge packages or a vendor RTI.

New tests added in this slice:

- `tests/test_mom_mim_time_management_v010.py`
- Existing focused tests retained in `tests/test_mom_mim_time_v10.py`

## Known gaps

This pass is intentionally practical rather than claiming final certification:

- Not every Annex G MOM report has fully decoded, semantically complete payloads yet.
- Cross-federate MOM service interactions are accepted; only a conservative subset is routed to real RTI service calls.
- Distributed LBTS/GALT algorithms are approximated for a single-process local RTI.
- DDM-region filtering is not yet fully integrated with TSO delivery and MOM region reporting.
- Save/restore MOM attributes are stateful but not backed by persistent snapshots.
