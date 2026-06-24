# Repo Mental Model

This repo feels like "wheels within wheels" when you read it as a tree.

Do not read it as a tree first.

Read it as five layers with one job each.

## The Short Version

1. standard API packages
   - `hla.rti1516e`
   - `hla.rti1516_2025`
   - job: define the public HLA-facing Python surfaces
2. shared runtime support
   - `hla.rti`
   - `hla.backends.common`
   - `hla.transports.common`
   - job: shared factory, registry, codec, and support logic
3. concrete backends
   - `hla.backends.python1516e`
   - `hla.backends.python1516_2025`
   - `hla.backends.certi`
   - job: actually execute HLA service behavior
4. integrations
   - `hla.transports.*`
   - `hla.vendors.*`
   - `hla.bridges.*`
   - job: connect the runtime to networks, Java runtimes, and vendor systems
5. leaves
   - `hla.foms.*`
   - `hla.verification`
   - `examples/`
   - job: package concrete FOMs, scenarios, and proof flows

That is the real structure.

Everything else is detail inside one of those layers.

## What Makes It Feel Hard

There are three different kinds of hierarchy mixed together:

1. package hierarchy
   - `packages/hla-backend-python1516e`
2. import hierarchy
   - `hla.backends.python1516e`
3. runtime role hierarchy
   - standard surface -> support -> backend -> integration -> scenario/proof

The third one is the important one.

The first two are mostly packaging mechanics.

## The Naming Pattern

Use this translation:

| Distribution | Import path | Meaning |
| --- | --- | --- |
| `hla-rti1516e` | `hla.rti1516e` | 2010 standard surface |
| `hla-rti1516-2025` | `hla.rti1516_2025` | 2025 standard surface |
| `hla-rti-core` | `hla.rti` | cross-version runtime support |
| `hla-backend-*` | `hla.backends.*` | concrete behavior engines |
| `hla-transport-*` | `hla.transports.*` | network/wire layers |
| `hla-vendor-*` | `hla.vendors.*` | vendor-specific runtime support |
| `hla-bridge-*` | `hla.bridges.*` | language/runtime bridges |
| `hla-fom-*` | `hla.foms.*` | concrete FOM packages |

If a name starts with `backend`, it owns behavior.
If it starts with `transport`, it owns wire movement.
If it starts with `vendor` or `bridge`, it owns external integration.
If it starts with `fom`, it owns concrete model assets or showcases.

## The Two Most Important Separations

Keep these boundaries straight:

1. standard package vs implementation package
   - `hla.rti1516e` is not where backend behavior should live
   - `hla.backends.*` is where backend behavior should live
2. backend vs transport
   - backend: executes semantics
   - transport: carries messages to a backend

Most confusion in the repo comes from those two lines getting blurry.

## Ignore These On First Pass

Do not start by reading:

- deep vendor-package docs
- archived evidence bundles
- generated dependency trees
- package-local migration notes
- long verification inventories

Those are reference material, not the mental model.

## Good Questions To Ask Instead

When you open any file or package, ask:

1. Is this public standard surface, shared support, concrete behavior, integration glue, or a leaf asset?
2. Does this code define behavior, carry data, or describe evidence?
3. Could this live in a smaller or lower layer?

Those three questions usually tell you where something belongs.

## Read Next

1. [`package_layout.md`](package_layout.md)
2. [`package_hierarchy_and_versioning.md`](package_hierarchy_and_versioning.md)
3. [`import_boundary_rules.md`](import_boundary_rules.md)
