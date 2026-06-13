# Human Editability + Traceability Finish Line

This note defines the finish line for making the repo human-editable,
traceable, and difficult to regress.

It is not enough for the docs to explain the smells. The repo needs tests,
scripts, generated indexes, and operator commands that make the smells hard to
reintroduce.

The current direction is already sound. The README names the intended front
doors as `hla2010.spec`, `hla2010.runtime_api`, `hla2010_rti_python`,
`hla2010_rti_transport_grpc`, and
`hla2010_fom_target_radar.scenarios`. The package layout already says the repo
root is tooling-only, `hla2010-spec` owns the abstract or core API, split
packages own concrete implementations, and `hla2010.rti` is the only temporary
root facade. This plan turns that target architecture into enforceable,
contributor-facing products.

## Finish Definition

The repo is human-editable when a new contributor can do all of the following
without guessing:

1. bootstrap the repo and run the pure Python RTI example
2. identify the public interfaces and backend interfaces
3. create a new federate and new FOM without touching core or backend internals
4. run the new federate or FOM against the Python RTI first
5. understand the optional Java backend path at a simple operational level
6. trace a requirement to implementation, tests, and generated artifacts
7. trace an implementation function back to requirement rows and proof
8. verify that no package relies on path sniffing, dynamic `__all__`, wildcard
   facades, root backend facades, or hidden import tricks

## Workstream 0: Baseline Inventory And Do-Not-Regress Gate

### Goal

Before changing structure, capture what exists and make the current smells
measurable.

### Deliverables

#### 0.1 Add a smell inventory document

Create `docs/plans/human_editability_smell_inventory.md` with these sections:

- current entrypoints
- package hierarchy
- public interfaces
- backend implementations
- FOM and example packages
- traceability assets
- generated artifacts
- known smells
- tests already guarding smells
- gaps not yet guarded

#### 0.2 Add a machine-readable smell checklist

Create `analysis/human_editability/smell_inventory.json`.

Example shape:

```json
{
  "version": 1,
  "checks": [
    {
      "id": "SMELL-TRACE-STale-IMPLEMENTATION-PATHS",
      "status": "open",
      "owner_area": "requirements",
      "evidence": [
        "requirements/traceability_matrix.csv"
      ]
    }
  ]
}
```

#### 0.3 Add a verification wrapper

Create `tools/human-editability`.

Supported commands:

```text
./tools/human-editability check
./tools/human-editability inventory
./tools/human-editability trace createFederationExecution
./tools/human-editability trace timeAdvanceRequest
```

Internally, this can call scripts under `scripts/` so `tools/` remains the
human operator surface. That matches the repo convention that `tools/` is the
canonical human-facing entrypoint directory.

### Tests

Add `tests/architecture/test_human_editability_inventory.py`.

Required checks:

- every smell row has an ID
- every open smell has a planned remediation workstream
- every closed smell has at least one verification command or test
- `./tools/human-editability check` can run in CI

### Done Means

This workstream is done when the repo can answer `./tools/human-editability
check` and produce a clear list of remaining smells with IDs, owner areas, and
remediation targets.

## Workstream 1: Requirement Traceability Repair

### Goal

Make requirement to implementation to test to artifact traceability real, not
aspirational.

This is the highest-priority workstream because the existing traceability
matrix still points at stale implementation paths such as
`hla2010/backends/python/federation_lifecycle.py`, while the current Python RTI
implementation lives under
`packages/hla2010-rti-python/src/hla2010_rti_python/`.

### Deliverables

#### 1.1 Add a traceability path validator

Create `scripts/validate_traceability_paths.py`.

It validates:

- `requirements/traceability_matrix.csv`
- `analysis/compliance/requirements_ledger.csv`
- other `requirements/*.csv` files that contain implementation, test, or
  artifact refs

Validation rules:

- `implementation_refs` must point to existing files, classes, functions, or
  explicit generated or external markers
- `test_refs` must point to existing files or `file.py::test_name` anchors
- `artifact_refs` must point to existing artifacts or explicitly generated
  outputs
- stale root paths like `hla2010/backends/python/...` are forbidden unless they
  are in historical or provenance docs
- broad rows marked `mapped` or `partial` must have concrete evidence anchors

