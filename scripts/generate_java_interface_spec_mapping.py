#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

import tomllib


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "docs" / "reference" / "java_interface_spec_mapping.md"
RTI_2025_PATH = ROOT / "packages" / "hla-rti1516-2025" / "src" / "hla" / "rti1516_2025" / "rti_ambassador.py"
FED_2025_PATH = ROOT / "packages" / "hla-rti1516-2025" / "src" / "hla" / "rti1516_2025" / "federate_ambassador.py"


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


def _parse_protocol_methods(path: Path, class_name: str) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {item.name for item in node.body if isinstance(item, ast.FunctionDef)}
    raise RuntimeError(f"Could not find class {class_name!r} in {path}")


def _load_rows() -> tuple[dict[str, list[dict[str, object]]], dict[str, list[object]], set[str], set[str]]:
    from hla.backends.common import get_deterministic_java_invocation_router
    from hla.rti1516e.raw_api import API_METADATA

    deterministic_routes = {}
    for route in get_deterministic_java_invocation_router().routes:
        deterministic_routes.setdefault(route.method_name, []).append(route)

    rti_2025_methods = _parse_protocol_methods(RTI_2025_PATH, "RTIambassador")
    fed_2025_methods = _parse_protocol_methods(FED_2025_PATH, "FederateAmbassador")
    return API_METADATA, deterministic_routes, rti_2025_methods, fed_2025_methods


def _java_overloads(overloads: list[dict[str, object]]) -> list[dict[str, object]]:
    return [overload for overload in overloads if overload.get("language") == "java"]


def _params_tuple(params: str) -> tuple[str, ...]:
    parts = [part.strip() for part in params.split(",") if part.strip()]
    return tuple(part.rsplit(" ", 1)[-1].replace("...", "") for part in parts)


def _route_policy(
    interface: str,
    method_name: str,
    params: str,
    java_overload_count: int,
    deterministic_routes: dict[str, list[object]],
) -> str:
    if interface == "FederateAmbassador":
        return "direct-callback-dispatch"

    if java_overload_count == 0:
        return "no-java-overload"

    route_params = _params_tuple(params)
    for route in deterministic_routes.get(method_name, ()):
        if tuple(getattr(route, "params")) == route_params:
            return "explicit-deterministic"

    if java_overload_count == 1:
        return "single-java-overload"

    return "weighted-or-shape-selected"


def _summary_counts(
    api_metadata: dict[str, dict[str, list[dict[str, object]]]],
    deterministic_routes: dict[str, list[object]],
) -> dict[str, int]:
    rti_methods = api_metadata["RTIambassador"]
    fed_methods = api_metadata["FederateAmbassador"]
    rti_java_rows = sum(len(_java_overloads(overloads)) for overloads in rti_methods.values())
    fed_java_rows = sum(len(_java_overloads(overloads)) for overloads in fed_methods.values())
    explicit_rows = sum(len(routes) for routes in deterministic_routes.values())
    weighted_rows = 0
    single_rows = 0
    for method_name, overloads in rti_methods.items():
        java_overloads = _java_overloads(overloads)
        for overload in java_overloads:
            policy = _route_policy(
                "RTIambassador",
                method_name,
                str(overload.get("params", "")),
                len(java_overloads),
                deterministic_routes,
            )
            if policy == "weighted-or-shape-selected":
                weighted_rows += 1
            elif policy == "single-java-overload":
                single_rows += 1
    return {
        "rti_methods": len(rti_methods),
        "fed_methods": len(fed_methods),
        "rti_java_rows": rti_java_rows,
        "fed_java_rows": fed_java_rows,
        "explicit_rows": explicit_rows,
        "weighted_rows": weighted_rows,
        "single_rows": single_rows,
    }


