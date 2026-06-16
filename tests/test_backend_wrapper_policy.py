from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

WRAPPER_MODULE_EXPECTATIONS = {
    "tests/vendors/test_certi_real_backend_exchange_matrix.py": {
        "run_two_federate_exchange_scenario",
        "run_synchronization_scenario",
        "run_support_factory_and_decode_scenario",
    },
    "tests/vendors/test_certi_real_backend_ownership_matrix.py": {
        "run_attribute_ownership_scenario",
        "run_negotiated_attribute_ownership_scenario",
    },
    "tests/vendors/test_certi_real_backend_time_matrix.py": {
        "run_section8_ordering_and_query_case",
        "run_section8_available_and_flush_case",
        "section8_matrix_config",
    },
    "tests/vendors/test_java_profile_backend_matrix.py": {
        "run_two_federate_exchange_scenario",
        "run_synchronization_scenario",
        "run_support_factory_and_decode_scenario",
        "run_attribute_ownership_scenario",
        "run_negotiated_attribute_ownership_scenario",
    },
    "tests/vendors/test_pitch_real_backend_matrix.py": {
        "run_synchronization_scenario",
        "run_federation_lifecycle_scenario",
        "run_save_restore_scenario",
        "run_transportation_type_scenario",
        "run_attribute_ownership_scenario",
        "run_negotiated_attribute_ownership_scenario",
    },
    "tests/vendors/test_portico_real_backend_matrix.py": {
        "run_two_federate_exchange_scenario",
        "run_synchronization_scenario",
    },
    "tests/vendors/test_real_vendor_runtime_smoke.py": {
        "run_federation_lifecycle_scenario",
        "run_two_federate_exchange_scenario",
        "run_save_restore_scenario",
        "run_suite_ddm_scenario",
    },
    "tests/transport/test_grpc_transport_python_server.py": {
        "run_two_federate_exchange_scenario",
        "run_synchronization_scenario",
        "run_attribute_ownership_scenario",
        "run_negotiated_attribute_ownership_scenario",
    },
    "tests/transport/test_grpc_transport_certi_server.py": {
        "run_two_federate_exchange_scenario",
        "run_synchronization_scenario",
        "run_attribute_ownership_scenario",
    },
}


def _load_module(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _top_level_harness_imports(module: ast.Module) -> set[str]:
    imports: set[str] = set()
    for node in module.body:
        if isinstance(node, ast.ImportFrom) and node.module == "hla.verification":
            imports.update(alias.name for alias in node.names)
    return imports


def _forbidden_internal_harness_imports(module: ast.Module) -> list[str]:
    imports: list[str] = []
    for node in module.body:
        if not isinstance(node, ast.ImportFrom) or node.module is None:
            continue
        if node.module.startswith("hla.verification.") and node.module != "hla.verification":
            imports.append(node.module)
    return imports


def _local_run_defs(module: ast.Module) -> list[str]:
    defs: list[str] = []
    for node in module.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("run_"):
            defs.append(node.name)
    return defs


def _referenced_names(module: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.Name):
            names.add(node.id)
    return names


def test_backend_and_transport_wrapper_modules_keep_shared_harness_entrypoints_explicit() -> None:
    for rel, expected_names in WRAPPER_MODULE_EXPECTATIONS.items():
        path = ROOT / rel
        module = _load_module(path)

        assert not _forbidden_internal_harness_imports(module), rel
        assert not _local_run_defs(module), rel

        harness_imports = _top_level_harness_imports(module)
        missing_imports = sorted(expected_names - harness_imports)
        assert not missing_imports, (rel, missing_imports)

        referenced_names = _referenced_names(module)
        missing_references = sorted(expected_names - referenced_names)
        assert not missing_references, (rel, missing_references)
