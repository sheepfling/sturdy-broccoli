#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "duplicate_audit"
COPY_SUFFIX_RE = re.compile(r"^(?P<base>.+?) (?P<copy>\d+)(?P<ext>(?:\.[^.]+)*)$")
SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    "node_modules",
}
SOURCE_ROOT_NAMES = {
    "docs",
    "examples",
    "packages",
    "requirements",
    "scripts",
    "testing",
    "tests",
    "tools",
    "third_party",
}
GENERATED_ROOT_NAMES = {
    ".local",
    "analysis",
    "artifacts",
}
AUTO_CLEAN_GENERATED_ROOT_NAMES = {
    "artifacts",
}


@dataclass(frozen=True, slots=True)
class DuplicateCandidate:
    path: str
    canonical_path: str
    copy_index: int
    canonical_exists: bool
    same_content_as_canonical: bool | None
    bytes: int
    canonical_bytes: int | None
    status: str
    area: str
    scope: str
    canonical_tracked: bool
    duplicate_tracked: bool
    delete_confidence: str


@dataclass(frozen=True, slots=True)
class DuplicateAuditReport:
    root: str
    scanned_paths: int
    duplicate_count: int
    same_content_count: int
    different_content_count: int
    orphan_count: int
    duplicates: tuple[DuplicateCandidate, ...]

    @property
    def has_findings(self) -> bool:
        return bool(self.duplicates)

    def to_json(self) -> str:
        return json.dumps(
            {
                "root": self.root,
                "scanned_paths": self.scanned_paths,
                "duplicate_count": self.duplicate_count,
                "same_content_count": self.same_content_count,
                "different_content_count": self.different_content_count,
                "orphan_count": self.orphan_count,
                "duplicates": [asdict(row) for row in self.duplicates],
            },
            indent=2,
            sort_keys=True,
        )


@dataclass(frozen=True, slots=True)
class DuplicateWorklist:
    root: str
    safe_same_content_source_deletes: tuple[DuplicateCandidate, ...]
    safe_generated_deletes: tuple[DuplicateCandidate, ...]
    manual_review_source_differences: tuple[DuplicateCandidate, ...]
    source_orphans: tuple[DuplicateCandidate, ...]
    generated_duplicates: tuple[DuplicateCandidate, ...]
    uncategorized_duplicates: tuple[DuplicateCandidate, ...]

    def to_json(self) -> str:
        return json.dumps(
            {
                "root": self.root,
                "safe_same_content_source_deletes": [asdict(row) for row in self.safe_same_content_source_deletes],
                "safe_generated_deletes": [asdict(row) for row in self.safe_generated_deletes],
                "manual_review_source_differences": [asdict(row) for row in self.manual_review_source_differences],
                "source_orphans": [asdict(row) for row in self.source_orphans],
                "generated_duplicates": [asdict(row) for row in self.generated_duplicates],
                "uncategorized_duplicates": [asdict(row) for row in self.uncategorized_duplicates],
            },
            indent=2,
            sort_keys=True,
        )


def default_audit_root() -> Path:
    configured = os.environ.get("HLA2010_DUPLICATE_AUDIT_ROOT")
    if configured:
        return Path(configured).resolve()
    return ROOT.resolve()


def strict_duplicate_candidates(report: DuplicateAuditReport) -> tuple[DuplicateCandidate, ...]:
    return tuple(row for row in report.duplicates if row.scope != "generated")


