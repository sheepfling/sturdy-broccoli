from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGES = ROOT / "packages"
STANDARD_PACKAGE_ROOTS = (
    PACKAGES / "hla-rti1516e" / "src" / "hla" / "rti1516e",
    PACKAGES / "hla-rti1516-2025" / "src" / "hla" / "rti1516_2025",
)
FORBIDDEN_STANDARD_IMPORT_PREFIXES = (
    "hla.runtime",
    "hla.fom",
    "hla.backends",
    "hla.transports",
    "hla.vendors",
    "hla.bridges",
)
TYPED_PUBLIC_PACKAGES = (
    PACKAGES / "hla-rti1516e" / "src" / "hla" / "rti1516e",
    PACKAGES / "hla-rti1516-2025" / "src" / "hla" / "rti1516_2025",
    PACKAGES / "hla-rti-core" / "src" / "hla" / "runtime",
    PACKAGES / "hla-rti-core" / "src" / "hla" / "fom",
    PACKAGES / "hla-rti-core" / "src" / "hla" / "spec",
)
COMPAT_FORWARDERS = (
    "hla.rti1516e.factory",
    "hla.rti1516e.plugin",
    "hla.rti1516e.fom",
    "hla.rti1516e.mom",
    "hla.rti1516_2025.factory",
    "hla.rti1516_2025.plugin",
    "hla.rti1516_2025.foms",
    "hla.rti1516_2025.validation",
)


def _python_files(root: Path):
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def test_forbidden_upstream_project_name_literal_is_absent() -> None:
    forbidden = "py" + "hla"
    violations: list[str] = []
    result = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    for rel in sorted(result.stdout.splitlines()):
        path = ROOT / rel
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if forbidden in rel.lower():
            violations.append(rel)
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if forbidden in text.lower():
            violations.append(rel)
    assert violations == []


def test_hla_is_pep420_namespace_package() -> None:
    assert list(PACKAGES.glob("*/src/hla/__init__.py")) == []


def test_standard_packages_do_not_import_implementation_namespaces() -> None:
    violations: list[str] = []
    for package_root in STANDARD_PACKAGE_ROOTS:
        for path in _python_files(package_root):
            rel = path.relative_to(ROOT).as_posix()
            for module in _imported_modules(path):
                if module.startswith(FORBIDDEN_STANDARD_IMPORT_PREFIXES):
                    violations.append(f"{rel}: {module}")
    assert violations == []


def test_contract_tests_and_runtime_do_not_import_upstream_reference() -> None:
    checked_roots = (
        ROOT / "tests" / "compat",
        ROOT / "scripts",
        PACKAGES / "hla-rti-core" / "src" / "hla",
        PACKAGES / "hla-rti1516e" / "src" / "hla" / "rti1516e",
        PACKAGES / "hla-rti1516-2025" / "src" / "hla" / "rti1516_2025",
    )
    violations: list[str] = []
    for root in checked_roots:
        for path in _python_files(root):
            rel = path.relative_to(ROOT).as_posix()
            for module in _imported_modules(path):
                if module == "upstream_reference" or module.startswith("upstream_reference."):
                    violations.append(f"{rel}: {module}")
    assert violations == []


def test_public_typed_packages_include_py_typed() -> None:
    missing = [path.relative_to(ROOT).as_posix() for path in TYPED_PUBLIC_PACKAGES if not (path / "py.typed").is_file()]
    assert missing == []


def test_no_compatibility_forwarders_are_present_without_tests() -> None:
    present = []
    for module_name in COMPAT_FORWARDERS:
        relative = Path(*module_name.split("."))
        candidates = list(PACKAGES.glob(f"*/src/{relative}.py"))
        present.extend(path.relative_to(ROOT).as_posix() for path in candidates)
    assert present == []


def test_fom_xml_assets_live_under_hla_fom_resources() -> None:
    standard_assets = []
    for package_root in STANDARD_PACKAGE_ROOTS:
        for suffix in ("*.xml", "*.xsd"):
            standard_assets.extend(path.relative_to(ROOT).as_posix() for path in package_root.rglob(suffix))
    assert standard_assets == []

    fom_resource_root = PACKAGES / "hla-rti-core" / "src" / "hla" / "fom" / "resources"
    assert any(fom_resource_root.rglob("*.xml"))


def test_contract_snapshots_live_under_compat_and_have_metadata() -> None:
    contract_root = ROOT / "compat" / "upstream_contract"
    snapshots = sorted((contract_root / "v0.1.1").glob("*.json"))
    assert {path.name for path in snapshots} == {"ieee1516_2025.json", "ieee1516e.json"}
    for snapshot in snapshots:
        payload = json.loads(snapshot.read_text(encoding="utf-8"))
        assert payload["standard"] in {"ieee1516e", "ieee1516_2025"}
        assert payload["tag"] == "v0.1.1"
        assert payload["tag_commit"] == "ed39b02e4c6e7813fce9e0e183b184c8513d4dd6"
        assert payload["package"].startswith("upstream_reference.")
        assert "contract_facts" in payload
        assert "modules" in payload


def test_2010_public_docs_advertise_canonical_camelcase_names() -> None:
    interface_contracts = (ROOT / "docs" / "reference" / "hla_interface_contracts.md").read_text(encoding="utf-8")
    orchestration = (ROOT / "docs" / "federation_orchestration.md").read_text(encoding="utf-8")
    java_bridge = (ROOT / "docs" / "java_bridge_wrapping_guide.md").read_text(encoding="utf-8")

    assert "snake_case" not in interface_contracts
    assert "evoke_multiple_callbacks(...)" not in orchestration
    assert "create_federation_execution" not in java_bridge
    assert "join_federation_execution" not in java_bridge
