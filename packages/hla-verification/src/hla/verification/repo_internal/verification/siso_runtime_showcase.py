"""Executable runtime showcase scenarios for high-value SISO FOM families."""
from __future__ import annotations

import csv
import json
import uuid
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hla.backends.common import RecordingFederateAmbassador
from hla.backends.python1516e import InMemoryRTIEngine
from hla.rti1516_2025.enums import CallbackModel as CallbackModel2025
from hla.rti1516_2025.enums import ResignAction as ResignAction2025
from hla.rti1516e.enums import CallbackModel as CallbackModel2010
from hla.rti1516e.enums import ResignAction as ResignAction2010
from hla.runtime.factory import create_rti_ambassador as create_rti_ambassador_2010
from hla.runtime.rti1516_2025_factory import create_rti_ambassador as create_rti_ambassador_2025
from hla.verification.repo_internal.fom_inventory import default_load_set_for_family
from hla.verification.repo_internal.verification.runtime_listener import RuntimeListenerFederate, RuntimeListenerSession
from hla.verification.scenario_support import register_named_object_instance, wait_for_callback_count_pair
from hla.verification.startup import FederationStartupConfig, connect_create_join, synchronize_ready_to_run


@dataclass(frozen=True)
class ShowcasePaths:
    output_dir: Path
    summary_json: Path
    scenario_csv: Path
    backend_matrix_csv: Path
    scenario_manifest_json: Path
    listener_index_json: Path
    listener_index_html: Path
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


def _resolve_object_class_handles(rtis: Iterable[Any], class_name: str) -> dict[Any, Any]:
    return {
        rti: _call_service(rti, "get_object_class_handle", "getObjectClassHandle", class_name)
        for rti in rtis
    }


def _resolve_attribute_handles(
    rtis: Iterable[Any],
    class_name: str,
    attribute_names: Iterable[str],
) -> tuple[dict[Any, Any], dict[Any, dict[str, Any]]]:
    class_handles = _resolve_object_class_handles(rtis, class_name)
    attribute_names = tuple(attribute_names)
    return (
        class_handles,
        {
            rti: {
                name: _call_service(rti, "get_attribute_handle", "getAttributeHandle", class_handles[rti], name)
                for name in attribute_names
            }
            for rti in class_handles
        },
    )


def _resolve_interaction_class_handles(rtis: Iterable[Any], class_name: str) -> dict[Any, Any]:
    return {
        rti: _call_service(rti, "get_interaction_class_handle", "getInteractionClassHandle", class_name)
        for rti in rtis
    }


def _resolve_parameter_handles(
    rtis: Iterable[Any],
    class_name: str,
    parameter_names: Iterable[str],
) -> tuple[dict[Any, Any], dict[Any, dict[str, Any]]]:
    class_handles = _resolve_interaction_class_handles(rtis, class_name)
    parameter_names = tuple(parameter_names)
    return (
        class_handles,
        {
            rti: {
                name: _call_service(rti, "get_parameter_handle", "getParameterHandle", class_handles[rti], name)
                for name in parameter_names
            }
            for rti in class_handles
        },
    )


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
    backend_name = backend or "python1516_2025"
    if runtime.edition == "2010":
        if backend_name not in {"python1516_2025", "python1516e"} and backend not in {None, ""}:
            return [create_rti_ambassador_2010(backend=backend_name) for _ in range(count)]
        engine = InMemoryRTIEngine()
        return [
            create_rti_ambassador_2010(backend="python1516e", engine=engine)
            for _ in range(count)
        ]
    return [
        create_rti_ambassador_2025(backend=backend_name)
        for _ in range(count)
    ]


def _drain(runtime: RuntimeSpec, *rtis: Any, rounds: int = 25) -> None:
    for _ in range(rounds):
        for rti in rtis:
            if runtime.edition == "2010":
                rti.evoke_multiple_callbacks(0.0, 0.0)
            else:
                rti.evokeMultipleCallbacks(0.0, 0.0)


def _callback_summary(federate: RecordingFederateAmbassador) -> dict[str, int]:
    return {
        "discoverObjectInstance": len(federate.callbacks_named("discoverObjectInstance")),
        "reflectAttributeValues": len(federate.callbacks_named("reflectAttributeValues")),
        "receiveInteraction": len(federate.callbacks_named("receiveInteraction")),
    }


