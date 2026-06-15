from __future__ import annotations

import argparse
import json
import pprint
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "specs" / "hla2010_api.json"
RAW_API_PATH = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "raw_api.py"
API_METADATA_RESOURCE_PATH = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "resources" / "api_metadata.json"
SPEC_INVENTORY_PATH = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "spec_inventory.py"
SPEC_REFS_PATH = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "spec_refs.py"
SPEC_SOURCES_PATH = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "spec_sources.py"

GENERATED_HEADER = """# Generated from specs/hla2010_api.json.
# Do not edit by hand. Run ./tools/spec-api generate.
"""
FEDERATE_INTERFACE_DOCUMENT = "IEEE 1516.1-2010 (2010 edition)"
OMT_DOCUMENT = "IEEE 1516.2-2010 (2010 edition)"


def _format_python(value: object) -> str:
    return pprint.pformat(value, indent=4, sort_dicts=True, width=120)


def _load_source() -> dict[str, object]:
    return json.loads(SOURCE_PATH.read_text(encoding="utf-8"))


def _interfaces(data: dict[str, object]) -> dict[str, dict[str, dict[str, object]]]:
    interfaces = data.get("interfaces")
    if not isinstance(interfaces, dict):
        raise ValueError("spec source must contain an 'interfaces' object")
    normalized: dict[str, dict[str, dict[str, object]]] = {}
    for interface_name, methods in interfaces.items():
        if not isinstance(methods, dict):
            raise ValueError(f"interface {interface_name!r} must map methods to metadata")
        normalized[interface_name] = {}
        for method_name, metadata in methods.items():
            if not isinstance(metadata, dict):
                raise ValueError(f"{interface_name}.{method_name} metadata must be an object")
            normalized[interface_name][method_name] = metadata
    return normalized


def _method_names(interfaces: dict[str, dict[str, dict[str, object]]], interface_name: str) -> list[str]:
    return sorted(interfaces.get(interface_name, {}))


def _api_metadata_payload(interfaces: dict[str, dict[str, dict[str, object]]]) -> dict[str, dict[str, list[dict[str, object]]]]:
    payload: dict[str, dict[str, list[dict[str, object]]]] = {}
    for interface_name, methods in interfaces.items():
        payload[interface_name] = {}
        for method_name, metadata in methods.items():
            overloads = metadata.get("overloads", [])
            if not isinstance(overloads, list):
                raise ValueError(f"{interface_name}.{method_name} overloads must be a list")
            payload[interface_name][method_name] = []
            for overload in overloads:
                if not isinstance(overload, dict):
                    raise ValueError(f"{interface_name}.{method_name} overload entries must be objects")
                payload[interface_name][method_name].append(
                    {
                        "group": overload.get("group"),
                        "language": overload.get("language"),
                        "params": overload.get("params"),
                        "return_type": overload.get("return_type"),
                        "service": overload.get("service"),
                        "source_file": overload.get("source_file"),
                        "source_line": overload.get("source_line"),
                        "throws": overload.get("throws", []),
                    }
                )
    return payload


def _render_raw_api(interfaces: dict[str, dict[str, dict[str, object]]]) -> str:
    parts = [
        GENERATED_HEADER.rstrip(),
        '"""Source-derived metadata surface for HLA IEEE 1516.1-2010 (2010 edition).',
        "",
        "This module intentionally exposes only the generated overload/source metadata.",
        "Contributor-facing interface reading should start with ``hla2010.spec`` and",
        "``hla2010.runtime_api`` instead of this compatibility metadata module.",
        "",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "import json",
        "from importlib import resources",
        "",
        "",
        "def _load_api_metadata() -> dict[str, dict[str, list[dict[str, object]]]]:",
        '    text = resources.files("hla2010").joinpath("resources/api_metadata.json").read_text(encoding="utf-8")',
        "    payload = json.loads(text)",
        "    return payload",
        "",
        "",
        "API_METADATA = _load_api_metadata()",
        "",
        '__all__ = ["API_METADATA"]',
        "",
    ]
    return "\n".join(parts)


