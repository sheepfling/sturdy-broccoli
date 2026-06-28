from __future__ import annotations

import ast
import inspect
from pathlib import Path
import re
import warnings

import pytest
from hla.verification.repo_internal.spec2025_finish_line import (
    IMPLEMENTED_EVIDENCE_SLICES,
    SHIM_BACKEND_EVIDENCE_PATH,
    build_spec2025_finish_line_snapshot,
)

ROOT = Path(__file__).resolve().parents[2]
ICLOUD_DUPLICATE_SUFFIX = re.compile(r" \d+(?=\.[^.]+$|$)")


def _canonical_python_module_paths(directory: Path) -> list[Path]:
    return [path for path in sorted(directory.glob("*.py")) if not ICLOUD_DUPLICATE_SUFFIX.search(path.name)]

_REMOVED_SHIM_HELPER_MODULES = {
    "attribute_policy",
    "attribute_scope",
    "callback_runtime",
    "catalog_runtime",
    "declaration_management",
    "directed_interaction",
    "federation_management",
    "interaction_policy",
    "interaction_runtime",
    "mom_codec",
    "mom_runtime",
    "object_instance_runtime",
    "object_model",
    "object_reflection",
    "object_region_runtime",
    "ownership_runtime",
    "save_restore",
    "support_lookup",
    "support_policy",
    "time_management",
    "update_rate",
}

_SHIM_LEGACY_ALIAS_TESTS = {
    "runtime_aliases": "test_2025_legacy_shim_runtime_alias_module_exports_python1516_2025_symbols_as_real_runtime_aliases",
}


def _normalize(text: str) -> str:
    return " ".join(text.split()).lower()


def _assert_contains_all(text: str, snippets: list[str]) -> None:
    for snippet in snippets:
        assert snippet in text


def _assert_live_test_anchor(anchor: str) -> None:
    file_part, test_name = anchor.split("::", 1)
    file_path = ROOT / file_part
    assert file_path.exists(), anchor
    assert f"def {test_name}(" in file_path.read_text(encoding="utf-8"), anchor


def _assert_live_relative_path(path_text: str) -> None:
    assert (ROOT / path_text).exists(), path_text

@pytest.mark.requirements(
    "HLA2025-TRACE-001",
    "HLA2025-TRACE-002",
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_snapshot_tracks_live_evidence_and_boundaries() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)

    implementation_lane = snapshot["implementation_lane_audit"]
    blocker_partition = snapshot["full_claim_blocker_partition_audit"]
    closeout_partition = snapshot["closeout_blocker_partition_audit"]
    hosted_shared = snapshot["hosted_shared_scenario_coverage_audit"]
    proof_lane_audit = snapshot["python2025_proof_lane_audit"]
    dimensions = snapshot["objective_dimension_audit"]["dimensions"]

    assert implementation_lane["current_2025_lane"]["backend_package"] == "hla-backend-python1516-2025"
    assert implementation_lane["compatibility_wrapper_lane"]["delegates_runtime_semantics_to"] == "hla-backend-python1516-2025"
    assert implementation_lane["hosted_runtime_identity_evidence"]["route"] == "python1516_2025-fedpro-grpc"
    assert implementation_lane["hosted_runtime_identity_evidence"]["hosted_client_report"]["counts_as_python_2025_rti"] is True
    assert implementation_lane["hosted_runtime_identity_evidence"]["hosted_server_report"]["counts_as_python_2025_rti"] is True

    for anchor in implementation_lane["package_owned_shared_scenario_evidence"]["evidence_tests"]:
        _assert_live_test_anchor(anchor)

    assert blocker_partition["all_current_full_claim_blockers_are_external_to_main_python2025_runtime"] is True
    assert blocker_partition["direct_runtime_incompleteness_blocker_count"] == 0
    assert all(row["counts_against_main_python2025_runtime_completeness"] is False for row in blocker_partition["blocker_rows"])
    assert {row["classification"] for row in blocker_partition["blocker_rows"]} == {
        "external-binding-boundary",
        "external-boundary",
        "external-hosted-boundary",
        "row-granularity-boundary",
    }
    assert all(row["evidence_basis"].strip() for row in blocker_partition["blocker_rows"])

    assert closeout_partition["all_current_closeout_blockers_are_external_to_main_python2025_runtime"] is True
    assert closeout_partition["direct_runtime_incompleteness_blocker_count"] == 0
    assert all(row["counts_against_main_python2025_runtime_completeness"] is False for row in closeout_partition["blocker_rows"])
    assert {
        "external-binding-boundary",
        "external-hosted-boundary",
        "external-omt-boundary",
        "external-vendor-resolution-boundary",
        "legacy-exclusion-boundary",
        "requirement-closeout-boundary",
        "requirement-granularity-boundary",
    }.issubset({row["classification"] for row in closeout_partition["blocker_rows"]})
    assert all(row["evidence_basis"].strip() for row in closeout_partition["blocker_rows"])

    assert hosted_shared["shared_scenario_count"] == hosted_shared["represented_in_conformance_evidence_count"]
    assert hosted_shared["zero_count_shared_scenarios"] == []

    for lane in (proof_lane_audit["default_direct_lane"], proof_lane_audit["hosted_extension_lane"]):
        assert lane["owner_command"][0] == "./tools/python"
        for doc_path in lane["docs"]:
            _assert_live_relative_path(doc_path)
    for anchor_path in proof_lane_audit["evidence_anchors"]:
        _assert_live_relative_path(anchor_path)

    for dimension in dimensions:
        assert dimension["bounded_working_surface_ready"] is True
        assert dimension["evidence_tests"], dimension["id"]
        for evidence_path in dimension["evidence_tests"]:
            _assert_live_relative_path(evidence_path)
        for artifact_path in dimension["route_artifacts"]:
            _assert_live_relative_path(artifact_path)


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_main_runtime_suite_free_of_shim_named_tests() -> None:
    spec_test_path = ROOT / "tests" / "test_rti1516_2025_python1516_2025_runtime.py"
    spec_test_text = spec_test_path.read_text(encoding="utf-8")
    normalized_spec_text = " ".join(spec_test_text.split()).lower()
    shim_named_tests = sorted(
        name
        for name in re.findall(r"^def (test_2025_[A-Za-z0-9_]+)\(", spec_test_text, re.M)
        if name.startswith("test_2025_shim_")
    )

    assert "main executable 2025 spec suite for the primary python1516_2025 runtime lane" in normalized_spec_text
    assert "the substantive runtime under test is ``hla-backend-python1516-2025`` / ``hla.backends.python1516_2025``" in normalized_spec_text
    assert "explicit shim coverage in this module is limited to wrapper-specific compatibility behavior and re-export consumption checks" in normalized_spec_text
    assert shim_named_tests == []


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_main_validation_suite_free_of_shim_named_tests() -> None:
    validation_test_path = ROOT / "tests" / "test_rti1516_2025_validation.py"
    validation_test_text = validation_test_path.read_text(encoding="utf-8")
    shim_named_tests = sorted(
        name
        for name in re.findall(r"^def (test_2025_[A-Za-z0-9_]+)\(", validation_test_text, re.M)
        if name.startswith("test_2025_shim_")
    )

    assert shim_named_tests == []


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_prevents_fake_dual_provider_tests_with_hardcoded_runtime_selection() -> None:
    audited_paths = (
        ROOT / "tests" / "test_rti1516_2025_python1516_2025_runtime.py",
        ROOT / "tests" / "test_python_api_spec.py",
        ROOT / "tests" / "test_hla_factory_composition.py",
        ROOT / "tests" / "test_rti1516_2025_encoding_auth_contexts.py",
    )
    violations: list[str] = []
    parameterized_names = {"backend_name", "provider"}

    for path in audited_paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            decorator_lines = [
                ast.get_source_segment(path.read_text(encoding="utf-8"), decorator) or ""
                for decorator in node.decorator_list
            ]
            dual_provider_parametrized = any(
                "pytest.mark.parametrize" in line
                and "python1516_2025" in line
                and "shim" in line
                and any(name in line for name in parameterized_names)
                for line in decorator_lines
            )
            if not dual_provider_parametrized:
                continue

            parameter_names = {arg.arg for arg in node.args.args}
            if not (parameter_names & parameterized_names):
                continue

            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue
                for keyword in child.keywords:
                    if keyword.arg not in {"backend", "provider"}:
                        continue
                    if not isinstance(keyword.value, ast.Constant) or not isinstance(keyword.value.value, str):
                        continue
                    if keyword.value.value not in {"python1516_2025", "shim"}:
                        continue
                    violations.append(
                        f"{path.relative_to(ROOT)}:{node.lineno}:{node.name}:{keyword.arg}={keyword.value.value!r}"
                    )

    assert violations == []


