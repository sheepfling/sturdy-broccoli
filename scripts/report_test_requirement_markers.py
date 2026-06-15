from __future__ import annotations

import argparse
import csv
import importlib.util
import inspect
import sys
from pathlib import Path

REPO_ROOT = Path.cwd()
DEFAULT_PATHS = [
    REPO_ROOT / "tests" / "backends" / "test_python_backend_federation_extended.py",
    REPO_ROOT / "tests" / "backends" / "test_python_backend_object_ownership_extended.py",
]


def _load_test_module(path: Path) -> object:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load test module from {path}")
    module = importlib.util.module_from_spec(spec)
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    spec.loader.exec_module(module)
    return module


def _rows_for_path(path: Path) -> list[dict[str, str]]:
    module = _load_test_module(path)
    rows: list[dict[str, str]] = []
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if not name.startswith("test_"):
            continue
        requirement_ids: list[str] = []
        for mark in getattr(func, "pytestmark", []):
            if getattr(mark, "name", "") != "requirements":
                continue
            requirement_ids.extend(str(arg).strip() for arg in mark.args if str(arg).strip())
        for requirement_id in requirement_ids:
            rows.append(
                {
                    "test_path": str(path.relative_to(REPO_ROOT)),
                    "test_name": name,
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