def _render_api_metadata_resource(interfaces: dict[str, dict[str, dict[str, object]]]) -> str:
    payload = _api_metadata_payload(interfaces)
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def _render_spec_inventory(interfaces: dict[str, dict[str, dict[str, object]]]) -> str:
    rti_names = _method_names(interfaces, "RTIambassador")
    fed_names = _method_names(interfaces, "FederateAmbassador")
    parts = [
        GENERATED_HEADER.rstrip(),
        '"""Plain-text HLA method inventory for the clean Python spec layer.',
        "",
        "This module deliberately carries only method-name inventories, not the raw API",
        "metadata used by adapter backends.",
        '"""',
        "from __future__ import annotations",
        "",
        "RTIAMBASSADOR_METHODS: tuple[str, ...] = (",
    ]
    parts.extend([f"    {name!r}," for name in rti_names])
    parts.extend(["    )", "", "FEDERATE_AMBASSADOR_METHODS: tuple[str, ...] = ("])
    parts.extend([f"    {name!r}," for name in fed_names])
    parts.extend(["    )", "", '__all__ = ["RTIAMBASSADOR_METHODS", "FEDERATE_AMBASSADOR_METHODS"]', ""])
    return "\n".join(parts)


def _render_spec_refs(interfaces: dict[str, dict[str, dict[str, object]]]) -> str:
    method_ref_data: dict[str, tuple[str, str, str]] = {}
    for methods in interfaces.values():
        for method_name, metadata in methods.items():
            section = metadata.get("section")
            service_group = metadata.get("service_group")
            title = metadata.get("title")
            no_section_reason = metadata.get("no_section_reason")
            if section and service_group and title:
                method_ref_data[method_name] = (str(section), str(service_group), str(title))
            elif not no_section_reason:
                raise ValueError(f"method {method_name} must define section/title/group or no_section_reason")
    parts = [
        GENERATED_HEADER.rstrip(),
        '"""Traceability references for the HLA 1516.1-2010 Python work.',
        "",
        "The values here are section identifiers and titles only. They are intended for",
        "engineering traceability and should not be treated as a replacement for the IEEE",
        "standards.",
        '"""',
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "from typing import Iterable",
        "",
        "",
        "@dataclass(frozen=True)",
        "class SpecReference:",
        "    document: str",
        "    section: str",
        "    title: str",
        "    service_group: str | None = None",
        "    note: str | None = None",
        "",
        "    @property",
        "    def label(self) -> str:",
        '        group = f" ({self.service_group})" if self.service_group else ""',
        '        return f"{self.document} §{self.section} {self.title}{group}"',
        "",
        "    def as_markdown_anchor(self) -> str:",
        '        anchor = self.section.lower().replace(".", "-").replace(" ", "-")',
        '        return f"[{self.document} §{self.section}](#{anchor}) — {self.title}"',
        "",
        "",
        'SERVICE_AREAS: dict[str, SpecReference] = {',
        f'    "federation_management": SpecReference("{FEDERATE_INTERFACE_DOCUMENT}", "4", "Federation management"),',
        f'    "declaration_management": SpecReference("{FEDERATE_INTERFACE_DOCUMENT}", "5", "Declaration management"),',
        f'    "object_management": SpecReference("{FEDERATE_INTERFACE_DOCUMENT}", "6", "Object management"),',
        f'    "ownership_management": SpecReference("{FEDERATE_INTERFACE_DOCUMENT}", "7", "Ownership management"),',
        f'    "time_management": SpecReference("{FEDERATE_INTERFACE_DOCUMENT}", "8", "Time management"),',
        f'    "data_distribution_management": SpecReference("{FEDERATE_INTERFACE_DOCUMENT}", "9", "Data distribution management"),',
        f'    "support_services": SpecReference("{FEDERATE_INTERFACE_DOCUMENT}", "10", "Support services"),',
        f'    "mom": SpecReference("{FEDERATE_INTERFACE_DOCUMENT}", "11", "Management object model"),',
        f'    "language_mappings": SpecReference("{FEDERATE_INTERFACE_DOCUMENT}", "12", "Programming language mappings"),',
        "}",
        "",
        'FOM_REFERENCES: dict[str, SpecReference] = {',
        f'    "omt_components": SpecReference("{OMT_DOCUMENT}", "4", "HLA OMT components"),',
        f'    "object_model_identification": SpecReference("{OMT_DOCUMENT}", "4.1", "Object model identification"),',
        f'    "object_class_structure": SpecReference("{OMT_DOCUMENT}", "4.2", "Object class structure table"),',
        f'    "interaction_class_structure": SpecReference("{OMT_DOCUMENT}", "4.3", "Interaction class structure table"),',
        f'    "attribute_table": SpecReference("{OMT_DOCUMENT}", "4.4", "Attribute table"),',
        f'    "parameter_table": SpecReference("{OMT_DOCUMENT}", "4.5", "Parameter table"),',
        f'    "dimension_table": SpecReference("{OMT_DOCUMENT}", "4.6", "Dimension table"),',
        f'    "time_representation_table": SpecReference("{OMT_DOCUMENT}", "4.7", "Time representation table"),',
        f'    "user_supplied_tag_table": SpecReference("{OMT_DOCUMENT}", "4.8", "User-supplied tag table"),',
        f'    "synchronization_table": SpecReference("{OMT_DOCUMENT}", "4.9", "Synchronization table"),',
        f'    "transportation_type_table": SpecReference("{OMT_DOCUMENT}", "4.10", "Transportation type table"),',
        f'    "update_rate_table": SpecReference("{OMT_DOCUMENT}", "4.11", "Update rate table"),',
        f'    "switches_table": SpecReference("{OMT_DOCUMENT}", "4.12", "Switches table"),',
        f'    "datatype_table": SpecReference("{OMT_DOCUMENT}", "4.13", "Datatype tables"),',
        f'    "notes_table": SpecReference("{OMT_DOCUMENT}", "4.14", "Notes table"),',
        f'    "lexicon": SpecReference("{OMT_DOCUMENT}", "5", "FOM/SOM lexicon"),',
        f'    "conformance": SpecReference("{OMT_DOCUMENT}", "6", "Conformance"),',
        f'    "merging_rules": SpecReference("{OMT_DOCUMENT}", "7", "FOM module/SOM module merging rules"),',
        f'    "dif": SpecReference("{OMT_DOCUMENT}", "Annex D", "OMT data interchange format"),',
        f'    "schema": SpecReference("{OMT_DOCUMENT}", "Annex E", "OMT conformance XML Schema"),',
        "}",
        "",
        f"_METHOD_REFERENCE_DATA: dict[str, tuple[str, str, str]] = {_format_python(method_ref_data)}",
        "",
        "METHOD_REFERENCES: dict[str, SpecReference] = {",
        f'    method: SpecReference("{FEDERATE_INTERFACE_DOCUMENT}", section, title, group)',
        "    for method, (section, group, title) in _METHOD_REFERENCE_DATA.items()",
        "}",
        "",
        "",
        "def snake_to_lower_camel(name: str) -> str:",
        '    parts = name.split("_")',
        "    if not parts:",
        "        return name",
        '    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])',
        "",
        "",
        "def method_reference(method_name: str) -> SpecReference | None:",
        '    """Return the spec reference for a lowerCamelCase or snake_case API method."""',
        "    direct = METHOD_REFERENCES.get(method_name)",
        "    if direct is not None:",
        "        return direct",
        "    camel = snake_to_lower_camel(method_name)",
        "    converted = METHOD_REFERENCES.get(camel)",
        "    if converted is not None:",
        "        return converted",
        "    lowered = camel.lower()",
        "    for key, ref in METHOD_REFERENCES.items():",
        "        if key.lower() == lowered:",
        "            return ref",
        "    return None",
        "",
        "",
        "def method_label(method_name: str) -> str:",
        "    ref = method_reference(method_name)",
        '    return ref.label if ref else "unmapped HLA service"',
        "",
        "",
        "def iter_method_references(prefixes: Iterable[str] | None = None):",
        "    prefixes_tuple = tuple(prefixes or ())",
        "    for method in sorted(METHOD_REFERENCES):",
        '        if not prefixes_tuple or method.startswith(prefixes_tuple):',
        "            yield method, METHOD_REFERENCES[method]",
        "",
        "",
        '__all__ = ["FOM_REFERENCES", "METHOD_REFERENCES", "SERVICE_AREAS", "SpecReference", "iter_method_references", "method_label", "method_reference", "snake_to_lower_camel"]',
        "",
    ]
    return "\n".join(parts)


