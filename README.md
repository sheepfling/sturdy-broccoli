# hla2010-python

This repository is an unofficial IEEE 1516.1-2010 HLA workspace centered on a
clean Python spec surface plus pluggable RTI backends.

The supported front door is:

- `hla.rti1516e.spec` for the clean interface contract
- `hla.rti1516e.runtime_api` for the Pythonic convenience layer
- `hla.backends.inmemory` for the local in-memory RTI backend
- `hla.transports.grpc` for networked transport-hosted RTI routes
- `hla.foms.target_radar.scenarios` for the Target/Radar example package

If you want the shortest path to "something runs", start with the pure Python
backend and the Target/Radar example.

If you want to understand the package split, start here:

- [`docs/package_layout.md`](docs/package_layout.md)
- [`docs/package_hierarchy_and_versioning.md`](docs/package_hierarchy_and_versioning.md)
- [`docs/package_dependency_tree.md`](docs/package_dependency_tree.md)
- [`packages/README.md`](packages/README.md)

This root `README` owns only three jobs:

- show the shortest runnable path
- point to the primary edit and trace lanes
- name the supported operator entrypoints

It is not the full architecture catalog, backend inventory, or package-family
map. Those live under `docs/` and `packages/`.

The repo is organized as a monorepo workspace:

- `hla.rti1516e` is the IEEE 1516.1-2010 API package
- `hla.rti` owns cross-version discovery and backend selection
- `packages/*/src/` holds package-owned backend, FOM, transport, and support implementations
- `tools/` is the canonical home for human-facing operator entrypoints
- `examples/`, `scripts/`, `tests/`, and `docs/` stay repo-local

## Start Here

1. Bootstrap the Python environment:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

That creates or refreshes the repo-local virtual environment and installs the
workspace in editable mode.

If you want the broader local QA environment instead of the lean operator
bootstrap, use:

```bash
HLA2010_BOOTSTRAP_EXTRAS=qa ./tools/bootstrap python
source .venv/bin/activate
```

For the full environment and install order, read
[`docs/python_environment.md`](docs/python_environment.md).

If you want the shortest single walkthrough, use
[`docs/first_run.md`](docs/first_run.md).

If you want the networked Python RTI guide, use
[`docs/networked_rti_python.md`](docs/networked_rti_python.md).

If you want the Target/Radar package guide, use
[`packages/hla-fom-target-radar/README.md`](packages/hla-fom-target-radar/README.md).

If you want an executable setup check first, run:

```bash
./tools/bootstrap doctor
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
./tools/test
```

If you need the vendor flows, stay on the `tools/` operator surface:

```bash
./tools/certi-easy preflight
./tools/certi-easy install
./tools/certi-easy smoke compare

./tools/pitch preflight
./tools/pitch install
./tools/pitch smoke
./tools/pitch verify

./tools/test-surface recommend
./tools/python verify-routes-preflight
./tools/python verify-routes
./tools/python verify-fast
./tools/python verify
./tools/vendor-green matrix
```

## Concrete Lanes

These are the primary newcomer lanes:

- run something: [`docs/first_run.md`](docs/first_run.md)
- edit one service: [`docs/python_rti_edit_one_service.md`](docs/python_rti_edit_one_service.md)
- create one FOM package: [`docs/create_federate_and_fom.md`](docs/create_federate_and_fom.md)
- trace one method: [`docs/requirements_trace_one_method.md`](docs/requirements_trace_one_method.md)
- understand ownership: [`packages/README.md`](packages/README.md)

## What This Repo Is For

The main 2010 import surface is `hla.rti1516e`, with cross-version discovery
and factory selection under `hla.rti`.

Concrete backend implementations now live in package-owned source trees such as:

- `packages/hla-backend-inmemory/src/hla/backends/inmemory/`
- `packages/hla-backend-certi/src/hla/backends/certi/`
- `packages/hla-bridge-java-jpype/src/hla.bridges.java.jpype/`
- `packages/hla-bridge-java-py4j/src/hla.bridges.java.py4j/`
- `packages/hla-vendor-portico/src/hla/vendors/portico/`

Namespace policy:

- `hla2010` is the supported runtime namespace
- `hla.verification` is the only supported public verification namespace
- `hla.foms.target_radar.scenarios` is public scenario/FOM surface
- `hla.rti1516e.testing` is not public API and is intentionally removed
- repo-only proof, report, and suite orchestration helpers live under `packages/hla-verification/src/hla/verification/repo_internal/verification/`

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
- `examples/java_shim_federate.py` - Java-bridge demo through the repo verification shim or a real bridge
- `examples/jpype_java_rti.py` - JPype vendor-RTI skeleton
- `examples/py4j_java_rti.py` - Py4J vendor-RTI skeleton
- `examples/fom_time_factories.py` - FOM/time factory example

For the Target/Radar example, the bundled FOM lives at:

- `packages/hla-fom-target-radar/src/hla.foms.target_radar/resources/foms/TargetRadarFOMmodule.xml`

