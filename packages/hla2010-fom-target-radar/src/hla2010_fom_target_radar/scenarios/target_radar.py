"""Single-target / radar HLA smoke scenario.

The scenario intentionally uses only ordinary RTIambassador/FederateAmbassador
calls so it can run against the pure Python RTI, a Java RTI through JPype/Py4J,
or an in-process Java-shaped shim.  It models two federates:

* ``SingleTarget`` publishes a target object with Position, Velocity, and RCS.
* ``Radar`` subscribes to target updates, requests fresh RCS via
  ``requestAttributeValueUpdate``, and produces track data as a Track object plus
  a TrackReport interaction.
"""
from __future__ import annotations

import math
import struct
from dataclasses import dataclass, field
from importlib import import_module
from importlib import resources
from typing import Any, Callable, Iterable, Mapping, Protocol

from hla2010.enums import CallbackModel, ResignAction
from hla2010.exceptions import FederatesCurrentlyJoined, FederationExecutionAlreadyExists, FederationExecutionDoesNotExist, RTIexception
from hla2010.handles import AttributeHandle, InteractionClassHandle, ObjectClassHandle, ObjectInstanceHandle, ParameterHandle
from hla2010.spec import FederateAmbassadorSpec
from hla2010.time import HLAinteger64Time

TARGET_CLASS = "HLAobjectRoot.Target"
TRACK_CLASS = "HLAobjectRoot.Track"
TRACK_REPORT_INTERACTION = "HLAinteractionRoot.TrackReport"

TARGET_POSITION = "Position"
TARGET_VELOCITY = "Velocity"
TARGET_RCS = "RCS"

TRACK_TARGET_NAME = "TargetName"
TRACK_POSITION = "Position"
TRACK_RANGE = "Range"
TRACK_BEARING = "Bearing"
TRACK_RCS = "RCS"
TRACK_TIME = "Time"

TRACK_PARAM_ID = "TrackId"
TRACK_PARAM_TARGET_NAME = "TargetName"
TRACK_PARAM_POSITION = "Position"
TRACK_PARAM_RANGE = "Range"
TRACK_PARAM_BEARING = "Bearing"
TRACK_PARAM_RCS = "RCS"
TRACK_PARAM_TIME = "Time"


@dataclass(frozen=True)
class Vec3:
    """Simple 3D vector in meters."""

    x: float
    y: float
    z: float = 0.0

    def add_scaled(self, velocity: Vec3, dt: float) -> Vec3:
        return Vec3(self.x + velocity.x * dt, self.y + velocity.y * dt, self.z + velocity.z * dt)

    def range_from(self, origin: Vec3) -> float:
        return math.sqrt((self.x - origin.x) ** 2 + (self.y - origin.y) ** 2 + (self.z - origin.z) ** 2)

    def bearing_from(self, origin: Vec3) -> float:
        return math.atan2(self.y - origin.y, self.x - origin.x)


@dataclass(frozen=True)
class TrackReport:
    """Radar-produced track report."""

    track_id: str
    target_name: str
    position: Vec3
    range_m: float
    bearing_rad: float
    rcs_square_meters: float
    time_seconds: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "target_name": self.target_name,
            "position": {"x": self.position.x, "y": self.position.y, "z": self.position.z},
            "range_m": self.range_m,
            "bearing_rad": self.bearing_rad,
            "rcs_square_meters": self.rcs_square_meters,
            "time_seconds": self.time_seconds,
        }


@dataclass
class ScenarioResult:
    """Result returned by :func:`run_target_radar_scenario`."""

    federation_name: str
    backend_kinds: tuple[str, str]
    target_name: str
    final_target_position: Vec3
    track_reports: list[TrackReport]
    target_events: list[tuple[str, Any]] = field(default_factory=list)
    radar_events: list[tuple[str, Any]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "federation_name": self.federation_name,
            "backend_kinds": self.backend_kinds,
            "target_name": self.target_name,
            "final_target_position": {
                "x": self.final_target_position.x,
                "y": self.final_target_position.y,
                "z": self.final_target_position.z,
            },
            "track_reports": [report.as_dict() for report in self.track_reports],
            "target_events": [(name, _safe_payload(payload)) for name, payload in self.target_events],
            "radar_events": [(name, _safe_payload(payload)) for name, payload in self.radar_events],
        }


