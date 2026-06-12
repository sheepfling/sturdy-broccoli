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


def main() -> int:
    violations: list[LinkViolation] = []
    for path in _iter_markdown_files():
        violations.extend(_find_broken_links(path))
    if not violations:
        print("doc links: ok")
        return 0
    print("doc links: broken")
    for violation in violations:
        print(violation.render())
    print(f"total broken links: {len(violations)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
