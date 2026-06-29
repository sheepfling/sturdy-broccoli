"""Audit helpers for overloaded Java API metadata."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hla.rti1516e.api_metadata import API_METADATA


@dataclass(frozen=True, slots=True)
class JavaOverloadAuditRow:
    interface: str
    method_name: str
    arity: int
    overload_count: int
    params: tuple[str, ...]
    same_arity_collision: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class JavaOverloadAuditReport:
    title: str
    total_overloaded_methods: int
    total_same_arity_collision_groups: int
    rows: tuple[JavaOverloadAuditRow, ...]

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "total_overloaded_methods": self.total_overloaded_methods,
                "total_same_arity_collision_groups": self.total_same_arity_collision_groups,
                "rows": [row.as_dict() for row in self.rows],
            },
            indent=2,
            sort_keys=True,
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _java_overload_rows() -> list[JavaOverloadAuditRow]:
    rows: list[JavaOverloadAuditRow] = []
    for interface in ("RTIambassador", "FederateAmbassador"):
        for method_name, overloads in API_METADATA.get(interface, {}).items():
            java_overloads = [overload for overload in overloads if overload.get("language") == "java"]
            if len(java_overloads) <= 1:
                continue
            by_arity: dict[int, list[str]] = {}
            for overload in java_overloads:
                params = str(overload.get("params", "")).strip()
                param_items = tuple(part.strip() for part in params.split(",") if part.strip())
                by_arity.setdefault(len(param_items), []).append(params)
            for arity, params in sorted(by_arity.items()):
                rows.append(
                    JavaOverloadAuditRow(
                        interface=interface,
                        method_name=method_name,
                        arity=arity,
                        overload_count=len(params),
                        params=tuple(params),
                        same_arity_collision=len(params) > 1,
                    )
                )
    rows.sort(key=lambda row: (row.interface, row.method_name, row.arity))
    return rows


def build_java_overload_audit(
    *,
    title: str = "Java Overload Audit",
) -> JavaOverloadAuditReport:
    rows = tuple(_java_overload_rows())
    overloaded_methods = {(row.interface, row.method_name) for row in rows}
    same_arity_groups = [row for row in rows if row.same_arity_collision]
    return JavaOverloadAuditReport(
        title=title,
        total_overloaded_methods=len(overloaded_methods),
        total_same_arity_collision_groups=len(same_arity_groups),
        rows=rows,
    )


def render_java_overload_audit_markdown(report: JavaOverloadAuditReport) -> str:
    lines = [
        f"# {report.title}",
        "",
        f"- Total overloaded Java methods: {report.total_overloaded_methods}",
        f"- Total same-arity collision groups: {report.total_same_arity_collision_groups}",
        "",
        "| Interface | Method | Arity | Overloads | Same-arity collision | Java parameter lists |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in report.rows:
        params = "<br>".join(f"`{value}`" if value else "`<empty>`" for value in row.params)
        lines.append(
            f"| `{row.interface}` | `{row.method_name}` | {row.arity} | {row.overload_count} | "
            f"{'yes' if row.same_arity_collision else 'no'} | {params} |"
        )
    return "\n".join(lines) + "\n"


def write_java_overload_audit(
    output_root: str | Path | None = None,
    *,
    title: str = "Java Overload Audit",
) -> tuple[Path, Path, JavaOverloadAuditReport]:
    root = Path(output_root) if output_root is not None else _repo_root() / "analysis" / "java_overload_audit"
    root.mkdir(parents=True, exist_ok=True)
    report = build_java_overload_audit(title=title)
    json_path = root / "java_overload_audit.json"
    md_path = root / "java_overload_audit.md"
    json_path.write_text(report.to_json() + "\n", encoding="utf-8")
    md_path.write_text(render_java_overload_audit_markdown(report), encoding="utf-8")
    return json_path, md_path, report


__all__ = [
    "JavaOverloadAuditReport",
    "JavaOverloadAuditRow",
    "build_java_overload_audit",
    "render_java_overload_audit_markdown",
    "write_java_overload_audit",
]
