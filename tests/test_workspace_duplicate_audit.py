from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
MODULE_PATH = SCRIPTS_DIR / "detect_workspace_duplicates.py"
MODULE_SPEC = importlib.util.spec_from_file_location("detect_workspace_duplicates", MODULE_PATH)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
detect_workspace_duplicates = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = detect_workspace_duplicates
MODULE_SPEC.loader.exec_module(detect_workspace_duplicates)

build_duplicate_audit = detect_workspace_duplicates.build_duplicate_audit
build_duplicate_worklist = detect_workspace_duplicates.build_duplicate_worklist
clean_same_content_source_duplicates = detect_workspace_duplicates.clean_same_content_source_duplicates
strict_duplicate_candidates = detect_workspace_duplicates.strict_duplicate_candidates
write_duplicate_audit = detect_workspace_duplicates.write_duplicate_audit
write_duplicate_worklist = detect_workspace_duplicates.write_duplicate_worklist


def test_build_duplicate_audit_classifies_same_diff_and_orphan(tmp_path: Path) -> None:
    (tmp_path / "notes.md").write_text("hello\n", encoding="utf-8")
    (tmp_path / "notes 2.md").write_text("hello\n", encoding="utf-8")
    (tmp_path / "spec.py").write_text("one\n", encoding="utf-8")
    (tmp_path / "spec 3.py").write_text("two\n", encoding="utf-8")
    (tmp_path / "lonely 2.txt").write_text("missing canonical\n", encoding="utf-8")

    report = build_duplicate_audit(tmp_path)

    assert report.duplicate_count == 3
    assert report.same_content_count == 1
    assert report.different_content_count == 1
    assert report.orphan_count == 1
    by_path = {row.path: row for row in report.duplicates}
    assert by_path["notes 2.md"].status == "same-content-copy"
    assert by_path["spec 3.py"].status == "different-content-copy"
    assert by_path["lonely 2.txt"].status == "orphaned-copy"
    assert by_path["notes 2.md"].area == "<root>"
    assert by_path["notes 2.md"].scope == "support"
    assert by_path["notes 2.md"].canonical_tracked is False
    assert by_path["notes 2.md"].duplicate_tracked is False
    assert by_path["notes 2.md"].delete_confidence == "likely-delete"


def test_write_duplicate_audit_emits_json_and_markdown(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "demo.py").write_text("print('x')\n", encoding="utf-8")
    (workspace / "demo 2.py").write_text("print('x')\n", encoding="utf-8")

    json_path, md_path, report = write_duplicate_audit(tmp_path / "artifacts", root=workspace)

    assert report.duplicate_count == 1
    assert json_path.exists()
    assert md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["duplicate_count"] == 1
    markdown = md_path.read_text(encoding="utf-8")
    assert "Workspace Duplicate Audit" in markdown
    assert "demo 2.py" in markdown


