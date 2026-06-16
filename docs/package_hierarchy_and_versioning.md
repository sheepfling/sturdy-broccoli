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
hla2010-spec
└── shared support
    ├── hla2010-rti-backend-common
    ├── hla2010-rti-transport-common
    ├── hla2010-rti-java-common
    ├── hla2010-rti-runtime-common
    └── hla2010-verification-harness
        └── hla2010-fom-target-radar

hla2010-spec
└── hla2010-rti-backend-common
    ├── hla2010-rti-python
    ├── hla2010-rti-transport-common
    │   ├── hla2010-rti-runtime-common
    │   │   ├── hla2010-rti-certi
    │   │   ├── hla2010-rti-pitch-common
    │   │   ├── hla2010-rti-transport-grpc
    │   │   ├── hla2010-rti-transport-rest
    │   │   ├── hla2010-fom-minimal-demo
    │   │   └── hla2010-fom-target-radar
    │   └── hla2010-rti-python
    └── hla2010-rti-java-common
        ├── hla2010-rti-java-jpype
        │   ├── hla2010-rti-pitch-jpype
        │   └── hla2010-rti-portico
        ├── hla2010-rti-java-py4j
        │   ├── hla2010-rti-pitch-py4j
        │   └── hla2010-rti-portico
        ├── hla2010-rti-pitch-common
        └── hla2010-rti-certi
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

- Layer 0: `hla2010-spec`
- Layer 1: `hla2010-rti-backend-common`
- Layer 2: `hla2010-rti-java-common`, `hla2010-rti-python`, `hla2010-rti-transport-common`
- Layer 3: `hla2010-rti-java-jpype`, `hla2010-rti-java-py4j`, `hla2010-rti-runtime-common`
- Layer 4: `hla2010-rti-certi`, `hla2010-rti-java`, `hla2010-rti-pitch-common`, `hla2010-rti-portico`, `hla2010-rti-transport-grpc`, `hla2010-rti-transport-rest`, `hla2010-verification-harness`
- Layer 5: `hla2010-fom-minimal-demo`, `hla2010-fom-target-radar`, `hla2010-rti-pitch-jpype`, `hla2010-rti-pitch-py4j`

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
  `hla2010-spec==0.13.0`
- that means the workspace behaves as a lockstep versioned package set

Examples of the current policy:

- `hla2010-rti-python` depends on:
  - `hla2010-spec==0.13.0`
  - `hla2010-rti-backend-common==0.13.0`
  - `hla2010-rti-transport-common==0.13.0`
- `hla2010-fom-target-radar` depends on:
  - `hla2010-spec==0.13.0`
  - `hla2010-verification-harness==0.13.0`
  - `hla2010-rti-runtime-common==0.13.0`

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

- `hla2010-fom-*`
- possibly `hla2010-rti-transport-*`

The riskiest place to start is the shared core:

- `hla2010-spec`
- `hla2010-rti-backend-common`
- `hla2010-rti-runtime-common`

## Recommended Reading Order

1. [`package_layout.md`](package_layout.md)
2. [`package_hierarchy_and_versioning.md`](package_hierarchy_and_versioning.md)
3. [`package_dependency_tree.md`](package_dependency_tree.md)
4. [`import_boundary_rules.md`](import_boundary_rules.md)
