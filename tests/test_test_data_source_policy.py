from __future__ import annotations

from pathlib import Path

from conftest import REPO_ROOT, read_repo_text


ROOT = REPO_ROOT
TESTS_DIR = ROOT / "tests"
ALLOWED_DIRECT_SOURCE_FILES = {
    Path("tests/conftest.py"),
    Path("tests/doc_test_helpers.py"),
    Path("tests/docs_policy_helpers.py"),
    Path("tests/test_backend_compliance_discovery_policy.py"),
    Path("tests/test_test_data_source_policy.py"),
    Path("tests/test_verification_harness_split_package.py"),
}
FORBIDDEN_FRAGMENTS = (
    '(ROOT / "tests" / "fixtures" /',
    '(ROOT / "analysis" / "compliance" /',
    '(project_root / "analysis" / "compliance" /',
)


def test_unit_tests_do_not_hardcode_external_test_data_sources() -> None:
    offenders: list[str] = []

    for path in sorted(TESTS_DIR.rglob("*.py")):
        rel_path = path.relative_to(ROOT)
        if rel_path in ALLOWED_DIRECT_SOURCE_FILES or "fixtures" in path.parts:
            continue
        text = read_repo_text(path)
        for fragment in FORBIDDEN_FRAGMENTS:
            if fragment in text:
                offenders.append(f"{rel_path}: contains {fragment!r}")

    assert not offenders, "\n".join(offenders)
