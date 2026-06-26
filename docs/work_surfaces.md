# Work Surfaces

Use this page when the question is:

"What kind of work am I actually doing here?"

The repo is easier to navigate when you start from one of three work surfaces:

1. `Backend` -> route names, backend swaps, JPype, Py4J, vendor lanes
2. `Transport` -> hosted routes, `grpc`, `rest`, callback polling, wire formats
3. `FOM` -> validation, baselines, UI/workbench, authoring

Two other top-level reading surfaces sit across those engineering lanes:

4. `Testing` -> repo-green entrypoints, shard selection, focused reruns, and failure diagnosis
5. `Requirements` -> bounded claims, proof notes, traceability, and requirement-facing evidence packets
6. `Requirements exports | status` -> spreadsheet handoff packets and honest closeout audit surfaces

## One-Page Summary

| If the question is about | Start here | Then read |
| --- | --- | --- |
| `Backend` -> backend swaps, route names, JPype, Py4J, vendor lanes, or wrapping a Java RTI | [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md) | [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md), [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md), [`java_bridge_encoding_and_bytes.md`](java_bridge_encoding_and_bytes.md), [`java_bridge_overload_resolution.md`](java_bridge_overload_resolution.md), [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md) |
| `Transport` -> `grpc`, `rest`, hosted routes, wire formats, callback polling, or a slightly different vendor protocol | [`extending_ambassador_transports.md`](extending_ambassador_transports.md) | [`transport_extension_playbook.md`](transport_extension_playbook.md), [`networked_rti_python.md`](networked_rti_python.md) |
| `FOM` -> FOM families, validation, workbench/UI, baselines, or authoring | [`fom_tooling_front_door.md`](fom_tooling_front_door.md) | [`fom_reading_map.md`](fom_reading_map.md), [`fom_validate.md`](fom_validate.md), [`fom_workbench.md`](fom_workbench.md) |
| `Testing` -> repo green, lane choice, shard reruns, or junior failure diagnosis | [`repo_green_quickstart.md`](repo_green_quickstart.md) | [`test_surface.md`](test_surface.md), [`local_verification_commands.md`](local_verification_commands.md), [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md) |
| `Requirements` -> claims, proofs, traceability, or requirement-facing evidence | [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md) or [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md) | [`verification/README.md`](verification/README.md), [`spec_reading_map.md`](spec_reading_map.md), [`requirements_trace_one_method.md`](requirements_trace_one_method.md) |
| `Requirements exports | status` -> boss-facing spreadsheets, closeout truth, or remaining bucket audit | [`verification/requirement_compliance_exports.md`](verification/requirement_compliance_exports.md) or [`plans/requirements_completion_audit.md`](plans/requirements_completion_audit.md) | [`plans/requirements_remaining_closure.md`](plans/requirements_remaining_closure.md), [`spec_reading_map.md`](spec_reading_map.md) |

## Surface 1: Backends And Route Wrapping

Use this when the question is:

- which backend or route name should I use?
- how do I swap between `python1516e`, `python1516_2025`, `pitch-jpype`, `pitch-py4j`, or `certi`?
- how do I minimally wrap a Java RTI?
- where do JPype and Py4J fit?

Start here:

- [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)

Read these next for Java route work:

1. [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md)
2. [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md)
3. [`java_bridge_encoding_and_bytes.md`](java_bridge_encoding_and_bytes.md)
4. [`java_bridge_overload_resolution.md`](java_bridge_overload_resolution.md)
5. [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md)

Useful follow-ons:

- [`backend_route_inventory.md`](backend_route_inventory.md)
- [`backend_capability_matrix.md`](backend_capability_matrix.md)
- [`rti_factory_reading_map.md`](rti_factory_reading_map.md)
- [`pitch_hla4_native_investigation.md`](pitch_hla4_native_investigation.md)

Practical rule:

- JPype is the primary in-process Java wrapping path
- Py4J is the process-separated Java wrapping path
- both should preserve the same normalized Python-facing ambassador contract

## Surface 2: Transport Options

Use this when the question is:

- should this be direct, hosted `grpc`, or hosted `rest`?
- where does callback polling live?
- how do I adapt a slightly different `grpc` protocol?
- how do I add a new wire protocol without changing RTI semantics?

Start here:

- [`extending_ambassador_transports.md`](extending_ambassador_transports.md)

Then read:

1. [`transport_extension_playbook.md`](transport_extension_playbook.md)
2. [`networked_rti_python.md`](networked_rti_python.md)

Useful follow-ons:

- [`backend_capability_matrix.md`](backend_capability_matrix.md)
- [`package_layout.md`](package_layout.md)

