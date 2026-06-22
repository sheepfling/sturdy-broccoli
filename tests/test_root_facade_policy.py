from __future__ import annotations

import importlib
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]
ROOT_FACADE_DOCS = (
    ROOT / "docs/import_boundary_rules.md",
    ROOT / "docs/package_layout.md",
    ROOT / "docs/workspace_layout.md",
)
SINGULAR_ROOT_FACADE_DOCS = (
    ROOT / "README.md",
    ROOT / "docs/python_environment.md",
    ROOT / "docs/workspace_layout.md",
    ROOT / "packages/README.md",
    ROOT / "packages/hla-rti1516e/README.md",
)
DIRECT_RUNTIME_PREFERENCE_DOCS = (
    ROOT / "docs/architecture.md",
    ROOT / "docs/rti_options_and_test_matrix.md",
    ROOT / "docs/import_boundary_rules.md",
)
REMOVED_ROOT_FACADE_MIGRATION_DOCS = {
    ROOT / "packages/hla-vendor-pitch-jpype/MIGRATION.md": "hla.rti1516e.backends.jpype",
    ROOT / "packages/hla-vendor-pitch-py4j/MIGRATION.md": "hla.rti1516e.backends.py4j",
    ROOT / "packages/hla-bridge-java-common/MIGRATION.md": "hla.rti1516e.backends.java_common",
    ROOT / "packages/hla-bridge-java-jpype/MIGRATION.md": "hla.rti1516e.backends.jpype",
    ROOT / "packages/hla-bridge-java-py4j/MIGRATION.md": "hla.rti1516e.backends.py4j",
    ROOT / "packages/hla-transport-rest/MIGRATION.md": "src/hla2010/backends/rest_transport/",
    ROOT / "packages/hla-fom-target-radar/MIGRATION.md": "src/hla2010/scenarios/",
}
RETAINED_PACKAGE_LOCAL_FACADE_DOCS = {
    ROOT / "packages/hla-bridge-java-jpype/MIGRATION.md",
    ROOT / "packages/hla-bridge-java-py4j/MIGRATION.md",
    ROOT / "packages/hla-vendor-pitch-jpype/MIGRATION.md",
    ROOT / "packages/hla-vendor-pitch-py4j/MIGRATION.md",
}
RETAINED_PACKAGE_LOCAL_FACADE_MODULES = {
    ROOT / "packages/hla-bridge-java-jpype/MIGRATION.md": (
        "packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/runtime.py",
        "packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/adapter.py",
        "packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/factory.py",
    ),
    ROOT / "packages/hla-bridge-java-py4j/MIGRATION.md": (
        "packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/runtime.py",
        "packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/adapter.py",
        "packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/factory.py",
    ),
    ROOT / "packages/hla-vendor-pitch-jpype/MIGRATION.md": (
        "packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/runtime.py",
        "packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/adapter.py",
        "packages/hla-vendor-pitch-jpype/src/hla/vendors/pitch/jpype/factory.py",
    ),
    ROOT / "packages/hla-vendor-pitch-py4j/MIGRATION.md": (
        "packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/runtime.py",
        "packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/adapter.py",
        "packages/hla-vendor-pitch-py4j/src/hla/vendors/pitch/py4j/factory.py",
    ),
}


def _join(*parts: str) -> str:
    return ".".join(parts)


def _live_root_python_files() -> set[str]:
    root = ROOT / "src" / "hla2010"
    if not root.exists():
        return set()
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
    }


def _root_modules_importing_split_packages() -> dict[str, list[str]]:
    root = ROOT / "src" / "hla2010"
    if not root.exists():
        return {}
    imports: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root).as_posix()
        hits: list[str] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("from hla2010_") or stripped.startswith("import hla.rti1516e_"):
                hits.append(stripped)
        if hits:
            imports[rel] = hits
    return imports


def test_removed_root_compatibility_modules_stay_unimportable() -> None:
    removed_modules = (
        _join("hla2010", "backends", "conversion"),
        _join("hla2010", "backends", "java_plugins"),
        _join("hla2010", "backends", "python"),
        _join("hla2010", "backends", "python", "backend"),
        _join("hla2010", "backends", "python", "engine"),
        _join("hla2010", "backends", "python", "factory"),
        _join("hla2010", "backends", "python", "state"),
        _join("hla2010", "backends", "base"),
        _join("hla2010", "backends", "grpc_transport"),
        _join("hla2010", "backends", "grpc_transport", "client"),
        _join("hla2010", "backends", "grpc_transport", "python_server"),
        _join("hla2010", "backends", "grpc_transport", "transport"),
        _join("hla2010", "backends", "transport"),
        _join("hla2010", "clause13_conformance"),
        _join("hla2010", "conformance"),
        _join("hla2010", "fom_overview"),
        _join("hla2010", "java_runtime"),
        _join("hla2010", "mom_catalog"),
        _join("hla2010", "mom_negative_testing"),
        _join("hla2010", "plugin_api"),
        _join("hla2010", "requirements_backlog"),
        _join("hla2010", "requirements_packet"),
        _join("hla2010", "scenarios", "target_radar"),
        _join("hla2010", "scenarios", "target_radar_cli"),
        _join("hla2010", "service_reporting"),
        _join("hla2010", "startup"),
        _join("hla2010", "time_management"),
        _join("hla2010", "transport_registry"),
        _join("hla2010", "transport_codecs"),
        _join("hla2010", "verification"),
    )

    for module_name in removed_modules:
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        raise AssertionError(f"removed root compatibility module still imports: {module_name}")