def _wait_pair_delivery(
    sender_rti: Any,
    receiver_rti: Any,
    receiver_federate: RecordingFederateAmbassador,
    *,
    discover_expected: int | None = None,
    reflect_expected: int | None = None,
    interaction_expected: int | None = None,
    loops: int = 120,
) -> None:
    if discover_expected is not None:
        wait_for_callback_count_pair(
            sender_rti,
            receiver_rti,
            receiver_federate,
            "discoverObjectInstance",
            discover_expected,
            loops=loops,
        )
    if reflect_expected is not None:
        wait_for_callback_count_pair(
            sender_rti,
            receiver_rti,
            receiver_federate,
            "reflectAttributeValues",
            reflect_expected,
            loops=loops,
        )
    if interaction_expected is not None:
        wait_for_callback_count_pair(
            sender_rti,
            receiver_rti,
            receiver_federate,
            "receiveInteraction",
            interaction_expected,
            loops=loops,
        )


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
        packet_root = _repo_root() / "third_party" / "fom_baseline" / "siso" / "RPR FOM v2.0 Link 16 and Link 11"
        ordered_names = (
            "RPR-Foundation_v2.0.xml",
            "RPR-Enumerations_v2.0.xml",
            "RPR-Base_v2.0.xml",
            "RPR-Physical_v2.0.xml",
            "RPR-Aggregate_v2.0.xml",
            "RPR-Communication_v2.0.xml",
            "RPR-DER_v2.0.xml",
            "RPR-Logistics_v2.0.xml",
            "RPR-Minefield_v2.0.xml",
            "RPR-SE_v2.0.xml",
            "RPR-SIMAN_v2.0.xml",
            "RPR-Switches_v2.0.xml",
            "RPR-UA_v2.0.xml",
            "RPR-Warfare_v2.0.xml",
            "Link_16_v2.0.xml",
        )
        return tuple(str((packet_root / name).resolve()) for name in ordered_names)
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


def _participant_profiles(family: str, topology: TopologySpec, federate_prefix: str) -> list[dict[str, Any]]:
    roles = _participant_roles(family, topology)
    profiles: list[dict[str, Any]] = []
    for idx, role in enumerate(roles, start=1):
        publishes: list[str] = []
        subscribes: list[str] = []
        posture = "observer"
        if family == "link16":
            if role.startswith("originator"):
                posture = "publisher"
                publishes = [
                    "HLAobjectRoot.EmbeddedSystem.RadioTransmitter",
                    "JTIDSMessageRadioSignal",
                    "RTTABRadioSignal",
                ]
            else:
                subscribes = [
                    "HLAobjectRoot.EmbeddedSystem.RadioTransmitter",
                    "JTIDSMessageRadioSignal",
                    "RTTABRadioSignal",
                ]
        elif family == "rpr":
            if role == "bridge-owner-shooter":
                posture = "bridge-owner + shooter"
                publishes = [
                    "HLAobjectRoot.EnvironmentObject.PointObject.BridgeObject",
                    "WeaponFire",
                    "MunitionDetonation",
                ]
            elif role == "bridge-owner":
                posture = "bridge-owner"
                publishes = ["HLAobjectRoot.EnvironmentObject.PointObject.BridgeObject"]
            elif role.startswith("shooter"):
                posture = "shooter"
                publishes = ["WeaponFire", "MunitionDetonation"]
            else:
                subscribes = [
                    "HLAobjectRoot.EnvironmentObject.PointObject.BridgeObject",
                    "WeaponFire",
                    "MunitionDetonation",
                ]
        elif family == "space":
            if role == "frame-authority-producer":
                posture = "frame-authority + producer"
                publishes = [
                    "HLAobjectRoot.ReferenceFrame",
                    "HLAobjectRoot.PhysicalEntity.DynamicalEntity",
                ]
            elif role == "frame-authority":
                posture = "frame-authority"
                publishes = ["HLAobjectRoot.ReferenceFrame"]
            elif role.startswith("producer"):
                posture = "producer"
                publishes = ["HLAobjectRoot.PhysicalEntity.DynamicalEntity"]
            else:
                subscribes = [
                    "HLAobjectRoot.ReferenceFrame",
                    "HLAobjectRoot.PhysicalEntity.DynamicalEntity",
                ]
        profiles.append(
            {
                "federate": f"{federate_prefix}{idx}",
                "role": role,
                "posture": posture,
                "publishes": publishes,
                "subscribes": subscribes,
            }
        )
    return profiles


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


def _default_backend_name(runtime: RuntimeSpec, backend: str | None) -> str:
    if backend:
        return backend
    return "python1516e" if runtime.edition == "2010" else "python1516_2025"


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


