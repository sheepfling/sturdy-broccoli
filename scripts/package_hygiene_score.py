#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGES_DIR = ROOT / "packages"

_TYPE_IGNORE_RE = re.compile(r"#\s*type:\s*ignore\b")
_PYRIGHT_IGNORE_RE = re.compile(r"#\s*pyright:\s*ignore\b")
_NOQA_RE = re.compile(r"#\s*noqa(?::.*)?$")


@dataclass(slots=True)
class PackageReport:
    package: str
    role: str
    status: str
    backend_names: tuple[str, ...]
    source_roots: tuple[str, ...]
    python_files: int
    test_files: int
    loc: int
    modules_with_future_annotations: int
    modules_missing_future_annotations: int
    functions_total: int
    functions_fully_annotated: int
    any_count: int
    cast_count: int
    type_ignore_count: int
    pyright_ignore_count: int
    noqa_count: int
    quoted_annotation_count: int
    bare_except_count: int
    tests_present: bool
    pyright_ok: bool | None
    pyright_returncode: int | None
    ruff_ok: bool | None
    ruff_returncode: int | None
    remediation_points: float
    score: int
    grade: str


class _SmellVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.functions_total = 0
        self.functions_fully_annotated = 0
        self.any_count = 0
        self.cast_count = 0
        self.quoted_annotation_count = 0
        self.bare_except_count = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == "Any":
            self.any_count += 1
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "Any":
            self.any_count += 1
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name) and func.id == "cast":
            self.cast_count += 1
        elif isinstance(func, ast.Attribute) and func.attr == "cast":
            self.cast_count += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self.bare_except_count += 1
        self.generic_visit(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.functions_total += 1
        parameters = [
            arg
            for arg in (
                list(node.args.posonlyargs)
                + list(node.args.args)
                + list(node.args.kwonlyargs)
            )
            if arg.arg not in {"self", "cls"}
        ]
        has_full_param_annotations = all(arg.annotation is not None for arg in parameters)
        if node.args.vararg is not None and node.args.vararg.annotation is None:
            has_full_param_annotations = False
        if node.args.kwarg is not None and node.args.kwarg.annotation is None:
            has_full_param_annotations = False
        if has_full_param_annotations and node.returns is not None:
            self.functions_fully_annotated += 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Score split packages for typing / hygiene smell density.",
    )
    parser.add_argument(
        "--package",
        action="append",
        default=[],
        help="Only include packages whose directory name contains this substring.",
    )
    parser.add_argument(
        "--pyright",
        action="store_true",
        help="Run pyright against each package source root.",
    )
    parser.add_argument(
        "--ruff",
        action="store_true",
        help="Run ruff check against each package source root.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of the default table.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Leaderboard length for best/worst/easy-win summaries.",
    )
    return parser.parse_args()


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _discover_package_dirs(filters: list[str]) -> list[Path]:
    matches: list[Path] = []
    for pyproject_path in sorted(PACKAGES_DIR.glob("*/pyproject.toml")):
        package_dir = pyproject_path.parent
        if filters and not any(token in package_dir.name for token in filters):
            continue
        matches.append(package_dir)
    return matches


def _source_roots(package_dir: Path, pyproject: dict[str, Any]) -> tuple[Path, ...]:
    package_meta = pyproject.get("tool", {}).get("hla", {}).get("package", {})
    configured = package_meta.get("source_roots")
    if isinstance(configured, list) and configured:
        roots = [ROOT / str(entry) for entry in configured]
        return tuple(root for root in roots if root.exists())
    src_dir = package_dir / "src"
    return (src_dir,) if src_dir.exists() else ()


def _test_file_count(package_dir: Path) -> int:
    tests_dir = package_dir / "tests"
    if not tests_dir.exists():
        return 0
    return sum(1 for path in tests_dir.rglob("*.py") if path.is_file())


def _module_has_future_annotations(tree: ast.Module) -> bool:
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module != "__future__":
            continue
        if any(alias.name == "annotations" for alias in node.names):
            return True
    return False


def _count_quoted_annotations(tree: ast.AST) -> int:
    count = 0
    for node in ast.walk(tree):
        annotation: Any | None = None
        if isinstance(node, ast.AnnAssign):
            annotation = node.annotation
        elif isinstance(node, (ast.arg, ast.FunctionDef, ast.AsyncFunctionDef)):
            annotation = getattr(node, "annotation", None)
        if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            count += 1
        returns = getattr(node, "returns", None)
        if isinstance(returns, ast.Constant) and isinstance(returns.value, str):
            count += 1
    return count


