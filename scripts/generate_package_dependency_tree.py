#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path.cwd()
PACKAGES_DIR = REPO_ROOT / "packages"
OUTPUT_PATH = REPO_ROOT / "docs/package_dependency_tree.md"
INTERNAL_PREFIX = "hla2010-"
DEP_NAME_RE = re.compile(r"^([A-Za-z0-9_.-]+)")


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()


def parse_dep_name(spec: str) -> str:
    match = DEP_NAME_RE.match(spec.strip())
    if not match:
        return spec.strip()
    return match.group(1)


def load_packages() -> dict[str, list[str]]:
    packages: dict[str, list[str]] = {}
    for pyproject in sorted(PACKAGES_DIR.glob("*/pyproject.toml")):
        data = tomllib.loads(pyproject.read_text())
        project = data["project"]
        name = project["name"]
        deps = [parse_dep_name(dep) for dep in project.get("dependencies", [])]
        packages[name] = deps
    return packages


def internal_deps(packages: dict[str, list[str]]) -> dict[str, list[str]]:
    names = set(packages)
    return {
        package: [dep for dep in deps if dep in names]
        for package, deps in packages.items()
    }


def external_deps(packages: dict[str, list[str]]) -> dict[str, list[str]]:
    names = set(packages)
    return {
        package: [dep for dep in deps if dep not in names]
        for package, deps in packages.items()
    }


def reverse_deps(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    reverse: dict[str, list[str]] = defaultdict(list)
    for package, deps in graph.items():
        for dep in deps:
            reverse[dep].append(package)
    for package in graph:
        reverse.setdefault(package, [])
        reverse[package].sort()
    return dict(reverse)


def roots(graph: dict[str, list[str]]) -> list[str]:
    return sorted([package for package, deps in graph.items() if not deps])


def level_map(graph: dict[str, list[str]]) -> dict[str, int]:
    memo: dict[str, int] = {}

    def level(node: str) -> int:
        if node in memo:
            return memo[node]
        deps = graph[node]
        if not deps:
            memo[node] = 0
            return 0
        memo[node] = 1 + max(level(dep) for dep in deps)
        return memo[node]

    for package in graph:
        level(package)
    return memo


def render_layers(graph: dict[str, list[str]]) -> str:
    levels = level_map(graph)
    buckets: dict[int, list[str]] = defaultdict(list)
    for package, layer in levels.items():
        buckets[layer].append(package)
    lines: list[str] = []
    for layer in sorted(buckets):
        packages = ", ".join(f"`{name}`" for name in sorted(buckets[layer]))
        lines.append(f"- Layer {layer}: {packages}")
    return "\n".join(lines)


def render_mermaid(graph: dict[str, list[str]]) -> str:
    lines = ["graph TD"]
    for package in sorted(graph):
        deps = graph[package]
        if not deps:
            lines.append(f"    {package.replace('-', '_')}[{package}]")
            continue
        for dep in sorted(deps):
            lines.append(
                f"    {dep.replace('-', '_')}[{dep}] --> {package.replace('-', '_')}[{package}]"
            )
    return "\n".join(lines)


def render_direct_table(packages: dict[str, list[str]], graph: dict[str, list[str]], external: dict[str, list[str]]) -> str:
    lines = [
        "| Package | Internal deps | External deps |",
        "| --- | --- | --- |",
    ]
    for package in sorted(packages):
        internal_text = ", ".join(graph[package]) if graph[package] else "-"
        external_text = ", ".join(external[package]) if external[package] else "-"
        lines.append(f"| `{package}` | `{internal_text}` | `{external_text}` |")
    return "\n".join(lines)


def render_summary(graph: dict[str, list[str]]) -> str:
    root_nodes = roots(graph)
    lines = [
        "- `hla2010-spec` is the single true root package.",
        "- `hla2010-rti-backend-common`, `hla2010-rti-runtime-common`, `hla2010-rti-transport-common`, and `hla2010-verification-harness` are the shared support layers.",
        "- Python and Java backend families are separated; `hla2010-rti-python` depends on backend-common rather than on Java support packages.",
        "- transport packages depend on `hla2010-spec`, `hla2010-rti-backend-common`, `hla2010-rti-transport-common`, and for hosted transports also `hla2010-rti-runtime-common`.",
        "- FOM and verification leaf packages depend only on `hla2010-spec` and `hla2010-verification-harness`.",
    ]
    if root_nodes != ["hla2010-spec"]:
        lines.append(f"- current roots detected from metadata: `{', '.join(root_nodes)}`.")
    return "\n".join(lines)


def main() -> int:
    packages = load_packages()
    graph = internal_deps(packages)
    external = external_deps(packages)
    layers = render_layers(graph)
    mermaid = render_mermaid(graph)
    table = render_direct_table(packages, graph, external)
    summary = render_summary(graph)

    content = f"""# Package Dependency Tree

This page is generated from the `project.dependencies` fields in
`packages/*/pyproject.toml`.

Regenerate it with:

```bash
./tools/package-deps generate
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
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(content)
    print(f"wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