The repo already states the honest-test rule: `mapped` or `partial` rows need
positive tests, negative tests, or generated artifacts as concrete evidence.
The validator makes that executable.

#### 1.2 Add a generated service trace index

Create:

- `analysis/traceability/service_trace_index.csv`
- `analysis/traceability/service_trace_index.md`
- `analysis/traceability/service_trace_index.json`

Required columns:

- `requirement_id`
- `section`
- `service_group`
- `hla_method`
- `python_name`
- `implementation_ref`
- `backend_package`
- `test_refs`
- `artifact_refs`
- `status`
- `notes`

#### 1.3 Add a human trace guide

Create `docs/requirements_traceability.md`.

It must show exact examples for:

- `createFederationExecution`
- `joinFederationExecution`
- `timeAdvanceRequest`
- `reflectAttributeValues`
- `requestAttributeValueUpdate`
- `timeAdvanceGrant`

For each example show:

- requirement row
- spec reference
- Python public method
- backend service
- test
- artifact

#### 1.4 Repair stale paths

Update requirement and compliance rows from old root paths to current
package-owned paths.

Example:

```text
OLD: hla2010/backends/python/federation_lifecycle.py
NEW: packages/hla2010-rti-python/src/hla2010_rti_python/federation_lifecycle.py
```

Where the implementation is split across mixins, point to the exact module and
`_svc_*` function.

### Tests

Add `tests/requirements/test_traceability_paths.py`.

Required checks:

- all refs in `requirements/traceability_matrix.csv` resolve
- all refs in `analysis/compliance/requirements_ledger.csv` resolve
- no stale `hla2010/backends/python` paths remain in active traceability files
- every `mapped` row has at least one test or generated artifact
- every `partial` row has a supported-boundary note

### Done Means

This is done when a contributor can run
`./tools/human-editability trace timeAdvanceRequest` and see:

- requirement ID
- IEEE section
- public RTI method
- Python snake_case method
- backend implementation function
- test evidence
- generated artifact evidence
- status

No stale active traceability path may remain.

## Workstream 2: Externalize API Metadata And Stop Hiding Specs In Blobs

### Goal

Make the HLA API inventory editable and reviewable.

Currently, `src/hla2010/raw_api.py` stores `API_METADATA` as base64-decoded
JSON. That is not human-editable. It should become generated code from a plain
source file.

### Deliverables

#### 2.1 Create a plain API metadata source file

Create one canonical source:

- `specs/hla2010_api.yaml`, or
- `specs/hla2010_api.json`

Recommended shape:

```yaml
interfaces:
  RTIambassador:
    createFederationExecution:
      python_name: create_federation_execution
      section: "4.5"
      service_group: Federation Management
      title: Create Federation Execution service
      overloads:
        - language: java
          source_file: apis/java/java/src/hla/rti1516e/RTIambassador.java
          source_line: 79
          return_type: void
          params:
            - name: federationExecutionName
              type: String
            - name: fomModules
              type: URL[]
          throws:
            - FederationExecutionAlreadyExists
            - CouldNotOpenFDD
```

#### 2.2 Generate current Python metadata files

Generate:

- `src/hla2010/raw_api.py`
- `src/hla2010/spec_inventory.py`
- `src/hla2010/spec_refs.py`
- `src/hla2010/spec_sources.py`

`raw_api.py` should contain ordinary Python data or load a package resource. It
should not contain base64-encoded source metadata.

#### 2.3 Add generator and check mode

Create:

- `scripts/generate_api_metadata.py`
- `tools/spec-api`

Supported commands:

```text
./tools/spec-api generate
./tools/spec-api check
```

#### 2.4 Add generated headers

Every generated file gets this header:

```python
# Generated from specs/hla2010_api.yaml.
# Do not edit by hand. Run ./tools/spec-api generate.
```

### Tests

Add `tests/spec/test_api_metadata_source.py`.

Required checks:

- YAML or JSON parses
- every RTI method has `python_name`
- every method has a spec section or an explicit `no_section` reason
- generated `spec_inventory.py` matches source
- generated `spec_refs.py` matches source
- generated `raw_api.py` matches source
- no base64 metadata blob remains in `raw_api.py`

### Done Means

A reviewer can inspect API metadata in a normal diff. No one has to decode a
string to update interface specs.

