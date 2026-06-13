# Human Editability Smell Inventory

This inventory captures the current contributor-facing surface before the repo
finishes the human-editability and traceability program.

Use it as the baseline for `./tools/human-editability inventory` and
`./tools/human-editability check`.

## Current Entrypoints

- `./tools/bootstrap`: workspace bootstrap and doctor flow
- `./tools/python`: canonical Python verification wrapper
- `./tools/test`: direct pytest wrapper
- `./tools/target-radar`: target/radar proof and matrix flow
- `./tools/two-federate`: generic two-federate artifact flow
- `./tools/compliance`: generated compliance and discovery flow
- `./tools/package-deps`: generated package dependency tree flow
- `./tools/rti-options`: generated RTI route and options matrix flow
- `./tools/human-editability`: human-editability inventory, checks, and early
  trace lookup surface

## Package Hierarchy

- `packages/hla2010-spec/src/hla2010/`: abstract or core API plus the
  documented temporary `hla2010.rti` root facade
- `packages/hla2010-spec`: installable core spec package with package-owned
  code under `packages/hla2010-spec/src/hla2010/`
- `packages/hla2010-rti-backend-common`: shared runtime and backend support
- `packages/hla2010-rti-python`: pure Python RTI backend
- `packages/hla2010-rti-transport-*`: transport implementations
- `packages/hla2010-rti-java-*`, `packages/hla2010-rti-certi`,
  `packages/hla2010-rti-pitch-*`, `packages/hla2010-rti-portico`: optional
  Java or vendor-backed routes
- `packages/hla2010-fom-target-radar`: package-owned FOM and scenario example
- `packages/hla2010-verification-harness`: shared verification helpers

## Public Interfaces

- `hla2010.spec`
- `hla2010.runtime_api`
- `hla2010.api`
- `hla2010.rti` as the only documented temporary root facade
- `hla2010_rti_python`
- `hla2010_rti_transport_grpc`
- `hla2010_fom_target_radar.scenarios`

## Backend Implementations

- Python RTI backend under
  `packages/hla2010-rti-python/src/hla2010_rti_python/`
- Runtime-common and backend-common support under
  `packages/hla2010-rti-runtime-common/src/` and
  `packages/hla2010-rti-backend-common/src/`
- Java and vendor bridges under split package roots, not the root `hla2010`
  namespace

## FOM And Example Packages

- `packages/hla2010-fom-target-radar`
- `packages/hla2010-fom-minimal-demo`
- `examples/target_radar_simulation.py`
- `examples/backend_recording.py`
- `examples/minimal_fom_demo.py`

## Traceability Assets

- `requirements/traceability_matrix.csv`
- `analysis/compliance/requirements_ledger.csv`
- `analysis/compliance/verification_traceability.csv`
- `analysis/compliance/requirements_matrix_2010.csv`

These assets are useful, but active rows still contain stale implementation
paths only when the validator or generated ledgers have not yet been refreshed.
Active contributor-facing files are now guarded by the traceability validator.

## Generated Artifacts

- `analysis/compliance/*.csv`
- `analysis/compliance/*.json`
- `analysis/compliance/*.md`
- `analysis/traceability/service_trace_index.csv`
- `analysis/traceability/service_trace_index.md`
- `analysis/traceability/service_trace_index.json`
- `analysis/traceability/runtime_method_index.md`
- `docs/package_dependency_tree.md`
- `docs/rti_options_and_test_matrix.md`

The repo now generates a contributor-facing service trace index, a runtime
method index, and a Python RTI service map. The first-run path also now carries
an expected-output artifact for the canonical Target/Radar smoke route.

## Known Smells

