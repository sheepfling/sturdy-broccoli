# hla2010-python

This repository is an unofficial IEEE 1516.1-2010 HLA workspace centered on a Python RTI surface.
It gives you:

- a dependency-free in-memory Python RTI for fast local development
- Java bridge profiles through JPype and Py4J
- repo-local CERTI and Pitch operator flows
- transport-hosted gRPC and REST routes
- example federates, scenario runners, tests, and verification artifacts

If you want the shortest path to "something runs", start with the Python backend and the Target/Radar example.

## Quick Start

1. Bootstrap the Python environment:

```bash
./scripts/bootstrap_python.sh
```

2. Run the simplest scenario:

```bash
python examples/target_radar_simulation.py --backend python --steps 5
```

3. Run the backend smoke example:

```bash
PYTHONPATH=. python examples/backend_recording.py
```

4. Run the default test wrapper:

```bash
./scripts/ci/test.sh
```

If you need the vendor flows, the repo also includes:

```bash
./certi-easy preflight
./certi-easy install
./certi-easy smoke compare

./pitch preflight
./pitch install
./pitch smoke
./pitch verify
```

## What This Repo Is For

The package under `hla2010/` is the code you build against. It includes:

- the backend-neutral RTI surface
- Python backend implementation details
- Java bridge adapters and vendor-facing runtime helpers
- scenario support for Target/Radar, synchronization, ownership, time, and MOM/MIM work
- compliance, traceability, and verification helpers

The installable package intentionally excludes `hla2010.testing`; those modules
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

- `hla2010/resources/foms/TargetRadarFOMmodule.xml`

The `examples/` tree is for runnable entrypoints and thin example-only assets.
Reusable runtime assets belong under `hla2010/resources/` so they ship with the
installable package and stay canonical in one place.

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
hla2010/              Python package source
examples/             runnable example federates and scenario entrypoints
tests/                pytest coverage and smoke tests
scripts/              operator entrypoints and CI wrappers
docs/                 route inventories, runbooks, and verification docs
specs/ieee-1516-2010/  retained IEEE reference PDFs and source ZIPs
CERTI/                vendored CERTI source tree
java_shims/           Java shim source for bridge validation
analysis/             generated compliance and verification artifacts
```

## More Detail

- [`docs/README.md`](docs/README.md) for the documentation index
- [`docs/workspace_layout.md`](docs/workspace_layout.md) for the top-level workspace area split
- [`docs/python_api_spec.md`](docs/python_api_spec.md) for the clean Pythonic abstract/prototype contract
- [`scripts/README.md`](scripts/README.md) for operator commands and wrappers
- [`docs/documentation_hierarchy.md`](docs/documentation_hierarchy.md) for the doc structure
- [`requirements/README.md`](requirements/README.md) for the seeded requirements catalog
- [`docs/certi_section8_runbook.md`](docs/certi_section8_runbook.md) for the CERTI operator runbook
- [`docs/pitch_decision_tree.md`](docs/pitch_decision_tree.md) for Pitch selection and troubleshooting

The repository intentionally keeps generated artifacts out of version control when they can be reproduced from source.