Practical rule:

- transport changes should change connection or envelope mechanics
- transport changes should not invent a second RTI semantic layer

## Surface 3: FOM And Tooling

Use this when the question is:

- which FOM should I start from?
- how do I inspect or validate a FOM?
- where is the workbench or UI path?
- how do I wire a FOM into a federate or scenario?

Start here:

- [`fom_tooling_front_door.md`](fom_tooling_front_door.md)

Then branch by job:

1. inventory and lookup:
   [`fom_reading_map.md`](fom_reading_map.md)
2. validation:
   [`fom_validate.md`](fom_validate.md)
3. merged inspection and UI:
   [`fom_workbench.md`](fom_workbench.md)
4. authoring and wiring:
   [`create_federate_and_fom.md`](create_federate_and_fom.md)

Use this when backend, transport, and FOM must be chosen together:

- [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)

## Surface 4: Testing

Use this when the question is:

- what should I run first?
- how do I get repo green?
- which shard should I rerun after a failure?
- where is the junior-friendly diagnosis path?

Start here:

- [`repo_green_quickstart.md`](repo_green_quickstart.md)

Then read:

1. [`test_surface.md`](test_surface.md)
2. [`local_verification_commands.md`](local_verification_commands.md)
3. [`junior_test_diagnosis_runbook.md`](junior_test_diagnosis_runbook.md)

Practical rule:

- treat testing as an operator work surface, not just a pile of pytest selectors
- use shards as the canonical runnable ownership units
- use views only as overlapping analysis or restart cuts
- do not let a view replace shard ownership or requirement status ownership

## Surface 5: Requirements And Proof

Use this when the question is:

- what does the repo claim?
- what is bounded versus out of scope?
- where is the proof for a capability family?
- which requirement-facing note or packet should I read first?

Start here:

- [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md) for the 2010 edition
- [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md) for the 2025 edition

Then read:

1. [`verification/README.md`](verification/README.md)
2. [`spec_reading_map.md`](spec_reading_map.md)
3. [`requirements_trace_one_method.md`](requirements_trace_one_method.md)

Practical rule:

- requirements docs explain claims and proof boundaries
- verification docs explain where executable or generated evidence lives
- backend resolution belongs in separate backend-specific columns or linked owner artifacts
- do not overload one status-like field to imply both canonical requirement disposition and backend support

## Surface 6: Requirements Exports And Honest Closeout

Use this when the question is:

- can I hand a manager a spreadsheet?
- what is the current honest answer to whether requirements closeout is done?
- where are the remaining buckets, shard owners, or view overlaps recorded?

Start here:

- [`verification/requirement_compliance_exports.md`](verification/requirement_compliance_exports.md) for CSV/XLSX handoff packets
- [`plans/requirements_completion_audit.md`](plans/requirements_completion_audit.md) for the current honest closeout answer

Then read:

1. [`plans/requirements_remaining_closure.md`](plans/requirements_remaining_closure.md)
2. [`spec_reading_map.md`](spec_reading_map.md)
3. [`test_surface.md`](test_surface.md)

Practical rule:

- spreadsheets are presentation surfaces, not canonical owner ledgers
- the audit and remaining-closure docs are the truth surfaces for whether the repo can honestly claim completion
- shard ownership should be named before broader views, finish-line packets, or matrix cuts

## Simple Decision Rule

If the main noun in the problem is:

- route, backend, JPype, Py4J, vendor, or edition:
  use `Backend`
- `grpc`, `rest`, callback pumping, protocol, envelope, or hosted route:
  use `Transport`
- FOM, OMT, module, validation, workbench, or baseline:
  use `FOM`
- repo green, shard, rerun, failure, or lane:
  use `Testing`
- requirement, claim, proof, bounded note, traceability, or evidence packet:
  use `Requirements`
- spreadsheet, compliance export, audit, remaining bucket, or closeout truth:
  use `Requirements exports | status`

## Read Next

1. [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)
2. [`extending_ambassador_transports.md`](extending_ambassador_transports.md)
3. [`fom_tooling_front_door.md`](fom_tooling_front_door.md)
4. [`repo_green_quickstart.md`](repo_green_quickstart.md)
5. [`requirements/ieee-1516-2010/README.md`](requirements/ieee-1516-2010/README.md)
6. [`requirements/ieee-1516-2025/README.md`](requirements/ieee-1516-2025/README.md)
7. [`verification/requirement_compliance_exports.md`](verification/requirement_compliance_exports.md)
8. [`plans/requirements_completion_audit.md`](plans/requirements_completion_audit.md)
