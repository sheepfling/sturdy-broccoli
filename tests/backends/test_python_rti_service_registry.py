from __future__ import annotations

import csv
import importlib
import inspect
import json
import subprocess
from pathlib import Path

from hla2010.raw_api import API_METADATA
from hla2010_rti_python.backend import PythonRTIBackend
from hla2010_rti_python.service_registry import (
    PYTHON_RTI_NON_RTI_SERVICE_REASONS,
    PYTHON_RTI_SERVICE_REGISTRY,
)


ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "analysis" / "compliance" / "requirements_ledger.csv"
MAP_JSON_PATH = ROOT / "analysis" / "traceability" / "python_rti_service_map.json"


def _ledger_rows() -> list[dict[str, str]]:
    with LEDGER_PATH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _map_rows() -> list[dict[str, str]]:
    payload = json.loads(MAP_JSON_PATH.read_text(encoding="utf-8"))
    rows = payload.get("rows", [])
    assert isinstance(rows, list)
    return rows  # type: ignore[return-value]


def _resolve_callable(dotted_path: str):
    parts = dotted_path.split(".")
    for index in range(len(parts), 0, -1):
        module_name = ".".join(parts[:index])
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        target = module
        for part in parts[index:]:
            target = getattr(target, part)
        return target
    raise AssertionError(f"could not resolve callable {dotted_path}")


def test_every_rti_method_has_a_registry_entry() -> None:
    assert set(PYTHON_RTI_SERVICE_REGISTRY) == set(API_METADATA["RTIambassador"])


def test_every_registry_entry_resolves_to_a_real_callable() -> None:
    for method_name, dotted_path in PYTHON_RTI_SERVICE_REGISTRY.items():
        target = _resolve_callable(dotted_path)
        assert callable(target), method_name


def test_every_python_backend_service_function_has_a_registry_entry() -> None:
    implemented = {
        name.removeprefix("_svc_")
        for name in dir(PythonRTIBackend)
        if name.startswith("_svc_") and callable(getattr(PythonRTIBackend, name))
    }
    covered = set(PYTHON_RTI_SERVICE_REGISTRY) | set(PYTHON_RTI_NON_RTI_SERVICE_REASONS)
    assert implemented == covered
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
    by_method = {row["hla_method"]: row for row in _map_rows()}
    assert set(by_method) == set(PYTHON_RTI_SERVICE_REGISTRY)
    for method_name, dotted_path in PYTHON_RTI_SERVICE_REGISTRY.items():
        row = by_method[method_name]
        assert row["implementation_symbol"] == dotted_path
        target = _resolve_callable(dotted_path)
        source_file = inspect.getsourcefile(target)
        assert source_file is not None
        assert row["implementation_module"] == Path(source_file).resolve().relative_to(ROOT).as_posix()
