from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_java_quickstart_puts_python_rti_first() -> None:
    quickstart = _read(ROOT / "docs" / "java_backends_quickstart.md")
    decision_tree = _read(ROOT / "docs" / "backend_decision_tree.md")
    assert "Start with the Python RTI first." in quickstart
    assert "./tools/bootstrap python" in quickstart
    assert "python examples/target_radar_simulation.py --backend python --steps 5" in quickstart
    assert "If you are unsure, use `python`." in decision_tree


def test_java_quickstart_is_honest_about_bridge_prerequisites() -> None:
    quickstart = _read(ROOT / "docs" / "java_backends_quickstart.md")
    jpype_readme = _read(ROOT / "packages" / "hla2010-rti-java-jpype" / "README.md")
    py4j_readme = _read(ROOT / "packages" / "hla2010-rti-java-py4j" / "README.md")

    for text in (quickstart, jpype_readme, py4j_readme):
        assert "classpath" in text or "gateway" in text
        assert "not installed" in text

    assert "JPype backend requested, but jpype is not installed" in quickstart
    assert "Py4J backend requested, but py4j is not installed" in quickstart


def test_java_docs_link_install_matrix_and_route_inventory() -> None:
    quickstart = _read(ROOT / "docs" / "java_backends_quickstart.md")
    assert "[install_matrix.md](install_matrix.md)" in quickstart
    assert "[backend_route_inventory.md](backend_route_inventory.md)" in quickstart
    assert "[backend_decision_tree.md](backend_decision_tree.md)" in quickstart


def test_java_bridge_readmes_use_split_package_imports() -> None:
    jpype_readme = _read(ROOT / "packages" / "hla2010-rti-java-jpype" / "README.md")
    py4j_readme = _read(ROOT / "packages" / "hla2010-rti-java-py4j" / "README.md")

    assert "from hla2010_rti_java_jpype import JPypeConfig, rti_ambassador" in jpype_readme
    assert "from hla2010_rti_java_py4j import Py4JConfig, rti_ambassador" in py4j_readme
    assert "hla2010.rti" not in jpype_readme
    assert "hla2010.rti" not in py4j_readme
