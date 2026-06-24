# Sturdy Broccoli

This repository is a Python-first IEEE HLA workspace.

- `hla.rti1516e` is the IEEE 1516.1-2010 API package
- `hla.rti1516_2025` is the IEEE 1516.1-2025 API package
- `hla.rti` owns cross-version discovery and ambassador creation
- multiple backend, transport, vendor, bridge, FOM, and verification packages

The repo is large. The right way to approach it is by lane, not by reading
everything.

## Start Here

If you want the shortest path to something running:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
python examples/backend_recording.py
python examples/target_radar_simulation.py --backend python1516e --steps 5
./tools/test
```

If you want the main follow-on guides, use:

- [`docs/onboarding.md`](docs/onboarding.md): choose the right path for your goal
- [`docs/first_run.md`](docs/first_run.md): shortest fresh-checkout walkthrough
- [`docs/python_environment.md`](docs/python_environment.md): fuller environment and install story
- [`docs/README.md`](docs/README.md): docs index by task

If you need a specific lane:

- repo mental model: [`docs/repo_mental_model.md`](docs/repo_mental_model.md)
- runtime editing: [`docs/python_rti_edit_one_service.md`](docs/python_rti_edit_one_service.md)
- package structure: [`docs/package_layout.md`](docs/package_layout.md)
- import rules: [`docs/import_boundary_rules.md`](docs/import_boundary_rules.md)
- FOM tooling: [`docs/fom_workbench.md`](docs/fom_workbench.md)
- two-federate flow: [`docs/two_federate_quickstart.md`](docs/two_federate_quickstart.md)
- package inventory: [`packages/README.md`](packages/README.md)

## What Lives Where

- `packages/`: installable workspace packages
- `docs/`: operator guides, architecture notes, and reference material
- `examples/`: runnable examples
- `tools/`: supported operator entrypoints
- `tests/`: verification and regression surface

The architectural namespace root is `hla`, contributed by split packages. The
main operator front doors are the versioned API packages, `hla.rti`, and the
`tools/` wrappers.

## Working Rule

Do not try to understand the whole repo at once.

Pick one of these and stay in it:

1. run an example
2. edit one package
3. trace one service
4. work on FOM tooling
5. run one verification lane

The repo becomes manageable once the scope is that small.

## Read Next

1. [`docs/onboarding.md`](docs/onboarding.md)
2. [`docs/first_run.md`](docs/first_run.md)
3. [`docs/python_environment.md`](docs/python_environment.md)
4. [`packages/README.md`](packages/README.md)
