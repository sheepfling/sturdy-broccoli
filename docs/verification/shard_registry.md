# Verification Shard Registry

Use this page when the question is:

- which runnable shard actually owns this proof?
- which shard gates repo-green?
- which stable command should I rerun after a change?

This is the canonical shard registry for the current repo-owned verification
surface.

Read it together with:

- [`../test_surface.md`](../test_surface.md) for the operator-facing lane map
- [`view_registry.md`](view_registry.md) for overlapping views and focused
  rerun slices
- [`../plans/requirements_remaining_closure.md`](../plans/requirements_remaining_closure.md)
  for requirement-facing shard ownership and backend-resolution rules

## Rules

Treat these statements as hard rules:

1. shards are the canonical runnable ownership units
2. every shard must have a stable command
3. every shard must have a clear pass/fail meaning
4. repo-green is composed from shards, not from overlapping views
5. requirement status changes should point at the narrowest owning shard that
   justified the change
6. backend divergence must stay in backend-resolution columns or companion
   artifacts, not in shard names

## Repo-Green Gating Model

Use this reading:

- `repo-green` is the default local green claim
- `repo-green-units` is the composite shard sweep that explains the unit-level
  ownership behind that claim
- broader lanes such as `python1516_2025-main`, `python1516_2025-routes`,
  `vendor`, and `matrix` are important, but they are not the same thing as the
  default unit shard gate

Current `repo-green-units` membership from
[`../../testing/test_surface_manifest.json`](../../testing/test_surface_manifest.json):

1. `unit-foundation`
2. `unit-python-core`
3. `unit-federate-examples`
4. `unit-vendor-onboarding`
5. `unit-shim-tooling`
6. `unit-fom-tooling`
7. `unit-python-2025-core`
8. `unit-transport-local`
9. `unit-scenarios-light`

If shard order or membership changes, update the manifest first and then update
this doc.

## Composite Lanes

These are still shards or composed lanes because they have stable commands and
clear execution meaning.

| Lane | Primary command | Role | Repo-green gate |
| --- | --- | --- | --- |
| `smoke` | `./tools/python verify-smoke` | cheapest structural and wrapper smoke lane | no |
| `fast` | `./tools/python verify-fast` | low-cost operator, docs, and policy lane | no |
| `repo-green` | `./tools/python verify` | default local green lane | yes |
| `repo-green-units` | `./tools/test-surface run repo-green-units` | composite unit shard sweep for the repo-green unit phase | yes |
| `python1516_2025-main` | `./tools/python verify-main-2025` | direct 2025 Python RTI proof lane | no |
| `python-routes` | `./tools/python verify-routes` | hosted 2010 Python route hygiene lane | no |
| `python1516_2025-routes` | `./tools/python verify-routes-2025` | hosted 2025 route hygiene and parity lane | no |
| `vendor` | `./tools/vendor-green matrix` | real-runtime vendor lane after preflight | no |
| `matrix` | `./tools/test-surface run matrix` | artifact-refresh and broader matrix lane | no |

## Unit Shards

These are the main independently runnable unit shards.

| Shard | Primary command | Alias hints | Main ownership | Typical use |
| --- | --- | --- | --- | --- |
| `unit-foundation` | `./tools/test-surface run unit-foundation` | `foundation` | wrapper policy, docs policy, manifest structure, package boundaries | cheapest first signal after structural changes |
| `unit-python-core` | `./tools/test-surface run unit-python-core` | `python-core` | direct Python examples and RTI-core helpers | cheap core-runtime rerun |
| `unit-federate-examples` | `./tools/test-surface run unit-federate-examples` | `examples` | federate CLI, walkthrough, TUI, and example-help surface | interactive operator regressions |
| `unit-vendor-onboarding` | `./tools/test-surface run unit-vendor-onboarding` | `onboarding` | Pitch/CERTI onboarding docs, preflight contracts, and wrapper entrypoints | newcomer vendor-setup regressions |
| `unit-shim-tooling` | `./tools/test-surface run unit-shim-tooling` | `shim-tooling` | Java/C++ toolchain doctors, shim docs, and standard-shim artifacts | Java/C++ setup or artifact regressions |
| `unit-fom-tooling` | `./tools/test-surface run unit-fom-tooling` | `fom` | FOM parsing, validation, workbench, and packaged factories | FOM/tooling regressions |
| `unit-python-2025-core` | `./tools/test-surface run unit-python-2025-core` | `python-2025` | direct `python1516_2025` unit semantics and validation helpers | 2025 runtime-only regressions |
| `unit-transport-local` | `./tools/test-surface run unit-transport-local` | `transport` | hosted gRPC/REST transport behavior without vendor runtime | route-wiring regressions |
| `unit-scenarios-light` | `./tools/test-surface run unit-scenarios-light` | `scenarios` | Target/Radar and scenario-level backend integration | scenario composition regressions |
| `unit-scenarios-visualizer` | `./tools/test-surface run unit-scenarios-visualizer` | none | SISO observer, visualizer, bridge, and hydrated artifact coverage | visualizer hydration or observer artifact regressions |

## Requirement-Oriented Shard Ownership

Use this quick map when a requirements owner doc needs a runnable proof owner:

| Requirement concern | Preferred shard first | Widen to |
| --- | --- | --- |
| docs policy, wrapper policy, manifest drift | `unit-foundation` | `repo-green` |
| Java/C++ setup or shim readiness | `unit-shim-tooling` | `repo-green` |
| hosted gRPC/REST route behavior | `unit-transport-local` | `python1516_2025-routes` |
| direct `python1516_2025` runtime behavior | `unit-python-2025-core` | `python1516_2025-main` |
| FOM parsing, validation, workbench, and packaged factories | `unit-fom-tooling` | `python1516_2025-main` |
| scenario-backed proof such as Target/Radar | `unit-scenarios-light` | `python1516_2025-main` or `python1516_2025-routes` |
| onboarding and preflight contracts | `unit-vendor-onboarding` | `vendor` |

## Update Rule

When a shard changes:

1. update `testing/test_surface_manifest.json`
2. update [`../test_surface.md`](../test_surface.md)
3. update this registry
4. update any owner docs or runbooks that depend on the shard alias or command

## Related Docs

- [`../test_surface.md`](../test_surface.md)
- [`view_registry.md`](view_registry.md)
- [`../repo_green_quickstart.md`](../repo_green_quickstart.md)
- [`../junior_test_diagnosis_runbook.md`](../junior_test_diagnosis_runbook.md)
- [`../plans/PLN-005_requirements_shards_views_and_verification_plan.md`](../plans/PLN-005_requirements_shards_views_and_verification_plan.md)