class RTIAmbassadorLike(Protocol):
    def connect(self, *args: Any, **kwargs: Any) -> Any: ...
    def create_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def join_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def resign_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def disconnect(self, *args: Any, **kwargs: Any) -> Any: ...
    def destroy_federation_execution(self, *args: Any, **kwargs: Any) -> Any: ...
    def evoke_multiple_callbacks(self, *args: Any, **kwargs: Any) -> Any: ...


class RoleBasedRtiFactory(Protocol):
    def make_rti(self, role: str) -> RTIAmbassadorLike: ...

    def close(self) -> None: ...


RtiFactory = Callable[[str], RTIAmbassadorLike] | RoleBasedRtiFactory


def encode_vec3(value: Vec3) -> bytes:
    return struct.pack(">ddd", float(value.x), float(value.y), float(value.z))


def decode_vec3(data: bytes) -> Vec3:
    x, y, z = struct.unpack(">ddd", bytes(data)[:24])
    return Vec3(x, y, z)


def encode_float(value: float) -> bytes:
    return struct.pack(">d", float(value))


def decode_float(data: bytes) -> float:
    return struct.unpack(">d", bytes(data)[:8])[0]


def encode_text(value: str) -> bytes:
    return value.encode("utf-8")


def decode_text(data: bytes) -> str:
    return bytes(data).decode("utf-8")


