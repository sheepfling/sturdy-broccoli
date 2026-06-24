# Sturdy Broccoli

This repository is a Python-first IEEE HLA workspace.

- `hla.rti1516e` is the IEEE 1516.1-2010 API package
- `hla.rti1516_2025` is the IEEE 1516.1-2025 API package
- `hla.rti` owns cross-version discovery and ambassador creation
- multiple backend, transport, vendor, bridge, FOM, and verification packages
- Use `hla.backends.python1516_2025` for the main Python RTI backend for IEEE 1516.1-2025.
- `hla-backend-python1516-2025` is the main full executable Python RTI implementation lane.
- `hla-backend-shim` is a compatibility-wrapper package over that runtime, not a separate RTI family.
- Java and C++ 2025 binding routes are supporting route surfaces over the Python 2025 lane, not alternate Python RTIs.
- `hla-backend-shim` remains only as compatibility-wrapper/import-compatibility code around that runtime.
- `python1516_2025` is the main Python RTI implementation lane for IEEE 1516.1-2025.
- `hla.backends.shim` is compatibility-wrapper/import-compatibility code over `python1516_2025`.

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
python examples/target_radar_simulation.py --backend python1516_2025 --steps 5
./tools/test
```

Operator commands that matter from the top level:

- `./tools/python verify`
- `./tools/test-focus inventory`
- `./tools/test-focus run target-radar`
- `./tools/test-focus run python-2025-time`
- `./tools/compliance generate`
- `./tools/compliance discover --show-backlog`
- `./tools/certi-easy preflight`
- `./tools/java verify`
- `./tools/pitch preflight`
- `./tools/vendor-green matrix`

If you want the main follow-on guides, use:

- [`docs/onboarding.md`](docs/onboarding.md): choose the right path for your goal
- [`docs/first_run.md`](docs/first_run.md): shortest fresh-checkout walkthrough
- [`docs/python_environment.md`](docs/python_environment.md): fuller environment and install story
- [`docs/junior_test_diagnosis_runbook.md`](docs/junior_test_diagnosis_runbook.md): shortest junior-friendly repo-green, rerun, and failure-diagnosis path
- [`docs/test_surface.md`](docs/test_surface.md): lane and focused-target map
- [`docs/README.md`](docs/README.md): docs index by task

Read [`docs/first_run.md`](docs/first_run.md) for the 2010 pure-Python bootstrap lane.

If you need a specific lane:

- repo mental model: [`docs/repo_mental_model.md`](docs/repo_mental_model.md)
- runtime editing: [`docs/python_rti_edit_one_service.md`](docs/python_rti_edit_one_service.md)
- package structure: [`docs/package_layout.md`](docs/package_layout.md)
- import rules: [`docs/import_boundary_rules.md`](docs/import_boundary_rules.md)
- FOM tooling: [`docs/fom_workbench.md`](docs/fom_workbench.md)
- two-federate flow: [`docs/two_federate_quickstart.md`](docs/two_federate_quickstart.md)
- package inventory: [`packages/README.md`](packages/README.md)
- minimal Java bridge wrapping recipe: [`docs/java_bridge_minimal_protocol_recipe.md`](docs/java_bridge_minimal_protocol_recipe.md)
- Java bridge quick guide: [`docs/java_bridge_wrapping_guide.md`](docs/java_bridge_wrapping_guide.md)
- Java bridge architecture: [`docs/java_rti_adaptation_architecture.md`](docs/java_rti_adaptation_architecture.md)

For the main 2025 Python RTI proof lanes:

- Use `verify-main-2025` as the default direct `python1516_2025` proof lane.
- Run `./tools/python verify-main-2025` for the default direct `python1516_2025` proof lane.
- Use `verify-routes-2025` when you also need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane over `hla-backend-python1516-2025`.
- Run `./tools/python verify-routes-2025` when you also need the bounded hosted `python1516_2025-fedpro-grpc` route lane.
- Accepted runtime spellings: `python1516_2025`, `python-1516-2025`, `python-1516-2025`.

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
