from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEY_PUBLIC_DOCS = (
    ROOT / "README.md",
    ROOT / "docs/README.md",
    ROOT / "docs/onboarding.md",
    ROOT / "docs/first_run.md",
    ROOT / "docs/python_environment.md",
    ROOT / "docs/two_federate_quickstart.md",
    ROOT / "packages/README.md",
    ROOT / "tests/README.md",
)
BANNED_PRIMARY_REFS = (
    "docs/evidence/",
    "docs/reference/archive_index.md",
)
EXPECTED_HEADINGS = {
    ROOT / "README.md": ("## Start Here", "## Read Next"),
    ROOT / "docs/README.md": ("## Start Here", "## Historical / Provenance", "## Read Next"),
    ROOT / "docs/onboarding.md": ("## What This Path Assumes", "## What This Path Avoids", "## Read Next"),
    ROOT / "docs/first_run.md": ("## Read Next",),
    ROOT / "docs/python_environment.md": ("## Read Next",),
    ROOT / "docs/two_federate_quickstart.md": ("## Read Next",),
    ROOT / "packages/README.md": ("## Start Here", "## Read Next"),
    ROOT / "tests/README.md": ("## Start Here", "## Read Next"),
}
EXPECTED_PATHS = {
    ROOT / "README.md": (
        ROOT / "tools/bootstrap",
        ROOT / "examples/target_radar_simulation.py",
        ROOT / "examples/backend_recording.py",
        ROOT / "tools/test",
    ),
    ROOT / "docs/onboarding.md": (
        ROOT / "docs/first_run.md",
        ROOT / "docs/python_rti_backend.md",
        ROOT / "docs/create_federate_and_fom.md",
        ROOT / "docs/requirements_traceability.md",
        ROOT / "docs/java_backends_quickstart.md",
        ROOT / "docs/verification/run_sequence.md",
    ),
    ROOT / "docs/first_run.md": (
        ROOT / "tools/bootstrap",
        ROOT / "examples/backend_recording.py",
        ROOT / "examples/target_radar_simulation.py",
    ),
    ROOT / "docs/python_environment.md": (
        ROOT / "tools/bootstrap",
        ROOT / "examples/target_radar_simulation.py",
        ROOT / "tools/two-federate",
        ROOT / "tools/test",
        ROOT / "tools/python",
        ROOT / "tools/certi-easy",
        ROOT / "tools/pitch",
    ),
    ROOT / "docs/two_federate_quickstart.md": (
        ROOT / "tools/two-federate",
        ROOT / "scripts/run_two_federate_suite.py",
        ROOT / "src/hla2010_repo_internal/verification/two_federate_suite_runner.py",
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
        text = _read(path)
        for heading in headings:
            assert heading in text, f"{path.relative_to(ROOT)} missing {heading}"


def test_key_public_docs_do_not_link_to_historical_material_in_primary_sections() -> None:
    for path in KEY_PUBLIC_DOCS:
        text = _read(path)
        historical_index = text.find("## Historical / Provenance")
        primary_text = text if historical_index == -1 else text[:historical_index]
        for banned in BANNED_PRIMARY_REFS:
            assert banned not in primary_text, f"{path.relative_to(ROOT)} promotes {banned} before the historical section"


def test_key_newcomer_docs_reference_existing_paths() -> None:
    for path, expected_paths in EXPECTED_PATHS.items():
        text = _read(path)
        for expected_path in expected_paths:
            repo_rel = expected_path.relative_to(ROOT).as_posix()
            doc_rel = expected_path.relative_to(ROOT).as_posix()
            if path.parent != ROOT:
                doc_rel = expected_path.relative_to(ROOT).as_posix()
                doc_rel = Path(
                    os.path.relpath(expected_path, start=path.parent)
                ).as_posix()
            assert repo_rel in text or doc_rel in text, (
                f"{path.relative_to(ROOT)} no longer references {repo_rel} "
                f"or {doc_rel}"
            )
            assert expected_path.exists(), repo_rel


def test_onboarding_doc_is_the_canonical_opinionated_map() -> None:
    text = _read(ROOT / "docs" / "onboarding.md")
    assert "1. [First Run](first_run.md)" in text
    assert "2. [Python RTI Backend](python_rti_backend.md)" in text
    assert "3. [Create A Federate And FOM](create_federate_and_fom.md)" in text
    assert "4. [Requirements Traceability](requirements_traceability.md)" in text
    assert "5. [Java Backends Later](java_backends_quickstart.md)" in text
    assert "6. [Full Verification](verification/run_sequence.md)" in text
    assert "docs/evidence/" not in text
    assert "reference/archive_index.md" not in text


def test_repo_does_not_keep_duplicate_markdown_copies() -> None:
    duplicates = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob("**/* 2.md")
        if path.is_file()
    )
    assert duplicates == [], f"duplicate markdown copies remain: {duplicates}"


def test_python_api_spec_matches_split_package_reality() -> None:
    path = ROOT / "docs/python_api_spec.md"
    text = _read(path)
    assert "installable root: `hla2010-spec`" in text
    assert "spec source root: `packages/hla2010-spec/src/hla2010/`" in text
    assert "package-owned implementations: `packages/*/src/...`" in text
    assert "temporary compatibility routing" in text
    assert "temporary backend-discovery and ambassador-factory compatibility facade" in text
    assert "../packages/hla2010-spec/src/hla2010/spec/__init__.py" in text
    assert "../packages/hla2010-spec/README.md" in text
    assert "../hla2010/spec/" not in text
    assert "hla2010.testing" not in text


def test_repo_overview_docs_describe_root_namespace_as_core_plus_temporary_facades() -> None:
    readme = _read(ROOT / "README.md")
    packages_readme = _read(ROOT / "packages" / "README.md")

    assert "`packages/hla2010-spec/src/hla2010/` is the package-owned root Python package for the abstract/core API plus the documented temporary compatibility facade `hla2010.rti`" in readme
    assert "`hla2010/` is a narrow top-level shim area for plugin-facing glue" not in readme
    assert "`packages/hla2010-spec/src/hla2010/` tree is the package-owned spec source root used for stable imports, abstract\ncore API ownership, and only documented temporary compatibility routing." in packages_readme