def test_build_duplicate_worklist_groups_source_and_generated_findings(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("same\n", encoding="utf-8")
    (tmp_path / "docs" / "guide 2.md").write_text("same\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "tool.py").write_text("left\n", encoding="utf-8")
    (tmp_path / "scripts" / "tool 2.py").write_text("right\n", encoding="utf-8")
    (tmp_path / "analysis").mkdir()
    (tmp_path / "analysis" / "plot.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "analysis" / "plot 2.json").write_text("{\"x\":1}\n", encoding="utf-8")

    report = build_duplicate_audit(tmp_path)
    worklist = build_duplicate_worklist(report)

    assert [row.path for row in worklist.safe_same_content_source_deletes] == ["docs/guide 2.md"]
    assert worklist.safe_generated_deletes == ()
    assert [row.path for row in worklist.manual_review_source_differences] == ["scripts/tool 2.py"]
    assert worklist.source_orphans == ()
    assert [row.path for row in worklist.generated_duplicates] == ["analysis/plot 2.json"]
    assert worklist.uncategorized_duplicates == ()


def test_build_duplicate_audit_uses_git_tracking_to_raise_delete_confidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("left\n", encoding="utf-8")
    (tmp_path / "docs" / "guide 2.md").write_text("right\n", encoding="utf-8")

    monkeypatch.setattr("detect_workspace_duplicates._tracked_relpaths", lambda root: {"docs/guide.md"})

    report = build_duplicate_audit(tmp_path)
    row = next(item for item in report.duplicates if item.path == "docs/guide 2.md")

    assert row.canonical_tracked is True
    assert row.duplicate_tracked is False
    assert row.delete_confidence == "delete"


def test_build_duplicate_worklist_marks_artifacts_duplicates_as_safe_generated_deletes(tmp_path: Path) -> None:
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts" / "report.json").write_text("{\"ok\":1}\n", encoding="utf-8")
    (tmp_path / "artifacts" / "report 2.json").write_text("{\"broken\":1}\n", encoding="utf-8")
    (tmp_path / ".local").mkdir()
    (tmp_path / ".local" / "cache.bin").write_text("x\n", encoding="utf-8")
    (tmp_path / ".local" / "cache 2.bin").write_text("y\n", encoding="utf-8")

    report = build_duplicate_audit(tmp_path)
    worklist = build_duplicate_worklist(report)

    assert [row.path for row in worklist.safe_generated_deletes] == ["artifacts/report 2.json"]
    assert sorted(row.path for row in worklist.generated_duplicates) == [
        ".local/cache 2.bin",
        "artifacts/report 2.json",
    ]
    assert strict_duplicate_candidates(report) == ()
    generated_row = next(item for item in report.duplicates if item.path == "artifacts/report 2.json")
    assert generated_row.delete_confidence == "delete"


def test_write_duplicate_worklist_emits_json_and_markdown(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "docs").mkdir(parents=True)
    (workspace / "docs" / "demo.md").write_text("x\n", encoding="utf-8")
    (workspace / "docs" / "demo 2.md").write_text("x\n", encoding="utf-8")

    json_path, md_path, worklist = write_duplicate_worklist(tmp_path / "artifacts", root=workspace)

    assert len(worklist.safe_same_content_source_deletes) == 1
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(payload["safe_same_content_source_deletes"]) == 1
    markdown = md_path.read_text(encoding="utf-8")
    assert "Workspace Duplicate Cleanup Worklist" in markdown
    assert "Safe Same-Content Source Deletes" in markdown


def test_clean_same_content_source_duplicates_dry_run_preserves_files(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("same\n", encoding="utf-8")
    duplicate = tmp_path / "docs" / "guide 2.md"
    duplicate.write_text("same\n", encoding="utf-8")

    removed, remaining = clean_same_content_source_duplicates(root=tmp_path, output_dir=tmp_path / "artifacts", dry_run=True)

    assert removed == ("docs/guide 2.md",)
    assert duplicate.exists()
    assert remaining.safe_same_content_source_deletes == (
        build_duplicate_worklist(build_duplicate_audit(tmp_path)).safe_same_content_source_deletes
    )


def test_clean_same_content_source_duplicates_removes_only_safe_source_duplicates(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("same\n", encoding="utf-8")
    duplicate = tmp_path / "docs" / "guide 2.md"
    duplicate.write_text("same\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "tool.py").write_text("left\n", encoding="utf-8")
    different = tmp_path / "scripts" / "tool 2.py"
    different.write_text("right\n", encoding="utf-8")

    removed, remaining = clean_same_content_source_duplicates(root=tmp_path, output_dir=tmp_path / "artifacts")

    assert removed == ("docs/guide 2.md",)
    assert not duplicate.exists()
    assert different.exists()
    assert [row.path for row in remaining.manual_review_source_differences] == ["scripts/tool 2.py"]


def test_clean_same_content_source_duplicates_removes_safe_generated_artifact_duplicates(tmp_path: Path) -> None:
    (tmp_path / "artifacts").mkdir()
    original = tmp_path / "artifacts" / "report.json"
    duplicate = tmp_path / "artifacts" / "report 2.json"
    original.write_text("{}\n", encoding="utf-8")
    duplicate.write_text("{\"dirty\": true}\n", encoding="utf-8")

    removed, remaining = clean_same_content_source_duplicates(root=tmp_path, output_dir=tmp_path / "duplicate_audit")

    assert removed == ("artifacts/report 2.json",)
    assert not duplicate.exists()
    assert original.exists()
    assert remaining.generated_duplicates == ()


def test_build_duplicate_audit_ignores_transient_disappearing_duplicate_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    duplicate = tmp_path / "demo 2.py"
    (tmp_path / "demo.py").write_text("print('x')\n", encoding="utf-8")
    duplicate.write_text("print('x')\n", encoding="utf-8")

    original_stat = Path.stat

    def flaky_stat(self: Path, *args, **kwargs):  # type: ignore[no-untyped-def]
        if self == duplicate:
            raise FileNotFoundError(self)
        return original_stat(self, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", flaky_stat)

    report = build_duplicate_audit(tmp_path)

    assert report.duplicate_count == 0
