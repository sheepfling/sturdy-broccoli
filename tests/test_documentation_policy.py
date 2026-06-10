from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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
        ROOT / "scripts/bootstrap_profile.sh",
        ROOT / "scripts/bootstrap_python.sh",
        ROOT / "examples/target_radar_simulation.py",
        ROOT / "examples/backend_recording.py",
        ROOT / "scripts/ci/test.sh",
    ),
    ROOT / "docs/first_run.md": (
        ROOT / "scripts/bootstrap_profile.sh",
        ROOT / "examples/backend_recording.py",
        ROOT / "examples/target_radar_simulation.py",
    ),
    ROOT / "docs/python_environment.md": (
        ROOT / "scripts/bootstrap_profile.sh",
        ROOT / "scripts/bootstrap_python.sh",
        ROOT / "examples/target_radar_simulation.py",
        ROOT / "scripts/run_two_federate_suite.py",
        ROOT / "scripts/ci/test.sh",
        ROOT / "tools/certi-easy",
        ROOT / "tools/pitch",
    ),
    ROOT / "docs/two_federate_quickstart.md": (
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


def test_python_api_spec_matches_split_package_reality() -> None:
    path = ROOT / "docs/python_api_spec.md"
    text = _read(path)
    assert "installable root: `hla2010-spec`" in text
    assert "workspace facade: `src/hla2010/`" in text
    assert "package-owned implementations: `packages/*/src/...`" in text
    assert "../src/hla2010/spec/__init__.py" in text
    assert "../packages/hla2010-spec/README.md" in text
    assert "../hla2010/spec/" not in text
    assert "hla2010.testing" not in text
