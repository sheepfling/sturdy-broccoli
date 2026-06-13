from __future__ import annotations

import argparse
import ast
import csv
import importlib
import json
import inspect
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPECS_PATH = ROOT / "specs" / "hla2010_api.json"
LEDGER_PATH = ROOT / "analysis" / "compliance" / "requirements_ledger.csv"
REGISTRY_PATH = ROOT / "packages" / "hla2010-rti-python" / "src" / "hla2010_rti_python" / "service_registry.py"
MAP_CSV_PATH = ROOT / "analysis" / "traceability" / "python_rti_service_map.csv"
MAP_JSON_PATH = ROOT / "analysis" / "traceability" / "python_rti_service_map.json"
MAP_MD_PATH = ROOT / "analysis" / "traceability" / "python_rti_service_map.md"

GENERATED_HEADER = """# Generated from specs/hla2010_api.json and analysis/compliance/requirements_ledger.csv.
# Do not edit by hand. Run python3 scripts/generate_python_rti_service_map.py generate.
"""


def _load_specs() -> dict[str, Any]:
    return json.loads(SPECS_PATH.read_text(encoding="utf-8"))


def _load_ledger_rows() -> list[dict[str, str]]:
    with LEDGER_PATH.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_existing_registry_mapping() -> dict[str, str]:
    module = ast.parse(REGISTRY_PATH.read_text(encoding="utf-8"), filename=str(REGISTRY_PATH))
    for node in module.body:
        if not isinstance(node, ast.AnnAssign):
            continue
        if not isinstance(node.target, ast.Name):
            continue
        if node.target.id != "PYTHON_RTI_SERVICE_REGISTRY":
            continue
        value = ast.literal_eval(node.value)
        assert isinstance(value, dict)
        return {str(key): str(symbol) for key, symbol in value.items()}
    raise RuntimeError("could not locate PYTHON_RTI_SERVICE_REGISTRY in service_registry.py")


def _resolve_callable(dotted_path: str) -> Any:
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
    raise RuntimeError(f"could not resolve callable {dotted_path!r}")


