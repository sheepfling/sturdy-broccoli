from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCANNED_ROOTS = (
    ROOT / "packages",
    ROOT / "src",
    ROOT / "tests",
    ROOT / "scripts",
)


def _has_future_annotations(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in tree.body[:5]
    )


def _stringified_annotations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    if not _has_future_annotations(tree):
        return []

    findings: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_arg(self, node: ast.arg) -> None:
            if isinstance(node.annotation, ast.Constant) and isinstance(node.annotation.value, str):
                findings.append(f"{path.relative_to(ROOT).as_posix()}:{node.lineno}: arg {node.arg}")

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if isinstance(node.returns, ast.Constant) and isinstance(node.returns.value, str):
                findings.append(f"{path.relative_to(ROOT).as_posix()}:{node.lineno}: return {node.name}")
            self.generic_visit(node)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            if isinstance(node.annotation, ast.Constant) and isinstance(node.annotation.value, str):
                target = getattr(node.target, "id", None) or getattr(node.target, "attr", "?")
                findings.append(f"{path.relative_to(ROOT).as_posix()}:{node.lineno}: annassign {target}")
            self.generic_visit(node)

    Visitor().visit(tree)
    return findings


def test_future_annotations_modules_do_not_use_stringified_annotations() -> None:
    violations: list[str] = []
    for root in SCANNED_ROOTS:
        for path in sorted(root.rglob("*.py")):
            violations.extend(_stringified_annotations(path))
    assert not violations, "\n".join(violations)
