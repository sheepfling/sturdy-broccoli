from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = (ROOT / "src", *(ROOT / "packages").glob("*/src"))
SKIP_PATH_PARTS = {
    "src/hla.verification.repo_internal",
}


def _should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return any(rel == skip or rel.startswith(f"{skip}/") for skip in SKIP_PATH_PARTS)


def _module_name(source_root: Path, path: Path) -> str:
    rel = path.relative_to(source_root).with_suffix("")
    parts = rel.parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _module_maps() -> tuple[dict[str, Path], dict[Path, str]]:
    module_to_path: dict[str, Path] = {}
    path_to_module: dict[Path, str] = {}
    for source_root in SOURCE_ROOTS:
        if not source_root.exists():
            continue
        for path in sorted(source_root.rglob("*.py")):
            if _should_skip(path):
                continue
            module = _module_name(source_root, path)
            if not module:
                continue
            module_to_path[module] = path
            path_to_module[path] = module
    return module_to_path, path_to_module


def _resolve_import_target(target: str, module_to_path: dict[str, Path]) -> str | None:
    while target:
        if target in module_to_path:
            return target
        target = target.rpartition(".")[0]
    return None


def _relative_target(current_module: str, level: int, imported: str | None) -> str:
    package_parts = current_module.split(".")
    current_path = package_parts[:-1]
    base_parts = current_path[: max(0, len(current_path) - level + 1)]
    if imported:
        base_parts.extend(imported.split("."))
    return ".".join(part for part in base_parts if part)


def _import_edges(module_to_path: dict[str, Path], path_to_module: dict[Path, str]) -> dict[str, set[str]]:
    edges: dict[str, set[str]] = defaultdict(set)
    for path, module in path_to_module.items():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            target: str | None = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = _resolve_import_target(alias.name, module_to_path)
                    if target and target != module:
                        edges[module].add(target)
            elif isinstance(node, ast.ImportFrom):
                raw_target = _relative_target(module, node.level, node.module) if node.level else (node.module or "")
                target = _resolve_import_target(raw_target, module_to_path)
                if target and target != module:
                    edges[module].add(target)
    return edges


def _strongly_connected_components(nodes: set[str], edges: dict[str, set[str]]) -> list[tuple[str, ...]]:
    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[tuple[str, ...]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in edges.get(node, ()):
            if target not in indices:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[target])
        if lowlinks[node] == indices[node]:
            component: list[str] = []
            while True:
                target = stack.pop()
                on_stack.remove(target)
                component.append(target)
                if target == node:
                    break
            if len(component) > 1:
                components.append(tuple(sorted(component)))

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return sorted(components, key=lambda item: (len(item), item))


def test_maintained_source_roots_have_no_import_cycles() -> None:
    module_to_path, path_to_module = _module_maps()
    edges = _import_edges(module_to_path, path_to_module)
    cycles = _strongly_connected_components(set(module_to_path), edges)
    assert not cycles, "\n".join(" -> ".join(cycle) for cycle in cycles)