def _render_interface_table(
    interface: str,
    methods: dict[str, list[dict[str, object]]],
    deterministic_routes: dict[str, list[object]],
    methods_2025: set[str],
) -> list[str]:
    lines = [
        f"## {interface}",
        "",
        "| Method | Group | Spec Ref | Java Params | Route Policy | 2025 Surface |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for method_name in sorted(methods):
        java_overloads = _java_overloads(methods[method_name])
        if not java_overloads:
            lines.append(
                f"| `{method_name}` | n/a | n/a | `n/a` | `no-java-overload` | `{'yes' if method_name in methods_2025 else 'no'}` |"
            )
            continue
        for overload in java_overloads:
            params = str(overload.get("params", "")).strip() or "(none)"
            policy = _route_policy(interface, method_name, str(overload.get("params", "")), len(java_overloads), deterministic_routes)
            lines.append(
                f"| `{method_name}` | `{overload.get('group', 'n/a')}` | `{overload.get('service', 'n/a')}` | "
                f"`{params}` | `{policy}` | `{'yes' if method_name in methods_2025 else 'no'}` |"
            )
    lines.append("")
    return lines


def render() -> str:
    api_metadata, deterministic_routes, rti_2025_methods, fed_2025_methods = _load_rows()
    counts = _summary_counts(api_metadata, deterministic_routes)

    lines = [
        "# Java Interface Spec Mapping",
        "",
        "Generated from source metadata. Do not edit by hand.",
        "Regenerate with `python3 scripts/generate_java_interface_spec_mapping.py`.",
        "Double-check with `./tools/java spec-map --check` or `bash scripts/ci/check_generated_docs.sh`.",
        "",
        "This page is the deterministic cross-language mapping reference for the Java HLA surface used by the JPype and Py4J routes.",
        "",
        "## Summary",
        "",
        f"- `RTIambassador` methods in 2010 metadata: `{counts['rti_methods']}`",
        f"- `FederateAmbassador` callbacks in 2010 metadata: `{counts['fed_methods']}`",
        f"- Java RTI overload rows mapped here: `{counts['rti_java_rows']}`",
        f"- Java callback overload rows mapped here: `{counts['fed_java_rows']}`",
        f"- Explicit deterministic overload rows: `{counts['explicit_rows']}`",
        f"- Weighted-or-shape-selected overload rows: `{counts['weighted_rows']}`",
        f"- Single-java-overload rows: `{counts['single_rows']}`",
        "",
        "## Route Policy Legend",
        "",
        "- `explicit-deterministic`: this exact Java overload has an explicit router entry in the deterministic router table.",
        "- `single-java-overload`: this method has only one Java overload in the source metadata, so no overload choice is required.",
        "- `weighted-or-shape-selected`: multiple Java overloads exist, but this exact overload is not in the explicit deterministic table and therefore remains on the weighted/shape-selected path.",
        "- `direct-callback-dispatch`: inbound Java callback shape is dispatched directly by callback name and converted by signature metadata.",
        "- `no-java-overload`: the 2010 source metadata does not carry a Java overload row for this method.",
        "",
        "## Source Authorities",
        "",
        "- `packages/hla-rti1516e/src/hla/rti1516e/api_metadata.json` via `hla.rti1516e.raw_api.API_METADATA`",
        "- `packages/hla-backend-common/src/hla/backends/common/invocation.py` deterministic router table",
        "- `packages/hla-rti1516-2025/src/hla/rti1516_2025/rti_ambassador.py`",
        "- `packages/hla-rti1516-2025/src/hla/rti1516_2025/federate_ambassador.py`",
        "",
    ]
    lines.extend(_render_interface_table("RTIambassador", api_metadata["RTIambassador"], deterministic_routes, rti_2025_methods))
    lines.extend(_render_interface_table("FederateAmbassador", api_metadata["FederateAmbassador"], deterministic_routes, fed_2025_methods))
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the Java interface spec mapping reference.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args(argv)

    _bootstrap_source_checkout()
    args.output.write_text(render(), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
