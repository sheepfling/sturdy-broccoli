"""FOM XML -> protobuf JSON -> XML round-trip verification helpers."""

from __future__ import annotations

import io
import json
import tempfile
import zipfile
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Iterable, Mapping

from google.protobuf import json_format

from hla.rti1516e.fom import FOMCatalog, FOMModule, FOMResolver, merge_fom_modules, parse_fom_xml, serialize_fom_module
from hla.transports.grpc.fedpro2010 import datatypes_pb2 as fedpro2010_datatypes
from hla.transports.grpc.fedpro2025 import datatypes_2025_pb2 as fedpro2025_datatypes


TARGET_RADAR_FOM = Path(
    str(resources.files("hla.foms.target_radar").joinpath("resources", "foms", "TargetRadarFOMmodule.xml"))
)

_DEFAULT_MODULES_2010: tuple[str, ...] = (
    "HLAstandardMIM.xml",
    "VendorSmokeFOM.xml",
    "DemoFOMmodule.xml",
    "TargetRadarFOMmodule.xml",
)
_DEFAULT_MODULES_2025: tuple[str, ...] = ("TargetRadarFOMmodule.xml",)
_DEFAULT_TRANSPORTATION_NAMES = ("HLAreliable", "HLAbestEffort")
_DEFAULT_SWITCH_SETTINGS = {
    "autoProvide": "false",
    "conveyRegionDesignatorSets": "false",
    "conveyProducingFederate": "false",
    "attributeScopeAdvisory": "false",
    "attributeRelevanceAdvisory": "false",
    "objectClassRelevanceAdvisory": "false",
    "interactionRelevanceAdvisory": "false",
    "serviceReporting": "false",
    "exceptionReporting": "false",
    "delaySubscriptionEvaluation": "false",
    "automaticResignAction": "NoAction",
}
_PROTO_MODULES = {
    2010: ("rti1516e", fedpro2010_datatypes),
    2025: ("rti1516_2025", fedpro2025_datatypes),
}
@dataclass(frozen=True)
class FOMRoundTripModuleReport:
    source: str
    name: str | None
    uri: str
    is_mim: bool
    xml_roundtrip_ok: bool
    protobuf_file_roundtrip_ok: bool
    protobuf_url_roundtrip_ok: bool
    protobuf_compressed_roundtrip_ok: bool
    object_classes: int
    interaction_classes: int
    datatype_names: int
    dimensions: tuple[str, ...]


@dataclass(frozen=True)
class FOMRoundTripReport:
    year: int
    protobuf_schema: str
    title: str
    sources: tuple[str, ...]
    mim_source: str | None
    include_standard_mim: bool
    merged_summary: dict[str, Any]
    module_reports: tuple[FOMRoundTripModuleReport, ...]

    def to_json(self) -> str:
        return json.dumps(
            {
                "year": self.year,
                "protobuf_schema": self.protobuf_schema,
                "title": self.title,
                "sources": list(self.sources),
                "mim_source": self.mim_source,
                "include_standard_mim": self.include_standard_mim,
                "merged_summary": self.merged_summary,
                "module_reports": [
                    {
                        "source": row.source,
                        "name": row.name,
                        "uri": row.uri,
                        "is_mim": row.is_mim,
                        "xml_roundtrip_ok": row.xml_roundtrip_ok,
                        "protobuf_file_roundtrip_ok": row.protobuf_file_roundtrip_ok,
                        "protobuf_url_roundtrip_ok": row.protobuf_url_roundtrip_ok,
                        "protobuf_compressed_roundtrip_ok": row.protobuf_compressed_roundtrip_ok,
                        "object_classes": row.object_classes,
                        "interaction_classes": row.interaction_classes,
                        "datatype_names": row.datatype_names,
                        "dimensions": list(row.dimensions),
                    }
                    for row in self.module_reports
                ],
        },
        indent=2,
        sort_keys=True,
    )