## Workstream 3: Replace Runtime Dunder Magic With Explicit Generated Methods

### Goal

Make the runtime adapter visible to static tools and human readers.

The backend-common adapter currently uses `__getattribute__` to redirect
snake_case names and then clears `__abstractmethods__`. That is clever, but it
is a human-editability smell.

### Deliverables

#### 3.1 Generate explicit delegating methods

Generate or hand-maintain explicit methods for:

- `DelegatingRTIAmbassador`
- `RTIambassador`
- `RTIambassadorSpec`
- `FederateAmbassadorSpec`

For every RTI method:

```python
def time_advance_request(self, *args: Any, **kwargs: Any) -> Any:
    return self.timeAdvanceRequest(*args, **kwargs)

def timeAdvanceRequest(self, *args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return self._invoke("timeAdvanceRequest", *args, **kwargs)
```

#### 3.2 Remove `__abstractmethods__` mutation

`DelegatingRTIAmbassador` should become concrete because it explicitly
implements the abstract surface, not because the class is patched.

#### 3.3 Add explicit method index docs

Create `analysis/traceability/runtime_method_index.md`.

Rows:

- `hla_method`
- `python_name`
- `interface`
- `runtime_class`
- `backend_invocation_name`
- `generated_from`

### Tests

Add `tests/spec/test_runtime_methods_are_explicit.py`.

Required checks:

- no `__abstractmethods__ =` mutation in public runtime code
- no `__getattribute__` method routing in public runtime classes
- every RTI method from API metadata has explicit camelCase and snake_case
  methods
- every `FederateAmbassador` callback has explicit camelCase and snake_case
  surface
- `inspect.getsource()` for a method points to a real method body

### Done Means

Searching for `time_advance_request`, `timeAdvanceRequest`, or
`createFederationExecution` lands on an explicit method body, not a hidden
dunder router.

## Workstream 4: Make Python RTI Service Implementation Traceable

### Goal

Make the Python RTI the obvious backend playground and make every service
implementation findable.

The Python backend already dispatches services dynamically with:

```python
getattr(self, f"_svc_{invocation.method_name}")
```

That can stay internally, but humans need an index and tests proving the map.

### Deliverables

#### 4.1 Create a service implementation registry

Create
`packages/hla2010-rti-python/src/hla2010_rti_python/service_registry.py`.

Example:

```python
PYTHON_RTI_SERVICE_REGISTRY: dict[str, str] = {
    "createFederationExecution": (
        "hla2010_rti_python.federation_lifecycle."
        "PythonRTIFederationMixin._svc_createFederationExecution"
    ),
    "joinFederationExecution": (
        "hla2010_rti_python.federation_lifecycle."
        "PythonRTIFederationMixin._svc_joinFederationExecution"
    ),
}
```

The registry may be generated from introspection, but the artifact must be
stable and reviewable.

#### 4.2 Generate a Python RTI service map

Create:

- `analysis/traceability/python_rti_service_map.csv`
- `analysis/traceability/python_rti_service_map.md`
- `analysis/traceability/python_rti_service_map.json`

Required columns:

- `hla_method`
- `python_name`
- `service_group`
- `implementation_module`
- `implementation_symbol`
- `requirement_ids`
- `positive_tests`
- `negative_tests`
- `status`

#### 4.3 Add `docs/python_rti_backend.md`

Required sections:

- what the Python RTI is
- when to use it
- backend package location
- service domain modules
- how invocation dispatch works
- how to add a service
- how to test a service
- how to link the service to requirements
- how to run it directly
- how to run it hosted over gRPC

The existing route inventory already says the direct Python RTI is green and
the Python RTI hosted over gRPC is also green. This doc should make those the
normal development routes.

### Tests

Add `tests/backends/test_python_rti_service_registry.py`.

Required checks:

- every RTI method in API metadata has a registry entry
- every registry entry resolves to a real callable
- every `_svc_*` function has a registry entry or explicit private reason
- every service has at least one requirement row or explicit unsupported or
  scope note
- `./tools/human-editability trace <method>` uses this registry

### Done Means

A new contributor can answer "Where is `requestAttributeValueUpdate`
implemented in the Python RTI?" with one command, one doc page, and one
generated artifact.

## Workstream 5: One Obvious First-Run Path

