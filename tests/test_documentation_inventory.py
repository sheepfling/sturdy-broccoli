from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_docs_family_indexes_cover_retained_subtrees() -> None:
    docs_readme = _read(ROOT / "docs" / "README.md")
    hierarchy = _read(ROOT / "docs" / "documentation_hierarchy.md")
    evidence_readme = _read(ROOT / "docs" / "evidence" / "README.md")
    plans_readme = _read(ROOT / "docs" / "plans" / "README.md")

    assert "compliance/README.md" in docs_readme
    assert "compliance/README.md" in hierarchy

    for rel in (
        "cpp-intake/README.md",
        "java-intake/README.md",
        "shim_routes/README.md",
    ):
        assert rel in evidence_readme

    for rel in (
        "spec2025_finish_line.md",
        "spec2025_finish_line_snapshot.json",
        "spec2025_route_parity_matrix.md",
        "2025_python_rti_backend_audit.md",
        "2025_requirement_by_requirement_audit.md",
    ):
        assert rel in plans_readme


def test_retained_doc_subtrees_have_local_readme_front_doors() -> None:
    required = (
        ROOT / "docs" / "compliance" / "README.md",
        ROOT / "docs" / "evidence" / "cpp-intake" / "README.md",
        ROOT / "docs" / "evidence" / "java-intake" / "README.md",
        ROOT / "docs" / "evidence" / "shim_routes" / "README.md",
        ROOT / "docs" / "evidence" / "shim_routes" / "route_traces" / "README.md",
    )
    for path in required:
        assert path.exists(), path.relative_to(ROOT).as_posix()


def test_packages_readme_describes_package_local_docs_and_migration_pattern() -> None:
    text = _read(ROOT / "packages" / "README.md")
    assert "packages/<name>/README.md" in text
    assert "packages/<name>/docs/README.md" in text
    assert "packages/<name>/MIGRATION.md" in text
    assert "packages/hla-backend-certi/docs/README.md" in text
    assert "packages/hla-vendor-pitch/docs/README.md" in text
    assert "packages/hla-vendor-portico/docs/README.md" in text
    assert "packages/hla-verification/docs/README.md" in text