def _split_refs(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def _build_registry_rows() -> list[dict[str, str]]:
    import sys

    for source_path in (
        str(ROOT / "packages" / "hla2010-spec" / "src"),
        str(ROOT / "packages" / "hla2010-rti-python" / "src"),
        str(ROOT / "packages" / "hla2010-rti-backend-common" / "src"),
    ):
        if source_path not in sys.path:
            sys.path.insert(0, source_path)

    specs = _load_specs()
    registry_mapping = _load_existing_registry_mapping()
    ledger_rows = _load_ledger_rows()
    ledger_by_method = {
        row["method"]: row for row in ledger_rows if row.get("interface") == "RTIambassador" and row.get("method")
    }
    rows: list[dict[str, str]] = []
    for method_name in sorted(specs["interfaces"]["RTIambassador"]):
        implementation_symbol = registry_mapping[method_name]
        service = _resolve_callable(implementation_symbol)
        source_file = inspect.getsourcefile(service)
        if source_file is None:
            raise RuntimeError(f"could not resolve source file for {method_name}")
        implementation_module_path = Path(source_file).resolve().relative_to(ROOT).as_posix()
        metadata = specs["interfaces"]["RTIambassador"][method_name]
        ledger = ledger_by_method.get(method_name, {})
        rows.append(
            {
                "hla_method": method_name,
                "python_name": str(metadata["python_name"]),
                "service_group": str(metadata.get("service_group") or ""),
                "implementation_module": implementation_module_path,
                "implementation_symbol": implementation_symbol,
                "requirement_ids": ledger.get("requirement_id", ""),
                "positive_tests": ledger.get("positive_test_refs", ""),
                "negative_tests": ledger.get("negative_test_refs", ""),
                "status": ledger.get("outcome", "unmapped"),
            }
        )
    return rows


def _registry_content(rows: list[dict[str, str]]) -> str:
    mapping = {row["hla_method"]: row["implementation_symbol"] for row in rows}
    import_targets: dict[str, set[str]] = {}
    handler_targets: dict[str, str] = {}
    for method_name, dotted_path in mapping.items():
        module_name, class_name, attr_name = dotted_path.rsplit(".", 2)
        package_module = module_name.split("hla2010_rti_python.", 1)[1]
        import_targets.setdefault(package_module, set()).add(class_name)
        handler_targets[method_name] = f"{class_name}.{attr_name}"
    callback_helpers = {
        "provideAttributeValueUpdate": "federate callback delivery helper",
        "startRegistrationForObjectClass": "federate callback delivery helper",
        "stopRegistrationForObjectClass": "federate callback delivery helper",
        "turnInteractionsOff": "federate callback delivery helper",
        "turnInteractionsOn": "federate callback delivery helper",
        "turnUpdatesOffForObjectInstance": "federate callback delivery helper",
        "turnUpdatesOnForObjectInstance": "federate callback delivery helper",
    }
    lines = [
        GENERATED_HEADER.rstrip(),
        '"""Stable Python RTI service registry.',
        "",
        "Maps each HLA RTI method name to the concrete `_svc_*` implementation symbol",
        "and explicit callable resolved from the Python RTI mixins.",
        '"""',
        "from __future__ import annotations",
        "",
    ]
    for module_name in sorted(import_targets):
        class_names = ", ".join(sorted(import_targets[module_name]))
        lines.append(f"from .{module_name} import {class_names}")
    lines.extend(
        [
            "",
            f"PYTHON_RTI_SERVICE_REGISTRY: dict[str, str] = {json.dumps(mapping, indent=2, sort_keys=True).replace('null', 'None')}",
            "",
            "PYTHON_RTI_SERVICE_HANDLERS: dict[str, object] = {",
        ]
    )
    for method_name in sorted(handler_targets):
        lines.append(f'  "{method_name}": {handler_targets[method_name]},')
    lines.extend(
        [
            "}",
            "",
            f"PYTHON_RTI_NON_RTI_SERVICE_REASONS: dict[str, str] = {json.dumps(callback_helpers, indent=2, sort_keys=True).replace('null', 'None')}",
            "",
            '__all__ = ["PYTHON_RTI_NON_RTI_SERVICE_REASONS", "PYTHON_RTI_SERVICE_HANDLERS", "PYTHON_RTI_SERVICE_REGISTRY"]',
            "",
        ]
    )
    return "\n".join(lines)


def _csv_content(rows: list[dict[str, str]]) -> str:
    fieldnames = [
        "hla_method",
        "python_name",
        "service_group",
        "implementation_module",
        "implementation_symbol",
        "requirement_ids",
        "positive_tests",
        "negative_tests",
        "status",
    ]
    output: list[str] = []
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _json_content(rows: list[dict[str, str]]) -> str:
    return json.dumps({"rows": rows}, indent=2, sort_keys=True) + "\n"


def _md_content(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Python RTI Service Map",
        "",
        "Generated from `specs/hla2010_api.json`, `analysis/compliance/requirements_ledger.csv`, and `PythonRTIBackend`.",
        "",
        "| hla_method | python_name | service_group | implementation_module | implementation_symbol | requirement_ids | positive_tests | negative_tests | status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                row[key] or "-"
                for key in (
                    "hla_method",
                    "python_name",
                    "service_group",
                    "implementation_module",
                    "implementation_symbol",
                    "requirement_ids",
                    "positive_tests",
                    "negative_tests",
                    "status",
                )
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _expected_outputs() -> dict[Path, str]:
    rows = _build_registry_rows()
    return {
        REGISTRY_PATH: _registry_content(rows),
        MAP_CSV_PATH: _csv_content(rows),
        MAP_JSON_PATH: _json_content(rows),
        MAP_MD_PATH: _md_content(rows),
    }


def generate() -> int:
    for path, content in _expected_outputs().items():
        path.write_text(content, encoding="utf-8")
        print(path.relative_to(ROOT).as_posix())
    return 0


def check() -> int:
    stale: list[str] = []
    for path, expected in _expected_outputs().items():
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != expected:
            stale.append(path.relative_to(ROOT).as_posix())
    if stale:
        print("Python RTI service registry outputs are out of date")
        for item in stale:
            print(f"- {item}")
        return 1
    print("Python RTI service registry outputs are current")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or validate the Python RTI service registry and maps.")
    parser.add_argument("command", choices=("generate", "check"))
    args = parser.parse_args()
    if args.command == "generate":
        return generate()
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
