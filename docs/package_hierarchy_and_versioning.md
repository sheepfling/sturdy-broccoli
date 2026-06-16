# Package Hierarchy And Versioning

Use this page when you need the shortest answer to two questions:

1. how do the installable packages depend on each other?
2. are the packages independently versioned?

For the deeper package ownership guide, use
[`package_layout.md`](package_layout.md).

For the generated dependency evidence, use
[`package_dependency_tree.md`](package_dependency_tree.md).

## Quick Dependency Tree

Read the package families from top to bottom:

```text
hla-rti1516e
└── shared support
    ├── hla-backend-common
    ├── hla-transport-common
    ├── hla-bridge-java-common
    ├── hla-rti-core
    └── hla-verification
        └── hla-fom-target-radar

hla-rti1516e
└── hla-backend-common
    ├── hla-backend-inmemory
    ├── hla-transport-common
    │   ├── hla-rti-core
    │   │   ├── hla-backend-certi
    │   │   ├── hla-vendor-pitch
    │   │   ├── hla-transport-grpc
    │   │   ├── hla-transport-rest
    │   │   └── hla-fom-target-radar
    │   └── hla-backend-inmemory
    └── hla-bridge-java-common
        ├── hla-bridge-java-jpype
        │   ├── hla-vendor-pitch-jpype
        │   └── hla-vendor-portico
        ├── hla-bridge-java-py4j
        │   ├── hla-vendor-pitch-py4j
        │   └── hla-vendor-portico
        ├── hla-vendor-pitch
        └── hla-backend-certi
```

That tree is intentionally simplified. It is meant to answer:

- what is the root package?
- which packages are shared support?
- which packages are backend families?
- which packages are transport families?
- which packages are leaves?

It is not the authoritative graph. The authoritative graph is the generated
one in [`package_dependency_tree.md`](package_dependency_tree.md).

## Current Layers

The current machine-generated layer model is:

- Layer 0: `hla-rti1516e`
- Layer 1: `hla-backend-common`
- Layer 2: `hla-bridge-java-common`, `hla-backend-inmemory`, `hla-transport-common`
- Layer 3: `hla-bridge-java-jpype`, `hla-bridge-java-py4j`, `hla-rti-core`
- Layer 4: `hla-backend-certi`, `hla-vendor-pitch`, `hla-vendor-portico`, `hla-transport-grpc`, `hla-transport-rest`, `hla-verification`
- Layer 5: `hla-fom-target-radar`, `hla-vendor-pitch-jpype`, `hla-vendor-pitch-py4j`

Regenerate and check the dependency evidence with:

```bash
./tools/package-deps generate
./tools/package-deps check
```

## Versioning Status

Every installable package has its own `project.version` field in its own
`pyproject.toml`.

So the repo is structurally capable of per-package version numbers.

But the repo is not currently using true independent versioning.

Current state:

- every package is at `0.13.0`
- internal package dependencies are pinned with exact versions such as
  `hla-rti1516e==0.13.0`
- that means the workspace behaves as a lockstep versioned package set

Examples of the current policy:

- `hla-backend-inmemory` depends on:
  - `hla-rti1516e==0.13.0`
  - `hla-backend-common==0.13.0`
  - `hla-transport-common==0.13.0`
- `hla-fom-target-radar` depends on:
  - `hla-rti1516e==0.13.0`
  - `hla-verification==0.13.0`
  - `hla-rti-core==0.13.0`

So the accurate answer is:

- `separate version fields`: yes
- `independently releasable today`: not cleanly

## What True Independent Versioning Would Require

To move from lockstep to real per-package versioning, the repo would need:

1. a compatibility policy for shared support packages
2. internal dependency ranges instead of exact `==` pins where appropriate
3. release tooling that can publish one package without forcing a full workspace bump
4. explicit rules for when a shared support package bump forces dependent package bumps

If the repo ever moves in that direction, the safest starting point is the
leaf packages first:

- `hla-fom-*`
- possibly transport leaf packages with limited reverse dependencies

The riskiest place to start is the shared core:

- `hla-rti1516e`
- `hla-backend-common`
- `hla-rti-core`

## Recommended Reading Order

1. [`package_layout.md`](package_layout.md)
2. [`package_hierarchy_and_versioning.md`](package_hierarchy_and_versioning.md)
3. [`package_dependency_tree.md`](package_dependency_tree.md)
4. [`import_boundary_rules.md`](import_boundary_rules.md)
