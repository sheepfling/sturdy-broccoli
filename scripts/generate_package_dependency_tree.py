#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path.cwd()
OUTPUT_PATH = REPO_ROOT / "docs/package_dependency_tree.md"
ANALYSIS_OUTPUT_PATH = REPO_ROOT / "analysis/package_graph.json"


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla2010_repo_internal.package_graph import build_analysis_payload, load_package_graph


def render_layers(graph: dict[str, dict[str, object]]) -> str:
    buckets: dict[int, list[str]] = {}
    for package_name, entry in graph.items():
        layer = int(entry["layer"])
        buckets.setdefault(layer, []).append(package_name)
    lines: list[str] = []
    for layer in sorted(buckets):
        packages = ", ".join(f"`{name}`" for name in sorted(buckets[layer]))
        lines.append(f"- Layer {layer}: {packages}")
    return "\n".join(lines)


def render_mermaid(graph: dict[str, dict[str, object]]) -> str:
    lines = ["graph TD"]
    for package in sorted(graph):
        deps = sorted(str(dep) for dep in graph[package].get("may_depend_on", []))
        if not deps:
            lines.append(f"    {package.replace('-', '_')}[{package}]")
            continue
        for dep in sorted(deps):
            lines.append(
                f"    {dep.replace('-', '_')}[{dep}] --> {package.replace('-', '_')}[{package}]"
            )
    return "\n".join(lines)


def render_direct_table(analysis_packages: dict[str, object]) -> str:
    lines = [
        "| Package | Layer | Role | Internal deps | External deps |",
        "| --- | --- | --- | --- | --- |",
    ]
    for package in sorted(analysis_packages):
        entry = analysis_packages[package]
        internal = entry["declared_internal_dependencies"]
        external = entry["declared_external_dependencies"]
        internal_text = ", ".join(internal) if internal else "-"
        external_text = ", ".join(external) if external else "-"
        lines.append(
            f"| `{package}` | `{entry['layer']}` | `{entry['role']}` | `{internal_text}` | `{external_text}` |"
        )
    return "\n".join(lines)


def render_summary(graph: dict[str, dict[str, object]]) -> str:
    root_nodes = sorted(package for package, entry in graph.items() if not entry.get("may_depend_on"))
    support_packages = sorted(
        package
        for package, entry in graph.items()
        if str(entry["role"]) in {"backend-support", "runtime-support", "transport-support", "verification-harness"}
    )
    transport_packages = sorted(package for package, entry in graph.items() if str(entry["role"]) == "transport")
    leaf_packages = sorted(package for package, entry in graph.items() if str(entry["role"]) == "fom-example")
    lines = [
        "- `hla2010-spec` is the single true root package.",
        f"- Shared support packages: {', '.join(f'`{name}`' for name in support_packages)}.",
        "- Python and Java backend families are separated; `hla2010-rti-python` depends on backend-common rather than on Java support packages.",
        f"- Transport packages are explicit leaves in the graph: {', '.join(f'`{name}`' for name in transport_packages)}.",
        f"- FOM/example leaf packages are explicit in the graph: {', '.join(f'`{name}`' for name in leaf_packages)}.",
    ]
    if root_nodes != ["hla2010-spec"]:
        lines.append(f"- current roots detected from metadata: `{', '.join(root_nodes)}`.")
    return "\n".join(lines)


def build_outputs(repo_root: Path) -> tuple[str, str]:
    graph_path = repo_root / "packages" / "package_graph.yaml"
    if not graph_path.exists():
        graph_path = SCRIPT_REPO_ROOT / "packages" / "package_graph.yaml"
    graph = load_package_graph(graph_path)
    analysis_payload = build_analysis_payload(graph_path=graph_path, packages_dir=repo_root / "packages")
    layers = render_layers(graph)
    mermaid = render_mermaid(graph)
    table = render_direct_table(analysis_payload["packages"])
    summary = render_summary(graph)

    content = f"""# Package Dependency Tree

This page is generated from the machine-readable package graph at
`packages/package_graph.yaml` and validated against the direct dependency
metadata in `packages/*/pyproject.toml`.

Use it as the evidence view, not the primary human ownership guide.

- For the canonical human package hierarchy, read [`package_layout.md`](package_layout.md).
- For the import/dependency guardrails, read [`import_boundary_rules.md`](import_boundary_rules.md).

Regenerate it with:

```bash
./tools/package-deps generate
```

Check it with:

```bash
./tools/package-deps check
```

## Summary

{summary}

## Dependency Layers

{layers}

## Direct Graph

```mermaid
{mermaid}
```

## Direct Dependencies

{table}
"""
    analysis_text = json.dumps(analysis_payload, indent=2, sort_keys=True) + "\n"
    return content, analysis_text


def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "generate"
    if command not in {"generate", "check"}:
        print(f"error: unknown command {command!r}; expected generate or check", file=sys.stderr)
        return 2

    graph_path = REPO_ROOT / "packages" / "package_graph.yaml"
    if not graph_path.exists():
        graph_path = SCRIPT_REPO_ROOT / "packages" / "package_graph.yaml"
    content, analysis_text = build_outputs(REPO_ROOT)

    if command == "check":
        failures: list[str] = []
        actual_doc = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else None
        actual_analysis = ANALYSIS_OUTPUT_PATH.read_text(encoding="utf-8") if ANALYSIS_OUTPUT_PATH.exists() else None
        if actual_doc != content:
            failures.append(str(OUTPUT_PATH))
        if actual_analysis != analysis_text:
            failures.append(str(ANALYSIS_OUTPUT_PATH))
        if failures:
            for failure in failures:
                print(f"stale generated package graph artifact: {failure}", file=sys.stderr)
            return 1
        print("package dependency tree artifacts are current")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content, encoding="utf-8")
    ANALYSIS_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ANALYSIS_OUTPUT_PATH.write_text(analysis_text, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")
    print(f"wrote {ANALYSIS_OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
