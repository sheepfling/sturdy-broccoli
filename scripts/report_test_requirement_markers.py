from __future__ import annotations

import argparse
import ast
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATHS = [
    REPO_ROOT / "tests" / "backends" / "test_python_backend_federation_extended.py",
    REPO_ROOT / "tests" / "backends" / "test_python_backend_object_ownership_extended.py",
]


def _requirement_ids_from_decorator(decorator: ast.expr) -> list[str]:
    if not isinstance(decorator, ast.Call):
        return []
    func = decorator.func
    if not isinstance(func, ast.Attribute) or func.attr != "requirements":
        return []
    return [
        arg.value.strip()
        for arg in decorator.args
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.strip()
    ]


def _rows_for_path(path: Path) -> list[dict[str, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rows: list[dict[str, str]] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
            continue
        requirement_ids: list[str] = []
        for decorator in node.decorator_list:
            requirement_ids.extend(_requirement_ids_from_decorator(decorator))
        for requirement_id in requirement_ids:
            rows.append(
                {
                    "test_path": str(path.relative_to(REPO_ROOT)),
                    "test_name": node.name,
                    "requirement_id": requirement_id,
                }
            )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="List explicit requirement markers carried by pytest tests."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional test file paths to scan. Defaults to the backend modules currently carrying Clause 4 through Clause 10 requirement markers.",
    )
    args = parser.parse_args(argv)

    paths = [Path(item).resolve() for item in args.paths] if args.paths else DEFAULT_PATHS
    rows: list[dict[str, str]] = []
    for path in paths:
        rows.extend(_rows_for_path(path))

    writer = csv.DictWriter(sys.stdout, fieldnames=["test_path", "test_name", "requirement_id"])
    writer.writeheader()
    writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
