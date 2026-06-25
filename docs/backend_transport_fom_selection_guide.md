# Backend, Transport, and FOM Selection Guide

Use this page when the real question is:

"What backend should I use, what transport should I use, and what FOM should I
start with?"

This is the shortest combined routing guide for those three decisions.

## One-Page Summary

Pick in this order:

1. backend/runtime lane
2. transport or bridge shape
3. FOM family and load mode

Keep the decisions separate:

- backend decides RTI semantics
- transport decides how you reach the RTI
- FOM decides object, interaction, and datatype shape

Do not choose a transport because you need different RTI semantics.
Do not choose a FOM because you think it changes transport behavior.

## Quick Decision Table

| If you want | Backend | Transport | FOM starting point |
| --- | --- | --- | --- |
| fastest local 2010 proof lane | `python1516e` | direct in-process | `DemoFOMmodule.xml` or `VendorSmokeFOM.xml` |
| fastest local 2025 proof lane | `python1516_2025` | direct in-process | Target/Radar or Proto2025 example FOMs |
| hosted 2010 route | `python1516e` or `certi` | `grpc` or `rest` | `VendorSmokeFOM.xml` first, then scenario-owned FOMs |
| hosted 2025 route | `python1516_2025` | bounded FedPro `grpc` | Target/Radar or tracked 2025 example FOMs |
| Java RTI in-process | Java route via JPype | object bridge, not network transport | same FOMs you would use on the equivalent edition |
| Java RTI separate process | Java route via Py4J | gateway bridge, not network transport | same FOMs you would use on the equivalent edition |
| slightly different vendor gRPC | keep backend semantics fixed | `vendor-grpc` or `quirky-vendor-grpc` style transport variant | same FOMs as the equivalent direct or hosted route |

## Step 1: Choose The Backend

Use these default answers.

### 2010

- use `python1516e` for the direct Python RTI lane
- use `certi` when you are intentionally exercising the transport-driven helper
  route or native CERTI path

### 2025

- use `python1516_2025` for the main executable Python 2025 RTI lane
- do not treat shim wording as the primary runtime lane

### Java

- use JPype when you want the clearest in-process Java wrapping path
- use Py4J when you need JVM process separation

Read next for backend choice:

- [rti_factory_reading_map.md](rti_factory_reading_map.md)
- [backend_route_inventory.md](backend_route_inventory.md)

## Step 2: Choose The Transport Or Bridge

Use this rule:

- direct in-process when you want the simplest proof lane
- `grpc` or `rest` when you want a hosted route
- JPype or Py4J when the RTI implementation is Java-owned
- transport variants when the wire is vendor-specific but the semantics are the
  same

### Direct In-Process

Choose this when:

- you are editing RTI semantics
- you want the shortest debug path
- you want the fastest local loop

### Hosted `grpc` / `rest`

Choose this when:

- you need a separate process boundary
- you are proving hosted route parity
- you need transport-specific testing or deployment behavior

### Transport Variants

Choose this when:

- the RTI speaks a different wire language
- the semantics are still the same
- only the envelope, service naming, metadata, or callback-poll RPC naming
  changed

Read next for transport choice:

- [networked_rti_python.md](networked_rti_python.md)
- [extending_ambassador_transports.md](extending_ambassador_transports.md)
- [transport_extension_playbook.md](transport_extension_playbook.md)

## Step 3: Choose The FOM

Choose the smallest FOM that proves the question you actually have.

### Small Smoke FOMs

Use these first when you are proving a route, startup, callback path, or
basic object/interaction exchange:

- `VendorSmokeFOM.xml`
- `DemoFOMmodule.xml`

### Scenario-Owned FOMs

Use these when the scenario itself matters:

- Target/Radar for reusable scenario and time-management proof
- Proto2025 example FOMs for 2025-specific example routes

### Imported Baselines

Use these when the question is about FOM family coverage, parser/load order, or
corpus validation rather than a small runnable federation:

- RPR families
- Space FOM
- NETN baseline
- optional local SISO corpora

Read next for FOM choice:

- [fom_reading_map.md](fom_reading_map.md)
- [fom-examples/fom_inventory.md](fom-examples/fom_inventory.md)
- [fom_validate.md](fom_validate.md)

## Copyable Starting Recipes

### Recipe 1: Small Local 2010 Federation

- backend: `python1516e`
- transport: direct
- FOM: `VendorSmokeFOM.xml`

Open:

1. [first_run.md](first_run.md)
2. [two_federate_quickstart.md](two_federate_quickstart.md)
3. [federation_orchestration.md](federation_orchestration.md)

### Recipe 2: Small Local 2025 Federation

- backend: `python1516_2025`
- transport: direct
- FOM: Target/Radar or Proto2025 example FOM

Open:

1. [python_rti_backend.md](python_rti_backend.md)
2. [networked_rti_python.md](networked_rti_python.md) only if you later need
   hosted `grpc`
3. [fom_reading_map.md](fom_reading_map.md)

### Recipe 3: Hosted Route Proof

- backend: same runtime semantics as the direct lane
- transport: `grpc` or `rest`
- FOM: start with `VendorSmokeFOM.xml`, then move to scenario-owned FOMs

Open:

1. [networked_rti_python.md](networked_rti_python.md)
2. [transport_extension_playbook.md](transport_extension_playbook.md)
3. [federation_orchestration.md](federation_orchestration.md)

### Recipe 4: Slightly Different Vendor gRPC

- backend: keep the equivalent direct or hosted backend lane
- transport: `vendor-grpc` or `quirky-vendor-grpc` pattern
- FOM: keep the same FOM you would use on the equivalent direct route

Open:

1. [transport_extension_playbook.md](transport_extension_playbook.md)
2. [../packages/hla-transport-grpc/README.md](../packages/hla-transport-grpc/README.md)
3. [fom_reading_map.md](fom_reading_map.md)

## What Is Still Weak

The repo still needs a stronger focused guide for "create a new federate and
owning FOM package" because
[create_federate_and_fom.md](create_federate_and_fom.md) is still only a
placeholder.

So today:

- backend and transport choice are well covered
- FOM inventory and validation are well covered
- new federate + new FOM authoring workflow is not yet documented as strongly
  as it should be

## Read Next

1. [rti_factory_reading_map.md](rti_factory_reading_map.md)
2. [transport_extension_playbook.md](transport_extension_playbook.md)
3. [fom_reading_map.md](fom_reading_map.md)