def _scan_sources(source_roots: tuple[Path, ...]) -> dict[str, Any]:
    python_files = 0
    loc = 0
    modules_with_future_annotations = 0
    modules_missing_future_annotations = 0
    functions_total = 0
    functions_fully_annotated = 0
    any_count = 0
    cast_count = 0
    type_ignore_count = 0
    pyright_ignore_count = 0
    noqa_count = 0
    quoted_annotation_count = 0
    bare_except_count = 0

    for source_root in source_roots:
        for path in sorted(source_root.rglob("*.py")):
            if not path.is_file():
                continue
            python_files += 1
            text = path.read_text(encoding="utf-8")
            loc += sum(1 for line in text.splitlines() if line.strip())
            type_ignore_count += len(_TYPE_IGNORE_RE.findall(text))
            pyright_ignore_count += len(_PYRIGHT_IGNORE_RE.findall(text))
            noqa_count += len(_NOQA_RE.findall(text))

            try:
                tree = ast.parse(text, filename=str(path))
            except SyntaxError:
                modules_missing_future_annotations += 1
                continue

            if _module_has_future_annotations(tree):
                modules_with_future_annotations += 1
            else:
                modules_missing_future_annotations += 1

            visitor = _SmellVisitor()
            visitor.visit(tree)
            functions_total += visitor.functions_total
            functions_fully_annotated += visitor.functions_fully_annotated
            any_count += visitor.any_count
            cast_count += visitor.cast_count
            bare_except_count += visitor.bare_except_count
            quoted_annotation_count += _count_quoted_annotations(tree)

    return {
        "python_files": python_files,
        "loc": loc,
        "modules_with_future_annotations": modules_with_future_annotations,
        "modules_missing_future_annotations": modules_missing_future_annotations,
        "functions_total": functions_total,
        "functions_fully_annotated": functions_fully_annotated,
        "any_count": any_count,
        "cast_count": cast_count,
        "type_ignore_count": type_ignore_count,
        "pyright_ignore_count": pyright_ignore_count,
        "noqa_count": noqa_count,
        "quoted_annotation_count": quoted_annotation_count,
        "bare_except_count": bare_except_count,
    }