### Goal

Collapse onboarding into one clear path.

The current first-run doc tells users to bootstrap, activate `.venv`, then run
a long manual editable install command. That makes the bootstrap feel
incomplete.

### Deliverables

#### 5.1 Make bootstrap sufficient for first run

Choose one supported path:

```text
./tools/bootstrap python
source .venv/bin/activate
python examples/target_radar_simulation.py --backend python --steps 5
```

If the manual editable install is still required, make `./tools/bootstrap
python` do it or rename the manual command as a recovery or debug path.

#### 5.2 Rewrite `docs/first_run.md`

Target structure:

- goal
- prerequisites
- one command path
- expected output
- what worked
- what to run next
- troubleshooting
- what not to do first

#### 5.3 Add an executable first-run smoke test

Create `tests/onboarding/test_first_run_commands.py`.

If the full command is too slow for unit CI, split into:

- doc command parser test
- lightweight import smoke
- optional integration lane

#### 5.4 Add expected output file

Create `docs/examples/target_radar_python_expected_output.txt`.

The output does not need to match every number exactly, but the doc should show
the expected shape.

### Tests

- `./tools/bootstrap doctor`
- `./tools/bootstrap python`
- `python examples/backend_recording.py`
- `python examples/target_radar_simulation.py --backend python --steps 5`
- `./tools/test`

### Done Means

A human can run the README path and get a working Python RTI scenario without
deciding which install instructions are canonical.

## Workstream 6: New FOM Or Federate Template

### Goal

Make "create a new federate with a new FOM" a documented, test-backed
workflow.

Target or Radar already provides a strong reusable example. The package owns
the FOM resource and scenario helpers. It exports useful entrypoints such as
`make_target_radar_factory`, `run_target_radar_scenario`, and
`target_radar_fom_path`.

### Deliverables

#### 6.1 Add a tutorial

Create `docs/create_federate_and_fom.md`.

Required sections:

1. where new FOM packages belong
2. minimal package layout
3. minimal FOM XML
4. minimal publisher federate
5. minimal subscriber federate
6. run with Python RTI
7. add a test
8. add requirement rows
9. add traceability refs
10. optional: run through JPype or Py4J later

#### 6.2 Add a tiny template package

Choose one of:

- `packages/hla2010-fom-minimal-demo/`
- `examples/new_fom_package_template/`

Option A is better if it should be tested as a real package. Option B is better
if it should remain copyable scaffolding.

Minimal layout:

```text
packages/hla2010-fom-minimal-demo/
  README.md
  pyproject.toml
  src/hla2010_fom_minimal_demo/
    __init__.py
    resources/foms/MinimalDemoFOMmodule.xml
    scenarios/__init__.py
    scenarios/minimal_demo.py
```

#### 6.3 Add a generator command

Optional but useful:

```text
./tools/new-fom-package minimal-demo
```

This can produce a local scaffold but should not be required.

### Tests

Add `tests/examples/test_minimal_fom_demo.py`.

Required checks:

- packaged FOM path resolves through `importlib.resources`
- two federates can create, join, and resign against Python RTI
- publish, subscribe, update, and callback flow works
- tutorial code snippets are importable or executable

### Done Means

A contributor can copy the template, rename the FOM, implement one object and
one interaction, and run it against the Python RTI without touching backend
internals.

## Workstream 7: Java Backend Quickstart Without Making Java The Main Path

### Goal

Make Java backend notes simple, honest, and secondary to Python RTI.

The install matrix already gives the correct order: bootstrap Python first, run
a pure-Python smoke path, then add bridge extras and vendor runtimes. It also
lists the backend families and their enablement paths. The JPype and Py4J
package READMEs, however, are currently ownership notes more than practical
quickstarts.

### Deliverables

#### 7.1 Add Java backend quickstart

Create `docs/java_backends_quickstart.md`.

Required sections:

- start with Python RTI
- what Java shim means
- what JPype means
- what Py4J means
- what CERTI, Pitch, and Portico mean
- which paths require real vendor installs
- minimal JPype shape
- minimal Py4J shape
- common failure messages
- how to fall back to Python RTI

#### 7.2 Expand JPype and Py4J READMEs

Update:

- `packages/hla2010-rti-java-jpype/README.md`
- `packages/hla2010-rti-java-py4j/README.md`