| ID | Status | Summary | Current evidence | Planned closure |
| --- | --- | --- | --- | --- |
| `SMELL-TRACE-STALE-IMPLEMENTATION-PATHS` | closed | Active traceability rows are now validated against current split-package implementation paths. | `scripts/validate_traceability_paths.py`, `tests/requirements/test_traceability_paths.py` | guarded by Workstream 1 |
| `SMELL-TRACE-NO-SERVICE-TRACE-INDEX` | closed | A generated contributor-facing service trace index and human guide now exist. | `analysis/traceability/service_trace_index.*`, `docs/requirements_traceability.md` | guarded by Workstream 1 |
| `SMELL-API-METADATA-BASE64-BLOB` | closed | API metadata now lives in a plain source file with generated Python outputs and a check mode. | `specs/hla2010_api.json`, `scripts/generate_api_metadata.py`, `tests/spec/test_api_metadata_source.py` | guarded by Workstream 2 |
| `SMELL-RUNTIME-DUNDER-ROUTING` | closed | Public runtime and callback surfaces are explicit and indexed; no dunder routing or abstract-method patching remains in maintained runtime files. | `packages/hla2010-spec/src/hla2010/runtime_api.py`, `packages/hla2010-spec/src/hla2010/_spec_impl.py`, `packages/hla2010-rti-backend-common/src/hla2010_rti_backend_common/recording.py`, `analysis/traceability/runtime_method_index.md` | guarded by Workstream 3 |
| `SMELL-PYTHON-RTI-SERVICE-LOCATIONS-HIDDEN` | closed | Python RTI service locations are now indexed in a stable generated registry and service map. | `packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py`, `analysis/traceability/python_rti_service_map.*`, `docs/python_rti_backend.md` | guarded by Workstream 4 |
| `SMELL-FIRST-RUN-CANONICAL-PATH-AMBIGUOUS` | closed | The canonical pure-Python first-run path now matches the real bootstrap contract and has an executable onboarding guard. | `docs/first_run.md`, `docs/examples/target_radar_python_expected_output.txt`, `tests/onboarding/test_first_run_commands.py` | guarded by Workstream 5 |
| `SMELL-FOM-FEDERATE-TEMPLATE-MISSING` | closed | A package-backed minimal demo, tutorial, and executable test path now exist for creating a new federate plus new FOM without backend edits. | `packages/hla2010-fom-minimal-demo`, `docs/create_federate_and_fom.md`, `tests/examples/test_minimal_fom_demo.py` | guarded by Workstream 6 |
| `SMELL-JAVA-BACKEND-QUICKSTART-NOT-CANONICAL` | closed | Java backend guidance now lives in one Python-first quickstart, one decision tree, and bridge README files with concrete install and failure-mode notes. | `docs/java_backends_quickstart.md`, `docs/backend_decision_tree.md`, JPype and Py4J README files | guarded by Workstream 7 |
| `SMELL-PACKAGE-HIERARCHY-RULES-DUPLICATED` | closed | The package graph YAML now drives generated docs, analysis artifacts, validator checks, and the package dependency/import-isolation tests. | `packages/package_graph.yaml`, `analysis/package_graph.json`, `scripts/validate_package_graph.py` | guarded by Workstream 8 |
| `SMELL-SPEC-SOURCE-ROOT-EXCEPTION` | closed | `hla2010-spec` now owns its code under `packages/hla2010-spec/src/hla2010/`, and bootstrap plus pytest source-checkout paths point at the package-local root. | root `pyproject.toml`, `packages/hla2010-spec/pyproject.toml`, `packages/hla2010-spec/src/hla2010`, `docs/plans/hla2010_spec_source_root_migration.md` | guarded by Workstream 9 |
| `SMELL-ONBOARDING-HIERARCHY-NOT-CANONICAL` | closed | The docs tree now has one short, opinionated onboarding map and doc-consistency coverage for the intended reader path. | `docs/onboarding.md`, `docs/README.md`, `docs/documentation_hierarchy.md`, `tests/test_documentation_policy.py` | guarded by Workstream 10 |
| `SMELL-SCRIPT-ROOT-SNIFFING-TEST-DISABLED` | closed | The script self-location policy is now enforced through an explicit allowlist plus a non-allowlisted regression check. | `tests/test_namespace_policy.py` | guarded by Workstream 11 |
| `SMELL-REMOVED-ROOT-FACADES-REGRESSION-GUARD` | closed | Removed root facade regressions already have a guard. | `tests/test_root_facade_policy.py` | keep guarded |
| `SMELL-PACKAGE-DYNAMIC-EXPORTS-REGRESSION-GUARD` | closed | Maintained package code already forbids dynamic exports and package walking. | `tests/test_namespace_policy.py` | keep guarded |
| `SMELL-PACKAGE-REPO-ROOT-SNIFFING-REGRESSION-GUARD` | closed | Installable package code already forbids repo-root sniffing. | `tests/test_namespace_policy.py` | keep guarded |

## Tests Already Guarding Smells

- `tests/test_root_facade_policy.py`: removed root facade regression guard
- `tests/test_namespace_policy.py`: package `sys.path` mutation, dynamic export,
  wildcard facade, removed compatibility import, and repo-root sniffing guards
- `tests/test_operator_surface_policy.py`: canonical operator wrapper surface
- `tests/test_documentation_policy.py`: newcomer docs and canonical navigation
- `tests/test_package_dependency_metadata.py`: internal dependency rule guard
- `tests/test_package_import_isolation.py`: cross-package import isolation guard

## Gaps Not Yet Guarded

- no remaining open human-editability smells in the current finish-line inventory
