# hla2010-python

This repository is an unofficial IEEE 1516.1-2010 HLA workspace centered on a
clean Python spec surface plus pluggable RTI backends.
It gives you:

- a dependency-free in-memory Python RTI for fast local development
- Java bridge profiles through JPype and Py4J
- repo-local CERTI and Pitch operator flows
- transport-hosted gRPC and REST routes
- example federates, scenario runners, tests, and verification artifacts

If you want the shortest path to "something runs", start with the pure Python
backend and the Target/Radar example.

The repo is organized as a monorepo workspace:

- `src/hla2010/` is the root Python package and compatibility layer
- `hla2010/` is a narrow top-level shim area for plugin-facing glue
- `packages/*/src/` holds package-owned backend, FOM, and support implementations
- `examples/`, `scripts/`, `tests/`, and `docs/` stay repo-local

## Quick Start

1. Bootstrap the Python environment:

```bash
./scripts/bootstrap_profile.sh python
source .venv/bin/activate
```

That creates or refreshes the repo-local virtual environment and installs the
workspace in editable mode.

If you want the broader local QA environment instead of the lean operator
bootstrap, use:

```bash
./scripts/bootstrap_python.sh
source .venv/bin/activate
```

For the full environment and install order, read
[`docs/python_environment.md`](docs/python_environment.md).

If you want the shortest single walkthrough, use
[`docs/first_run.md`](docs/first_run.md).

If you want an executable setup check first, run:

```bash
./scripts/bootstrap_profile.sh doctor
```

2. Run the simplest scenario:

```bash
python examples/target_radar_simulation.py --backend python --steps 5
```

3. Run the backend smoke example:

```bash
python examples/backend_recording.py
```

4. Run the default test wrapper:

```bash
./scripts/ci/test.sh
```

If you need the vendor flows, the repo also includes:

```bash
./scripts/certi_easy.sh preflight
./scripts/certi_easy.sh install
./scripts/certi_easy.sh smoke compare

./scripts/pitch_docker_easy.sh preflight
./scripts/pitch_docker_easy.sh install
./scripts/pitch_docker_easy.sh smoke
./scripts/pitch_docker_easy.sh verify

./scripts/ci/repo_green.sh
./scripts/ci/vendor_green.sh matrix
```

## What This Repo Is For

The main import surface is `hla2010`, with the clean contract at
`hla2010.spec`. The `src/hla2010/` tree is the stable API layer plus
compatibility facades while backend ownership moves into separate installable
distributions. In practice:

- the backend-neutral RTI surface
- compatibility exports for split backend families
- shared abstractions used across backend packages
- scenario support for Target/Radar, synchronization, ownership, time, and MOM/MIM work
- compliance, traceability, and verification helpers

Concrete backend implementations now live in package-owned source trees such as:

- `packages/hla2010-rti-python/src/hla2010_rti_python/`
- `packages/hla2010-rti-certi/src/hla2010_rti_certi/`
- `packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/`
- `packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/`
- `packages/hla2010-rti-portico/src/hla2010_rti_portico/`

The installable package intentionally excludes `hla2010/testing`; those modules
are repo-internal support code for tests, scenario runners, and artifact
generation.

The repo is intended to make it easy to:

- write federates against one API
- swap backends without rewriting application logic
- validate behavior against local, bridged, and real vendor runtimes
- generate the evidence needed to understand what is supported today

## Example Federates

The `examples/` directory is the fastest way to see the API in action.

Good starting points:

- `examples/target_radar_simulation.py` - backend-neutral Target/Radar scenario runner
- `examples/target_radar.py` - JSON-formatted Target/Radar scenario output
- `examples/backend_recording.py` - tiny backend abstraction smoke example
- `examples/minimal_federate.py` - minimal callback skeleton
- `examples/java_shim_federate.py` - Java-bridge demo through the in-process shim or a real bridge
- `examples/jpype_java_rti.py` - JPype vendor-RTI skeleton
- `examples/py4j_java_rti.py` - Py4J vendor-RTI skeleton
- `examples/fom_time_factories.py` - FOM/time factory example

