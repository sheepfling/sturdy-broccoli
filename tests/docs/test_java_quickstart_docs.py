from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from conftest import REPO_ROOT, load_json_fixture, read_repo_text


ROOT = REPO_ROOT


@dataclass(frozen=True)
class JavaQuickstartPolicy:
    quickstart_contains: tuple[str, ...]
    decision_tree_contains: tuple[str, ...]
    bridge_prerequisite_tokens: tuple[str, ...]
    jpype_readme_contains: tuple[str, ...]
    py4j_readme_contains: tuple[str, ...]
    bridge_readme_absent: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: dict[str, object]) -> JavaQuickstartPolicy:
        return cls(
            quickstart_contains=tuple(str(item) for item in payload["quickstart_contains"]),
            decision_tree_contains=tuple(str(item) for item in payload["decision_tree_contains"]),
            bridge_prerequisite_tokens=tuple(str(item) for item in payload["bridge_prerequisite_tokens"]),
            jpype_readme_contains=tuple(str(item) for item in payload["jpype_readme_contains"]),
            py4j_readme_contains=tuple(str(item) for item in payload["py4j_readme_contains"]),
            bridge_readme_absent=tuple(str(item) for item in payload["bridge_readme_absent"]),
        )


POLICY = JavaQuickstartPolicy.from_mapping(load_json_fixture("java_quickstart_policy.json"))


def _read(path: Path) -> str:
    return read_repo_text(path)


def test_java_quickstart_puts_python_rti_first() -> None:
    quickstart = _read(ROOT / "docs" / "java_backends_quickstart.md")
    decision_tree = _read(ROOT / "docs" / "backend_decision_tree.md")
    for snippet in POLICY.quickstart_contains[:3]:
        assert snippet in quickstart
    for snippet in POLICY.decision_tree_contains:
        assert snippet in decision_tree


def test_java_quickstart_is_honest_about_bridge_prerequisites() -> None:
    quickstart = _read(ROOT / "docs" / "java_backends_quickstart.md")
    jpype_readme = _read(ROOT / "packages" / "hla2010-rti-java-jpype" / "README.md")
    py4j_readme = _read(ROOT / "packages" / "hla2010-rti-java-py4j" / "README.md")

    for text in (quickstart, jpype_readme, py4j_readme):
        assert any(token in text for token in POLICY.bridge_prerequisite_tokens[:2])
        assert POLICY.bridge_prerequisite_tokens[2] in text

    for snippet in POLICY.quickstart_contains[6:]:
        assert snippet in quickstart


def test_java_docs_link_install_matrix_and_route_inventory() -> None:
    quickstart = _read(ROOT / "docs" / "java_backends_quickstart.md")
    for snippet in POLICY.quickstart_contains[3:6]:
        assert snippet in quickstart


def test_java_bridge_readmes_use_split_package_imports() -> None:
    jpype_readme = _read(ROOT / "packages" / "hla2010-rti-java-jpype" / "README.md")
    py4j_readme = _read(ROOT / "packages" / "hla2010-rti-java-py4j" / "README.md")

    for snippet in POLICY.jpype_readme_contains:
        assert snippet in jpype_readme
    for snippet in POLICY.py4j_readme_contains:
        assert snippet in py4j_readme
    for snippet in POLICY.bridge_readme_absent:
        assert snippet not in jpype_readme
        assert snippet not in py4j_readme
