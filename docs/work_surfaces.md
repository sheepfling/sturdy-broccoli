# Work Surfaces

Use this page when the question is:

"What kind of work am I actually doing here?"

The repo is easier to navigate when you start from one of three work surfaces:

1. `Backend` -> route names, backend swaps, JPype, Py4J, vendor lanes
2. `Transport` -> hosted routes, `grpc`, `rest`, callback polling, wire formats
3. `FOM` -> validation, baselines, UI/workbench, authoring

## One-Page Summary

| If the question is about | Start here | Then read |
| --- | --- | --- |
| `Backend` -> backend swaps, route names, JPype, Py4J, vendor lanes, or wrapping a Java RTI | [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md) | [`java_bridge_minimal_protocol_recipe.md`](java_bridge_minimal_protocol_recipe.md), [`java_bridge_wrapping_guide.md`](java_bridge_wrapping_guide.md), [`java_bridge_overload_resolution.md`](java_bridge_overload_resolution.md), [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md) |
| `Transport` -> `grpc`, `rest`, hosted routes, wire formats, callback polling, or a slightly different vendor protocol | [`extending_ambassador_transports.md`](extending_ambassador_transports.md) | [`transport_extension_playbook.md`](transport_extension_playbook.md), [`networked_rti_python.md`](networked_rti_python.md) |
| `FOM` -> FOM families, validation, workbench/UI, baselines, or authoring | [`fom_tooling_front_door.md`](fom_tooling_front_door.md) | [`fom_reading_map.md`](fom_reading_map.md), [`fom_validate.md`](fom_validate.md), [`fom_workbench.md`](fom_workbench.md) |

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
3. [`java_bridge_overload_resolution.md`](java_bridge_overload_resolution.md)
4. [`java_rti_adaptation_architecture.md`](java_rti_adaptation_architecture.md)

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

## Simple Decision Rule

If the main noun in the problem is:

- route, backend, JPype, Py4J, vendor, or edition:
  use `Backend`
- `grpc`, `rest`, callback pumping, protocol, envelope, or hosted route:
  use `Transport`
- FOM, OMT, module, validation, workbench, or baseline:
  use `FOM`

## Read Next

1. [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)
2. [`extending_ambassador_transports.md`](extending_ambassador_transports.md)
3. [`fom_tooling_front_door.md`](fom_tooling_front_door.md)