def _run_link16_scenario(
    runtime: RuntimeSpec,
    topology: TopologySpec,
    *,
    backend: str | None = None,
    listener_output_dir: str | Path | None = None,
) -> dict[str, Any]:
    packet_id = "link16-rpr2-integrated"
    foms = _packet_paths(packet_id)
    rtis = _create_rtis(runtime, topology.federate_count, backend=backend)
    federation_name = f"SisoLink16-{runtime.edition}-{topology.slug}-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []
    operation_attempts = {
        "object_registrations": 0,
        "attribute_updates": 0,
        "interactions_sent": 0,
    }
    sender_count = _sender_count(topology.federate_count)
    participants = _participant_profiles("link16", topology, "Link16Federate")
    listener = RuntimeListenerSession(
        scenario=f"link16-rpr2-integrated-{runtime.edition}-{topology.slug}",
        family="link16",
        runtime_edition=runtime.edition,
        topology=topology.slug,
        federation_name=federation_name,
        backend=_default_backend_name(runtime, backend),
        fom_modules=[Path(path).name for path in foms],
        participants=participants,
        story=_story_for_family("link16", topology),
        output_root=listener_output_dir,
    )
    federates = [RecordingFederateAmbassador() for _ in rtis]
    federates[-1] = RuntimeListenerFederate(listener, federate_name=participants[-1]["federate"], role=participants[-1]["role"])
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
        listener.mark_phase("ready-to-run-synchronized")
        discover_baseline = len(monitor.callbacks_named("discoverObjectInstance"))
        reflect_baseline = len(monitor.callbacks_named("reflectAttributeValues"))
        interaction_baseline = len(monitor.callbacks_named("receiveInteraction"))
        attr_names = ("RadioIndex", "Frequency", "WorldLocation")
        object_classes, attrs_by_rti = _resolve_attribute_handles(rtis, "HLAobjectRoot.EmbeddedSystem.RadioTransmitter", attr_names)
        for rti in rtis[:sender_count]:
            _call_service(
                rti,
                "publish_object_class_attributes",
                "publishObjectClassAttributes",
                object_classes[rti],
                set(attrs_by_rti[rti].values()),
            )
        for rti in rtis[sender_count:]:
            _call_service(
                rti,
                "subscribe_object_class_attributes",
                "subscribeObjectClassAttributes",
                object_classes[rti],
                set(attrs_by_rti[rti].values()),
            )
        jtids_classes, jtids_params_by_rti = _resolve_parameter_handles(
            rtis,
            jtids_signal,
            ("NPGNumber", "NetNumber", "Link16Version", "JTIDSHeader", "TADILJMessage"),
        )
        rttab_classes, rttab_params_by_rti = _resolve_parameter_handles(
            rtis,
            rttab_signal,
            ("NPGNumber", "NetNumber", "Link16Version", "RTTAB"),
        )
        for rti in rtis[:sender_count]:
            _call_service(rti, "publish_interaction_class", "publishInteractionClass", jtids_classes[rti])
            _call_service(rti, "publish_interaction_class", "publishInteractionClass", rttab_classes[rti])
        for rti in rtis[sender_count:]:
            _call_service(rti, "subscribe_interaction_class", "subscribeInteractionClass", jtids_classes[rti])
            _call_service(rti, "subscribe_interaction_class", "subscribeInteractionClass", rttab_classes[rti])
        lifecycle.append("publication-ready")
        listener.mark_phase("publication-ready")

        for idx, rti in enumerate(rtis[:sender_count], start=1):
            attrs = attrs_by_rti[rti]
            jtids_params = jtids_params_by_rti[rti]
            rttab_params = rttab_params_by_rti[rti]
            transmitter = register_named_object_instance(
                rti,
                federates[idx - 1],
                object_classes[rti],
                f"Link16Radio-{idx}",
            )
            operation_attempts["object_registrations"] += 1
            listener.record_operation(
                "register-object",
                actor=participants[idx - 1]["federate"],
                target=f"Link16Radio-{idx}",
                details={"object_class": "HLAobjectRoot.EmbeddedSystem.RadioTransmitter"},
            )
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
            operation_attempts["attribute_updates"] += 1
            listener.record_operation(
                "update-object",
                actor=participants[idx - 1]["federate"],
                target=f"Link16Radio-{idx}",
                tag=_rpr_tag_bytes(f"link16-transmitter-state-{idx}"),
                details={"attributes": ["RadioIndex", "Frequency", "WorldLocation"]},
            )
            _call_service(
                rti,
                "send_interaction",
                "sendInteraction",
                jtids_classes[rti],
                {
                    jtids_params["NPGNumber"]: str(7 + idx).encode("utf-8"),
                    jtids_params["NetNumber"]: b"12",
                    jtids_params["Link16Version"]: b"BlockUpgrade2",
                    jtids_params["JTIDSHeader"]: f"header-{idx}".encode("utf-8"),
                    jtids_params["TADILJMessage"]: f"J3.2 AIR TRACK {idx}".encode("utf-8"),
                },
                _rpr_tag_bytes(f"link16-jtids-message-{idx}"),
            )
            operation_attempts["interactions_sent"] += 1
            listener.record_operation(
                "send-interaction",
                actor=participants[idx - 1]["federate"],
                target=jtids_signal,
                tag=_rpr_tag_bytes(f"link16-jtids-message-{idx}"),
                details={"message_type": "JTIDS"},
            )
            _call_service(
                rti,
                "send_interaction",
                "sendInteraction",
                rttab_classes[rti],
                {
                    rttab_params["NPGNumber"]: str(7 + idx).encode("utf-8"),
                    rttab_params["NetNumber"]: b"12",
                    rttab_params["Link16Version"]: b"BlockUpgrade2",
                    rttab_params["RTTAB"]: f"request-time-slot-reblock-{idx}".encode("utf-8"),
                },
                _rpr_tag_bytes(f"link16-rttab-{idx}"),
            )
            operation_attempts["interactions_sent"] += 1
            listener.record_operation(
                "send-interaction",
                actor=participants[idx - 1]["federate"],
                target=rttab_signal,
                tag=_rpr_tag_bytes(f"link16-rttab-{idx}"),
                details={"message_type": "RTTAB"},
            )
        _drain(runtime, *rtis)
        if topology.federate_count == 2:
            _wait_pair_delivery(
                rtis[0],
                rtis[-1],
                monitor,
                discover_expected=discover_baseline + sender_count,
                reflect_expected=reflect_baseline + sender_count,
                interaction_expected=interaction_baseline + (sender_count * 2),
            )
        lifecycle.append("message-traffic-observed")
        listener.mark_phase(
            "message-traffic-observed",
            metrics={
                "discoveries": len(monitor.callbacks_named("discoverObjectInstance")),
                "reflections": len(monitor.callbacks_named("reflectAttributeValues")),
                "interactions": len(monitor.callbacks_named("receiveInteraction")),
            },
        )

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
        listener_summary = listener.finalize(
            lifecycle=lifecycle,
            operation_attempts=operation_attempts,
            execution_complete=execution_complete,
            status="lifecycle-green" if execution_complete else "failed",
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
            "participant_profiles": participants,
            "lifecycle": lifecycle,
            "object_class": "HLAobjectRoot.EmbeddedSystem.RadioTransmitter",
            "interaction_classes": [jtids_signal, rttab_signal],
            "discoveries": len(discoveries),
            "reflections": len(reflections),
            "interactions": len(receives),
            "operation_attempts": operation_attempts,
            "federate_callback_summaries": {
                f"Link16Federate{idx + 1}": _callback_summary(federate)
                for idx, federate in enumerate(federates)
            },
            "delivered_tags": [_jsonable(tag) for tag in delivered_tags],
            "listener_summary": listener_summary["statistics"],
            "listener_artifacts": listener_summary["artifacts"],
            "listener_event_count": listener_summary["event_count"],
            "key_outcome": "multiple Link 16 radio publishers reflected state and delivered JTIDS/RTTAB traffic to shared observers",
            "execution_complete": execution_complete,
        }
    finally:
        _shutdown(runtime, federation_name, rtis)