Add:

- install commands
- minimal import examples
- classpath or gateway notes
- expected "no runtime found" behavior
- link back to `docs/java_backends_quickstart.md`

#### 7.3 Add backend route decision tree

Create `docs/backend_decision_tree.md`.

Example:

```text
Need to learn API? -> python
Need local multi-federate? -> python
Need process boundary? -> python + grpc
Need Java bridge mechanics only? -> java-shim
Need real vendor? -> Pitch/CERTI/Portico after preflight
```

### Tests

Add `tests/docs/test_java_quickstart_docs.py`.

Required checks:

- docs mention Python RTI first
- docs do not imply JPype or Py4J work without runtime, classpath, or gateway
  setup
- docs link to install matrix and route inventory
- examples import canonical split packages, not removed root facades

### Done Means

A human knows when Java routes are appropriate and how to start, without
confusing them with the primary Python RTI development backend.

## Workstream 8: Single Source Of Truth For Package Hierarchy

### Goal

Stop duplicating dependency policy across docs and tests.

The import-boundary tests currently hard-code package allowlists. The
dependency metadata test also hard-codes the allowed internal dependency graph.
The docs separately describe the same package hierarchy. This is understandable,
but it will drift.

### Deliverables

#### 8.1 Create package graph source

Create `packages/package_graph.yaml`.

Example:

```yaml
packages:
  hla2010-spec:
    import_root: hla2010
    layer: 0
    role: core-spec
    may_depend_on: []
  hla2010-rti-backend-common:
    import_root: hla2010_rti_backend_common
    layer: 1
    role: shared-support
    may_depend_on:
      - hla2010-spec
  hla2010-rti-python:
    import_root: hla2010_rti_python
    layer: 2
    role: backend
    backend_names:
      - python
    may_depend_on:
      - hla2010-spec
      - hla2010-rti-backend-common
```

#### 8.2 Generate docs and test fixtures from graph

Create:

- `docs/package_dependency_tree.md`
- `analysis/package_graph.json`

Tests should load the YAML rather than duplicate the rules.

#### 8.3 Validate pyprojects against graph

Create `scripts/validate_package_graph.py`.

Required checks:

- every package in `packages/*/pyproject.toml` appears in the graph
- every internal dependency is allowed
- every package import root matches package name or explicit override
- every entrypoint backend package has backend metadata
- no leaf package depends on concrete backend or vendor packages
- no transport package depends directly on concrete backend packages

### Tests

Refactor:

- `tests/test_package_import_isolation.py`
- `tests/test_package_dependency_metadata.py`

so they read `packages/package_graph.yaml`.

### Done Means

Changing dependency hierarchy requires editing one source file. Docs and tests
are generated or validated from that source.

## Workstream 9: Final Package-Root Cleanup For `hla2010-spec`

### Goal

Make every installable package physically self-contained.

Right now, `packages/hla2010-spec/pyproject.toml` packages from `../../src`,
unlike most split packages that own code under `packages/<name>/src`. This is
documented, but it remains a mental-model exception.

### Deliverables

#### 9.1 Prepare migration note

Create `docs/plans/hla2010_spec_source_root_migration.md`.

It should list:

- current package root
- current source root
- target source root
- affected imports
- affected tests
- artifact impact
- rollback plan

#### 9.2 Move source root

Move:

```text
src/hla2010/
```

to:

```text
packages/hla2010-spec/src/hla2010/
```

#### 9.3 Keep repo-internal code separate

Keep repo-internal code under `src/hla2010_repo_internal/`, or move it to
`tools/internal/` only if that does not blur package boundaries.

#### 9.4 Update `pyproject.toml`

Update:

```toml
[tool.setuptools.package-dir]
"" = "src"

[tool.setuptools.packages.find]
where = ["src"]
include = ["hla2010*"]
```

#### 9.5 Update root pytest and pythonpath configuration

The root `pyproject.toml` currently enumerates many package source roots for
pytest. Update it to the new `packages/hla2010-spec/src` path.

### Tests

- full import suite
- package isolation suite
- namespace policy suite
- docs link checker if available
- first-run smoke
- traceability validator

### Done Means

Every installable package owns code under its own `packages/<name>/src` tree,
except explicitly repo-internal tooling.