def _module_signature(module: FOMModule) -> dict[str, Any]:
    transportation_names = list(_DEFAULT_TRANSPORTATION_NAMES)
    for name in module.transportation_names:
        if name not in transportation_names:
            transportation_names.append(name)
    return {
        "name": module.name,
        "model_type": module.model_type,
        "object_class_names": sorted(spec.full_name for spec in module.object_classes),
        "interaction_class_names": sorted(spec.full_name for spec in module.interaction_classes),
        "dimensions": list(module.dimensions),
        "transportation_names": transportation_names,
        "update_rates": dict(module.update_rates),
        "switch_settings": {**_DEFAULT_SWITCH_SETTINGS, **dict(module.switch_settings)},
        "time_stamp_datatype": module.time_stamp_datatype,
        "lookahead_datatype": module.lookahead_datatype,
        "is_mim": module.is_mim,
    }


def _compressed_module_payload(name: str, xml_text: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(name, xml_text.encode("utf-8"))
    return buffer.getvalue()


def _protobuf_round_trip(year: int, source_path: Path, xml_text: str, uri: str) -> tuple[bool, bool, bool]:
    _, datatypes_module = _PROTO_MODULES[year]
    payloads = (
        datatypes_module.FomModule(
            file=datatypes_module.FileFomModule(name=source_path.name, content=xml_text.encode("utf-8"))
        ),
        datatypes_module.FomModule(url=uri),
        datatypes_module.FomModule(compressedModule=_compressed_module_payload(source_path.name, xml_text)),
    )
    results: list[bool] = []
    for module_message in payloads:
        json_payload = json_format.MessageToJson(module_message, preserving_proto_field_name=True)
        reparsed = datatypes_module.FomModule()
        json_format.Parse(json_payload, reparsed)
        results.append(module_message == reparsed)
    return results[0], results[1], results[2]


def _xml_round_trip(module: FOMModule) -> tuple[bool, FOMModule, str]:
    xml_text = serialize_fom_module(module)
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False, encoding="utf-8") as handle:
        temp_path = Path(handle.name)
        handle.write(xml_text)
    try:
        reparsed = parse_fom_xml(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)
    return _module_signature(module) == _module_signature(reparsed), reparsed, xml_text


def _module_reports(year: int, resolved_modules: Iterable[FOMModule]) -> tuple[FOMRoundTripModuleReport, ...]:
    reports: list[FOMRoundTripModuleReport] = []
    for module in resolved_modules:
        xml_ok, reparsed, xml_text = _xml_round_trip(module)
        source_path = Path(str(module.path or module.source))
        file_ok, url_ok, compressed_ok = _protobuf_round_trip(year, source_path, xml_text, module.uri)
        reports.append(
            FOMRoundTripModuleReport(
                source=str(module.source),
                name=module.name,
                uri=module.uri,
                is_mim=module.is_mim,
                xml_roundtrip_ok=xml_ok,
                protobuf_file_roundtrip_ok=file_ok,
                protobuf_url_roundtrip_ok=url_ok,
                protobuf_compressed_roundtrip_ok=compressed_ok,
                object_classes=len(module.object_classes),
                interaction_classes=len(module.interaction_classes),
                datatype_names=len(module.datatype_names),
                dimensions=tuple(module.dimensions),
            )
        )
        if not xml_ok:
            raise AssertionError(f"XML round-trip signature mismatch for {module.source!r}")
        if not file_ok:
            raise AssertionError(f"protobuf file JSON round-trip mismatch for {module.source!r}")
        if not url_ok:
            raise AssertionError(f"protobuf url JSON round-trip mismatch for {module.source!r}")
        if not compressed_ok:
            raise AssertionError(f"protobuf compressed JSON round-trip mismatch for {module.source!r}")
        if _module_signature(module) != _module_signature(reparsed):
            raise AssertionError(f"module signature mismatch after round-trip for {module.source!r}")
    return tuple(reports)


def _dedupe_modules(*groups: Iterable[FOMModule]) -> tuple[FOMModule, ...]:
    seen: set[str] = set()
    ordered: list[FOMModule] = []
    for group in groups:
        for module in group:
            key = module.uri or str(module.source)
            if key in seen:
                continue
            seen.add(key)
            ordered.append(module)
    return tuple(ordered)


