# FOM Tooling Front Door

Use this page when the question is simply:

"Where do I start with FOM work?"

Do not start by reading every FOM document. Pick the job first, then take the
matching path.

If you have not already classified the problem, start one step higher at
[`work_surfaces.md`](work_surfaces.md).

## One-Page Summary

Use this routing:

1. find or inspect a FOM:
   [`fom_reading_map.md`](fom_reading_map.md)
2. validate a FOM or load set:
   [`fom_validate.md`](fom_validate.md)
3. inspect through the UI or workbench:
   [`fom_workbench.md`](fom_workbench.md)
4. understand how SISO families relate, which editions they target, and which ones are Pitch-eligible:
   [`fom_siso_family_map.md`](fom_siso_family_map.md)
5. add or wire a FOM into a federate or scenario:
   [`create_federate_and_fom.md`](create_federate_and_fom.md)
6. choose backend, transport, and FOM together:
   [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)

If the question turns out not to be mostly about FOM work:

- for backend or route selection:
  [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)
- for transport or hosted route shape:
  [`extending_ambassador_transports.md`](extending_ambassador_transports.md)

## Pick The Shortest Lane

### I Need To Find The Right FOM

Read:

- [`fom_reading_map.md`](fom_reading_map.md)
- [`fom_siso_family_map.md`](fom_siso_family_map.md) for Link 16, RPR, Space, edition scope, and vendor/runtime eligibility

Use this when you need:

- inventory and ownership
- baseline example selection
- family or module lookup

### I Need To Understand How SISO Families Fit Together

Read:

- [`fom_siso_family_map.md`](fom_siso_family_map.md)

Use this when you need:

- root versus extension module structure
- Link 16 versus RPR versus Space family boundaries
- 2010 versus 2025 edition scope
- parser normalization notes for odd datatypes
- Pitch-eligible versus Python-only scenario/runtime lanes

### I Need To Check Whether A FOM Is Valid

Read:

- [`fom_validate.md`](fom_validate.md)

Typical commands:

```bash
./tools/fom-validate DemoFOMmodule.xml
./tools/fom-validate path/to/base.xml path/to/extension.xml --html
```

Use this when you need:

- schema and edition checks
- merged load-set validation
- report output for diagnosis

### I Need A UI Or Merged View

Read:

- [`fom_workbench.md`](fom_workbench.md)

Typical commands:

```bash
./tools/fom-workbench
./tools/fom-workbench --html
```

Use this when you need:

- merged counts
- load-set inspection
- family comparison
- quick browsing without writing code

### I Need To Add A Federate Or Scenario That Uses A FOM

Read:

- [`create_federate_and_fom.md`](create_federate_and_fom.md)

Use this when you need:

- the shortest authoring workflow
- guidance on where XML belongs
- smallest useful validation and test steps

### I Need To Pick Runtime Route And FOM Together

Read:

- [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)

Use this when backend selection, transport selection, and FOM selection are
part of the same decision.

## Minimal Working Order

When in doubt, do this:

1. inspect with [`fom_reading_map.md`](fom_reading_map.md)
2. classify family and edition scope with [`fom_siso_family_map.md`](fom_siso_family_map.md) when the source is SISO-backed
3. validate with [`fom_validate.md`](fom_validate.md)
4. inspect merged behavior with [`fom_workbench.md`](fom_workbench.md)
5. wire code with [`create_federate_and_fom.md`](create_federate_and_fom.md)

## Read Next

1. [`fom_reading_map.md`](fom_reading_map.md)
2. [`fom_siso_family_map.md`](fom_siso_family_map.md)
3. [`fom_validate.md`](fom_validate.md)
4. [`fom_workbench.md`](fom_workbench.md)
