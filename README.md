# Sturdy Broccoli

This repository is a Python-first IEEE HLA workspace.

It gives you:

- installable IEEE HLA API packages for 2010 and 2025
- Python RTI implementation lanes for both editions
- vendor, bridge, hosted, and transport-backed RTI routes
- runnable examples, FOM tooling, and verification lanes

The two other major top-level reading areas are:

- `Testing`: how to get repo green, choose the right lane, and rerun failures cheaply
- `Requirements`: what is claimed, what is proven, and which evidence packet or bounded proof note supports it

The front door is route-oriented:

- use `./tools/...` commands for operator workflows
- use `hla.rti`, `hla.rti1516e`, and `hla.rti1516_2025` for code-facing RTI entrypoints
- use `hla.backends.python1516_2025` for the main Python RTI backend for IEEE 1516.1-2025
- pass backend or route names such as `python1516e`, `python1516_2025`, `pitch-jpype`, or `certi` as selector strings

Those names are lookup strings that select a route. They are not all separate RTI
implementations.

## Start Here

### Get Repo Green

If you want the shortest path to repo green:

```bash
./tools/bootstrap doctor
./tools/bootstrap python
source .venv/bin/activate
./tools/test-surface validate
./tools/python verify-smoke
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

- `hla-backend-python1516-2025` is the main full executable Python RTI implementation lane
- `python1516_2025` is the main Python RTI implementation lane for IEEE 1516.1-2025
- `hla-backend-shim` and `hla.backends.shim` are legacy compatibility shim layers, not separate RTI families
- Java and C++ 2025 binding routes are supporting route surfaces over the Python 2025 lane, not alternate Python RTIs

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
- `./tools/shim-routes cpp doctor`
- `./tools/pitch preflight`
- `./tools/vendor-green matrix`

## Read Next

Start with these:

- [`docs/repo_green_quickstart.md`](docs/repo_green_quickstart.md): one-page junior path to repo green
- [`docs/onboarding.md`](docs/onboarding.md): choose the right path for your goal
- [`docs/first_run.md`](docs/first_run.md): shortest fresh-checkout walkthrough
- [`docs/python_environment.md`](docs/python_environment.md): fuller environment and install story
- [`docs/test_surface.md`](docs/test_surface.md): lane map and shard selection front door
- [`docs/requirements/ieee-1516-2010/README.md`](docs/requirements/ieee-1516-2010/README.md): requirements and proof front door for the 2010 requirement surface
- [`docs/requirements/ieee-1516-2025/README.md`](docs/requirements/ieee-1516-2025/README.md): requirements and proof front door for the 2025 requirement surface

Read [`docs/first_run.md`](docs/first_run.md) for the direct `python1516e`
bootstrap lane.

## Testing

Treat testing as its own top-level reading surface.

Start here, in order:

1. [`docs/repo_green_quickstart.md`](docs/repo_green_quickstart.md): shortest path to repo green
2. [`docs/test_surface.md`](docs/test_surface.md): every named lane and shard, including `matrix`
3. [`docs/local_verification_commands.md`](docs/local_verification_commands.md): exact commands
4. [`docs/junior_test_diagnosis_runbook.md`](docs/junior_test_diagnosis_runbook.md): failure restart path

Top-level testing commands that matter:

- `./tools/test-surface recommend`
- `./tools/test-surface run repo-green-units`
- `./tools/test-surface run matrix`
- `./tools/python verify-smoke`
- `./tools/python verify-fast`
- `./tools/python verify`
- `./tools/python verify-main-2025`
- `./tools/python verify-routes`
- `./tools/python verify-routes-2025`

Use [`docs/test_surface.md`](docs/test_surface.md) when the question is which
lane to run. Use [`docs/local_verification_commands.md`](docs/local_verification_commands.md)
when the question is the exact command list.

## Requirements

Treat requirements and proof as their own top-level reading surface.

Start here, in order:

1. [`docs/requirements/ieee-1516-2025/README.md`](docs/requirements/ieee-1516-2025/README.md): current requirement-facing claim map
2. [`docs/requirements/ieee-1516-2010/README.md`](docs/requirements/ieee-1516-2010/README.md): 2010 requirement-facing claim map
3. [`docs/verification/README.md`](docs/verification/README.md): proof and generated-evidence index
4. [`docs/spec_reading_map.md`](docs/spec_reading_map.md): standards-facing reading order and traceability path

Use this reading surface when the question is:

- what does the repo claim?
- what is bounded versus out of scope?
- where is the proof for a capability family?
- which requirement-facing note should I read first?

## Common Tasks

If you need a specific lane or deeper task guide:

- three main work surfaces: [`docs/work_surfaces.md`](docs/work_surfaces.md)
- testing front doors: [`docs/repo_green_quickstart.md`](docs/repo_green_quickstart.md), [`docs/test_surface.md`](docs/test_surface.md), [`docs/junior_test_diagnosis_runbook.md`](docs/junior_test_diagnosis_runbook.md)
- requirements and proof front doors: [`docs/requirements/ieee-1516-2010/README.md`](docs/requirements/ieee-1516-2010/README.md), [`docs/requirements/ieee-1516-2025/README.md`](docs/requirements/ieee-1516-2025/README.md), [`docs/verification/README.md`](docs/verification/README.md), [`docs/spec_reading_map.md`](docs/spec_reading_map.md)
- repo-green failure diagnosis: [`docs/junior_test_diagnosis_runbook.md`](docs/junior_test_diagnosis_runbook.md)
- Pitch + Docker first-run path: [`docs/pitch_docker_first_run.md`](docs/pitch_docker_first_run.md)
- lane and focused-target map: [`docs/test_surface.md`](docs/test_surface.md)
- repo mental model: [`docs/repo_mental_model.md`](docs/repo_mental_model.md)
- runtime editing: [`docs/python_rti_edit_one_service.md`](docs/python_rti_edit_one_service.md)
- package structure and imports: [`docs/package_layout.md`](docs/package_layout.md), [`docs/import_boundary_rules.md`](docs/import_boundary_rules.md)
- FOM tooling: [`docs/fom_workbench.md`](docs/fom_workbench.md)
- transport options and extension: [`docs/extending_ambassador_transports.md`](docs/extending_ambassador_transports.md), [`docs/transport_extension_playbook.md`](docs/transport_extension_playbook.md)
- two-federate flow: [`docs/two_federate_quickstart.md`](docs/two_federate_quickstart.md)
- standard Java/C++ shim route setup: [`docs/java_toolchain.md`](docs/java_toolchain.md), [`docs/cpp_toolchain.md`](docs/cpp_toolchain.md), [`docs/language_shim_routes.md`](docs/language_shim_routes.md)
- Java bridge work: [`docs/java_bridge_minimal_protocol_recipe.md`](docs/java_bridge_minimal_protocol_recipe.md), [`docs/java_bridge_wrapping_guide.md`](docs/java_bridge_wrapping_guide.md), [`docs/java_bridge_overload_resolution.md`](docs/java_bridge_overload_resolution.md), [`docs/java_rti_adaptation_architecture.md`](docs/java_rti_adaptation_architecture.md)
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
3. run one verification lane
4. read one requirements or proof packet
5. trace one service
6. work on FOM tooling

The repo becomes manageable once the scope is that small.

## Default Reading Order

1. [`docs/onboarding.md`](docs/onboarding.md)
2. [`docs/repo_green_quickstart.md`](docs/repo_green_quickstart.md)
3. [`docs/first_run.md`](docs/first_run.md)
4. [`docs/python_environment.md`](docs/python_environment.md)
