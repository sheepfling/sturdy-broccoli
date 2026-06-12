from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JAVA_PROFILE_MATRIX_PATH = ROOT / "tests" / "vendors" / "test_java_profile_backend_matrix.py"
TARGET_FUNCTIONS = {
    "test_inprocess_java_shim_time_factory_matrix": "run_two_federate_exchange_scenario",
    "test_inprocess_java_shim_backend_matrix": "run_two_federate_exchange_scenario",
    "test_inprocess_java_shim_synchronization_scenario": "run_synchronization_scenario",
    "test_inprocess_java_shim_support_factory_and_decode_scenario": "run_support_factory_and_decode_scenario",
    "test_inprocess_java_shim_ownership_scenario": "run_attribute_ownership_scenario",
    "test_inprocess_java_shim_negotiated_ownership_scenario": "run_negotiated_attribute_ownership_scenario",
    "test_certi_java_profile_backend_matrix": "run_two_federate_exchange_scenario",
}
SCENARIO_ENTRYPOINT_RE = re.compile(r"\b((?:run|probe)_[A-Za-z0-9_]+)\(")
DIRECT_BACKEND_CALL_RE = re.compile(
    r"\b(?:leader|wing|owner|acquirer|publisher|subscriber|rti)\.[A-Za-z_][A-Za-z0-9_]*\("
)


def _function_sources() -> dict[str, str]:
    source = JAVA_PROFILE_MATRIX_PATH.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(JAVA_PROFILE_MATRIX_PATH))
    functions: dict[str, str] = {}
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in TARGET_FUNCTIONS:
            segment = ast.get_source_segment(source, node)
            assert segment is not None, node.name
            functions[node.name] = segment
    return functions


def _scenario_entrypoints(source: str) -> list[str]:
    return SCENARIO_ENTRYPOINT_RE.findall(source)


def test_java_profile_matrix_wrappers_stay_shared_harness_driven() -> None:
    sources = _function_sources()
    assert set(TARGET_FUNCTIONS).issubset(sources)

    for function_name, runner_name in TARGET_FUNCTIONS.items():
        source = sources[function_name]
        assert _scenario_entrypoints(source) == [runner_name], function_name
        assert not DIRECT_BACKEND_CALL_RE.search(source), function_name