def build_fom_roundtrip(
    year: int,
    sources: Iterable[str | Path] | None = None,
    *,
    include_standard_mim: bool = True,
    mim_source: str | Path | None = None,
    title: str | None = None,
) -> FOMRoundTripReport:
    if year not in _PROTO_MODULES:
        supported = ", ".join(str(item) for item in sorted(_PROTO_MODULES))
        raise ValueError(f"Unsupported FOM round-trip year {year!r}; supported years: {supported}")

    resolver = FOMResolver()
    module_sources = tuple(sources or (_DEFAULT_MODULES_2010 if year == 2010 else _DEFAULT_MODULES_2025))
    resolved_sources = resolver.resolve_many(module_sources)

    mim_module = None
    mim_label: str | None = None
    if mim_source is not None:
        mim_module = resolver.resolve(mim_source)
        mim_label = str(mim_source)
    elif include_standard_mim and year == 2010:
        from hla.rti1516e.fom import standard_mim_module

        mim_module = standard_mim_module()
        mim_label = "HLAstandardMIM"

    merged_catalog: FOMCatalog = merge_fom_modules(resolved_sources, mim_module=mim_module)
    report_modules = _dedupe_modules((mim_module,) if mim_module is not None else (), resolved_sources)
    module_reports = _module_reports(year, report_modules)

    schema_name, _ = _PROTO_MODULES[year]
    report_title = title or f"{year} FedPro FOM XML/JSON round-trip"
    return FOMRoundTripReport(
        year=year,
        protobuf_schema=schema_name,
        title=report_title,
        sources=tuple(str(source) for source in module_sources),
        mim_source=mim_label,
        include_standard_mim=include_standard_mim,
        merged_summary=merged_catalog.as_summary(),
        module_reports=module_reports,
    )


def write_fom_roundtrip(
    year: int,
    sources: Iterable[str | Path] | None = None,
    *,
    output_dir: str | Path,
    include_standard_mim: bool = True,
    mim_source: str | Path | None = None,
    title: str | None = None,
) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report = build_fom_roundtrip(
        year,
        sources,
        include_standard_mim=include_standard_mim,
        mim_source=mim_source,
        title=title,
    )

    slug = f"fom-roundtrip-{year}"
    json_path = output_path / f"{slug}.json"
    md_path = output_path / f"{slug}.md"
    json_path.write_text(report.to_json() + "\n", encoding="utf-8")

    lines = [
        f"# {report.title}",
        "",
        f"- year: `{report.year}`",
        f"- protobuf schema: `{report.protobuf_schema}`",
        f"- sources: {', '.join(report.sources) or 'n/a'}",
        f"- standard MIM: {'yes' if report.include_standard_mim else 'no'}",
        f"- mim source: `{report.mim_source or 'n/a'}`",
        "",
        "## Module Results",
        "",
        "| Source | Name | XML | File JSON | URL JSON | Compressed JSON | Objects | Interactions | Datatypes |",
        "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for row in report.module_reports:
        lines.append(
            f"| {row.source} | {row.name or ''} | {'yes' if row.xml_roundtrip_ok else 'no'} | "
            f"{'yes' if row.protobuf_file_roundtrip_ok else 'no'} | "
            f"{'yes' if row.protobuf_url_roundtrip_ok else 'no'} | "
            f"{'yes' if row.protobuf_compressed_roundtrip_ok else 'no'} | "
            f"{row.object_classes} | {row.interaction_classes} | {row.datatype_names} |"
        )
    lines.extend(
        [
            "",
            "## Merged Summary",
            "",
            f"- object classes: `{len(report.merged_summary.get('object_classes', []))}`",
            f"- interaction classes: `{len(report.merged_summary.get('interaction_classes', []))}`",
            f"- dimensions: `{', '.join(report.merged_summary.get('dimensions', [])) or 'n/a'}`",
            f"- logical time implementation: `{report.merged_summary.get('logical_time_implementation') or 'n/a'}`",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


__all__ = [
    "FOMRoundTripModuleReport",
    "FOMRoundTripReport",
    "build_fom_roundtrip",
    "write_fom_roundtrip",
]
