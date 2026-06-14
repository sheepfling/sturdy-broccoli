from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import defaultdict, deque
from pathlib import Path

from tests.docs_policy_helpers import (
    BANNED_PRIMARY_REFS,
    EXPECTED_HEADINGS,
    EXPECTED_PATHS,
    KEY_PUBLIC_DOCS,
    doc_relative_reference,
)
from tests.doc_test_helpers import ROOT, read

AUTHORED_DOC_ROOTS = (
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "plans" / "README.md",
    ROOT / "docs" / "reference" / "README.md",
    ROOT / "docs" / "verification" / "README.md",
)
AUTHORED_DOC_EXCLUDED_PREFIXES = (
    "docs/evidence/",
)
DOC_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HOST_ABSOLUTE_PATH_RE = re.compile(r"/Users/|/private/tmp|/tmp/|/var/folders|/mnt/data|file://|[A-Za-z]:[\\/]")


def test_markdown_links_are_valid() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/ci/check_doc_links.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout or result.stderr


def test_markdown_links_checker_bootstraps_from_outside_repo(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "ci" / "check_doc_links.py")],
        cwd=tmp_path,
        env={"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", "")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout or result.stderr


def test_key_public_docs_keep_required_navigation_headings() -> None:
    for path, headings in EXPECTED_HEADINGS.items():
        text = read(path)
        for heading in headings:
            assert heading in text, f"{path.relative_to(ROOT)} missing {heading}"


def test_key_public_docs_do_not_link_to_historical_material_in_primary_sections() -> None:
    for path in KEY_PUBLIC_DOCS:
        text = read(path)
        historical_index = text.find("## Historical / Provenance")
        primary_text = text if historical_index == -1 else text[:historical_index]
        for banned in BANNED_PRIMARY_REFS:
            assert banned not in primary_text, f"{path.relative_to(ROOT)} promotes {banned} before the historical section"


def test_key_newcomer_docs_reference_existing_paths() -> None:
    for path, expected_paths in EXPECTED_PATHS.items():
        text = read(path)
        for expected_path in expected_paths:
            repo_rel, doc_rel = doc_relative_reference(path, expected_path)
            assert repo_rel in text or doc_rel in text, (
                f"{path.relative_to(ROOT)} no longer references {repo_rel} or {doc_rel}"
            )
            assert expected_path.exists(), repo_rel


def _authored_docs() -> list[Path]:
    return sorted(
        path
        for path in (ROOT / "docs").rglob("*.md")
        if not any(path.relative_to(ROOT).as_posix().startswith(prefix) for prefix in AUTHORED_DOC_EXCLUDED_PREFIXES)
    )


def test_authored_docs_do_not_contain_host_absolute_paths() -> None:
    violations: list[str] = []
    for path in _authored_docs():
        text = read(path)
        if HOST_ABSOLUTE_PATH_RE.search(text):
            violations.append(path.relative_to(ROOT).as_posix())
    assert not violations, "\n".join(violations)


def test_authored_docs_are_reachable_from_docs_family_entrypoints() -> None:
    docs = _authored_docs()
    normalized = {path.resolve(): path for path in docs}
    adjacency: dict[Path, set[Path]] = defaultdict(set)
    for path in docs:
        text = read(path)
        for match in DOC_LINK_RE.finditer(text):
            target = match.group(1).strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            candidate = (path.parent / target).resolve() if not target.startswith("/") else (ROOT / target.lstrip("/")).resolve()
            if candidate in normalized:
                adjacency[path.resolve()].add(candidate)

    reachable: set[Path] = set()
    queue = deque(path.resolve() for path in AUTHORED_DOC_ROOTS)
    while queue:
        current = queue.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        queue.extend(adjacency.get(current, ()))

    orphans = sorted(path.relative_to(ROOT).as_posix() for path in docs if path.resolve() not in reachable)
    assert not orphans, "\n".join(orphans)
