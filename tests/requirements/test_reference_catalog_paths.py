from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFERENCE_DIR = ROOT / "requirements" / "reference"
FORBIDDEN_PLACEHOLDERS = (
    "docs/omt",
    "docs/rationale",
    "requirements/source_control",
    "tests/conformance",
    "tests/omt_conformance",
)


def test_reference_requirement_catalogs_do_not_use_removed_placeholder_paths() -> None:
    violations: list[str] = []
    for path in sorted(REFERENCE_DIR.glob("*.csv")):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_PLACEHOLDERS:
            if marker in text:
                violations.append(f"{path.relative_to(ROOT).as_posix()}: {marker}")
    assert not violations, "\n".join(violations)


def test_reference_requirement_catalogs_do_not_point_to_root_level_clause_catalogs() -> None:
    violations: list[str] = []
    for path in sorted(REFERENCE_DIR.glob("*.csv")):
        text = path.read_text(encoding="utf-8")
        if "requirements/hla" in text:
            violations.append(path.relative_to(ROOT).as_posix())
    assert not violations, "\n".join(violations)