def _tracked_relpaths(root: Path) -> set[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            capture_output=True,
            text=False,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {
        entry.decode("utf-8", errors="replace")
        for entry in completed.stdout.split(b"\x00")
        if entry
    }


def _is_candidate_name(name: str) -> re.Match[str] | None:
    return COPY_SUFFIX_RE.match(name)


def _canonical_path_for(path: Path) -> tuple[Path, int] | None:
    match = _is_candidate_name(path.name)
    if match is None:
        return None
    base = match.group("base")
    ext = match.group("ext")
    copy_index = int(match.group("copy"))
    return path.with_name(f"{base}{ext}"), copy_index


def _classify_scope(path: Path, root: Path) -> tuple[str, str]:
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    root_area = root.name
    if root_area in SOURCE_ROOT_NAMES:
        return (root_area, "source")
    if root_area in GENERATED_ROOT_NAMES:
        return (root_area, "generated")
    parts = rel.parts
    if not parts:
        return ("<root>", "support")
    if len(parts) == 1:
        return ("<root>", "support")
    area = parts[0]
    if area in SOURCE_ROOT_NAMES:
        return (area, "source")
    if area in GENERATED_ROOT_NAMES:
        return (area, "generated")
    return (area, "support")


def _iter_repo_files(root: Path) -> Iterable[Path]:
    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = [
            name
            for name in dir_names
            if name not in SKIP_DIR_NAMES
        ]
        current = Path(current_root)
        for file_name in file_names:
            path = current / file_name
            try:
                exists = path.exists()
            except FileNotFoundError:
                continue
            if not exists:
                continue
            yield path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_duplicate_audit(root: Path | None = None) -> DuplicateAuditReport:
    audit_root = (root or default_audit_root()).resolve()
    duplicates: list[DuplicateCandidate] = []
    scanned_paths = 0
    tracked_relpaths = _tracked_relpaths(audit_root)

    for path in sorted(_iter_repo_files(audit_root)):
        try:
            scanned_paths += 1
            resolved = _canonical_path_for(path)
            if resolved is None:
                continue
            canonical_path, copy_index = resolved
            bytes_size = path.stat().st_size
            canonical_exists = canonical_path.exists()
            same_content_as_canonical: bool | None = None
            canonical_bytes: int | None = None
            status = "orphaned-copy"
            if canonical_exists:
                try:
                    canonical_bytes = canonical_path.stat().st_size
                    same_content_as_canonical = _sha256(path) == _sha256(canonical_path)
                except FileNotFoundError:
                    canonical_exists = False
                    canonical_bytes = None
                    same_content_as_canonical = None
                status = "same-content-copy" if same_content_as_canonical else "different-content-copy"
            if not canonical_exists:
                status = "orphaned-copy"
            row_area, row_scope = _classify_scope(path, audit_root)
            rel_path = str(path.relative_to(audit_root))
            canonical_rel_path = str(canonical_path.relative_to(audit_root))
            duplicate_tracked = rel_path in tracked_relpaths
            canonical_tracked = canonical_rel_path in tracked_relpaths
            delete_confidence = "manual-review"
            if status == "orphaned-copy":
                delete_confidence = "manual-review"
            elif canonical_tracked and not duplicate_tracked:
                delete_confidence = "delete"
            elif row_scope == "generated":
                delete_confidence = "delete"
            elif status == "same-content-copy":
                delete_confidence = "likely-delete"
            duplicates.append(
                DuplicateCandidate(
                    path=rel_path,
                    canonical_path=canonical_rel_path,
                    copy_index=copy_index,
                    canonical_exists=canonical_exists,
                    same_content_as_canonical=same_content_as_canonical,
                    bytes=bytes_size,
                    canonical_bytes=canonical_bytes,
                    status=status,
                    area=row_area,
                    scope=row_scope,
                    canonical_tracked=canonical_tracked,
                    duplicate_tracked=duplicate_tracked,
                    delete_confidence=delete_confidence,
                )
            )
        except FileNotFoundError:
            continue

    same_content_count = sum(1 for row in duplicates if row.status == "same-content-copy")
    different_content_count = sum(1 for row in duplicates if row.status == "different-content-copy")
    orphan_count = sum(1 for row in duplicates if row.status == "orphaned-copy")
    return DuplicateAuditReport(
        root=str(audit_root),
        scanned_paths=scanned_paths,
        duplicate_count=len(duplicates),
        same_content_count=same_content_count,
        different_content_count=different_content_count,
        orphan_count=orphan_count,
        duplicates=tuple(duplicates),
    )


def build_duplicate_worklist(report: DuplicateAuditReport) -> DuplicateWorklist:
    safe_same_content_source_deletes = tuple(
        row for row in report.duplicates if row.scope == "source" and row.status == "same-content-copy"
    )
    safe_generated_deletes = tuple(
        row for row in report.duplicates if row.scope == "generated" and row.area in AUTO_CLEAN_GENERATED_ROOT_NAMES
    )
    manual_review_source_differences = tuple(
        row for row in report.duplicates if row.scope == "source" and row.status == "different-content-copy"
    )
    source_orphans = tuple(
        row for row in report.duplicates if row.scope == "source" and row.status == "orphaned-copy"
    )
    generated_duplicates = tuple(row for row in report.duplicates if row.scope == "generated")
    uncategorized_duplicates = tuple(row for row in report.duplicates if row.scope == "support")
    return DuplicateWorklist(
        root=report.root,
        safe_same_content_source_deletes=safe_same_content_source_deletes,
        safe_generated_deletes=safe_generated_deletes,
        manual_review_source_differences=manual_review_source_differences,
        source_orphans=source_orphans,
        generated_duplicates=generated_duplicates,
        uncategorized_duplicates=uncategorized_duplicates,
    )


def render_markdown(report: DuplicateAuditReport) -> str:
    lines = [
        "# Workspace Duplicate Audit",
        "",
        f"- root: `{report.root}`",
        f"- scanned paths: `{report.scanned_paths}`",
        f"- duplicate candidates: `{report.duplicate_count}`",
        f"- same-content copies: `{report.same_content_count}`",
        f"- different-content copies: `{report.different_content_count}`",
        f"- orphaned copies: `{report.orphan_count}`",
        "",
        "| Duplicate | Canonical | Area | Scope | Canonical Tracked | Duplicate Tracked | Delete Confidence | Copy # | Status | Bytes | Canonical Bytes |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | --- | ---: | ---: |",
    ]
    for row in report.duplicates:
        lines.append(
            "| "
            + " | ".join(
                (
                    row.path,
                    row.canonical_path,
                    row.area,
                    row.scope,
                    "yes" if row.canonical_tracked else "no",
                    "yes" if row.duplicate_tracked else "no",
                    row.delete_confidence,
                    str(row.copy_index),
                    row.status,
                    str(row.bytes),
                    "" if row.canonical_bytes is None else str(row.canonical_bytes),
                )
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def render_worklist_markdown(worklist: DuplicateWorklist) -> str:
    lines = [
        "# Workspace Duplicate Cleanup Worklist",
        "",
        f"- root: `{worklist.root}`",
        f"- safe same-content source deletes: `{len(worklist.safe_same_content_source_deletes)}`",
        f"- safe generated deletes: `{len(worklist.safe_generated_deletes)}`",
        f"- manual review source differences: `{len(worklist.manual_review_source_differences)}`",
        f"- source orphans: `{len(worklist.source_orphans)}`",
        f"- generated-tree duplicates: `{len(worklist.generated_duplicates)}`",
        f"- support/uncategorized duplicates: `{len(worklist.uncategorized_duplicates)}`",
        "",
    ]
    sections: Sequence[tuple[str, tuple[DuplicateCandidate, ...]]] = (
        ("Safe Same-Content Source Deletes", worklist.safe_same_content_source_deletes),
        ("Safe Generated Deletes", worklist.safe_generated_deletes),
        ("Manual Review Source Differences", worklist.manual_review_source_differences),
        ("Source Orphans", worklist.source_orphans),
        ("Generated Duplicates", worklist.generated_duplicates),
        ("Support Or Uncategorized Duplicates", worklist.uncategorized_duplicates),
    )
    for title, rows in sections:
        lines.extend([f"## {title}", ""])
        if not rows:
            lines.extend(["None.", ""])
            continue
        for row in rows:
            lines.append(
                f"- `{row.path}` -> `{row.canonical_path}` "
                f"({row.status}, area={row.area}, scope={row.scope}, "
                f"canonical_tracked={row.canonical_tracked}, duplicate_tracked={row.duplicate_tracked}, "
                f"delete_confidence={row.delete_confidence})"
            )
        lines.append("")
    return "\n".join(lines)


def write_duplicate_audit(output_dir: Path | None = None, *, root: Path | None = None) -> tuple[Path, Path, DuplicateAuditReport]:
    report = build_duplicate_audit(root)
    destination = (output_dir or DEFAULT_OUTPUT_DIR).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / "workspace_duplicate_audit.json"
    md_path = destination / "workspace_duplicate_audit.md"
    json_path.write_text(report.to_json() + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path, report


def write_duplicate_worklist(
    output_dir: Path | None = None,
    *,
    root: Path | None = None,
) -> tuple[Path, Path, DuplicateWorklist]:
    report = build_duplicate_audit(root)
    worklist = build_duplicate_worklist(report)
    destination = (output_dir or DEFAULT_OUTPUT_DIR).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    json_path = destination / "workspace_duplicate_worklist.json"
    md_path = destination / "workspace_duplicate_worklist.md"
    json_path.write_text(worklist.to_json() + "\n", encoding="utf-8")
    md_path.write_text(render_worklist_markdown(worklist) + "\n", encoding="utf-8")
    return json_path, md_path, worklist


def print_worklist_summary(worklist: DuplicateWorklist) -> None:
    print(f"safe-same-content-source-deletes: {len(worklist.safe_same_content_source_deletes)}")
    print(f"safe-generated-deletes: {len(worklist.safe_generated_deletes)}")
    print(f"manual-review-source-differences: {len(worklist.manual_review_source_differences)}")
    print(f"source-orphans: {len(worklist.source_orphans)}")
    print(f"generated-duplicates: {len(worklist.generated_duplicates)}")
    print(f"support-duplicates: {len(worklist.uncategorized_duplicates)}")


def clean_same_content_source_duplicates(
    *,
    root: Path | None = None,
    output_dir: Path | None = None,
    dry_run: bool = False,
) -> tuple[tuple[str, ...], DuplicateWorklist]:
    report = build_duplicate_audit(root)
    worklist = build_duplicate_worklist(report)
    removed: list[str] = []
    audit_root = Path(worklist.root)
    for row in worklist.safe_same_content_source_deletes:
        removed.append(row.path)
        if dry_run:
            continue
        (audit_root / row.path).unlink(missing_ok=True)
    for row in worklist.safe_generated_deletes:
        removed.append(row.path)
        if dry_run:
            continue
        (audit_root / row.path).unlink(missing_ok=True)
    write_duplicate_audit(output_dir, root=audit_root)
    write_duplicate_worklist(output_dir, root=audit_root)
    refreshed = build_duplicate_worklist(build_duplicate_audit(audit_root))
    return tuple(removed), refreshed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detect iCloud-style duplicate workspace files such as '* 2.ext' or '* 3.ext'.")
    parser.add_argument(
        "command",
        nargs="?",
        default="check",
        choices=("check", "worklist", "clean-same-content"),
        help="`check` writes the raw audit and exits nonzero on findings. `worklist` writes grouped cleanup worklists. `clean-same-content` removes only hash-identical source-tree copies.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=default_audit_root(),
        help="Workspace root to scan. Defaults to the repository root.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Artifact directory for JSON and markdown audit outputs.",
    )
    parser.add_argument(
        "--allow-findings",
        action="store_true",
        help="Exit 0 even when duplicate candidates are found.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview cleanup actions without deleting files.",
    )
    args = parser.parse_args(argv)

    if args.command == "clean-same-content":
        removed, remaining = clean_same_content_source_duplicates(
            output_dir=args.output_dir,
            root=args.root,
            dry_run=args.dry_run,
        )
        print((args.output_dir.resolve() / "workspace_duplicate_audit.json"))
        print((args.output_dir.resolve() / "workspace_duplicate_worklist.json"))
        print(f"removed-safe-source-copies: {len(removed)}")
        action_label = "would-remove" if args.dry_run else "removed"
        for path in removed:
            print(f"{action_label}: {path}")
        print_worklist_summary(remaining)
        return 0

    if args.command == "worklist":
        json_path, md_path, worklist = write_duplicate_worklist(args.output_dir, root=args.root)
        print(json_path)
        print(md_path)
        print_worklist_summary(worklist)
        has_findings = any(
            (
                worklist.safe_same_content_source_deletes,
                worklist.safe_generated_deletes,
                worklist.manual_review_source_differences,
                worklist.source_orphans,
                worklist.uncategorized_duplicates,
            )
        )
        if has_findings and not args.allow_findings:
            return 1
        return 0

    json_path, md_path, report = write_duplicate_audit(args.output_dir, root=args.root)
    print(json_path)
    print(md_path)
    print(f"scanned-paths: {report.scanned_paths}")
    print(f"duplicate-candidates: {report.duplicate_count}")
    print(f"same-content-copies: {report.same_content_count}")
    print(f"different-content-copies: {report.different_content_count}")
    print(f"orphaned-copies: {report.orphan_count}")
    if strict_duplicate_candidates(report) and not args.allow_findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
