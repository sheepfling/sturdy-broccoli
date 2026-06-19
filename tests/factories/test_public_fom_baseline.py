from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

from google.protobuf import json_format

from hla.rti1516e.fom import FOMResolver, FOMModule, merge_fom_modules
from hla.transports.grpc.fedpro2010 import datatypes_pb2 as fedpro2010_datatypes


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "third_party" / "fom_baseline" / "manifest" / "public_fom_baseline_sources.json"


def _load_manifest() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _family_paths(family: dict[str, object], baseline_root: Path) -> list[Path]:
    repository = str(family["repository"])
    return [baseline_root / repository / str(path) for path in family["files"]]


def _protobuf_payloads(path: Path, uri: str, xml_text: str) -> tuple[fedpro2010_datatypes.FomModule, ...]:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(path.name, xml_text.encode("utf-8"))
    compressed = buffer.getvalue()
    return (
        fedpro2010_datatypes.FomModule(
            file=fedpro2010_datatypes.FileFomModule(name=path.name, content=xml_text.encode("utf-8"))
        ),
        fedpro2010_datatypes.FomModule(url=uri),
        fedpro2010_datatypes.FomModule(compressedModule=compressed),
    )


def test_public_fom_baseline_manifest_files_exist() -> None:
    manifest = _load_manifest()
    baseline_root = ROOT / str(manifest["baseline_root"])
    assert baseline_root.exists()

    for family in manifest["families"]:
        for path in _family_paths(family, baseline_root):
            assert path.exists(), path


def test_public_fom_baseline_families_load_as_ordered_sets() -> None:
    manifest = _load_manifest()
    baseline_root = ROOT / str(manifest["baseline_root"])
    resolver = FOMResolver()

    for family in manifest["families"]:
        paths = _family_paths(family, baseline_root)
        modules = resolver.resolve_many(paths)
        assert len(modules) == len(paths)
        catalog = merge_fom_modules(modules)
        assert catalog.object_classes or catalog.interaction_classes, family["id"]


def test_public_fom_baseline_modules_round_trip_through_fedpro_json() -> None:
    manifest = _load_manifest()
    baseline_root = ROOT / str(manifest["baseline_root"])
    resolver = FOMResolver()

    for family in manifest["families"]:
        modules = resolver.resolve_many(_family_paths(family, baseline_root))
        for module in modules:
            assert isinstance(module, FOMModule)
            assert module.path is not None
            xml_text = module.path.read_text(encoding="utf-8")
            for payload in _protobuf_payloads(module.path, module.uri, xml_text):
                encoded = json_format.MessageToJson(payload, preserving_proto_field_name=True)
                reparsed = fedpro2010_datatypes.FomModule()
                json_format.Parse(encoded, reparsed)
                assert reparsed == payload, (family["id"], module.path.name)
