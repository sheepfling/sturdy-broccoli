# FOM Tooling Front Door

Use this page when the question is simply:

"Where do I start with FOM work?"

Do not start by reading every FOM document. Pick the job first, then take the
matching path.

## One-Page Summary

Use this routing:

1. find or inspect a FOM:
   [`fom_reading_map.md`](fom_reading_map.md)
2. validate a FOM or load set:
   [`fom_validate.md`](fom_validate.md)
3. inspect through the UI or workbench:
   [`fom_workbench.md`](fom_workbench.md)
4. add or wire a FOM into a federate or scenario:
   [`create_federate_and_fom.md`](create_federate_and_fom.md)
5. choose backend, transport, and FOM together:
   [`backend_transport_fom_selection_guide.md`](backend_transport_fom_selection_guide.md)

## Pick The Shortest Lane

### I Need To Find The Right FOM

Read:

- [`fom_reading_map.md`](fom_reading_map.md)

Use this when you need:

- inventory and ownership
- baseline example selection
- family or module lookup

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
2. validate with [`fom_validate.md`](fom_validate.md)
3. inspect merged behavior with [`fom_workbench.md`](fom_workbench.md)
4. wire code with [`create_federate_and_fom.md`](create_federate_and_fom.md)