This workstream should happen late, after traceability and generated indexes
exist, because moving source before repairing traceability will make the
stale-path problem worse.

## Workstream 10: Documentation Hierarchy Cleanup

### Goal

Make the repo readable without deleting valuable evidence.

The docs already intend a start-here, reference, and historical or provenance
structure. This plan makes that unavoidable.

### Deliverables

#### 10.1 Create one onboarding map

Create `docs/onboarding.md`.

It should be short and opinionated:

1. first run
2. Python RTI backend
3. create FOM or federate
4. requirement traceability
5. Java backends later
6. full verification

#### 10.2 Move detailed docs into named families

Suggested structure:

- `docs/start/`
- `docs/architecture/`
- `docs/backends/`
- `docs/requirements/`
- `docs/verification/`
- `docs/vendor/`
- `docs/provenance/`
- `docs/plans/`

This can be done gradually with redirects or links.

#### 10.3 Add doc ownership metadata

Optional but useful:

```yaml
---
doc_family: onboarding
status: canonical
generated: false
owner_area: repo
---
```

#### 10.4 Add doc consistency tests

Required checks:

- only one doc is marked canonical first-run
- only one doc is marked canonical package hierarchy
- only one doc is marked canonical traceability guide
- historical or provenance docs do not appear in the onboarding path
- public docs do not recommend removed namespaces

The repo already has namespace-policy tests that prevent public docs from
recommending removed testing namespaces. Extend that approach to onboarding
hierarchy.

### Done Means

A new contributor can start at `docs/onboarding.md` and never see
provenance, evidence, or vendor deep-dives until they choose to go there.

## Workstream 11: Guard All Eliminated Smells

### Goal

Make closed smells stay closed.

The repo already has tests forbidding dynamic exports, package walking,
wildcard facades, runtime class injection patterns, `sys.path` mutation,
removed compatibility imports, and repo-root sniffing from package code. Keep
those, but make the policy more systematic.

### Deliverables

#### 11.1 Add architecture policy test suite

Create `tests/architecture/`.

Move or mirror architecture-specific tests there:

- `test_import_boundaries.py`
- `test_namespace_policy.py`
- `test_package_graph.py`
- `test_traceability_paths.py`
- `test_generated_sources.py`
- `test_public_docs.py`

#### 11.2 Fix suspicious disabled script-root sniffing test

The current
`test_scripts_do_not_sniff_repo_root_from_file_paths` immediately continues
inside the loop, so it does not enforce what its name suggests.

Either:

- rename it to document that operator scripts are exempt, or
- split it into:
  - operator wrappers may self-locate
  - non-operator scripts may not self-locate unless allowlisted

#### 11.3 Add one smell closure table

Create `analysis/human_editability/smell_closure_matrix.csv`.

Columns:

- `smell_id`
- `description`
- `closed_by_pr`
- `guard_test`
- `operator_command`
- `doc_anchor`
- `status`

### Done Means

Every eliminated smell has a guard test or command. No smell is marked closed
based on documentation alone.

## PR Sequence

### PR 1: Baseline + Smell Inventory

Products:

- `docs/plans/human_editability_traceability_finish_line.md`
- `docs/plans/human_editability_smell_inventory.md`
- `analysis/human_editability/smell_inventory.json`
- `tools/human-editability`
- `tests/architecture/test_human_editability_inventory.py`

Verification:

- `./tools/human-editability inventory`
- `./tools/human-editability check`
- `pytest tests/architecture/test_human_editability_inventory.py`

### PR 2: Traceability Path Validator

Products:

- `scripts/validate_traceability_paths.py`
- `tests/requirements/test_traceability_paths.py`
- repaired stale implementation refs
- generated `analysis/traceability/service_trace_index.*`
- `docs/requirements_traceability.md`

Verification:

- `./tools/human-editability trace createFederationExecution`
- `./tools/human-editability trace timeAdvanceRequest`
- `pytest tests/requirements/test_traceability_paths.py`

### PR 3: API Metadata Source Of Truth

Products:

- `specs/hla2010_api.yaml`
- `scripts/generate_api_metadata.py`
- `tools/spec-api`
- generated `raw_api.py`, `spec_inventory.py`, `spec_refs.py`,
  `spec_sources.py`