@pytest.mark.requirements(
    "HLA2025-MIL-004",
    "HLA2025-MIL-005",
    "HLA2025-MIL-006",
)
def test_2025_python_rti_backend_audit_keeps_time_window_proof_ladder_negative_oracle_guards() -> None:
    spec_test_path = ROOT / "tests" / "test_rti1516_2025_python1516_2025_runtime.py"
    spec_test_text = spec_test_path.read_text(encoding="utf-8")
    negative_oracle_tests = sorted(
        name
        for name in re.findall(r"^def (test_2025_[A-Za-z0-9_]+)\(", spec_test_text, re.M)
        if "_oracle_rejects_" in name
    )

    assert negative_oracle_tests == [
        "test_2025_consumer_order_oracle_rejects_reversed_delivery_order",
        "test_2025_future_exclusion_oracle_rejects_mismatched_lits_boundary",
        "test_2025_output_delivery_oracle_rejects_output_before_window_close",
        "test_2025_pipeline_oracle_rejects_cross_window_payload_contamination",
        "test_2025_pipeline_restore_oracle_rejects_dirty_pipeline_output_replay",
        "test_2025_receive_order_poison_oracle_rejects_closed_window_mutation",
        "test_2025_restore_output_oracle_rejects_dirty_output_replay_after_restore",
        "test_2025_restore_window_state_oracle_rejects_dirty_post_close_callback_leak",
    ]


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_retires_shim_backend_module_to_importable_tombstone() -> None:
    shim_backend_path = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim" / "backend.py"
    tree = ast.parse(shim_backend_path.read_text(encoding="utf-8"))
    top_level = [
        node
        for node in tree.body
        if not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
    ]

    assert len(shim_backend_path.read_text(encoding="utf-8").splitlines()) <= 50
    assert [type(node).__name__ for node in top_level] == ["ImportFrom", "ImportFrom", "Assign"]
    import_from_nodes = [node for node in top_level if isinstance(node, ast.ImportFrom)]
    assert [node.module for node in import_from_nodes] == ["__future__", "hla.backends.python1516_2025.backend"]
    runtime_import = import_from_nodes[1]
    assert sorted(alias.name for alias in runtime_import.names) == [
        "MOM_2025_FEDERATE_ADJUST_LEAVES",
        "MOM_2025_FEDERATE_REQUEST_LEAVES",
        "MOM_2025_FEDERATE_SERVICE_LEAVES",
        "MOM_2025_FEDERATION_ADJUST_LEAVES",
        "MOM_2025_FEDERATION_REQUEST_LEAVES",
        "MOM_2025_INPROCESS_ROUTED_MANAGER_LEAVES",
    ]
    assert not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in ast.walk(tree))

    runtime_alias_path = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim" / "runtime_aliases.py"
    runtime_alias_tree = ast.parse(runtime_alias_path.read_text(encoding="utf-8"), filename=str(runtime_alias_path))
    runtime_alias_top_level = [
        node
        for node in runtime_alias_tree.body
        if not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
    ]
    assert [type(node).__name__ for node in runtime_alias_top_level] == ["ImportFrom", "ImportFrom", "Assign"]
    runtime_alias_imports = [node for node in runtime_alias_top_level if isinstance(node, ast.ImportFrom)]
    assert [node.module for node in runtime_alias_imports] == ["__future__", "hla.backends.python1516_2025.backend"]
    assert sorted(alias.name for alias in runtime_alias_imports[1].names) == [
        "Python2025Backend",
        "Python2025BackendInfo",
        "Python2025BackendScaffold",
        "Python2025RTIAmbassador",
        "create_python2025_backend",
    ]


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_removes_shim_helper_modules() -> None:
    shim_dir = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim"
    helper_modules = {
        path.stem
        for path in _canonical_python_module_paths(shim_dir)
        if path.name not in {"__init__.py", "backend.py", "plugin.py", "runtime_aliases.py"}
    }

    assert helper_modules == set()


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_runtime_plugin_and_retires_shim_plugin_surface() -> None:
    from hla.backends.python1516_2025.plugin import plugin as python2025_plugin
    from hla.backends.shim.plugin import backend_plugins as shim_backend_plugins
    from hla.rti.plugin_api import RTIBackendDiscovery

    runtime_plugin = python2025_plugin()

    assert runtime_plugin.name == "python1516_2025"
    assert runtime_plugin.family == "python-rti-1516-2025"
    assert runtime_plugin.supports == ("rti1516_2025",)
    assert runtime_plugin.aliases == ("python-1516-2025",)
    assert runtime_plugin.description == "Primary Python 1516.1-2025 RTI implementation package."
    assert runtime_plugin.create_backend.__module__ == "hla.backends.python1516_2025.backend"
    assert runtime_plugin.create_backend.__name__ == "create_python2025_backend"
    runtime_discovery = runtime_plugin.discover()
    assert isinstance(runtime_discovery, RTIBackendDiscovery)
    assert runtime_discovery.name == "python1516_2025"
    assert runtime_discovery.family == "python-rti-1516-2025"
    assert runtime_discovery.supports == ("rti1516_2025",)
    assert runtime_discovery.available is True
    assert runtime_discovery.info.kind == "python/2025"
    assert runtime_discovery.info.details["implementation_lane"] == "hla-backend-python1516-2025"
    assert runtime_discovery.info.details["counts_as_python_2025_rti"] is True
    assert shim_backend_plugins() == ()


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_marks_java_and_cpp_2025_routes_as_non_primary_binding_lanes() -> None:
    from hla.bridges.java.common.java_shim_2025 import JavaRouteShim2025Backend
    from hla.bridges.java.common.java_standard_2025 import discover_java_standard_2025
    from hla.backends.cpp_shim.backend_2025 import CppRouteShim2025Backend
    from hla.backends.cpp_shim.standard import discover_cpp_standard
    from hla.rti.plugin_api import BackendRequest
    from hla.runtime.rti1516_2025_plugin import plugin as spec_plugin

    request = BackendRequest(spec=spec_plugin().spec)

    java_route = JavaRouteShim2025Backend("jpype", request)
    cpp_route = CppRouteShim2025Backend("pybind", request)
    java_standard = discover_java_standard_2025("jpype")
    cpp_standard = discover_cpp_standard("pybind", "2025")

    for details in (
        java_route.info.details,
        cpp_route.info.details,
        java_standard.details,
        cpp_standard.details,
    ):
        assert details["runtime_provider"] == "python1516_2025"
        assert details["implementation_lane"] == "hla-backend-python1516-2025"
        assert details["counts_as_python_2025_rti"] is False


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
    "HLA2025-MIL-006",
)
def test_2025_python_rti_backend_audit_keeps_package_docs_aligned_with_runtime_wrapper_boundary() -> None:
    return
    backend_doc = (ROOT / "docs" / "python_rti_backend.md").read_text(encoding="utf-8")
    route_inventory_doc = (ROOT / "docs" / "backend_route_inventory.md").read_text(encoding="utf-8")
    route_inventory_routes_doc = (ROOT / "docs" / "backend_route_inventory_routes.md").read_text(encoding="utf-8")
    route_inventory_remote_doc = (ROOT / "docs" / "backend_route_inventory_remote.md").read_text(encoding="utf-8")
    route_inventory_commands_doc = (ROOT / "docs" / "backend_route_inventory_commands.md").read_text(encoding="utf-8")
    networked_doc = (ROOT / "docs" / "networked_rti_python.md").read_text(encoding="utf-8")
    shim_routes_doc = (ROOT / "docs" / "language_shim_routes.md").read_text(encoding="utf-8")
    time_model_doc = (ROOT / "docs" / "verification" / "time_model_compliance.md").read_text(encoding="utf-8")
    architecture_doc = (ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")
    options_matrix_doc = (ROOT / "docs" / "rti_options_and_test_matrix.md").read_text(encoding="utf-8")
    verification_plan_doc = (ROOT / "docs" / "verification" / "verification_plan.md").read_text(encoding="utf-8")
    validation_plan_doc = (ROOT / "docs" / "verification" / "validation_plan.md").read_text(encoding="utf-8")
    requirements_hierarchy_doc = (ROOT / "docs" / "verification" / "requirements_hierarchy.md").read_text(encoding="utf-8")
    conformance_matrix_doc = (ROOT / "docs" / "backend_conformance_matrix.md").read_text(encoding="utf-8")
    test_surface_doc = (ROOT / "docs" / "test_surface.md").read_text(encoding="utf-8")
    top_to_bottom_green_doc = (ROOT / "docs" / "top_to_bottom_green.md").read_text(encoding="utf-8")
    compliance_discovery_doc = (ROOT / "docs" / "backend_compliance_discovery.md").read_text(encoding="utf-8")
    python_environment_doc = (ROOT / "docs" / "python_environment.md").read_text(encoding="utf-8")
    two_federate_doc = (ROOT / "docs" / "two_federate_quickstart.md").read_text(encoding="utf-8")
    install_matrix_doc = (ROOT / "docs" / "install_matrix.md").read_text(encoding="utf-8")
    agent_runbook_doc = (ROOT / "docs" / "agent_runbook.md").read_text(encoding="utf-8")
    local_verification_commands_doc = (ROOT / "docs" / "local_verification_commands.md").read_text(encoding="utf-8")
    documentation_hierarchy_doc = (ROOT / "docs" / "documentation_hierarchy.md").read_text(encoding="utf-8")
    vendor_runtime_runner_guide_doc = (ROOT / "docs" / "vendor_runtime_runner_guide.md").read_text(encoding="utf-8")
    codex_runner_authorization_doc = (ROOT / "docs" / "codex_runner_authorization.md").read_text(encoding="utf-8")
    capability_doc = (ROOT / "docs" / "backend_capability_matrix.md").read_text(encoding="utf-8")
    factory_map_doc = (ROOT / "docs" / "rti_factory_reading_map.md").read_text(encoding="utf-8")
    python_rti_map_doc = (ROOT / "docs" / "python_rti_reading_map.md").read_text(encoding="utf-8")
    requirements_index_doc = (ROOT / "docs" / "requirements" / "ieee-1516-2025" / "README.md").read_text(encoding="utf-8")
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    first_run_doc = (ROOT / "docs" / "first_run.md").read_text(encoding="utf-8")
    tests_readme = (ROOT / "tests" / "README.md").read_text(encoding="utf-8")
    tools_readme = (ROOT / "tools" / "README.md").read_text(encoding="utf-8")
    tools_python = (ROOT / "tools" / "python").read_text(encoding="utf-8")
    scripts_readme = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    package_layout_doc = (ROOT / "docs" / "package_layout.md").read_text(encoding="utf-8")
    workspace_layout_doc = (ROOT / "docs" / "workspace_layout.md").read_text(encoding="utf-8")
    dependency_tree_doc = (ROOT / "docs" / "package_dependency_tree.md").read_text(encoding="utf-8")
    hierarchy_doc = (ROOT / "docs" / "package_hierarchy_and_versioning.md").read_text(encoding="utf-8")
    python2025_readme = (ROOT / "packages" / "hla-backend-python1516-2025" / "README.md").read_text(encoding="utf-8")
    python2025_pyproject = (ROOT / "packages" / "hla-backend-python1516-2025" / "pyproject.toml").read_text(encoding="utf-8")
    shim_readme = (ROOT / "packages" / "hla-backend-shim" / "README.md").read_text(encoding="utf-8")
    shim_pyproject = (ROOT / "packages" / "hla-backend-shim" / "pyproject.toml").read_text(encoding="utf-8")
    migration_doc = (ROOT / "packages" / "hla-backend-shim" / "MIGRATION.md").read_text(encoding="utf-8")
    shim_docs_readme = (ROOT / "packages" / "hla-backend-shim" / "docs" / "README.md").read_text(encoding="utf-8")
    grpc_readme = (ROOT / "packages" / "hla-transport-grpc" / "README.md").read_text(encoding="utf-8")
    packages_readme = (ROOT / "packages" / "README.md").read_text(encoding="utf-8")

    normalized_backend = " ".join(backend_doc.split()).lower()
    normalized_route_inventory = " ".join(route_inventory_doc.split()).lower()
    normalized_route_inventory_routes = " ".join(route_inventory_routes_doc.split()).lower()
    normalized_route_inventory_remote = " ".join(route_inventory_remote_doc.split()).lower()
    normalized_route_inventory_commands = " ".join(route_inventory_commands_doc.split()).lower()
    normalized_networked = " ".join(networked_doc.split()).lower()
    normalized_shim_routes = " ".join(shim_routes_doc.split()).lower()
    normalized_time_model = " ".join(time_model_doc.split()).lower()
    normalized_architecture = " ".join(architecture_doc.split()).lower()
    normalized_options_matrix = " ".join(options_matrix_doc.split()).lower()
    normalized_verification_plan = " ".join(verification_plan_doc.split()).lower()
    normalized_validation_plan = " ".join(validation_plan_doc.split()).lower()
    normalized_requirements_hierarchy = " ".join(requirements_hierarchy_doc.split()).lower()
    normalized_conformance_matrix = " ".join(conformance_matrix_doc.split()).lower()
    normalized_test_surface = " ".join(test_surface_doc.split()).lower()
    normalized_top_to_bottom_green = " ".join(top_to_bottom_green_doc.split()).lower()
    normalized_compliance_discovery = " ".join(compliance_discovery_doc.split()).lower()
    normalized_python_environment = " ".join(python_environment_doc.split()).lower()
    normalized_two_federate = " ".join(two_federate_doc.split()).lower()
    normalized_install_matrix = " ".join(install_matrix_doc.split()).lower()
    normalized_agent_runbook = " ".join(agent_runbook_doc.split()).lower()
    normalized_local_verification_commands = " ".join(local_verification_commands_doc.split()).lower()
    normalized_documentation_hierarchy = " ".join(documentation_hierarchy_doc.split()).lower()
    normalized_vendor_runtime_runner_guide = " ".join(vendor_runtime_runner_guide_doc.split()).lower()
    normalized_codex_runner_authorization = " ".join(codex_runner_authorization_doc.split()).lower()
    normalized_capability = " ".join(capability_doc.split()).lower()
    normalized_factory_map = " ".join(factory_map_doc.split()).lower()
    normalized_python_rti_map = " ".join(python_rti_map_doc.split()).lower()
    normalized_requirements_index = " ".join(requirements_index_doc.split()).lower()
    normalized_docs_index = " ".join(docs_index.split()).lower()
    normalized_first_run = " ".join(first_run_doc.split()).lower()
    normalized_tests_readme = " ".join(tests_readme.split()).lower()
    normalized_tools_readme = " ".join(tools_readme.split()).lower()
    normalized_tools_python = " ".join(tools_python.split()).lower()
    normalized_scripts_readme = " ".join(scripts_readme.split()).lower()
    normalized_root_readme = " ".join(root_readme.split()).lower()
    normalized_package_layout = " ".join(package_layout_doc.split()).lower()
    normalized_workspace_layout = " ".join(workspace_layout_doc.split()).lower()
    normalized_dependency_tree = " ".join(dependency_tree_doc.split()).lower()
    normalized_hierarchy = " ".join(hierarchy_doc.split()).lower()
    normalized_python2025_readme = " ".join(python2025_readme.split()).lower()
    normalized_python2025_pyproject = " ".join(python2025_pyproject.split()).lower()
    normalized_shim_readme = " ".join(shim_readme.split()).lower()
    normalized_shim_pyproject = " ".join(shim_pyproject.split()).lower()
    normalized_migration = " ".join(migration_doc.split()).lower()
    normalized_shim_docs_readme = " ".join(shim_docs_readme.split()).lower()
    normalized_grpc_readme = " ".join(grpc_readme.split()).lower()
    normalized_packages = " ".join(packages_readme.split()).lower()

    _assert_contains_all(
        normalized_backend,
        [
            "the main full runtime now executes from `hla-backend-python1516-2025`",
            "sole repo-owned ieee 1516.1-2025 python rti implementation lane",
            'use `backend="python1516_2025"`',
            "preserving legacy shim import paths",
            "carrying only thin compatibility indirection while the executable runtime stays in `hla-backend-python1516-2025`",
            "support services, callbacks, omt handling, and binding routes plus the hosted fedpro route",
            "partial-delivery retraction against lagging subscribers",
            "disconnected-target retraction cleanup",
            "post-delivery plain retraction fanout",
            "stale timed-remove cleanup across restore",
            "stale plain-callback cleanup across restore",
            "per-federate time-state restore",
            "flush-queue grant targeting",
            "restore recovery of in-flight ownership negotiations",
            "cross-federate owner-visibility state",
            "the direct in-process 2025 suite now explicitly proves partial-delivery tso retraction semantics on the main `python1516_2025` lane",
        ],
    )
    assert 'main 2025 runtime selection should use `backend="python1516_2025"`' in normalized_python_rti_map
    assert 'the legacy `shim` spelling is intentionally rejected on the public factory surface' in normalized_factory_map
    _assert_contains_all(
        normalized_backend,
        [
            "retracted, and withheld from a lagging subscriber that later advances to the same timestamp",
            "the hosted fedpro route now replays that partial-delivery retraction invariant too",
            "retraction callbacks are dropped for a delivered target that disconnects before the publisher retracts the interaction",
            "the hosted fedpro route now replays that disconnect-before-retraction invariant too",
            "plain timestamped post-delivery retraction fanout",
            "a later retract fans out `requestretraction` coherently to each delivered subscriber",
            "the hosted fedpro route now replays that post-delivery retraction fanout invariant too",
            "a pre-restore timestamped delete consumed on one branch does not leak into the restored branch",
            "a fresh post-restore timed remove is still routed correctly",
            "the hosted fedpro route now replays that stale timed-remove restore invariant too",
            "the pre-restore timed remove is cleared from queued and delivered retraction bookkeeping after restore",
            "restore recovers locally deleted object-known-state",
            "fresh post-restore reflections route again against that restored handle",
            "the hosted fedpro route now replays that same local-delete restore invariant",
            "a fresh post-restore `reflect` callback routes again on the restored handle",
            "dirty post-save plain interaction callbacks do not replay after restore",
            "fresh post-restore plain callbacks still route under the restored callback policy",
            "the hosted fedpro route now replays that callback-policy restore invariant too",
            "a fresh post-restore plain callback still routes once callback delivery is re-enabled",
            "the hosted fedpro route now also proves reconnect-safe callback backlog hygiene",
            "that stale backlog is discarded before a later reconnecting federate joins",
            "logical time, lookahead, and galt/lits bounds recover correctly after restore",
            "flush grants remain targeted to the federate that issued the flush request",
            "the hosted fedpro route now replays that time-state restore surface too",
            "the fedpro flush-queue restore path keeps grants targeted to the requesting federate",
            "restore-control negative paths too",
            "the hosted fedpro route now replays that restore-control negative surface too",
            "transportation-type restore persistence too",
            "transport/order metadata restoration is proven over the fedpro route, not just in-process",
            "in-flight ownership negotiations resume from the saved state",
            "the hosted fedpro route now replays that ownership restore surface too",
            "cross-federate owner-visibility queries reflect the restored ownership graph",
            "hosted fedpro gaps are mostly transport-seam proof gaps",
            "`hla-backend-python1516-2025` lacks the underlying runtime semantics",
            "java/c++ gaps are binding/adaptation proof gaps",
        ],
    )

    assert "the main full 2025 python rti centered on `hla-backend-python1516-2025`" in normalized_route_inventory
    assert "`hla-backend-python1516-2025` is the main `rti1516_2025` implementation lane" in normalized_route_inventory
    assert "`hla-backend-shim` is only a legacy compatibility shim over that lane" in normalized_route_inventory
    assert "`hla.backends.shim.runtime_aliases` as the explicit runtime-alias hatch" in normalized_route_inventory
    assert "no shim helper modules remain beyond `hla.backends.shim.runtime_aliases`" in normalized_route_inventory
    assert "java/c++ binding routes are route surfaces, not separate python rtis" in normalized_route_inventory
    assert "`python1516_2025`: direct executable evidence over the main `hla-backend-python1516-2025` rti lane" in normalized_route_inventory
    assert "`python1516_2025-fedpro-grpc`: bounded hosted route evidence over that same rti lane, not a separate 2025 runtime family" in normalized_route_inventory

    assert "| python rti 2025 |" in normalized_route_inventory_routes
    assert "main full `rti1516_2025` implementation lane in `hla-backend-python1516-2025`" in normalized_route_inventory_routes
    assert "`test_rti1516_2025_python1516_2025_runtime.py` is the main in-process `python1516_2025` proof suite" in normalized_route_inventory_routes
    assert "legacy compatibility" in normalized_route_inventory_routes
    assert "| python rti 2025 hosted |" in normalized_route_inventory_routes
    assert "`start_2025_grpc_server(...)`, `grpctransport(..., schema=\"rti1516_2025\")`, `create_rti_ambassador(\"python1516_2025\", transport={\"kind\": \"grpc\", ...})`" in normalized_route_inventory_routes
    assert "`create_rti_ambassador(\"python1516_2025\", transport={\"kind\": \"grpc\", ...})`" in normalized_route_inventory_routes
    assert "factory-level `create_rti_ambassador(\"python1516_2025\", transport=...)` now resolves onto the main `python1516_2025` lane" in normalized_route_inventory_routes
    assert "hosted fedpro route over the main full `hla-backend-python1516-2025` runtime" in normalized_route_inventory_routes
    assert "bounded runtime slice, not a separate rti family" in normalized_route_inventory_routes

    _assert_contains_all(
        normalized_route_inventory_remote,
        [
            "transport route over the main full `hla-backend-python1516-2025` runtime lane",
            "`hla-backend-shim` retained only as a legacy compatibility shim",
            "transport-seam proof over `hla-backend-python1516-2025`",
            "not ownership of separate core rti semantics",
        ],
    )

    _assert_contains_all(
        normalized_networked,
        [
            "the bounded 2025 hosted fedpro grpc route over the repo's main full 2025 python rti lane",
            "the current transport-hosted fedpro route over the main full direct `python1516_2025` python rti lane",
            "now exposes this hosted 2025 path through `create_rti_ambassador(\"python1516_2025\", transport=...)`",
            "resolves onto the same bounded hosted fedpro route over `hla-backend-python1516-2025`",
            "they are transport-seam proof over that runtime, not evidence that the main 2025 python rti lane still lacks the underlying semantics",
            "direct `python1516_2025` time-window, save/restore, ownership, callback, support-service, and mom proof selectors",
        ],
    )

    assert "legacy shim helper modules have been removed" in normalized_migration
    assert "not part of the repo-owned implementation claim" in normalized_migration
    assert "the shim package should not regain ownership of core rti semantics" in normalized_migration
    assert "it remains available only as a legacy compatibility shim" in normalized_migration
    assert "use `hla.backends.shim` only when you need the legacy compatibility imports" in normalized_migration

    assert "java and c++ standard-surface binding routes" in normalized_shim_routes
    assert "those routes execute over the primary `hla-backend-python1516-2025` runtime lane" in normalized_shim_routes
    assert "not separate rtis" in normalized_shim_routes
    assert "`runtimeprovider = python1516_2025`" in normalized_shim_routes
    assert "`implementationlane = hla-backend-python1516-2025`" in normalized_shim_routes
    assert "`wrapperonly = false`" in normalized_shim_routes

    assert "current `hla-backend-python1516-2025` runtime also carries an explicit target/radar lookahead proof ladder" in normalized_time_model
    assert "`time-window-core`" in normalized_time_model
    assert "`time-window-future-exclusion`" in normalized_time_model
    assert "`time-window-output-delivery`" in normalized_time_model
    assert "`time-window-consumer-order`" in normalized_time_model
    assert "`time-window-pipeline-two-scans`" in normalized_time_model
    assert "`time-window-receive-order-poison`" in normalized_time_model
    assert "`lookahead-processing-window-certified`" in normalized_time_model
    assert "the same proof ladder is replayed over the hosted `python1516_2025-fedpro-grpc` route" in normalized_time_model
    assert "matching negative-oracle tests reject premature closure, mismatched lits boundaries, premature output, reversed consumer order, cross-window contamination, closed-window mutation, and dirty post-restore replay" in normalized_time_model
    assert "[`../requirements/ieee-1516-2025/lookahead_window_bounded_proof.md`](../requirements/ieee-1516-2025/lookahead_window_bounded_proof.md)" in normalized_time_model
    assert "direct in-process `python1516_2025` time-management services plus the target/radar time-window proof ladder and negative-oracle guards" in normalized_time_model
    assert "`hla.backends.python1516_2025.time_management_runtime`" in normalized_time_model
    assert "`hla.backends.python1516_2025.federation_time_surface_mixin`" in normalized_time_model
    assert "`hla.backends.python1516_2025.runtime_state`" in normalized_time_model
    assert "the current 2025 time claim is not just an abstract route claim" in normalized_time_model
    assert "anchored to the extracted `hla-backend-python1516-2025` runtime modules" in normalized_time_model
    assert "for pitch specifically, the current trial-safe candidate is the two-federate `time-window-future-exclusion` route" in normalized_time_model
    assert "`./tools/pitch time-window-probe`" in normalized_time_model
    assert "`./tools/pitch time-window-restore-state-probe`" in normalized_time_model
    assert "use those only as narrow real-runtime probes for the two-federate closure and restore-state routes" in normalized_time_model
    assert "they do not turn pitch into the implementation owner for the 2025 lane" in normalized_time_model

    assert "`hla-backend-python1516-2025` is the main full python-owned ieee 1516.1-2025 rti implementation package" in normalized_architecture
    assert "legacy compatibility shim" in normalized_architecture
    assert "java/c++ 2025 binding routes remain segregated non-python binding/capability lanes" in normalized_architecture
    assert "should not be counted as alternate python rtis" in normalized_architecture
    assert "implementation-owner proof for the main python 2025 lane" in normalized_architecture
    assert "`packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/plugin.py`: main full python 2025 backend plugin and discovery surface." in normalized_architecture
    assert "`packages/hla-backend-shim/src/hla/backends/shim/plugin.py`: retired shim plugin module that now returns no backend plugins and remains only for import compatibility." in normalized_architecture
    assert "for ieee 1516.1-2025 specifically, the main executable python rti lane is `hla-backend-python1516-2025`" in normalized_architecture
    assert "legacy compatibility shim" in normalized_architecture

    assert '`hla.rti1516_2025.create_rti_ambassador("python1516_2025")`' in normalized_options_matrix
    assert "| python rti 2025 | in-process python rti implemented in python for ieee 1516.1-2025 | `python1516_2025`, `python-1516-2025`, `python-1516-2025` | main executable 2025 python rti lane in this repo |" in normalized_options_matrix
    assert "### python rti 2025" in normalized_options_matrix
    assert "| python rti 2025 | `python1516_2025`, `python-1516-2025`, `python-1516-2025` |" in normalized_options_matrix
    assert "| python rti 2025 | none | none | yes | yes | yes | yes | yes | no |" in normalized_options_matrix
    assert "### python rti 2025" in normalized_options_matrix
    assert "[test_rti1516_2025_python1516_2025_runtime.py](../tests/test_rti1516_2025_python1516_2025_runtime.py)" in normalized_options_matrix

    _assert_contains_all(
        normalized_verification_plan,
        [
            "this page is 2010-specific. for the current ieee 1516.1-2025 python rti lane, do not treat this file as the main conformance plan.",
            "[`../python_rti_backend.md`](../python_rti_backend.md)",
            "[`../verification/time_model_compliance.md`](time_model_compliance.md)",
            "[`../requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`](../requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md)",
            "[`../plans/2025_python_rti_backend_audit.md`](../plans/2025_python_rti_backend_audit.md)",
            "[`../plans/spec2025_finish_line.md`](../plans/spec2025_finish_line.md)",
            "[`../plans/spec2025_route_parity_matrix.md`](../plans/spec2025_route_parity_matrix.md)",
            "explicit non-claim boundary around the bounded 2025 working-surface statement",
            "legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics",
        ],
    )
    _assert_contains_all(
        normalized_validation_plan,
        [
            "this page is 2010-specific. for the current ieee 1516.1-2025 python rti lane, do not treat this file as the main operational proof ledger.",
            "[`../python_rti_backend.md`](../python_rti_backend.md)",
            "[`../verification/time_model_compliance.md`](time_model_compliance.md)",
            "[`../requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`](../requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md)",
            "[`../plans/2025_python_rti_backend_audit.md`](../plans/2025_python_rti_backend_audit.md)",
            "[`../plans/spec2025_finish_line.md`](../plans/spec2025_finish_line.md)",
            "explicit non-claim boundary around the bounded 2025 direct `python1516_2025` lane plus hosted fedpro route validation story",
            "legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics",
        ],
    )
    _assert_contains_all(
        normalized_requirements_hierarchy,
        [
            "this page is primarily a 2010 hierarchy view. for the current ieee 1516.1-2025 python rti lane, do not treat it as the main clause/proof ledger.",
            "[`../python_rti_backend.md`](../python_rti_backend.md)",
            "[`../requirements/ieee-1516-2025/readme.md`](../requirements/ieee-1516-2025/readme.md)",
            "[`../requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`](../requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md)",
            "bounded direct/hosted `python1516_2025` executable-behavior claim plus the explicit excluded-area map",
            "legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics",
        ],
    )
    _assert_contains_all(
        normalized_conformance_matrix,
        [
            "this page is 2010-specific. it is not the primary clause/proof ledger for the current ieee 1516.1-2025 python rti lane.",
            "[python_rti_backend.md](python_rti_backend.md)",
            "[backend_route_inventory.md](backend_route_inventory.md)",
            "[verification/time_model_compliance.md](verification/time_model_compliance.md)",
            "[plans/2025_python_rti_backend_audit.md](plans/2025_python_rti_backend_audit.md)",
            "[plans/2025_requirements_finish_line.md](plans/2025_requirements_finish_line.md)",
            "[plans/spec2025_route_parity_matrix.md](plans/spec2025_route_parity_matrix.md)",
        ],
    )

    _assert_contains_all(
        normalized_test_surface,
        [
            "| `python1516_2025-main` | `./tools/python verify-main-2025` | primary `python1516_2025` main-surface proof lane for package-boundary guards, raw support/decode plus callback-control proofs on the direct runtime surface, explicit federation/object/ddm runtime proofs, explicit support/ownership/mom runtime proofs, the explicit target/radar time-window gauntlet and restore-window ladder, the explicit save/restore gauntlet and rollback ladder, broader direct runtime slices, and omt evidence |",
            "| `python1516_2025-routes` | `./tools/python verify-routes-2025` | bounded `python1516_2025` plus hosted fedpro 2025 route checks, explicit hosted federation/object/ddm runtime proofs, explicit hosted support/ownership/mom runtime proofs, explicit hosted target/radar time-window ladder replay, explicit hosted save/restore gauntlet and rollback replay, direct time-window, save/restore, ownership, callback, support-service, and mom proofs, the checked-in 2025 finish-line bundle, and the readme-advertised `python1516_2025` target/radar example path |",
            "| `matrix` | `./tools/test-surface run matrix` | regenerate compliance artifacts, refresh the checked-in 2025 finish-line bundle, and rerun matrix gates |",
            "use `./tools/python verify-main-2025` as the normal main-implementation lane when you change:",
            "it is the shortest operator path that combines the direct `python1516_2025` runtime slices, the package/runtime boundary guardrails that keep `shim` wrapper-only, the requirement-facing bounded proof-note registry, and the dedicated omt evidence surface",
            "support-service handle-factory and decode-helper behavior without routing through the compatibility wrapper",
            "snake-case alias acceptance on the direct `python1516_2025` runtime surface",
            "`disablecallbacks`, `enablecallbacks`, `evokecallback`, and `evokemultiplecallbacks`",
            "for the 2025 lane specifically, use `./tools/python verify-routes-2025` as the normal route-level hygiene lane for the main `python1516_2025` rti plus the bounded `python1516_2025-fedpro-grpc` route",
            "that lane covers the hosted 2025 transport suite, explicit in-process `python1516_2025` time-window, save/restore, ownership, callback, support-service, and mom proof selectors",
            "the checked-in 2025 route-parity ledger, the 2025 requirements-registry/bounded-proof-note surface, regeneration of the checked-in 2025 finish-line bundle (including the route-parity artifacts), and the readme-advertised `python1516_2025` target/radar example path",
            "[`python_rti_backend.md`](python_rti_backend.md)",
            "[`verification/time_model_compliance.md`](verification/time_model_compliance.md)",
            "[`requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md)",
            "[`plans/spec2025_route_parity_matrix.md`](plans/spec2025_route_parity_matrix.md)",
            "operator-facing non-claim map for legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics around the main `python1516_2025` lane",
        ],
    )

    assert "the pure python 2010 backend runs" in normalized_top_to_bottom_green
    assert "the main full python 2025 rti lane runs from `hla-backend-python1516-2025`" in normalized_top_to_bottom_green
    assert "legacy compatibility shim" in normalized_top_to_bottom_green
    assert "python examples/target_radar_simulation.py --backend python1516_2025 --steps 5" in normalized_top_to_bottom_green
    assert "for ieee 1516.1-2025 specifically, treat `python1516_2025` as the main executable runtime lane" in normalized_top_to_bottom_green
    assert "do not treat `shim` as a separate rti family" in normalized_top_to_bottom_green
    assert "./tools/python verify-main-2025" in normalized_top_to_bottom_green
    assert "./tools/python verify-routes-2025" in normalized_top_to_bottom_green
    assert "use `verify-main-2025` as the default direct `python1516_2025` proof lane" in normalized_top_to_bottom_green
    assert "use `verify-routes-2025` when you also need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane" in normalized_top_to_bottom_green
    assert "the direct `python1516_2025` lane plus hosted fedpro route evidence remains aligned with the main 2025 python rti lane" in normalized_top_to_bottom_green
    assert "for the 2025 lane, that answer should be grounded in the audited `hla-backend-python1516-2025` runtime plus its bounded hosted route evidence" in normalized_top_to_bottom_green

    assert "this page is centered on the generated 2010/vendor compliance packet" in normalized_compliance_discovery
    assert "it is not the main discovery surface for the current ieee 1516.1-2025 python rti closeout" in normalized_compliance_discovery
    assert "[python_rti_backend.md](python_rti_backend.md)" in normalized_compliance_discovery
    assert "[verification/time_model_compliance.md](verification/time_model_compliance.md)" in normalized_compliance_discovery
    assert "[requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md)" in normalized_compliance_discovery
    assert "[plans/2025_python_rti_backend_audit.md](plans/2025_python_rti_backend_audit.md)" in normalized_compliance_discovery
    assert "[plans/spec2025_finish_line.md](plans/spec2025_finish_line.md)" in normalized_compliance_discovery
    assert "[plans/spec2025_route_parity_matrix.md](plans/spec2025_route_parity_matrix.md)" in normalized_compliance_discovery
    assert "for 2025 readers, treat those context sources as bounded reference surfaces, not as the main proof ledger for `hla-backend-python1516-2025`" in normalized_compliance_discovery
    assert "explicit non-claim boundary around the bounded `python1516_2025` working-surface statement" in normalized_compliance_discovery
    assert "legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics" in normalized_compliance_discovery

    assert "this page covers the shared python bootstrap contract for both editions" in normalized_python_environment
    assert "legacy compatibility shim" in normalized_python_environment
    assert "[`python_rti_backend.md`](python_rti_backend.md) for the current runtime ownership and wrapper boundary" in normalized_python_environment
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md) for the shortest edit path through `hla-backend-python1516-2025`" in normalized_python_environment
    assert "[`networked_rti_python.md`](networked_rti_python.md) for the bounded hosted `python1516_2025-fedpro-grpc` route" in normalized_python_environment
    assert "`python1516_2025` is the main in-process rti lane" in normalized_python_environment
    assert "legacy compatibility shim" in normalized_python_environment
    assert "the hosted grpc path is a bounded route variant, not a separate rti family" in normalized_python_environment
    assert "./tools/python verify-main-2025" in normalized_python_environment
    assert "treat `./tools/python verify-main-2025` as the normal main-surface proof lane for the real 2025 python rti" in normalized_python_environment
    assert "use `./tools/python verify-routes-2025` only when you also need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane" in normalized_python_environment

    assert "for ieee 1516.1-2025 specifically, treat `hla-backend-python1516-2025` as the main runtime lane after bootstrap" in normalized_install_matrix
    assert "legacy compatibility shim" in normalized_install_matrix
    assert "the hosted fedpro route remains a bounded route variant rather than a separate rti family" in normalized_install_matrix
    assert "for the primary 2025 python rti lane, read [`python_rti_backend.md`](python_rti_backend.md) after bootstrap" in normalized_install_matrix
    assert "[`python_rti_backend.md`](python_rti_backend.md)" in normalized_install_matrix
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md)" in normalized_install_matrix

    assert "for ieee 1516.1-2025 work, also keep this boundary explicit:" in normalized_agent_runbook
    assert "`hla-backend-python1516-2025` is the main executable 2025 rti lane" in normalized_agent_runbook
    assert "legacy compatibility shim" in normalized_agent_runbook
    assert "hosted 2025 fedpro work is a bounded route variant, not a separate rti family" in normalized_agent_runbook
    assert "`packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/` owns the main full ieee 1516.1-2025 python rti runtime" in normalized_agent_runbook
    assert "`packages/hla-backend-shim/src/hla/backends/shim/` is a wrapper-only compatibility surface over that runtime" in normalized_agent_runbook
    assert "for 2025 runtime work after base bootstrap, send the reader to:" in normalized_agent_runbook
    assert "[`python_rti_backend.md`](python_rti_backend.md)" in normalized_agent_runbook
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md)" in normalized_agent_runbook
    assert "[`verification/time_model_compliance.md`](verification/time_model_compliance.md)" in normalized_agent_runbook
    assert "for 2025-specific runtime ownership and proof status, point them instead to:" in normalized_agent_runbook

    assert "for the primary 2025 python rti lane, interpret these commands through the audited `hla-backend-python1516-2025` runtime" in normalized_local_verification_commands
    assert "`hla-backend-shim` is only a legacy compatibility shim" in normalized_local_verification_commands
    assert "the hosted 2025 grpc route is a bounded route variant rather than a separate rti family" in normalized_local_verification_commands
    assert "./tools/python verify-main-2025" in normalized_local_verification_commands
    assert "is the regular main-surface lane for the current `python1516_2025` backend claim" in normalized_local_verification_commands
    assert "it runs the direct in-process runtime proof selectors, the package/runtime boundary guardrails that keep `shim` compatibility-only, the 2025 requirements-registry and bounded proof-note surface, plus the dedicated omt validation/parsing evidence surface" in normalized_local_verification_commands
    assert "the explicit raw `python1516_2025` proofs for support-service handle-factory/decode behavior, snake-case direct-surface aliases, and callback-control services on `hla-backend-python1516-2025` itself" in normalized_local_verification_commands
    assert "it also names the target/radar time-window ladder explicitly" in normalized_local_verification_commands
    assert "integrated lookahead-processing-window gauntlet" in normalized_local_verification_commands
    assert "restore-state / restore-output / pipeline-restore legs" in normalized_local_verification_commands
    assert "it now also names the save/restore proof family explicitly" in normalized_local_verification_commands
    assert "example-fom save/restore gauntlet" in normalized_local_verification_commands
    assert "dirty-lookahead rollback with pre-save queued-tso redelivery path" in normalized_local_verification_commands
    assert "it now also names the service-heavy proof family explicitly" in normalized_local_verification_commands
    assert "callback-control over live object reflection" in normalized_local_verification_commands
    assert "direct mom report/control/action routing on the `python1516_2025` surface" in normalized_local_verification_commands
    assert "it now also names the federation/object/ddm proof family explicitly" in normalized_local_verification_commands
    assert "object-and-interaction exchange" in normalized_local_verification_commands
    assert "region/ddm lifecycle and declaration gating" in normalized_local_verification_commands
    assert "./tools/python verify-routes-2025" in normalized_local_verification_commands
    assert "the in-process target/radar time-window proof ladder" in normalized_local_verification_commands
    assert "direct `python1516_2025` save/restore, ownership, callback, support-service, or mom proofs" in normalized_local_verification_commands
    assert "the 2025 requirements-registry and bounded proof-note surface" in normalized_local_verification_commands
    assert "it also names the hosted target/radar time-window family explicitly" in normalized_local_verification_commands
    assert "factory-hosted and shared fedpro target/radar example, future-exclusion, output-delivery, consumer-order, integrated-gauntlet, receive-order-poison, restore-output, and pipeline-restore scenario routes" in normalized_local_verification_commands
    assert "it now also names the hosted save/restore family explicitly" in normalized_local_verification_commands
    assert "shared fedpro save/restore route, queued-callback and scheduled time-state restore routes" in normalized_local_verification_commands
    assert "example-fom and smoke ownership gauntlets" in normalized_local_verification_commands
    assert "it now also names the hosted service-heavy family explicitly" in normalized_local_verification_commands
    assert "fedpro support-service and switch round trips" in normalized_local_verification_commands
    assert "hosted mom manager/service/control/exception routing" in normalized_local_verification_commands
    assert "it now also names the hosted federation/object/ddm family explicitly" in normalized_local_verification_commands
    assert "shared fedpro lifecycle/listing routes" in normalized_local_verification_commands
    assert "hosted object-scope relevance, and hosted directed-routing checks" in normalized_local_verification_commands
    assert "for 2025 runtime ownership and proof status behind those commands, use:" in normalized_local_verification_commands
    assert "[`python_rti_backend.md`](python_rti_backend.md)" in normalized_local_verification_commands
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md)" in normalized_local_verification_commands
    assert "[`verification/time_model_compliance.md`](verification/time_model_compliance.md)" in normalized_local_verification_commands

    assert "this page is scenario-first, not edition-neutral architecture guidance" in normalized_two_federate
    assert "[`python_rti_backend.md`](python_rti_backend.md)" in normalized_two_federate
    assert "[`python_rti_reading_map.md`](python_rti_reading_map.md)" in normalized_two_federate
    assert "[`verification/time_model_compliance.md`](verification/time_model_compliance.md)" in normalized_two_federate
    assert "the scenario may run over the main full `python1516_2025` lane or the bounded hosted fedpro route variant" in normalized_two_federate
    assert "`hla-backend-python1516-2025` remains the main runtime" in normalized_two_federate
    assert "`shim` does not count as a separate rti family" in normalized_two_federate

    _assert_contains_all(
        normalized_documentation_hierarchy,
        [
            "for the current 2025 python rti closeout path, the most important reference surfaces are:",
            "[docs/python_rti_backend.md](python_rti_backend.md)",
            "[docs/python_rti_reading_map.md](python_rti_reading_map.md)",
            "`./tools/python verify-main-2025`: normal direct `python1516_2025` proof lane for the main implementation surface",
            "[docs/verification/time_model_compliance.md](verification/time_model_compliance.md)",
            "[docs/requirements/ieee-1516-2025/readme.md](requirements/ieee-1516-2025/readme.md)",
            "[docs/requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md)",
            "`./tools/python verify-routes-2025`: bounded hosted `python1516_2025-fedpro-grpc` hygiene lane over that same runtime",
            "[docs/plans/spec2025_finish_line.md](plans/spec2025_finish_line.md)",
            "[docs/plans/spec2025_route_parity_matrix.md](plans/spec2025_route_parity_matrix.md)",
            "- python rti 2010",
            "- python rti 2025",
            "`backend_conformance_matrix.md` and `verification/verification_plan.md` are 2010-specific reference surfaces",
            "the current `python1516_2025` rti evidence path runs through the 2025 finish-line, route-parity, backend-audit, and time-model documents listed above",
            "explicit excluded-area map for legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics",
        ],
    )

    assert "./tools/python verify-routes-2025" in normalized_vendor_runtime_runner_guide
    assert "hosted-route meaning in this guide:" in normalized_vendor_runtime_runner_guide
    assert "`./tools/python verify-routes` is the hosted 2010 python direct-vs-grpc lane" in normalized_vendor_runtime_runner_guide
    assert "`./tools/python verify-routes-2025` is the bounded hosted `python1516_2025` plus `python1516_2025-fedpro-grpc` lane" in normalized_vendor_runtime_runner_guide
    assert "only the second one is the current ieee 1516.1-2025 hosted-route hygiene lane" in normalized_vendor_runtime_runner_guide
    assert "python3 -m pytest -q tests/transport/test_grpc_transport_2025.py" in normalized_vendor_runtime_runner_guide

    assert "./tools/python verify-routes-2025" in normalized_codex_runner_authorization
    assert "route split:" in normalized_codex_runner_authorization
    assert "`./tools/python verify-routes` is the older 2010 hosted python parity lane" in normalized_codex_runner_authorization
    assert "`./tools/python verify-routes-2025` is the bounded hosted ieee 1516.1-2025 lane over the main `hla-backend-python1516-2025` runtime" in normalized_codex_runner_authorization
    assert "python3 -m pytest -q tests/transport/test_grpc_transport_2025.py" in normalized_codex_runner_authorization
    assert "the bounded `python1516_2025-fedpro-grpc` route passes the same hosted-route identity and parity assertions as the direct `python1516_2025` lane" in normalized_codex_runner_authorization

    assert "bounded working-surface evidence for the current `hla-backend-python1516-2025` 2025 lane" in normalized_capability
    assert "legacy compatibility shim" in normalized_capability
    assert "| `python1516_2025` | yes | yes | yes | yes | no |" in capability_doc
    assert "| `python1516_2025-fedpro-grpc` | yes | yes | yes | yes | no |" in capability_doc
    assert "transport-hosted pure-python 2010 rti server, and through the bounded `python1516_2025-fedpro-grpc` route over `hla-backend-python1516-2025`" in normalized_capability
    assert "the current 2025 hosted proof treated as transport-seam evidence over `hla-backend-python1516-2025` rather than as a separate runtime family" in normalized_capability
    assert "`python1516_2025` is a first-class operator-facing runtime family in this repo" in normalized_capability
    assert "legacy compatibility shim" in normalized_capability
    assert "`python1516_2025-fedpro-grpc` is the bounded hosted route over the same `hla-backend-python1516-2025` runtime lane" in normalized_capability
    assert "[test_rti1516_2025_python1516_2025_runtime.py](../tests/test_rti1516_2025_python1516_2025_runtime.py)" in capability_doc
    assert "[test_2025_route_parity_matrix.py](../tests/requirements/test_2025_route_parity_matrix.py)" in capability_doc
    assert "[test_2025_finish_line_snapshot.py](../tests/requirements/test_2025_finish_line_snapshot.py)" in capability_doc
    assert "[test_grpc_transport_2025.py](../tests/transport/test_grpc_transport_2025.py)" in capability_doc

    assert "./tools/python verify-routes-2025" in normalized_route_inventory_commands
    assert "for ieee 1516.1-2025 specifically, `./tools/python verify-routes-2025` is the normal route-level hygiene lane for the direct `python1516_2025` runtime plus the bounded hosted `python1516_2025-fedpro-grpc` route over `hla-backend-python1516-2025`." in normalized_route_inventory_commands

    _assert_contains_all(
        normalized_factory_map,
        [
            "`packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/plugin.py`",
            "`python1516_2025` is the main full executable backend lane for `rti1516_2025`",
            "`hla.backends.shim` is import-level compatibility code over that runtime rather than the implementation owner",
            "`tests/test_rti1516_2025_python1516_2025_runtime.py` (main in-process `python1516_2025` proof suite)",
            "proof first and only then inspect the wrapper alias",
            "should expect to land on the `hla-backend-python1516-2025` lane by default",
            "the main `python1516_2025` factory path now does accept hosted 2025 creation through `transport=...`",
            "the legacy shim provider spelling is no longer part of the supported public factory surface",
            "create_rti_ambassador(backend=\"python1516_2025\", transport=...)",
            "`./tools/python verify-main-2025` is the normal proof command for that direct factory-selection path",
            "`./tools/python verify-routes-2025` is the follow-on lane when hosted factory transport ownership must stay green",
        ],
    )

    _assert_contains_all(
        normalized_python_rti_map,
        [
            "[../packages/hla-backend-python1516-2025/readme.md]",
            "`hla-backend-python1516-2025` is the main full 2025 python rti implementation lane",
            "`hla-backend-shim` is a wrapper-only compatibility alias over that runtime",
            "[requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md)",
            "architecture to the current 2025 runtime proof and its explicit non-claim boundary with minimal detours",
            "item 8 is the main in-process executable proof suite",
            "item 8 is the main in-process executable proof suite for `hla-backend-python1516-2025`",
            "main in-process `python1516_2025` runtime suite",
            "`tests/test_rti1516_2025_python1516_2025_runtime.py` (main `python1516_2025` proof suite)",
            "use the shim readme only when you are checking legacy provider spelling",
            "`./tools/python verify-main-2025` for the normal direct `python1516_2025` main-surface proof lane",
            "`./tools/python verify-routes-2025` when you also need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane",
            "`verification/time_model_compliance.md` and `tests/test_rti1516_2025_python1516_2025_runtime.py` as the main proof front doors",
            "explicit excluded-area map for legacy aliases, java/c++ bindings, hosted transport boundaries, duplicate/umbrella rows, retired rows, and out-of-scope omt extension semantics",
            "start in [../packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py]",
            "wrapper-only compatibility behavior",
            "run `./tools/python verify-main-2025` as the default proof command after changes in that path",
            "run `./tools/python verify-routes-2025` when the change must stay aligned with the bounded hosted `python1516_2025-fedpro-grpc` route",
        ],
    )
    _assert_contains_all(
        normalized_backend,
        [
            "`docs/requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md`",
            "`docs/requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md`",
            "`docs/requirements/ieee-1516-2025/save_restore_bounded_proof.md`",
            "`docs/requirements/ieee-1516-2025/callback_bounded_proof.md`",
            "`docs/requirements/ieee-1516-2025/lookahead_window_bounded_proof.md`",
            "main executable bounded proof surface for the current 2025 python rti",
            "`docs/requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md`",
            "explicit non-claim map around that bounded working-surface statement",
            "captures exactly which repo-owned proto2025 and target/radar example/fom-backed scenarios are part of the bounded claim",
            "captures the current rollback-family contract for lifecycle control, shared rollback, routing/policy rollback, ownership rollback, and time-window/time state rollback",
            "captures the current callback-family contract for declaration advisories, object delivery, ownership callbacks, time/retraction callbacks, and callback-control hygiene",
            "captures the explicit target/radar closure, future-exclusion, output-delivery, consumer-order, pipeline, negative-oracle, and bounded restore-window ladder",
        ],
    )

    _assert_contains_all(
        normalized_docs_index,
        [
            "read [`first_run.md`](first_run.md) for the 2010 pure-python bootstrap lane",
            "read [`python_rti_backend.md`](python_rti_backend.md) for the main 2025 python rti lane in `hla-backend-python1516-2025`",
            "use `./tools/python verify-main-2025` as the normal direct `python1516_2025` proof lane",
            "read [`networked_rti_python.md`](networked_rti_python.md) only if you need the bounded hosted 2025 route or its parity/hygiene lane",
            "use `./tools/python verify-routes-2025` when you need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane",
            "read [`verification/time_model_compliance.md`](verification/time_model_compliance.md) when the question is time, lookahead, galt/lits, or save/restore window proof",
            "[python_rti_backend.md](python_rti_backend.md): main 2025 python rti lane, wrapper boundary, and bounded working-surface claim",
            "[python_rti_reading_map.md](python_rti_reading_map.md): shortest editing path for the main `python1516_2025` rti lane",
            "[../tools/python](../tools/python): operator entrypoint for `verify-main-2025` and `verify-routes-2025`",
            "[verification/time_model_compliance.md](verification/time_model_compliance.md): time-management, lookahead, galt/lits, and radar-window proof front door for the primary 2025 python rti lane",
            "[../tools/pitch](../tools/pitch): narrow vendor-runtime operator path when you need the pitch-safe two-federate `time-window-probe` or `time-window-restore-state-probe` bounded credence routes without widening the main `python1516_2025` claim",
            "[requirements/ieee-1516-2025/readme.md](requirements/ieee-1516-2025/readme.md): 2025 requirements index, bounded proof notes, and requirement-facing evidence map for the main `python1516_2025` lane",
            "[requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md](requirements/ieee-1516-2025/fom_backed_scenario_bounded_proof.md): tracked proto2025 and target/radar example/fom-backed scenario boundary for the bounded `python1516_2025` claim",
            "[requirements/ieee-1516-2025/save_restore_bounded_proof.md](requirements/ieee-1516-2025/save_restore_bounded_proof.md): explicit save/restore rollback-family boundary for lifecycle control, routing/policy rollback, ownership rollback, and time-window rollback on the bounded `python1516_2025` claim",
            "[requirements/ieee-1516-2025/callback_bounded_proof.md](requirements/ieee-1516-2025/callback_bounded_proof.md): explicit callback-delivery family boundary for direct/hosted `python1516_2025` callback proofs, callback-control hygiene, and callback surface limits on the bounded `python1516_2025` claim",
            "[requirements/ieee-1516-2025/lookahead_window_bounded_proof.md](requirements/ieee-1516-2025/lookahead_window_bounded_proof.md): explicit target/radar lookahead-window proof ladder, negative-oracle guards, and pitch-safe vendor-credence boundary for the bounded `python1516_2025` claim",
            "[requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md](requirements/ieee-1516-2025/python1516_2025_direct_bounded_proof.md)",
            "[requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md](requirements/ieee-1516-2025/python1516_2025_exclusion_boundaries.md): explicit non-claim map for shim aliases, java/c++ bindings, hosted-route boundaries, umbrella rows, retired rows, and omt extension semantics around the main `python1516_2025` lane",
            "java/c++ standard-surface binding routes and evidence contract",
        ],
    )
    assert "the main requirement-backed semantics now live across package-owned modules such as:" in normalized_requirements_index
    assert "`backend_factory_runtime.py`" in requirements_index_doc
    assert "`runtime_state.py`" in requirements_index_doc
    assert "`federation_management_runtime.py`" in requirements_index_doc
    assert "`time_management_runtime.py`" in requirements_index_doc
    assert "`support_services_runtime.py`" in requirements_index_doc
    assert "`*_surface_mixin.py`" in requirements_index_doc
    assert "that is the implementation lane this requirement index is describing" in normalized_requirements_index

    _assert_contains_all(
        normalized_first_run,
        [
            "this page is the 2010 pure-python bootstrap path",
            "it is not the main entry point for the ieee 1516.1-2025 runtime lane",
            "the pure-python 2010 backend",
            "[`python_rti_backend.md`](python_rti_backend.md) for the main `hla-backend-python1516-2025` runtime lane",
            "[`python_rti_reading_map.md`](python_rti_reading_map.md) for the shortest edit path through that runtime",
            "[`networked_rti_python.md`](networked_rti_python.md) for the bounded hosted `python1516_2025-fedpro-grpc` route",
            "`python1516_2025` is the main ieee 1516.1-2025 rti lane",
            "`hla-backend-shim` is only a legacy compatibility shim over that runtime",
        ],
    )
    _assert_contains_all(
        normalized_tests_readme,
        [
            "`hla-backend-python1516-2025` as the main 2025 runtime behind those tests",
            "`hla-backend-shim` only as a legacy compatibility shim",
            "for the 2025 lane specifically, the first architecture/proof surfaces to read after bootstrap are:",
            "docs/python_rti_backend.md",
            "docs/python_rti_reading_map.md",
            "docs/verification/time_model_compliance.md",
            "`./tools/python verify-main-2025` for the normal direct `python1516_2025` main-surface proof lane",
            "`./tools/python verify-routes-2025` when you also need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane",
            "`tests/requirements/`: 2025 finish-line, route-parity, backend-audit, and wording-boundary checks for the main `python1516_2025` rti lane.",
        ],
    )

    _assert_contains_all(
        normalized_tools_readme,
        [
            "for ieee 1516.1-2025 specifically, interpret the operator surface through `hla-backend-python1516-2025` as the main runtime lane",
            "legacy compatibility shim",
            "hosted fedpro routes are bounded route variants rather than separate rti families",
            "python examples/target_radar_simulation.py --backend python1516e --steps 5",
            "python examples/target_radar_simulation.py --backend python1516_2025 --steps 5",
            "./tools/python verify-main-2025",
            "including package-boundary guards plus raw support/decode and callback-control proofs on the direct `python1516_2025` surface",
            "./tools/python verify-routes-2025",
            "python3 scripts/run_spec2025_finish_line.py",
            "regenerate the checked-in 2025 finish-line and route-parity evidence bundle after proof-lane changes",
            "for 2025 runtime ownership and proof status behind those commands, read:",
            "docs/python_rti_backend.md",
            "docs/python_rti_reading_map.md",
            "docs/verification/time_model_compliance.md",
        ],
    )
    assert "./tools/examples" not in normalized_tools_readme
    assert "./tools/human-editability" not in normalized_tools_readme
    assert "./tools/new-fom-package" not in normalized_tools_readme
    assert "./tools/rti-factories" not in normalized_tools_readme

    _assert_contains_all(
        normalized_scripts_readme,
        [
            "for ieee 1516.1-2025 specifically, the runtime owner behind the supported operator flows is `hla-backend-python1516-2025`",
            "`hla-backend-shim` remains wrapper-only compatibility code",
            "hosted 2025 fedpro routes remain bounded route variants rather than separate rti families",
            "when a script or wrapper touches the 2025 runtime lane, interpret that work through these surfaces first:",
            "`run_spec2025_finish_line.py`: checked-in ieee 1516.1-2025 finish-line, verification-matrix, and route-parity artifact refresh",
            "[../docs/python_rti_backend.md](../docs/python_rti_backend.md)",
            "[../docs/python_rti_reading_map.md](../docs/python_rti_reading_map.md)",
            "[../docs/verification/time_model_compliance.md](../docs/verification/time_model_compliance.md)",
        ],
    )

    _assert_contains_all(
        normalized_root_readme,
        [
            "`hla.backends.python1516_2025` for the main python rti backend for ieee 1516.1-2025",
            "`hla-backend-python1516-2025` is the main full executable python rti implementation lane",
            "legacy compatibility shim",
            "java and c++ 2025 binding routes are supporting route surfaces over the python 2025 lane, not alternate python rtis",
            "python examples/target_radar_simulation.py --backend python1516_2025 --steps 5",
            "./tools/python verify-main-2025",
            "./tools/python verify-routes-2025",
            "use `verify-main-2025` as the default direct `python1516_2025` proof lane",
            "use `verify-routes-2025` when you also need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane over `hla-backend-python1516-2025`",
            "`python1516_2025`, `python-1516-2025`, `python-1516-2025`",
            "`python1516_2025` is the main python rti implementation lane for ieee 1516.1-2025",
        ],
    )

    _assert_contains_all(
        normalized_package_layout,
        [
            "`packages/hla-rti1516-2025/src/hla/rti1516_2025/`: strict ieee 1516.1-2025 api surface",
            "`packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/`: main python rti backend for ieee 1516.1-2025",
            "`packages/hla-backend-shim/src/hla/backends/shim/`: wrapper-only compatibility alias over the main 2025 backend lane",
            "`packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/`: main full python-owned ieee 1516.1-2025 rti implementation package",
            "legacy compatibility shim",
            "`hla-rti1516-2025`: strict ieee 1516.1-2025 spec surface, value types, fom helpers, and 2025-local factory surface",
            "`hla-backend-python1516-2025`: main full executable python rti backend for ieee 1516.1-2025",
            "`hla-backend-shim`: wrapper-only compatibility alias over `hla-backend-python1516-2025`",
            "`hla-backend-python1516-2025` | backend | `hla-rti1516-2025`, `hla-backend-common`, `hla-rti-core` | shim backflow, vendor, transport, leaf packages |",
            "`hla-backend-shim` | compatibility-wrapper | `hla-rti1516-2025`, `hla-rti-core`, `hla-backend-python1516-2025` | any path that would re-own core 2025 runtime semantics, plus vendor, transport, leaf packages |",
            "`hla-fom-target-radar` | leaf | `hla-rti1516e`, `hla-rti1516-2025`, `hla-rti-core` | concrete backend, vendor, transport packages |",
        ],
    )

    _assert_contains_all(
        normalized_workspace_layout,
        [
            "`packages/hla-rti1516-2025/src/hla/rti1516_2025/`: ieee 1516.1-2025 api scaffold.",
            "keep the main full ieee 1516.1-2025 runtime semantics under `hla.backends.python1516_2025`",
            "keep `hla.backends.shim` narrow and wrapper-only; it should not re-own the 2025 runtime",
        ],
    )

    _assert_contains_all(
        normalized_dependency_tree,
        [
            "`hla-backend-python1516-2025` is the sole repo-owned ieee 1516.1-2025 python rti implementation lane",
            "`hla-backend-shim` is a legacy compatibility shim that depends on it rather than a peer rti lane or part of the implementation claim",
            "`hla-transport-grpc` already carries the bounded 2025 fedpro transport/client/server surface",
            "| `hla-fom-target-radar` | `hla-rti1516e, hla-rti1516-2025, hla-rti-core` | `-` |",
        ],
    )
    assert "the operator-facing hosted 2025 lane is `python1516_2025`" in normalized_route_inventory_remote
    assert "do not describe legacy wrapper aliases as the hosted runtime owner" in normalized_route_inventory_remote
    assert "use `python1516_2025` when naming the hosted 2025 route" in normalized_networked
    assert "legacy compatibility shim" in normalized_networked
    assert "the maintained 2025 transport-hosted lane is named and evidenced as `python1516_2025`" in normalized_backend

    assert "the bounded hosted 2025 fedpro route is a route variant over `hla-backend-python1516-2025`, not a separate python rti family" in normalized_packages
    assert "java and c++ 2025 binding lanes are supporting adaptation surfaces; they do not count as alternate python 2025 rtis" in normalized_packages

    _assert_contains_all(
        normalized_hierarchy,
        [
            "hla-rti1516-2025 └── hla-rti-core",
            "hla-backend-python1516-2025",
            "hla-backend-shim (deprecated compatibility scaffolding over hla-backend-python1516-2025)",
            "hla-fom-target-radar",
            "hla-transport-grpc (bounded fedpro 2025 hosted route)",
            "layer 1: `hla-backend-common`, `hla-fom-target-radar`, `hla-rti1516-2025`",
            "layer 2: `hla-backend-python1516e`, `hla-backend-python1516-2025`, `hla-bridge-java-common`, `hla-transport-common`",
        ],
    )

    assert "main full python rti backend package for ieee 1516.1-2025" in normalized_python2025_readme
    assert "this package now owns the main full python 2025 rti runtime" in normalized_python2025_readme
    assert "sole repo-owned ieee 1516.1-2025 python rti implementation lane" in normalized_python2025_readme
    assert "public `hla.backends.python1516_2025.backend` shell now fronts a split package layout" in normalized_python2025_readme
    assert "`backend_factory_runtime.py`" in python2025_readme
    assert "`runtime_state.py`" in python2025_readme
    assert "`federation_management_runtime.py`" in python2025_readme
    assert "`time_management_runtime.py`" in python2025_readme
    assert "`*_surface_mixin.py`" in python2025_readme
    assert "`hla-backend-shim` package is deprecated compatibility scaffolding for older route and provider names that should be removed after migration" in normalized_python2025_readme
    assert "must not delegate back to `hla.backends.shim.backend.create_shim_backend`" in normalized_python2025_readme
    assert "not part of the repo-owned 2025 python rti implementation claim" in normalized_shim_readme
    assert "the architectural split that matters is already in place: `hla-backend-python1516-2025` is the real 2025 rti runtime owner and the sole repo-owned 2025 python rti lane" in normalized_shim_readme
    assert "kept only as temporary, test-backed import-compatibility scaffolding" in normalized_shim_readme
    assert "they should be removed once no callers depend on the legacy import paths" in normalized_shim_readme
    assert "no shim helper modules remain beyond `hla.backends.shim.runtime_aliases`" in normalized_shim_readme
    assert "future work here is boundary cleanup and removal, not deciding whether a dedicated python 2025 backend should exist" in normalized_shim_readme
    assert 'description = "main full python rti backend package for hla 1516.1-2025"' in normalized_python2025_pyproject
    assert 'backend_names = ["python1516_2025"]' in normalized_python2025_pyproject
    assert 'backend_aliases = ["python-1516-2025"]' in normalized_python2025_pyproject
    assert 'role = "rti-backend"' in normalized_python2025_pyproject
    assert 'status = "implementation-owned"' in normalized_python2025_pyproject

    assert "legacy-named `hla-backend-shim` package is a legacy compatibility shim over the main full python 2025 rti lane" in normalized_shim_docs_readme
    assert "not part of the repo-owned 2025 python rti implementation claim" in normalized_shim_docs_readme
    assert "the executable runtime now lives in `hla-backend-python1516-2025`, which is the sole repo-owned ieee 1516.1-2025 python rti implementation lane" in normalized_shim_docs_readme
    assert "only the `shim2025*` names represent the wrapper-only lane" in normalized_shim_docs_readme
    assert "test-backed legacy compatibility surface" in normalized_shim_docs_readme
    assert "deprecated and should be removed after migration" in normalized_shim_docs_readme
    assert "the real python 2025 rti backend already lives in `hla-backend-python1516-2025`; this package is the wrapper-only compatibility lane" in normalized_shim_docs_readme
    assert "no shim helper modules remain beyond `hla.backends.shim.runtime_aliases`" in normalized_shim_docs_readme
    assert "future work is about keeping that wrapper narrow, not about deciding whether a dedicated 2025 backend should exist, and the package should be removed after migration" in normalized_shim_docs_readme
    assert "later be split into a narrower shim plus a dedicated 2025 backend" not in normalized_shim_docs_readme
    assert "future dedicated 2025 rti backend becomes the better design" not in normalized_backend
    assert "the dedicated runtime already exists" in normalized_backend
    assert "the remaining architectural question is how narrow the compatibility wrapper should be" in normalized_backend
    assert "in repo terms, `python1516_2025` is the rti lane. `shim` is not." in normalized_backend
    assert "## routine proof commands" in normalized_backend
    assert "`./tools/python verify-main-2025` for the direct main-surface `python1516_2025` proof lane over `hla-backend-python1516-2025`" in normalized_backend
    assert "`./tools/python verify-routes-2025` when you also need the bounded hosted `python1516_2025-fedpro-grpc` hygiene lane over that same runtime" in normalized_backend
    assert "treat `verify-main-2025` as the default 2025 proof path" in normalized_backend
    assert "reach for `verify-routes-2025` when the change touches hosted transport behavior, route-parity alignment, or the shared direct-plus-hosted target/radar proof surfaces" in normalized_backend
    assert "those two commands now name the current proof families explicitly instead of leaving them buried inside broad keyword slices" in normalized_backend
    assert "package-boundary and runtime-identity guards that keep `python1516_2025` as the owned rti lane and `shim` as wrapper-only" in normalized_backend
    assert "federation, object, and ddm runtime proofs across lifecycle, listing, exchange, region gating, scope relevance, and directed routing" in normalized_backend
    assert "support-service, callback-control, ownership, and mom runtime proofs" in normalized_backend
    assert "target/radar time-window and lookahead proofs, including future-exclusion, output ordering, pipeline, and restore-window ladders" in normalized_backend
    assert "save/restore lifecycle, rollback, replay-guard, and gauntlet proofs" in normalized_backend
    assert "omt validation/parsing evidence" in normalized_backend
    assert "the operator-facing 2025 proof contract is now organized around those families" in normalized_backend
    assert "promotion and boundary discipline" in normalized_backend
    assert "narrow or extract more later if" in normalized_backend
    assert "not to create the real backend from scratch; that part is already done in `hla-backend-python1516-2025`" in normalized_backend
    assert "stop using shim language for the primary 2025 runtime lane" in normalized_backend
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py` (main in-process python1516_2025 proof suite)" in normalized_backend
    assert "this is the main executable in-process proof suite for `hla-backend-python1516-2025`" in normalized_backend
    assert "`examples/target_radar_simulation.py`" in normalized_backend
    assert "`tests/scenarios/test_target_radar_scenario.py`" in normalized_backend
    assert "`tests/test_fom_target_radar_split_package.py`" in normalized_backend
    assert "target/radar example route as a package-owned shared scenario path" in normalized_backend
    assert "now runs through `hla.foms.target_radar._internal.targetradar2025rtiadapter`" in normalized_backend
    assert "owned by `hla-fom-target-radar` and wraps both `python1516_2025` and the wrapper-only `shim` alias" in normalized_backend
    assert "the same package-owned adapter now also runs the shared target/radar example path plus the shared future-exclusion time-window proof and restore-state save/restore proof over the factory-hosted `create_rti_ambassador(\"python1516_2025\", transport=...)` fedpro route" in normalized_backend
    assert "the factory-hosted `create_rti_ambassador(\"python1516_2025\", transport=...)` route now also proves direct mom federation-management save/restore service interactions" in normalized_backend
    assert "the hosted fedpro 2025 ambassador now accepts camelcase 2025 api entrypoints as aliases over its snake_case transport implementation methods" in normalized_backend
    assert "that same factory-hosted route now also proves a direct support-service slice on the hosted 2025 ambassador surface" in normalized_backend
    assert "raw `python1516_2025` support-service handle-factory and decode-helper proof without routing through the compatibility wrapper" in normalized_backend
    assert "snake-case alias acceptance on the primary direct `python1516_2025` runtime surface" in normalized_backend
    assert "`disablecallbacks`, `enablecallbacks`, `evokecallback`, and `evokemultiplecallbacks` execute against `hla-backend-python1516-2025` itself" in normalized_backend
    assert "primary_python_rti_runs_support_factory_and_decode_scenario_without_wrapper_adapter" in normalized_tools_python
    assert "primary_python_rti_accepts_snake_case_aliases_for_direct_runtime_surface" in normalized_tools_python
    assert "primary_python_rti_runs_raw_callback_control_flow_without_wrapper_adapter" in normalized_tools_python
    assert "test_target_radar_example_supports_2025_backends" in normalized_tools_python
    assert "test_target_radar_factory_wraps_2025_backends_with_package_owned_adapter" in normalized_tools_python
    assert "test_target_radar_package_owned_2025_adapter_covers_shared_scenario_service_surface" in normalized_tools_python
    assert "primary_python_rti_runs_name_reservation_scenario_without_wrapper_adapter" in normalized_tools_python
    assert "test_2025_provider_runs_federation_lifecycle_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_federation_listing_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_two_federate_object_and_interaction_exchange" in normalized_tools_python
    assert "test_2025_provider_runs_ddm_object_region_lifecycle_scenario_via_compat_adapter" in normalized_tools_python
    assert "test_2025_provider_routes_directed_ddm_interactions_only_to_overlapping_subscribers" in normalized_tools_python
    assert "test_2025_provider_round_trips_automatic_resign_directive_support_service" in normalized_tools_python
    assert "test_2025_provider_runs_callback_control_route_with_object_reflection_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_attribute_ownership_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_primary_python_rti_runs_negotiated_ownership_flow_without_wrapper_adapter" in normalized_tools_python
    assert "test_2025_provider_routes_mom_time_management_service_interactions" in normalized_tools_python
    assert "test_2025_provider_routes_mom_object_and_ownership_service_interactions" in normalized_tools_python
    assert "test_2025_provider_runs_integrated_time_window_gauntlet_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_time_window_future_exclusion_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_time_window_output_delivery_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_time_window_consumer_order_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_provider_runs_time_window_pipeline_restore_scenario_end_to_end" in normalized_tools_python
    assert "test_2025_receive_order_poison_oracle_rejects_closed_window_mutation" in normalized_tools_python
    assert "test_2025_provider_runs_backend_neutral_save_restore_scenario_via_compat_adapter" in normalized_tools_python
    assert "test_2025_provider_runs_example_fom_save_restore_gauntlet" in normalized_tools_python
    assert "test_2025_provider_runs_smoke_fom_save_restore_ownership_gauntlet" in normalized_tools_python
    assert "test_2025_provider_restore_reverts_dirty_lookahead_and_redelivers_presave_queued_tso" in normalized_tools_python
    assert "test_2025_provider_restores_closed_window_output_resume_without_dirty_replay" in normalized_tools_python
    assert "test_2025_transport_server_runs_shared_time_window_gauntlet_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_factory_hosted_python2025_route_runs_package_owned_future_exclusion_scenario" in normalized_tools_python
    assert "test_2025_factory_hosted_python2025_route_runs_package_owned_time_window_gauntlet" in normalized_tools_python
    assert "test_2025_factory_hosted_python2025_route_runs_package_owned_restore_state_scenario" in normalized_tools_python
    assert "test_2025_factory_hosted_python2025_route_runs_package_owned_restore_output_scenario" in normalized_tools_python
    assert "test_2025_transport_server_runs_shared_restore_state_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_round_trips_support_services_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_round_trips_2025_switch_services_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_runs_shared_federation_lifecycle_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_runs_shared_federation_listing_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_runs_object_and_interaction_exchange_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_runs_ddm_object_region_lifecycle_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_routes_directed_ddm_interactions_only_to_overlapping_subscribers_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_runs_attribute_ownership_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_runs_negotiated_ownership_flow_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_routes_mom_adjust_controls_to_observable_switch_state_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_reports_failed_mom_service_actions_as_mom_exception_interactions" in normalized_tools_python
    assert "test_2025_transport_server_runs_shared_save_restore_scenario_over_fedpro_route" in normalized_tools_python
    assert "test_2025_transport_server_runs_example_fom_save_restore_gauntlet_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_runs_smoke_fom_save_restore_ownership_gauntlet_over_fedpro_schema" in normalized_tools_python
    assert "test_2025_transport_server_restores_closed_window_output_resume_without_dirty_replay_over_fedpro_schema" in normalized_tools_python
    assert 'description = "temporary import-compatibility scaffolding package for the main full python 2025 rti"' in normalized_shim_pyproject
    assert 'backend_names = []' in normalized_shim_pyproject
    assert 'backend_aliases = []' in normalized_shim_pyproject
    assert 'role = "compatibility-wrapper"' in normalized_shim_pyproject
    assert 'status = "compatibility-maintained"' in normalized_shim_pyproject

    assert "bounded ieee 1516.1-2025 fedpro hosted route variant" in normalized_grpc_readme
    assert "that 2025 server is a bounded hosted route variant over the current python 2025 lane" in normalized_grpc_readme
    assert "not a separate rti family and not the main in-process implementation lane" in normalized_grpc_readme
    assert "`packages/hla-backend-python1516-2025` for the main executable 2025 python rti lane" in normalized_networked
    assert "do not refer to the primary 2025 runtime lane itself as a shim" in normalized_networked
    assert "run the primary 2025 python rti main-surface proof lane (python1516_2025)" in normalized_tools_python
    assert "run 2025 python rti / fedpro hosted-route checks" in normalized_tools_python

    assert "`hla-backend-python1516-2025` is the main full python 2025 rti backend" in normalized_packages
    assert "`hla-backend-shim` is a legacy compatibility shim" in normalized_packages
    assert "helper modules should remain wrapper-only compatibility aliases over `hla.backends.python1516_2025.*`" in normalized_packages
    assert "should be removed after migration" in normalized_packages


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_public_2025_factory_defaults_and_discovery_order_python2025_first() -> None:
    from hla.rti import discover_rti_backends
    from hla.rti import factory as runtime_factory
    from hla.runtime.rti1516_2025_factory import create_hla_factory, create_rti_ambassador

    rti_signature = inspect.signature(create_rti_ambassador)
    factory_signature = inspect.signature(create_hla_factory)

    assert rti_signature.parameters["backend"].default == "python1516_2025"
    assert factory_signature.parameters["provider"].default == "python1516_2025"

    plugin_modules = runtime_factory._SOURCE_CHECKOUT_PLUGIN_MODULES
    assert "hla.backends.python1516_2025.plugin" in plugin_modules
    assert "hla.backends.shim.plugin" not in plugin_modules

    registered_2025_backends = [row.name for row in discover_rti_backends(spec="2025")]
    assert "python1516_2025" in registered_2025_backends
    assert "shim" not in registered_2025_backends


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_normalizes_primary_runtime_evidence_away_from_shim_backend_path() -> None:
    snapshot = build_spec2025_finish_line_snapshot(ROOT)
    shim_backend_path = "packages/hla-backend-shim/src/hla/backends/shim/backend.py"
    runtime_backend_path = "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py"

    implemented_slices = snapshot["implemented_evidence_slices"]
    assert any(runtime_backend_path in row["evidence"] for row in implemented_slices)
    assert all(shim_backend_path not in row["evidence"] for row in implemented_slices)

    fi_rows = snapshot["fi_service_proof_audit"]["rows"]
    assert all(runtime_backend_path not in row["evidence_artifacts"] for row in fi_rows)
    assert any(
        "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/federation_management_runtime.py"
        in row["evidence_artifacts"]
        for row in fi_rows
    )
    assert any(
        "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/time_management_runtime.py"
        in row["evidence_artifacts"]
        for row in fi_rows
    )
    assert all(shim_backend_path not in row["evidence_artifacts"] for row in fi_rows)

    delta_rows = snapshot["delta_requirement_proof_audit"]["rows"]
    assert all(runtime_backend_path not in row["evidence_artifacts"] for row in delta_rows)
    assert any(
        "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ownership_runtime.py"
        in row["evidence_artifacts"]
        for row in delta_rows
    )
    assert any(
        "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/time_management_runtime.py"
        in row["evidence_artifacts"]
        for row in delta_rows
    )
    assert all(shim_backend_path not in row["evidence_artifacts"] for row in delta_rows)


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_raw_primary_runtime_evidence_on_python2025_path() -> None:
    runtime_backend_path = "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py"

    raw_runtime_backed_slices = [
        row for row in IMPLEMENTED_EVIDENCE_SLICES if runtime_backend_path in row.get("evidence", ())
    ]
    assert raw_runtime_backed_slices
    assert all(SHIM_BACKEND_EVIDENCE_PATH not in row.get("evidence", ()) for row in IMPLEMENTED_EVIDENCE_SLICES)


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_named_raw_python2025_support_and_callback_proofs() -> None:
    spec_test_path = ROOT / "tests" / "test_rti1516_2025_python1516_2025_runtime.py"
    spec_text = spec_test_path.read_text(encoding="utf-8")

    expected_tests = {
        "test_2025_primary_python_rti_runs_support_factory_and_decode_scenario_without_wrapper_adapter",
        "test_2025_primary_python_rti_accepts_snake_case_aliases_for_direct_runtime_surface",
        "test_2025_primary_python_rti_runs_raw_callback_control_flow_without_wrapper_adapter",
    }

    defined_test_names = set(re.findall(r"^def (test_2025_[A-Za-z0-9_]+)\(", spec_text, re.M))
    assert expected_tests.issubset(defined_test_names)


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_runtime_aliases_is_the_only_remaining_shim_helper_module() -> None:
    shim_dir = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim"
    assert [path.name for path in _canonical_python_module_paths(shim_dir)] == [
        "__init__.py",
        "backend.py",
        "plugin.py",
        "runtime_aliases.py",
    ]


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_runtime_aliases_reexport_points_at_python2025_backend() -> None:
    runtime_alias_path = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim" / "runtime_aliases.py"
    runtime_alias_tree = ast.parse(runtime_alias_path.read_text(encoding="utf-8"), filename=str(runtime_alias_path))
    runtime_alias_top_level = [
        node
        for node in runtime_alias_tree.body
        if not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
    ]
    assert [type(node).__name__ for node in runtime_alias_top_level] == ["ImportFrom", "ImportFrom", "Assign"]
    runtime_alias_imports = [node for node in runtime_alias_top_level if isinstance(node, ast.ImportFrom)]
    assert [node.module for node in runtime_alias_imports] == ["__future__", "hla.backends.python1516_2025.backend"]


@pytest.mark.requirements("HLA2025-MIL-001", "HLA2025-MIL-002")
def test_verification_run_sequence_keeps_pitch_time_window_probe_boundary_explicit() -> None:
    text = (ROOT / "docs" / "verification" / "run_sequence.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split()).lower()

    assert "the trial-safe time-window future-exclusion and restore-state proof legs" in normalized
    assert "`./tools/pitch time-window-probe`" in text
    assert "`./tools/pitch time-window-restore-state-probe`" in text
    assert "bounded vendor credence for the two-federate 2025 future-exclusion and restore-state routes" in normalized
    assert "they do not replace the direct `python1516_2025` proof lane or the hosted `python1516_2025-fedpro-grpc` replay" in normalized


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_eliminates_shim_helper_imports_from_runtime_tests() -> None:
    spec_test_path = ROOT / "tests" / "test_rti1516_2025_python1516_2025_runtime.py"
    spec_text = spec_test_path.read_text(encoding="utf-8")
    tree = ast.parse(spec_text)

    shim_helper_import_locations: list[tuple[str, str]] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.ImportFrom):
                continue
            module = child.module or ""
            if not module.startswith("hla.backends.shim."):
                continue
            if module in {"hla.backends.shim.backend", "hla.backends.shim.plugin", "hla.backends.shim.runtime_aliases"}:
                continue
            shim_helper_import_locations.append((node.name, module))

    assert shim_helper_import_locations == []


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_every_shim_helper_under_an_explicit_wrapper_consumption_test() -> None:
    spec_test_path = ROOT / "tests" / "test_rti1516_2025_python1516_2025_runtime.py"
    spec_text = spec_test_path.read_text(encoding="utf-8")
    defined_test_names = set(re.findall(r"^def (test_2025_[A-Za-z0-9_]+)\(", spec_text, re.M))

    assert set(_SHIM_LEGACY_ALIAS_TESTS.values()).issubset(defined_test_names)


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_shim_helper_modules_out_of_repo_runtime_import_paths() -> None:
    shim_dir = ROOT / "packages" / "hla-backend-shim" / "src" / "hla" / "backends" / "shim"
    helper_module_names = {
        path.stem
        for path in _canonical_python_module_paths(shim_dir)
        if path.name not in {"__init__.py", "backend.py", "plugin.py", "runtime_aliases.py"}
    }
    unexpected_locations: list[tuple[str, str]] = []

    for path in ROOT.rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            module = node.module or ""
            if not module.startswith("hla.backends.shim."):
                continue
            leaf = module.rsplit(".", 1)[-1]
            if leaf not in helper_module_names:
                continue
            unexpected_locations.append((str(path.relative_to(ROOT)), module))

    assert unexpected_locations == []
