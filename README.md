# hla2010-python

This repository is an unofficial IEEE 1516.1-2010 HLA workspace centered on a
clean Python spec surface plus pluggable RTI backends.

The supported runtime front door is:

- `hla2010.spec` for the clean interface contract
- `hla2010.runtime_api` for the Pythonic convenience layer
- `hla2010_rti_python` for the local in-memory RTI backend
- `hla2010_rti_transport_grpc` for networked transport-hosted RTI routes
- `hla2010_fom_target_radar.scenarios` for the Target/Radar example package

If you want the shortest path to "something runs", start with the pure Python
backend and the Target/Radar example.

This root `README` is for:

- what the repo is for
- the shortest run/edit/scaffold/trace path
- the canonical operator entrypoints

It is not the full architecture catalog, backend inventory, or package-family
map. Those live under `docs/` and `packages/`.

`packages/hla2010-spec/src/hla2010/` is the package-owned root Python package for the abstract/core API plus the documented temporary compatibility facade `hla2010.rti`

## Start Here

Use this task-first path:

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
[`packages/hla2010-fom-target-radar/README.md`](packages/hla2010-fom-target-radar/README.md).

If you want an executable setup check first, run:

```bash
./tools/bootstrap doctor
```

2. Run one working Python path:

```bash
python examples/target_radar_simulation.py --backend python --steps 5
```

If you want the workspace-backed wrapper instead of calling the example
directly, use:

```bash
./tools/examples target-radar --backend in-memory --steps 5
```

3. Edit one Python RTI service:

Start with:

```bash
./tools/human-editability front-doors python-rti-service
./tools/human-editability trace getHLAversion
```

That is the shortest maintainer lane for changing one concrete backend service.

4. Scaffold one package-owned FOM and federate example:

```bash
./tools/new-fom-package your-demo
```

5. Trace one method from requirement row to implementation and proof:

```bash
./tools/human-editability front-doors requirements-trace
./tools/human-editability trace getHLAversion
```

6. Run the backend smoke example:

```bash
python examples/backend_recording.py
```

Or through the wrapper:

```bash
./tools/examples backend-recording
```

7. Run the default test wrapper:

```bash
./tools/test
```

## Concrete Lanes

These are the primary newcomer lanes:

- run something: [`docs/first_run.md`](docs/first_run.md)
- edit one service: [`docs/python_rti_edit_one_service.md`](docs/python_rti_edit_one_service.md)
- create one FOM package: [`docs/create_federate_and_fom.md`](docs/create_federate_and_fom.md)
- trace one method: [`docs/requirements_trace_one_method.md`](docs/requirements_trace_one_method.md)
- understand ownership: [`packages/README.md`](packages/README.md)

If you need the vendor flows, use the `tools/` operator surface:

```bash
./tools/certi-easy preflight
./tools/certi-easy install
./tools/certi-easy smoke compare

./tools/pitch preflight
./tools/pitch install
./tools/pitch smoke
./tools/pitch verify

./tools/python verify
./tools/vendor-green matrix
```

## What This Repo Is For

The main import surface is `hla2010`, with the clean contract at
`hla2010.spec`. The `packages/hla2010-spec/src/hla2010/` tree stays limited to the abstract/core API,
backend-neutral types and contracts, FOM/MOM helpers, and the one documented
temporary split-package facade `hla2010.rti`.

Concrete backend implementations now live in package-owned source trees such as:

- `packages/hla2010-rti-python/src/hla2010_rti_python/`
- `packages/hla2010-rti-certi/src/hla2010_rti_certi/`
- `packages/hla2010-rti-java-jpype/src/hla2010_rti_java_jpype/`
- `packages/hla2010-rti-java-py4j/src/hla2010_rti_java_py4j/`
- `packages/hla2010-rti-portico/src/hla2010_rti_portico/`

Namespace policy:

- `hla2010` is the supported runtime namespace
- `hla2010_verification_harness` is the only supported public verification namespace
- `hla2010_fom_target_radar.scenarios` is public scenario/FOM surface
- `hla2010.testing` is not public API and is intentionally removed
- repo-only proof, report, and suite orchestration helpers live under `src/hla2010_repo_internal/verification/`

The repo is intended to make it easy to:

- write federates against one API
- swap backends without rewriting application logic
- validate behavior against local, bridged, and real vendor runtimes
- generate the evidence needed to understand what is supported today

For the shortest deeper maps after this page:

- examples and first run: [`docs/first_run.md`](docs/first_run.md)
- package ownership: [`packages/README.md`](packages/README.md)
- workspace areas: [`docs/workspace_layout.md`](docs/workspace_layout.md)
- package-family boundaries: [`docs/package_layout.md`](docs/package_layout.md)
- backend maturity and routes: [`docs/backend_route_inventory.md`](docs/backend_route_inventory.md)
- full docs index: [`docs/README.md`](docs/README.md)

If you only need the shortest "what works right now?" answer, use:

```bash
./tools/compliance generate
./tools/compliance discover --show-backlog
```

## Read Next

1. [`docs/onboarding.md`](docs/onboarding.md) for the canonical run/edit/scaffold/trace onboarding path
2. [`docs/first_run.md`](docs/first_run.md) for the shortest new-machine-to-first-example path
3. [`docs/python_rti_edit_one_service.md`](docs/python_rti_edit_one_service.md) for the shortest maintainer service-edit lane
4. [`docs/create_federate_and_fom.md`](docs/create_federate_and_fom.md) for the package-backed FOM/federate path
5. [`docs/requirements_trace_one_method.md`](docs/requirements_trace_one_method.md) for the shortest requirement-to-code trace lane
6. [`packages/README.md`](packages/README.md) for package ownership cards
7. [`docs/README.md`](docs/README.md) for the full documentation map

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
- [`packages/hla2010-rti-certi/docs/certi_section8_runbook.md`](packages/hla2010-rti-certi/docs/certi_section8_runbook.md) for the CERTI operator runbook
- [`packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md`](packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md) for Pitch selection and troubleshooting

## Historical / Provenance

These are kept for audit and provenance, not for onboarding:

- [`docs/source_documents.md`](docs/source_documents.md)
- [`docs/reference/README.md`](docs/reference/README.md)
- [`docs/evidence/README.md`](docs/evidence/README.md)

The repository intentionally keeps generated artifacts out of version control when they can be reproduced from source.