def _render_spec_sources() -> str:
    return "\n".join(
        [
            GENERATED_HEADER.rstrip(),
            '"""Readable source references for the HLA 1516.1-2010 Python work.',
            "",
            "This module keeps the Java and C++ source locations in ordinary Python strings",
            "so the clean spec layer can surface them directly in docstrings.",
            '"""',
            "from __future__ import annotations",
            "",
            "from functools import lru_cache",
            "",
            "from .raw_api import API_METADATA",
            "",
            '_LANGUAGE_LABELS = {"cpp": "C++", "java": "Java"}',
            "",
            "",
            "@lru_cache(maxsize=None)",
            "def method_source_summary(method_name: str) -> str | None:",
            '    """Return a human-readable summary of Java and C++ source locations."""',
            "    entries: list[str] = []",
            "    seen: set[str] = set()",
            '    for class_name in ("RTIambassador", "FederateAmbassador"):',
            '        for item in API_METADATA[class_name].get(method_name, ()):',
            '            language_key = item.get("language")',
            '            if isinstance(language_key, str):',
            '                language = _LANGUAGE_LABELS.get(language_key, language_key)',
            "            else:",
            '                language = "source"',
            '            source_file = item.get("source_file")',
            '            source_line = item.get("source_line")',
            "            if not source_file or source_line is None:",
            "                continue",
            '            label = f"{language}: {source_file}:{source_line}"',
            "            if label not in seen:",
            "                seen.add(label)",
            "                entries.append(label)",
            '    return "; ".join(entries) if entries else None',
            "",
        ]
    )


