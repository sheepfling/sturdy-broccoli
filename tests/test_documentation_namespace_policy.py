from __future__ import annotations

from tests.doc_test_helpers import ROOT, assert_absent_all, assert_contains_all, normalized_text, read


def test_python_rti_backend_doc_matches_registry_backed_dispatch_reality() -> None:
    text = read(ROOT / "docs" / "python_rti_backend.md")
    assert_contains_all(
        text,
        ("generated service registry", "PYTHON_RTI_SERVICE_REGISTRY", "`getattr(...)`"),
        path=ROOT / "docs" / "python_rti_backend.md",
    )


def test_repo_does_not_keep_duplicate_markdown_copies() -> None:
    duplicates = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob("**/* 2.md")
        if path.is_file()
    )
    assert duplicates == [], f"duplicate markdown copies remain: {duplicates}"


def test_python_api_spec_matches_split_package_reality() -> None:
    text = read(ROOT / "docs" / "python_api_spec.md")
    assert_contains_all(
        text,
        (
            "installable root: `hla2010-spec`",
            "spec source root: `packages/hla2010-spec/src/hla2010/`",
            "package-owned implementations: `packages/*/src/...`",
            "temporary compatibility routing",
            "temporary backend-discovery and ambassador-factory compatibility facade",
            "../packages/hla2010-spec/src/hla2010/spec/__init__.py",
            "../packages/hla2010-spec/README.md",
        ),
        path=ROOT / "docs" / "python_api_spec.md",
    )
    assert_absent_all(
        text,
        ("../hla2010/spec/", "hla2010.testing"),
        path=ROOT / "docs" / "python_api_spec.md",
    )


def test_repo_overview_docs_describe_root_namespace_as_core_plus_temporary_facades() -> None:
    readme = normalized_text(ROOT / "README.md")
    packages_readme = normalized_text(ROOT / "packages" / "README.md")

    assert_contains_all(
        readme,
        (
            "`packages/hla2010-spec/src/hla2010/`",
            "package-owned root Python package",
            "abstract/core API",
            "temporary compatibility facade",
            "`hla2010.rti`",
        ),
        path=ROOT / "README.md",
    )
    assert_absent_all(
        readme,
        ("`hla2010/` is a narrow top-level shim area for plugin-facing glue",),
        path=ROOT / "README.md",
    )
    assert_contains_all(
        packages_readme,
        (
            "`packages/hla2010-spec/src/hla2010/` tree",
            "package-owned spec source root",
            "stable imports",
            "abstract core API ownership",
            "temporary compatibility routing",
        ),
        path=ROOT / "packages/README.md",
    )
