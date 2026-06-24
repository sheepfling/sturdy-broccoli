#!/usr/bin/env python3
"""Validate frozen upstream_reference contract snapshots checked into this repo.

Default CI must not import live ``upstream_reference``. This checker validates the checked-in
packet metadata and structural shape; local sturdy API parity checks are added
incrementally by later contract-test slices.
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib
import inspect
import json
import sys
from enum import Enum
from pathlib import Path
from typing import Any


EXPECTED_TAG = "v0.1.1"
EXPECTED_COMMIT = "ed39b02e4c6e7813fce9e0e183b184c8513d4dd6"
EXPECTED_STANDARDS = {
    "ieee1516e": {
        "package": "upstream_reference.ieee1516e",
        "modules": {
            "datatypes",
            "handles",
            "enums",
            "exceptions",
            "logical_time",
            "time",
            "encoding",
            "handle_factory",
            "rti_factory",
            "rti_ambassador",
            "federate_ambassador",
        },
        "ambassador_method_counts": {
            "RTIambassador": 162,
            "FederateAmbassador": 51,
        },
        "has_RTIexception": True,
        "has_RTIException": False,
        "has_handle_value_map_getValueReference": True,
        "has_handle_value_map_get_value_reference": False,
    },
    "ieee1516_2025": {
        "package": "upstream_reference.ieee1516_2025",
        "modules": {
            "auth",
            "datatypes",
            "handles",
            "enums",
            "exceptions",
            "logical_time",
            "time",
            "encoding",
            "handle_factory",
            "rti_factory",
            "rti_ambassador",
            "federate_ambassador",
        },
        "ambassador_method_counts": {
            "RTIambassador": 188,
            "FederateAmbassador": 56,
        },
        "has_RTIexception": True,
        "has_RTIException": False,
        "has_handle_value_map_getValueReference": False,
        "has_handle_value_map_get_value_reference": False,
    },
}
LOCAL_PACKAGE_BY_STANDARD = {
    "ieee1516e": "hla.rti1516e",
    "ieee1516_2025": "hla.rti1516_2025",
}
REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = (
    "packages/hla-rti1516e/src",
    "packages/hla-rti1516-2025/src",
)


def ensure_source_checkout_path() -> None:
    for rel in reversed(SOURCE_ROOTS):
        path = str(REPO_ROOT / rel)
        if path not in sys.path:
            sys.path.insert(0, path)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_snapshot(snapshot: dict[str, Any], *, path: Path | None = None) -> list[str]:
    label = str(path) if path is not None else snapshot.get("standard", "<snapshot>")
    errors: list[str] = []
    standard = snapshot.get("standard")
    expected = EXPECTED_STANDARDS.get(str(standard))
    if expected is None:
        return [f"{label}: unexpected standard {standard!r}"]

    if snapshot.get("tag") != EXPECTED_TAG:
        errors.append(f"{label}: expected tag {EXPECTED_TAG!r}, got {snapshot.get('tag')!r}")
    if snapshot.get("tag_commit") != EXPECTED_COMMIT:
        errors.append(f"{label}: expected tag_commit {EXPECTED_COMMIT!r}, got {snapshot.get('tag_commit')!r}")
    if snapshot.get("package") != expected["package"]:
        errors.append(f"{label}: expected package {expected['package']!r}, got {snapshot.get('package')!r}")

    modules = snapshot.get("modules")
    if not isinstance(modules, dict):
        errors.append(f"{label}: modules must be an object")
        return errors

    missing_modules = sorted(expected["modules"] - set(modules))
    if missing_modules:
        errors.append(f"{label}: missing strict modules: {', '.join(missing_modules)}")

    for module_name, module_payload in modules.items():
        if not isinstance(module_payload, dict):
            errors.append(f"{label}: module {module_name} must be an object")
            continue
        if module_payload.get("module") != f"{expected['package']}.{module_name}":
            errors.append(f"{label}: module {module_name} has unexpected module name {module_payload.get('module')!r}")
        public_symbols = module_payload.get("public_symbols")
        if not isinstance(public_symbols, list):
            errors.append(f"{label}: module {module_name} public_symbols must be a list")
        for section in ("classes", "dataclasses", "enums", "exceptions", "namedtuples"):
            if section in module_payload and not isinstance(module_payload[section], dict):
                errors.append(f"{label}: module {module_name} {section} must be an object")

    facts = snapshot.get("contract_facts")
    if not isinstance(facts, dict):
        errors.append(f"{label}: contract_facts must be an object")
        return errors
    if facts.get("ambassador_method_counts") != expected["ambassador_method_counts"]:
        errors.append(
            f"{label}: expected ambassador counts {expected['ambassador_method_counts']!r}, "
            f"got {facts.get('ambassador_method_counts')!r}"
        )
    for fact_name in (
        "has_RTIexception",
        "has_RTIException",
        "has_handle_value_map_getValueReference",
        "has_handle_value_map_get_value_reference",
    ):
        if facts.get(fact_name) != expected[fact_name]:
            errors.append(f"{label}: expected {fact_name}={expected[fact_name]!r}, got {facts.get(fact_name)!r}")
    return errors


def validate_allowed_differences(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != 1:
        errors.append("allowed_differences.json: schema must be 1")
    if payload.get("upstream_contract_version") != EXPECTED_TAG:
        errors.append("allowed_differences.json: upstream_contract_version mismatch")
    if payload.get("upstream_reference_commit") != EXPECTED_COMMIT:
        errors.append("allowed_differences.json: upstream_reference_commit mismatch")
    standards = payload.get("standards", {})
    if set(standards) != set(EXPECTED_STANDARDS):
        errors.append("allowed_differences.json: standards set mismatch")
    return errors


def _allowed_extra_symbols(allowed_differences: dict[str, Any], standard: str, module_name: str) -> set[str]:
    standard_payload = allowed_differences.get("standards", {}).get(standard, {})
    extra_symbols = standard_payload.get("extra_symbols_allowed", {})
    return set(extra_symbols.get(module_name, ()))


def _local_method_shape(method: Any) -> list[tuple[str, str, bool]]:
    signature = inspect.signature(method)
    return [
        (parameter.name, parameter.kind.name, parameter.default is not inspect.Signature.empty)
        for parameter in signature.parameters.values()
    ]


def _snapshot_method_shape(method: dict[str, Any]) -> list[tuple[str, str, bool]]:
    return [
        (parameter["name"], parameter["kind"], bool(parameter["has_default"]))
        for parameter in method.get("parameters", ())
    ]


def _descriptor_kind(value: Any) -> str:
    if isinstance(value, property):
        return "property"
    if isinstance(value, classmethod):
        return "classmethod"
    if isinstance(value, staticmethod):
        return "staticmethod"
    if inspect.isfunction(value):
        return "method"
    if callable(value):
        return "callable"
    return type(value).__name__


def _local_member_shape(cls: type[Any], member_name: str) -> tuple[str, list[tuple[str, str, bool]]] | None:
    try:
        descriptor = inspect.getattr_static(cls, member_name)
    except AttributeError:
        return None

    kind = _descriptor_kind(descriptor)
    if kind == "property":
        return kind, []

    if kind == "classmethod":
        function = descriptor.__func__
    elif kind == "staticmethod":
        function = descriptor.__func__
    else:
        function = descriptor

    if not callable(function):
        return kind, []
    return kind, _local_method_shape(function)


def _expected_fields(class_payload: dict[str, Any] | list[Any]) -> list[str] | None:
    if isinstance(class_payload, list):
        return [str(field.get("name")) if isinstance(field, dict) else str(field) for field in class_payload]
    fields = class_payload.get("fields")
    if fields is None:
        return None
    return [str(field) for field in fields]


def _local_fields(cls: type[Any]) -> list[str] | None:
    if hasattr(cls, "_fields"):
        return [str(field) for field in getattr(cls, "_fields")]
    if dataclasses.is_dataclass(cls):
        return [field.name for field in dataclasses.fields(cls)]
    return None


def validate_local_datatype_handle_contract(snapshot: dict[str, Any]) -> list[str]:
    """Compare local datatypes and handles to the frozen structural contract."""

    ensure_source_checkout_path()
    errors: list[str] = []
    standard = str(snapshot.get("standard"))
    local_package = LOCAL_PACKAGE_BY_STANDARD.get(standard)
    if local_package is None:
        return [f"{standard}: no local package mapping"]

    for module_name in ("datatypes", "handles"):
        label = f"{standard}.{module_name}"
        local_module = importlib.import_module(f"{local_package}.{module_name}")
        module_payload = snapshot["modules"][module_name]
        expected_classes = module_payload.get("classes", {})
        expected_namedtuples = module_payload.get("namedtuples", {})
        expected_dataclasses = module_payload.get("dataclasses", {})

        for class_name, class_payload in sorted(expected_classes.items()):
            if not hasattr(local_module, class_name):
                errors.append(f"{label}: missing class {class_name}")
                continue
            local_class = getattr(local_module, class_name)
            if not isinstance(local_class, type):
                errors.append(f"{label}.{class_name}: expected class, got {type(local_class).__name__}")
                continue

            expected_fields = _expected_fields(class_payload)
            if expected_fields is not None:
                local_fields = _local_fields(local_class)
                if local_fields != expected_fields:
                    errors.append(
                        f"{label}.{class_name}: field drift; "
                        f"expected {expected_fields!r}, got {local_fields!r}"
                    )

            for method in class_payload.get("methods", ()):
                method_name = str(method["name"])
                expected_kind = str(method["kind"])
                local_member = _local_member_shape(local_class, method_name)
                if local_member is None:
                    errors.append(f"{label}.{class_name}: missing member {method_name}")
                    continue
                local_kind, local_shape = local_member
                expected_shape = _snapshot_method_shape(method)
                if local_kind != expected_kind:
                    errors.append(
                        f"{label}.{class_name}.{method_name}: member kind drift; "
                        f"expected {expected_kind!r}, got {local_kind!r}"
                    )
                if local_shape != expected_shape:
                    errors.append(
                        f"{label}.{class_name}.{method_name}: parameter shape drift; "
                        f"expected {expected_shape!r}, got {local_shape!r}"
                    )

        for class_name, class_payload in sorted(expected_namedtuples.items()):
            if not hasattr(local_module, class_name):
                errors.append(f"{label}: missing namedtuple {class_name}")
                continue
            local_fields = _local_fields(getattr(local_module, class_name))
            expected_fields = _expected_fields(class_payload)
            if local_fields != expected_fields:
                errors.append(
                    f"{label}.{class_name}: namedtuple field drift; "
                    f"expected {expected_fields!r}, got {local_fields!r}"
                )

        for class_name, class_payload in sorted(expected_dataclasses.items()):
            if not hasattr(local_module, class_name):
                errors.append(f"{label}: missing dataclass {class_name}")
                continue
            local_class = getattr(local_module, class_name)
            if not dataclasses.is_dataclass(local_class):
                errors.append(f"{label}.{class_name}: expected dataclass")
                continue
            local_fields = _local_fields(local_class)
            expected_fields = _expected_fields(class_payload)
            if local_fields != expected_fields:
                errors.append(
                    f"{label}.{class_name}: dataclass field drift; "
                    f"expected {expected_fields!r}, got {local_fields!r}"
                )
    return errors


def _validate_local_structural_modules(snapshot: dict[str, Any], module_names: tuple[str, ...]) -> list[str]:
    ensure_source_checkout_path()
    errors: list[str] = []
    standard = str(snapshot.get("standard"))
    local_package = LOCAL_PACKAGE_BY_STANDARD.get(standard)
    if local_package is None:
        return [f"{standard}: no local package mapping"]

    for module_name in module_names:
        if module_name not in snapshot["modules"]:
            continue
        label = f"{standard}.{module_name}"
        try:
            local_module = importlib.import_module(f"{local_package}.{module_name}")
        except ModuleNotFoundError as exc:
            errors.append(f"{label}: missing module")
            continue

        module_payload = snapshot["modules"][module_name]
        for class_name, class_payload in sorted(module_payload.get("classes", {}).items()):
            if not hasattr(local_module, class_name):
                errors.append(f"{label}: missing class {class_name}")
                continue
            local_class = getattr(local_module, class_name)
            if not isinstance(local_class, type):
                errors.append(f"{label}.{class_name}: expected class, got {type(local_class).__name__}")
                continue

            expected_fields = _expected_fields(class_payload)
            if expected_fields is not None:
                local_fields = _local_fields(local_class)
                if local_fields != expected_fields:
                    errors.append(
                        f"{label}.{class_name}: field drift; "
                        f"expected {expected_fields!r}, got {local_fields!r}"
                    )

            for method in class_payload.get("methods", ()):
                method_name = str(method["name"])
                expected_kind = str(method["kind"])
                local_member = _local_member_shape(local_class, method_name)
                if local_member is None:
                    errors.append(f"{label}.{class_name}: missing member {method_name}")
                    continue
                local_kind, local_shape = local_member
                expected_shape = _snapshot_method_shape(method)
                if local_kind != expected_kind:
                    errors.append(
                        f"{label}.{class_name}.{method_name}: member kind drift; "
                        f"expected {expected_kind!r}, got {local_kind!r}"
                    )
                if local_shape != expected_shape:
                    errors.append(
                        f"{label}.{class_name}.{method_name}: parameter shape drift; "
                        f"expected {expected_shape!r}, got {local_shape!r}"
                    )

        for class_name, class_payload in sorted(module_payload.get("namedtuples", {}).items()):
            if not hasattr(local_module, class_name):
                errors.append(f"{label}: missing namedtuple {class_name}")
                continue
            local_fields = _local_fields(getattr(local_module, class_name))
            expected_fields = _expected_fields(class_payload)
            if local_fields != expected_fields:
                errors.append(
                    f"{label}.{class_name}: namedtuple field drift; "
                    f"expected {expected_fields!r}, got {local_fields!r}"
                )

        for class_name, class_payload in sorted(module_payload.get("dataclasses", {}).items()):
            if not hasattr(local_module, class_name):
                errors.append(f"{label}: missing dataclass {class_name}")
                continue
            local_class = getattr(local_module, class_name)
            if not dataclasses.is_dataclass(local_class):
                errors.append(f"{label}.{class_name}: expected dataclass")
                continue
            local_fields = _local_fields(local_class)
            expected_fields = _expected_fields(class_payload)
            if local_fields != expected_fields:
                errors.append(
                    f"{label}.{class_name}: dataclass field drift; "
                    f"expected {expected_fields!r}, got {local_fields!r}"
                )

        for exception_name in sorted(module_payload.get("exceptions", {})):
            if not hasattr(local_module, exception_name):
                errors.append(f"{label}: missing exception {exception_name}")

        expected_functions = module_payload.get("functions", {})
        if isinstance(expected_functions, dict):
            function_items = sorted(expected_functions.items())
        else:
            function_items = [(function["name"], function) for function in expected_functions]
        for function_name, function_payload in function_items:
            if not hasattr(local_module, function_name):
                errors.append(f"{label}: missing function {function_name}")
                continue
            local_function = getattr(local_module, function_name)
            if not callable(local_function):
                errors.append(f"{label}.{function_name}: expected callable")
                continue
            expected_shape = _snapshot_method_shape(function_payload)
            local_shape = _local_method_shape(local_function)
            if local_shape != expected_shape:
                errors.append(
                    f"{label}.{function_name}: parameter shape drift; "
                    f"expected {expected_shape!r}, got {local_shape!r}"
                )
    return errors


def validate_local_remaining_standard_contract(snapshot: dict[str, Any]) -> list[str]:
    """Compare remaining standard modules after ambassador/datatype/enum slices."""

    return _validate_local_structural_modules(
        snapshot,
        ("logical_time", "time", "encoding", "_byte_wrapper", "handle_factory", "rti_factory"),
    )


def validate_local_ambassador_contract(snapshot: dict[str, Any]) -> list[str]:
    """Compare local sturdy ambassador protocols to the frozen upstream snapshot.

    This v1 check intentionally ignores annotations and return annotations. It
    enforces method names, parameter names, parameter kind, and default presence.
    """

    ensure_source_checkout_path()
    errors: list[str] = []
    standard = str(snapshot.get("standard"))
    local_package = LOCAL_PACKAGE_BY_STANDARD.get(standard)
    if local_package is None:
        return [f"{standard}: no local package mapping"]

    for module_name, class_name in (
        ("rti_ambassador", "RTIambassador"),
        ("federate_ambassador", "FederateAmbassador"),
    ):
        label = f"{standard}.{module_name}.{class_name}"
        expected_methods = {
            method["name"]: method
            for method in snapshot["modules"][module_name]["classes"][class_name]["methods"]
        }
        local_module = importlib.import_module(f"{local_package}.{module_name}")
        local_class = getattr(local_module, class_name)
        local_methods = {
            name: value
            for name, value in vars(local_class).items()
            if callable(value) and not name.startswith("_")
        }

        missing = sorted(set(expected_methods) - set(local_methods))
        extra = sorted(set(local_methods) - set(expected_methods))
        if missing:
            errors.append(f"{label}: missing methods: {', '.join(missing)}")
        if extra:
            errors.append(f"{label}: unreviewed extra methods: {', '.join(extra)}")

        for method_name in sorted(set(expected_methods) & set(local_methods)):
            expected_shape = _snapshot_method_shape(expected_methods[method_name])
            local_shape = _local_method_shape(local_methods[method_name])
            if local_shape != expected_shape:
                errors.append(
                    f"{label}.{method_name}: parameter shape drift; "
                    f"expected {expected_shape!r}, got {local_shape!r}"
                )
    return errors


def validate_local_enum_exception_contract(
    snapshot: dict[str, Any],
    allowed_differences: dict[str, Any],
) -> list[str]:
    """Compare local enum values and exception names to the frozen snapshot."""

    ensure_source_checkout_path()
    errors: list[str] = []
    standard = str(snapshot.get("standard"))
    local_package = LOCAL_PACKAGE_BY_STANDARD.get(standard)
    if local_package is None:
        return [f"{standard}: no local package mapping"]

    enum_module = importlib.import_module(f"{local_package}.enums")
    expected_enums = snapshot["modules"]["enums"]["enums"]
    local_enums = {
        name: [(member.name, member.value) for member in value]
        for name, value in vars(enum_module).items()
        if isinstance(value, type)
        and issubclass(value, Enum)
        and value.__module__ == enum_module.__name__
        and not name.startswith("_")
    }
    missing_enums = sorted(set(expected_enums) - set(local_enums))
    extra_enums = sorted(set(local_enums) - set(expected_enums) - _allowed_extra_symbols(allowed_differences, standard, "enums"))
    if missing_enums:
        errors.append(f"{standard}.enums: missing enums: {', '.join(missing_enums)}")
    if extra_enums:
        errors.append(f"{standard}.enums: unreviewed extra enums: {', '.join(extra_enums)}")
    for enum_name in sorted(set(expected_enums) & set(local_enums)):
        expected_members = [(member["name"], member["value"]) for member in expected_enums[enum_name]]
        if local_enums[enum_name] != expected_members:
            errors.append(
                f"{standard}.enums.{enum_name}: member drift; "
                f"expected {expected_members!r}, got {local_enums[enum_name]!r}"
            )

    exception_module = importlib.import_module(f"{local_package}.exceptions")
    expected_exceptions = snapshot["modules"]["exceptions"]["exceptions"]
    local_exceptions = {
        name: value
        for name, value in vars(exception_module).items()
        if isinstance(value, type)
        and issubclass(value, BaseException)
        and value.__module__ == exception_module.__name__
        and not name.startswith("_")
    }
    allowed_exception_extras = _allowed_extra_symbols(allowed_differences, standard, "exceptions")
    missing_exceptions = sorted(set(expected_exceptions) - set(local_exceptions))
    extra_exceptions = sorted(set(local_exceptions) - set(expected_exceptions) - allowed_exception_extras)
    if missing_exceptions:
        errors.append(f"{standard}.exceptions: missing exceptions: {', '.join(missing_exceptions)}")
    if extra_exceptions:
        errors.append(f"{standard}.exceptions: unreviewed extra exceptions: {', '.join(extra_exceptions)}")

    base_exception = local_exceptions.get("RTIexception")
    if base_exception is None:
        errors.append(f"{standard}.exceptions: missing RTIexception base")
    else:
        for exception_name in sorted(set(expected_exceptions) & set(local_exceptions)):
            if exception_name == "RTIexception":
                continue
            if not issubclass(local_exceptions[exception_name], base_exception):
                errors.append(f"{standard}.exceptions.{exception_name}: does not subclass RTIexception")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("compat/upstream_contract"))
    parser.add_argument("--snapshot", type=Path, action="append")
    parser.add_argument("--check-local-ambassadors", action="store_true")
    parser.add_argument("--check-local-enums-exceptions", action="store_true")
    parser.add_argument("--check-local-datatypes-handles", action="store_true")
    parser.add_argument("--check-local-standard-support", action="store_true")
    args = parser.parse_args()

    snapshot_paths = args.snapshot or sorted((args.root / EXPECTED_TAG).glob("*.json"))
    errors: list[str] = []
    allowed_differences = load_json(args.root / "allowed_differences.json")
    errors.extend(validate_allowed_differences(allowed_differences))
    for snapshot_path in snapshot_paths:
        snapshot = load_json(snapshot_path)
        errors.extend(validate_snapshot(snapshot, path=snapshot_path))
        if args.check_local_ambassadors:
            errors.extend(validate_local_ambassador_contract(snapshot))
        if args.check_local_enums_exceptions:
            errors.extend(validate_local_enum_exception_contract(snapshot, allowed_differences))
        if args.check_local_datatypes_handles:
            errors.extend(validate_local_datatype_handle_contract(snapshot))
        if args.check_local_standard_support:
            errors.extend(validate_local_remaining_standard_contract(snapshot))

    if errors:
        print("upstream_reference contract snapshot validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
