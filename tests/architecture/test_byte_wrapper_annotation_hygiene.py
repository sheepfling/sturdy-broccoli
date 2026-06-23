from __future__ import annotations

import ast
from pathlib import Path

BYTE_WRAPPER_SURFACE_PATHS = (
    Path("packages/hla-rti1516e/src/hla/rti1516e/_byte_wrapper.py"),
    Path("packages/hla-rti1516-2025/src/hla/rti1516_2025/_byte_wrapper.py"),
)


def _read(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())


def _has_future_annotations_import(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            return any(alias.name == "annotations" for alias in node.names)
        return False
    return False


def _stringified_annotation_nodes(tree: ast.Module) -> list[tuple[str, int]]:
    findings: list[tuple[str, int]] = []

    def _visit_function(node: ast.FunctionDef | ast.AsyncFunctionDef, owner: str = "") -> None:
        full_name = f"{owner}{node.name}" if owner else node.name
        if isinstance(node.returns, ast.Constant) and isinstance(node.returns.value, str):
            findings.append((full_name, node.returns.lineno))
        for arg in (*node.args.args, *node.args.posonlyargs, *node.args.kwonlyargs, node.args.vararg, node.args.kwarg):
            if arg is not None and isinstance(arg.annotation, ast.Constant) and isinstance(arg.annotation.value, str):
                findings.append((f"{full_name}:{arg.arg}", arg.lineno))
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _visit_function(child, f"{full_name}.")

    def _visit_class(node: ast.ClassDef, owner: str = "") -> None:
        class_owner = f"{owner}{node.name}."
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _visit_function(child, class_owner)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _visit_function(node)
        elif isinstance(node, ast.ClassDef):
            _visit_class(node)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.annotation, ast.Constant) and isinstance(node.annotation.value, str):
            findings.append(("module", node.lineno))

    return findings


def _has_type_checking_import(tree: ast.Module) -> bool:
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module != "typing":
            continue
        if any(alias.name == "TYPE_CHECKING" for alias in node.names):
            return True
    return False


def test_byte_wrapper_protocol_modules_use_future_annotations() -> None:
    for relpath in BYTE_WRAPPER_SURFACE_PATHS:
        path = Path(__file__).resolve().parents[2] / relpath
        tree = _read(path)
        assert _has_future_annotations_import(tree), path


def test_byte_wrapper_protocol_modules_avoid_stringified_annotations() -> None:
    for relpath in BYTE_WRAPPER_SURFACE_PATHS:
        path = Path(__file__).resolve().parents[2] / relpath
        tree = _read(path)
        hits = _stringified_annotation_nodes(tree)
        assert not hits, (path, hits)


def test_byte_wrapper_protocol_modules_do_not_import_type_checking() -> None:
    for relpath in BYTE_WRAPPER_SURFACE_PATHS:
        path = Path(__file__).resolve().parents[2] / relpath
        tree = _read(path)
        assert not _has_type_checking_import(tree), path
