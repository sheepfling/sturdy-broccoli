from __future__ import annotations

import json

from hla.verification.repo_internal.java_overload_audit import (
    build_java_overload_audit,
    write_java_overload_audit,
)


def test_build_java_overload_audit_captures_known_same_arity_groups() -> None:
    report = build_java_overload_audit()

    assert report.total_overloaded_methods == 27
    assert report.total_same_arity_collision_groups == 8

    rows = {(row.interface, row.method_name, row.arity): row for row in report.rows}
    assert rows[("RTIambassador", "createFederationExecution", 2)].same_arity_collision is True
    assert rows[("RTIambassador", "createFederationExecution", 3)].same_arity_collision is True
    assert rows[("RTIambassador", "joinFederationExecution", 3)].same_arity_collision is True
    assert rows[("RTIambassador", "requestAttributeValueUpdate", 3)].same_arity_collision is True
    assert rows[("RTIambassador", "connect", 2)].same_arity_collision is False


def test_write_java_overload_audit_writes_json_and_markdown(tmp_path) -> None:
    json_path, md_path, report = write_java_overload_audit(tmp_path / "java-audit")

    assert json_path.name == "java_overload_audit.json"
    assert md_path.name == "java_overload_audit.md"

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["title"] == report.title
    assert payload["total_same_arity_collision_groups"] == report.total_same_arity_collision_groups

    markdown = md_path.read_text(encoding="utf-8")
    assert "# Java Overload Audit" in markdown
    assert "`RTIambassador`" in markdown
    assert "`createFederationExecution`" in markdown