def _expected_outputs() -> dict[Path, str]:
    data = _load_source()
    interfaces = _interfaces(data)
    return {
        RAW_API_PATH: _render_raw_api(interfaces),
        API_METADATA_RESOURCE_PATH: _render_api_metadata_resource(interfaces),
        SPEC_INVENTORY_PATH: _render_spec_inventory(interfaces),
        SPEC_REFS_PATH: _render_spec_refs(interfaces),
        SPEC_SOURCES_PATH: _render_spec_sources(),
    }


def _write_outputs() -> None:
    for path, content in _expected_outputs().items():
        path.write_text(content, encoding="utf-8")


def _check_outputs() -> list[str]:
    errors: list[str] = []
    for path, expected in _expected_outputs().items():
        current = path.read_text(encoding="utf-8")
        if current != expected:
            errors.append(path.relative_to(ROOT).as_posix())
    return errors


def _bootstrap_from_current() -> None:
    from hla2010.raw_api import API_METADATA
    from hla2010.spec_refs import method_reference

    payload: dict[str, object] = {"interfaces": {}}
    interfaces: dict[str, object] = {}
    for interface_name in ("RTIambassador", "FederateAmbassador"):
        methods: dict[str, object] = {}
        for method_name, overloads in API_METADATA[interface_name].items():
            ref = method_reference(method_name)
            python_name = method_name if interface_name == "RTIambassador" else _camel_to_snake(method_name)
            methods[method_name] = {
                "python_name": python_name,
                "section": ref.section if ref else None,
                "service_group": ref.service_group if ref else None,
                "title": ref.title if ref else None,
                "no_section_reason": None if ref else "no generated spec reference",
                "overloads": list(overloads),
            }
        interfaces[interface_name] = methods
    payload["interfaces"] = interfaces
    SOURCE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _camel_to_snake(name: str) -> str:
    chars: list[str] = []
    for index, char in enumerate(name):
        if char.isupper() and index:
            chars.append("_")
        chars.append(char.lower())
    return "".join(chars)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or validate HLA API metadata outputs.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("generate")
    subparsers.add_parser("check")
    subparsers.add_parser("bootstrap-current")
    args = parser.parse_args()

    if args.command == "bootstrap-current":
        _bootstrap_from_current()
        print(SOURCE_PATH.relative_to(ROOT).as_posix())
        return 0
    if args.command == "generate":
        _write_outputs()
        for path in _expected_outputs():
            print(path.relative_to(ROOT).as_posix())
        return 0

    errors = _check_outputs()
    if errors:
        print("API metadata outputs are out of date")
        for item in errors:
            print(f"- {item}")
        return 1
    print("API metadata outputs are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
