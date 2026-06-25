# Sturdy Broccoli

This repository is a Python-first IEEE HLA workspace.

It gives you:

- installable IEEE HLA API packages for 2010 and 2025
- Python RTI implementation lanes for both editions
- vendor, bridge, hosted, and transport-backed RTI routes
- runnable examples, FOM tooling, and verification lanes

The front door is route-oriented:

- use `./tools/...` commands for operator workflows
- use `hla.rti`, `hla.rti1516e`, and `hla.rti1516_2025` for code-facing RTI entrypoints
- pass backend or route names such as `python1516e`, `python1516_2025`, `pitch-jpype`, or `certi` as selector strings

Those names are lookup strings that select a route. They are not all separate RTI
implementations.

## Fastest Paths

### Get Repo Green

If you want the shortest path to repo green:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
./tools/python verify
```

Use [`docs/repo_green_quickstart.md`](docs/repo_green_quickstart.md) for the
shortest junior-friendly verification path.

### Run Something

If you want the shortest path to something running:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
python examples/backend_recording.py
python examples/target_radar_simulation.py --backend python1516e --steps 5
python examples/target_radar_simulation.py --backend python1516_2025 --steps 5
```

If you want the broader default local test surface after that:

```bash
./tools/test
```

## Route Mental Model

The main route identities are:

- `python1516e`: primary in-process IEEE 1516.1-2010 Python RTI lane
- `python1516_2025`: primary in-process IEEE 1516.1-2025 Python RTI lane
- `python1516_2025` with transport options: hosted 2025 route over the same runtime
- `pitch-jpype`, `pitch-py4j`, `certi`, and similar names: vendor or bridge-backed routes

Example:

```python
from hla.runtime.factory import create_rti_ambassador

rti_2010 = create_rti_ambassador("python1516e")
rti_2025 = create_rti_ambassador("python1516_2025")
rti_pitch = create_rti_ambassador("pitch-jpype")
```

Important architecture rule:

- `hla-backend-python1516-2025` is the implementation-owning 2025 Python RTI package
- `hla-backend-shim` and `hla.backends.shim` are legacy compatibility layers, not separate RTI families
- Java and C++ 2025 bindings are supporting route surfaces over the Python 2025 lane, not alternate Python RTIs

Practical rule:

- treat `python1516e`, `python1516_2025`, `pitch-jpype`, `pitch-py4j`, and `certi` as route names you choose at the edge
- do not start by reasoning about shim packages unless you are editing bridge or compatibility code

At the package level:

- `hla.rti1516e` is the IEEE 1516.1-2010 API package
- `hla.rti1516_2025` is the IEEE 1516.1-2025 API package
- `hla.rti` owns cross-version discovery and ambassador creation
- the repo also contains backend, transport, vendor, bridge, FOM, and verification packages

The repo is large. The right way to approach it is by lane, not by reading
everything.

## Main Commands

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

## Read Next

Start with these:

- [`docs/repo_green_quickstart.md`](docs/repo_green_quickstart.md): one-page junior path to repo green
- [`docs/onboarding.md`](docs/onboarding.md): choose the right path for your goal
- [`docs/first_run.md`](docs/first_run.md): shortest fresh-checkout walkthrough
- [`docs/python_environment.md`](docs/python_environment.md): fuller environment and install story

Read [`docs/first_run.md`](docs/first_run.md) for the direct `python1516e`
bootstrap lane.

## Common Tasks

If you need a specific lane or deeper task guide:

- repo-green failure diagnosis: [`docs/junior_test_diagnosis_runbook.md`](docs/junior_test_diagnosis_runbook.md)
- lane and focused-target map: [`docs/test_surface.md`](docs/test_surface.md)
- repo mental model: [`docs/repo_mental_model.md`](docs/repo_mental_model.md)
- runtime editing: [`docs/python_rti_edit_one_service.md`](docs/python_rti_edit_one_service.md)
- package structure and imports: [`docs/package_layout.md`](docs/package_layout.md), [`docs/import_boundary_rules.md`](docs/import_boundary_rules.md)
- FOM tooling: [`docs/fom_workbench.md`](docs/fom_workbench.md)
- two-federate flow: [`docs/two_federate_quickstart.md`](docs/two_federate_quickstart.md)
- Java bridge work: [`docs/java_bridge_minimal_protocol_recipe.md`](docs/java_bridge_minimal_protocol_recipe.md), [`docs/java_bridge_wrapping_guide.md`](docs/java_bridge_wrapping_guide.md), [`docs/java_rti_adaptation_architecture.md`](docs/java_rti_adaptation_architecture.md)
- package inventory: [`packages/README.md`](packages/README.md)
- full docs index: [`docs/README.md`](docs/README.md)

## 2025 Verification Lanes

For the main 2025 Python RTI proof lanes:

- Use `verify-main-2025` as the default direct `python1516_2025` proof lane.
- Run `./tools/python verify-main-2025` for the default direct `python1516_2025` proof lane.
- Use `verify-routes-2025` when you also need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane over `hla-backend-python1516-2025`.
- Run `./tools/python verify-routes-2025` when you also need the bounded hosted `python1516_2025-fedpro-grpc` route lane.
- Accepted runtime spellings: `python1516_2025`, `python-1516-2025`, `python-1516-2025`.

## Repository Layout

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

## Default Reading Order

1. [`docs/onboarding.md`](docs/onboarding.md)
2. [`docs/repo_green_quickstart.md`](docs/repo_green_quickstart.md)
3. [`docs/first_run.md`](docs/first_run.md)
4. [`docs/python_environment.md`](docs/python_environment.md)