For the Target/Radar example, the bundled FOM lives at:

- `packages/hla2010-fom-target-radar/src/hla2010_fom_target_radar/resources/foms/TargetRadarFOMmodule.xml`

The `examples/` tree is for runnable entrypoints and thin example-only assets.
Reusable runtime assets belong under their owning package roots. For
Target/Radar that canonical owner is `hla2010-fom-target-radar`; the
`src/hla2010/resources/` path is kept only for compatibility during migration.

## Two-Federate Starter

If you want a focused starting note for the two-federate example, use
[`docs/two_federate_quickstart.md`](docs/two_federate_quickstart.md).

## Backend Surface

This workspace has a lot more than just the pure Python RTI.

Current backend names include:

- `python`, `in-memory`, `python-in-memory`
- `java-shim-jpype`, `java-shim-py4j`
- `jpype`, `py4j`
- `pitch-jpype`, `pitch-py4j`
- `certi`, `certi-jpype`, `certi-py4j`
- `portico`, `portico-jpype`, `portico-py4j`
- transport surfaces under `grpc`, `rest`, and `http-json`

The important part is that these are not all the same level of maturity:

- `python` is the strongest local reference path
- the Java shims are useful bridge proofs
- CERTI and Pitch are real vendor paths with their own launch and smoke flows
- Portico wiring exists, but local evidence depends on installed runtime
- `grpc` and `rest` are transport surfaces, not separate RTI families

For the current route inventory and support status, read:

- [`docs/backend_route_inventory.md`](docs/backend_route_inventory.md)
- [`docs/backend_capability_matrix.md`](docs/backend_capability_matrix.md)
- [`docs/backend_conformance_matrix.md`](docs/backend_conformance_matrix.md)
- [`docs/rti_options_and_test_matrix.md`](docs/rti_options_and_test_matrix.md)

If you only need the shortest "what works right now?" answer, use:

```bash
python3 scripts/generate_compliance_artifacts.py
python3 scripts/discover_backend_compliance.py --show-backlog
```

## Repository Layout

```text
src/hla2010/          core API layer and compatibility facades
hla2010/              narrow plugin-facing shim area
packages/*/src/       package-owned backend and support implementation roots
examples/             runnable example federates and scenario entrypoints
tests/                pytest coverage and smoke tests
scripts/              operator entrypoints and CI wrappers
docs/                 route inventories, runbooks, and verification docs
packages/             installable workspace packages and migration metadata
specs/ieee-1516-2010/  retained IEEE reference PDFs and source ZIPs
CERTI/                vendored CERTI source tree
java_shims/           Java shim source for bridge validation
analysis/             generated compliance and verification artifacts
```

## More Detail

- [`docs/README.md`](docs/README.md) for the documentation index
- [`docs/first_run.md`](docs/first_run.md) for the shortest new-machine-to-first-example path
- [`docs/python_environment.md`](docs/python_environment.md) for environment setup and install order
- [`docs/install_matrix.md`](docs/install_matrix.md) for extras, bridge deps, and vendor-runtime ordering
- [`docs/agent_runbook.md`](docs/agent_runbook.md) for the agent/automation startup sequence
- [`docs/workspace_layout.md`](docs/workspace_layout.md) for the top-level workspace area split
- [`docs/python_api_spec.md`](docs/python_api_spec.md) for the clean Python spec package
- [`scripts/README.md`](scripts/README.md) for operator commands and wrappers
- [`docs/documentation_hierarchy.md`](docs/documentation_hierarchy.md) for the doc structure
- [`requirements/README.md`](requirements/README.md) for the seeded requirements catalog
- [`packages/hla2010-rti-certi/docs/certi_section8_runbook.md`](packages/hla2010-rti-certi/docs/certi_section8_runbook.md) for the CERTI operator runbook
- [`packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md`](packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md) for Pitch selection and troubleshooting

The repository intentionally keeps generated artifacts out of version control when they can be reproduced from source.