def test_removed_root_compatibility_files_stay_absent() -> None:
    removed_paths = (
        ROOT / "src/hla2010/backends/__init__.py",
        ROOT / "src/hla2010/backends/python/__init__.py",
        ROOT / "src/hla2010/backends/base.py",
        ROOT / "src/hla2010/backends/grpc_transport/__init__.py",
        ROOT / "src/hla2010/scenarios/__init__.py",
        ROOT / "src/hla2010/verification.py",
        ROOT / "src/hla2010/conformance.py",
        ROOT / "src/hla2010/time_management.py",
        ROOT / "src/hla2010/transport_registry.py",
    )

    leftovers = [path.relative_to(ROOT).as_posix() for path in removed_paths if path.exists()]
    assert not leftovers, "\n".join(leftovers)


def test_live_root_python_surface_stays_narrow() -> None:
    assert _live_root_python_files() == set()


def test_only_documented_root_facades_import_split_packages() -> None:
    assert _root_modules_importing_split_packages() == {}


def test_root_facade_docs_explicitly_name_the_neutral_runtime_facade() -> None:
    required_fragments = (
        "hla.rti",
        "cross-version",
        "PEP 420",
    )
    for path in ROOT_FACADE_DOCS:
        text = path.read_text(encoding="utf-8")
        for fragment in required_fragments:
            assert fragment in text, f"{path.relative_to(ROOT)} missing {fragment}"


def test_high_level_docs_name_versioned_specs_and_neutral_runtime_facade() -> None:
    required_fragments = (
        "hla.rti1516e",
        "hla.rti",
    )
    forbidden_fragments = (
        "temporary compatibility facades",
        "temporary split-package facades",
        "small number of documented temporary compatibility facades",
        "narrow set of documented workspace facades",
    )

    for path in SINGULAR_ROOT_FACADE_DOCS:
        text = path.read_text(encoding="utf-8")
        for fragment in required_fragments:
            assert fragment in text, f"{path.relative_to(ROOT)} missing {fragment}"
        for fragment in forbidden_fragments:
            assert fragment not in text, f"{path.relative_to(ROOT)} still uses plural facade wording: {fragment}"


def test_runtime_discovery_docs_keep_direct_runtime_package_preferred_over_root_facade() -> None:
    required_fragments = (
        "hla.rti",
        "backend discovery",
    )

    for path in DIRECT_RUNTIME_PREFERENCE_DOCS:
        text = path.read_text(encoding="utf-8")
        for fragment in required_fragments:
            assert fragment in text, f"{path.relative_to(ROOT)} missing {fragment}"

    architecture_text = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    assert "neutral spec/backend discovery and ambassador-creation facade" in architecture_text

    options_text = (ROOT / "docs/rti_options_and_test_matrix.md").read_text(encoding="utf-8")
    assert "hla.rti" in options_text

    import_boundary_text = (ROOT / "docs/import_boundary_rules.md").read_text(encoding="utf-8")
    assert "Package-owned code should import runtime factory helpers" in import_boundary_text
    assert "hla-backend-python2025" in import_boundary_text
    assert "must not import back through `hla.backends.shim.*`" in import_boundary_text
    assert "hla-backend-shim" in import_boundary_text


def test_package_migration_docs_do_not_claim_removed_root_compatibility_facades_remain() -> None:
    for path, removed_facade in REMOVED_ROOT_FACADE_MIGRATION_DOCS.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        normalized_text = " ".join(text.split())
        assert removed_facade in text, f"{path.relative_to(ROOT)} missing removed facade reference"
        assert "do not remain available" in normalized_text or "Removed root compatibility facades" in text, (
            f"{path.relative_to(ROOT)} should describe removed root facade state explicitly"
        )
        assert "remain as compatibility facades" not in text or "package-local compatibility facades" in text, (
            f"{path.relative_to(ROOT)} still claims removed root facade remains"
        )