def _run_rpr_scenario(runtime: RuntimeSpec, topology: TopologySpec, *, backend: str | None = None, listener_output_dir: str | Path | None = None) -> dict[str, Any]:
    packet_id = "rpr3-annex-a-normative" if runtime.edition == "2025" else "rpr3-merged-informative-1516-2010"
    foms = _packet_paths(packet_id)
    rtis = _create_rtis(runtime, topology.federate_count, backend=backend)
    federation_name = f"SisoRpr-{runtime.edition}-{topology.slug}-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []
    operation_attempts = {
        "object_registrations": 0,
        "attribute_updates": 0,
        "interactions_sent": 0,
    }
    shooter_count = _sender_count(topology.federate_count) if topology.federate_count > 2 else 0
    bridge_owner = rtis[0]
    participants = _participant_profiles("rpr", topology, "RprFederate")
    listener = RuntimeListenerSession(
        scenario=f"rpr-runtime-{runtime.edition}-{topology.slug}",
        family="rpr",
        runtime_edition=runtime.edition,
        topology=topology.slug,
        federation_name=federation_name,
        backend=_default_backend_name(runtime, backend),
        fom_modules=[Path(path).name for path in foms],
        participants=participants,
        story=_story_for_family("rpr", topology),
        output_root=listener_output_dir,
    )
    federates = [RecordingFederateAmbassador() for _ in rtis]
    federates[-1] = RuntimeListenerFederate(listener, federate_name=participants[-1]["federate"], role=participants[-1]["role"])
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
        listener.mark_phase("ready-to-run-synchronized")
        discover_baseline = len(monitor.callbacks_named("discoverObjectInstance"))
        reflect_baseline = len(monitor.callbacks_named("reflectAttributeValues"))
        interaction_baseline = len(monitor.callbacks_named("receiveInteraction"))
        object_classes, attrs_by_rti = _resolve_attribute_handles(rtis, object_class_name, ("ObjectIdentifier", "Location", "Damage"))
        _call_service(
            bridge_owner,
            "publish_object_class_attributes",
            "publishObjectClassAttributes",
            object_classes[bridge_owner],
            set(attrs_by_rti[bridge_owner].values()),
        )
        for rti in rtis[1:]:
            _call_service(
                rti,
                "subscribe_object_class_attributes",
                "subscribeObjectClassAttributes",
                object_classes[rti],
                set(attrs_by_rti[rti].values()),
            )
        fire_classes, fire_params_by_rti = _resolve_parameter_handles(
            rtis,
            fire_name,
            ("FiringObjectIdentifier", "TargetObjectIdentifier", "EventIdentifier", "MunitionType", "QuantityFired"),
        )
        detonation_classes, detonation_params_by_rti = _resolve_parameter_handles(
            rtis,
            detonation_name,
            ("EventIdentifier", "DetonationLocation", "DetonationResultCode", "TargetObjectIdentifier", "QuantityFired"),
        )
        shooter_rtis = rtis[1 : 1 + shooter_count] if shooter_count else [bridge_owner]
        observer_rtis = rtis[1 + shooter_count :] if shooter_count else rtis[1:]
        for rti in shooter_rtis:
            _call_service(rti, "publish_interaction_class", "publishInteractionClass", fire_classes[rti])
            _call_service(rti, "publish_interaction_class", "publishInteractionClass", detonation_classes[rti])
        for rti in observer_rtis:
            _call_service(rti, "subscribe_interaction_class", "subscribeInteractionClass", fire_classes[rti])
            _call_service(rti, "subscribe_interaction_class", "subscribeInteractionClass", detonation_classes[rti])
        lifecycle.append("engagement-publication-ready")
        listener.mark_phase("engagement-publication-ready")

        attrs = attrs_by_rti[bridge_owner]
        bridge = register_named_object_instance(
            bridge_owner,
            federates[0],
            object_classes[bridge_owner],
            "Bridge-Alpha",
        )
        operation_attempts["object_registrations"] += 1
        listener.record_operation(
            "register-object",
            actor=participants[0]["federate"],
            target="Bridge-Alpha",
            details={"object_class": object_class_name},
        )
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
        operation_attempts["attribute_updates"] += 1
        listener.record_operation(
            "update-object",
            actor=participants[0]["federate"],
            target="Bridge-Alpha",
            tag=_rpr_fixed_tag(0),
            details={"attributes": ["ObjectIdentifier", "Location", "Damage"]},
        )
        active_shooter_count = len(shooter_rtis)
        for idx, rti in enumerate(shooter_rtis, start=1):
            fire_params = fire_params_by_rti[rti]
            detonation_params = detonation_params_by_rti[rti]
            _call_service(
                rti,
                "send_interaction",
                "sendInteraction",
                fire_classes[rti],
                {
                    fire_params["FiringObjectIdentifier"]: f"shooter-{idx}".encode("utf-8"),
                    fire_params["TargetObjectIdentifier"]: b"bridge-alpha",
                    fire_params["EventIdentifier"]: f"engagement-{idx:03d}".encode("utf-8"),
                    fire_params["MunitionType"]: b"guided-munition",
                    fire_params["QuantityFired"]: str(idx).encode("utf-8"),
                },
                _rpr_fixed_tag(idx),
            )
            operation_attempts["interactions_sent"] += 1
            listener.record_operation(
                "send-interaction",
                actor=participants[0 if topology.federate_count == 2 else idx]["federate"],
                target=fire_name,
                tag=_rpr_fixed_tag(idx),
                details={"event_identifier": f"engagement-{idx:03d}"},
            )
            _call_service(
                rti,
                "send_interaction",
                "sendInteraction",
                detonation_classes[rti],
                {
                    detonation_params["EventIdentifier"]: f"engagement-{idx:03d}".encode("utf-8"),
                    detonation_params["DetonationLocation"]: b"41.88,-87.63,0",
                    detonation_params["DetonationResultCode"]: b"detonation",
                    detonation_params["TargetObjectIdentifier"]: b"bridge-alpha",
                    detonation_params["QuantityFired"]: str(idx).encode("utf-8"),
                },
                _rpr_fixed_tag(100 + idx),
            )
            operation_attempts["interactions_sent"] += 1
            listener.record_operation(
                "send-interaction",
                actor=participants[0 if topology.federate_count == 2 else idx]["federate"],
                target=detonation_name,
                tag=_rpr_fixed_tag(100 + idx),
                details={"event_identifier": f"engagement-{idx:03d}"},
            )
        _drain(runtime, *rtis)
        if topology.federate_count == 2:
            _wait_pair_delivery(
                bridge_owner,
                rtis[-1],
                monitor,
                discover_expected=discover_baseline + 1,
                reflect_expected=reflect_baseline + 1,
                interaction_expected=interaction_baseline + (active_shooter_count * 2),
            )
        lifecycle.append("engagement-chain-observed")
        listener.mark_phase(
            "engagement-chain-observed",
            metrics={
                "discoveries": len(monitor.callbacks_named("discoverObjectInstance")),
                "reflections": len(monitor.callbacks_named("reflectAttributeValues")),
                "interactions": len(monitor.callbacks_named("receiveInteraction")),
            },
        )

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
        listener_summary = listener.finalize(
            lifecycle=lifecycle,
            operation_attempts=operation_attempts,
            execution_complete=execution_complete,
            status="lifecycle-green" if execution_complete else "failed",
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
            "participant_profiles": participants,
            "lifecycle": lifecycle,
            "object_class": object_class_name,
            "interaction_classes": [fire_name, detonation_name],
            "discoveries": len(discoveries),
            "reflections": len(reflections),
            "interactions": len(receives),
            "operation_attempts": operation_attempts,
            "federate_callback_summaries": {
                f"RprFederate{idx + 1}": _callback_summary(federate)
                for idx, federate in enumerate(federates)
            },
            "delivered_tags": [_jsonable(tag) for tag in delivered_tags],
            "listener_summary": listener_summary["statistics"],
            "listener_artifacts": listener_summary["artifacts"],
            "listener_event_count": listener_summary["event_count"],
            "key_outcome": "bridge state and multi-shooter fire/detonation chains reached the tactical observer set",
            "execution_complete": execution_complete,
        }
    finally:
        _shutdown(runtime, federation_name, rtis)


