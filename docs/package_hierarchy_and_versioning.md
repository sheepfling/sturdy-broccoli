# Package Hierarchy And Versioning

Use this page for the short answer to:

1. what are the layers?
2. how do the installable packages fit into those layers?
3. are the packages versioned independently?

For the deeper ownership guide, use [`package_layout.md`](package_layout.md).
For the stricter import rules, use
[`import_boundary_rules.md`](import_boundary_rules.md).
For the generated dependency graph, use
[`package_dependency_tree.md`](package_dependency_tree.md).

## The Layer Model

Read the repo from top to bottom like this:

| Layer | What it owns | Main packages |
| --- | --- | --- |
| 1. Standard surfaces | public HLA-facing Python APIs | `hla-rti1516e`, `hla-rti1516-2025` |
| 2. Shared support | factories, registries, shared codecs, common helpers | `hla-rti-core`, `hla-backend-common`, `hla-transport-common`, `hla-bridge-java-common` |
| 3. Concrete backends | actual HLA service behavior | `hla-backend-inmemory`, `hla-backend-python2025`, `hla-backend-certi`, `hla-backend-shim`, `hla-backend-cpp-shim` |
| 4. Integrations | transport, vendor, and bridge routes | `hla-transport-grpc`, `hla-transport-rest`, `hla-bridge-java-jpype`, `hla-bridge-java-py4j`, `hla-vendor-pitch`, `hla-vendor-pitch-jpype`, `hla-vendor-pitch-py4j`, `hla-vendor-portico` |
| 5. Leaves | concrete FOMs, scenarios, and proof harnesses | `hla-fom-target-radar`, `hla-fom-proto2025-message-test`, `hla-fom-proto2025-space-lite`, `hla-fom-proto2025-time-mgmt-test`, `hla-verification` |

This is the hierarchy that matters most.

## The Package Families

Use this as the quick family map:

- `hla-rti1516e`
  - 2010 standard API package
- `hla-rti1516-2025`
  - 2025 standard API package
- `hla-rti-core`
  - cross-version runtime discovery and factory support through `hla.rti`
- `hla-backend-common`
  - shared backend-neutral support code
- `hla-transport-common`
  - shared transport-neutral hosted request support
- `hla-bridge-java-common`
  - shared Java bridge support
- `hla-backend-*`
  - concrete runtime behavior engines
- `hla-transport-*`
  - concrete network and hosted transport layers
- `hla-vendor-*`
  - vendor-specific runtime integrations
- `hla-bridge-*`
  - JPype/Py4J bridge implementations
- `hla-fom-*`
  - concrete FOM resources and showcase packages
- `hla-verification`
  - public verification surface plus repo-internal proof helpers

## The Dependency Story

The intended direction is simple:

```text
standard surface
  -> shared support
  -> concrete backend
  -> transport / vendor / bridge integration
  -> FOM / scenario / verification leaves
```

That does not mean every package depends on every lower layer. It means the
repo should become easier to reason about as you move downward from abstract
surface to concrete execution.

The most important rules are:

- standard packages should stay small
- shared support should not quietly become a backend
- transport is not a backend
- vendor packages are integrations, not standard surfaces
- FOM/example packages are leaves, not core runtime layers

## What Makes The Hierarchy Feel Confusing

There are three different structures at once:

1. distribution names
   - `hla-backend-inmemory`
2. import paths
   - `hla.backends.inmemory`
3. runtime role
   - standard surface, support, backend, integration, leaf

The runtime role is the one to optimize for when reading the repo.

## Versioning Status

Every installable package has its own `project.version` field in its own
`pyproject.toml`, so the workspace is structurally capable of independent
versioning.

But it is not operating that way today.

Current state:

- every package is at `0.13.0`
- internal dependencies are pinned exactly
- the workspace behaves like a lockstep versioned package set

So the accurate answer is:

- separate version fields: yes
- independently releasable today: not cleanly

## What True Independent Versioning Would Require

To move away from lockstep versioning, the repo would need:

1. compatibility policy for shared support packages
2. dependency ranges instead of exact `==` pins where appropriate
3. release tooling that can publish one package intentionally
4. explicit bump rules for dependent packages

The safest place to start would be the leaf packages.
The riskiest place to start would be the standard surfaces and shared core.

## Read Next

1. [`repo_mental_model.md`](repo_mental_model.md)
2. [`package_layout.md`](package_layout.md)
3. [`package_dependency_tree.md`](package_dependency_tree.md)
4. [`import_boundary_rules.md`](import_boundary_rules.md)
