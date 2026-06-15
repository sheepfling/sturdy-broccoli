# hla2010-python

This repository is an unofficial IEEE 1516.1-2010 HLA workspace centered on:

- a clean Python-facing HLA spec surface
- split installable packages under `packages/`
- pluggable RTI backends, transports, and verification tooling

Use this page for only three things:

1. get to a working path quickly
2. understand the package hierarchy at a glance
3. find the next document to read

If you want the deep architecture map, use:

- [`docs/package_layout.md`](docs/package_layout.md)
- [`packages/README.md`](packages/README.md)
- [`docs/package_dependency_tree.md`](docs/package_dependency_tree.md)

## Start Here

1. Bootstrap the workspace:

```bash
./tools/bootstrap python
source .venv/bin/activate
```

If you want the broader local QA environment:

```bash
HLA2010_BOOTSTRAP_EXTRAS=qa ./tools/bootstrap python
source .venv/bin/activate
```

2. Run one working pure-Python path:

```bash
python examples/target_radar_simulation.py --backend python --steps 5
```

Wrapper form:

```bash
./tools/examples target-radar --backend in-memory --steps 5
```

3. Ask the repo what verification lane makes sense:

```bash
./tools/test-surface recommend
```

4. Run the default test wrapper:

```bash
./tools/test
```

If you want one more concrete repo-backed smoke example, run:

```bash
python examples/backend_recording.py
```

## Package Hierarchy

The installable package root is [`packages/`](packages/README.md). The
repository root is tooling and workspace orchestration, not an installable
Python package.

Read the package tree this way:

```text
hla2010-spec
  -> shared support packages
    -> backend and transport families
      -> verification and FOM/scenario leaf packages
```

The main families are:

- `hla2010-spec`
  - architectural root package
  - owns the public HLA surface, shared value types, FOM/MOM helpers, and the
    narrow compatibility facade
- shared support
  - `hla2010-rti-backend-common`
  - `hla2010-rti-runtime-common`
  - `hla2010-rti-transport-common`
  - `hla2010-rti-java-common`
  - `hla2010-verification-harness`
- backend families
  - `hla2010-rti-python`
  - `hla2010-rti-certi`
  - `hla2010-rti-java-jpype`
  - `hla2010-rti-java-py4j`
  - `hla2010-rti-pitch-*`
  - `hla2010-rti-portico`
- transport families
  - `hla2010-rti-transport-grpc`
  - `hla2010-rti-transport-rest`
- leaf packages
  - `hla2010-fom-*`

The canonical package docs are:

- [`docs/package_layout.md`](docs/package_layout.md): human-readable hierarchy and family roles
- [`packages/README.md`](packages/README.md): package ownership cards and where to edit first
- [`docs/package_dependency_tree.md`](docs/package_dependency_tree.md): generated dependency evidence
- [`docs/import_boundary_rules.md`](docs/import_boundary_rules.md): allowed dependency directions

## Supported Python Surfaces

Neutral namespace:

- `hla.spec`
- `hla.runtime_api`
- `hla.editions.ed2010`

2010 compatibility namespace:

- `hla2010.spec`
- `hla2010.runtime_api`

Concrete package-owned examples of supported backend and scenario surfaces:

- `hla2010_rti_python`
- `hla2010_rti_transport_grpc`
- `hla2010_fom_target_radar.scenarios`

## Common Paths

Shortest newcomer lanes:

- run something: [`docs/first_run.md`](docs/first_run.md)
- run the backend recording smoke: [`examples/backend_recording.py`](examples/backend_recording.py)
- understand the package split: [`docs/package_layout.md`](docs/package_layout.md)
- decide where to edit: [`packages/README.md`](packages/README.md)
- edit one Python RTI service: [`docs/python_rti_edit_one_service.md`](docs/python_rti_edit_one_service.md)
- create one FOM package: [`docs/create_federate_and_fom.md`](docs/create_federate_and_fom.md)
- trace one requirement to code: [`docs/requirements_trace_one_method.md`](docs/requirements_trace_one_method.md)
- understand verification lanes: [`docs/test_surface.md`](docs/test_surface.md)

## Operator Surface

Stay on `tools/` for supported operator commands:

```bash
./tools/bootstrap python
./tools/test
./tools/test-surface recommend
./tools/python verify-fast
./tools/python verify
./tools/certi-easy preflight
./tools/pitch preflight
```

For vendor and route-specific commands, use:

- [`tools/README.md`](tools/README.md)
- [`docs/backend_route_inventory.md`](docs/backend_route_inventory.md)
- [`docs/rti_options_and_test_matrix.md`](docs/rti_options_and_test_matrix.md)

## Read Next

1. [`docs/onboarding.md`](docs/onboarding.md)
2. [`docs/first_run.md`](docs/first_run.md)
3. [`docs/package_layout.md`](docs/package_layout.md)
4. [`packages/README.md`](packages/README.md)
5. [`docs/python_environment.md`](docs/python_environment.md)
6. [`docs/README.md`](docs/README.md)

## Historical / Provenance

These are for audit and provenance, not onboarding:

- [`docs/source_documents.md`](docs/source_documents.md)
- [`docs/reference/README.md`](docs/reference/README.md)
- [`docs/evidence/README.md`](docs/evidence/README.md)