def _run_space_scenario(runtime: RuntimeSpec, topology: TopologySpec, *, backend: str | None = None, listener_output_dir: str | Path | None = None) -> dict[str, Any]:
    packet_id = "space-fom-core"
    foms = _packet_paths(packet_id)
    rtis = _create_rtis(runtime, topology.federate_count, backend=backend)
    federation_name = f"SisoSpace-{runtime.edition}-{topology.slug}-{uuid.uuid4().hex[:8]}"
    lifecycle: list[str] = []
    operation_attempts = {
        "object_registrations": 0,
        "attribute_updates": 0,
        "interactions_sent": 0,
    }
    producer_count = _sender_count(topology.federate_count) if topology.federate_count > 2 else 0
    frame_authority = rtis[0]
    participants = _participant_profiles("space", topology, "SpaceFederate")
    listener = RuntimeListenerSession(
        scenario=f"space-fom-core-{runtime.edition}-{topology.slug}",
        family="space",
        runtime_edition=runtime.edition,
        topology=topology.slug,
        federation_name=federation_name,
        backend=_default_backend_name(runtime, backend),
        fom_modules=[Path(path).name for path in foms],
        participants=participants,
        story=_story_for_family("space", topology),
        output_root=listener_output_dir,
    )
    federates = [RecordingFederateAmbassador() for _ in rtis]
    federates[-1] = RuntimeListenerFederate(listener, federate_name=participants[-1]["federate"], role=participants[-1]["role"])
    federate_by_rti = dict(zip(rtis, federates, strict=True))
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
        listener.mark_phase("ready-to-run-synchronized")
        discover_baseline = len(monitor.callbacks_named("discoverObjectInstance"))
        reflect_baseline = len(monitor.callbacks_named("reflectAttributeValues"))
        frame_classes, frame_attrs_by_rti = _resolve_attribute_handles(rtis, reference_frame_class_name, ("name", "parent_name", "state"))
        entity_classes, entity_attrs_by_rti = _resolve_attribute_handles(
            rtis,
            entity_class_name,
            ("name", "type", "status", "parent_reference_frame", "state"),
        )
        _call_service(
            frame_authority,
            "publish_object_class_attributes",
            "publishObjectClassAttributes",
            frame_classes[frame_authority],
            set(frame_attrs_by_rti[frame_authority].values()),
        )
        producer_rtis = rtis[1 : 1 + producer_count] if producer_count else [frame_authority]
        observer_rtis = rtis[1 + producer_count :] if producer_count else rtis[1:]
        for rti in producer_rtis:
            _call_service(
                rti,
                "publish_object_class_attributes",
                "publishObjectClassAttributes",
                entity_classes[rti],
                set(entity_attrs_by_rti[rti].values()),
            )
        for rti in observer_rtis:
            _call_service(
                rti,
                "subscribe_object_class_attributes",
                "subscribeObjectClassAttributes",
                frame_classes[rti],
                set(frame_attrs_by_rti[rti].values()),
            )
            _call_service(
                rti,
                "subscribe_object_class_attributes",
                "subscribeObjectClassAttributes",
                entity_classes[rti],
                set(entity_attrs_by_rti[rti].values()),
            )
        lifecycle.append("space-publication-ready")
        listener.mark_phase("space-publication-ready")

        frame_attrs = frame_attrs_by_rti[frame_authority]
        frame = register_named_object_instance(
            frame_authority,
            federates[0],
            frame_classes[frame_authority],
            "EarthMJ2000Eq",
        )
        operation_attempts["object_registrations"] += 1
        listener.record_operation(
            "register-object",
            actor=participants[0]["federate"],
            target="EarthMJ2000Eq",
            details={"object_class": reference_frame_class_name},
        )
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
        operation_attempts["attribute_updates"] += 1
        listener.record_operation(
            "update-object",
            actor=participants[0]["federate"],
            target="EarthMJ2000Eq",
            tag=_tag_bytes("space-reference-frame"),
            details={"attributes": ["name", "parent_name", "state"]},
        )
        active_producer_count = len(producer_rtis)
        for idx, rti in enumerate(producer_rtis, start=1):
            entity_attrs = entity_attrs_by_rti[rti]
            entity = register_named_object_instance(
                rti,
                federate_by_rti[rti],
                entity_classes[rti],
                f"Scout-{idx}",
            )
            operation_attempts["object_registrations"] += 1
            listener.record_operation(
                "register-object",
                actor=participants[0 if topology.federate_count == 2 else idx]["federate"],
                target=f"Scout-{idx}",
                details={"object_class": entity_class_name},
            )
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
            operation_attempts["attribute_updates"] += 1
            listener.record_operation(
                "update-object",
                actor=participants[0 if topology.federate_count == 2 else idx]["federate"],
                target=f"Scout-{idx}",
                tag=_tag_bytes(f"space-dynamics-state-{idx}"),
                details={"attributes": ["name", "type", "status", "parent_reference_frame", "state"]},
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
            operation_attempts["attribute_updates"] += 1
            listener.record_operation(
                "update-object",
                actor=participants[0 if topology.federate_count == 2 else idx]["federate"],
                target=f"Scout-{idx}",
                tag=_tag_bytes(f"space-dynamics-update-{idx}"),
                details={"attributes": ["status", "state"]},
            )
        _drain(runtime, *rtis)
        if topology.federate_count == 2:
            _wait_pair_delivery(
                frame_authority,
                rtis[-1],
                monitor,
                discover_expected=discover_baseline + 1 + active_producer_count,
                reflect_expected=reflect_baseline + 1 + (active_producer_count * 2),
            )
        lifecycle.append("space-state-reflected")
        listener.mark_phase(
            "space-state-reflected",
            metrics={
                "discoveries": len(monitor.callbacks_named("discoverObjectInstance")),
                "reflections": len(monitor.callbacks_named("reflectAttributeValues")),
            },
        )

        discoveries = monitor.callbacks_named("discoverObjectInstance")
        reflections = monitor.callbacks_named("reflectAttributeValues")
        execution_complete = (
            len(discoveries) >= 1 + active_producer_count
            and len(reflections) >= 1 + (active_producer_count * 2)
        )
        listener_summary = listener.finalize(
            lifecycle=lifecycle,
            operation_attempts=operation_attempts,
            execution_complete=execution_complete,
            status="lifecycle-green" if execution_complete else "failed",
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
            "participant_profiles": participants,
            "lifecycle": lifecycle,
            "object_classes": [reference_frame_class_name, entity_class_name],
            "discoveries": len(discoveries),
            "reflections": len(reflections),
            "interactions": 0,
            "operation_attempts": operation_attempts,
            "federate_callback_summaries": {
                f"SpaceFederate{idx + 1}": _callback_summary(federate)
                for idx, federate in enumerate(federates)
            },
            "delivered_tags": [],
            "listener_summary": listener_summary["statistics"],
            "listener_artifacts": listener_summary["artifacts"],
            "listener_event_count": listener_summary["event_count"],
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
                profiles = _participant_profiles(
                    family,
                    topology,
                    "Link16Federate" if family == "link16" else "RprFederate" if family == "rpr" else "SpaceFederate",
                )
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
                        "participant_profiles": profiles,
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
    listener_output_dir: str | Path | None = None,
) -> dict[str, Any]:
    manifest = build_siso_runtime_showcase_manifest()
    selected = next((row for row in manifest["scenarios"] if row["scenario"] == scenario), None)
    if selected is None:
        raise KeyError(f"Unknown showcase scenario {scenario!r}")
    runtime = _runtime_for_edition(str(selected["runtime_edition"]))
    topology = _topology_for_slug(str(selected["topology"]))
    family = str(selected["family"])
    return _family_runner(family)(runtime, topology, backend=backend, listener_output_dir=listener_output_dir)


def run_siso_runtime_showcase(*, listener_output_dir: str | Path | None = None) -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    for runtime in (RUNTIME_2010, RUNTIME_2025):
        for topology in TOPOLOGIES:
            scenarios.append(_run_link16_scenario(runtime, topology, listener_output_dir=listener_output_dir))
            scenarios.append(_run_rpr_scenario(runtime, topology, listener_output_dir=listener_output_dir))
            scenarios.append(_run_space_scenario(runtime, topology, listener_output_dir=listener_output_dir))
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
        f"- listener index json: `{paths.listener_index_json}`",
        f"- listener index html: `{paths.listener_index_html}`",
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
                f"- Listener events: `{row.get('listener_event_count', 0)}`",
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
        if row.get("listener_artifacts"):
            lines.append(f"- Listener summary json: `{row['listener_artifacts'].get('summary_json', 'n/a')}`")
            lines.append(f"- Listener trace ndjson: `{row['listener_artifacts'].get('trace_ndjson', 'n/a')}`")
            lines.append(f"- Listener report html: `{row['listener_artifacts'].get('report_html', 'n/a')}`")
    return "\n".join(lines) + "\n"


def _write_listener_index_json(path: Path, rows: list[Mapping[str, Any]]) -> Path:
    payload = {
        "scenario_count": len(rows),
        "listeners": [
            {
                "scenario": row["scenario"],
                "family": row["family"],
                "runtime_edition": row["runtime_edition"],
                "topology": row["topology"],
                "listener_event_count": row.get("listener_event_count", 0),
                "listener_artifacts": row.get("listener_artifacts", {}),
            }
            for row in rows
        ],
    }
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_listener_index_html(path: Path, rows: list[Mapping[str, Any]]) -> Path:
    table_rows = "\n".join(
        "<tr>"
        f"<td>{row['scenario']}</td>"
        f"<td>{row['family']}</td>"
        f"<td>{row['runtime_edition']}</td>"
        f"<td>{row['topology']}</td>"
        f"<td>{row.get('listener_event_count', 0)}</td>"
        f"<td><code>{row.get('listener_artifacts', {}).get('summary_json', '')}</code></td>"
        f"<td><code>{row.get('listener_artifacts', {}).get('report_html', '')}</code></td>"
        "</tr>"
        for row in rows
    )
    path.write_text(
        "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>SISO runtime listener index</title>"
        "<style>body{font:15px/1.5 Menlo,Consolas,monospace;background:#f4f1e8;color:#1f2933;padding:24px}"
        "table{width:100%;border-collapse:collapse;background:#fffdfa}th,td{border:1px solid #d7cbb8;padding:8px;text-align:left}"
        "h1{color:#9f3a16}</style></head><body><h1>SISO Runtime Listener Index</h1><table><thead><tr>"
        "<th>Scenario</th><th>Family</th><th>Edition</th><th>Topology</th><th>Events</th><th>Summary JSON</th><th>HTML</th>"
        f"</tr></thead><tbody>{table_rows}</tbody></table></body></html>",
        encoding="utf-8",
    )
    return path


def write_siso_runtime_showcase_artifacts(output_dir: str | Path) -> ShowcasePaths:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = ShowcasePaths(
        output_dir=out,
        summary_json=out / "siso_runtime_showcase_summary.json",
        scenario_csv=out / "siso_runtime_showcase_scenarios.csv",
        backend_matrix_csv=out / "siso_runtime_showcase_backend_matrix.csv",
        scenario_manifest_json=out / "siso_runtime_showcase_manifest.json",
        listener_index_json=out / "siso_runtime_showcase_listener_index.json",
        listener_index_html=out / "siso_runtime_showcase_listener_index.html",
        report_markdown=out / "siso_runtime_showcase_report.md",
    )
    summary = run_siso_runtime_showcase(listener_output_dir=out / "listener")
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
    _write_listener_index_json(paths.listener_index_json, summary["scenarios"])
    _write_listener_index_html(paths.listener_index_html, summary["scenarios"])
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