def _safe_payload(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, Vec3):
        return {"x": value.x, "y": value.y, "z": value.z}
    if isinstance(value, TrackReport):
        return value.as_dict()
    if isinstance(value, dict):
        return {repr(key): _safe_payload(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe_payload(item) for item in value]
    return repr(value)


class TargetFederate(FederateAmbassadorSpec):
    """Federate that owns one moving target object."""

    def __init__(
        self,
        *,
        name: str = "Target-1",
        position: Vec3 = Vec3(10_000.0, 1_000.0, 2_000.0),
        velocity: Vec3 = Vec3(250.0, 30.0, 0.0),
        rcs_square_meters: float = 12.5,
    ) -> None:
        self.name = name
        self.position = position
        self.velocity = velocity
        self.rcs_square_meters = rcs_square_meters
        self.rti: Any | None = None
        self.object_class: ObjectClassHandle | None = None
        self.position_attr: AttributeHandle | None = None
        self.velocity_attr: AttributeHandle | None = None
        self.rcs_attr: AttributeHandle | None = None
        self.object_handle: ObjectInstanceHandle | None = None
        self.events: list[tuple[str, Any]] = []
        self._pending_rcs_requests: list[tuple[ObjectInstanceHandle, bytes]] = []

    def setup(self, rti: Any) -> None:
        self.rti = rti
        self.object_class = rti.get_object_class_handle(TARGET_CLASS)
        self.position_attr = rti.get_attribute_handle(self.object_class, TARGET_POSITION)
        self.velocity_attr = rti.get_attribute_handle(self.object_class, TARGET_VELOCITY)
        self.rcs_attr = rti.get_attribute_handle(self.object_class, TARGET_RCS)
        rti.publish_object_class_attributes(
            self.object_class,
            {self.position_attr, self.velocity_attr, self.rcs_attr},
        )
        self.object_handle = rti.register_object_instance(self.object_class, self.name)
        self.update_position_velocity(tag=b"target-initial")

    def step(self, *, time_seconds: float, dt: float) -> None:
        self.position = self.position.add_scaled(self.velocity, dt)
        self.events.append(("step", {"time_seconds": time_seconds, "position": self.position}))
        self.update_position_velocity(tag=f"target-step-{time_seconds:g}".encode("ascii"))

    def update_position_velocity(self, *, tag: bytes) -> None:
        assert self.rti is not None
        assert self.object_handle is not None
        assert self.position_attr is not None
        assert self.velocity_attr is not None
        self.rti.update_attribute_values(
            self.object_handle,
            {
                self.position_attr: encode_vec3(self.position),
                self.velocity_attr: encode_vec3(self.velocity),
            },
            tag,
        )

    def update_rcs(self, *, tag: bytes = b"target-rcs-response") -> None:
        assert self.rti is not None
        assert self.object_handle is not None
        assert self.rcs_attr is not None
        self.rti.update_attribute_values(
            self.object_handle,
            {self.rcs_attr: encode_float(self.rcs_square_meters)},
            tag,
        )

    def provide_attribute_value_update(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: Iterable[AttributeHandle],
        user_supplied_tag: bytes,
        *extra: Any,
    ) -> None:
        self.events.append(("provide_attribute_value_update", (the_object, set(the_attributes), user_supplied_tag)))
        if self.object_handle is None or the_object != self.object_handle:
            return
        if self.rcs_attr in set(the_attributes):
            self._pending_rcs_requests.append((the_object, b"rcs-response:" + bytes(user_supplied_tag)))

    def flush_pending_rcs_requests(self) -> int:
        pending = self._pending_rcs_requests
        self._pending_rcs_requests = []
        for _object_handle, tag in pending:
            self.update_rcs(tag=tag)
        return len(pending)


@dataclass
class RadarContact:
    object_handle: ObjectInstanceHandle
    object_name: str
    position: Vec3 | None = None
    velocity: Vec3 | None = None
    rcs_square_meters: float | None = None


class RadarFederate(FederateAmbassadorSpec):
    """Federate that tracks targets and produces track data."""

    def __init__(self, *, name: str = "Radar-1", origin: Vec3 = Vec3(0.0, 0.0, 0.0)) -> None:
        self.name = name
        self.origin = origin
        self.rti: Any | None = None

        self.target_class: ObjectClassHandle | None = None
        self.position_attr: AttributeHandle | None = None
        self.velocity_attr: AttributeHandle | None = None
        self.rcs_attr: AttributeHandle | None = None

        self.track_class: ObjectClassHandle | None = None
        self.track_attrs: dict[str, AttributeHandle] = {}
        self.track_objects: dict[ObjectInstanceHandle, ObjectInstanceHandle] = {}

        self.track_report_interaction: InteractionClassHandle | None = None
        self.track_params: dict[str, ParameterHandle] = {}

        self.contacts: dict[ObjectInstanceHandle, RadarContact] = {}
        self.track_reports: list[TrackReport] = []
        self.events: list[tuple[str, Any]] = []
        self._pending_track_contacts: list[ObjectInstanceHandle] = []

    def setup(self, rti: Any) -> None:
        self.rti = rti

        self.target_class = rti.get_object_class_handle(TARGET_CLASS)
        self.position_attr = rti.get_attribute_handle(self.target_class, TARGET_POSITION)
        self.velocity_attr = rti.get_attribute_handle(self.target_class, TARGET_VELOCITY)
        self.rcs_attr = rti.get_attribute_handle(self.target_class, TARGET_RCS)
        rti.subscribe_object_class_attributes(
            self.target_class,
            {self.position_attr, self.velocity_attr, self.rcs_attr},
        )

        self.track_class = rti.get_object_class_handle(TRACK_CLASS)
        for name in (TRACK_TARGET_NAME, TRACK_POSITION, TRACK_RANGE, TRACK_BEARING, TRACK_RCS, TRACK_TIME):
            self.track_attrs[name] = rti.get_attribute_handle(self.track_class, name)
        rti.publish_object_class_attributes(self.track_class, set(self.track_attrs.values()))

        self.track_report_interaction = rti.get_interaction_class_handle(TRACK_REPORT_INTERACTION)
        for name in (
            TRACK_PARAM_ID,
            TRACK_PARAM_TARGET_NAME,
            TRACK_PARAM_POSITION,
            TRACK_PARAM_RANGE,
            TRACK_PARAM_BEARING,
            TRACK_PARAM_RCS,
            TRACK_PARAM_TIME,
        ):
            self.track_params[name] = rti.get_parameter_handle(self.track_report_interaction, name)
        rti.publish_interaction_class(self.track_report_interaction)

    def discover_object_instance(self, the_object: ObjectInstanceHandle, the_object_class: ObjectClassHandle, object_name: str, *extra: Any) -> None:
        if self.target_class is not None and the_object_class == self.target_class:
            self.contacts[the_object] = RadarContact(the_object, str(object_name))
            self.events.append(("discover", (the_object, the_object_class, object_name)))

    def reflect_attribute_values(
        self,
        the_object: ObjectInstanceHandle,
        the_attributes: Mapping[AttributeHandle, bytes],
        user_supplied_tag: bytes,
        sent_ordering: Any,
        transportation_type: Any,
        *extra: Any,
    ) -> None:
        contact = self.contacts.setdefault(the_object, RadarContact(the_object, f"Object-{the_object.value}"))
        if self.position_attr in the_attributes:
            contact.position = decode_vec3(the_attributes[self.position_attr])
        if self.velocity_attr in the_attributes:
            contact.velocity = decode_vec3(the_attributes[self.velocity_attr])
        rcs_updated = False
        if self.rcs_attr in the_attributes:
            contact.rcs_square_meters = decode_float(the_attributes[self.rcs_attr])
            rcs_updated = True
        self.events.append(("reflect", (the_object, dict(the_attributes), user_supplied_tag)))
        if rcs_updated and contact.position is not None and contact.rcs_square_meters is not None:
            self._pending_track_contacts.append(the_object)

    def query_rcs_for_all_contacts(self) -> None:
        assert self.rti is not None
        assert self.rcs_attr is not None
        for object_handle in list(self.contacts):
            self.events.append(("query_rcs", object_handle))
            self.rti.request_attribute_value_update(object_handle, {self.rcs_attr}, b"radar-rcs-query")

    def flush_pending_track_reports(self) -> int:
        pending_handles = self._pending_track_contacts
        self._pending_track_contacts = []
        produced = 0
        for object_handle in pending_handles:
            contact = self.contacts.get(object_handle)
            if contact is None or contact.position is None or contact.rcs_square_meters is None:
                continue
            self.produce_track(contact, time_seconds=float(len(self.track_reports) + 1))
            produced += 1
        return produced

    def produce_track(self, contact: RadarContact, *, time_seconds: float) -> TrackReport:
        assert self.rti is not None
        assert self.track_class is not None
        assert self.track_report_interaction is not None
        assert contact.position is not None
        assert contact.rcs_square_meters is not None

        track_id = f"TRK-{len(self.track_reports) + 1:03d}"
        report = TrackReport(
            track_id=track_id,
            target_name=contact.object_name,
            position=contact.position,
            range_m=contact.position.range_from(self.origin),
            bearing_rad=contact.position.bearing_from(self.origin),
            rcs_square_meters=contact.rcs_square_meters,
            time_seconds=time_seconds,
        )

        track_object = self.track_objects.get(contact.object_handle)
        if track_object is None:
            track_object = self.rti.register_object_instance(self.track_class, f"Track-{contact.object_name}")
            self.track_objects[contact.object_handle] = track_object

        self.rti.update_attribute_values(
            track_object,
            {
                self.track_attrs[TRACK_TARGET_NAME]: encode_text(report.target_name),
                self.track_attrs[TRACK_POSITION]: encode_vec3(report.position),
                self.track_attrs[TRACK_RANGE]: encode_float(report.range_m),
                self.track_attrs[TRACK_BEARING]: encode_float(report.bearing_rad),
                self.track_attrs[TRACK_RCS]: encode_float(report.rcs_square_meters),
                self.track_attrs[TRACK_TIME]: encode_float(report.time_seconds),
            },
            b"track-object-update",
        )

        self.rti.send_interaction(
            self.track_report_interaction,
            {
                self.track_params[TRACK_PARAM_ID]: encode_text(report.track_id),
                self.track_params[TRACK_PARAM_TARGET_NAME]: encode_text(report.target_name),
                self.track_params[TRACK_PARAM_POSITION]: encode_vec3(report.position),
                self.track_params[TRACK_PARAM_RANGE]: encode_float(report.range_m),
                self.track_params[TRACK_PARAM_BEARING]: encode_float(report.bearing_rad),
                self.track_params[TRACK_PARAM_RCS]: encode_float(report.rcs_square_meters),
                self.track_params[TRACK_PARAM_TIME]: encode_float(report.time_seconds),
            },
            b"track-report",
        )
        self.track_reports.append(report)
        self.events.append(("track", report))
        return report


def create_python_target_radar_pair() -> tuple[Any, Any]:
    """Create target/radar RTI ambassadors sharing one Python in-memory engine."""

    return import_module("hla2010_rti_python").create_python_pair()


def _python_pair_factory() -> RtiFactory:
    pair_by_role: dict[str, RTIAmbassadorLike] = {}

    def factory(role: str) -> RTIAmbassadorLike:
        if role not in pair_by_role:
            target_rti, radar_rti = create_python_target_radar_pair()
            pair_by_role.update({"target": target_rti, "radar": radar_rti})
        return pair_by_role[role]

    return factory


def _call_factory(factory: RtiFactory, role: str) -> RTIAmbassadorLike:
    maker = getattr(factory, "make_rti", None)
    if callable(maker):
        return maker(role)
    try:
        return factory(role)
    except TypeError:
        # Backward-friendly for zero-argument factories.
        return factory()  # type: ignore[misc]


def _close_factory(factory: RtiFactory) -> None:
    close = getattr(factory, "close", None)
    if callable(close):
        close()


def _drain_callbacks(*rtis: Any, cycles: int = 8) -> None:
    # Some callbacks produce more RTI traffic, which queues more callbacks on
    # another federate.  A few deterministic drain cycles are sufficient for this
    # local scenario and still work against evoked-callback Java RTIs.
    for _ in range(cycles):
        for rti in rtis:
            rti.evoke_multiple_callbacks(0.0, 0.1)


def _default_target_radar_fom_modules() -> list[str]:
    return [
        str(
            resources.files("hla2010_fom_target_radar.resources.foms").joinpath(
                "TargetRadarFOMmodule.xml"
            )
        )
    ]


def run_target_radar_scenario(
    rti_factory: RtiFactory | None = None,
    *,
    federation_name: str = "TargetRadarFederation",
    steps: int = 3,
    dt: float = 1.0,
    target: TargetFederate | None = None,
    radar: RadarFederate | None = None,
    fom_modules: Iterable[Any] | None = None,
    cleanup: bool = True,
) -> ScenarioResult:
    """Run the single-target/radar scenario with any backend-neutral RTI pair.

    ``rti_factory`` is called twice as ``rti_factory("target")`` and
    ``rti_factory("radar")``.  Both returned RTI ambassadors must be connected to
    the same RTI/federation environment.  When omitted, a shared pure Python
    in-memory engine is used.
    """

    if rti_factory is None:
        rti_factory = _python_pair_factory()

    target = target or TargetFederate()
    radar = radar or RadarFederate()
    target_rti = _call_factory(rti_factory, "target")
    radar_rti = _call_factory(rti_factory, "radar")

    target_rti.connect(target, CallbackModel.HLA_EVOKED)
    radar_rti.connect(radar, CallbackModel.HLA_EVOKED)

    try:
        target_rti.create_federation_execution(
            federation_name,
            list(fom_modules) if fom_modules else _default_target_radar_fom_modules(),
        )
    except FederationExecutionAlreadyExists:
        pass

    target_rti.join_federation_execution("SingleTarget", "target", federation_name)
    radar_rti.join_federation_execution("Radar", "radar", federation_name)

    # Radar subscribes before the target registers, so discovery is observable.
    radar.setup(radar_rti)
    target.setup(target_rti)
    _drain_callbacks(target_rti, radar_rti)

    for step_index in range(1, steps + 1):
        target.step(time_seconds=step_index * dt, dt=dt)
        _drain_callbacks(target_rti, radar_rti)
        radar.query_rcs_for_all_contacts()
        _drain_callbacks(target_rti, radar_rti)
        while True:
            progress = False
            progress = bool(target.flush_pending_rcs_requests()) or progress
            if progress:
                _drain_callbacks(target_rti, radar_rti)
            progress = bool(radar.flush_pending_track_reports()) or progress
            if progress:
                _drain_callbacks(target_rti, radar_rti)
            if not progress:
                break
        target_rti.time_advance_request(HLAinteger64Time(step_index))
        radar_rti.time_advance_request(HLAinteger64Time(step_index))
        _drain_callbacks(target_rti, radar_rti)

    backend_kinds = (
        getattr(getattr(target_rti, "backend_info", None), "kind", "unknown"),
        getattr(getattr(radar_rti, "backend_info", None), "kind", "unknown"),
    )
    result = ScenarioResult(
        federation_name=federation_name,
        backend_kinds=backend_kinds,
        target_name=target.name,
        final_target_position=target.position,
        track_reports=list(radar.track_reports),
        target_events=list(target.events),
        radar_events=list(radar.events),
    )

    if cleanup:
        for rti in (radar_rti, target_rti):
            try:
                rti.resign_federation_execution(ResignAction.NO_ACTION)
            except RTIexception:
                pass
        try:
            target_rti.destroy_federation_execution(federation_name)
        except (FederationExecutionDoesNotExist, FederatesCurrentlyJoined, RTIexception):
            pass
        for rti in (radar_rti, target_rti):
            try:
                rti.disconnect()
            except RTIexception:
                pass
        for rti in (radar_rti, target_rti):
            close = getattr(rti, "close", None)
            if callable(close):
                close()
            _close_factory(rti_factory)

    return result


__all__ = [
    "RadarFederate",
    "ScenarioResult",
    "TargetFederate",
    "TrackReport",
    "Vec3",
    "create_python_target_radar_pair",
    "decode_float",
    "decode_text",
    "decode_vec3",
    "encode_float",
    "encode_text",
    "encode_vec3",
    "run_target_radar_scenario",
]