The `examples/` tree is for runnable entrypoints and thin example-only assets.
Reusable runtime assets belong under their owning package roots. For
Target/Radar that canonical owner is `hla-fom-target-radar`.

## Two-Federate Starter

If you want a focused starting note for the two-federate example, use
[`docs/two_federate_quickstart.md`](docs/two_federate_quickstart.md).

## Backend Surface

This workspace has a lot more than just the pure Python RTI.

Current backend names include:

- `python`, `in-memory`, `python-in-memory`
- `jpype`, `py4j`
- `pitch-jpype`, `pitch-py4j`
- `certi`, `certi-jpype`, `certi-py4j`
- `portico`, `portico-jpype`, `portico-py4j`
- transport surfaces under `grpc`, `rest`, and `http-json`

The important part is that these are not all the same level of maturity:

- `python` is the strongest local reference path
- the Java shims are repo verification backends, not part of the public runtime surface
- CERTI and Pitch are real vendor paths with their own launch and smoke flows
- Portico wiring exists, but local evidence depends on installed runtime
- `grpc` and `rest` are transport surfaces, not separate RTI families

For the current route inventory and support status, read:

- [`docs/backend_route_inventory.md`](docs/backend_route_inventory.md)
- [`docs/backend_capability_matrix.md`](docs/backend_capability_matrix.md)
- [`docs/backend_conformance_matrix.md`](docs/backend_conformance_matrix.md)
- [`docs/rti_options_and_test_matrix.md`](docs/rti_options_and_test_matrix.md)
- [`docs/networked_rti_python.md`](docs/networked_rti_python.md)

If you only need the shortest "what works right now?" answer, use:

```bash
./tools/compliance generate
./tools/compliance discover --show-backlog
```

## Repository Layout

```text
src/hla2010/          core API layer plus the documented temporary compatibility facade hla.rti1516e.rti
packages/hla-verification/src/hla/verification/repo_internal/ verification/proof/report helpers kept out of public API
packages/*/src/       package-owned backend and support implementation roots
examples/             runnable example federates and scenario entrypoints
tests/                pytest coverage and smoke tests
tools/                human-facing operator entrypoints
scripts/              implementation helpers, CI wrappers, and plumbing
docs/                 route inventories, runbooks, and verification docs
packages/             installable workspace packages and migration metadata
specs/ieee-1516-2010/  retained IEEE reference PDFs and source ZIPs
CERTI/                vendored CERTI source tree
java_shims/           Java shim source for bridge validation
analysis/             generated compliance and verification artifacts
```

## Read Next

1. [`docs/first_run.md`](docs/first_run.md) for the shortest new-machine-to-first-example path
2. [`docs/python_environment.md`](docs/python_environment.md) for environment setup and install order
3. [`docs/two_federate_quickstart.md`](docs/two_federate_quickstart.md) for the first artifact-producing two-federate flow
4. [`docs/README.md`](docs/README.md) for the full documentation map

## Reference

- [`docs/README.md`](docs/README.md) for the documentation index
- [`docs/first_run.md`](docs/first_run.md) for the shortest new-machine-to-first-example path
- [`docs/python_environment.md`](docs/python_environment.md) for environment setup and install order
- [`docs/top_to_bottom_green.md`](docs/top_to_bottom_green.md) for the explicit finish definition and green acceptance contract
- [`docs/install_matrix.md`](docs/install_matrix.md) for extras, bridge deps, and vendor-runtime ordering
- [`docs/agent_runbook.md`](docs/agent_runbook.md) for the agent/automation startup sequence
- [`docs/workspace_layout.md`](docs/workspace_layout.md) for the top-level workspace area split
- [`docs/python_api_spec.md`](docs/python_api_spec.md) for the clean Python spec package
- [`tools/README.md`](tools/README.md) for the supported operator command surface
- [`scripts/README.md`](scripts/README.md) for implementation helpers and wrappers
- [`docs/documentation_hierarchy.md`](docs/documentation_hierarchy.md) for the doc structure
- [`requirements/README.md`](requirements/README.md) for the seeded requirements catalog
- [`packages/hla-backend-certi/docs/certi_section8_runbook.md`](packages/hla-backend-certi/docs/certi_section8_runbook.md) for the CERTI operator runbook
- [`packages/hla-vendor-pitch/docs/pitch_decision_tree.md`](packages/hla-vendor-pitch/docs/pitch_decision_tree.md) for Pitch selection and troubleshooting

## Historical / Provenance

These are kept for audit and provenance, not for onboarding:

- [`docs/source_documents.md`](docs/source_documents.md)
- [`docs/reference/README.md`](docs/reference/README.md)
- [`docs/reference/hla_interface_contracts.md`](docs/reference/hla_interface_contracts.md) for the generated interface-contract snapshot
- [`docs/evidence/README.md`](docs/evidence/README.md)

The repository intentionally keeps generated artifacts out of version control when they can be reproduced from source.
