# Create a Federate and FOM

Use this page when the real task is:

"I need to add a small federate or scenario and choose or add the FOM that it
uses."

This is the shortest authoring workflow for:

- choosing an existing FOM first
- validating it before wiring code
- putting new code in the right package
- avoiding transport or backend confusion while doing FOM work

## One-Page Summary

Author in this order:

1. decide whether an existing FOM already fits
2. validate the FOM before writing scenario code
3. keep reusable FOM assets in an owning package, not under `examples/`
4. keep scenario wrappers thin and put reusable logic in package-owned helpers

Use the smallest possible FOM first:

- `VendorSmokeFOM.xml` for route and lifecycle proof
- `DemoFOMmodule.xml` for small 2010 round trips
- Target/Radar or Proto2025 FOMs when the scenario itself matters

## Step 1: Decide Whether You Need A New FOM

Do this before authoring XML.

Use an existing FOM when:

- you are proving backend or transport behavior
- you only need one object class or interaction
- the question is route plumbing, startup, callback flow, or time flow

Add a new FOM only when:

- the domain model is genuinely new
- the scenario requires new object, interaction, or datatype structure
- a tracked example package should own a distinct reusable model

Start here:

- [fom_reading_map.md](fom_reading_map.md)
- [fom-examples/fom_inventory.md](fom-examples/fom_inventory.md)

## Step 2: Pick The Owning Package

Put reusable assets where they belong.

### Repo-Owned Example Or Shared Smoke FOM

Good fit:

- shared smoke XML
- demo XML
- small reusable baseline assets

Typical home:

- package-owned `resources/foms/`

### Scenario-Owned FOM

Good fit:

- Target/Radar
- Proto2025 family examples
- a package with reusable scenario helpers and resources

Typical home:

- `packages/hla-fom-*/src/hla/foms/.../resources/foms/`

### Do Not Do This

- do not duplicate reusable FOM XML under `examples/`
- do not hide canonical XML only inside tests
- do not put transport-specific meaning into the FOM

## Step 3: Validate Before Wiring Code

Run validation first.

Typical commands:

```bash
./tools/fom-validate DemoFOMmodule.xml
./tools/fom-validate TargetRadarFOMmodule.xml
./tools/fom-validate path/to/new_module.xml --edition 2025 --strict-identification
```

If the FOM belongs to a family or load set, validate that load set too:

```bash
./tools/fom-validate path/to/base.xml path/to/extension.xml --html
```

Read:

- [fom_validate.md](fom_validate.md)

## Step 4: Inspect It In The Workbench

Use the workbench when you need inspection, family context, or merged-view
checks.

Typical commands:

```bash
./tools/fom-workbench
./tools/fom-workbench --html
```

Use this when you need:

- inventory context
- merged counts
- load-set confirmation
- comparison against another family or custom load set

Read:

- [fom_workbench.md](fom_workbench.md)

## Step 5: Wire The Federate Or Scenario

Keep the shape simple.

### Minimal Scenario Pattern

1. choose backend and transport
2. resolve the FOM path
3. create RTI ambassadors
4. connect, create, and join
5. publish and subscribe
6. register objects or send interactions
7. drain callbacks explicitly

Read:

- [backend_transport_fom_selection_guide.md](backend_transport_fom_selection_guide.md)
- [federation_orchestration.md](federation_orchestration.md)

### Where Logic Belongs

Put reusable logic in:

- package-owned `_internal/` scenario helpers
- package-owned FOM path helpers
- verification/shared scenario helpers when the logic is route-neutral

Keep thin wrappers in:

- `examples/`
- small CLI entrypoints

## Step 6: Add The Smallest Useful Test

Pick the lowest layer that proves the change.

### FOM-Only Change

Add:

- validation test
- parse/load test
- workbench or inventory test if catalog metadata changed

### Scenario Or Federate Change

Add:

- one focused route-neutral scenario test first
- route-specific transport test only if the transport seam is part of the change

### New FOM Family Or Example

Add:

- inventory registration proof
- validation proof
- one runnable scenario or smoke proof if behavior is claimed

## FOM Tooling Front Door

Use this routing:

- inspect or find a FOM:
  [fom_reading_map.md](fom_reading_map.md)
- validate a FOM:
  [fom_validate.md](fom_validate.md)
- inspect through the UI/workbench:
  [fom_workbench.md](fom_workbench.md)
- choose backend + transport + FOM together:
  [backend_transport_fom_selection_guide.md](backend_transport_fom_selection_guide.md)

## Copyable Starting Recipes

### Recipe 1: Add A Small Route-Proof Federate

- use existing `VendorSmokeFOM.xml`
- validate it
- wire a tiny two-federate scenario
- prove startup, exchange, or callback flow

Open:

1. [backend_transport_fom_selection_guide.md](backend_transport_fom_selection_guide.md)
2. [fom_validate.md](fom_validate.md)
3. [two_federate_quickstart.md](two_federate_quickstart.md)

### Recipe 2: Add A Scenario-Owned Example

- choose Target/Radar or Proto2025-style ownership
- keep XML in the owning package
- add reusable helper logic under `_internal/`
- keep the top-level example script thin

Open:

1. [fom_reading_map.md](fom_reading_map.md)
2. [fom_workbench.md](fom_workbench.md)
3. [federation_orchestration.md](federation_orchestration.md)

### Recipe 3: Add A New FOM Family Artifact

- register it in inventory
- validate it directly
- validate the family load set if applicable
- only then add runnable claims

Open:

1. [fom-examples/fom_inventory.md](fom-examples/fom_inventory.md)
2. [fom_validate.md](fom_validate.md)
3. [fom_workbench.md](fom_workbench.md)

## Read Next

1. [backend_transport_fom_selection_guide.md](backend_transport_fom_selection_guide.md)
2. [fom_reading_map.md](fom_reading_map.md)
3. [fom_validate.md](fom_validate.md)
4. [fom_workbench.md](fom_workbench.md)
