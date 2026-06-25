#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = SCRIPT_REPO_ROOT
DOC_GLOBS = (
    "README.md",
    "compat/**/*.md",
    "docs/**/*.md",
    "packages/**/*.md",
    "tests/**/*.md",
    "scripts/**/*.md",
    "tools/**/*.md",
)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
IGNORED_SCHEMES = ("http://", "https://", "mailto:")
ABSOLUTE_TARGET_RE = re.compile(r"^(?:/|[A-Za-z]:[\\/]|file://)")
ALLOW_MISSING_ROOT_PREFIXES = (
    "analysis/",
    "archives/",
)
DOC_ORPHAN_ENTRYPOINTS = (
    "README.md",
    "docs/README.md",
    "docs/onboarding.md",
)
DOC_ORPHAN_EXCLUDED_PREFIXES = (
    "docs/compliance/",
    "docs/evidence/",
    "docs/migration/",
    "docs/openapi/",
    "docs/plans/",
    "docs/reference/",
    "docs/requirements/",
    "docs/specs/",
    "docs/verification/",
)
DOC_ORPHAN_ALLOWED_PATHS = (
    "docs/inbox_inventory_2026-06-05.md",
)


@dataclass(frozen=True)
class LinkViolation:
    source_path: Path
    line_number: int
    label: str
    target: str
    resolved_path: Path
    note: str

    def render(self) -> str:
        rel_source = self.source_path.relative_to(ROOT).as_posix()
        try:
            rel_resolved = self.resolved_path.relative_to(ROOT).as_posix()
        except ValueError:
            rel_resolved = str(self.resolved_path)
        return (
            f"{rel_source}:{self.line_number}: [{self.label}]({self.target}) -> "
            f"{rel_resolved} ({self.note})"
        )


@dataclass(frozen=True)
class OrphanViolation:
    path: Path
    note: str

    def render(self) -> str:
        rel_path = self.path.relative_to(ROOT).as_posix()
        return f"{rel_path} ({self.note})"


def _iter_markdown_files() -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for pattern in DOC_GLOBS:
        for path in ROOT.glob(pattern):
            resolved = path.resolve()
            if resolved in seen or not path.is_file():
                continue
            seen.add(resolved)
            files.append(path)
    return sorted(files)


def _is_ignored_target(target: str) -> bool:
    return target.startswith(IGNORED_SCHEMES) or target.startswith("#")


def _is_absolute_target(target: str) -> bool:
    return bool(ABSOLUTE_TARGET_RE.match(target))


def _allow_missing_resolved_path(path: Path) -> bool:
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        return False
    return any(rel.startswith(prefix) for prefix in ALLOW_MISSING_ROOT_PREFIXES)


def _link_note(source_path: Path, target: str, resolved_path: Path) -> str:
    rel_source = source_path.relative_to(ROOT).as_posix()
    if rel_source.startswith("docs/") and target.startswith(("docs/", "tests/", "scripts/", "packages/", "src/", "analysis/")):
        return "looks like a repo-root-relative assumption from inside docs/"
    if rel_source.startswith("docs/verification/") and target.startswith(("../tests/", "../scripts/", "../packages/", "../src/", "../analysis/")):
        return "likely missing one ../ from docs/verification/"
    return "missing target"


def _absolute_link_note(source_path: Path, target: str) -> str:
    rel_source = source_path.relative_to(ROOT).as_posix()
    if rel_source.startswith("docs/"):
        return "absolute links are not allowed in documentation"
    return "absolute link target is not allowed"


def _find_broken_links(path: Path) -> list[LinkViolation]:
    text = path.read_text(encoding="utf-8")
    violations: list[LinkViolation] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for label, raw_target in MARKDOWN_LINK_RE.findall(line):
            target = raw_target.strip()
            if _is_ignored_target(target):
                continue
            clean_target = target.split("#", 1)[0].strip()
            if not clean_target:
                continue
            if _is_absolute_target(clean_target):
                violations.append(
                    LinkViolation(
                        source_path=path,
                        line_number=line_number,
                        label=label,
                        target=target,
                        resolved_path=Path(clean_target),
                        note=_absolute_link_note(path, clean_target),
                    )
                )
                continue
            resolved_path = (path.parent / clean_target).resolve()
            if resolved_path.exists():
                continue
            if _allow_missing_resolved_path(resolved_path):
                continue
            violations.append(
                LinkViolation(
                    source_path=path,
                    line_number=line_number,
                    label=label,
                    target=target,
                    resolved_path=resolved_path,
                    note=_link_note(path, clean_target, resolved_path),
                )
            )
    return violations


def _iter_curated_doc_files() -> list[Path]:
    files = [ROOT / "README.md"]
    files.extend(ROOT.glob("docs/**/*.md"))
    return sorted({path.resolve(): path for path in files if path.is_file()}.values())


def _extract_markdown_doc_targets(path: Path, allowed_paths: set[Path]) -> set[Path]:
    text = path.read_text(encoding="utf-8")
    targets: set[Path] = set()
    for _label, raw_target in MARKDOWN_LINK_RE.findall(text):
        target = raw_target.strip()
        if _is_ignored_target(target):
            continue
        clean_target = target.split("#", 1)[0].strip()
        if not clean_target or _is_absolute_target(clean_target):
            continue
        resolved_path = (path.parent / clean_target).resolve()
        if resolved_path in allowed_paths:
            targets.add(resolved_path)
    return targets


def _is_excluded_curated_doc(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return rel in DOC_ORPHAN_ALLOWED_PATHS or any(rel.startswith(prefix) for prefix in DOC_ORPHAN_EXCLUDED_PREFIXES)


def _find_curated_doc_orphans() -> list[OrphanViolation]:
    doc_files = _iter_curated_doc_files()
    allowed_paths = {path.resolve() for path in doc_files}
    adjacency = {path.resolve(): _extract_markdown_doc_targets(path, allowed_paths) for path in doc_files}
    entrypoints = [(ROOT / rel).resolve() for rel in DOC_ORPHAN_ENTRYPOINTS if (ROOT / rel).is_file()]
    reachable: set[Path] = set()
    stack = list(entrypoints)
    while stack:
        current = stack.pop()
        if current in reachable:
            continue
        reachable.add(current)
        stack.extend(adjacency.get(current, ()))
    violations: list[OrphanViolation] = []
    for path in doc_files:
        resolved = path.resolve()
        if resolved in reachable or _is_excluded_curated_doc(path):
            continue
        violations.append(OrphanViolation(path=path, note="curated doc is not reachable from README.md/docs/README.md/onboarding.md"))
    return violations


def main() -> int:
    violations: list[LinkViolation] = []
    for path in _iter_markdown_files():
        violations.extend(_find_broken_links(path))
    orphan_violations = _find_curated_doc_orphans()
    if not violations and not orphan_violations:
        print("doc links: ok")
        return 0
    print("doc links: broken")
    for violation in violations:
        print(violation.render())
    for violation in orphan_violations:
        print(violation.render())
    print(f"total broken links: {len(violations)}")
    print(f"total curated doc orphans: {len(orphan_violations)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
