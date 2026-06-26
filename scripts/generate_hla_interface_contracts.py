from __future__ import annotations

import argparse
import json
import keyword
import re
import sys
from pathlib import Path
from typing import Any

import tomllib


ROOT = Path(__file__).resolve().parents[1]
API_METADATA_SOURCE = "packages/hla-rti1516e/src/hla/rti1516e/api_metadata.json"
BASE_PATH = ROOT / "packages" / "hla-backend-common" / "src" / "hla.backends.common" / "base.py"
DOC_PATH = ROOT / "docs" / "reference" / "hla_interface_contracts.md"

GENERATED_HEADER = """# Generated from packages/hla-rti1516e/src/hla/rti1516e/api_metadata.json.
# Do not edit by hand. Run python3 scripts/generate_hla_interface_contracts.py generate.
"""


JAVA_TYPE_MAP = {
    "AttributeHandle": "AttributeHandle",
    "AttributeHandleFactory": "AttributeHandleFactory",
    "AttributeHandleSet": "AttributeHandleSet",
    "AttributeHandleSetFactory": "AttributeHandleSetFactory",
    "AttributeHandleValueMap": "AttributeHandleValueMap",
    "AttributeHandleValueMapFactory": "AttributeHandleValueMapFactory",
    "AttributeSetRegionSetPairList": "AttributeSetRegionSetPairList",
    "AttributeSetRegionSetPairListFactory": "AttributeSetRegionSetPairListFactory",
    "CallbackModel": "CallbackModel",
    "DimensionHandle": "DimensionHandle",
    "DimensionHandleFactory": "DimensionHandleFactory",
    "DimensionHandleSet": "DimensionHandleSet",
    "DimensionHandleSetFactory": "DimensionHandleSetFactory",
    "FederateAmbassador": "NullFederateAmbassador",
    "FederateHandle": "FederateHandle",
    "FederateHandleFactory": "FederateHandleFactory",
    "FederateHandleSaveStatusPair[]": "Sequence[FederateHandleSaveStatusPair]",
    "FederateHandleSet": "FederateHandleSet",
    "FederateHandleSetFactory": "FederateHandleSetFactory",
    "FederateRestoreStatus[]": "Sequence[FederateRestoreStatus]",
    "FederationExecutionInformationSet": "FederationExecutionInformationSet",
    "InteractionClassHandle": "InteractionClassHandle",
    "InteractionClassHandleFactory": "InteractionClassHandleFactory",
    "InteractionClassHandleSet": "InteractionClassHandleSet",
    "LogicalTime": "LogicalTimeLike",
    "LogicalTimeFactory": "LogicalTimeFactoryLike",
    "LogicalTimeInterval": "LogicalTimeIntervalLike",
    "MessageRetractionHandle": "MessageRetractionHandle",
    "MessageRetractionReturn": "MessageRetractionReturn",
    "ObjectClassHandle": "ObjectClassHandle",
    "ObjectClassHandleFactory": "ObjectClassHandleFactory",
    "ObjectInstanceHandle": "ObjectInstanceHandle",
    "ObjectInstanceHandleFactory": "ObjectInstanceHandleFactory",
    "OrderType": "OrderType",
    "ParameterHandle": "ParameterHandle",
    "ParameterHandleFactory": "ParameterHandleFactory",
    "ParameterHandleValueMap": "ParameterHandleValueMap",
    "ParameterHandleValueMapFactory": "ParameterHandleValueMapFactory",
    "RangeBounds": "RangeBounds",
    "RegionHandle": "RegionHandle",
    "RegionHandleSet": "RegionHandleSet",
    "RegionHandleSetFactory": "RegionHandleSetFactory",
    "ResignAction": "ResignAction",
    "RestoreFailureReason": "RestoreFailureReason",
    "SaveFailureReason": "SaveFailureReason",
    "ServiceGroup": "ServiceGroup",
    "Set<String>": "set[str]",
    "String": "str",
    "SupplementalReceiveInfo": "SupplementalReceiveInfo",
    "SupplementalReflectInfo": "SupplementalReflectInfo",
    "SupplementalRemoveInfo": "SupplementalRemoveInfo",
    "SynchronizationPointFailureReason": "SynchronizationPointFailureReason",
    "TimeQueryReturn": "TimeQueryReturn",
    "TransportationType": "TransportationType",
    "TransportationTypeHandle": "TransportationTypeHandle",
    "TransportationTypeHandleFactory": "TransportationTypeHandleFactory",
    "URL": "URLLike",
    "URL[]": "Sequence[URLLike]",
    "VariableLengthData": "VariableLengthDataLike",
    "boolean": "bool",
    "byte[]": "VariableLengthDataLike",
    "double": "float",
    "long": "int",
    "std::vector<std::wstring>": "Sequence[URLLike]",
    "std::wstring": "str",
    "void": "None",
}

