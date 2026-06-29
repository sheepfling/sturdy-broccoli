from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = ROOT / "requirements"
REQUIREMENTS_2010 = REQUIREMENTS / "2010"
REQUIREMENTS_2025 = REQUIREMENTS / "2025"

REQUIREMENTS_2025_FILENAMES = {
    "README.md",
    "MERGE_REPORT.md",
    "NOTICE.md",
    "SOURCE_TRACE.md",
    "STRICT_DOC_INVENTORY.json",
    "STRICT_DOC_REPORT.md",
    "canonical_requirements.json",
    "backend_resolution.json",
    "requirement_completion_backlog.csv",
}


def test_requirements_corpus_blocks_are_explicit_and_separate() -> None:
    assert REQUIREMENTS_2010.is_dir()
    assert REQUIREMENTS_2025.is_dir()

    root_files = sorted(
        path.name
        for path in REQUIREMENTS.iterdir()
        if path.is_file() and path.name not in {"README.md", ".DS_Store"}
    )
    assert root_files == ["hla_1516_master_harmonization_index_v1_0.csv"]

    block_2010_files = sorted(path.name for path in REQUIREMENTS_2010.iterdir() if path.is_file() and path.name != "README.md")
    assert block_2010_files

    for path in REQUIREMENTS_2010.iterdir():
        if path.name == "README.md":
            continue
        assert path.is_file(), path
        assert not path.is_symlink(), path

    block_2025_files = sorted(path.name for path in REQUIREMENTS_2025.iterdir() if path.is_file())
    assert block_2025_files == sorted(REQUIREMENTS_2025_FILENAMES)
    assert not (REQUIREMENTS / "SOURCE_TRACE.md").exists()
    assert not (REQUIREMENTS / "MERGE_REPORT.md").exists()
    assert not (REQUIREMENTS / "STRICT_DOC_REPORT.md").exists()
