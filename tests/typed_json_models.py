from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tests.compliance_row_models import BackendCatalogRow


def _string(value: object) -> str:
    return str(value).strip()


def _string_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(_string(item) for item in value)
    return ()


def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


@dataclass(frozen=True)
class RequirementSpec:
    spec_id: str
    legacy_requirement_prefix: str
    document_title: str
    edition_year: int | None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RequirementSpec:
        edition_year = payload.get("edition_year")
        return cls(
            spec_id=_string(payload.get("spec_id")),
            legacy_requirement_prefix=_string(payload.get("legacy_requirement_prefix")),
            document_title=_string(payload.get("document_title")),
            edition_year=edition_year if isinstance(edition_year, int) else None,
        )

    def aliases(self) -> tuple[str, ...]:
        aliases = [self.spec_id]
        if self.legacy_requirement_prefix:
            aliases.append(self.legacy_requirement_prefix)
        return tuple(alias for alias in aliases if alias)

    def to_mapping(self) -> dict[str, object]:
        return {
            "spec_id": self.spec_id,
            "legacy_requirement_prefix": self.legacy_requirement_prefix,
            "document_title": self.document_title,
            "edition_year": self.edition_year,
        }


@dataclass(frozen=True)
class RequirementRegistry:
    active_bindings: dict[str, str]
    specs: tuple[RequirementSpec, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RequirementRegistry:
        active_bindings_raw = payload.get("active_bindings")
        return cls(
            active_bindings={
                _string(key): _string(value)
                for key, value in active_bindings_raw.items()
            }
            if isinstance(active_bindings_raw, Mapping)
            else {},
            specs=tuple(
                RequirementSpec.from_mapping(spec)
                for spec in payload.get("specs", ())
                if isinstance(spec, Mapping)
            ),
        )

    def title_for_alias(self, alias: str) -> str:
        candidate = _string(alias)
        for spec in self.specs:
            if candidate in spec.aliases():
                return spec.document_title or candidate
        return candidate

    def title_for_binding(self, binding: str) -> str:
        return self.title_for_alias(self.active_bindings.get(_string(binding), _string(binding)))

    def to_mapping(self) -> dict[str, object]:
        return {
            "active_bindings": dict(self.active_bindings),
            "specs": [spec.to_mapping() for spec in self.specs],
        }


@dataclass(frozen=True)
class RequirementSourceOfTruth:
    registry: RequirementRegistry

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RequirementSourceOfTruth:
        return cls(
            registry=RequirementRegistry.from_mapping(_mapping(payload.get("requirement_id_registry")))
        )

    def title_for_alias(self, alias: str) -> str:
        return self.registry.title_for_alias(alias)

    def title_for_binding(self, binding: str) -> str:
        return self.registry.title_for_binding(binding)

    def to_mapping(self) -> dict[str, object]:
        return {"requirement_id_registry": self.registry.to_mapping()}


@dataclass(frozen=True)
class ApiOverload:
    data: Mapping[str, object]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> ApiOverload:
        return cls(data=dict(payload))

    def to_mapping(self) -> dict[str, object]:
        return dict(self.data)


@dataclass(frozen=True)
class ApiMethodMetadata:
    python_name: str
    section: str
    no_section_reason: str
    service_group: str
    title: str
    overloads: tuple[ApiOverload, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> ApiMethodMetadata:
        return cls(
            python_name=_string(payload.get("python_name")),
            section=_string(payload.get("section")),
            no_section_reason=_string(payload.get("no_section_reason")),
            service_group=_string(payload.get("service_group")),
            title=_string(payload.get("title")),
            overloads=tuple(
                ApiOverload.from_mapping(overload)
                for overload in payload.get("overloads", ())
                if isinstance(overload, Mapping)
            ),
        )

    def overload_mappings(self) -> list[dict[str, object]]:
        return [overload.to_mapping() for overload in self.overloads]


@dataclass(frozen=True)
class ApiMetadataSource:
    interfaces: dict[str, dict[str, ApiMethodMetadata]]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> ApiMetadataSource:
        interfaces: dict[str, dict[str, ApiMethodMetadata]] = {}
        for interface_name, methods in _mapping(payload.get("interfaces")).items():
            if not isinstance(methods, Mapping):
                continue
            interfaces[_string(interface_name)] = {
                _string(method_name): ApiMethodMetadata.from_mapping(metadata)
                for method_name, metadata in methods.items()
                if isinstance(metadata, Mapping)
            }
        return cls(interfaces=interfaces)


@dataclass(frozen=True)
class PythonRtiServiceMapRow:
    hla_method: str
    python_name: str
    service_group: str
    implementation_module: str
    implementation_symbol: str
    requirement_ids: tuple[str, ...]
    positive_tests: tuple[str, ...]
    negative_tests: tuple[str, ...]
    status: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> PythonRtiServiceMapRow:
        return cls(
            hla_method=_string(payload.get("hla_method")),
            python_name=_string(payload.get("python_name")),
            service_group=_string(payload.get("service_group")),
            implementation_module=_string(payload.get("implementation_module")),
            implementation_symbol=_string(payload.get("implementation_symbol")),
            requirement_ids=tuple(
                entry.strip() for entry in _string(payload.get("requirement_ids")).split(";") if entry.strip()
            ),
            positive_tests=tuple(
                entry.strip() for entry in _string(payload.get("positive_tests")).split(";") if entry.strip()
            ),
            negative_tests=tuple(
                entry.strip() for entry in _string(payload.get("negative_tests")).split(";") if entry.strip()
            ),
            status=_string(payload.get("status")),
        )


@dataclass(frozen=True)
class FactoryBackendInfo:
    kind: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> FactoryBackendInfo:
        return cls(kind=_string(payload.get("kind")))


@dataclass(frozen=True)
class FactoryProbe:
    available: bool

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> FactoryProbe:
        return cls(available=bool(payload.get("available")))


@dataclass(frozen=True)
class FactorySelectionOutput:
    selected_name: str
    selectable_names: tuple[str, ...]
    backend_info: FactoryBackendInfo
    probe: FactoryProbe

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> FactorySelectionOutput:
        return cls(
            selected_name=_string(payload.get("selected_name")),
            selectable_names=_string_tuple(payload.get("selectable_names")),
            backend_info=FactoryBackendInfo.from_mapping(_mapping(payload.get("backend_info"))),
            probe=FactoryProbe.from_mapping(_mapping(payload.get("probe"))),
        )


@dataclass(frozen=True)
class PreflightCheckRow:
    name: str
    ok: bool
    message: str
    detail: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> PreflightCheckRow:
        return cls(
            name=_string(payload.get("name")),
            ok=bool(payload.get("ok")),
            message=_string(payload.get("message")),
            detail=_string(payload.get("detail")),
        )


@dataclass(frozen=True)
class CertiBuildRootStatus:
    marker_exists: bool

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> CertiBuildRootStatus:
        return cls(marker_exists=bool(payload.get("marker_exists")))


@dataclass(frozen=True)
class PathMarkerStatus:
    path: str
    marker: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> PathMarkerStatus:
        return cls(path=_string(payload.get("path")), marker=_string(payload.get("marker")))


@dataclass(frozen=True)
class CertiRuntimeProfile:
    build_root: CertiBuildRootStatus
    prefix: PathMarkerStatus
    source: PathMarkerStatus

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> CertiRuntimeProfile:
        return cls(
            build_root=CertiBuildRootStatus.from_mapping(_mapping(payload.get("build_root"))),
            prefix=PathMarkerStatus.from_mapping(_mapping(payload.get("prefix"))),
            source=PathMarkerStatus.from_mapping(_mapping(payload.get("source"))),
        )


@dataclass(frozen=True)
class CertiRuntimeProfiles:
    active: CertiRuntimeProfile
    patched: CertiRuntimeProfile

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> CertiRuntimeProfiles:
        return cls(
            active=CertiRuntimeProfile.from_mapping(_mapping(payload.get("active"))),
            patched=CertiRuntimeProfile.from_mapping(_mapping(payload.get("patched"))),
        )


@dataclass(frozen=True)
class RuntimeMarkerRequirement:
    required_marker: str
    container_name: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RuntimeMarkerRequirement:
        return cls(
            required_marker=_string(payload.get("required_marker")),
            container_name=_string(payload.get("container_name")),
        )


@dataclass(frozen=True)
class PortStatus:
    port: int | None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> PortStatus:
        port = payload.get("port")
        return cls(port=port if isinstance(port, int) else None)


@dataclass(frozen=True)
class PitchPorts:
    crc: PortStatus
    fedpro: PortStatus

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> PitchPorts:
        return cls(
            crc=PortStatus.from_mapping(_mapping(payload.get("crc"))),
            fedpro=PortStatus.from_mapping(_mapping(payload.get("fedpro"))),
        )


@dataclass(frozen=True)
class CertiPreflightOutput:
    tool: str
    exit_code: int | None
    result: str
    checks: tuple[PreflightCheckRow, ...]
    runtime_profiles: CertiRuntimeProfiles
    required_markers: dict[str, str]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> CertiPreflightOutput:
        exit_code = payload.get("exit_code")
        return cls(
            tool=_string(payload.get("tool")),
            exit_code=exit_code if isinstance(exit_code, int) else None,
            result=_string(payload.get("result")),
            checks=tuple(
                PreflightCheckRow.from_mapping(row)
                for row in payload.get("checks", ())
                if isinstance(row, Mapping)
            ),
            runtime_profiles=CertiRuntimeProfiles.from_mapping(_mapping(payload.get("runtime_profiles"))),
            required_markers={
                _string(key): _string(value)
                for key, value in _mapping(payload.get("required_markers")).items()
            },
        )

    def check(self, name: str) -> PreflightCheckRow:
        return next(row for row in self.checks if row.name == name)


@dataclass(frozen=True)
class PitchPreflightOutput:
    tool: str
    exit_code: int | None
    result: str
    checks: tuple[PreflightCheckRow, ...]
    runtime: RuntimeMarkerRequirement
    required_markers: dict[str, str]
    ports: PitchPorts

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> PitchPreflightOutput:
        exit_code = payload.get("exit_code")
        return cls(
            tool=_string(payload.get("tool")),
            exit_code=exit_code if isinstance(exit_code, int) else None,
            result=_string(payload.get("result")),
            checks=tuple(
                PreflightCheckRow.from_mapping(row)
                for row in payload.get("checks", ())
                if isinstance(row, Mapping)
            ),
            runtime=RuntimeMarkerRequirement.from_mapping(_mapping(payload.get("runtime"))),
            required_markers={
                _string(key): _string(value)
                for key, value in _mapping(payload.get("required_markers")).items()
            },
            ports=PitchPorts.from_mapping(_mapping(payload.get("ports"))),
        )

    def check(self, name: str) -> PreflightCheckRow:
        return next(row for row in self.checks if row.name == name)


@dataclass(frozen=True)
class StatusField:
    status: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> StatusField:
        return cls(status=_string(payload.get("status")))


@dataclass(frozen=True)
class PythonRoutePreflightOutput:
    tool: str
    python_direct: str
    loopback: StatusField
    grpc_import: StatusField
    python_grpc: StatusField

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> PythonRoutePreflightOutput:
        return cls(
            tool=_string(payload.get("tool")),
            python_direct=_string(payload.get("python_direct")),
            loopback=StatusField.from_mapping(_mapping(payload.get("loopback"))),
            grpc_import=StatusField.from_mapping(_mapping(payload.get("grpc_import"))),
            python_grpc=StatusField.from_mapping(_mapping(payload.get("python_grpc"))),
        )


@dataclass(frozen=True)
class VendorRunnerTemplateProfile:
    ok: bool

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorRunnerTemplateProfile:
        return cls(ok=bool(payload.get("ok")))


@dataclass(frozen=True)
class VendorRunnerTemplateDriftOutput:
    suite_name: str
    exit_code: int | None
    profiles: tuple[VendorRunnerTemplateProfile, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorRunnerTemplateDriftOutput:
        exit_code = payload.get("exit_code")
        return cls(
            suite_name=_string(payload.get("suite_name")),
            exit_code=exit_code if isinstance(exit_code, int) else None,
            profiles=tuple(
                VendorRunnerTemplateProfile.from_mapping(row)
                for row in payload.get("profiles", ())
                if isinstance(row, Mapping)
            ),
        )


@dataclass(frozen=True)
class TargetRadarBackendResult:
    backend: str
    status: str
    track_reports: int | None
    range_delta_m: float | int | None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> TargetRadarBackendResult:
        track_reports = payload.get("track_reports")
        range_delta_m = payload.get("range_delta_m")
        return cls(
            backend=_string(payload.get("backend")),
            status=_string(payload.get("status")),
            track_reports=track_reports if isinstance(track_reports, int) else None,
            range_delta_m=range_delta_m if isinstance(range_delta_m, (int, float)) else None,
        )


@dataclass(frozen=True)
class TargetRadarBackendMatrixSummary:
    suite_name: str
    passed: int | None
    skipped: int | None
    failed: int | None
    results: tuple[TargetRadarBackendResult, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> TargetRadarBackendMatrixSummary:
        passed = payload.get("passed")
        skipped = payload.get("skipped")
        failed = payload.get("failed")
        return cls(
            suite_name=_string(payload.get("suite_name")),
            passed=passed if isinstance(passed, int) else None,
            skipped=skipped if isinstance(skipped, int) else None,
            failed=failed if isinstance(failed, int) else None,
            results=tuple(
                TargetRadarBackendResult.from_mapping(row)
                for row in payload.get("results", ())
                if isinstance(row, Mapping)
            ),
        )


@dataclass(frozen=True)
class AnalyzeSpecsOutput:
    out: str
    zip_path: str
    java_rti_unique: int | None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> AnalyzeSpecsOutput:
        java_rti_unique = payload.get("java_rti_unique")
        return cls(
            out=_string(payload.get("out")),
            zip_path=_string(payload.get("zip")),
            java_rti_unique=java_rti_unique if isinstance(java_rti_unique, int) else None,
        )


@dataclass(frozen=True)
class VendorRuntimeStatusSummary:
    suite_name: str
    lane: str
    overall_classification: str
    exit_code: int | None
    blocked_vendors: tuple[str, ...]
    ready_vendors: tuple[str, ...]
    unexpected_failure_vendors: tuple[str, ...]
    recommended_next_steps: dict[str, tuple[str, ...]]
    artifact_dir: str
    vendors: tuple["VendorRuntimeVendorRow", ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorRuntimeStatusSummary:
        exit_code = payload.get("exit_code")
        return cls(
            suite_name=_string(payload.get("suite_name")),
            lane=_string(payload.get("lane")),
            overall_classification=_string(payload.get("overall_classification")),
            exit_code=exit_code if isinstance(exit_code, int) else None,
            blocked_vendors=_string_tuple(payload.get("blocked_vendors")),
            ready_vendors=_string_tuple(payload.get("ready_vendors")),
            unexpected_failure_vendors=_string_tuple(payload.get("unexpected_failure_vendors")),
            recommended_next_steps={
                _string(key): _string_tuple(value)
                for key, value in _mapping(payload.get("recommended_next_steps")).items()
            },
            artifact_dir=_string(payload.get("artifact_dir")),
            vendors=tuple(
                VendorRuntimeVendorRow.from_mapping(row)
                for row in payload.get("vendors", ())
                if isinstance(row, Mapping)
            ),
        )


@dataclass(frozen=True)
class VendorParityArtifactsSummary:
    suite_name: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorParityArtifactsSummary:
        return cls(suite_name=_string(payload.get("suite_name")))


@dataclass(frozen=True)
class VendorRuntimeVendorRow:
    artifact_path: str
    blocked_reason: str
    blocked_checks: tuple[PreflightCheckRow, ...]
    required_markers: dict[str, str]
    required_ports: dict[str, PortStatus]
    next_steps: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorRuntimeVendorRow:
        return cls(
            artifact_path=_string(payload.get("artifact_path")),
            blocked_reason=_string(payload.get("blocked_reason")),
            blocked_checks=tuple(
                PreflightCheckRow.from_mapping(row)
                for row in payload.get("blocked_checks", ())
                if isinstance(row, Mapping)
            ),
            required_markers={
                _string(key): _string(value)
                for key, value in _mapping(payload.get("required_markers")).items()
            },
            required_ports={
                _string(key): PortStatus.from_mapping(_mapping(value))
                for key, value in _mapping(payload.get("required_ports")).items()
            },
            next_steps=_string_tuple(payload.get("next_steps")),
        )


@dataclass(frozen=True)
class PromotionReviewRow:
    profile: str
    gap_status: str
    review_decision: str
    next_action: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> PromotionReviewRow:
        return cls(
            profile=_string(payload.get("profile")),
            gap_status=_string(payload.get("gap_status")),
            review_decision=_string(payload.get("review_decision")),
            next_action=_string(payload.get("next_action")),
        )


@dataclass(frozen=True)
class VendorProbePromotionReviewSummary:
    suite_name: str
    candidate_count: int | None
    profiles: tuple[PromotionReviewRow, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorProbePromotionReviewSummary:
        candidate_count = payload.get("candidate_count")
        return cls(
            suite_name=_string(payload.get("suite_name")),
            candidate_count=candidate_count if isinstance(candidate_count, int) else None,
            profiles=tuple(
                PromotionReviewRow.from_mapping(row)
                for row in payload.get("profiles", ())
                if isinstance(row, Mapping)
            ),
        )

    def profile_row(self, profile: str) -> PromotionReviewRow:
        return next(row for row in self.profiles if row.profile == profile)


@dataclass(frozen=True)
class ParityProfileSummary:
    vendor_family: str
    evidence_tier: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> ParityProfileSummary:
        return cls(
            vendor_family=_string(payload.get("vendor_family")),
            evidence_tier=_string(payload.get("evidence_tier")),
        )


@dataclass(frozen=True)
class ParityCommandSummary:
    command: str
    evidence_tier: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> ParityCommandSummary:
        return cls(
            command=_string(payload.get("command")),
            evidence_tier=_string(payload.get("evidence_tier")),
        )


@dataclass(frozen=True)
class VendorParityArtifactsFullSummary:
    suite_name: str
    artifact_count: int | None
    missing_required_count: int | None
    profiles: tuple[ParityProfileSummary, ...]
    profile_commands: tuple[ParityCommandSummary, ...]
    preflight: dict[str, object]
    runtime_status: dict[str, object]
    gap_profiles: dict[str, VendorGapProfile | None]
    probe_stability: dict[str, VendorProbeStabilitySummary | None]
    probe_promotion_review: VendorProbePromotionReviewSummary | None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorParityArtifactsFullSummary:
        artifact_count = payload.get("artifact_count")
        missing_required_count = payload.get("missing_required_count")
        gap_profiles = {
            _string(key): (
                VendorGapProfile.from_mapping(value) if isinstance(value, Mapping) else None
            )
            for key, value in _mapping(payload.get("gap_profiles")).items()
        }
        probe_stability = {
            _string(key): (
                VendorProbeStabilitySummary.from_mapping(value) if isinstance(value, Mapping) else None
            )
            for key, value in _mapping(payload.get("probe_stability")).items()
        }
        promotion_review_payload = payload.get("probe_promotion_review")
        return cls(
            suite_name=_string(payload.get("suite_name")),
            artifact_count=artifact_count if isinstance(artifact_count, int) else None,
            missing_required_count=missing_required_count if isinstance(missing_required_count, int) else None,
            profiles=tuple(
                ParityProfileSummary.from_mapping(row)
                for row in payload.get("profiles", ())
                if isinstance(row, Mapping)
            ),
            profile_commands=tuple(
                ParityCommandSummary.from_mapping(row)
                for row in payload.get("profile_commands", ())
                if isinstance(row, Mapping)
            ),
            preflight=dict(_mapping(payload.get("preflight"))),
            runtime_status=dict(_mapping(payload.get("runtime_status"))),
            gap_profiles=gap_profiles,
            probe_stability=probe_stability,
            probe_promotion_review=(
                VendorProbePromotionReviewSummary.from_mapping(promotion_review_payload)
                if isinstance(promotion_review_payload, Mapping)
                else None
            ),
        )


@dataclass(frozen=True)
class VendorRuntimeCiStateSummary:
    profile: str
    classification: str
    exit_code: int | None
    required_vars: tuple[str, ...]
    required_markers: tuple[str, ...]
    checks: tuple[PreflightCheckRow, ...]
    compatibility_vars: dict[str, str]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorRuntimeCiStateSummary:
        exit_code = payload.get("exit_code")
        return cls(
            profile=_string(payload.get("profile")),
            classification=_string(payload.get("classification")),
            exit_code=exit_code if isinstance(exit_code, int) else None,
            required_vars=_string_tuple(payload.get("required_vars")),
            required_markers=_string_tuple(payload.get("required_markers")),
            checks=tuple(
                PreflightCheckRow.from_mapping(row)
                for row in payload.get("checks", ())
                if isinstance(row, Mapping)
            ),
            compatibility_vars={
                _string(key): _string(value)
                for key, value in _mapping(payload.get("compatibility_vars")).items()
            },
        )

    def check(self, name: str) -> PreflightCheckRow:
        return next(row for row in self.checks if row.name == name)


@dataclass(frozen=True)
class ComplianceArtifactSummary:
    row_count: int | None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> ComplianceArtifactSummary:
        row_count = payload.get("row_count")
        return cls(row_count=row_count if isinstance(row_count, int) else None)


@dataclass(frozen=True)
class ComplianceArtifactOutput:
    summary: ComplianceArtifactSummary

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> ComplianceArtifactOutput:
        return cls(summary=ComplianceArtifactSummary.from_mapping(_mapping(payload.get("summary"))))


@dataclass(frozen=True)
class BackendCatalogSummary:
    backend_count: int | None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> BackendCatalogSummary:
        backend_count = payload.get("backend_count")
        return cls(backend_count=backend_count if isinstance(backend_count, int) else None)


@dataclass(frozen=True)
class BackendDiscoveryCatalog:
    summary: BackendCatalogSummary
    backends: tuple[BackendCatalogRow, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> BackendDiscoveryCatalog:
        return cls(
            summary=BackendCatalogSummary.from_mapping(_mapping(payload.get("summary"))),
            backends=tuple(
                BackendCatalogRow.from_mapping(row)
                for row in payload.get("backends", ())
                if isinstance(row, Mapping)
            ),
        )


@dataclass(frozen=True)
class BackendDiscoveryOutput:
    catalog: BackendDiscoveryCatalog

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> BackendDiscoveryOutput:
        return cls(catalog=BackendDiscoveryCatalog.from_mapping(_mapping(payload.get("catalog"))))


@dataclass(frozen=True)
class BootstrapPlanOutput:
    extras: str
    profile: str
    workspace_packages: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> BootstrapPlanOutput:
        return cls(
            extras=_string(payload.get("extras")),
            profile=_string(payload.get("profile")),
            workspace_packages=_string_tuple(payload.get("workspace_packages")),
        )


@dataclass(frozen=True)
class BootstrapDoctorCheck:
    name: str
    status: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> BootstrapDoctorCheck:
        return cls(name=_string(payload.get("name")), status=_string(payload.get("status")))


@dataclass(frozen=True)
class BootstrapDoctorOutput:
    repo_root: str
    summary: str
    checks: tuple[BootstrapDoctorCheck, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> BootstrapDoctorOutput:
        return cls(
            repo_root=_string(payload.get("repo_root")),
            summary=_string(payload.get("summary")),
            checks=tuple(
                BootstrapDoctorCheck.from_mapping(row)
                for row in payload.get("checks", ())
                if isinstance(row, Mapping)
            ),
        )

    def check(self, name: str) -> BootstrapDoctorCheck:
        return next(row for row in self.checks if row.name == name)


@dataclass(frozen=True)
class PitchReproOutput:
    pitch_home: str
    launcher_mode: str
    docker_info_exit_code: int | None
    raw: Mapping[str, object]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> PitchReproOutput:
        docker_info_exit_code = payload.get("docker_info_exit_code")
        return cls(
            pitch_home=_string(payload.get("pitch_home")),
            launcher_mode=_string(payload.get("launcher_mode")),
            docker_info_exit_code=docker_info_exit_code if isinstance(docker_info_exit_code, int) else None,
            raw=dict(payload),
        )

    def has_key(self, name: str) -> bool:
        return name in self.raw


@dataclass(frozen=True)
class RecordedProfile:
    profile: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RecordedProfile:
        return cls(profile=_string(payload.get("profile")))


@dataclass(frozen=True)
class RecordedArgvCall:
    argv: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RecordedArgvCall:
        return cls(argv=_string_tuple(payload.get("argv")))


@dataclass(frozen=True)
class LabeledRecordedCall:
    label: str
    argv: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> LabeledRecordedCall:
        return cls(label=_string(payload.get("label")), argv=_string_tuple(payload.get("argv")))


@dataclass(frozen=True)
class RecordedProfileExitCode:
    profile: str
    exit_code: int | None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> RecordedProfileExitCode:
        exit_code = payload.get("exit_code")
        return cls(
            profile=_string(payload.get("profile")),
            exit_code=exit_code if isinstance(exit_code, int) else None,
        )


@dataclass(frozen=True)
class VendorProbeAttempt:
    exit_code: int | None

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorProbeAttempt:
        exit_code = payload.get("exit_code")
        return cls(exit_code=exit_code if isinstance(exit_code, int) else None)


@dataclass(frozen=True)
class VendorProbeStabilitySummary:
    profile: str
    evidence_tier: str
    command: str
    executor_command: str
    repeat_count: int | None
    attempt_count: int | None
    success_count: int | None
    failure_count: int | None
    stable: bool
    promotion_readiness: str
    attempts: tuple[VendorProbeAttempt, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorProbeStabilitySummary:
        repeat_count = payload.get("repeat_count")
        attempt_count = payload.get("attempt_count")
        success_count = payload.get("success_count")
        failure_count = payload.get("failure_count")
        return cls(
            profile=_string(payload.get("profile")),
            evidence_tier=_string(payload.get("evidence_tier")),
            command=_string(payload.get("command")),
            executor_command=_string(payload.get("executor_command")),
            repeat_count=repeat_count if isinstance(repeat_count, int) else None,
            attempt_count=attempt_count if isinstance(attempt_count, int) else None,
            success_count=success_count if isinstance(success_count, int) else None,
            failure_count=failure_count if isinstance(failure_count, int) else None,
            stable=bool(payload.get("stable")),
            promotion_readiness=_string(payload.get("promotion_readiness")),
            attempts=tuple(
                VendorProbeAttempt.from_mapping(row)
                for row in payload.get("attempts", ())
                if isinstance(row, Mapping)
            ),
        )


@dataclass(frozen=True)
class VendorGapProfile:
    profile: str
    classification: str
    vendor: str
    area: str
    status: str
    operator_state: str
    blocker_summary: str
    operator_artifact_refs: tuple[str, ...]
    next_steps: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> VendorGapProfile:
        return cls(
            profile=_string(payload.get("profile")),
            classification=_string(payload.get("classification")),
            vendor=_string(payload.get("vendor")),
            area=_string(payload.get("area")),
            status=_string(payload.get("status")),
            operator_state=_string(payload.get("operator_state")),
            blocker_summary=_string(payload.get("blocker_summary")),
            operator_artifact_refs=_string_tuple(payload.get("operator_artifact_refs")),
            next_steps=_string_tuple(payload.get("next_steps")),
        )