PYTHON_NAME_OVERRIDES = {
    "getHLAversion": "get_hla_version",
}

PYTHON_ALIAS_PARAM_OVERRIDES = {
    "createFederationExecution": [
        "self",
        "federation_execution_name: str",
        "fom_modules: FomModuleLike",
        "*",
        "mim_module: URLLike | None = None",
        "logical_time_implementation_name: str | None = None",
    ],
    "joinFederationExecution": [
        "self",
        "federate_type: str",
        "federation_execution_name: str",
        "*",
        "federate_name: str | None = None",
        "additional_fom_modules: Sequence[URLLike] | None = None",
    ],
    "requestAttributeValueUpdate": [
        "self",
        "target: ObjectInstanceHandle | ObjectClassHandle",
        "the_attributes: AttributeHandleSet",
        "user_supplied_tag: VariableLengthDataLike",
    ],
}


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


def lower_camel_to_snake(name: str) -> str:
    name = name.replace("HLAversion", "HLAVersion")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def split_java_params(params: str) -> list[str]:
    params = params.strip()
    params = params.split(") const", 1)[0]
    params = params.split(") throw", 1)[0]
    if not params:
        return []
    return [part.strip() for part in params.split(",") if part.strip()]


def required_param_count(params: list[str]) -> int:
    return sum("=" not in param for param in params)


def clean_param_decl(param_decl: str) -> str:
    cleaned = param_decl.split(") const", 1)[0]
    cleaned = cleaned.split(") throw", 1)[0]
    cleaned = cleaned.split("=", 1)[0]
    return cleaned.strip()


def clean_type(type_name: str) -> str:
    cleaned = type_name.replace(" const", "").replace("const ", "").replace("&", "").strip()
    return re.sub(r"\s+", " ", cleaned)


def param_name(param_decl: str) -> str:
    param_decl = clean_param_decl(param_decl)
    name = re.split(r"\s+", param_decl.strip())[-1].replace("...", "")
    if keyword.iskeyword(name):
        return f"{name}_"
    return name


def param_type(param_decl: str) -> str:
    param_decl = clean_param_decl(param_decl)
    pieces = re.split(r"\s+", param_decl.strip())
    if len(pieces) <= 1:
        return "object"
    return clean_type(" ".join(pieces[:-1]).replace("...", ""))


def python_type(java_type: str | None) -> str:
    return JAVA_TYPE_MAP.get(java_type or "", "object")


def load_interfaces() -> dict[str, dict[str, dict[str, Any]]]:
    _bootstrap_source_checkout()
    from hla.rti1516e.raw_api import API_METADATA

    return API_METADATA