def _run_check(argv: list[str]) -> tuple[bool | None, int | None]:
    try:
        completed = subprocess.run(
            argv,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except OSError:
        return None, None
    return completed.returncode == 0, completed.returncode


def _run_pyright(source_roots: tuple[Path, ...]) -> tuple[bool | None, int | None]:
    return _run_check([sys.executable, "-m", "pyright", *[str(path) for path in source_roots]])


def _run_ruff(source_roots: tuple[Path, ...]) -> tuple[bool | None, int | None]:
    return _run_check([sys.executable, "-m", "ruff", "check", *[str(path) for path in source_roots]])


def _score_report(metrics: dict[str, Any], *, pyright_ok: bool | None, ruff_ok: bool | None) -> tuple[int, str]:
    score = 100.0

    functions_total = max(int(metrics["functions_total"]), 1)
    typed_ratio = float(metrics["functions_fully_annotated"]) / functions_total

    python_files = max(int(metrics["python_files"]), 1)
    missing_future_ratio = float(metrics["modules_missing_future_annotations"]) / python_files

    score -= (1.0 - typed_ratio) * 30.0
    score -= missing_future_ratio * 15.0
    score -= min(float(metrics["any_count"]) * 0.20, 18.0)
    score -= min(float(metrics["cast_count"]) * 0.35, 14.0)
    score -= min(float(metrics["type_ignore_count"]) * 1.5, 20.0)
    score -= min(float(metrics["pyright_ignore_count"]) * 2.0, 16.0)
    score -= min(float(metrics["quoted_annotation_count"]) * 0.5, 10.0)
    score -= min(float(metrics["bare_except_count"]) * 2.5, 10.0)
    score -= min(float(metrics["noqa_count"]) * 0.2, 6.0)

    if pyright_ok is False:
        score -= 15.0
    elif pyright_ok is None:
        score -= 0.0

    if ruff_ok is False:
        score -= 8.0
    elif ruff_ok is None:
        score -= 0.0

    clamped = max(0, min(100, round(score)))
    if clamped >= 90:
        grade = "A"
    elif clamped >= 80:
        grade = "B"
    elif clamped >= 70:
        grade = "C"
    elif clamped >= 60:
        grade = "D"
    else:
        grade = "F"
    return clamped, grade


def _remediation_points(metrics: dict[str, Any], *, pyright_ok: bool | None, ruff_ok: bool | None) -> float:
    points = 0.0
    points += float(metrics["modules_missing_future_annotations"]) * 2.0
    points += float(metrics["type_ignore_count"]) * 3.0
    points += float(metrics["pyright_ignore_count"]) * 4.0
    points += float(metrics["bare_except_count"]) * 3.0
    points += float(metrics["cast_count"]) * 1.5
    points += float(metrics["quoted_annotation_count"]) * 0.75
    points += float(metrics["noqa_count"]) * 0.5
    points += float(metrics["any_count"]) * 0.05
    if pyright_ok is False:
        points += 8.0
    if ruff_ok is False:
        points += 4.0
    return round(points, 1)


def _build_report(package_dir: Path, *, run_pyright: bool, run_ruff: bool) -> PackageReport:
    pyproject = _load_toml(package_dir / "pyproject.toml")
    package_meta = pyproject.get("tool", {}).get("hla", {}).get("package", {})
    source_roots = _source_roots(package_dir, pyproject)
    metrics = _scan_sources(source_roots)
    pyright_ok, pyright_returncode = _run_pyright(source_roots) if run_pyright and source_roots else (None, None)
    ruff_ok, ruff_returncode = _run_ruff(source_roots) if run_ruff and source_roots else (None, None)
    score, grade = _score_report(metrics, pyright_ok=pyright_ok, ruff_ok=ruff_ok)
    remediation_points = _remediation_points(metrics, pyright_ok=pyright_ok, ruff_ok=ruff_ok)
    return PackageReport(
        package=package_dir.name,
        role=str(package_meta.get("role", "")),
        status=str(package_meta.get("status", "")),
        backend_names=tuple(str(name) for name in package_meta.get("backend_names", []) if isinstance(name, str)),
        source_roots=tuple(str(path.relative_to(ROOT)) for path in source_roots),
        python_files=int(metrics["python_files"]),
        test_files=_test_file_count(package_dir),
        loc=int(metrics["loc"]),
        modules_with_future_annotations=int(metrics["modules_with_future_annotations"]),
        modules_missing_future_annotations=int(metrics["modules_missing_future_annotations"]),
        functions_total=int(metrics["functions_total"]),
        functions_fully_annotated=int(metrics["functions_fully_annotated"]),
        any_count=int(metrics["any_count"]),
        cast_count=int(metrics["cast_count"]),
        type_ignore_count=int(metrics["type_ignore_count"]),
        pyright_ignore_count=int(metrics["pyright_ignore_count"]),
        noqa_count=int(metrics["noqa_count"]),
        quoted_annotation_count=int(metrics["quoted_annotation_count"]),
        bare_except_count=int(metrics["bare_except_count"]),
        tests_present=_test_file_count(package_dir) > 0,
        pyright_ok=pyright_ok,
        pyright_returncode=pyright_returncode,
        ruff_ok=ruff_ok,
        ruff_returncode=ruff_returncode,
        remediation_points=remediation_points,
        score=score,
        grade=grade,
    )


def _format_percent(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "n/a"
    return f"{(100.0 * numerator / denominator):5.1f}%"


def _check_mark(ok: bool | None) -> str:
    if ok is None:
        return "-"
    return "ok" if ok else "fail"


def _print_table(reports: list[PackageReport]) -> None:
    header = (
        "package".ljust(30)
        + " score"
        + " grade"
        + " files"
        + " tests"
        + " typed_fn"
        + " future"
        + " any"
        + " cast"
        + " ign"
        + " pyi"
        + " qann"
        + " ruff"
        + " pyright"
    )
    print(header)
    print("-" * len(header))
    for report in reports:
        typed_percent = _format_percent(report.functions_fully_annotated, report.functions_total)
        future_percent = _format_percent(report.modules_with_future_annotations, report.python_files)
        row = (
            report.package.ljust(30)
            + f"{report.score:6d}"
            + f"{report.grade:>6}"
            + f"{report.python_files:6d}"
            + f"{report.test_files:6d}"
            + f"{typed_percent:>9}"
            + f"{future_percent:>8}"
            + f"{report.any_count:5d}"
            + f"{report.cast_count:6d}"
            + f"{report.type_ignore_count:5d}"
            + f"{report.pyright_ignore_count:5d}"
            + f"{report.quoted_annotation_count:6d}"
            + f"{_check_mark(report.ruff_ok):>6}"
            + f"{_check_mark(report.pyright_ok):>9}"
        )
        print(row)


def _print_scoreboards(reports: list[PackageReport], *, top: int) -> None:
    healthiest = sorted(reports, key=lambda item: (-item.score, item.remediation_points, item.package))[:top]
    smelliest = sorted(reports, key=lambda item: (item.score, -item.remediation_points, item.package))[:top]
    easy_win_pool = [report for report in reports if report.score < 90]
    easy_wins = sorted(
        easy_win_pool,
        key=lambda item: (item.remediation_points, item.score, item.python_files, item.package),
    )[:top]

    def _section(title: str, rows: list[PackageReport]) -> None:
        print(title)
        for index, report in enumerate(rows, start=1):
            typed_percent = _format_percent(report.functions_fully_annotated, report.functions_total)
            future_percent = _format_percent(report.modules_with_future_annotations, report.python_files)
            print(
                f"  {index}. {report.package} "
                f"(score={report.score}, grade={report.grade}, remediation={report.remediation_points}, "
                f"files={report.python_files}, typed_fn={typed_percent}, future={future_percent}, "
                f"Any={report.any_count}, cast={report.cast_count}, ignore={report.type_ignore_count + report.pyright_ignore_count})"
            )
        print()

    _section("Best packages", healthiest)
    _section("Worst packages", smelliest)
    _section("Easy wins", easy_wins)


def main() -> int:
    args = _parse_args()
    package_dirs = _discover_package_dirs(args.package)
    reports = [
        _build_report(package_dir, run_pyright=args.pyright, run_ruff=args.ruff)
        for package_dir in package_dirs
    ]
    reports.sort(key=lambda item: (-item.score, item.package))
    if args.json:
        print(json.dumps([asdict(report) for report in reports], indent=2, sort_keys=True))
    else:
        _print_scoreboards(reports, top=max(1, args.top))
        _print_table(reports)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
