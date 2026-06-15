from __future__ import annotations

import json
import subprocess
from pathlib import Path

from hla2010.raw_api import API_METADATA
from hla2010.spec_inventory import FEDERATE_AMBASSADOR_METHODS, RTIAMBASSADOR_METHODS
from hla2010.spec_refs import METHOD_REFERENCES
from tests.typed_json_models import ApiMetadataSource, ApiMethodMetadata


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "specs" / "hla2010_api.json"
RAW_API_PATH = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "raw_api.py"
API_METADATA_RESOURCE_PATH = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "resources" / "api_metadata.json"
SPEC_INVENTORY_PATH = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "spec_inventory.py"
SPEC_REFS_PATH = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "spec_refs.py"
SPEC_SOURCES_PATH = ROOT / "packages" / "hla2010-spec" / "src" / "hla2010" / "spec_sources.py"


def _source_payload() -> ApiMetadataSource:
    return ApiMetadataSource.from_mapping(json.loads(SOURCE_PATH.read_text(encoding="utf-8")))


def _interfaces() -> dict[str, dict[str, ApiMethodMetadata]]:
    return _source_payload().interfaces


def test_api_metadata_source_parses() -> None:
    interfaces = _interfaces()
    assert "RTIambassador" in interfaces
    assert "FederateAmbassador" in interfaces


def test_every_method_has_python_name() -> None:
    for methods in _interfaces().values():
        for method_name, metadata in methods.items():
            assert metadata.python_name, method_name


def test_every_method_has_section_or_explicit_no_section_reason() -> None:
    for methods in _interfaces().values():
        for method_name, metadata in methods.items():
            assert metadata.section or metadata.no_section_reason, method_name


def test_generated_inventory_matches_source() -> None:
    interfaces = _interfaces()
    assert tuple(sorted(interfaces["RTIambassador"])) == RTIAMBASSADOR_METHODS
    assert tuple(sorted(interfaces["FederateAmbassador"])) == FEDERATE_AMBASSADOR_METHODS


def test_generated_refs_match_source() -> None:
    for methods in _interfaces().values():
        for method_name, metadata in methods.items():
            if not metadata.section:
                continue
            ref = METHOD_REFERENCES.get(method_name)
            assert ref is not None, method_name
            assert ref.section == metadata.section
            assert ref.title == metadata.title
            assert ref.service_group == metadata.service_group


def test_generated_raw_api_matches_source() -> None:
    interfaces = _interfaces()
    for interface_name, methods in interfaces.items():
        assert set(API_METADATA[interface_name]) == set(methods)
        for method_name, metadata in methods.items():
            assert API_METADATA[interface_name][method_name] == metadata.overload_mappings()


def test_generated_files_are_current() -> None:
    result = subprocess.run(
        ["bash", "./tools/spec-api", "check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "API metadata outputs are current" in result.stdout


def test_generated_files_have_headers() -> None:
    for path in (RAW_API_PATH, SPEC_INVENTORY_PATH, SPEC_REFS_PATH, SPEC_SOURCES_PATH):
        text = path.read_text(encoding="utf-8")
        assert text.startswith("# Generated from specs/hla2010_api.json.\n# Do not edit by hand. Run ./tools/spec-api generate.\n"), path


def test_raw_api_no_longer_uses_base64_metadata_blob() -> None:
    text = RAW_API_PATH.read_text(encoding="utf-8")
    assert "base64.b64decode" not in text
    assert "import base64" not in text


def test_generated_api_metadata_resource_matches_source() -> None:
    interfaces = _interfaces()
    payload = json.loads(API_METADATA_RESOURCE_PATH.read_text(encoding="utf-8"))
    for interface_name, methods in interfaces.items():
        assert set(payload[interface_name]) == set(methods)
        for method_name, metadata in methods.items():
            assert payload[interface_name][method_name] == metadata.overload_mappings()


def test_raw_api_is_a_thin_metadata_loader() -> None:
    text = RAW_API_PATH.read_text(encoding="utf-8")
    assert 'resources.files("hla2010").joinpath("resources/api_metadata.json")' in text
    assert "API_METADATA = {" not in text
    assert len(text.splitlines()) < 1200
