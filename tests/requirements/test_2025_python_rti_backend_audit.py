from __future__ import annotations

import ast
import inspect
from pathlib import Path
import re
import warnings

import pytest
from hla.verification.repo_internal.requirements.loaders import (
    load_backend_resolution_catalog,
    load_canonical_requirement_catalog,
)

ROOT = Path(__file__).resolve().parents[2]
ICLOUD_DUPLICATE_SUFFIX = re.compile(r" \d+(?=\.[^.]+$|$)")
CANONICAL_REQUIREMENTS = ROOT / "requirements/2025/canonical_requirements.json"
BACKEND_RESOLUTION = ROOT / "requirements/2025/backend_resolution.json"


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


def _canonical_2025_rows() -> tuple[object, ...]:
    return load_canonical_requirement_catalog(CANONICAL_REQUIREMENTS).rows


def _backend_2025_rows() -> tuple[object, ...]:
    return load_backend_resolution_catalog(BACKEND_RESOLUTION).rows


def _binding_route_rows() -> list[object]:
    return [row for row in _backend_2025_rows() if row.resolution_type == "binding-route-resolution"]

@pytest.mark.requirements(
    "HLA2025-TRACE-001",
    "HLA2025-TRACE-002",
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_snapshot_tracks_live_evidence_and_boundaries() -> None:
    direct_proof_text = (
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "python1516_2025_direct_bounded_proof.md"
    ).read_text(encoding="utf-8")
    hosted_proof_text = (
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "hosted_fedpro_bounded_proof.md"
    ).read_text(encoding="utf-8")
    binding_boundary_text = (
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "binding_and_hosted_route_boundaries.md"
    ).read_text(encoding="utf-8")
    exclusion_boundary_text = (
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "python1516_2025_exclusion_boundaries.md"
    ).read_text(encoding="utf-8")
    federation_boundary_text = (
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "federation_management_bounded_proof.md"
    ).read_text(encoding="utf-8")
    pitch_boundary_text = (
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "pitch_202x_bounded_comparison.md"
    ).read_text(encoding="utf-8")
    test_surface_text = (ROOT / "docs" / "test_surface.md").read_text(encoding="utf-8")
    grpc_transport_text = (ROOT / "tests" / "transport" / "test_grpc_transport_2025.py").read_text(encoding="utf-8")
    runtime_text = (ROOT / "tests" / "test_rti1516_2025_python1516_2025_runtime.py").read_text(encoding="utf-8")
    canonical_rows = _canonical_2025_rows()
    binding_rows = _binding_route_rows()

    covered_rows = [row for row in canonical_rows if row.canonical_status == "covered"]
    duplicate_rows = [row for row in canonical_rows if row.canonical_status == "duplicate/umbrella"]
    legacy_rows = [row for row in canonical_rows if row.canonical_status == "retired/legacy-only"]

    assert len(covered_rows) == 645
    assert len(duplicate_rows) == 22
    assert len(legacy_rows) == 24
    assert len(canonical_rows) == len(covered_rows) + len(duplicate_rows) + len(legacy_rows) == 691
    assert len(binding_rows) == 196
    assert sum(1 for row in binding_rows if row.backend_fields["java_surface"] == "present") == 196
    assert sum(1 for row in binding_rows if row.backend_fields["cpp_surface"] == "present") == 196
    assert sum(1 for row in binding_rows if row.backend_fields["fedpro_surface"] == "present") == 191
    assert sum(1 for row in binding_rows if row.backend_fields["fedpro_surface"] == "present-via-class-and-instance-split") == 1
    assert sum(
        1
        for row in binding_rows
        if row.backend_fields["fedpro_surface"] == "not-present-route-boundary-callback-pump-control"
    ) == 4

    fedpro_split_rows = [
        row for row in binding_rows if row.backend_fields["fedpro_surface"] == "present-via-class-and-instance-split"
    ]
    assert [row.requirement_id for row in fedpro_split_rows] == ["HLA2025-FI-SVC-070"]

    fedpro_boundary_rows = [
        row
        for row in binding_rows
        if row.backend_fields["fedpro_surface"] == "not-present-route-boundary-callback-pump-control"
    ]
    assert {row.requirement_id for row in fedpro_boundary_rows} >= {
        "HLA2025-FI-SVC-193",
        "HLA2025-FI-SVC-194",
        "HLA2025-FI-SVC-195",
        "HLA2025-FI-SVC-196",
    }

    _assert_contains_all(
        direct_proof_text,
        [
            "`hla-backend-python1516-2025` is the sole repo-owned IEEE 1516.1-2025 Python RTI",
            "`./tools/python verify-main-2025` is the default direct proof lane",
            "`./tools/python verify-routes-2025` is the companion hosted hygiene lane",
        ],
    )
    _assert_contains_all(
        hosted_proof_text,
        [
            "`python1516_2025-fedpro-grpc` is a hosted route variant over",
            "not a separate 2025 RTI owner",
            "`./tools/python verify-routes-2025` is the maintained hosted hygiene lane",
        ],
    )
    normalized_binding_boundary_text = _normalize(binding_boundary_text)
    _assert_contains_all(
        normalized_binding_boundary_text,
        [
            "the java and c++ packages remain adapter/binding surfaces over that runtime",
            "the hosted fedpro route remains a transport-facing runtime slice over the same lane",
            "not a second rti implementation lane",
        ],
    )
    _assert_contains_all(
        exclusion_boundary_text,
        [
            "Legacy aliases and shim imports",
            "Java/C++ bindings",
            "Hosted transport boundaries",
            "Duplicate/umbrella rows",
            "Retired/legacy-only rows",
            "OMT extension semantics",
        ],
    )
    normalized_pitch_boundary_text = _normalize(pitch_boundary_text)
    _assert_contains_all(
        normalized_pitch_boundary_text,
        [
            "backend-resolution note, not a second 2025 rti-owner claim",
            "does not by itself prove ieee 1516.1-2025 closure",
            "that vendor label is backend-resolution terminology only.",
        ],
    )
    _assert_contains_all(
        federation_boundary_text,
        [
            "Current exact execution-membership evidence anchors for this 2025 reading",
            "`./tools/test-focus run execution-membership`",
            "`./tools/python verify-main-2025`",
            "`./tools/python verify-routes-2025`",
        ],
    )
    _assert_contains_all(
        test_surface_text,
        [
            "| `unit-python-2025-core` | `./tools/test-surface run unit-python-2025-core` | primary `python1516_2025` unit shard",
            "| `unit-transport-local` | `./tools/test-surface run unit-transport-local` | hosted transport shard for gRPC and REST tests without vendor-runtime lanes |",
            "| `python1516_2025-main` | `./tools/python verify-main-2025` | primary `python1516_2025` main-surface proof lane",
            "| `python1516_2025-routes` | `./tools/python verify-routes-2025` | bounded `python1516_2025` plus hosted FedPro 2025 route checks",
        ],
    )

    for anchor in (
        "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_runs_federation_lifecycle_negative_scenario_end_to_end",
        "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_runs_resign_precondition_scenario_end_to_end",
        "tests/test_rti1516_2025_python1516_2025_runtime.py::test_2025_provider_reports_federation_executions_and_members",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_join_precondition_matrix",
        "tests/scenarios/test_federation_management_backend_matrix.py::test_python_backend_resign_precondition_matrix",
        "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_federation_lifecycle_negative_scenario_over_fedpro_route",
        "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_join_precondition_scenario_over_fedpro_route",
        "tests/transport/test_grpc_transport_2025.py::test_2025_transport_server_runs_shared_resign_precondition_scenario_over_fedpro_route",
        "tests/transport/test_rest_transport.py::test_2025_rest_transport_server_runs_shared_federation_lifecycle_negative_scenario",
        "tests/transport/test_rest_transport.py::test_2025_rest_transport_server_runs_shared_join_precondition_scenario",
        "tests/transport/test_rest_transport.py::test_2025_rest_transport_server_runs_shared_resign_precondition_scenario",
    ):
        _assert_live_test_anchor(anchor)

    assert 'backend_info.details["counts_as_python_2025_rti"] is True' in runtime_text
    assert "counts_as_python_2025_rti is True" in grpc_transport_text


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
    backend_doc = (ROOT / "docs" / "python_rti_backend.md").read_text(encoding="utf-8")
    test_surface_doc = (ROOT / "docs" / "test_surface.md").read_text(encoding="utf-8")
    local_verification_commands_doc = (ROOT / "docs" / "local_verification_commands.md").read_text(encoding="utf-8")
    python_rti_map_doc = (ROOT / "docs" / "python_rti_reading_map.md").read_text(encoding="utf-8")
    requirements_index_doc = (ROOT / "docs" / "requirements" / "ieee-1516-2025" / "README.md").read_text(encoding="utf-8")
    python2025_readme = (ROOT / "packages" / "hla-backend-python1516-2025" / "README.md").read_text(encoding="utf-8")
    shim_readme = (ROOT / "packages" / "hla-backend-shim" / "README.md").read_text(encoding="utf-8")

    normalized_backend = _normalize(backend_doc)
    normalized_shim = _normalize(shim_readme)

    _assert_contains_all(
        normalized_backend,
        [
            "hla-backend-python1516-2025",
            "working python 2025 rti surface",
            "python1516_2025",
        ],
    )
    _assert_contains_all(
        test_surface_doc,
        [
            "./tools/python verify-main-2025",
            "./tools/python verify-routes-2025",
            "unit-python-2025-core",
            "unit-transport-local",
        ],
    )
    _assert_contains_all(
        local_verification_commands_doc,
        [
            "./tools/python verify-main-2025",
            "./tools/python verify-routes-2025",
        ],
    )
    _assert_contains_all(
        python_rti_map_doc,
        [
            "python1516_2025",
            "hla-backend-python1516-2025",
        ],
    )
    _assert_contains_all(
        requirements_index_doc,
        [
            "python1516_2025_direct_bounded_proof.md",
            "hosted_fedpro_bounded_proof.md",
            "binding_and_hosted_route_boundaries.md",
        ],
    )
    _assert_contains_all(
        python2025_readme,
        [
            "hla-backend-python1516-2025",
            "python1516_2025",
        ],
    )
    _assert_contains_all(
        normalized_shim,
        [
            "compatibility alias",
            "python 2025 backend",
        ],
    )


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
    shim_backend_path = "packages/hla-backend-shim/src/hla/backends/shim/backend.py"
    runtime_backend_path = "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py"
    requirements_index_text = (ROOT / "docs" / "requirements" / "ieee-1516-2025" / "README.md").read_text(encoding="utf-8")
    support_services_text = (
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "support_services_bounded_proof.md"
    ).read_text(encoding="utf-8")
    canonical_rows = load_canonical_requirement_catalog(CANONICAL_REQUIREMENTS).rows
    canonical_evidence_text = "\n".join("; ".join(row.evidence_refs) for row in canonical_rows)

    _assert_live_relative_path(runtime_backend_path)
    _assert_live_relative_path("packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/federation_management_runtime.py")
    _assert_live_relative_path("packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/time_management_runtime.py")
    _assert_live_relative_path("packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/ownership_runtime.py")
    _assert_live_relative_path("packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_services_runtime.py")

    assert runtime_backend_path not in canonical_evidence_text
    assert shim_backend_path not in canonical_evidence_text
    assert shim_backend_path not in requirements_index_text
    assert shim_backend_path not in support_services_text

    assert "federation_management_runtime.py" in requirements_index_text
    assert "time_management_runtime.py" in requirements_index_text
    assert (
        "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_services_runtime.py"
        in support_services_text
    )
    assert (
        "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/support_services_runtime.py"
        in canonical_evidence_text
    )


@pytest.mark.requirements(
    "HLA2025-MIL-001",
    "HLA2025-MIL-002",
    "HLA2025-MIL-003",
)
def test_2025_python_rti_backend_audit_keeps_raw_primary_runtime_evidence_on_python2025_path() -> None:
    shim_backend_path = "packages/hla-backend-shim/src/hla/backends/shim/backend.py"
    runtime_backend_path = "packages/hla-backend-python1516-2025/src/hla/backends/python1516_2025/backend.py"
    direct_proof_text = (
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "python1516_2025_direct_bounded_proof.md"
    ).read_text(encoding="utf-8")
    hosted_proof_text = (
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "hosted_fedpro_bounded_proof.md"
    ).read_text(encoding="utf-8")
    python_backend_text = (ROOT / "docs" / "python_rti_backend.md").read_text(encoding="utf-8")
    python_reading_map_text = (ROOT / "docs" / "python_rti_reading_map.md").read_text(encoding="utf-8")
    traceability_matrix_text = (ROOT / "docs" / "evidence" / "spec2025" / "traceability_matrix.json").read_text(
        encoding="utf-8"
    )

    _assert_live_relative_path(runtime_backend_path)
    assert runtime_backend_path in python_reading_map_text
    assert shim_backend_path in python_reading_map_text
    assert shim_backend_path not in traceability_matrix_text
    assert "`hla-backend-python1516-2025` is the sole repo-owned IEEE 1516.1-2025 Python RTI" in direct_proof_text
    assert "`tests/test_rti1516_2025_python1516_2025_runtime.py` is the main direct runtime" in direct_proof_text
    normalized_hosted_proof_text = _normalize(hosted_proof_text)
    assert "`python1516_2025-fedpro-grpc` is a hosted route variant over" in hosted_proof_text
    assert "rather than a second rti implementation family" in normalized_hosted_proof_text
    assert "full remote-rti semantics claim" in normalized_hosted_proof_text
    normalized_python_backend_text = _normalize(python_backend_text)
    assert "current reality: `hla-backend-python1516-2025` is the main full python 2025 rti implementation lane" in normalized_python_backend_text
    assert "ownership reality: `hla-backend-python1516-2025` is the sole repo-owned ieee 1516.1-2025 python rti implementation lane" in normalized_python_backend_text
    assert "compatibility reality: `hla-backend-shim` is a legacy compatibility shim over that lane" in normalized_python_backend_text


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