- tests proving generated files are current

Verification:

- `./tools/spec-api check`
- `pytest tests/spec/test_api_metadata_source.py`

### PR 4: Explicit Runtime Adapter Methods

Products:

- generated explicit runtime or spec methods
- no public `__abstractmethods__` mutation
- no dunder method routing for public API names
- generated runtime method index

Verification:

- `pytest tests/spec/test_runtime_methods_are_explicit.py`
- `pytest tests/test_python_api_spec.py`

### PR 5: Python RTI Service Registry

Products:

- `hla2010_rti_python/service_registry.py`
- generated Python RTI service map
- `docs/python_rti_backend.md`
- trace command integration

Verification:

- `./tools/human-editability trace requestAttributeValueUpdate`
- `pytest tests/backends/test_python_rti_service_registry.py`

### PR 6: First-Run Cleanup

Products:

- simplified `docs/first_run.md`
- expected output sample
- first-run doc command tests
- bootstrap behavior clarified or fixed

Verification:

- `./tools/bootstrap doctor`
- `./tools/bootstrap python`
- `source .venv/bin/activate`
- `python examples/target_radar_simulation.py --backend python --steps 5`
- `pytest tests/onboarding/test_first_run_commands.py`

### PR 7: New FOM Or Federate Tutorial And Template

Products:

- `docs/create_federate_and_fom.md`
- minimal demo FOM package or copyable template
- tested Python RTI demo
- traceability example row

Verification:

- `python examples/minimal_fom_demo.py --backend python`
- `pytest tests/examples/test_minimal_fom_demo.py`

### PR 8: Java Backend Quickstart

Products:

- `docs/java_backends_quickstart.md`
- expanded JPype or Py4J READMEs
- `docs/backend_decision_tree.md`
- doc tests

Verification:

- `pytest tests/docs/test_java_quickstart_docs.py`

### PR 9: Package Graph Source Of Truth

Products:

- `packages/package_graph.yaml`
- generated package dependency docs
- refactored package dependency or import isolation tests

Verification:

- `./tools/package-deps generate`
- `python scripts/validate_package_graph.py`
- `pytest tests/test_package_import_isolation.py tests/test_package_dependency_metadata.py`

### PR 10: Final Source-Root Cleanup

Products:

- move `src/hla2010` to `packages/hla2010-spec/src/hla2010`
- updated `pyproject.toml` files
- updated pytest pythonpath
- repaired docs and traceability paths

Verification:

- `./tools/human-editability check`
- `./tools/spec-api check`
- `./tools/package-deps generate`
- `./tools/test`
- `python examples/target_radar_simulation.py --backend python --steps 5`

## Global Acceptance Matrix

| Smell | Closed by | Verification |
| --- | --- | --- |
| Too many unclear start paths | Workstreams 5 and 10 | one canonical onboarding doc; first-run tests |
| Stale traceability paths | Workstream 1 | path validator; trace command |
| Base64 API metadata | Workstream 2 | `./tools/spec-api check`; no base64 blob |
| Runtime dunder routing | Workstream 3 | explicit-method tests |
| Hidden Python RTI service locations | Workstream 4 | service registry and service map |
| Hard to create new FOM or federate | Workstream 6 | minimal demo package, test, tutorial |
| Java backend confusion | Workstream 7 | Java quickstart docs and tests |
| Duplicated package hierarchy rules | Workstream 8 | package graph YAML plus generated docs and tests |
| Core package source-root exception | Workstream 9 | all installable package code under package roots |
| Path sniffing, dynamic `__all__`, wildcard facades | Workstream 11 | architecture policy tests |
| Requirements overclaiming | Workstreams 1 and 11 | `mapped` or `partial` rows require evidence anchors |

## Non-Negotiable Rules While Executing

1. do not move implementation before traceability validation exists
2. do not mark a requirement `mapped` unless evidence is concrete
3. do not add new root facades
4. do not use package code to sniff repo paths
5. do not reintroduce `sys.path` mutation in maintained runtime code
6. do not add dynamic `__all__` generation
7. do not make Java or vendor routes part of first run
8. do not let generated artifacts become hand-edited truth
9. do not allow docs and tests to define package hierarchy separately
10. do not close a smell without a guard test, command, or generated artifact
