from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ICLOUD_DUPLICATE_SUFFIX = " 2.md"
SUFFIXED_DUPLICATE_FILE = re.compile(r" 2(?=\.[^.]+$)")
KEY_PUBLIC_DOCS = (
    ROOT / "README.md",
    ROOT / "docs/README.md",
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
    ROOT / "docs/vendor_runtime_runner_guide.md": (
        ROOT / "tools/java",
    ),
    ROOT / "docs/two_federate_quickstart.md": (
        ROOT / "tools/two-federate",
        ROOT / "scripts/run_two_federate_suite.py",
        ROOT / "packages/hla-verification/src/hla/verification/repo_internal/verification/two_federate_suite_runner.py",
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
            rel = expected_path.relative_to(ROOT).as_posix()
            assert rel in text, f"{path.relative_to(ROOT)} no longer references {rel}"
            assert expected_path.exists(), rel


def test_repo_does_not_keep_duplicate_markdown_copies() -> None:
    duplicates = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob("**/* 2.md")
        if path.is_file()
        and ".venv" not in path.parts
        and not path.name.endswith(ICLOUD_DUPLICATE_SUFFIX)
    )
    assert duplicates == [], f"duplicate markdown copies remain: {duplicates}"


def test_requirement_surfaces_do_not_keep_suffixed_duplicate_files() -> None:
    duplicates = sorted(
        path.relative_to(ROOT).as_posix()
        for base in (ROOT / "requirements", ROOT / "docs" / "requirements")
        for path in base.glob("**/*")
        if path.is_file() and SUFFIXED_DUPLICATE_FILE.search(path.name)
    )
    assert duplicates == [], f"duplicate requirement surface files remain: {duplicates}"


def test_top_level_requirements_tree_stays_as_an_edition_index() -> None:
    top_level_files = sorted(
        path.name
        for path in (ROOT / "requirements").iterdir()
        if path.is_file()
    )
    assert top_level_files == ["README.md", "hla_1516_master_harmonization_index_v1_0.csv"]

    text = _read(ROOT / "requirements" / "README.md")
    assert "hla_1516_master_harmonization_index_v1_0.csv" in text
    assert "generated or legacy projections" in text


def test_each_requirement_edition_has_a_single_source_side_inventory_front_door() -> None:
    inventory_markers = {
        ROOT / "requirements" / "2010" / "README.md": "## Canonical 2010 Inventory",
        ROOT / "requirements" / "2025" / "README.md": "## Canonical 2025 Inventory",
    }
    for path, marker in inventory_markers.items():
        text = _read(path)
        assert marker in text, f"{path.relative_to(ROOT)} missing {marker}"


def test_each_human_facing_requirement_front_door_points_to_source_inventory_and_verification() -> None:
    expectations = {
        ROOT / "docs" / "requirements" / "ieee-1516-2010" / "README.md": (
            "../../../requirements/2010/README.md",
            "../../verification/README.md",
            "../../spec_reading_map.md",
        ),
        ROOT / "docs" / "requirements" / "ieee-1516-2025" / "README.md": (
            "../../../requirements/2025/README.md",
            "../../verification/README.md",
            "../../spec_reading_map.md",
        ),
    }
    for path, refs in expectations.items():
        text = _read(path)
        for ref in refs:
            assert ref in text, f"{path.relative_to(ROOT)} missing {ref}"


def test_python_api_spec_matches_split_package_reality() -> None:
    path = ROOT / "docs/python_api_spec.md"
    text = _read(path)
    assert "installable root: `hla-rti1516e`" in text
    assert "versioned API root: `packages/hla-rti1516e/src/hla/rti1516e/`" in text
    assert "package-owned implementations: `packages/*/src/...`" in text
    assert "cross-version discovery and factory selection live under `hla.rti`" in text.lower()
    assert "../packages/hla-rti1516e/src/hla/rti1516e/rti_ambassador.py" in text
    assert "../packages/hla-rti1516e/src/hla/rti1516e/federate_ambassador.py" in text
    assert "../packages/hla-rti1516e/README.md" in text
    assert "../hla2010/spec/" not in text
    assert "hla.rti1516e.testing" not in text


def test_repo_overview_docs_describe_root_namespace_as_core_plus_temporary_facades() -> None:
    readme = _read(ROOT / "README.md")
    packages_readme = _read(ROOT / "packages" / "README.md")

    assert "`hla.rti1516e` is the IEEE 1516.1-2010 API package" in readme
    assert "`hla2010/` is a narrow top-level shim area for plugin-facing glue" not in readme
    assert "`hla` is a PEP 420 namespace package" in packages_readme


def test_tools_readme_mentions_short_java_front_door() -> None:
    text = _read(ROOT / "tools" / "README.md")
    assert "./tools/java" in text
