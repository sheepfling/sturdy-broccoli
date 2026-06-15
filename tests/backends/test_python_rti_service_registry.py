from __future__ import annotations

import csv
import inspect
import subprocess
from io import StringIO
from pathlib import Path

from hla2010.raw_api import API_METADATA
from hla2010_rti_backend_common import Invocation
from hla2010_rti_python.backend import PythonRTIBackend
from hla2010_rti_python.service_registry import (
    PYTHON_RTI_NON_RTI_SERVICE_REASONS,
    PYTHON_RTI_SERVICE_HANDLERS,
    PYTHON_RTI_SERVICE_REGISTRY,
)
from tests.conftest import REPO_ROOT, load_traceability_json, read_repo_text
from tests.typed_json_models import PythonRtiServiceMapRow


ROOT = REPO_ROOT


def _ledger_rows() -> list[dict[str, str]]:
    return list(csv.DictReader(StringIO(read_repo_text("analysis/compliance/requirements_ledger.csv"))))


def _map_rows() -> list[PythonRtiServiceMapRow]:
    payload = load_traceability_json("python_rti_service_map.json")
    rows = payload.get("rows", [])
    assert isinstance(rows, list)
    return [PythonRtiServiceMapRow.from_mapping(row) for row in rows if isinstance(row, dict)]


def test_every_rti_method_has_a_registry_entry() -> None:
    assert set(PYTHON_RTI_SERVICE_REGISTRY) == set(API_METADATA["RTIambassador"])


def test_every_registry_entry_has_a_direct_callable_handler() -> None:
    for method_name in PYTHON_RTI_SERVICE_REGISTRY:
        target = PYTHON_RTI_SERVICE_HANDLERS[method_name]
        assert callable(target), method_name


def test_every_python_backend_service_function_has_a_registry_entry() -> None:
    assert set(PYTHON_RTI_SERVICE_HANDLERS) == set(PYTHON_RTI_SERVICE_REGISTRY)
    for method_name, reason in PYTHON_RTI_NON_RTI_SERVICE_REASONS.items():
        assert reason == "federate callback delivery helper", method_name


def test_every_service_has_at_least_one_requirement_row() -> None:
    rows_by_method = {
        row["method"]: row
        for row in _ledger_rows()
        if row.get("interface") == "RTIambassador" and row.get("method")
    }
    for method_name in PYTHON_RTI_SERVICE_REGISTRY:
        assert method_name in rows_by_method, method_name


def test_python_backend_invoke_uses_registry_backed_service_lookup() -> None:
    source = inspect.getsource(PythonRTIBackend.invoke)
    assert "PYTHON_RTI_SERVICE_HANDLERS.get" in source
    assert "_resolve_service_callable" not in source
    assert 'getattr(self, f"_svc_{invocation.method_name}"' not in source


def test_python_backend_internal_service_calls_use_semantic_service_names() -> None:
    source = inspect.getsource(PythonRTIBackend.call_service)
    assert "self._service_handler(method_name)" in source
    assert "_svc_" not in source


def test_python_backend_invoke_routes_through_direct_registry_handler() -> None:
    backend = PythonRTIBackend()

    result = backend.invoke(Invocation(method_name="getHLAversion", args=(), kwargs={}, overloads=()))

    assert result == "HLA 1516-2010 Python in-memory RTI subset"


def test_python_backend_call_service_routes_through_direct_registry_handler() -> None:
    backend = PythonRTIBackend()

    result = backend.call_service("getHLAversion")

    assert result == "HLA 1516-2010 Python in-memory RTI subset"


def test_generated_python_rti_service_map_is_current() -> None:
    result = subprocess.run(
        ["python3", "scripts/generate_python_rti_service_map.py", "check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Python RTI service registry outputs are current" in result.stdout


def test_trace_command_uses_registry_backed_implementation_path() -> None:
    result = subprocess.run(
        ["bash", "./tools/human-editability", "trace", "requestAttributeValueUpdate"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "hla2010_rti_python.object_delivery_attributes.PythonRTIObjectAttributeDeliveryMixin._svc_requestAttributeValueUpdate" in result.stdout
    assert "packages/hla2010-rti-python/src/hla2010_rti_python/object_delivery_attributes.py" in result.stdout
    assert "python_rti_service_map: analysis/traceability/python_rti_service_map.json" in result.stdout


def test_generated_service_map_rows_match_registry() -> None:
    by_method = {row.hla_method: row for row in _map_rows()}
    assert set(by_method) == set(PYTHON_RTI_SERVICE_REGISTRY)
    for method_name, dotted_path in PYTHON_RTI_SERVICE_REGISTRY.items():
        row = by_method[method_name]
        assert row.implementation_symbol == dotted_path
        target = PYTHON_RTI_SERVICE_HANDLERS[method_name]
        source_file = inspect.getsourcefile(target)
        assert source_file is not None
        assert row.implementation_module == Path(source_file).resolve().relative_to(ROOT).as_posix()