def _overload_items(method_meta: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(method_meta, list):
        return method_meta
    return list(method_meta.get("overloads", []))


def java_overloads(method_meta: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in _overload_items(method_meta) if item.get("language") == "java"]


def canonical_overload(method_meta: dict[str, Any] | list[dict[str, Any]]) -> tuple[list[str], list[str], int, str]:
    overloads = java_overloads(method_meta)
    if not overloads:
        source_overloads = _overload_items(method_meta)
        parsed = [split_java_params(str(item.get("params") or "")) for item in source_overloads]
        longest = max(parsed, key=len, default=[])
        min_arity = min((required_param_count(params) for params in parsed), default=0)
        names = [param_name(part) for part in longest]
        types = [python_type(param_type(part)) for part in longest]
        return_type = python_type(clean_type(str(source_overloads[0].get("return_type") if source_overloads else "void")))
        return names, types, min_arity, return_type
    parsed = [split_java_params(str(item.get("params") or "")) for item in overloads]
    longest = max(parsed, key=len, default=[])
    min_arity = min((required_param_count(params) for params in parsed), default=0)
    names = [param_name(part) for part in longest]
    types = [python_type(param_type(part)) for part in longest]
    return_type = python_type(str(overloads[0].get("return_type") if overloads else "void"))
    return names, types, min_arity, return_type


def annotated_params(names: list[str], types: list[str], min_arity: int, *, snake: bool) -> list[str]:
    params: list[str] = ["self"]
    for index, (name, typ) in enumerate(zip(names, types)):
        py_name = lower_camel_to_snake(name) if snake else name
        if index >= min_arity:
            if " | None" not in typ:
                typ = f"{typ} | None"
            params.append(f"{py_name}: {typ} = None")
        else:
            params.append(f"{py_name}: {typ}")
    return params


def alias_params(method_name: str, names: list[str], types: list[str], min_arity: int) -> list[str]:
    return PYTHON_ALIAS_PARAM_OVERRIDES.get(method_name) or annotated_params(names, types, min_arity, snake=True)


def format_signature(name: str, params: list[str], return_type: str, *, noqa: bool = False) -> list[str]:
    suffix = "  # noqa: N802" if noqa else ""
    one_line = f"def {name}({', '.join(params)}) -> {return_type}:{suffix}"
    if len(one_line) <= 118:
        return [one_line]
    return [f"def {name}(", *[f"    {param}," for param in params], f") -> {return_type}:{suffix}"]


def indent(lines: list[str], spaces: int) -> list[str]:
    prefix = " " * spaces
    return [f"{prefix}{line}" if line else "" for line in lines]


def call_args(names: list[str], min_arity: int, *, snake: bool) -> list[str]:
    args: list[str] = []
    for index, name in enumerate(names):
        py_name = lower_camel_to_snake(name) if snake else name
        if index < min_arity:
            args.append(py_name)
    return args


def optional_append_block(names: list[str], min_arity: int, *, snake: bool, indent: str = "        ") -> list[str]:
    lines: list[str] = []
    if len(names) <= min_arity:
        return lines
    required = call_args(names, min_arity, snake=snake)
    tuple_expr = ", ".join(required)
    if len(required) == 1:
        tuple_expr += ","
    lines.append(f"{indent}args: tuple[object, ...] = ({tuple_expr})" if required else f"{indent}args: tuple[object, ...] = ()")
    for name in names[min_arity:]:
        py_name = lower_camel_to_snake(name) if snake else name
        lines.append(f"{indent}if {py_name} is not None:")
        lines.append(f"{indent}    args = (*args, {py_name})")
    return lines


def alias_body(method_name: str) -> list[str] | None:
    if method_name == "createFederationExecution":
        return [
            "        args: tuple[object, ...] = (federation_execution_name, fom_modules)",
            "        if mim_module is not None:",
            "            args = (*args, mim_module)",
            "        if logical_time_implementation_name is not None:",
            "            args = (*args, logical_time_implementation_name)",
            "        return self.createFederationExecution(*args)",
        ]
    if method_name == "joinFederationExecution":
        return [
            "        if federate_name is None:",
            "            args: tuple[object, ...] = (federate_type, federation_execution_name)",
            "        else:",
            "            args = (federate_name, federate_type, federation_execution_name)",
            "        if additional_fom_modules is not None:",
            "            args = (*args, additional_fom_modules)",
            "        return self.joinFederationExecution(*args)",
        ]
    if method_name == "requestAttributeValueUpdate":
        return [
            "        return self.requestAttributeValueUpdate(target, the_attributes, user_supplied_tag)",
        ]
    return None


def delegate_alias_body(method_name: str) -> list[str] | None:
    if method_name == "createFederationExecution":
        return [
            "        args: tuple[object, ...] = (federation_execution_name, fom_modules)",
            "        if mim_module is not None:",
            "            args = (*args, mim_module)",
            "        if logical_time_implementation_name is not None:",
            "            args = (*args, logical_time_implementation_name)",
            '        return self._invoke("createFederationExecution", *args)',
        ]
    if method_name == "joinFederationExecution":
        return [
            "        if federate_name is None:",
            "            args: tuple[object, ...] = (federate_type, federation_execution_name)",
            "        else:",
            "            args = (federate_name, federate_type, federation_execution_name)",
            "        if additional_fom_modules is not None:",
            "            args = (*args, additional_fom_modules)",
            '        return self._invoke("joinFederationExecution", *args)',
        ]
    if method_name == "requestAttributeValueUpdate":
        return [
            '        return self._invoke("requestAttributeValueUpdate", target, the_attributes, user_supplied_tag)',
        ]
    return None


def render_rti_method(method_name: str, method_meta: dict[str, Any]) -> list[str]:
    names, types, min_arity, return_type = canonical_overload(method_meta)
    lines = [
        f'    @_service_metadata("{method_name}")',
        "    @abstractmethod",
        *indent(format_signature(method_name, annotated_params(names, types, min_arity, snake=False), return_type, noqa=True), 4),
        "        raise NotImplementedError",
        "",
    ]
    snake_name = PYTHON_NAME_OVERRIDES.get(method_name, lower_camel_to_snake(method_name))
    if snake_name != method_name:
        lines.extend(
            [
                f'    @_service_metadata("{method_name}")',
                *indent(format_signature(snake_name, alias_params(method_name, names, types, min_arity), return_type), 4),
            ]
        )
        override_body = alias_body(method_name)
        if override_body is not None:
            lines.extend(override_body)
        else:
            optional = optional_append_block(names, min_arity, snake=True)
            if optional:
                lines.extend(optional)
                lines.append(f"        return self.{method_name}(*args)")
            else:
                lines.append(f"        return self.{method_name}({', '.join(call_args(names, min_arity, snake=True))})")
        lines.append("")
    return lines


def render_delegate_method(method_name: str, method_meta: dict[str, Any]) -> list[str]:
    names, types, min_arity, return_type = canonical_overload(method_meta)
    lines = [
        *indent(format_signature(method_name, annotated_params(names, types, min_arity, snake=False), return_type, noqa=True), 4),
        f'        """Delegate HLA RTI service {method_name} to the configured backend."""',
    ]
    optional = optional_append_block(names, min_arity, snake=False)
    if optional:
        lines.extend(optional)
        lines.append(f'        return self._invoke("{method_name}", *args)')
    else:
        required_args = ", ".join(call_args(names, min_arity, snake=False))
        if required_args:
            lines.append(f'        return self._invoke("{method_name}", {required_args})')
        else:
            lines.append(f'        return self._invoke("{method_name}")')
    lines.append("")

    snake_name = PYTHON_NAME_OVERRIDES.get(method_name, lower_camel_to_snake(method_name))
    if snake_name != method_name:
        lines.extend(
            [
                *indent(format_signature(snake_name, alias_params(method_name, names, types, min_arity), return_type), 4),
                f'        """Delegate the Pythonic RTI service alias to {method_name}."""',
            ]
        )
        override_body = delegate_alias_body(method_name)
        if override_body is not None:
            lines.extend(override_body)
        else:
            optional = optional_append_block(names, min_arity, snake=True)
            if optional:
                lines.extend(optional)
                lines.append(f'        return self._invoke("{method_name}", *args)')
            else:
                required_args = ", ".join(call_args(names, min_arity, snake=True))
                lines.append(f"        return self.{method_name}({required_args})")
        lines.append("")
    return lines


def render_delegate_methods() -> str:
    interfaces = load_interfaces()
    lines = ["    # BEGIN GENERATED RTI SERVICE METHODS"]
    for method_name in sorted(interfaces["RTIambassador"]):
        lines.extend(render_delegate_method(method_name, interfaces["RTIambassador"][method_name]))
    lines.append("    # END GENERATED RTI SERVICE METHODS")
    return "\n".join(lines)


def render_callback_method(method_name: str, method_meta: dict[str, Any]) -> list[str]:
    names, types, min_arity, return_type = canonical_overload(method_meta)
    snake_name = PYTHON_NAME_OVERRIDES.get(method_name, lower_camel_to_snake(method_name))
    lines = [
        f'    @_callback("{method_name}")',
        *indent(format_signature(snake_name, annotated_params(names, types, min_arity, snake=True), return_type), 4),
        "        return None",
        "",
        f'    @_callback("{method_name}")',
        *indent(format_signature(method_name, annotated_params(names, types, min_arity, snake=False), return_type, noqa=True), 4),
    ]
    optional = optional_append_block(names, min_arity, snake=False)
    if optional:
        lines.extend(optional)
        lines.append(f"        return self.{snake_name}(*args)")
    else:
        lines.append(f"        return self.{snake_name}({', '.join(call_args(names, min_arity, snake=False))})")
    lines.append("")
    return lines


def render_spec_impl() -> str:
    interfaces = load_interfaces()
    lines = [
        GENERATED_HEADER.rstrip(),
        '"""Source-named and Pythonic HLA 1516.1-2010 API contracts.',
        "",
        "Java lowerCamelCase method names remain the canonical HLA service names.",
        "Each RTI service and federate callback also exposes the matching Python",
        "snake_case alias with snake_case parameter names.",
        '"""',
        "from __future__ import annotations",
        "",
        "from abc import ABC, abstractmethod",
        "from collections.abc import Sequence",
        "from dataclasses import dataclass",
        "from os import PathLike",
        "import re",
        "from typing import Callable, TypeAlias",
        "",
        "from .enums import *",
        "from .handles import *",
        "from .time import HLAfloat64Interval, HLAfloat64Time, HLAinteger64Interval, HLAinteger64Time, LogicalTimeFactory",
        "from .types import *",
        "from .spec_refs import method_reference",
        "from .spec_sources import method_source_summary",
        "",
        "LogicalTimeLike: TypeAlias = HLAfloat64Time | HLAinteger64Time | float | int",
        "LogicalTimeIntervalLike: TypeAlias = HLAfloat64Interval | HLAinteger64Interval | float | int",
        "LogicalTimeFactoryLike: TypeAlias = LogicalTimeFactory[HLAinteger64Time | HLAfloat64Time, HLAinteger64Interval | HLAfloat64Interval]",
        "URLLike: TypeAlias = str | PathLike[str]",
        "VariableLengthDataLike: TypeAlias = bytes | bytearray | memoryview",
        "",
        "@dataclass(frozen=True)",
        "class SupplementalReceiveInfo:",
        "    producing_federate: FederateHandle | None = None",
        "    sent_regions: RegionHandleSet | None = None",
        "",
        "@dataclass(frozen=True)",
        "class SupplementalReflectInfo:",
        "    producing_federate: FederateHandle | None = None",
        "    sent_regions: RegionHandleSet | None = None",
        "",
        "@dataclass(frozen=True)",
        "class SupplementalRemoveInfo:",
        "    producing_federate: FederateHandle | None = None",
        "    sent_regions: RegionHandleSet | None = None",
        "",
        "",
        "def lower_camel_to_snake(name: str) -> str:",
        '    """Convert a lowerCamelCase HLA method name to snake_case."""',
        '    name = name.replace("HLAversion", "HLAVersion")',
        '    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\\1_\\2", name)',
        '    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\\1_\\2", s1)',
        "    return s2.lower()",
        "",
        "",
        "def _method_doc(method_name: str) -> str:",
        "    ref = method_reference(method_name)",
        "    source_summary = method_source_summary(method_name)",
        "    snake_name = lower_camel_to_snake(method_name)",
        '    doc_parts = [f"{method_name} / {snake_name}"]',
        "    if ref is not None:",
        '        doc_parts.append(f"IEEE reference: {ref.label}.")',
        "    if source_summary:",
        '        doc_parts.append(f"Sources: {source_summary}.")',
        '    return " ".join(doc_parts)',
        "",
        "",
        "def _service_metadata(method_name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:",
        "    def _decorate(method: Callable[..., object]) -> Callable[..., object]:",
        "        method.spec_name = method_name  # type: ignore[attr-defined]",
        "        method.spec_reference = method_reference(method_name)  # type: ignore[attr-defined]",
        "        method.spec_source_summary = method_source_summary(method_name)  # type: ignore[attr-defined]",
        "        method.__doc__ = _method_doc(method_name)",
        "        return method",
        "",
        "    return _decorate",
        "",
        "",
        "def _callback(method_name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:",
        "    def _decorate(method: Callable[..., object]) -> Callable[..., object]:",
        "        method.spec_name = method_name  # type: ignore[attr-defined]",
        "        method.spec_reference = method_reference(method_name)  # type: ignore[attr-defined]",
        "        method.spec_source_summary = method_source_summary(method_name)  # type: ignore[attr-defined]",
        "        method.__doc__ = _method_doc(method_name)",
        "        return method",
        "",
        "    return _decorate",
        "",
        "",
        "class RTIambassador(ABC):",
        '    """Source-named abstract contract for an HLA RTI ambassador."""',
        "",
    ]
    for method_name in sorted(interfaces["RTIambassador"]):
        lines.extend(render_rti_method(method_name, interfaces["RTIambassador"][method_name]))
    lines.extend(
        [
            "",
            "class NullFederateAmbassador:",
            '    """No-op federate callback prototype with Java names and Python aliases."""',
            "",
        ]
    )
    for method_name in sorted(interfaces["FederateAmbassador"]):
        lines.extend(render_callback_method(method_name, interfaces["FederateAmbassador"][method_name]))
    lines.extend(
        [
            'RTIAmbassadorSpec = RTIambassador',
            'NullNullFederateAmbassador = NullFederateAmbassador',
            "",
            "__all__ = [",
            '    "NullFederateAmbassador",',
            '    "NullNullFederateAmbassador",',
            '    "RTIAmbassadorSpec",',
            '    "RTIambassador",',
            '    "SupplementalReceiveInfo",',
            '    "SupplementalReflectInfo",',
            '    "SupplementalRemoveInfo",',
            '    "lower_camel_to_snake",',
            "]",
            "",
        ]
    )
    return "\n".join(lines)


def render_docs() -> str:
    interfaces = load_interfaces()
    lines = [
        "# HLA Interface Contracts",
        "",
        f"Generated from `{API_METADATA_SOURCE}`.",
        "Regenerate with `./tools/contracts generate`.",
        "Double-check with `./tools/contracts check` or `bash scripts/ci/check_generated_docs.sh`.",
        "",
        "Java lowerCamelCase method names are preserved as canonical HLA service and callback names. Python aliases mirror those names in underscore form.",
        "",
    ]
    for interface_name in ("RTIambassador", "FederateAmbassador"):
        lines.extend(
            [
                f"## {interface_name}",
                "",
                "| Java name | Python alias | Signature | Returns |",
                "| --- | --- | --- | --- |",
            ]
        )
        for method_name in sorted(interfaces[interface_name]):
            names, types, min_arity, return_type = canonical_overload(interfaces[interface_name][method_name])
            snake_name = PYTHON_NAME_OVERRIDES.get(method_name, lower_camel_to_snake(method_name))
            if interface_name == "RTIambassador":
                params = alias_params(method_name, names, types, min_arity)
            else:
                params = annotated_params(names, types, min_arity, snake=True)
            signature = f"{snake_name}({', '.join(params[1:])})"
            lines.append(f"| `{method_name}` | `{snake_name}` | `{signature}` | `{return_type}` |")
        lines.append("")
    return "\n".join(lines)


def replace_delegate_methods(base_content: str) -> str:
    start_marker = "    # BEGIN GENERATED RTI SERVICE METHODS"
    end_marker = "    # END GENERATED RTI SERVICE METHODS"
    if start_marker in base_content and end_marker in base_content:
        start = base_content.index(start_marker)
        end = base_content.index(end_marker, start) + len(end_marker)
        return base_content[:start] + render_delegate_methods() + base_content[end:]

    start_anchor = "\n    def abortFederationRestore("
    end_anchor = "\n\nclass RecordingBackend"
    start = base_content.index(start_anchor) + 1
    end = base_content.index(end_anchor, start)
    return base_content[:start] + render_delegate_methods() + base_content[end:]


def expected_base_content() -> str:
    return replace_delegate_methods(BASE_PATH.read_text(encoding="utf-8"))


def expected_outputs() -> dict[Path, str]:
    return {
        DOC_PATH: render_docs(),
        BASE_PATH: expected_base_content(),
    }


def expected_doc_outputs() -> dict[Path, str]:
    return {
        DOC_PATH: render_docs(),
    }


def generate() -> None:
    for path, content in expected_outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def generate_docs() -> None:
    for path, content in expected_doc_outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def check() -> list[str]:
    stale: list[str] = []
    for path, content in expected_outputs().items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(path.relative_to(ROOT).as_posix())
    return stale


def check_docs() -> list[str]:
    stale: list[str] = []
    for path, content in expected_doc_outputs().items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(path.relative_to(ROOT).as_posix())
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate typed HLA interface contracts.")
    parser.add_argument("command", choices=("generate", "check", "generate-docs", "check-docs"))
    args = parser.parse_args()
    if args.command == "generate":
        generate()
        for path in expected_outputs():
            print(path.relative_to(ROOT).as_posix())
        return 0
    if args.command == "generate-docs":
        generate_docs()
        for path in expected_doc_outputs():
            print(path.relative_to(ROOT).as_posix())
        return 0
    if args.command == "check-docs":
        stale = check_docs()
        if stale:
            print("Stale HLA interface contract docs:")
            for path in stale:
                print(f"  {path}")
            return 1
        print("HLA interface contract docs are current")
        return 0
    stale = check()
    if stale:
        print("Stale HLA interface contract outputs:")
        for path in stale:
            print(f"  {path}")
        return 1
    print("HLA interface contract outputs are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
