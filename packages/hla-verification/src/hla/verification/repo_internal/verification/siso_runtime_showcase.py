"""Executable runtime showcase scenarios for high-value SISO FOM families."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
import csv
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hla.backends.common import RecordingFederateAmbassador
from hla.backends.python1516e import InMemoryRTIEngine
from hla.runtime.factory import create_rti_ambassador as create_rti_ambassador_2010
from hla.runtime.rti1516_2025_factory import create_rti_ambassador as create_rti_ambassador_2025
from hla.rti1516e.enums import CallbackModel as CallbackModel2010, ResignAction as ResignAction2010
from hla.rti1516_2025.enums import CallbackModel as CallbackModel2025, ResignAction as ResignAction2025
from hla.verification.repo_internal.fom_inventory import default_load_set_for_family
from hla.verification.startup import FederationStartupConfig, connect_create_join, synchronize_ready_to_run


@dataclass(frozen=True)
class ShowcasePaths:
    output_dir: Path
    summary_json: Path
    scenario_csv: Path
    backend_matrix_csv: Path
    scenario_manifest_json: Path
    report_markdown: Path


@dataclass(frozen=True)
class RuntimeSpec:
    edition: str
    callback_model: Any
    resign_action: Any


@dataclass(frozen=True)
class TopologySpec:
    slug: str
    federate_count: int


RUNTIME_2010 = RuntimeSpec("2010", CallbackModel2010.HLA_EVOKED, ResignAction2010.DELETE_OBJECTS)
RUNTIME_2025 = RuntimeSpec("2025", CallbackModel2025.HLA_EVOKED, ResignAction2025.DELETE_OBJECTS)
TOPOLOGIES = (
    TopologySpec("micro-2", 2),
    TopologySpec("squad-5", 5),
    TopologySpec("constellation-10", 10),
)
FAMILIES = ("link16", "rpr", "space")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[7]


def _call_service(target: Any, snake_name: str, camel_name: str, *args: Any) -> Any:
    method = getattr(target, snake_name, None) or getattr(target, camel_name)
    return method(*args)


def _runtime_for_edition(edition: str) -> RuntimeSpec:
    if edition == "2010":
        return RUNTIME_2010
    if edition == "2025":
        return RUNTIME_2025
    raise KeyError(f"Unknown runtime edition {edition!r}")


def _topology_for_slug(slug: str) -> TopologySpec:
    for topology in TOPOLOGIES:
        if topology.slug == slug:
            return topology
    raise KeyError(f"Unknown topology slug {slug!r}")


def _create_rtis(runtime: RuntimeSpec, count: int, *, backend: str | None = None) -> list[Any]:
    if runtime.edition == "2010":
        if backend not in {None, "", "python1516e"}:
            return [create_rti_ambassador_2010(backend=backend) for _ in range(count)]
        engine = InMemoryRTIEngine()
        return [
            create_rti_ambassador_2010(backend="python1516e", engine=engine)
            for _ in range(count)
        ]
    return [
        create_rti_ambassador_2025(backend=backend or "python1516_2025")
        for _ in range(count)
    ]


def _drain(runtime: RuntimeSpec, *rtis: Any, rounds: int = 25) -> None:
    for _ in range(rounds):
        for rti in rtis:
            if runtime.edition == "2010":
                rti.evoke_multiple_callbacks(0.0, 0.0)
            else:
                rti.evokeMultipleCallbacks(0.0, 0.0)


def _dedupe_paths(paths: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        ordered.append(path)
    return tuple(ordered)


def _family_paths(
    family: str,
    *,
    include_fragment: str | None = None,
    exclude_fragment: str | None = None,
) -> tuple[str, ...]:
    records = default_load_set_for_family(family)
    selected = [
        record.path
        for record in records
        if (include_fragment is None or include_fragment in record.path)
        and (exclude_fragment is None or exclude_fragment not in record.path)
    ]
    repo_root = _repo_root()
    resolved: list[str] = []
    for path_text in (selected or [record.path for record in records]):
        path = Path(path_text)
        resolved.append(str(path if path.is_absolute() else (repo_root / path).resolve()))
    return _dedupe_paths(resolved)


def _packet_paths(packet_id: str) -> tuple[str, ...]:
    if packet_id == "link16-rpr2-integrated":
        return _family_paths("siso-rpr-2.0", include_fragment="Link 16")
    if packet_id == "rpr3-annex-a-normative":
        return _family_paths(
            "siso-rpr-3.0",
            include_fragment="Annex A Files Normative",
            exclude_fragment="Annex B Files Informative",
        )
    if packet_id == "rpr3-merged-informative-1516-2010":
        return _family_paths("siso-rpr-3.0", include_fragment="1516-2010")
    if packet_id == "space-fom-core":
        return _family_paths("siso-space-fom")
    raise KeyError(f"Unknown packet id {packet_id!r}")


def _source_packet_for_family(family: str, edition: str) -> str:
    if family == "link16":
        return "link16-rpr2-integrated"
    if family == "rpr":
        return "rpr3-annex-a-normative" if edition == "2025" else "rpr3-merged-informative-1516-2010"
    if family == "space":
        return "space-fom-core"
    raise KeyError(f"Unknown family {family!r}")


def _story_for_family(family: str, topology: TopologySpec) -> str:
    if family == "link16":
        return (
            "Link 16 originators publish RadioTransmitter state and JTIDS/RTTAB traffic to a shared observer set."
            if topology.federate_count == 2
            else "Multiple Link 16 originators publish RadioTransmitter state and JTIDS/RTTAB traffic to a shared observer set."
        )
    if family == "rpr":
        return (
            "A bridge owner and tactical observer exercise WeaponFire and MunitionDetonation flow over the RPR packet."
            if topology.federate_count == 2
            else "A bridge owner, multiple shooters, and observers exercise WeaponFire and MunitionDetonation flow over the RPR packet."
        )
    if family == "space":
        return (
            "A frame authority and observer propagate reference-frame and orbital state through the Space FOM core."
            if topology.federate_count == 2
            else "A frame authority, multiple entity producers, and observers propagate reference-frame and orbital state through the Space FOM core."
        )
    raise KeyError(f"Unknown family {family!r}")


def _participant_roles(family: str, topology: TopologySpec) -> list[str]:
    count = topology.federate_count
    sender_count = _sender_count(count)
    if family == "link16":
        roles = [f"originator-{idx}" for idx in range(1, sender_count + 1)]
        roles.extend(f"observer-{idx}" for idx in range(1, count - sender_count + 1))
        return roles
    if family == "rpr":
        if count == 2:
            return ["bridge-owner-shooter", "tactical-observer"]
        shooter_count = _sender_count(count)
        roles = ["bridge-owner"]
        roles.extend(f"shooter-{idx}" for idx in range(1, shooter_count + 1))
        observer_count = count - 1 - shooter_count
        roles.extend(f"observer-{idx}" for idx in range(1, observer_count + 1))
        return roles
    if family == "space":
        if count == 2:
            return ["frame-authority-producer", "observer"]
        producer_count = _sender_count(count)
        roles = ["frame-authority"]
        roles.extend(f"producer-{idx}" for idx in range(1, producer_count + 1))
        observer_count = count - 1 - producer_count
        roles.extend(f"observer-{idx}" for idx in range(1, observer_count + 1))
        return roles
    raise KeyError(f"Unknown family {family!r}")


def _family_runner(family: str) -> Any:
    if family == "link16":
        return _run_link16_scenario
    if family == "rpr":
        return _run_rpr_scenario
    if family == "space":
        return _run_space_scenario
    raise KeyError(f"Unknown family {family!r}")


def _scenario_name(family: str, edition: str, topology_slug: str) -> str:
    if family == "link16":
        return f"link16-rpr2-integrated-{edition}-{topology_slug}"
    if family == "rpr":
        return f"rpr-runtime-{edition}-{topology_slug}"
    if family == "space":
        return f"space-fom-core-{edition}-{topology_slug}"
    raise KeyError(f"Unknown family {family!r}")


def _jsonable(value: Any) -> Any:
    if isinstance(value, bytes):
        decoded = value.decode("utf-8", errors="replace").rstrip("\x00")
        if decoded and all(character.isprintable() for character in decoded):
            return decoded
        return value.hex()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _tag_bytes(value: str) -> bytes:
    return value.encode("utf-8") + b"\x00"


def _rpr_tag_bytes(value: str) -> bytes:
    return b"00000000" + value.encode("utf-8") + b"\x00"


def _rpr_fixed_tag(sequence: int) -> bytes:
    return int(sequence).to_bytes(8, byteorder="big", signed=True) + b"\x01"


def _startup(
    runtime: RuntimeSpec,
    rtis: list[Any],
    federates: list[RecordingFederateAmbassador],
    *,
    federation_name: str,
    foms: tuple[str, ...],
    federate_type_prefix: str,
    lifecycle: list[str],
) -> None:
    for idx, (rti, federate) in enumerate(zip(rtis, federates, strict=True)):
        connect_create_join(
            rti,
            federate,
            FederationStartupConfig(
                federation_name=federation_name,
                federate_name=f"{federate_type_prefix}{idx + 1}",
                federate_type=federate_type_prefix,
                fom_modules=foms,
                callback_model=runtime.callback_model,
            ),
            create_federation=(idx == 0),
        )
    lifecycle.extend(["connected", "joined"])
    synchronize_ready_to_run(rtis, label="ReadyToRun")
    lifecycle.append("ready-to-run-synchronized")


def _shutdown(runtime: RuntimeSpec, federation_name: str, rtis: list[Any]) -> None:
    for rti in rtis:
        try:
            _call_service(
                rti,
                "resign_federation_execution",
                "resignFederationExecution",
                runtime.resign_action,
            )
        except Exception:
            pass
    try:
        _call_service(
            rtis[0],
            "destroy_federation_execution",
            "destroyFederationExecution",
            federation_name,
        )
    except Exception:
        pass
    for rti in reversed(rtis):
        try:
            rti.disconnect()
        except Exception:
            pass


def _sender_count(federate_count: int) -> int:
    if federate_count >= 10:
        return 3
    if federate_count >= 5:
        return 2
    return 1


def _subscriber_rtis(rtis: list[Any], sender_count: int, reserved_front: int = 0) -> list[Any]:
    return rtis[reserved_front + sender_count :]


def _subscriber_feds(
    federates: list[RecordingFederateAmbassador],
    sender_count: int,
    reserved_front: int = 0,
) -> list[RecordingFederateAmbassador]:
    return federates[reserved_front + sender_count :]


def _run_link16_scenario(runtime: RuntimeSpec, topology: TopologySpec, *, backend: str | None = None) -> dict[str, Any]:
    packet_id = "link16-rpr2-integrated"
    foms = _packet_paths(packet_id)
    rtis = _create_rtis(runtime, topology.federate_count, backend=backend)
    federates = [RecordingFederateAmbassador() for _ in rtis]
    federation_name = f"SisoLink16-{runtime.edition}-{topology.slug}-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []
    sender_count = _sender_count(topology.federate_count)
    monitor = federates[-1]
    jtids_signal = "HLAinteractionRoot.RadioSignal.RawBinaryRadioSignal.TDLBinaryRadioSignal.Link16RadioSignal.JTIDSMessageRadioSignal"
    rttab_signal = "HLAinteractionRoot.RadioSignal.RawBinaryRadioSignal.TDLBinaryRadioSignal.Link16RadioSignal.RTTABRadioSignal"
    try:
        _startup(
            runtime,
            rtis,
            federates,
            federation_name=federation_name,
            foms=foms,
            federate_type_prefix="Link16Federate",
            lifecycle=lifecycle,
        )
        object_class = _call_service(rtis[0], "get_object_class_handle", "getObjectClassHandle", "HLAobjectRoot.EmbeddedSystem.RadioTransmitter")
        attr_names = ("RadioIndex", "Frequency", "WorldLocation")
        attrs = {
            name: _call_service(rtis[0], "get_attribute_handle", "getAttributeHandle", object_class, name)
            for name in attr_names
        }
        for rti in rtis[:sender_count]:
            _call_service(rti, "publish_object_class_attributes", "publishObjectClassAttributes", object_class, set(attrs.values()))
        for rti in rtis[sender_count:]:
            _call_service(rti, "subscribe_object_class_attributes", "subscribeObjectClassAttributes", object_class, set(attrs.values()))
        jtids_class = _call_service(rtis[0], "get_interaction_class_handle", "getInteractionClassHandle", jtids_signal)
        jtids_params = {
            name: _call_service(rtis[0], "get_parameter_handle", "getParameterHandle", jtids_class, name)
            for name in ("NPGNumber", "NetNumber", "Link16Version", "JTIDSHeader", "TADILJMessage")
        }
        rttab_class = _call_service(rtis[0], "get_interaction_class_handle", "getInteractionClassHandle", rttab_signal)
        rttab_params = {
            name: _call_service(rtis[0], "get_parameter_handle", "getParameterHandle", rttab_class, name)
            for name in ("NPGNumber", "NetNumber", "Link16Version", "RTTAB")
        }
        for rti in rtis[:sender_count]:
            _call_service(rti, "publish_interaction_class", "publishInteractionClass", jtids_class)
            _call_service(rti, "publish_interaction_class", "publishInteractionClass", rttab_class)
        for rti in rtis[sender_count:]:
            _call_service(rti, "subscribe_interaction_class", "subscribeInteractionClass", jtids_class)
            _call_service(rti, "subscribe_interaction_class", "subscribeInteractionClass", rttab_class)
        lifecycle.append("publication-ready")

        for idx, rti in enumerate(rtis[:sender_count], start=1):
            transmitter = _call_service(rti, "register_object_instance", "registerObjectInstance", object_class, f"Link16Radio-{idx}")
            _call_service(
                rti,
                "update_attribute_values",
                "updateAttributeValues",
                transmitter,
                {
                    attrs["RadioIndex"]: str(idx).encode("utf-8"),
                    attrs["Frequency"]: str(969000000 + (idx * 1000)).encode("utf-8"),
                    attrs["WorldLocation"]: f"41.88,-87.63,{12000 + idx * 500}".encode("utf-8"),
                },
                _rpr_tag_bytes(f"link16-transmitter-state-{idx}"),
            )
            _call_service(
                rti,
                "send_interaction",
                "sendInteraction",
                jtids_class,
                {
                    jtids_params["NPGNumber"]: str(7 + idx).encode("utf-8"),
                    jtids_params["NetNumber"]: b"12",
                    jtids_params["Link16Version"]: b"BlockUpgrade2",
                    jtids_params["JTIDSHeader"]: f"header-{idx}".encode("utf-8"),
                    jtids_params["TADILJMessage"]: f"J3.2 AIR TRACK {idx}".encode("utf-8"),
                },
                _rpr_tag_bytes(f"link16-jtids-message-{idx}"),
            )
            _call_service(
                rti,
                "send_interaction",
                "sendInteraction",
                rttab_class,
                {
                    rttab_params["NPGNumber"]: str(7 + idx).encode("utf-8"),
                    rttab_params["NetNumber"]: b"12",
                    rttab_params["Link16Version"]: b"BlockUpgrade2",
                    rttab_params["RTTAB"]: f"request-time-slot-reblock-{idx}".encode("utf-8"),
                },
                _rpr_tag_bytes(f"link16-rttab-{idx}"),
            )
        _drain(runtime, *rtis)
        lifecycle.append("message-traffic-observed")

        discoveries = monitor.callbacks_named("discoverObjectInstance")
        reflections = monitor.callbacks_named("reflectAttributeValues")
        receives = monitor.callbacks_named("receiveInteraction")
        delivered_tags = [record.args[2] for record in receives]
        expected_tags = [
            _rpr_tag_bytes(f"link16-jtids-message-{idx}")
            for idx in range(1, sender_count + 1)
        ] + [
            _rpr_tag_bytes(f"link16-rttab-{idx}")
            for idx in range(1, sender_count + 1)
        ]
        execution_complete = (
            len(discoveries) >= sender_count
            and len(reflections) >= sender_count
            and set(expected_tags).issubset(set(delivered_tags))
        )
        return {
            "scenario": f"link16-rpr2-integrated-{runtime.edition}-{topology.slug}",
            "family": "link16",
            "source_packet": packet_id,
            "runtime_edition": runtime.edition,
            "topology": topology.slug,
            "federate_count": topology.federate_count,
            "status": "lifecycle-green" if execution_complete else "failed",
            "federation_name": federation_name,
            "fom_modules": [Path(path).name for path in foms],
            "federates": [f"Link16Federate{idx + 1}" for idx in range(topology.federate_count)],
            "lifecycle": lifecycle,
            "object_class": "HLAobjectRoot.EmbeddedSystem.RadioTransmitter",
            "interaction_classes": [jtids_signal, rttab_signal],
            "discoveries": len(discoveries),
            "reflections": len(reflections),
            "interactions": len(receives),
            "delivered_tags": [_jsonable(tag) for tag in delivered_tags],
            "key_outcome": "multiple Link 16 radio publishers reflected state and delivered JTIDS/RTTAB traffic to shared observers",
            "execution_complete": execution_complete,
        }
    finally:
        _shutdown(runtime, federation_name, rtis)


def _run_rpr_scenario(runtime: RuntimeSpec, topology: TopologySpec, *, backend: str | None = None) -> dict[str, Any]:
    packet_id = "rpr3-annex-a-normative" if runtime.edition == "2025" else "rpr3-merged-informative-1516-2010"
    foms = _packet_paths(packet_id)
    rtis = _create_rtis(runtime, topology.federate_count, backend=backend)
    federates = [RecordingFederateAmbassador() for _ in rtis]
    federation_name = f"SisoRpr-{runtime.edition}-{topology.slug}-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []
    shooter_count = _sender_count(topology.federate_count) if topology.federate_count > 2 else 0
    bridge_owner = rtis[0]
    monitor = federates[-1]
    object_class_name = "HLAobjectRoot.EnvironmentObject.PointObject.BridgeObject"
    fire_name = "HLAinteractionRoot.Fire.WeaponFire"
    detonation_name = "HLAinteractionRoot.Detonation.MunitionDetonation"
    try:
        _startup(
            runtime,
            rtis,
            federates,
            federation_name=federation_name,
            foms=foms,
            federate_type_prefix="RprFederate",
            lifecycle=lifecycle,
        )
        object_class = _call_service(bridge_owner, "get_object_class_handle", "getObjectClassHandle", object_class_name)
        attrs = {
            name: _call_service(bridge_owner, "get_attribute_handle", "getAttributeHandle", object_class, name)
            for name in ("ObjectIdentifier", "Location", "Damage")
        }
        _call_service(bridge_owner, "publish_object_class_attributes", "publishObjectClassAttributes", object_class, set(attrs.values()))
        for rti in rtis[1:]:
            _call_service(rti, "subscribe_object_class_attributes", "subscribeObjectClassAttributes", object_class, set(attrs.values()))
        fire_class = _call_service(bridge_owner, "get_interaction_class_handle", "getInteractionClassHandle", fire_name)
        fire_params = {
            name: _call_service(bridge_owner, "get_parameter_handle", "getParameterHandle", fire_class, name)
            for name in ("FiringObjectIdentifier", "TargetObjectIdentifier", "EventIdentifier", "MunitionType", "QuantityFired")
        }
        detonation_class = _call_service(bridge_owner, "get_interaction_class_handle", "getInteractionClassHandle", detonation_name)
        detonation_params = {
            name: _call_service(bridge_owner, "get_parameter_handle", "getParameterHandle", detonation_class, name)
            for name in ("EventIdentifier", "DetonationLocation", "DetonationResultCode", "TargetObjectIdentifier", "QuantityFired")
        }
        shooter_rtis = rtis[1 : 1 + shooter_count] if shooter_count else [bridge_owner]
        observer_rtis = rtis[1 + shooter_count :] if shooter_count else rtis[1:]
        for rti in shooter_rtis:
            _call_service(rti, "publish_interaction_class", "publishInteractionClass", fire_class)
            _call_service(rti, "publish_interaction_class", "publishInteractionClass", detonation_class)
        for rti in observer_rtis:
            _call_service(rti, "subscribe_interaction_class", "subscribeInteractionClass", fire_class)
            _call_service(rti, "subscribe_interaction_class", "subscribeInteractionClass", detonation_class)
        lifecycle.append("engagement-publication-ready")

        bridge = _call_service(bridge_owner, "register_object_instance", "registerObjectInstance", object_class, "Bridge-Alpha")
        _call_service(
            bridge_owner,
            "update_attribute_values",
            "updateAttributeValues",
            bridge,
            {
                attrs["ObjectIdentifier"]: b"bridge-alpha",
                attrs["Location"]: b"41.88,-87.63,0",
                attrs["Damage"]: b"minor",
            },
            _rpr_fixed_tag(0),
        )
        active_shooter_count = len(shooter_rtis)
        for idx, rti in enumerate(shooter_rtis, start=1):
            _call_service(
                rti,
                "send_interaction",
                "sendInteraction",
                fire_class,
                {
                    fire_params["FiringObjectIdentifier"]: f"shooter-{idx}".encode("utf-8"),
                    fire_params["TargetObjectIdentifier"]: b"bridge-alpha",
                    fire_params["EventIdentifier"]: f"engagement-{idx:03d}".encode("utf-8"),
                    fire_params["MunitionType"]: b"guided-munition",
                    fire_params["QuantityFired"]: str(idx).encode("utf-8"),
                },
                _rpr_fixed_tag(idx),
            )
            _call_service(
                rti,
                "send_interaction",
                "sendInteraction",
                detonation_class,
                {
                    detonation_params["EventIdentifier"]: f"engagement-{idx:03d}".encode("utf-8"),
                    detonation_params["DetonationLocation"]: b"41.88,-87.63,0",
                    detonation_params["DetonationResultCode"]: b"detonation",
                    detonation_params["TargetObjectIdentifier"]: b"bridge-alpha",
                    detonation_params["QuantityFired"]: str(idx).encode("utf-8"),
                },
                _rpr_fixed_tag(100 + idx),
            )
        _drain(runtime, *rtis)
        lifecycle.append("engagement-chain-observed")

        discoveries = monitor.callbacks_named("discoverObjectInstance")
        reflections = monitor.callbacks_named("reflectAttributeValues")
        receives = monitor.callbacks_named("receiveInteraction")
        delivered_tags = [record.args[2] for record in receives]
        expected_tags = [
            _rpr_fixed_tag(idx)
            for idx in range(1, active_shooter_count + 1)
        ] + [
            _rpr_fixed_tag(100 + idx)
            for idx in range(1, active_shooter_count + 1)
        ]
        execution_complete = (
            len(discoveries) >= 1
            and len(reflections) >= 1
            and set(expected_tags).issubset(set(delivered_tags))
        )
        return {
            "scenario": f"rpr-runtime-{runtime.edition}-{topology.slug}",
            "family": "rpr",
            "source_packet": packet_id,
            "runtime_edition": runtime.edition,
            "topology": topology.slug,
            "federate_count": topology.federate_count,
            "status": "lifecycle-green" if execution_complete else "failed",
            "federation_name": federation_name,
            "fom_modules": [Path(path).name for path in foms],
            "federates": [f"RprFederate{idx + 1}" for idx in range(topology.federate_count)],
            "lifecycle": lifecycle,
            "object_class": object_class_name,
            "interaction_classes": [fire_name, detonation_name],
            "discoveries": len(discoveries),
            "reflections": len(reflections),
            "interactions": len(receives),
            "delivered_tags": [_jsonable(tag) for tag in delivered_tags],
            "key_outcome": "bridge state and multi-shooter fire/detonation chains reached the tactical observer set",
            "execution_complete": execution_complete,
        }
    finally:
        _shutdown(runtime, federation_name, rtis)


def _run_space_scenario(runtime: RuntimeSpec, topology: TopologySpec, *, backend: str | None = None) -> dict[str, Any]:
    packet_id = "space-fom-core"
    foms = _packet_paths(packet_id)
    rtis = _create_rtis(runtime, topology.federate_count, backend=backend)
    federates = [RecordingFederateAmbassador() for _ in rtis]
    federation_name = f"SisoSpace-{runtime.edition}-{topology.slug}-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []
    producer_count = _sender_count(topology.federate_count) if topology.federate_count > 2 else 0
    frame_authority = rtis[0]
    monitor = federates[-1]
    reference_frame_class_name = "HLAobjectRoot.ReferenceFrame"
    entity_class_name = "HLAobjectRoot.PhysicalEntity.DynamicalEntity"
    try:
        _startup(
            runtime,
            rtis,
            federates,
            federation_name=federation_name,
            foms=foms,
            federate_type_prefix="SpaceFederate",
            lifecycle=lifecycle,
        )
        frame_class = _call_service(frame_authority, "get_object_class_handle", "getObjectClassHandle", reference_frame_class_name)
        frame_attrs = {
            name: _call_service(frame_authority, "get_attribute_handle", "getAttributeHandle", frame_class, name)
            for name in ("name", "parent_name", "state")
        }
        entity_class = _call_service(frame_authority, "get_object_class_handle", "getObjectClassHandle", entity_class_name)
        entity_attrs = {
            name: _call_service(frame_authority, "get_attribute_handle", "getAttributeHandle", entity_class, name)
            for name in ("name", "type", "status", "parent_reference_frame", "state")
        }
        _call_service(frame_authority, "publish_object_class_attributes", "publishObjectClassAttributes", frame_class, set(frame_attrs.values()))
        producer_rtis = rtis[1 : 1 + producer_count] if producer_count else [frame_authority]
        observer_rtis = rtis[1 + producer_count :] if producer_count else rtis[1:]
        for rti in producer_rtis:
            _call_service(rti, "publish_object_class_attributes", "publishObjectClassAttributes", entity_class, set(entity_attrs.values()))
        for rti in observer_rtis:
            _call_service(rti, "subscribe_object_class_attributes", "subscribeObjectClassAttributes", frame_class, set(frame_attrs.values()))
            _call_service(rti, "subscribe_object_class_attributes", "subscribeObjectClassAttributes", entity_class, set(entity_attrs.values()))
        lifecycle.append("space-publication-ready")

        frame = _call_service(frame_authority, "register_object_instance", "registerObjectInstance", frame_class, "EarthMJ2000Eq")
        _call_service(
            frame_authority,
            "update_attribute_values",
            "updateAttributeValues",
            frame,
            {
                frame_attrs["name"]: b"EarthMJ2000Eq",
                frame_attrs["parent_name"]: b"SolarSystemBarycentric",
                frame_attrs["state"]: b"frame-state-epoch-1000",
            },
            _tag_bytes("space-reference-frame"),
        )
        active_producer_count = len(producer_rtis)
        for idx, rti in enumerate(producer_rtis, start=1):
            entity = _call_service(rti, "register_object_instance", "registerObjectInstance", entity_class, f"Scout-{idx}")
            _call_service(
                rti,
                "update_attribute_values",
                "updateAttributeValues",
                entity,
                {
                    entity_attrs["name"]: f"Scout-{idx}".encode("utf-8"),
                    entity_attrs["type"]: b"spacecraft",
                    entity_attrs["status"]: b"tracking",
                    entity_attrs["parent_reference_frame"]: b"EarthMJ2000Eq",
                    entity_attrs["state"]: f"r={7000 + idx * 20}km,v=7.{5 - (idx % 2)}kmps".encode("utf-8"),
                },
                _tag_bytes(f"space-dynamics-state-{idx}"),
            )
            _call_service(
                rti,
                "update_attribute_values",
                "updateAttributeValues",
                entity,
                {
                    entity_attrs["status"]: b"maneuvering",
                    entity_attrs["state"]: f"r={7020 + idx * 20}km,v=7.{4 + (idx % 2)}kmps".encode("utf-8"),
                },
                _tag_bytes(f"space-dynamics-update-{idx}"),
            )
        _drain(runtime, *rtis)
        lifecycle.append("space-state-reflected")

        discoveries = monitor.callbacks_named("discoverObjectInstance")
        reflections = monitor.callbacks_named("reflectAttributeValues")
        execution_complete = (
            len(discoveries) >= 1 + active_producer_count
            and len(reflections) >= 1 + (active_producer_count * 2)
        )
        return {
            "scenario": f"space-fom-core-{runtime.edition}-{topology.slug}",
            "family": "space",
            "source_packet": packet_id,
            "runtime_edition": runtime.edition,
            "topology": topology.slug,
            "federate_count": topology.federate_count,
            "status": "lifecycle-green" if execution_complete else "failed",
            "federation_name": federation_name,
            "fom_modules": [Path(path).name for path in foms],
            "federates": [f"SpaceFederate{idx + 1}" for idx in range(topology.federate_count)],
            "lifecycle": lifecycle,
            "object_classes": [reference_frame_class_name, entity_class_name],
            "discoveries": len(discoveries),
            "reflections": len(reflections),
            "interactions": 0,
            "delivered_tags": [],
            "key_outcome": "reference frame plus multi-entity orbital state updates propagated across the observer set",
            "execution_complete": execution_complete,
        }
    finally:
        _shutdown(runtime, federation_name, rtis)


def build_siso_runtime_showcase_manifest() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for runtime in (RUNTIME_2010, RUNTIME_2025):
        for topology in TOPOLOGIES:
            for family in FAMILIES:
                scenario = _scenario_name(family, runtime.edition, topology.slug)
                source_packet = _source_packet_for_family(family, runtime.edition)
                backend_row = _backend_matrix_row(
                    {
                        "scenario": scenario,
                        "family": family,
                        "source_packet": source_packet,
                        "runtime_edition": runtime.edition,
                        "topology": topology.slug,
                        "federate_count": topology.federate_count,
                    }
                )
                roles = _participant_roles(family, topology)
                rows.append(
                    {
                        "scenario": scenario,
                        "family": family,
                        "runtime_edition": runtime.edition,
                        "topology": topology.slug,
                        "federate_count": topology.federate_count,
                        "source_packet": source_packet,
                        "fom_modules": [Path(path).name for path in _packet_paths(source_packet)],
                        "story": _story_for_family(family, topology),
                        "participant_roles": roles,
                        "role_count": len(roles),
                        "python_backend": backend_row["python_backend"],
                        "pitch_2010_profiles": [item for item in backend_row["pitch_2010_profiles"].split(",") if item],
                        "pitch_202x_profiles": [item for item in backend_row["pitch_202x_profiles"].split(",") if item],
                        "vendor_status": backend_row["vendor_status"],
                        "vendor_notes": backend_row["vendor_notes"],
                    }
                )
    return {
        "schema_version": "siso-runtime-showcase-manifest-v0.1",
        "scenario_count": len(rows),
        "families": list(FAMILIES),
        "runtime_editions": ["2010", "2025"],
        "topologies": [topology.slug for topology in TOPOLOGIES],
        "scenarios": rows,
    }


def load_siso_runtime_showcase_manifest(manifest_path: str | Path | None = None) -> dict[str, Any]:
    if manifest_path is None:
        return build_siso_runtime_showcase_manifest()
    path = Path(manifest_path)
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def run_siso_runtime_showcase_scenario(
    scenario: str,
    *,
    backend: str | None = None,
) -> dict[str, Any]:
    manifest = build_siso_runtime_showcase_manifest()
    selected = next((row for row in manifest["scenarios"] if row["scenario"] == scenario), None)
    if selected is None:
        raise KeyError(f"Unknown showcase scenario {scenario!r}")
    runtime = _runtime_for_edition(str(selected["runtime_edition"]))
    topology = _topology_for_slug(str(selected["topology"]))
    family = str(selected["family"])
    return _family_runner(family)(runtime, topology, backend=backend)


def run_siso_runtime_showcase() -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    for runtime in (RUNTIME_2010, RUNTIME_2025):
        for topology in TOPOLOGIES:
            scenarios.append(_run_link16_scenario(runtime, topology))
            scenarios.append(_run_rpr_scenario(runtime, topology))
            scenarios.append(_run_space_scenario(runtime, topology))
    backend_matrix = [_backend_matrix_row(row) for row in scenarios]
    scenario_manifest = build_siso_runtime_showcase_manifest()
    return {
        "suite_name": "siso-fom-runtime-showcase",
        "suite_version": "0.3",
        "status": "lifecycle-green" if all(row["execution_complete"] for row in scenarios) else "failed",
        "scenario_count": len(scenarios),
        "backend_matrix_count": len(backend_matrix),
        "manifest_scenario_count": int(scenario_manifest["scenario_count"]),
        "matrix_dimensions": {
            "families": ["link16", "rpr", "space"],
            "runtime_editions": ["2010", "2025"],
            "topologies": [topology.slug for topology in TOPOLOGIES],
            "federate_counts": [topology.federate_count for topology in TOPOLOGIES],
        },
        "scenarios": scenarios,
        "backend_matrix": backend_matrix,
        "scenario_manifest": scenario_manifest,
    }


def _write_csv(path: Path, fieldnames: list[str], rows: list[Mapping[str, Any]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _jsonable(row.get(field, "")) for field in fieldnames})
    return path


def _backend_matrix_row(row: Mapping[str, Any]) -> dict[str, Any]:
    edition = str(row["runtime_edition"])
    federate_count = int(row["federate_count"])
    topology = str(row["topology"])
    vendor_micro = federate_count == 2
    pitch_2010_profiles = "pitch-jpype,pitch-py4j" if edition == "2010" and vendor_micro else ""
    pitch_202x_profiles = "pitch-202x-jpype,pitch-202x-py4j" if edition == "2025" and vendor_micro else ""
    if edition == "2010":
        python_backend = "python1516e"
        vendor_status = "eligible" if vendor_micro else "python-only-topology"
        vendor_notes = (
            "Real Pitch 2010 parity lane is supported only for 2-federate micro scenarios."
            if vendor_micro
            else "Pitch 2010 is intentionally capped at the 2-federate parity lane; 5- and 10-federate runs stay on the in-process Python baseline."
        )
    else:
        python_backend = "python1516_2025"
        vendor_status = "bounded-eligible" if vendor_micro else "python-only-topology"
        vendor_notes = (
            "Pitch 202X wrappers are allowed only as a 2-federate bounded vendor-credence lane and do not constitute IEEE 1516.1-2025 conformance."
            if vendor_micro
            else "Pitch 202X is limited to bounded 2-federate checks; 5- and 10-federate 2025 showcases remain Python-only."
        )
    return {
        "scenario": row["scenario"],
        "family": row["family"],
        "source_packet": row["source_packet"],
        "runtime_edition": edition,
        "topology": topology,
        "federate_count": federate_count,
        "python_backend": python_backend,
        "python_execution_mode": "in-process",
        "pitch_2010_profiles": pitch_2010_profiles,
        "pitch_202x_profiles": pitch_202x_profiles,
        "vendor_micro_parity": vendor_micro,
        "vendor_status": vendor_status,
        "vendor_notes": vendor_notes,
    }


def _render_markdown(summary: Mapping[str, Any], paths: ShowcasePaths) -> str:
    lines = [
        "# SISO FOM Runtime Showcase",
        "",
        f"- suite: `{summary['suite_name']}`",
        f"- status: `{summary['status']}`",
        f"- scenarios: `{summary['scenario_count']}`",
        f"- summary json: `{paths.summary_json}`",
        f"- scenario csv: `{paths.scenario_csv}`",
        f"- backend matrix csv: `{paths.backend_matrix_csv}`",
        f"- scenario manifest json: `{paths.scenario_manifest_json}`",
        "",
        "## Backend Policy",
        "",
        "- `python1516e` and `python1516_2025` are the executable baseline for every scenario in the 18-row showcase matrix.",
        "- Real Pitch 2010 vendor routes are restricted to the `micro-2` parity lane via `pitch-jpype` and `pitch-py4j`.",
        "- Pitch `202X` routes are also restricted to the `micro-2` lane via `pitch-202x-jpype` and `pitch-202x-py4j`.",
        "- The `202X` Pitch lane is bounded vendor-credence only and must not be treated as IEEE `1516.1-2025` conformance proof.",
        "",
        "## Scenario Summary",
        "",
        "| Scenario | Family | Edition | Topology | Federates | Status | Discoveries | Reflections | Interactions | Key Outcome |",
        "| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for row in summary["scenarios"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row["scenario"]),
                    str(row["family"]),
                    str(row["runtime_edition"]),
                    str(row["topology"]),
                    str(row["federate_count"]),
                    str(row["status"]),
                    str(row.get("discoveries", 0)),
                    str(row.get("reflections", 0)),
                    str(row.get("interactions", 0)),
                    str(row["key_outcome"]),
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Backend Eligibility Matrix",
            "",
            "| Scenario | Edition | Family | Topology | Federates | Python | Pitch 2010 | Pitch 202X | Vendor Status |",
            "| --- | --- | --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in summary["backend_matrix"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    str(row["scenario"]),
                    str(row["runtime_edition"]),
                    str(row["family"]),
                    str(row["topology"]),
                    str(row["federate_count"]),
                    str(row["python_backend"]),
                    str(row["pitch_2010_profiles"] or "n/a"),
                    str(row["pitch_202x_profiles"] or "n/a"),
                    str(row["vendor_status"]),
                )
            )
            + " |"
        )
    for row in summary["scenarios"]:
        lines.extend(
            [
                "",
                f"## {row['scenario']}",
                "",
                f"- Family: `{row['family']}`",
                f"- Source packet: `{row['source_packet']}`",
                f"- Runtime edition: `{row['runtime_edition']}`",
                f"- Topology: `{row['topology']}`",
                f"- Federate count: `{row['federate_count']}`",
                f"- FOM modules: `{', '.join(row['fom_modules'])}`",
                f"- Federates: `{', '.join(row['federates'])}`",
                f"- Lifecycle: `{', '.join(row['lifecycle'])}`",
                f"- Key outcome: {row['key_outcome']}",
            ]
        )
        backend_row = next(item for item in summary["backend_matrix"] if item["scenario"] == row["scenario"])
        lines.extend(
            [
                f"- Python backend: `{backend_row['python_backend']}` ({backend_row['python_execution_mode']})",
                f"- Pitch 2010 profiles: `{backend_row['pitch_2010_profiles'] or 'n/a'}`",
                f"- Pitch 202X profiles: `{backend_row['pitch_202x_profiles'] or 'n/a'}`",
                f"- Vendor boundary: {backend_row['vendor_notes']}",
            ]
        )
        if row.get("interaction_classes"):
            lines.append(f"- Interaction classes: `{', '.join(row['interaction_classes'])}`")
        if row.get("object_class"):
            lines.append(f"- Object class: `{row['object_class']}`")
        if row.get("object_classes"):
            lines.append(f"- Object classes: `{', '.join(row['object_classes'])}`")
    return "\n".join(lines) + "\n"


def write_siso_runtime_showcase_artifacts(output_dir: str | Path) -> ShowcasePaths:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = ShowcasePaths(
        output_dir=out,
        summary_json=out / "siso_runtime_showcase_summary.json",
        scenario_csv=out / "siso_runtime_showcase_scenarios.csv",
        backend_matrix_csv=out / "siso_runtime_showcase_backend_matrix.csv",
        scenario_manifest_json=out / "siso_runtime_showcase_manifest.json",
        report_markdown=out / "siso_runtime_showcase_report.md",
    )
    summary = run_siso_runtime_showcase()
    paths.summary_json.write_text(json.dumps(_jsonable(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths.scenario_manifest_json.write_text(
        json.dumps(_jsonable(summary["scenario_manifest"]), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_csv(
        paths.scenario_csv,
        [
            "scenario",
            "family",
            "source_packet",
            "runtime_edition",
            "topology",
            "federate_count",
            "status",
            "discoveries",
            "reflections",
            "interactions",
            "execution_complete",
            "key_outcome",
        ],
        summary["scenarios"],
    )
    _write_csv(
        paths.backend_matrix_csv,
        [
            "scenario",
            "family",
            "source_packet",
            "runtime_edition",
            "topology",
            "federate_count",
            "python_backend",
            "python_execution_mode",
            "pitch_2010_profiles",
            "pitch_202x_profiles",
            "vendor_micro_parity",
            "vendor_status",
            "vendor_notes",
        ],
        summary["backend_matrix"],
    )
    paths.report_markdown.write_text(_render_markdown(summary, paths), encoding="utf-8")
    return paths


__all__ = [
    "ShowcasePaths",
    "build_siso_runtime_showcase_manifest",
    "load_siso_runtime_showcase_manifest",
    "run_siso_runtime_showcase",
    "run_siso_runtime_showcase_scenario",
    "write_siso_runtime_showcase_artifacts",
]