def test_only_expected_package_migration_docs_advertise_retained_package_local_facades() -> None:
    migration_docs = sorted((ROOT / "packages").rglob("MIGRATION.md"))
    with_retained_heading = {
        path
        for path in migration_docs
        if "Compatibility facades retained:" in path.read_text(encoding="utf-8")
    }
    assert with_retained_heading == RETAINED_PACKAGE_LOCAL_FACADE_DOCS

    for path in with_retained_heading:
        text = path.read_text(encoding="utf-8")
        assert "Removed root compatibility facades:" in text, (
            f"{path.relative_to(ROOT)} should distinguish retained package-local facades from removed root facades"
        )


def test_retained_package_local_facade_docs_point_at_real_package_modules() -> None:
    for path, modules in RETAINED_PACKAGE_LOCAL_FACADE_MODULES.items():
        text = path.read_text(encoding="utf-8")
        for module_path in modules:
            module = ".".join(module_path.removesuffix(".py").split("/"))
            dotted = module.split("src.", 1)[1]
            assert dotted in text, f"{path.relative_to(ROOT)} missing retained module {dotted}"
            assert (ROOT / module_path).exists(), f"documented retained facade missing file: {module_path}"


def test_root_package_version_matches_hla2010_spec_package_version() -> None:
    assert not (ROOT / "src" / "hla2010" / "__init__.py").exists()


def test_legacy_root_namespace_directories_contain_no_python_modules() -> None:
    legacy_dirs = (
        ROOT / "src/hla2010/backends",
        ROOT / "src/hla2010/backends/certi",
        ROOT / "src/hla2010/backends/certi_java",
        ROOT / "src/hla2010/backends/grpc_transport",
        ROOT / "src/hla2010/backends/jpype",
        ROOT / "src/hla2010/backends/py4j",
        ROOT / "src/hla2010/backends/python",
        ROOT / "src/hla2010/backends/rest_transport",
        ROOT / "src/hla2010/scenarios",
        ROOT / "src/hla2010/testing",
    )

    leftovers: list[str] = []
    for directory in legacy_dirs:
        leftovers.extend(path.relative_to(ROOT).as_posix() for path in directory.rglob("*.py"))
    assert not leftovers, "\n".join(sorted(leftovers))


def test_documented_root_workspace_facades_remain_available() -> None:
    import hla.rti1516e.ambassadors
    import hla.rti1516e.api
    import hla.rti1516e.rti

    assert hla.rti1516e.ambassadors.__name__ == "hla.rti1516e.ambassadors"
    assert hla.rti1516e.api.__name__ == "hla.rti1516e.api"
    assert hla.rti1516e.rti.__name__ == "hla.rti1516e.rti"


def test_root_rti_workspace_facade_is_only_used_by_deliberate_public_contract_tests() -> None:
    allowed = {
        "tests/test_python_api_spec.py",
        "tests/test_root_facade_policy.py",
    }
    import_pattern = re.compile(r"^\s*(from hla2010\.rti import|import hla.rti1516e\.rti\b)")

    hits: set[str] = set()
    for path in sorted((ROOT / "tests").rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        for line in path.read_text(encoding="utf-8").splitlines():
            if import_pattern.search(line):
                hits.add(rel)
                break

    assert hits == allowed


def test_root_ambassadors_workspace_facade_is_only_used_by_deliberate_public_contract_tests() -> None:
    allowed = {
        "tests/test_root_facade_policy.py",
    }
    import_pattern = re.compile(r"^\s*(from hla2010\.ambassadors import|import hla.rti1516e\.ambassadors\b)")

    hits: set[str] = set()
    for path in sorted((ROOT / "tests").rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        for line in path.read_text(encoding="utf-8").splitlines():
            if import_pattern.search(line):
                hits.add(rel)
                break

    assert hits == allowed


def test_removed_runtime_api_workspace_facade_is_not_used_by_tests() -> None:
    allowed: set[str] = set()
    import_pattern = re.compile(r"^\s*(from hla2010\.runtime_api import|import hla.rti1516e\.runtime_api\b)")

    hits: set[str] = set()
    for path in sorted((ROOT / "tests").rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        for line in path.read_text(encoding="utf-8").splitlines():
            if import_pattern.search(line):
                hits.add(rel)
                break

    assert hits == allowed


def test_root_api_workspace_facade_is_only_used_by_deliberate_public_contract_tests() -> None:
    allowed = {
        "tests/test_root_facade_policy.py",
    }
    import_pattern = re.compile(r"^\s*(from hla2010\.api import|import hla.rti1516e\.api\b)")

    hits: set[str] = set()
    for path in sorted((ROOT / "tests").rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        for line in path.read_text(encoding="utf-8").splitlines():
            if import_pattern.search(line):
                hits.add(rel)
                break

    assert hits == allowed
