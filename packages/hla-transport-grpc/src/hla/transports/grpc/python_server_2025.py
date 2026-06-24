"""Transport-hosted IEEE 1516.1-2025 RTI server for the gRPC wire path."""

from __future__ import annotations

from concurrent import futures
from copy import deepcopy
from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

from hla.transports.grpc.fedpro2025 import FederateAmbassador_2025_pb2 as callback_pb2
from hla.transports.grpc.fedpro2025 import HLA2025RTITransport_pb2_grpc as pb2_grpc
from hla.transports.grpc.fedpro2025 import RTIambassador_2025_pb2 as rti_pb2
from hla.transports.grpc.fedpro2025 import datatypes_2025_pb2 as datatypes_pb2

try:  # pragma: no cover - import guarded for optional dependency
    import grpc
except Exception as exc:  # pragma: no cover - optional dependency
    grpc = None  # type: ignore[assignment]
    _GRPC_IMPORT_ERROR = exc
else:
    _GRPC_IMPORT_ERROR = None


@dataclass(frozen=True)
class RTI2025GrpcServerConfig:
    host: str = "127.0.0.1"
    port: int = 0
    max_workers: int = 4


@dataclass
class _FederationSnapshot:
    object_instances: dict[str, dict[str, str]]
    reserved_object_instance_names: dict[str, str]
    attribute_owners: dict[tuple[str, str], str]
    unowned_attributes: set[tuple[str, str]]
    offered_attributes: set[tuple[str, str]]
    pending_attribute_acquisitions: dict[tuple[str, str], bytes]
    pending_attribute_requesters: dict[tuple[str, str], str]
    current_time: datatypes_pb2.LogicalTime
    next_object_instance_handle: int
    lookahead: datatypes_pb2.LogicalTimeInterval
    handle_current_times: dict[str, datatypes_pb2.LogicalTime] = field(default_factory=dict)
    handle_lookahead: dict[str, datatypes_pb2.LogicalTimeInterval] = field(default_factory=dict)
    object_update_regions: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    regions: dict[str, set[str]] = field(default_factory=dict)
    region_bounds: dict[str, dict[str, tuple[int, int]]] = field(default_factory=dict)
    published_object_attributes: dict[str, set[str]] = field(default_factory=dict)
    handle_published_object_attributes: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    handle_subscribed_object_attributes: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    handle_subscribed_object_regions: dict[str, dict[str, dict[str, set[str]]]] = field(default_factory=dict)
    published_interactions: set[str] = field(default_factory=set)
    handle_published_interactions: dict[str, set[str]] = field(default_factory=dict)
    default_attribute_transportation: dict[tuple[str, str], str] = field(default_factory=dict)
    default_attribute_order: dict[tuple[str, str], int] = field(default_factory=dict)
    interaction_transportation: tuple[str, str] | None = None
    interaction_order: tuple[str, int] | None = None
    switch_states: dict[str, bool] = field(default_factory=dict)
    service_reporting: bool = False
    handle_service_reporting: dict[str, bool] = field(default_factory=dict)
    handle_exception_reporting: dict[str, bool] = field(default_factory=dict)
    automatic_resign_directive: int = datatypes_pb2.NO_ACTION
    time_regulating: bool = False
    time_constrained: bool = False
    asynchronous_delivery_enabled: bool = False
    handle_time_regulating: dict[str, bool] = field(default_factory=dict)
    handle_time_constrained: dict[str, bool] = field(default_factory=dict)
    handle_asynchronous_delivery_enabled: dict[str, bool] = field(default_factory=dict)
    handle_pending_time_advance: dict[str, tuple[str, datatypes_pb2.LogicalTime]] = field(default_factory=dict)
    callback_delivery_enabled: bool = True
    peer_callback_delivery_enabled: dict[str, bool] = field(default_factory=dict)
    handle_locally_deleted_objects: dict[str, set[str]] = field(default_factory=dict)
    directed_interaction_region_gates: set[str] = field(default_factory=set)
    published_directed_interactions: dict[str, set[str]] = field(default_factory=dict)
    handle_published_directed_interactions: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    handle_subscribed_directed_interactions: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    handle_subscribed_interactions: dict[str, set[str]] = field(default_factory=dict)
    handle_subscribed_interaction_regions: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    queued_tso_callbacks: dict[str, tuple[float, list[callback_pb2.CallbackRequest]]] = field(default_factory=dict)
    queued_tso_target_handles: dict[str, list[frozenset[str] | None]] = field(default_factory=dict)
    delivered_retractions: set[str] = field(default_factory=set)
    delivered_retraction_targets: dict[str, frozenset[str]] = field(default_factory=dict)
    requested_retractions: set[str] = field(default_factory=set)
    next_retraction_handle: int = 1


def _callback_request() -> callback_pb2.CallbackRequest:
    return callback_pb2.CallbackRequest()


def _logical_time_value(time: datatypes_pb2.LogicalTime) -> float:
    raw = time.data.decode("ascii") if time.data else "HLAinteger64Time:0"
    _, _, value = raw.partition(":")
    try:
        return float(value or raw)
    except ValueError:
        return 0.0


def _logical_interval_value(interval: datatypes_pb2.LogicalTimeInterval) -> float:
    raw = interval.data.decode("ascii") if interval.data else "HLAinteger64Interval:0"
    _, _, value = raw.partition(":")
    try:
        return float(value or raw)
    except ValueError:
        return 0.0


def _handle(handle_type: type, value: str | int):
    return handle_type(data=str(value).encode("ascii"))


_MOM_INTERACTION_NAME_ALIASES = {
    "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMData":
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata",
    "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMData":
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata",
}


def _canonical_mom_interaction_name(name: str) -> str:
    return _MOM_INTERACTION_NAME_ALIASES.get(name, name)


def _canonical_mom_parameter_name(interaction_name: str, parameter_name: str) -> str:
    if interaction_name == "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata":
        if parameter_name == "HLAMIMData":
            return "HLAMIMdata"
    return parameter_name


def _attribute_set(values: list[str] | tuple[str, ...] | str) -> datatypes_pb2.AttributeHandleSet:
    result = datatypes_pb2.AttributeHandleSet()
    items = values.split(",") if isinstance(values, str) else values
    for item in items:
        if item:
            result.attributeHandle.add(data=str(item).encode("ascii"))
    return result


def _fom_module_designators(fom_modules) -> list[str]:
    modules = []
    for module in fom_modules.fomModule:
        designator = module.url or module.file.name
        if designator:
            modules.append(designator)
    return modules


def _resolve_2025_fom_modules(sources: tuple[str, ...], *, mim: bool) -> tuple[object, ...]:
    fom = import_module("hla.fom")
    try:
        modules = fom.FOMResolver(require_local_parse=True).resolve_many(sources)
        if not mim:
            validation = import_module("hla.fom.validation")
            issues = validation.validate_fom_modules(modules)
            if issues:
                raise ValueError(issues[0].message)
        return tuple(modules)
    except fom.FOMResolutionError as exc:
        kind = getattr(exc, "kind", "open")
        if mim:
            return _raise_resolution_error(kind, str(exc), open_name="CouldNotOpenMIM", read_name="ErrorReadingMIM")
        return _raise_resolution_error(kind, str(exc), open_name="CouldNotOpenFOM", read_name="ErrorReadingFOM")
    except ValueError as exc:
        if mim:
            raise RuntimeError(("InvalidMIM", str(exc))) from exc
        raise RuntimeError(("InvalidFOM", str(exc))) from exc
    except Exception as exc:
        if mim:
            raise RuntimeError(("InvalidMIM", str(exc))) from exc
        raise RuntimeError(("InvalidFOM", str(exc))) from exc


def _raise_resolution_error(kind: str, details: str, *, open_name: str, read_name: str):
    if kind == "read":
        raise RuntimeError((read_name, details))
    raise RuntimeError((open_name, details))


def _merge_2025_fom_modules(modules: tuple[object, ...], *, mim_module: object) -> object:
    fom = import_module("hla.fom")
    try:
        return fom.merge_fom_modules(modules, mim_module=mim_module)
    except fom.FOMMergeError as exc:
        raise RuntimeError(("InconsistentFOM", str(exc))) from exc


def _module_payload_text(module: object, designator: str) -> str:
    path = getattr(module, "path", None)
    if path is not None:
        return Path(path).read_text(encoding="utf-8")
    return designator


def _dimension_set(values: list[str] | tuple[str, ...] | str) -> datatypes_pb2.DimensionHandleSet:
    result = datatypes_pb2.DimensionHandleSet()
    items = values.split(",") if isinstance(values, str) else values
    for item in items:
        if item:
            result.dimensionHandle.add(data=str(item).encode("ascii"))
    return result


_MOM_FEDERATE_ADJUST_LEAVES = (
    "HLAsetTiming",
    "HLAmodifyAttributeState",
    "HLAsetServiceReporting",
    "HLAsetExceptionReporting",
    "HLAsetSwitches",
)
_MOM_FEDERATION_ADJUST_LEAVES = ("HLAsetSwitches",)
_MOM_FEDERATE_SERVICE_LEAVES = (
    "HLAresignFederationExecution",
    "HLAsynchronizationPointAchieved",
    "HLAfederateSaveBegun",
    "HLAfederateSaveComplete",
    "HLAfederateRestoreComplete",
    "HLApublishObjectClassAttributes",
    "HLAunpublishObjectClassAttributes",
    "HLApublishInteractionClass",
    "HLAunpublishInteractionClass",
    "HLAsubscribeObjectClassAttributes",
    "HLAunsubscribeObjectClassAttributes",
    "HLAsubscribeInteractionClass",
    "HLAunsubscribeInteractionClass",
    "HLAdeleteObjectInstance",
    "HLAlocalDeleteObjectInstance",
    "HLArequestAttributeTransportationTypeChange",
    "HLArequestInteractionTransportationTypeChange",
    "HLAunconditionalAttributeOwnershipDivestiture",
    "HLAenableTimeRegulation",
    "HLAdisableTimeRegulation",
    "HLAenableTimeConstrained",
    "HLAdisableTimeConstrained",
    "HLAtimeAdvanceRequest",
    "HLAtimeAdvanceRequestAvailable",
    "HLAnextMessageRequest",
    "HLAnextMessageRequestAvailable",
    "HLAflushQueueRequest",
    "HLAenableAsynchronousDelivery",
    "HLAdisableAsynchronousDelivery",
    "HLAmodifyLookahead",
    "HLAchangeAttributeOrderType",
    "HLAchangeInteractionOrderType",
)


class _FedPro2025GatewayServicer(pb2_grpc.HLA2025FedProGatewayServicer):
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.federations: set[str] = set()
        self.federation_logical_time_implementations: dict[str, str] = {}
        self.fom_modules: list[str] = []
        self.joined_federates: dict[str, str] = {}
        self.joined_federate_handles: dict[str, str] = {}
        self.joined_federate_types: dict[str, str] = {}
        self.next_federate_handle = 1
        self.next_object_instance_handle = 1000
        self.next_region_handle = 700
        self.object_classes = {
            "HLAobjectRoot.RouteTarget": "100",
            "HLAobjectRoot.Target": "101",
            "HLAobjectRoot.HLAmanager.HLAfederation": "102",
            "HLAobjectRoot.RateObject": "103",
            "HLAobjectRoot.HLAmanager.HLAfederate": "104",
            "HLAobjectRoot.SmokeObject": "105",
        }
        self.object_class_names = {value: key for key, value in self.object_classes.items()}
        self.attributes = {
            ("100", "Position"): "200",
            ("101", "Position"): "201",
            ("101", "RCS"): "202",
            ("102", "HLAfederationName"): "203",
            ("103", "Payload"): "204",
            ("102", "HLAfederatesInFederation"): "205",
            ("104", "HLAfederateName"): "206",
            ("105", "Payload"): "207",
        }
        self.next_object_class_handle = max(int(handle) for handle in self.object_classes.values()) + 1
        self.next_attribute_handle = max(int(handle) for handle in self.attributes.values()) + 1
        self.attribute_names = {(object_class, value): name for (object_class, name), value in self.attributes.items()}
        self.interactions = {
            "HLAinteractionRoot.TrackReport": "400",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation": "401",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata": "402",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata": "403",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestPublications": "404",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication": "405",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestSubscriptions": "406",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription": "407",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestInteractionsSent": "408",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsSent": "409",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestInteractionsReceived": "410",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsReceived": "411",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestUpdatesSent": "412",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportUpdatesSent": "413",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestReflectionsReceived": "414",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportReflectionsReceived": "415",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception": "416",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstanceInformation": "417",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation": "418",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesThatCanBeDeleted": "419",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesThatCanBeDeleted": "420",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesUpdated": "421",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesUpdated": "422",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesReflected": "423",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesReflected": "424",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestFOMmoduleData": "425",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFOMmoduleData": "426",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPoints": "427",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPoints": "428",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPointStatus": "429",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPointStatus": "430",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFederateLost": "431",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestFOMmoduleData": "432",
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportFOMmoduleData": "433",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionPublication": "434",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionSubscription": "435",
        }
        next_interaction_handle = 600
        for leaf in _MOM_FEDERATE_ADJUST_LEAVES:
            self.interactions[f"HLAinteractionRoot.HLAmanager.HLAfederate.HLAadjust.{leaf}"] = str(next_interaction_handle)
            next_interaction_handle += 1
        for leaf in _MOM_FEDERATION_ADJUST_LEAVES:
            self.interactions[f"HLAinteractionRoot.HLAmanager.HLAfederation.HLAadjust.{leaf}"] = str(next_interaction_handle)
            next_interaction_handle += 1
        for leaf in _MOM_FEDERATE_SERVICE_LEAVES:
            self.interactions[f"HLAinteractionRoot.HLAmanager.HLAfederate.HLAservice.{leaf}"] = str(next_interaction_handle)
            next_interaction_handle += 1
        self.next_interaction_handle = next_interaction_handle
        self.interaction_names = {value: key for key, value in self.interactions.items()}
        self.parameters = {
            ("400", "TrackId"): "500",
            ("401", "HLAfederate"): "501",
            ("401", "HLAservice"): "502",
            ("401", "HLAserialNumber"): "503",
            ("403", "HLAMIMdata"): "504",
            ("404", "HLAfederate"): "505",
            ("405", "HLAfederate"): "506",
            ("405", "HLAnumberOfClasses"): "507",
            ("405", "HLAobjectClass"): "508",
            ("405", "HLAattributeList"): "509",
            ("406", "HLAfederate"): "510",
            ("407", "HLAfederate"): "511",
            ("407", "HLAnumberOfClasses"): "512",
            ("407", "HLAobjectClass"): "513",
            ("407", "HLAactive"): "514",
            ("407", "HLAmaxUpdateRate"): "515",
            ("407", "HLAattributeList"): "516",
            ("408", "HLAfederate"): "517",
            ("409", "HLAfederate"): "518",
            ("409", "HLAinteractionsSent"): "519",
            ("410", "HLAfederate"): "520",
            ("411", "HLAfederate"): "521",
            ("411", "HLAinteractionsReceived"): "522",
            ("412", "HLAfederate"): "523",
            ("413", "HLAfederate"): "524",
            ("413", "HLAupdatesSent"): "525",
            ("414", "HLAfederate"): "526",
            ("415", "HLAfederate"): "527",
            ("415", "HLAreflectionsReceived"): "528",
            ("416", "HLAservice"): "529",
            ("416", "HLAexception"): "530",
            ("416", "HLAparameterError"): "531",
            ("418", "HLAfederate"): "532",
            ("418", "HLAobjectInstance"): "533",
            ("418", "HLAobjectClass"): "534",
            ("418", "HLAobjectInstanceName"): "535",
            ("418", "HLAattributeList"): "536",
            ("418", "HLAregisteredClass"): "567",
            ("418", "HLAknownClass"): "568",
            ("418", "HLAownedInstanceAttributeList"): "569",
            ("419", "HLAfederate"): "537",
            ("420", "HLAfederate"): "538",
            ("420", "HLAobjectInstanceCounts"): "539",
            ("421", "HLAfederate"): "540",
            ("422", "HLAfederate"): "541",
            ("422", "HLAobjectInstanceCounts"): "542",
            ("423", "HLAfederate"): "543",
            ("424", "HLAfederate"): "544",
            ("424", "HLAobjectInstanceCounts"): "545",
            ("425", "HLAfederate"): "546",
            ("425", "HLAFOMmoduleIndicator"): "547",
            ("426", "HLAfederate"): "548",
            ("426", "HLAFOMmoduleIndicator"): "549",
            ("426", "HLAFOMmoduleData"): "550",
            ("428", "HLAsynchronizationPoints"): "551",
            ("429", "HLAlabel"): "552",
            ("430", "HLAlabel"): "553",
            ("430", "HLAfederateList"): "554",
            ("430", "HLAfederateSynchronizationStatusList"): "555",
            ("431", "HLAfederate"): "556",
            ("431", "HLAfederateName"): "557",
            ("431", "HLAtimeStamp"): "558",
            ("431", "HLAfaultDescription"): "559",
            ("432", "HLAFOMmoduleIndicator"): "560",
            ("433", "HLAFOMmoduleIndicator"): "561",
            ("433", "HLAFOMmoduleData"): "562",
            ("434", "HLAfederate"): "563",
            ("434", "HLAinteractionClassList"): "564",
            ("435", "HLAfederate"): "565",
            ("435", "HLAinteractionClassList"): "566",
        }
        self.next_parameter_handle = 800
        self.parameter_names = {(interaction_class, value): name for (interaction_class, name), value in self.parameters.items()}
        self.dimensions = {"RoutingSpace": "300"}
        self.next_dimension_handle = max(int(handle) for handle in self.dimensions.values()) + 1
        self.dimension_names = {value: key for key, value in self.dimensions.items()}
        self.transportations = {"HLAreliable": "1", "HLAbestEffort": "2"}
        self.transportation_names = {value: key for key, value in self.transportations.items()}
        self.object_instances: dict[str, dict[str, str]] = {}
        self.mom_federation_object_handle: str | None = None
        self.mom_federation_name: str | None = None
        self.mom_federate_object_handles: dict[str, str] = {}
        self.federation_fom_designators: dict[str, tuple[str, ...]] = {}
        self.federation_fom_payloads: dict[str, tuple[str, ...]] = {}
        self.reserved_object_instance_names: dict[str, str] = {}
        self.attribute_owners: dict[tuple[str, str], str] = {}
        self.published_object_attributes: dict[str, set[str]] = {}
        self.handle_published_object_attributes: dict[str, dict[str, set[str]]] = {}
        self.subscribed_object_attributes: dict[str, set[str]] = {}
        self.subscribed_object_regions: dict[str, dict[str, set[str]]] = {}
        self.handle_subscribed_object_attributes: dict[str, dict[str, set[str]]] = {}
        self.handle_subscribed_object_update_rates: dict[str, dict[tuple[str, str], str]] = {}
        self.handle_last_update_rate_delivery_time: dict[str, dict[tuple[str, str], float]] = {}
        self.handle_subscribed_object_regions: dict[str, dict[str, dict[str, set[str]]]] = {}
        self.object_update_regions: dict[str, dict[str, set[str]]] = {}
        self.regions: dict[str, set[str]] = {}
        self.region_bounds: dict[str, dict[str, tuple[int, int]]] = {}
        self.published_interactions: set[str] = set()
        self.handle_published_interactions: dict[str, set[str]] = {}
        self.subscribed_interactions: set[str] = set()
        self.handle_subscribed_interactions: dict[str, set[str]] = {}
        self.handle_subscribed_interaction_regions: dict[str, dict[str, set[str]]] = {}
        self.subscribed_interaction_regions: dict[str, set[str]] = {}
        self.directed_interaction_region_gates: set[str] = set()
        self.published_directed_interactions: dict[str, set[str]] = {}
        self.handle_published_directed_interactions: dict[str, dict[str, set[str]]] = {}
        self.subscribed_directed_interactions: dict[str, set[str]] = {}
        self.handle_subscribed_directed_interactions: dict[str, dict[str, set[str]]] = {}
        self.unowned_attributes: set[tuple[str, str]] = set()
        self.offered_attributes: set[tuple[str, str]] = set()
        self.pending_attribute_acquisitions: dict[tuple[str, str], bytes] = {}
        self.pending_attribute_requesters: dict[tuple[str, str], str] = {}
        self.default_attribute_transportation: dict[tuple[str, str], str] = {}
        self.default_attribute_order: dict[tuple[str, str], int] = {}
        self.interaction_transportation: tuple[str, str] | None = None
        self.service_reporting = False
        self.handle_service_reporting: dict[str, bool] = {}
        self.handle_exception_reporting: dict[str, bool] = {}
        self.automatic_resign_directive = datatypes_pb2.NO_ACTION
        self.switch_states: dict[str, bool] = {
            "advisoriesUseKnownClass": False,
            "allowRelaxedDDM": False,
            "attributeRelevanceAdvisory": False,
            "attributeScopeAdvisory": False,
            "autoProvide": False,
            "conveyRegionDesignatorSets": False,
            "delaySubscriptionEvaluation": False,
            "exceptionReporting": True,
            "interactionRelevanceAdvisory": False,
            "nonRegulatedGrant": False,
            "objectClassRelevanceAdvisory": False,
            "sendServiceReportsToFile": False,
            "serviceReporting": False,
        }
        self.service_report_serial = 1
        self.next_retraction_handle = 1
        self.current_time = datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:0")
        self.lookahead = datatypes_pb2.LogicalTimeInterval(data=b"HLAinteger64Interval:1")
        self.time_regulating = False
        self.time_constrained = False
        self.asynchronous_delivery_enabled = False
        self.handle_current_times: dict[str, datatypes_pb2.LogicalTime] = {}
        self.handle_lookahead: dict[str, datatypes_pb2.LogicalTimeInterval] = {}
        self.handle_time_regulating: dict[str, bool] = {}
        self.handle_time_constrained: dict[str, bool] = {}
        self.handle_asynchronous_delivery_enabled: dict[str, bool] = {}
        self.handle_pending_time_advance: dict[str, tuple[str, datatypes_pb2.LogicalTime]] = {}
        self.callback_delivery_enabled = True
        self.peer_callback_delivery_enabled: dict[str, bool] = {}
        self.handle_locally_deleted_objects: dict[str, set[str]] = {}
        self.peer_federate_handles: dict[str, str] = {}
        self.updates_sent = 0
        self.reflections_received = 0
        self.interactions_sent = 0
        self.interactions_received = 0
        self.object_instances_updated = 0
        self.object_instances_reflected = 0
        self.handle_updates_sent: dict[str, int] = {}
        self.handle_reflections_received: dict[str, int] = {}
        self.handle_interactions_sent: dict[str, int] = {}
        self.handle_interactions_received: dict[str, int] = {}
        self.handle_object_instances_updated: dict[str, int] = {}
        self.handle_object_instances_reflected: dict[str, int] = {}
        self.queued_tso_callbacks: dict[str, tuple[float, list[callback_pb2.CallbackRequest]]] = {}
        self.delivered_retractions: set[str] = set()
        self.delivered_retraction_targets: dict[str, frozenset[str]] = {}
        self.requested_retractions: set[str] = set()
        self.saved_labels: set[str] = set()
        self.saved_snapshots: dict[str, _FederationSnapshot] = {}
        self.next_save_name: str | None = None
        self.next_save_time: datatypes_pb2.LogicalTime | None = None
        self.save_label: str | None = None
        self.save_status: dict[str, int] = {}
        self.restore_label: str | None = None
        self.restore_status: dict[str, int] = {}
        self.synchronization_points: dict[str, dict[str, bytes | bool | set[str]]] = {}
        self.attribute_scope_state: dict[tuple[str, str, str], bool] = {}
        self.callback_queue: list[callback_pb2.CallbackRequest] = []
        self.callback_targets: dict[int, tuple[frozenset[str] | None, frozenset[str] | None]] = {}

    def _install_fom_catalog_handles(self, catalog: object) -> None:
        for class_name, spec in sorted(getattr(catalog, "object_classes", {}).items()):
            class_handle = self.object_classes.get(class_name)
            if class_handle is None:
                class_handle = str(self.next_object_class_handle)
                self.next_object_class_handle += 1
                self.object_classes[class_name] = class_handle
                self.object_class_names[class_handle] = class_name
            for attribute_name in getattr(spec, "attributes", ()):
                key = (class_handle, attribute_name)
                if key in self.attributes:
                    continue
                attribute_handle = str(self.next_attribute_handle)
                self.next_attribute_handle += 1
                self.attributes[key] = attribute_handle
                self.attribute_names[(class_handle, attribute_handle)] = attribute_name

        for interaction_name, spec in sorted(getattr(catalog, "interaction_classes", {}).items()):
            interaction_handle = self.interactions.get(interaction_name)
            if interaction_handle is None:
                interaction_handle = str(self.next_interaction_handle)
                self.next_interaction_handle += 1
                self.interactions[interaction_name] = interaction_handle
                self.interaction_names[interaction_handle] = interaction_name
            for parameter_name in getattr(spec, "parameters", ()):
                key = (interaction_handle, parameter_name)
                if key in self.parameters:
                    continue
                parameter_handle = str(self.next_parameter_handle)
                self.next_parameter_handle += 1
                self.parameters[key] = parameter_handle
                self.parameter_names[(interaction_handle, parameter_handle)] = parameter_name

        for dimension_name in sorted(getattr(catalog, "dimensions", ())):
            if dimension_name in self.dimensions:
                continue
            dimension_handle = str(self.next_dimension_handle)
            self.next_dimension_handle += 1
            self.dimensions[dimension_name] = dimension_handle
            self.dimension_names[dimension_handle] = dimension_name

    def Call(self, request, context):  # noqa: N802 - grpc generated naming
        request_kind = request.WhichOneof("callRequest")
        peer = self._context_peer(context)
        if request_kind is not None:
            self.calls.append(request_kind)
        if request_kind in {
            "connectRequest",
            "connectWithCredentialsRequest",
            "connectWithConfigurationRequest",
            "connectWithConfigurationAndCredentialsRequest",
        }:
            if peer in self.peer_callback_delivery_enabled:
                return self._error("AlreadyConnected", peer)
            self.peer_callback_delivery_enabled[peer] = True
            return rti_pb2.CallResponse(connectResponse=rti_pb2.ConnectResponse())
        if request_kind == "disconnectRequest":
            if peer in self.peer_federate_handles:
                return self._error("FederateIsExecutionMember", peer)
            self.peer_callback_delivery_enabled.pop(peer, None)
            self._remove_peer_federate(peer)
            return rti_pb2.CallResponse(disconnectResponse=rti_pb2.DisconnectResponse())
        if request_kind in {
            "createFederationExecutionRequest",
            "createFederationExecutionWithTimeRequest",
            "createFederationExecutionWithModulesRequest",
            "createFederationExecutionWithModulesAndTimeRequest",
            "createFederationExecutionWithMIMRequest",
            "createFederationExecutionWithMIMAndTimeRequest",
        }:
            payload = getattr(request, request_kind)
            if payload.federationName in self.federations:
                return self._error("FederationExecutionAlreadyExists", payload.federationName)
            try:
                if request_kind in {
                    "createFederationExecutionRequest",
                    "createFederationExecutionWithTimeRequest",
                }:
                    fom_designator = payload.fomModule.url or payload.fomModule.file.name
                    fom_designators = (fom_designator,) if fom_designator else ()
                else:
                    fom_designators = tuple(_fom_module_designators(payload.fomModules))
                if not fom_designators:
                    return self._error("InvalidFOM", "At least one FOM module designator is required")
                mim_designator = ""
                if request_kind in {
                    "createFederationExecutionWithMIMRequest",
                    "createFederationExecutionWithMIMAndTimeRequest",
                }:
                    mim_designator = payload.mimModule.url or payload.mimModule.file.name
                    if mim_designator in {"HLAstandardMIM", "HLAstandardMIM.xml"}:
                        return self._error("DesignatorIsHLAstandardMIM", "Explicit MIM designator shall not be HLAstandardMIM")
                    if not mim_designator:
                        return self._error("InvalidMIM", "Explicit createFederationExecutionWithMIM requires a MIM module designator")
                    resolved_mim = _resolve_2025_fom_modules((mim_designator,), mim=True)[0]
                else:
                    fom = import_module("hla.fom")
                    resolved_mim = fom.standard_mim_module()
                resolved_foms = _resolve_2025_fom_modules(fom_designators, mim=False)
                merged_catalog = _merge_2025_fom_modules(resolved_foms, mim_module=resolved_mim)
            except RuntimeError as exc:
                name, details = exc.args[0]
                return self._error(name, details)
            self._install_fom_catalog_handles(merged_catalog)
            self.federations.add(payload.federationName)
            self.federation_logical_time_implementations[payload.federationName] = getattr(
                payload,
                "logicalTimeImplementationName",
                "",
            ) or "HLAinteger64Time"
            self.fom_modules = list(fom_designators)
            self.federation_fom_designators[payload.federationName] = tuple(fom_designators)
            self.federation_fom_payloads[payload.federationName] = tuple(
                _module_payload_text(module, designator)
                for module, designator in zip(resolved_foms, fom_designators, strict=False)
            )
            self._ensure_mom_federation_object(payload.federationName)
            if request_kind == "createFederationExecutionWithTimeRequest":
                return rti_pb2.CallResponse(createFederationExecutionWithTimeResponse=rti_pb2.CreateFederationExecutionWithTimeResponse())
            if request_kind == "createFederationExecutionRequest":
                return rti_pb2.CallResponse(createFederationExecutionResponse=rti_pb2.CreateFederationExecutionResponse())
            if request_kind == "createFederationExecutionWithModulesAndTimeRequest":
                return rti_pb2.CallResponse(createFederationExecutionWithModulesAndTimeResponse=rti_pb2.CreateFederationExecutionWithModulesAndTimeResponse())
            if request_kind == "createFederationExecutionWithMIMAndTimeRequest":
                return rti_pb2.CallResponse(createFederationExecutionWithMIMAndTimeResponse=rti_pb2.CreateFederationExecutionWithMIMAndTimeResponse())
            if request_kind == "createFederationExecutionWithMIMRequest":
                return rti_pb2.CallResponse(createFederationExecutionWithMIMResponse=rti_pb2.CreateFederationExecutionWithMIMResponse())
            return rti_pb2.CallResponse(createFederationExecutionWithModulesResponse=rti_pb2.CreateFederationExecutionWithModulesResponse())
        if request_kind == "listFederationExecutionsRequest":
            report = datatypes_pb2.FederationExecutionInformationSet(
                federationExecutionInformation=[
                    datatypes_pb2.FederationExecutionInformation(
                        federationExecutionName=federation_name,
                        logicalTimeImplementationName=self.federation_logical_time_implementations.get(
                            federation_name,
                            "HLAinteger64Time",
                        ),
                    )
                    for federation_name in sorted(self.federations)
                ]
            )
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    reportFederationExecutions=callback_pb2.ReportFederationExecutions(report=report)
                ),
                target_peers={peer},
            )
            return rti_pb2.CallResponse(listFederationExecutionsResponse=rti_pb2.ListFederationExecutionsResponse())
        if request_kind == "listFederationExecutionMembersRequest":
            federation_name = request.listFederationExecutionMembersRequest.federationName
            if federation_name not in self.federations:
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        reportFederationExecutionDoesNotExist=callback_pb2.ReportFederationExecutionDoesNotExist(
                            federationName=federation_name
                        )
                    ),
                    target_peers={peer},
                )
            else:
                report = datatypes_pb2.FederationExecutionMemberInformationSet(
                    federationExecutionMemberInformation=[
                        datatypes_pb2.FederationExecutionMemberInformation(
                            federateName=federate_name,
                            federateType=self.joined_federate_types.get(handle, ""),
                        )
                        for handle, federate_name in sorted(self.joined_federate_handles.items(), key=lambda item: int(item[0]))
                        if self.joined_federates.get(federate_name) == federation_name
                    ]
                )
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        reportFederationExecutionMembers=callback_pb2.ReportFederationExecutionMembers(
                            federationName=federation_name,
                            report=report,
                        )
                    ),
                    target_peers={peer},
                )
            return rti_pb2.CallResponse(
                listFederationExecutionMembersResponse=rti_pb2.ListFederationExecutionMembersResponse()
            )
        if request_kind in {
            "joinFederationExecutionRequest",
            "joinFederationExecutionWithNameRequest",
            "joinFederationExecutionWithModulesRequest",
            "joinFederationExecutionWithNameAndModulesRequest",
        }:
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer in self.peer_federate_handles:
                return self._error("FederateAlreadyExecutionMember", peer)
            payload = getattr(request, request_kind)
            federation_name = payload.federationName
            if self.save_label is not None or self.next_save_name is not None:
                return self._error("SaveInProgress", federation_name)
            if self.restore_label is not None:
                return self._error("RestoreInProgress", federation_name)
            if federation_name not in self.federations:
                return self._error("FederationExecutionDoesNotExist", federation_name)
            if request_kind in {"joinFederationExecutionWithModulesRequest", "joinFederationExecutionWithNameAndModulesRequest"}:
                fom_designators = tuple(_fom_module_designators(payload.additionalFomModules))
                if fom_designators:
                    try:
                        fom = import_module("hla.fom")
                        resolved_join_foms = _resolve_2025_fom_modules(fom_designators, mim=False)
                        base_designators = self.federation_fom_designators.get(federation_name, ())
                        resolved_base_foms = _resolve_2025_fom_modules(base_designators, mim=False)
                        merged_catalog = _merge_2025_fom_modules(
                            resolved_base_foms + resolved_join_foms,
                            mim_module=fom.standard_mim_module(),
                        )
                    except RuntimeError as exc:
                        name, details = exc.args[0]
                        return self._error(name, details)
                    self._install_fom_catalog_handles(merged_catalog)
            federate_name = getattr(payload, "federateName", "") or f"fedpro-federate-{self.next_federate_handle}"
            if federate_name in self.joined_federates:
                return self._error("FederateNameAlreadyInUse", federate_name)
            handle = self.next_federate_handle
            self.next_federate_handle += 1
            self.joined_federates[federate_name] = federation_name
            self.joined_federate_handles[str(handle)] = federate_name
            self.joined_federate_types[str(handle)] = payload.federateType
            self._ensure_mom_federation_object(federation_name)
            mom_federate_object = self._ensure_mom_federate_object(str(handle), federate_name)
            self.peer_federate_handles[peer] = str(handle)
            self.handle_service_reporting.setdefault(str(handle), False)
            self.handle_exception_reporting.setdefault(str(handle), True)
            self.handle_updates_sent.setdefault(str(handle), 0)
            self.handle_reflections_received.setdefault(str(handle), 0)
            self.handle_interactions_sent.setdefault(str(handle), 0)
            self.handle_interactions_received.setdefault(str(handle), 0)
            self.handle_object_instances_updated.setdefault(str(handle), 0)
            self.handle_object_instances_reflected.setdefault(str(handle), 0)
            self.handle_current_times.setdefault(str(handle), datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:0"))
            self.handle_lookahead.setdefault(str(handle), datatypes_pb2.LogicalTimeInterval(data=b"HLAinteger64Interval:1"))
            self.handle_time_regulating.setdefault(str(handle), False)
            self.handle_time_constrained.setdefault(str(handle), False)
            self.handle_asynchronous_delivery_enabled.setdefault(str(handle), False)
            self._sync_time_globals(str(handle))
            for label, record in self.synchronization_points.items():
                synchronized = record.get("synchronized", False)
                dynamic_members = record.get("dynamic_members", False)
                if not isinstance(synchronized, bool) or synchronized:
                    continue
                if not isinstance(dynamic_members, bool) or not dynamic_members:
                    continue
                federates = record.get("federates", set())
                if isinstance(federates, set):
                    federates.add(str(handle))
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        announceSynchronizationPoint=callback_pb2.AnnounceSynchronizationPoint(
                            synchronizationPointLabel=label,
                            userSuppliedTag=record.get("tag", b"") if isinstance(record.get("tag", b""), bytes) else b"",
                        )
                    ),
                    target_handles={str(handle)},
                )
            result = datatypes_pb2.JoinResult(
                federateHandle=datatypes_pb2.FederateHandle(data=str(handle).encode("ascii")),
                logicalTimeImplementationName="HLAinteger64Time",
            )
            discovery_targets = self._discovery_target_handles(
                self.object_classes["HLAobjectRoot.HLAmanager.HLAfederate"],
                exclude_handle=str(handle),
            )
            if discovery_targets:
                self._queue_discovery(
                    mom_federate_object,
                    self.object_classes["HLAobjectRoot.HLAmanager.HLAfederate"],
                    self.object_instances[mom_federate_object]["name"],
                    target_handles=discovery_targets,
                )
            if request_kind in {"joinFederationExecutionWithNameRequest", "joinFederationExecutionWithNameAndModulesRequest"}:
                return rti_pb2.CallResponse(joinFederationExecutionWithNameResponse=rti_pb2.JoinFederationExecutionWithNameResponse(result=result))
            return rti_pb2.CallResponse(joinFederationExecutionResponse=rti_pb2.JoinFederationExecutionResponse(result=result))
        if request_kind == "resignFederationExecutionRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            action = request.resignFederationExecutionRequest.resignAction
            try:
                datatypes_pb2.ResignAction.Name(action)
            except ValueError:
                return self._error("InvalidResignAction", str(action))
            current_handle = self._current_federate_handle(peer)
            if action == datatypes_pb2.NO_ACTION:
                if any(requester_handle == current_handle for requester_handle in self.pending_attribute_requesters.values()):
                    return self._error(
                        "OwnershipAcquisitionPending",
                        "Cannot resign with pending ownership acquisition using NO_ACTION",
                    )
                if any(owner_handle == current_handle for owner_handle in self.attribute_owners.values()):
                    return self._error(
                        "FederateOwnsAttributes",
                        "Cannot resign while owning attributes using NO_ACTION",
                    )
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    federateResigned=callback_pb2.FederateResigned(
                        reasonForResignDescription=datatypes_pb2.ResignAction.Name(action)
                    )
                ),
                target_peers={peer},
            )
            self._apply_resign_action(action)
            self._remove_peer_federate(
                peer,
                preserve_owned_attributes=(action == datatypes_pb2.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS),
            )
            return rti_pb2.CallResponse(resignFederationExecutionResponse=rti_pb2.ResignFederationExecutionResponse())
        if request_kind == "destroyFederationExecutionRequest":
            payload = request.destroyFederationExecutionRequest
            if payload.federationName not in self.federations:
                return self._error("FederationExecutionDoesNotExist", payload.federationName)
            if self.joined_federates:
                return self._error("FederatesCurrentlyJoined", payload.federationName)
            self.federations.discard(payload.federationName)
            self.federation_logical_time_implementations.pop(payload.federationName, None)
            self.federation_fom_designators.pop(payload.federationName, None)
            self.federation_fom_payloads.pop(payload.federationName, None)
            if not self.federations or self.mom_federation_name == payload.federationName:
                self.mom_federation_name = None
                self.mom_federation_object_handle = None
            return rti_pb2.CallResponse(destroyFederationExecutionResponse=rti_pb2.DestroyFederationExecutionResponse())
        if request_kind == "getFederateHandleRequest":
            name = request.getFederateHandleRequest.federateName
            for handle, federate_name in self.joined_federate_handles.items():
                if federate_name == name:
                    return rti_pb2.CallResponse(
                        getFederateHandleResponse=rti_pb2.GetFederateHandleResponse(
                            result=_handle(datatypes_pb2.FederateHandle, handle)
                        )
                    )
            if not self.joined_federate_handles:
                return rti_pb2.CallResponse(
                    getFederateHandleResponse=rti_pb2.GetFederateHandleResponse(
                        result=_handle(datatypes_pb2.FederateHandle, "42")
                    )
                )
            return self._error("NameNotFound", name)
        if request_kind == "getFederateNameRequest":
            handle = request.getFederateNameRequest.federate.data.decode("ascii")
            try:
                return rti_pb2.CallResponse(getFederateNameResponse=rti_pb2.GetFederateNameResponse(result=self.joined_federate_handles[handle]))
            except KeyError:
                return self._error("FederateNotExecutionMember", handle)
        if request_kind == "getObjectClassHandleRequest":
            name = request.getObjectClassHandleRequest.objectClassName
            try:
                handle = self.object_classes[name]
            except KeyError:
                return self._error("NameNotFound", name)
            self._queue_service_report("getObjectClassHandle", peer=peer)
            return rti_pb2.CallResponse(
                getObjectClassHandleResponse=rti_pb2.GetObjectClassHandleResponse(
                    result=_handle(datatypes_pb2.ObjectClassHandle, handle)
                )
            )
        if request_kind == "getObjectClassNameRequest":
            handle = request.getObjectClassNameRequest.objectClass.data.decode("ascii")
            return rti_pb2.CallResponse(
                getObjectClassNameResponse=rti_pb2.GetObjectClassNameResponse(
                    result=self.object_class_names.get(handle, "")
                )
            )
        if request_kind == "getObjectInstanceHandleRequest":
            name = request.getObjectInstanceHandleRequest.objectInstanceName
            current_handle = self._current_federate_handle(peer)
            if name == self.mom_federation_name and self.mom_federation_object_handle is not None:
                return rti_pb2.CallResponse(
                    getObjectInstanceHandleResponse=rti_pb2.GetObjectInstanceHandleResponse(
                        result=_handle(datatypes_pb2.ObjectInstanceHandle, self.mom_federation_object_handle)
                    )
                )
            for handle, record in self.object_instances.items():
                if record["name"] == name:
                    if handle in self.handle_locally_deleted_objects.get(current_handle, set()):
                        return self._error("ObjectInstanceNotKnown", name)
                    return rti_pb2.CallResponse(
                        getObjectInstanceHandleResponse=rti_pb2.GetObjectInstanceHandleResponse(
                            result=_handle(datatypes_pb2.ObjectInstanceHandle, handle)
                        )
                    )
            return self._error("ObjectInstanceNotKnown", name)
        if request_kind == "getObjectInstanceNameRequest":
            handle = request.getObjectInstanceNameRequest.objectInstance.data.decode("ascii")
            current_handle = self._current_federate_handle(peer)
            if handle == self.mom_federation_object_handle and self.mom_federation_name is not None:
                return rti_pb2.CallResponse(getObjectInstanceNameResponse=rti_pb2.GetObjectInstanceNameResponse(result=self.mom_federation_name))
            record = self.object_instances.get(handle)
            if record is None:
                return self._error("ObjectInstanceNotKnown", handle)
            if handle in self.handle_locally_deleted_objects.get(current_handle, set()):
                return self._error("ObjectInstanceNotKnown", handle)
            return rti_pb2.CallResponse(getObjectInstanceNameResponse=rti_pb2.GetObjectInstanceNameResponse(result=record["name"]))
        if request_kind == "getAttributeHandleRequest":
            payload = request.getAttributeHandleRequest
            object_class = payload.objectClass.data.decode("ascii")
            try:
                handle = self.attributes[(object_class, payload.attributeName)]
            except KeyError:
                return self._error("NameNotFound", payload.attributeName)
            return rti_pb2.CallResponse(
                getAttributeHandleResponse=rti_pb2.GetAttributeHandleResponse(
                    result=_handle(datatypes_pb2.AttributeHandle, handle)
                )
            )
        if request_kind == "getAttributeNameRequest":
            payload = request.getAttributeNameRequest
            object_class = payload.objectClass.data.decode("ascii")
            attribute = payload.attribute.data.decode("ascii")
            try:
                name = self.attribute_names[(object_class, attribute)]
            except KeyError:
                return self._error("AttributeNotDefined", attribute)
            return rti_pb2.CallResponse(getAttributeNameResponse=rti_pb2.GetAttributeNameResponse(result=name))
        if request_kind == "getInteractionClassHandleRequest":
            name = _canonical_mom_interaction_name(request.getInteractionClassHandleRequest.interactionClassName)
            try:
                handle = self.interactions[name]
            except KeyError:
                return self._error("NameNotFound", name)
            return rti_pb2.CallResponse(
                getInteractionClassHandleResponse=rti_pb2.GetInteractionClassHandleResponse(
                    result=_handle(datatypes_pb2.InteractionClassHandle, handle)
                )
            )
        if request_kind == "getInteractionClassNameRequest":
            handle = request.getInteractionClassNameRequest.interactionClass.data.decode("ascii")
            return rti_pb2.CallResponse(getInteractionClassNameResponse=rti_pb2.GetInteractionClassNameResponse(result=self.interaction_names.get(handle, "")))
        if request_kind == "getParameterHandleRequest":
            payload = request.getParameterHandleRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            interaction_name = self.interaction_names.get(interaction_class, "")
            parameter_name = _canonical_mom_parameter_name(interaction_name, payload.parameterName)
            try:
                handle = self.parameters[(interaction_class, parameter_name)]
            except KeyError:
                if ".HLAmanager." not in interaction_name:
                    return self._error("NameNotFound", parameter_name)
                handle = str(self.next_parameter_handle)
                self.next_parameter_handle += 1
                self.parameters[(interaction_class, parameter_name)] = handle
                self.parameter_names[(interaction_class, handle)] = parameter_name
            return rti_pb2.CallResponse(
                getParameterHandleResponse=rti_pb2.GetParameterHandleResponse(result=_handle(datatypes_pb2.ParameterHandle, handle))
            )
        if request_kind == "getParameterNameRequest":
            payload = request.getParameterNameRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            parameter = payload.parameter.data.decode("ascii")
            try:
                name = self.parameter_names[(interaction_class, parameter)]
            except KeyError:
                return self._error("InteractionParameterNotDefined", parameter)
            return rti_pb2.CallResponse(getParameterNameResponse=rti_pb2.GetParameterNameResponse(result=name))
        if request_kind in {
            "registerFederationSynchronizationPointRequest",
            "registerFederationSynchronizationPointWithSetRequest",
        }:
            payload = getattr(request, request_kind)
            if payload.synchronizationPointLabel in self.synchronization_points:
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        synchronizationPointRegistrationFailed=callback_pb2.SynchronizationPointRegistrationFailed(
                            synchronizationPointLabel=payload.synchronizationPointLabel,
                            reason=datatypes_pb2.SYNCHRONIZATION_POINT_LABEL_NOT_UNIQUE,
                        )
                    ),
                    target_handles={self._current_federate_handle(peer)},
                )
                if request_kind == "registerFederationSynchronizationPointWithSetRequest":
                    return rti_pb2.CallResponse(
                        registerFederationSynchronizationPointWithSetResponse=rti_pb2.RegisterFederationSynchronizationPointWithSetResponse()
                    )
                return rti_pb2.CallResponse(
                    registerFederationSynchronizationPointResponse=rti_pb2.RegisterFederationSynchronizationPointResponse()
                )
            target_federates = set(self._joined_handle_values())
            dynamic_members = request_kind == "registerFederationSynchronizationPointRequest"
            if request_kind == "registerFederationSynchronizationPointWithSetRequest":
                target_federates = {
                    item.data.decode("ascii") for item in payload.synchronizationSet.federateHandle if item.data
                }
                if not target_federates:
                    target_federates = set(self._joined_handle_values())
                    dynamic_members = True
                else:
                    dynamic_members = False
            record = self._synchronization_point_record(payload.synchronizationPointLabel)
            record["tag"] = bytes(payload.userSuppliedTag)
            record["federates"] = target_federates
            record["achieved"].clear()
            record["failed"].clear()
            record["synchronized"] = False
            record["dynamic_members"] = dynamic_members
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    synchronizationPointRegistrationSucceeded=callback_pb2.SynchronizationPointRegistrationSucceeded(
                        synchronizationPointLabel=payload.synchronizationPointLabel
                    )
                ),
                target_handles={self._current_federate_handle(peer)},
            )
            self._enqueue_callback_per_handle(
                callback_pb2.CallbackRequest(
                    announceSynchronizationPoint=callback_pb2.AnnounceSynchronizationPoint(
                        synchronizationPointLabel=payload.synchronizationPointLabel,
                        userSuppliedTag=payload.userSuppliedTag,
                    )
                ),
                target_handles=target_federates,
            )
            if request_kind == "registerFederationSynchronizationPointWithSetRequest":
                return rti_pb2.CallResponse(
                    registerFederationSynchronizationPointWithSetResponse=rti_pb2.RegisterFederationSynchronizationPointWithSetResponse()
                )
            return rti_pb2.CallResponse(
                registerFederationSynchronizationPointResponse=rti_pb2.RegisterFederationSynchronizationPointResponse()
            )
        if request_kind == "synchronizationPointAchievedRequest":
            payload = request.synchronizationPointAchievedRequest
            record = self._synchronization_point_record(payload.synchronizationPointLabel)
            if payload.successfully:
                record["achieved"].add(self._current_federate_handle(peer))
            else:
                record["failed"].add(self._current_federate_handle(peer))
            self._queue_federation_synchronized_if_ready(payload.synchronizationPointLabel)
            return rti_pb2.CallResponse(synchronizationPointAchievedResponse=rti_pb2.SynchronizationPointAchievedResponse())
        if request_kind == "getDimensionHandleRequest":
            name = request.getDimensionHandleRequest.dimensionName
            if name == "HLAdefaultRoutingSpace":
                name = "RoutingSpace"
            try:
                handle = self.dimensions[name]
            except KeyError:
                return self._error("NameNotFound", name)
            return rti_pb2.CallResponse(getDimensionHandleResponse=rti_pb2.GetDimensionHandleResponse(result=_handle(datatypes_pb2.DimensionHandle, handle)))
        if request_kind == "getDimensionNameRequest":
            handle = request.getDimensionNameRequest.dimension.data.decode("ascii")
            try:
                return rti_pb2.CallResponse(getDimensionNameResponse=rti_pb2.GetDimensionNameResponse(result=self.dimension_names[handle]))
            except KeyError:
                return self._error("InvalidDimensionHandle", handle)
        if request_kind == "getAvailableDimensionsForObjectClassRequest":
            return rti_pb2.CallResponse(
                getAvailableDimensionsForObjectClassResponse=rti_pb2.GetAvailableDimensionsForObjectClassResponse(
                    result=_dimension_set(("300",))
                )
            )
        if request_kind == "getAvailableDimensionsForInteractionClassRequest":
            return rti_pb2.CallResponse(
                getAvailableDimensionsForInteractionClassResponse=rti_pb2.GetAvailableDimensionsForInteractionClassResponse(
                    result=_dimension_set(("300",))
                )
            )
        if request_kind == "getDimensionUpperBoundRequest":
            return rti_pb2.CallResponse(getDimensionUpperBoundResponse=rti_pb2.GetDimensionUpperBoundResponse(result=1024))
        if request_kind == "createRegionRequest":
            payload = request.createRegionRequest
            handle = str(self.next_region_handle)
            self.next_region_handle += 1
            dimensions = {dimension.data.decode("ascii") for dimension in payload.dimensions.dimensionHandle}
            self.regions[handle] = dimensions
            self.region_bounds[handle] = {dimension: (0, 1024) for dimension in dimensions}
            return rti_pb2.CallResponse(
                createRegionResponse=rti_pb2.CreateRegionResponse(
                    result=_handle(datatypes_pb2.RegionHandle, handle)
                )
            )
        if request_kind == "getDimensionHandleSetRequest":
            region = request.getDimensionHandleSetRequest.region.data.decode("ascii")
            return rti_pb2.CallResponse(
                getDimensionHandleSetResponse=rti_pb2.GetDimensionHandleSetResponse(
                    result=_dimension_set(tuple(sorted(self.regions.get(region, ()))))
                )
            )
        if request_kind == "setRangeBoundsRequest":
            payload = request.setRangeBoundsRequest
            region = payload.region.data.decode("ascii")
            dimension = payload.dimension.data.decode("ascii")
            self.region_bounds.setdefault(region, {})[dimension] = (
                int(payload.rangeBounds.lower),
                int(payload.rangeBounds.upper),
            )
            return rti_pb2.CallResponse(setRangeBoundsResponse=rti_pb2.SetRangeBoundsResponse())
        if request_kind == "getRangeBoundsRequest":
            payload = request.getRangeBoundsRequest
            region = payload.region.data.decode("ascii")
            dimension = payload.dimension.data.decode("ascii")
            lower, upper = self.region_bounds.get(region, {}).get(dimension, (0, 1024))
            return rti_pb2.CallResponse(
                getRangeBoundsResponse=rti_pb2.GetRangeBoundsResponse(
                    result=datatypes_pb2.RangeBounds(lower=lower, upper=upper)
                )
            )
        if request_kind == "commitRegionModificationsRequest":
            self._queue_attribute_scope_advisories()
            return rti_pb2.CallResponse(commitRegionModificationsResponse=rti_pb2.CommitRegionModificationsResponse())
        if request_kind == "deleteRegionRequest":
            region = request.deleteRegionRequest.region.data.decode("ascii")
            self.regions.pop(region, None)
            self.region_bounds.pop(region, None)
            self._remove_region_references(region)
            self._queue_attribute_scope_advisories()
            return rti_pb2.CallResponse(deleteRegionResponse=rti_pb2.DeleteRegionResponse())
        if request_kind == "getTransportationTypeHandleRequest":
            name = request.getTransportationTypeHandleRequest.transportationTypeName
            try:
                handle = self.transportations[name]
            except KeyError:
                return self._error("InvalidTransportationName", name)
            return rti_pb2.CallResponse(
                getTransportationTypeHandleResponse=rti_pb2.GetTransportationTypeHandleResponse(
                    result=_handle(datatypes_pb2.TransportationTypeHandle, handle)
                )
            )
        if request_kind == "getTransportationTypeNameRequest":
            handle = request.getTransportationTypeNameRequest.transportationType.data.decode("ascii")
            try:
                return rti_pb2.CallResponse(
                    getTransportationTypeNameResponse=rti_pb2.GetTransportationTypeNameResponse(
                        result=self.transportation_names[handle]
                    )
                )
            except KeyError:
                return self._error("InvalidTransportationTypeHandle", handle)
        if request_kind == "getOrderTypeRequest":
            name = request.getOrderTypeRequest.orderTypeName
            normalized = str(name).strip().lower()
            if normalized in {"hlareceive", "receive", "ro"}:
                return rti_pb2.CallResponse(getOrderTypeResponse=rti_pb2.GetOrderTypeResponse(result=datatypes_pb2.RECEIVE))
            if normalized in {"hlatimestamp", "timestamp", "tso"}:
                return rti_pb2.CallResponse(getOrderTypeResponse=rti_pb2.GetOrderTypeResponse(result=datatypes_pb2.TIMESTAMP))
            return self._error("InvalidOrderType", name)
        if request_kind == "getOrderNameRequest":
            order = request.getOrderNameRequest.orderType
            if order == datatypes_pb2.RECEIVE:
                return rti_pb2.CallResponse(getOrderNameResponse=rti_pb2.GetOrderNameResponse(result="HLAreceive"))
            if order == datatypes_pb2.TIMESTAMP:
                return rti_pb2.CallResponse(getOrderNameResponse=rti_pb2.GetOrderNameResponse(result="HLAtimestamp"))
            return self._error("InvalidOrderType", str(order))
        if request_kind == "getUpdateRateValueRequest":
            designator = request.getUpdateRateValueRequest.updateRateDesignator
            normalized = designator.strip().lower()
            if normalized not in {"hladefaultupdaterate", "hladefault", "default", "fast"}:
                return self._error("InvalidUpdateRateDesignator", designator)
            value = self._update_rate_hz(designator)
            return rti_pb2.CallResponse(getUpdateRateValueResponse=rti_pb2.GetUpdateRateValueResponse(result=value))
        if request_kind == "getUpdateRateValueForAttributeRequest":
            return rti_pb2.CallResponse(getUpdateRateValueForAttributeResponse=rti_pb2.GetUpdateRateValueForAttributeResponse(result=0.0))
        if request_kind == "getKnownObjectClassHandleRequest":
            object_instance = request.getKnownObjectClassHandleRequest.objectInstance.data.decode("ascii")
            current_handle = self._current_federate_handle(peer)
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            if object_instance in self.handle_locally_deleted_objects.get(current_handle, set()):
                return self._error("ObjectInstanceNotKnown", object_instance)
            return rti_pb2.CallResponse(
                getKnownObjectClassHandleResponse=rti_pb2.GetKnownObjectClassHandleResponse(
                    result=_handle(datatypes_pb2.ObjectClassHandle, record["objectClass"])
                )
            )
        if request_kind == "normalizeServiceGroupRequest":
            return rti_pb2.CallResponse(
                normalizeServiceGroupResponse=rti_pb2.NormalizeServiceGroupResponse(
                    result=request.normalizeServiceGroupRequest.serviceGroup
                )
            )
        if request_kind == "normalizeFederateHandleRequest":
            return rti_pb2.CallResponse(
                normalizeFederateHandleResponse=rti_pb2.NormalizeFederateHandleResponse(result=int(request.normalizeFederateHandleRequest.federate.data.decode("ascii")))
            )
        if request_kind == "normalizeObjectClassHandleRequest":
            return rti_pb2.CallResponse(
                normalizeObjectClassHandleResponse=rti_pb2.NormalizeObjectClassHandleResponse(result=int(request.normalizeObjectClassHandleRequest.objectClass.data.decode("ascii")))
            )
        if request_kind == "normalizeInteractionClassHandleRequest":
            return rti_pb2.CallResponse(
                normalizeInteractionClassHandleResponse=rti_pb2.NormalizeInteractionClassHandleResponse(result=int(request.normalizeInteractionClassHandleRequest.interactionClass.data.decode("ascii")))
            )
        if request_kind == "normalizeObjectInstanceHandleRequest":
            return rti_pb2.CallResponse(
                normalizeObjectInstanceHandleResponse=rti_pb2.NormalizeObjectInstanceHandleResponse(result=int(request.normalizeObjectInstanceHandleRequest.objectInstance.data.decode("ascii")))
            )
        if request_kind == "modifyLookaheadRequest":
            handle = self._current_federate_handle(peer)
            if not self.handle_time_regulating.get(handle, False):
                return self._error("TimeRegulationIsNotEnabled", "Time regulation is not enabled")
            self._set_handle_lookahead(handle, request.modifyLookaheadRequest.lookahead)
            return rti_pb2.CallResponse(modifyLookaheadResponse=rti_pb2.ModifyLookaheadResponse())
        if request_kind == "queryLookaheadRequest":
            handle = self._current_federate_handle(peer)
            if not self.handle_time_regulating.get(handle, False):
                return self._error("TimeRegulationIsNotEnabled", "Time regulation is not enabled")
            return rti_pb2.CallResponse(
                queryLookaheadResponse=rti_pb2.QueryLookaheadResponse(
                    result=self._handle_lookahead(handle)
                )
            )
        if request_kind == "queryGALTRequest":
            return rti_pb2.CallResponse(
                queryGALTResponse=rti_pb2.QueryGALTResponse(result=self._query_galt(self._current_federate_handle(peer)))
            )
        if request_kind == "queryLITSRequest":
            return rti_pb2.CallResponse(
                queryLITSResponse=rti_pb2.QueryLITSResponse(result=self._query_lits(self._current_federate_handle(peer)))
            )
        if request_kind == "getServiceReportingSwitchRequest":
            handle = self._current_federate_handle(peer)
            return rti_pb2.CallResponse(
                getServiceReportingSwitchResponse=rti_pb2.GetServiceReportingSwitchResponse(
                    result=self.handle_service_reporting.get(handle, self.service_reporting)
                )
            )
        if request_kind == "setServiceReportingSwitchRequest":
            self.handle_service_reporting[self._current_federate_handle(peer)] = request.setServiceReportingSwitchRequest.value
            self._recompute_service_reporting()
            self.switch_states["serviceReporting"] = self.service_reporting
            return rti_pb2.CallResponse(setServiceReportingSwitchResponse=rti_pb2.SetServiceReportingSwitchResponse())
        if request_kind == "getExceptionReportingSwitchRequest":
            handle = self._current_federate_handle(peer)
            return rti_pb2.CallResponse(
                getExceptionReportingSwitchResponse=rti_pb2.GetExceptionReportingSwitchResponse(
                    result=self.handle_exception_reporting.get(handle, self.switch_states.get("exceptionReporting", False))
                )
            )
        if request_kind == "setExceptionReportingSwitchRequest":
            handle = self._current_federate_handle(peer)
            self.handle_exception_reporting[handle] = request.setExceptionReportingSwitchRequest.value
            self._recompute_exception_reporting()
            return rti_pb2.CallResponse(setExceptionReportingSwitchResponse=rti_pb2.SetExceptionReportingSwitchResponse())
        if request_kind == "getAutomaticResignDirectiveRequest":
            return rti_pb2.CallResponse(
                getAutomaticResignDirectiveResponse=rti_pb2.GetAutomaticResignDirectiveResponse(
                    result=self.automatic_resign_directive
                )
            )
        if request_kind == "setAutomaticResignDirectiveRequest":
            self.automatic_resign_directive = request.setAutomaticResignDirectiveRequest.value
            return rti_pb2.CallResponse(
                setAutomaticResignDirectiveResponse=rti_pb2.SetAutomaticResignDirectiveResponse()
            )
        if request_kind.startswith("get") and request_kind.endswith("SwitchRequest"):
            switch_name = request_kind.removeprefix("get").removesuffix("SwitchRequest")
            state_key = switch_name[0].lower() + switch_name[1:]
            response_kind = request_kind.removesuffix("Request") + "Response"
            response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
            return rti_pb2.CallResponse(**{response_kind: response_type(result=self.switch_states.get(state_key, False))})
        if request_kind.startswith("set") and request_kind.endswith("SwitchRequest"):
            switch_name = request_kind.removeprefix("set").removesuffix("SwitchRequest")
            state_key = switch_name[0].lower() + switch_name[1:]
            self.switch_states[state_key] = getattr(request, request_kind).value
            if state_key == "attributeScopeAdvisory":
                self._queue_attribute_scope_advisories()
            response_kind = request_kind.removesuffix("Request") + "Response"
            response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
            return rti_pb2.CallResponse(**{response_kind: response_type()})
        if request_kind == "requestFederationSaveWithTimeRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            payload = request.requestFederationSaveWithTimeRequest
            if self.restore_label is not None:
                return self._error("RestoreInProgress", payload.label)
            if self.save_label is not None or self.next_save_name is not None:
                return self._error("SaveInProgress", payload.label)
            if payload.time.data:
                current_time = self._handle_current_time(self._current_federate_handle(peer))
                if _logical_time_value(payload.time) < _logical_time_value(current_time):
                    return self._error("InvalidLogicalTime", payload.time.data.decode("ascii"))
                self.next_save_name = payload.label
                self.next_save_time = datatypes_pb2.LogicalTime(data=payload.time.data)
                self._process_scheduled_save()
            else:
                self._start_federation_save(payload.label, None)
            return rti_pb2.CallResponse(requestFederationSaveWithTimeResponse=rti_pb2.RequestFederationSaveWithTimeResponse())
        if request_kind == "federateSaveBegunRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            if self.save_label is None:
                return self._error("SaveNotInitiated", "No federation save is in progress")
            self.save_status[self._current_federate_handle(peer)] = datatypes_pb2.FEDERATE_SAVING
            return rti_pb2.CallResponse(federateSaveBegunResponse=rti_pb2.FederateSaveBegunResponse())
        if request_kind == "queryFederationSaveStatusRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    federationSaveStatusResponse=callback_pb2.FederationSaveStatusResponse(response=self._save_status_array())
                ),
                target_peers={peer},
            )
            return rti_pb2.CallResponse(queryFederationSaveStatusResponse=rti_pb2.QueryFederationSaveStatusResponse())
        if request_kind == "federateSaveCompleteRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            if self.save_label is None:
                return self._error("SaveNotInitiated", "No federation save is in progress")
            self.save_status[self._current_federate_handle(peer)] = datatypes_pb2.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE
            if self.save_status and all(status == datatypes_pb2.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE for status in self.save_status.values()):
                self.saved_snapshots[self.save_label] = self._snapshot()
                self.saved_labels.add(self.save_label)
                self.save_label = None
                self.save_status = {}
                for handle in self._joined_handle_values():
                    self._enqueue_callback(
                        callback_pb2.CallbackRequest(federationSaved=callback_pb2.FederationSaved()),
                        target_handles={handle},
                    )
            return rti_pb2.CallResponse(federateSaveCompleteResponse=rti_pb2.FederateSaveCompleteResponse())
        if request_kind == "federateSaveNotCompleteRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            if self.save_label is None:
                return self._error("SaveNotInitiated", "No federation save is in progress")
            self.next_save_name = None
            self.next_save_time = None
            self.save_label = None
            self.save_status = {}
            for handle in self._joined_handle_values():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        federationNotSaved=callback_pb2.FederationNotSaved(reason=datatypes_pb2.FEDERATE_REPORTED_FAILURE_DURING_SAVE)
                    ),
                    target_handles={handle},
                )
            return rti_pb2.CallResponse(federateSaveNotCompleteResponse=rti_pb2.FederateSaveNotCompleteResponse())
        if request_kind == "abortFederationSaveRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            if self.save_label is None:
                return self._error("SaveNotInitiated", "No federation save is in progress")
            self.next_save_name = None
            self.next_save_time = None
            self.save_label = None
            self.save_status = {}
            for handle in self._joined_handle_values():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(federationNotSaved=callback_pb2.FederationNotSaved(reason=datatypes_pb2.SAVE_ABORTED)),
                    target_handles={handle},
                )
            return rti_pb2.CallResponse(abortFederationSaveResponse=rti_pb2.AbortFederationSaveResponse())
        if request_kind == "requestFederationRestoreRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            label = request.requestFederationRestoreRequest.label
            if self.save_label is not None or self.next_save_name is not None:
                return self._error("SaveInProgress", label)
            if self.restore_label is not None:
                return self._error("RestoreInProgress", label)
            if label not in self.saved_labels:
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        requestFederationRestoreFailed=callback_pb2.RequestFederationRestoreFailed(label=label)
                    ),
                    target_peers={peer},
                )
                return rti_pb2.CallResponse(requestFederationRestoreResponse=rti_pb2.RequestFederationRestoreResponse())
            self.restore_label = label
            self.restore_status = {handle: datatypes_pb2.FEDERATE_RESTORE_REQUEST_PENDING for handle in self._joined_handle_values()}
            for handle in self._joined_handle_values():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        requestFederationRestoreSucceeded=callback_pb2.RequestFederationRestoreSucceeded(label=label)
                    ),
                    target_handles={handle},
                )
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(federationRestoreBegun=callback_pb2.FederationRestoreBegun()),
                    target_handles={handle},
                )
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        initiateFederateRestore=callback_pb2.InitiateFederateRestore(
                            label=label,
                            federateName=self.joined_federate_handles.get(handle, "fedpro-federate"),
                            postRestoreFederateHandle=_handle(datatypes_pb2.FederateHandle, handle),
                        )
                    ),
                    target_handles={handle},
                )
            return rti_pb2.CallResponse(requestFederationRestoreResponse=rti_pb2.RequestFederationRestoreResponse())
        if request_kind == "queryFederationRestoreStatusRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    federationRestoreStatusResponse=callback_pb2.FederationRestoreStatusResponse(response=self._restore_status_array())
                ),
                target_peers={peer},
            )
            return rti_pb2.CallResponse(queryFederationRestoreStatusResponse=rti_pb2.QueryFederationRestoreStatusResponse())
        if request_kind == "federateRestoreCompleteRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            if self.restore_label is None:
                return self._error("RestoreNotRequested", "No federation restore is in progress")
            self.restore_status[self._current_federate_handle(peer)] = datatypes_pb2.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE
            if self.restore_status and all(status == datatypes_pb2.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE for status in self.restore_status.values()):
                self._restore_snapshot(self.restore_label)
                self.restore_label = None
                self.restore_status = {}
                for handle in self._joined_handle_values():
                    self._enqueue_callback(
                        callback_pb2.CallbackRequest(federationRestored=callback_pb2.FederationRestored()),
                        target_handles={handle},
                    )
            return rti_pb2.CallResponse(federateRestoreCompleteResponse=rti_pb2.FederateRestoreCompleteResponse())
        if request_kind == "federateRestoreNotCompleteRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            if self.restore_label is None:
                return self._error("RestoreNotRequested", "No federation restore is in progress")
            self.restore_label = None
            self.restore_status = {}
            for handle in self._joined_handle_values():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        federationNotRestored=callback_pb2.FederationNotRestored(reason=datatypes_pb2.FEDERATE_REPORTED_FAILURE_DURING_RESTORE)
                    ),
                    target_handles={handle},
                )
            return rti_pb2.CallResponse(federateRestoreNotCompleteResponse=rti_pb2.FederateRestoreNotCompleteResponse())
        if request_kind == "abortFederationRestoreRequest":
            if peer not in self.peer_callback_delivery_enabled:
                return self._error("NotConnected", peer)
            if peer not in self.peer_federate_handles:
                return self._error("FederateNotExecutionMember", peer)
            if self.restore_label is None:
                return self._error("RestoreNotInProgress", "No federation restore is in progress")
            self.restore_label = None
            self.restore_status = {}
            for handle in self._joined_handle_values():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(federationNotRestored=callback_pb2.FederationNotRestored(reason=datatypes_pb2.RESTORE_ABORTED)),
                    target_handles={handle},
                )
            return rti_pb2.CallResponse(abortFederationRestoreResponse=rti_pb2.AbortFederationRestoreResponse())
        if request_kind == "changeDefaultAttributeTransportationTypeRequest":
            payload = request.changeDefaultAttributeTransportationTypeRequest
            object_class = payload.objectClass.data.decode("ascii")
            transportation = payload.transportationType.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.default_attribute_transportation[(object_class, attribute.data.decode("ascii"))] = transportation
            return rti_pb2.CallResponse(changeDefaultAttributeTransportationTypeResponse=rti_pb2.ChangeDefaultAttributeTransportationTypeResponse())
        if request_kind == "requestAttributeTransportationTypeChangeRequest":
            payload = request.requestAttributeTransportationTypeChangeRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            if self.save_label is not None:
                return self._error("SaveInProgress", object_instance)
            if self.restore_label is not None:
                return self._error("RestoreInProgress", object_instance)
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            object_class = record["objectClass"]
            transportation = payload.transportationType.data.decode("ascii")
            if transportation not in self.transportation_names:
                return self._error("InvalidTransportationType", transportation)
            current_handle = self._current_federate_handle(peer)
            for attribute in payload.attributes.attributeHandle:
                attribute_handle = attribute.data.decode("ascii")
                if (object_class, attribute_handle) not in self.attribute_names:
                    return self._error("AttributeNotDefined", attribute_handle)
                if self.attribute_owners.get((object_instance, attribute_handle)) != current_handle:
                    return self._error("AttributeNotOwned", attribute_handle)
                self.default_attribute_transportation[(object_instance, attribute_handle)] = transportation
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    confirmAttributeTransportationTypeChange=callback_pb2.ConfirmAttributeTransportationTypeChange(
                        objectInstance=payload.objectInstance,
                        attributes=payload.attributes,
                        transportationType=payload.transportationType,
                    )
                ),
                target_handles={self._current_federate_handle(peer)},
            )
            return rti_pb2.CallResponse(
                requestAttributeTransportationTypeChangeResponse=rti_pb2.RequestAttributeTransportationTypeChangeResponse()
            )
        if request_kind == "queryAttributeTransportationTypeRequest":
            payload = request.queryAttributeTransportationTypeRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            if self.save_label is not None:
                return self._error("SaveInProgress", object_instance)
            if self.restore_label is not None:
                return self._error("RestoreInProgress", object_instance)
            attribute = payload.attribute.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            object_class = record["objectClass"]
            if (object_class, attribute) not in self.attribute_names:
                return self._error("AttributeNotDefined", attribute)
            transportation = self.default_attribute_transportation.get(
                (object_instance, attribute),
                self.default_attribute_transportation.get((object_class, attribute), "1"),
            )
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    reportAttributeTransportationType=callback_pb2.ReportAttributeTransportationType(
                        objectInstance=payload.objectInstance,
                        attribute=payload.attribute,
                        transportationType=_handle(datatypes_pb2.TransportationTypeHandle, transportation),
                    )
                ),
                target_handles={self._current_federate_handle(peer)},
            )
            return rti_pb2.CallResponse(
                queryAttributeTransportationTypeResponse=rti_pb2.QueryAttributeTransportationTypeResponse()
            )
        if request_kind == "requestInteractionTransportationTypeChangeRequest":
            payload = request.requestInteractionTransportationTypeChangeRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            if self.save_label is not None:
                return self._error("SaveInProgress", interaction_class)
            if self.restore_label is not None:
                return self._error("RestoreInProgress", interaction_class)
            if interaction_class not in self.interaction_names:
                return self._error("InvalidInteractionClassHandle", interaction_class)
            transportation = payload.transportationType.data.decode("ascii")
            if transportation not in self.transportation_names:
                return self._error("InvalidTransportationType", transportation)
            self.interaction_transportation = (interaction_class, transportation)
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    confirmInteractionTransportationTypeChange=callback_pb2.ConfirmInteractionTransportationTypeChange(
                        interactionClass=payload.interactionClass,
                        transportationType=payload.transportationType,
                    )
                ),
                target_handles={self._current_federate_handle(peer)},
            )
            return rti_pb2.CallResponse(
                requestInteractionTransportationTypeChangeResponse=rti_pb2.RequestInteractionTransportationTypeChangeResponse()
            )
        if request_kind == "queryInteractionTransportationTypeRequest":
            payload = request.queryInteractionTransportationTypeRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            if self.save_label is not None:
                return self._error("SaveInProgress", interaction_class)
            if self.restore_label is not None:
                return self._error("RestoreInProgress", interaction_class)
            if interaction_class not in self.interaction_names:
                return self._error("InvalidInteractionClassHandle", interaction_class)
            transportation = (
                self.interaction_transportation[1]
                if self.interaction_transportation is not None and self.interaction_transportation[0] == interaction_class
                else "1"
            )
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    reportInteractionTransportationType=callback_pb2.ReportInteractionTransportationType(
                        federate=payload.federate,
                        interactionClass=payload.interactionClass,
                        transportationType=_handle(datatypes_pb2.TransportationTypeHandle, transportation),
                    )
                ),
                target_handles={self._current_federate_handle(peer)},
            )
            return rti_pb2.CallResponse(
                queryInteractionTransportationTypeResponse=rti_pb2.QueryInteractionTransportationTypeResponse()
            )
        if request_kind == "changeDefaultAttributeOrderTypeRequest":
            payload = request.changeDefaultAttributeOrderTypeRequest
            object_class = payload.theObjectClass.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.default_attribute_order[(object_class, attribute.data.decode("ascii"))] = payload.orderType
            return rti_pb2.CallResponse(changeDefaultAttributeOrderTypeResponse=rti_pb2.ChangeDefaultAttributeOrderTypeResponse())
        if request_kind == "changeAttributeOrderTypeRequest":
            payload = request.changeAttributeOrderTypeRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            if object_instance not in self.object_instances:
                return self._error("ObjectInstanceNotKnown", object_instance)
            for attribute in payload.attributes.attributeHandle:
                self.default_attribute_order[(object_instance, attribute.data.decode("ascii"))] = payload.orderType
            return rti_pb2.CallResponse(changeAttributeOrderTypeResponse=rti_pb2.ChangeAttributeOrderTypeResponse())
        if request_kind == "changeInteractionOrderTypeRequest":
            payload = request.changeInteractionOrderTypeRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            if interaction_class not in self.published_interactions:
                return self._error("InteractionClassNotPublished", interaction_class)
            self.interaction_order = (interaction_class, payload.orderType)
            return rti_pb2.CallResponse(changeInteractionOrderTypeResponse=rti_pb2.ChangeInteractionOrderTypeResponse())
        if request_kind == "publishObjectClassAttributesRequest":
            payload = request.publishObjectClassAttributesRequest
            object_class = payload.objectClass.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                attribute_handle = attribute.data.decode("ascii")
                if (object_class, attribute_handle) not in self.attribute_names:
                    return self._error("AttributeNotDefined", attribute_handle)
            handle = self._current_federate_handle(peer)
            previous_interest = self._registration_interest_snapshot()
            self.handle_published_object_attributes.setdefault(handle, {}).setdefault(object_class, set()).update(
                attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle
            )
            self._rebuild_published_object_aggregates()
            self._emit_registration_interest_transitions(previous_interest)
            return rti_pb2.CallResponse(publishObjectClassAttributesResponse=rti_pb2.PublishObjectClassAttributesResponse())
        if request_kind == "unpublishObjectClassRequest":
            payload = request.unpublishObjectClassRequest
            object_class = payload.objectClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            previous_interest = self._registration_interest_snapshot()
            self.handle_published_object_attributes.get(handle, {}).pop(object_class, None)
            self._rebuild_published_object_aggregates()
            self._emit_registration_interest_transitions(previous_interest)
            return rti_pb2.CallResponse(unpublishObjectClassResponse=rti_pb2.UnpublishObjectClassResponse())
        if request_kind == "unpublishObjectClassAttributesRequest":
            payload = request.unpublishObjectClassAttributesRequest
            object_class = payload.objectClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            previous_interest = self._registration_interest_snapshot()
            published = self.handle_published_object_attributes.setdefault(handle, {}).setdefault(object_class, set())
            published.difference_update(attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle)
            if not published:
                self.handle_published_object_attributes.get(handle, {}).pop(object_class, None)
            self._rebuild_published_object_aggregates()
            self._emit_registration_interest_transitions(previous_interest)
            return rti_pb2.CallResponse(
                unpublishObjectClassAttributesResponse=rti_pb2.UnpublishObjectClassAttributesResponse()
            )
        if request_kind in {
            "subscribeObjectClassAttributesRequest",
            "subscribeObjectClassAttributesWithRateRequest",
            "subscribeObjectClassAttributesPassivelyRequest",
            "subscribeObjectClassAttributesPassivelyWithRateRequest",
        }:
            payload = getattr(request, request_kind)
            object_class = payload.objectClass.data.decode("ascii")
            attributes = {attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle}
            update_rate_designator = getattr(payload, "updateRateDesignator", "")
            handle = self._current_federate_handle(peer)
            previous_interest = self._registration_interest_snapshot()
            self.handle_subscribed_object_attributes.setdefault(handle, {}).setdefault(
                object_class,
                set(),
            ).update(attributes)
            update_rates = self.handle_subscribed_object_update_rates.setdefault(handle, {})
            for attribute in attributes:
                if update_rate_designator:
                    update_rates[(object_class, attribute)] = update_rate_designator
                else:
                    update_rates.pop((object_class, attribute), None)
            self._rebuild_subscribed_object_aggregates()
            self._emit_registration_interest_transitions(previous_interest)
            for object_instance, record in self.object_instances.items():
                if record["objectClass"] == object_class:
                    self._queue_discovery(
                        object_instance,
                        object_class,
                        record["name"],
                        target_handles={handle},
                    )
            self._queue_turn_updates_on(
                object_class,
                attributes,
                update_rate_designator,
                target_handles={handle},
            )
            response_kind = request_kind.replace("Request", "Response")
            response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
            return rti_pb2.CallResponse(**{response_kind: response_type()})
        if request_kind == "subscribeObjectClassAttributesWithRegionsRequest":
            payload = request.subscribeObjectClassAttributesWithRegionsRequest
            object_class = payload.objectClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            previous_interest = self._registration_interest_snapshot()
            prior_scope_state = dict(self.attribute_scope_state)
            region_map = self.handle_subscribed_object_regions.setdefault(handle, {}).setdefault(object_class, {})
            for attribute, regions in self._attribute_region_pairs(payload.attributesAndRegions):
                self.handle_subscribed_object_attributes.setdefault(handle, {}).setdefault(object_class, set()).add(attribute)
                region_map.setdefault(attribute, set()).update(regions)
            self._rebuild_subscribed_object_aggregates()
            self._emit_registration_interest_transitions(previous_interest)
            self._queue_attribute_scope_advisories()
            for object_instance, record in self.object_instances.items():
                if record["objectClass"] != object_class:
                    continue
                matching_attributes = self._reflectable_attribute_names_for_handle(handle, object_instance, object_class)
                if not matching_attributes:
                    continue
                newly_eligible_attributes = {
                    attribute
                    for attribute in matching_attributes
                    if prior_scope_state.get((handle, object_instance, attribute)) is not True
                }
                self._queue_discovery(
                    object_instance,
                    object_class,
                    record["name"],
                    target_handles={handle},
                )
                self._queue_turn_updates_on_for_object_instance(
                    object_instance,
                    newly_eligible_attributes & self.published_object_attributes.get(object_class, set()),
                    target_handles={handle},
                )
            return rti_pb2.CallResponse(
                subscribeObjectClassAttributesWithRegionsResponse=rti_pb2.SubscribeObjectClassAttributesWithRegionsResponse()
            )
        if request_kind == "unsubscribeObjectClassAttributesWithRegionsRequest":
            payload = request.unsubscribeObjectClassAttributesWithRegionsRequest
            object_class = payload.objectClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            previous_interest = self._registration_interest_snapshot()
            region_map = self.handle_subscribed_object_regions.setdefault(handle, {}).setdefault(object_class, {})
            removed_attributes: set[str] = set()
            for attribute, regions in self._attribute_region_pairs(payload.attributesAndRegions):
                current = region_map.setdefault(attribute, set())
                current.difference_update(regions)
                if not current:
                    region_map.pop(attribute, None)
                    self.handle_subscribed_object_attributes.setdefault(handle, {}).get(object_class, set()).discard(attribute)
                    removed_attributes.add(attribute)
            self._rebuild_subscribed_object_aggregates()
            self._emit_registration_interest_transitions(previous_interest)
            self._queue_turn_updates_off(object_class, removed_attributes, target_handles={handle})
            self._queue_attribute_scope_advisories()
            return rti_pb2.CallResponse(
                unsubscribeObjectClassAttributesWithRegionsResponse=rti_pb2.UnsubscribeObjectClassAttributesWithRegionsResponse()
            )
        if request_kind == "unsubscribeObjectClassRequest":
            payload = request.unsubscribeObjectClassRequest
            object_class = payload.objectClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            previous_interest = self._registration_interest_snapshot()
            removed_attributes = set(self.handle_subscribed_object_attributes.get(handle, {}).get(object_class, set()))
            self.handle_subscribed_object_attributes.get(handle, {}).pop(object_class, None)
            self.handle_subscribed_object_regions.get(handle, {}).pop(object_class, None)
            self._rebuild_subscribed_object_aggregates()
            self._emit_registration_interest_transitions(previous_interest)
            self._queue_turn_updates_off(object_class, removed_attributes, target_handles={handle})
            self._queue_attribute_scope_advisories()
            return rti_pb2.CallResponse(unsubscribeObjectClassResponse=rti_pb2.UnsubscribeObjectClassResponse())
        if request_kind == "unsubscribeObjectClassAttributesRequest":
            payload = request.unsubscribeObjectClassAttributesRequest
            object_class = payload.objectClass.data.decode("ascii")
            removed_attributes = {attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle}
            handle = self._current_federate_handle(peer)
            previous_interest = self._registration_interest_snapshot()
            current = self.handle_subscribed_object_attributes.setdefault(handle, {}).setdefault(
                object_class,
                set(),
            )
            current.difference_update(removed_attributes)
            update_rates = self.handle_subscribed_object_update_rates.setdefault(handle, {})
            last_delivery = self.handle_last_update_rate_delivery_time.setdefault(handle, {})
            for attribute in removed_attributes:
                update_rates.pop((object_class, attribute), None)
                last_delivery.pop((object_class, attribute), None)
            self._rebuild_subscribed_object_aggregates()
            self._emit_registration_interest_transitions(previous_interest)
            self._queue_turn_updates_off(
                object_class,
                removed_attributes,
                target_handles={handle},
            )
            return rti_pb2.CallResponse(
                unsubscribeObjectClassAttributesResponse=rti_pb2.UnsubscribeObjectClassAttributesResponse()
            )
        if request_kind == "publishInteractionClassRequest":
            interaction_class = request.publishInteractionClassRequest.interactionClass.data.decode("ascii")
            previous_interest = self._interaction_interest_snapshot()
            self.handle_published_interactions.setdefault(self._current_federate_handle(peer), set()).add(interaction_class)
            self._rebuild_published_interaction_aggregates()
            self._emit_interaction_interest_transitions(previous_interest)
            return rti_pb2.CallResponse(publishInteractionClassResponse=rti_pb2.PublishInteractionClassResponse())
        if request_kind == "unpublishInteractionClassRequest":
            interaction_class = request.unpublishInteractionClassRequest.interactionClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            previous_interest = self._interaction_interest_snapshot()
            self.handle_published_interactions.setdefault(handle, set()).discard(interaction_class)
            self._rebuild_published_interaction_aggregates()
            self._emit_interaction_interest_transitions(previous_interest)
            return rti_pb2.CallResponse(unpublishInteractionClassResponse=rti_pb2.UnpublishInteractionClassResponse())
        if request_kind == "publishObjectClassDirectedInteractionsRequest":
            payload = request.publishObjectClassDirectedInteractionsRequest
            object_class = payload.objectClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            published = self.handle_published_directed_interactions.setdefault(handle, {}).setdefault(object_class, set())
            published.update(interaction.data.decode("ascii") for interaction in payload.interactionClasses.interactionClassHandle)
            self._rebuild_published_directed_interactions()
            return rti_pb2.CallResponse(
                publishObjectClassDirectedInteractionsResponse=rti_pb2.PublishObjectClassDirectedInteractionsResponse()
            )
        if request_kind in {
            "unpublishObjectClassDirectedInteractionsRequest",
            "unpublishObjectClassDirectedInteractionsWithSetRequest",
        }:
            payload = getattr(request, request_kind)
            object_class = payload.objectClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            if request_kind == "unpublishObjectClassDirectedInteractionsRequest":
                self.handle_published_directed_interactions.get(handle, {}).pop(object_class, None)
                self._rebuild_published_directed_interactions()
                return rti_pb2.CallResponse(
                    unpublishObjectClassDirectedInteractionsResponse=rti_pb2.UnpublishObjectClassDirectedInteractionsResponse()
                )
            published = self.handle_published_directed_interactions.setdefault(handle, {}).setdefault(object_class, set())
            published.difference_update(interaction.data.decode("ascii") for interaction in payload.interactionClasses.interactionClassHandle)
            if not published:
                self.handle_published_directed_interactions.get(handle, {}).pop(object_class, None)
            self._rebuild_published_directed_interactions()
            return rti_pb2.CallResponse(
                unpublishObjectClassDirectedInteractionsWithSetResponse=rti_pb2.UnpublishObjectClassDirectedInteractionsWithSetResponse()
            )
        if request_kind in {
            "subscribeInteractionClassRequest",
            "subscribeInteractionClassPassivelyRequest",
        }:
            payload = getattr(request, request_kind)
            interaction_class = payload.interactionClass.data.decode("ascii")
            previous_interest = self._interaction_interest_snapshot()
            self.handle_subscribed_interactions.setdefault(self._current_federate_handle(peer), set()).add(interaction_class)
            self._rebuild_subscribed_interaction_aggregates()
            self._emit_interaction_interest_transitions(previous_interest)
            response_kind = request_kind.replace("Request", "Response")
            response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
            return rti_pb2.CallResponse(**{response_kind: response_type()})
        if request_kind == "subscribeInteractionClassWithRegionsRequest":
            payload = request.subscribeInteractionClassWithRegionsRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            previous_interest = self._interaction_interest_snapshot()
            self.handle_subscribed_interactions.setdefault(handle, set()).add(interaction_class)
            self.directed_interaction_region_gates.add(interaction_class)
            self.handle_subscribed_interaction_regions.setdefault(handle, {}).setdefault(interaction_class, set()).update(
                region.data.decode("ascii") for region in payload.regions.regionHandle
            )
            self._rebuild_subscribed_interaction_aggregates()
            self._emit_interaction_interest_transitions(previous_interest)
            return rti_pb2.CallResponse(subscribeInteractionClassWithRegionsResponse=rti_pb2.SubscribeInteractionClassWithRegionsResponse())
        if request_kind == "unsubscribeInteractionClassWithRegionsRequest":
            payload = request.unsubscribeInteractionClassWithRegionsRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            previous_interest = self._interaction_interest_snapshot()
            regions = self.handle_subscribed_interaction_regions.setdefault(handle, {}).setdefault(interaction_class, set())
            regions.difference_update(region.data.decode("ascii") for region in payload.regions.regionHandle)
            if not regions:
                self.handle_subscribed_interaction_regions.get(handle, {}).pop(interaction_class, None)
                self.handle_subscribed_interactions.setdefault(handle, set()).discard(interaction_class)
            self._rebuild_subscribed_interaction_aggregates()
            self._emit_interaction_interest_transitions(previous_interest)
            return rti_pb2.CallResponse(unsubscribeInteractionClassWithRegionsResponse=rti_pb2.UnsubscribeInteractionClassWithRegionsResponse())
        if request_kind == "unsubscribeInteractionClassRequest":
            payload = request.unsubscribeInteractionClassRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            previous_interest = self._interaction_interest_snapshot()
            self.handle_subscribed_interactions.setdefault(handle, set()).discard(interaction_class)
            self.handle_subscribed_interaction_regions.get(handle, {}).pop(interaction_class, None)
            self._rebuild_subscribed_interaction_aggregates()
            self._emit_interaction_interest_transitions(previous_interest)
            return rti_pb2.CallResponse(unsubscribeInteractionClassResponse=rti_pb2.UnsubscribeInteractionClassResponse())
        if request_kind in {
            "subscribeObjectClassDirectedInteractionsRequest",
            "subscribeObjectClassDirectedInteractionsUniversallyRequest",
        }:
            payload = getattr(request, request_kind)
            object_class = payload.objectClass.data.decode("ascii")
            subscribed = self.subscribed_directed_interactions.setdefault(object_class, set())
            handle_subscribed = self.handle_subscribed_directed_interactions.setdefault(
                self._current_federate_handle(peer),
                {},
            ).setdefault(object_class, set())
            values = {interaction.data.decode("ascii") for interaction in payload.interactionClasses.interactionClassHandle}
            subscribed.update(values)
            handle_subscribed.update(values)
            response_kind = (
                "subscribeObjectClassDirectedInteractionsUniversallyResponse"
                if request_kind == "subscribeObjectClassDirectedInteractionsUniversallyRequest"
                else "subscribeObjectClassDirectedInteractionsResponse"
            )
            response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
            return rti_pb2.CallResponse(**{response_kind: response_type()})
        if request_kind in {
            "unsubscribeObjectClassDirectedInteractionsRequest",
            "unsubscribeObjectClassDirectedInteractionsWithSetRequest",
        }:
            payload = getattr(request, request_kind)
            object_class = payload.objectClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            if request_kind == "unsubscribeObjectClassDirectedInteractionsRequest":
                self.handle_subscribed_directed_interactions.get(handle, {}).pop(object_class, None)
                self.subscribed_directed_interactions.pop(object_class, None)
                self._rebuild_subscribed_directed_interactions()
                return rti_pb2.CallResponse(
                    unsubscribeObjectClassDirectedInteractionsResponse=rti_pb2.UnsubscribeObjectClassDirectedInteractionsResponse()
                )
            subscribed = self.subscribed_directed_interactions.setdefault(object_class, set())
            handle_subscribed = self.handle_subscribed_directed_interactions.setdefault(handle, {}).setdefault(object_class, set())
            removed = {interaction.data.decode("ascii") for interaction in payload.interactionClasses.interactionClassHandle}
            handle_subscribed.difference_update(removed)
            subscribed.difference_update(removed)
            if not subscribed:
                self.subscribed_directed_interactions.pop(object_class, None)
            if not handle_subscribed:
                self.handle_subscribed_directed_interactions.get(handle, {}).pop(object_class, None)
            self._rebuild_subscribed_directed_interactions()
            return rti_pb2.CallResponse(
                unsubscribeObjectClassDirectedInteractionsWithSetResponse=rti_pb2.UnsubscribeObjectClassDirectedInteractionsWithSetResponse()
            )
        if request_kind in {
            "registerObjectInstanceRequest",
            "registerObjectInstanceWithNameRequest",
            "registerObjectInstanceWithRegionsRequest",
            "registerObjectInstanceWithNameAndRegionsRequest",
        }:
            payload = getattr(request, request_kind)
            object_class = payload.objectClass.data.decode("ascii")
            object_name = getattr(payload, "objectInstanceName", "") or f"fedpro-object-{self.next_object_instance_handle}"
            if request_kind in {"registerObjectInstanceWithNameRequest", "registerObjectInstanceWithNameAndRegionsRequest"}:
                if any(record["name"] == object_name for record in self.object_instances.values()):
                    return self._error("ObjectInstanceNameInUse", object_name)
                reserved_by = self.reserved_object_instance_names.get(object_name)
                if reserved_by is not None and reserved_by != self._current_federate_handle(peer):
                    return self._error("ObjectInstanceNameInUse", object_name)
            handle = str(self.next_object_instance_handle)
            self.next_object_instance_handle += 1
            self.object_instances[handle] = {"name": object_name, "objectClass": object_class}
            owner_handle = self._current_federate_handle(peer)
            for (declared_object_class, _name), attribute_handle in self.attributes.items():
                if declared_object_class == object_class:
                    self.attribute_owners[(handle, attribute_handle)] = owner_handle
            if request_kind in {"registerObjectInstanceWithRegionsRequest", "registerObjectInstanceWithNameAndRegionsRequest"}:
                update_regions = self.object_update_regions.setdefault(handle, {})
                for attribute, regions in self._attribute_region_pairs(payload.attributesAndRegions):
                    update_regions.setdefault(attribute, set()).update(regions)
            self.reserved_object_instance_names.pop(object_name, None)
            discovery_targets = self._discovery_target_handles(object_class, exclude_handle=owner_handle)
            if discovery_targets:
                self._queue_discovery(handle, object_class, object_name, target_handles=discovery_targets)
            response_kind = {
                "registerObjectInstanceRequest": "registerObjectInstanceResponse",
                "registerObjectInstanceWithNameRequest": "registerObjectInstanceWithNameResponse",
                "registerObjectInstanceWithRegionsRequest": "registerObjectInstanceWithRegionsResponse",
                "registerObjectInstanceWithNameAndRegionsRequest": "registerObjectInstanceWithNameAndRegionsResponse",
            }[request_kind]
            response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
            return rti_pb2.CallResponse(**{response_kind: response_type(result=_handle(datatypes_pb2.ObjectInstanceHandle, handle))})
        if request_kind == "reserveObjectInstanceNameRequest":
            name = request.reserveObjectInstanceNameRequest.objectInstanceName
            if any(record["name"] == name for record in self.object_instances.values()) or name in self.reserved_object_instance_names:
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        objectInstanceNameReservationFailed=callback_pb2.ObjectInstanceNameReservationFailed(objectInstanceName=name)
                    ),
                    target_handles={self._current_federate_handle(peer)},
                )
            else:
                self.reserved_object_instance_names[name] = self._current_federate_handle(peer)
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        objectInstanceNameReservationSucceeded=callback_pb2.ObjectInstanceNameReservationSucceeded(objectInstanceName=name)
                    ),
                    target_handles={self._current_federate_handle(peer)},
                )
            return rti_pb2.CallResponse(reserveObjectInstanceNameResponse=rti_pb2.ReserveObjectInstanceNameResponse())
        if request_kind == "releaseObjectInstanceNameRequest":
            name = request.releaseObjectInstanceNameRequest.objectInstanceName
            if self.reserved_object_instance_names.get(name) != self._current_federate_handle(peer):
                return self._error("ObjectInstanceNameNotReserved", name)
            self.reserved_object_instance_names.pop(name, None)
            return rti_pb2.CallResponse(releaseObjectInstanceNameResponse=rti_pb2.ReleaseObjectInstanceNameResponse())
        if request_kind == "reserveMultipleObjectInstanceNamesRequest":
            names = tuple(request.reserveMultipleObjectInstanceNamesRequest.objectInstanceNames)
            if any(
                any(record["name"] == name for record in self.object_instances.values()) or name in self.reserved_object_instance_names
                for name in names
            ):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        multipleObjectInstanceNameReservationFailed=callback_pb2.MultipleObjectInstanceNameReservationFailed(
                            objectInstanceNames=names
                        )
                    ),
                    target_handles={self._current_federate_handle(peer)},
                )
            else:
                owner = self._current_federate_handle(peer)
                for name in names:
                    self.reserved_object_instance_names[name] = owner
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        multipleObjectInstanceNameReservationSucceeded=callback_pb2.MultipleObjectInstanceNameReservationSucceeded(
                            objectInstanceNames=names
                        )
                    ),
                    target_handles={owner},
                )
            return rti_pb2.CallResponse(
                reserveMultipleObjectInstanceNamesResponse=rti_pb2.ReserveMultipleObjectInstanceNamesResponse()
            )
        if request_kind == "releaseMultipleObjectInstanceNamesRequest":
            names = tuple(request.releaseMultipleObjectInstanceNamesRequest.objectInstanceNames)
            owner = self._current_federate_handle(peer)
            for name in names:
                if self.reserved_object_instance_names.get(name) != owner:
                    return self._error("ObjectInstanceNameNotReserved", name)
            for name in names:
                self.reserved_object_instance_names.pop(name, None)
            return rti_pb2.CallResponse(
                releaseMultipleObjectInstanceNamesResponse=rti_pb2.ReleaseMultipleObjectInstanceNamesResponse()
            )
        if request_kind == "associateRegionsForUpdatesRequest":
            payload = request.associateRegionsForUpdatesRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            update_regions = self.object_update_regions.setdefault(object_instance, {})
            for attribute, regions in self._attribute_region_pairs(payload.attributesAndRegions):
                update_regions.setdefault(attribute, set()).update(regions)
            self._queue_attribute_scope_advisories()
            return rti_pb2.CallResponse(associateRegionsForUpdatesResponse=rti_pb2.AssociateRegionsForUpdatesResponse())
        if request_kind == "unassociateRegionsForUpdatesRequest":
            payload = request.unassociateRegionsForUpdatesRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            update_regions = self.object_update_regions.setdefault(object_instance, {})
            for attribute, regions in self._attribute_region_pairs(payload.attributesAndRegions):
                current = update_regions.setdefault(attribute, set())
                current.difference_update(regions)
                if not current:
                    update_regions.pop(attribute, None)
            self._queue_attribute_scope_advisories()
            return rti_pb2.CallResponse(unassociateRegionsForUpdatesResponse=rti_pb2.UnassociateRegionsForUpdatesResponse())
        if request_kind == "updateAttributeValuesRequest":
            payload = request.updateAttributeValuesRequest
            source_handle = self._current_federate_handle(peer)
            self.updates_sent += 1
            self.object_instances_updated += 1
            self._increment_counter(self.handle_updates_sent, source_handle)
            self._increment_counter(self.handle_object_instances_updated, source_handle)
            object_instance = payload.objectInstance.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            object_class = record["objectClass"]
            for item in payload.attributeValues.attributeHandleValue:
                attribute = item.attributeHandle.data.decode("ascii")
                if self.attribute_owners.get((object_instance, attribute)) != source_handle:
                    return self._error("AttributeNotOwned", attribute)
            published = self.published_object_attributes.get(object_class, set())
            if any(item.attributeHandle.data.decode("ascii") not in published for item in payload.attributeValues.attributeHandleValue):
                return self._error("ObjectClassNotPublished", object_class)
            reflected_by_handle = self._reflection_target_handles(
                object_instance,
                object_class,
                tuple(item.attributeHandle.data.decode("ascii") for item in payload.attributeValues.attributeHandleValue),
            )
            for target_handle, attribute_values in reflected_by_handle.items():
                if object_instance in self.handle_locally_deleted_objects.get(target_handle, set()):
                    self.handle_locally_deleted_objects[target_handle].discard(object_instance)
                    self._queue_discovery(object_instance, object_class, record["name"], target_handles={target_handle})
                reflected_items = [
                    item
                    for item in payload.attributeValues.attributeHandleValue
                    if item.attributeHandle.data.decode("ascii") in set(attribute_values)
                ]
                for transportation, grouped_items in self._partition_reflected_items_by_transport(
                    object_instance,
                    object_class,
                    reflected_items,
                ):
                    values = datatypes_pb2.AttributeHandleValueMap()
                    for item in grouped_items:
                        row = values.attributeHandleValue.add()
                        row.attributeHandle.CopyFrom(item.attributeHandle)
                        row.value = item.value
                    self._enqueue_callback(
                        callback_pb2.CallbackRequest(
                            reflectAttributeValues=callback_pb2.ReflectAttributeValues(
                                objectInstance=payload.objectInstance,
                                attributeValues=values,
                                userSuppliedTag=payload.userSuppliedTag,
                                transportationType=_handle(datatypes_pb2.TransportationTypeHandle, transportation),
                                producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle(peer)),
                                optionalSentRegions=self._conveyed_regions_for(object_instance, grouped_items),
                            )
                        ),
                        target_handles={target_handle},
                    )
            self.reflections_received += len(reflected_by_handle)
            self.object_instances_reflected += len(reflected_by_handle)
            for target_handle in reflected_by_handle:
                self._increment_counter(self.handle_reflections_received, target_handle)
                self._increment_counter(self.handle_object_instances_reflected, target_handle)
            return rti_pb2.CallResponse(updateAttributeValuesResponse=rti_pb2.UpdateAttributeValuesResponse())
        if request_kind == "updateAttributeValuesWithTimeRequest":
            payload = request.updateAttributeValuesWithTimeRequest
            source_handle = self._current_federate_handle(peer)
            if not self._validate_tso_send_time(source_handle, payload.time):
                return self._error("InvalidLogicalTime", "Timestamp is earlier than the logical-time/lookahead lower bound")
            self.updates_sent += 1
            self.object_instances_updated += 1
            self._increment_counter(self.handle_updates_sent, source_handle)
            self._increment_counter(self.handle_object_instances_updated, source_handle)
            object_instance = payload.objectInstance.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            object_class = record["objectClass"]
            for item in payload.attributeValues.attributeHandleValue:
                attribute = item.attributeHandle.data.decode("ascii")
                if self.attribute_owners.get((object_instance, attribute)) != source_handle:
                    return self._error("AttributeNotOwned", attribute)
            published = self.published_object_attributes.get(object_class, set())
            if any(item.attributeHandle.data.decode("ascii") not in published for item in payload.attributeValues.attributeHandleValue):
                return self._error("ObjectClassNotPublished", object_class)
            retraction_handle = self._next_retraction_handle()
            send_time_value = _logical_time_value(payload.time)
            reflected_by_handle = self._reflection_target_handles(
                object_instance,
                object_class,
                tuple(item.attributeHandle.data.decode("ascii") for item in payload.attributeValues.attributeHandleValue),
            )
            for target_handle, attribute_values in reflected_by_handle.items():
                if object_instance in self.handle_locally_deleted_objects.get(target_handle, set()):
                    self.handle_locally_deleted_objects[target_handle].discard(object_instance)
                    self._queue_discovery(object_instance, object_class, record["name"], target_handles={target_handle})
                reflected_items = [
                    item
                    for item in payload.attributeValues.attributeHandleValue
                    if item.attributeHandle.data.decode("ascii") in set(attribute_values)
                ]
                reflected_items = [
                    item
                    for item in reflected_items
                    if self._update_rate_allows_delivery(
                        target_handle,
                        object_class,
                        item.attributeHandle.data.decode("ascii"),
                        send_time_value,
                    )
                ]
                if not reflected_items:
                    continue
                for transportation, grouped_items in self._partition_reflected_items_by_transport(
                    object_instance,
                    object_class,
                    reflected_items,
                ):
                    values = datatypes_pb2.AttributeHandleValueMap()
                    for item in grouped_items:
                        row = values.attributeHandleValue.add()
                        row.attributeHandle.CopyFrom(item.attributeHandle)
                        row.value = item.value
                    self._queue_tso_callback(
                        retraction_handle,
                        payload.time,
                        callback_pb2.CallbackRequest(
                            reflectAttributeValuesWithTime=callback_pb2.ReflectAttributeValuesWithTime(
                                objectInstance=payload.objectInstance,
                                attributeValues=values,
                                userSuppliedTag=payload.userSuppliedTag,
                                transportationType=_handle(datatypes_pb2.TransportationTypeHandle, transportation),
                                producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle(peer)),
                                optionalSentRegions=self._conveyed_regions_for(object_instance, grouped_items),
                                time=payload.time,
                                sentOrderType=datatypes_pb2.TIMESTAMP,
                                receivedOrderType=datatypes_pb2.TIMESTAMP,
                                optionalRetraction=_handle(datatypes_pb2.MessageRetractionHandle, retraction_handle),
                            )
                        ),
                        target_handles={target_handle},
                    )
            return rti_pb2.CallResponse(
                updateAttributeValuesWithTimeResponse=rti_pb2.UpdateAttributeValuesWithTimeResponse(
                    result=self._message_retraction_return(retraction_handle)
                )
            )
        if request_kind == "deleteObjectInstanceRequest":
            payload = request.deleteObjectInstanceRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            record = self._remove_object_instance(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            remove_targets = self._discovery_target_handles(record["objectClass"], exclude_handle=self._current_federate_handle(peer))
            if remove_targets:
                callback = callback_pb2.CallbackRequest(
                    removeObjectInstance=callback_pb2.RemoveObjectInstance(
                        objectInstance=payload.objectInstance,
                        userSuppliedTag=payload.userSuppliedTag,
                        producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle(peer)),
                    )
                )
                if len(remove_targets) > 1:
                    self._enqueue_callback_per_handle(callback, target_handles=remove_targets)
                else:
                    self._enqueue_callback(callback, target_handles=remove_targets)
            return rti_pb2.CallResponse(deleteObjectInstanceResponse=rti_pb2.DeleteObjectInstanceResponse())
        if request_kind == "deleteObjectInstanceWithTimeRequest":
            payload = request.deleteObjectInstanceWithTimeRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            record = self._remove_object_instance(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            retraction_handle = self._next_retraction_handle()
            remove_targets = self._discovery_target_handles(record["objectClass"], exclude_handle=self._current_federate_handle(peer))
            callback = callback_pb2.CallbackRequest(
                removeObjectInstanceWithTime=callback_pb2.RemoveObjectInstanceWithTime(
                    objectInstance=payload.objectInstance,
                    userSuppliedTag=payload.userSuppliedTag,
                    producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle()),
                    time=payload.time,
                    sentOrderType=datatypes_pb2.TIMESTAMP,
                    receivedOrderType=datatypes_pb2.TIMESTAMP,
                    optionalRetraction=_handle(datatypes_pb2.MessageRetractionHandle, retraction_handle),
                )
            )
            if remove_targets:
                if len(remove_targets) > 1:
                    for target_handle in sorted(remove_targets, key=int):
                        clone = callback_pb2.CallbackRequest()
                        clone.CopyFrom(callback)
                        self._queue_tso_callback(retraction_handle, payload.time, clone, target_handles={target_handle})
                else:
                    self._queue_tso_callback(retraction_handle, payload.time, callback, target_handles=remove_targets)
            return rti_pb2.CallResponse(
                deleteObjectInstanceWithTimeResponse=rti_pb2.DeleteObjectInstanceWithTimeResponse(
                    result=self._message_retraction_return(retraction_handle)
                )
            )
        if request_kind == "localDeleteObjectInstanceRequest":
            payload = request.localDeleteObjectInstanceRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            if object_instance not in self.object_instances:
                return self._error("ObjectInstanceNotKnown", object_instance)
            current_handle = self._current_federate_handle(peer)
            self.handle_locally_deleted_objects.setdefault(current_handle, set()).add(object_instance)
            return rti_pb2.CallResponse(localDeleteObjectInstanceResponse=rti_pb2.LocalDeleteObjectInstanceResponse())
        if request_kind == "requestInstanceAttributeValueUpdateRequest":
            payload = request.requestInstanceAttributeValueUpdateRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            requested_attributes = [attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle]
            current_handle = self._current_federate_handle(peer)
            if self._mom_attribute_value(object_instance, requested_attributes[0]) is not None:
                self._queue_rti_owned_attribute_reflection(
                    current_handle,
                    object_instance,
                    requested_attributes,
                    payload.userSuppliedTag,
                )
                return rti_pb2.CallResponse(
                    requestInstanceAttributeValueUpdateResponse=rti_pb2.RequestInstanceAttributeValueUpdateResponse()
                )
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            owner_attributes: dict[str, list[str]] = {}
            for attribute in requested_attributes:
                owner_handle = self.attribute_owners.get((object_instance, attribute))
                if owner_handle is None:
                    continue
                owner_attributes.setdefault(owner_handle, []).append(attribute)
            for owner_handle, attributes in owner_attributes.items():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        provideAttributeValueUpdate=callback_pb2.ProvideAttributeValueUpdate(
                            objectInstance=payload.objectInstance,
                            attributes=_attribute_set(tuple(attributes)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    ),
                    target_handles={owner_handle},
                )
            return rti_pb2.CallResponse(
                requestInstanceAttributeValueUpdateResponse=rti_pb2.RequestInstanceAttributeValueUpdateResponse()
            )
        if request_kind == "requestClassAttributeValueUpdateRequest":
            payload = request.requestClassAttributeValueUpdateRequest
            object_class = payload.objectClass.data.decode("ascii")
            requested_attributes = [attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle]
            current_handle = self._current_federate_handle(peer)
            if object_class in {
                self.object_classes["HLAobjectRoot.HLAmanager.HLAfederation"],
                self.object_classes["HLAobjectRoot.HLAmanager.HLAfederate"],
            }:
                for object_instance, record in self.object_instances.items():
                    if record["objectClass"] != object_class:
                        continue
                    self._queue_rti_owned_attribute_reflection(
                        current_handle,
                        object_instance,
                        requested_attributes,
                        payload.userSuppliedTag,
                    )
                return rti_pb2.CallResponse(
                    requestClassAttributeValueUpdateResponse=rti_pb2.RequestClassAttributeValueUpdateResponse()
                )
            for object_instance, record in self.object_instances.items():
                if record["objectClass"] != object_class:
                    continue
                owner_attributes: dict[str, list[str]] = {}
                for attribute in requested_attributes:
                    owner_handle = self.attribute_owners.get((object_instance, attribute))
                    if owner_handle is None:
                        continue
                    owner_attributes.setdefault(owner_handle, []).append(attribute)
                for owner_handle, attributes in owner_attributes.items():
                    self._enqueue_callback(
                        callback_pb2.CallbackRequest(
                            provideAttributeValueUpdate=callback_pb2.ProvideAttributeValueUpdate(
                                objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                                attributes=_attribute_set(tuple(attributes)),
                                userSuppliedTag=payload.userSuppliedTag,
                            )
                        ),
                        target_handles={owner_handle},
                    )
            return rti_pb2.CallResponse(
                requestClassAttributeValueUpdateResponse=rti_pb2.RequestClassAttributeValueUpdateResponse()
            )
        if request_kind == "requestAttributeValueUpdateWithRegionsRequest":
            payload = request.requestAttributeValueUpdateWithRegionsRequest
            object_class = payload.objectClass.data.decode("ascii")
            requested_pairs = list(self._attribute_region_pairs(payload.attributesAndRegions))
            for object_instance, record in self.object_instances.items():
                if record["objectClass"] != object_class:
                    continue
                matching_attributes = [
                    attribute
                    for attribute, _regions in requested_pairs
                    if self._attribute_regions_overlap(object_instance, object_class, attribute)
                ]
                if not matching_attributes:
                    continue
                owner_attributes: dict[str, list[str]] = {}
                for attribute in matching_attributes:
                    owner_handle = self.attribute_owners.get((object_instance, attribute))
                    if owner_handle is None:
                        continue
                    owner_attributes.setdefault(owner_handle, []).append(attribute)
                for owner_handle, attributes in owner_attributes.items():
                    self._enqueue_callback(
                        callback_pb2.CallbackRequest(
                            provideAttributeValueUpdate=callback_pb2.ProvideAttributeValueUpdate(
                                objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                                attributes=_attribute_set(tuple(attributes)),
                                userSuppliedTag=payload.userSuppliedTag,
                            )
                        ),
                        target_handles={owner_handle},
                    )
            return rti_pb2.CallResponse(
                requestAttributeValueUpdateWithRegionsResponse=rti_pb2.RequestAttributeValueUpdateWithRegionsResponse()
            )
        if request_kind == "sendInteractionRequest":
            payload = request.sendInteractionRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            interaction_name = self.interaction_names.get(interaction_class, "")
            if ".HLAmanager." in interaction_name and (
                ".HLAservice." in interaction_name or ".HLAadjust." in interaction_name
            ):
                try:
                    self._route_mom_manager_action(interaction_name, payload.parameterValues, peer=peer)
                except Exception as exc:
                    self._queue_mom_exception_report(interaction_name, exc, parameter_error=False)
                    return self._error("RTIinternalError", str(exc))
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"]:
                self._queue_mim_report()
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestPublications"]:
                self._queue_object_publication_report(payload.parameterValues)
                self._queue_interaction_publication_report(payload.parameterValues)
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestSubscriptions"]:
                self._queue_object_subscription_report(payload.parameterValues)
                self._queue_interaction_subscription_report(payload.parameterValues)
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestInteractionsSent"]:
                params = self._mom_params(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestInteractionsSent",
                    payload.parameterValues,
                )
                requested_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsSent",
                    "HLAinteractionsSent",
                    self.handle_interactions_sent.get(requested_handle, 0),
                    requested_handle,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestInteractionsReceived"]:
                params = self._mom_params(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestInteractionsReceived",
                    payload.parameterValues,
                )
                requested_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsReceived",
                    "HLAinteractionsReceived",
                    self.handle_interactions_received.get(requested_handle, 0),
                    requested_handle,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestUpdatesSent"]:
                params = self._mom_params(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestUpdatesSent",
                    payload.parameterValues,
                )
                requested_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportUpdatesSent",
                    "HLAupdatesSent",
                    self.handle_updates_sent.get(requested_handle, 0),
                    requested_handle,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestReflectionsReceived"]:
                params = self._mom_params(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestReflectionsReceived",
                    payload.parameterValues,
                )
                requested_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportReflectionsReceived",
                    "HLAreflectionsReceived",
                    self.handle_reflections_received.get(requested_handle, 0),
                    requested_handle,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesThatCanBeDeleted"]:
                params = self._mom_params(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesThatCanBeDeleted",
                    payload.parameterValues,
                )
                requested_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
                count = 0
                for object_instance, record in self.object_instances.items():
                    if ".HLAmanager." in record["objectClass"]:
                        continue
                    if any(
                        owner_handle == requested_handle and owned_instance == object_instance
                        for (owned_instance, _attribute), owner_handle in self.attribute_owners.items()
                    ):
                        count += 1
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesThatCanBeDeleted",
                    "HLAobjectInstanceCounts",
                    count,
                    requested_handle,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesUpdated"]:
                params = self._mom_params(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesUpdated",
                    payload.parameterValues,
                )
                requested_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesUpdated",
                    "HLAobjectInstanceCounts",
                    self.handle_object_instances_updated.get(requested_handle, 0),
                    requested_handle,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesReflected"]:
                params = self._mom_params(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesReflected",
                    payload.parameterValues,
                )
                requested_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesReflected",
                    "HLAobjectInstanceCounts",
                    self.handle_object_instances_reflected.get(requested_handle, 0),
                    requested_handle,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestFOMmoduleData"]:
                self._queue_fom_module_data_report(payload.parameterValues)
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestFOMmoduleData"]:
                self._queue_federation_fom_module_data_report(payload.parameterValues)
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstanceInformation"]:
                self._queue_object_instance_information_report(payload.parameterValues)
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPoints"]:
                self._queue_synchronization_points_report()
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPointStatus"]:
                self._queue_synchronization_point_status_report(payload.parameterValues)
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class not in self.published_interactions:
                return self._error("InteractionClassNotPublished", interaction_class)
            target_handles = self._interaction_target_handles(interaction_class, ())
            source_handle = self._current_federate_handle(peer)
            for target_handle in sorted(target_handles, key=int):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        receiveInteraction=callback_pb2.ReceiveInteraction(
                            interactionClass=payload.interactionClass,
                            parameterValues=payload.parameterValues,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=self._interaction_transportation_type(interaction_class),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle(peer)),
                        )
                    ),
                    target_handles={target_handle},
                )
            self.interactions_received += len(target_handles)
            self.interactions_sent += 1
            self._increment_counter(self.handle_interactions_sent, source_handle)
            for target_handle in target_handles:
                self._increment_counter(self.handle_interactions_received, target_handle)
            return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
        if request_kind == "sendInteractionWithRegionsRequest":
            payload = request.sendInteractionWithRegionsRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            source_regions = tuple(region.data.decode("ascii") for region in payload.regions.regionHandle)
            if interaction_class not in self.published_interactions:
                return self._error("InteractionClassNotPublished", interaction_class)
            target_handles = self._interaction_target_handles(interaction_class, source_regions)
            source_handle = self._current_federate_handle(peer)
            for target_handle in sorted(target_handles, key=int):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        receiveInteraction=callback_pb2.ReceiveInteraction(
                            interactionClass=payload.interactionClass,
                            parameterValues=payload.parameterValues,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=self._interaction_transportation_type(interaction_class),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle(peer)),
                            optionalSentRegions=self._conveyed_regions_from(source_regions),
                        )
                    ),
                    target_handles={target_handle},
                )
            self.interactions_received += len(target_handles)
            self.interactions_sent += 1
            self._increment_counter(self.handle_interactions_sent, source_handle)
            for target_handle in target_handles:
                self._increment_counter(self.handle_interactions_received, target_handle)
            return rti_pb2.CallResponse(sendInteractionWithRegionsResponse=rti_pb2.SendInteractionWithRegionsResponse())
        if request_kind == "sendInteractionWithTimeRequest":
            payload = request.sendInteractionWithTimeRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            if interaction_class not in self.published_interactions:
                return self._error("InteractionClassNotPublished", interaction_class)
            source_handle = self._current_federate_handle(peer)
            if not self._validate_tso_send_time(source_handle, payload.time):
                return self._error("InvalidLogicalTime", "Timestamp is earlier than the logical-time/lookahead lower bound")
            retraction_handle = self._next_retraction_handle()
            target_handles = self._interaction_target_handles(interaction_class, ())
            for target_handle in sorted(target_handles, key=int):
                self._queue_tso_callback(
                    retraction_handle,
                    payload.time,
                    callback_pb2.CallbackRequest(
                        receiveInteractionWithTime=callback_pb2.ReceiveInteractionWithTime(
                            interactionClass=payload.interactionClass,
                            parameterValues=payload.parameterValues,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=self._interaction_transportation_type(interaction_class),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle(peer)),
                            time=payload.time,
                            sentOrderType=datatypes_pb2.TIMESTAMP,
                            receivedOrderType=datatypes_pb2.TIMESTAMP,
                            optionalRetraction=_handle(datatypes_pb2.MessageRetractionHandle, retraction_handle),
                        )
                    ),
                    target_handles={target_handle},
                )
            self.interactions_received += len(target_handles)
            self.interactions_sent += 1
            return rti_pb2.CallResponse(
                sendInteractionWithTimeResponse=rti_pb2.SendInteractionWithTimeResponse(
                    result=self._message_retraction_return(retraction_handle)
                )
            )
        if request_kind == "sendInteractionWithRegionsAndTimeRequest":
            payload = request.sendInteractionWithRegionsAndTimeRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            source_regions = tuple(region.data.decode("ascii") for region in payload.regions.regionHandle)
            if interaction_class not in self.published_interactions:
                return self._error("InteractionClassNotPublished", interaction_class)
            source_handle = self._current_federate_handle(peer)
            if not self._validate_tso_send_time(source_handle, payload.time):
                return self._error("InvalidLogicalTime", "Timestamp is earlier than the logical-time/lookahead lower bound")
            retraction_handle = self._next_retraction_handle()
            target_handles = self._interaction_target_handles(interaction_class, source_regions)
            for target_handle in sorted(target_handles, key=int):
                self._queue_tso_callback(
                    retraction_handle,
                    payload.time,
                    callback_pb2.CallbackRequest(
                        receiveInteractionWithTime=callback_pb2.ReceiveInteractionWithTime(
                            interactionClass=payload.interactionClass,
                            parameterValues=payload.parameterValues,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=self._interaction_transportation_type(interaction_class),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, source_handle),
                            time=payload.time,
                            sentOrderType=datatypes_pb2.TIMESTAMP,
                            receivedOrderType=datatypes_pb2.TIMESTAMP,
                            optionalRetraction=_handle(datatypes_pb2.MessageRetractionHandle, retraction_handle),
                            optionalSentRegions=self._conveyed_regions_from(source_regions),
                        )
                    ),
                    target_handles={target_handle},
                )
            self.interactions_received += len(target_handles)
            self.interactions_sent += 1
            self._increment_counter(self.handle_interactions_sent, source_handle)
            for target_handle in target_handles:
                self._increment_counter(self.handle_interactions_received, target_handle)
            return rti_pb2.CallResponse(
                sendInteractionWithRegionsAndTimeResponse=rti_pb2.SendInteractionWithRegionsAndTimeResponse(
                    result=self._message_retraction_return(retraction_handle)
                )
            )
        if request_kind == "sendDirectedInteractionRequest":
            payload = request.sendDirectedInteractionRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            object_class = record["objectClass"]
            interaction_class = payload.interactionClass.data.decode("ascii")
            if interaction_class not in self.published_directed_interactions.get(object_class, set()):
                return self._error("InteractionClassNotPublished", interaction_class)
            target_handles = self._directed_interaction_target_handles(object_instance, object_class, interaction_class)
            source_handle = self._current_federate_handle(peer)
            for target_handle in sorted(target_handles, key=int):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        receiveDirectedInteraction=callback_pb2.ReceiveDirectedInteraction(
                            interactionClass=payload.interactionClass,
                            objectInstance=payload.objectInstance,
                            parameterValues=payload.parameterValues,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle(peer)),
                        )
                    ),
                    target_handles={target_handle},
                )
            self.interactions_received += len(target_handles)
            self.interactions_sent += 1
            self._increment_counter(self.handle_interactions_sent, source_handle)
            for target_handle in target_handles:
                self._increment_counter(self.handle_interactions_received, target_handle)
            return rti_pb2.CallResponse(sendDirectedInteractionResponse=rti_pb2.SendDirectedInteractionResponse())
        if request_kind == "sendDirectedInteractionWithTimeRequest":
            payload = request.sendDirectedInteractionWithTimeRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            object_class = record["objectClass"]
            interaction_class = payload.interactionClass.data.decode("ascii")
            if interaction_class not in self.published_directed_interactions.get(object_class, set()):
                return self._error("InteractionClassNotPublished", interaction_class)
            retraction_handle = self._next_retraction_handle()
            target_handles = self._directed_interaction_target_handles(object_instance, object_class, interaction_class)
            for target_handle in sorted(target_handles, key=int):
                self._queue_tso_callback(
                    retraction_handle,
                    payload.time,
                    callback_pb2.CallbackRequest(
                        receiveDirectedInteractionWithTime=callback_pb2.ReceiveDirectedInteractionWithTime(
                            interactionClass=payload.interactionClass,
                            objectInstance=payload.objectInstance,
                            parameterValues=payload.parameterValues,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle(peer)),
                            time=payload.time,
                            sentOrderType=datatypes_pb2.TIMESTAMP,
                            receivedOrderType=datatypes_pb2.TIMESTAMP,
                            optionalRetraction=_handle(datatypes_pb2.MessageRetractionHandle, retraction_handle),
                        )
                    ),
                    target_handles={target_handle},
                )
            self.interactions_received += len(target_handles)
            self.interactions_sent += 1
            return rti_pb2.CallResponse(
                sendDirectedInteractionWithTimeResponse=rti_pb2.SendDirectedInteractionWithTimeResponse(
                    result=self._message_retraction_return(retraction_handle)
                )
            )
        if request_kind == "retractRequest":
            handle = request.retractRequest.retraction.data.decode("ascii")
            if handle in self.queued_tso_callbacks:
                del self.queued_tso_callbacks[handle]
                if handle not in self.requested_retractions:
                    self.requested_retractions.add(handle)
                    self._queue_request_retraction(handle)
                return rti_pb2.CallResponse(retractResponse=rti_pb2.RetractResponse())
            if handle in self.delivered_retractions:
                if handle not in self.requested_retractions:
                    self.requested_retractions.add(handle)
                    self._queue_request_retraction(handle)
                    return rti_pb2.CallResponse(retractResponse=rti_pb2.RetractResponse())
                return self._error("MessageCanNoLongerBeRetracted", handle)
            return self._error("InvalidMessageRetractionHandle", handle)
        if request_kind == "isAttributeOwnedByFederateRequest":
            payload = request.isAttributeOwnedByFederateRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            attribute = payload.attribute.data.decode("ascii")
            owner_handle = self.attribute_owners.get((object_instance, attribute))
            return rti_pb2.CallResponse(
                isAttributeOwnedByFederateResponse=rti_pb2.IsAttributeOwnedByFederateResponse(
                    result=not self._is_rti_owned_attribute(object_instance, attribute)
                    and (object_instance, attribute) not in self.unowned_attributes
                    and owner_handle == self._current_federate_handle(peer)
                )
            )
        if request_kind == "unconditionalAttributeOwnershipDivestitureRequest":
            payload = request.unconditionalAttributeOwnershipDivestitureRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            requester_handle = self._current_federate_handle(peer)
            for attribute in payload.attributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                key = (object_instance, attribute_value)
                if self.attribute_owners.get(key) != requester_handle:
                    return self._error("AttributeNotOwned", attribute_value)
                self.unowned_attributes.add(key)
                self.attribute_owners.pop(key, None)
            return rti_pb2.CallResponse(unconditionalAttributeOwnershipDivestitureResponse=rti_pb2.UnconditionalAttributeOwnershipDivestitureResponse())
        if request_kind == "queryAttributeOwnershipRequest":
            payload = request.queryAttributeOwnershipRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            unowned = []
            owned = []
            rti_owned = []
            requester_handle = self._current_federate_handle(peer)
            for attribute in payload.attributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                if self._is_rti_owned_attribute(object_instance, attribute_value):
                    rti_owned.append(attribute_value)
                elif (object_instance, attribute_value) in self.unowned_attributes:
                    unowned.append(attribute_value)
                else:
                    owned.append(attribute_value)
            if unowned:
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        attributeIsNotOwned=callback_pb2.AttributeIsNotOwned(
                            objectInstance=payload.objectInstance,
                            attributes=_attribute_set(tuple(unowned)),
                        )
                    ),
                    target_peers={peer},
                )
            if rti_owned:
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        attributeIsOwnedByRTI=callback_pb2.AttributeIsOwnedByRTI(
                            objectInstance=payload.objectInstance,
                            attributes=_attribute_set(tuple(rti_owned)),
                        )
                    ),
                    target_peers={peer},
                )
            if owned:
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        informAttributeOwnership=callback_pb2.InformAttributeOwnership(
                            objectInstance=payload.objectInstance,
                            attributes=_attribute_set(tuple(owned)),
                            federate=_handle(
                                datatypes_pb2.FederateHandle,
                                self.attribute_owners.get((object_instance, owned[0]), self._current_federate_handle(peer)),
                            ),
                        )
                    ),
                    target_peers={peer},
                )
            return rti_pb2.CallResponse(queryAttributeOwnershipResponse=rti_pb2.QueryAttributeOwnershipResponse())
        if request_kind == "attributeOwnershipAcquisitionIfAvailableRequest":
            payload = request.attributeOwnershipAcquisitionIfAvailableRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            requester_handle = self._current_federate_handle(peer)
            available = []
            unavailable = []
            for attribute in payload.desiredAttributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                key = (object_instance, attribute_value)
                if self.attribute_owners.get(key) == requester_handle:
                    return self._error("AttributeAlreadyOwned", attribute_value)
                if key in self.unowned_attributes:
                    self.unowned_attributes.discard(key)
                    self.attribute_owners[key] = requester_handle
                    available.append(attribute_value)
                else:
                    unavailable.append(attribute_value)
            if available:
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        attributeOwnershipAcquisitionNotification=callback_pb2.AttributeOwnershipAcquisitionNotification(
                            objectInstance=payload.objectInstance,
                            securedAttributes=_attribute_set(tuple(available)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    ),
                    target_handles={self._current_federate_handle(peer)},
                )
            if unavailable:
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        attributeOwnershipUnavailable=callback_pb2.AttributeOwnershipUnavailable(
                            objectInstance=payload.objectInstance,
                            attributes=_attribute_set(tuple(unavailable)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    ),
                    target_handles={self._current_federate_handle(peer)},
                )
            return rti_pb2.CallResponse(attributeOwnershipAcquisitionIfAvailableResponse=rti_pb2.AttributeOwnershipAcquisitionIfAvailableResponse())
        if request_kind == "negotiatedAttributeOwnershipDivestitureRequest":
            payload = request.negotiatedAttributeOwnershipDivestitureRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.offered_attributes.add((object_instance, attribute.data.decode("ascii")))
            other_handles = set(self.joined_federate_handles) - {self._current_federate_handle(peer)}
            for handle in sorted(other_handles, key=int):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        requestAttributeOwnershipAssumption=callback_pb2.RequestAttributeOwnershipAssumption(
                            objectInstance=payload.objectInstance,
                            offeredAttributes=payload.attributes,
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    ),
                    target_handles={handle},
                )
            return rti_pb2.CallResponse(negotiatedAttributeOwnershipDivestitureResponse=rti_pb2.NegotiatedAttributeOwnershipDivestitureResponse())
        if request_kind == "attributeOwnershipAcquisitionRequest":
            payload = request.attributeOwnershipAcquisitionRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            offered_by_owner: dict[str, list[str]] = {}
            requested_by_owner: dict[str, list[str]] = {}
            for attribute in payload.desiredAttributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                key = (object_instance, attribute_value)
                self.pending_attribute_acquisitions[key] = payload.userSuppliedTag
                self.pending_attribute_requesters[key] = self._current_federate_handle(peer)
                owner_handle = self.attribute_owners.get(key)
                if key in self.offered_attributes:
                    offered_by_owner.setdefault(owner_handle or self._current_federate_handle(peer), []).append(attribute_value)
                else:
                    requested_by_owner.setdefault(owner_handle or self._current_federate_handle(peer), []).append(attribute_value)
            for owner_handle, attributes in offered_by_owner.items():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        requestDivestitureConfirmation=callback_pb2.RequestDivestitureConfirmation(
                            objectInstance=payload.objectInstance,
                            releasedAttributes=_attribute_set(tuple(attributes)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    ),
                    target_handles={owner_handle},
                )
            for owner_handle, attributes in requested_by_owner.items():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        requestAttributeOwnershipRelease=callback_pb2.RequestAttributeOwnershipRelease(
                            objectInstance=payload.objectInstance,
                            candidateAttributes=_attribute_set(tuple(attributes)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    ),
                    target_handles={owner_handle},
                )
            return rti_pb2.CallResponse(attributeOwnershipAcquisitionResponse=rti_pb2.AttributeOwnershipAcquisitionResponse())
        if request_kind == "confirmDivestitureRequest":
            payload = request.confirmDivestitureRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            confirmed_by_requester: dict[str, list[str]] = {}
            for attribute in payload.confirmedAttributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                key = (object_instance, attribute_value)
                self.offered_attributes.discard(key)
                self.unowned_attributes.discard(key)
                self.pending_attribute_acquisitions.pop(key, None)
                owner_handle = self.pending_attribute_requesters.pop(key, self._current_federate_handle(peer))
                self.attribute_owners[key] = owner_handle
                confirmed_by_requester.setdefault(owner_handle, []).append(attribute_value)
            for owner_handle, attributes in confirmed_by_requester.items():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        attributeOwnershipAcquisitionNotification=callback_pb2.AttributeOwnershipAcquisitionNotification(
                            objectInstance=payload.objectInstance,
                            securedAttributes=_attribute_set(tuple(attributes)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    ),
                    target_handles={owner_handle},
                )
            return rti_pb2.CallResponse(confirmDivestitureResponse=rti_pb2.ConfirmDivestitureResponse())
        if request_kind == "attributeOwnershipDivestitureIfWantedRequest":
            payload = request.attributeOwnershipDivestitureIfWantedRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            divested = []
            divested_by_requester: dict[str, list[str]] = {}
            for attribute in payload.attributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                key = (object_instance, attribute_value)
                if key in self.pending_attribute_acquisitions:
                    self.pending_attribute_acquisitions.pop(key, None)
                    owner_handle = self.pending_attribute_requesters.pop(key, self._current_federate_handle(peer))
                    self.unowned_attributes.discard(key)
                    self.attribute_owners[key] = owner_handle
                    divested.append(attribute_value)
                    divested_by_requester.setdefault(owner_handle, []).append(attribute_value)
            for owner_handle, attributes in divested_by_requester.items():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        attributeOwnershipAcquisitionNotification=callback_pb2.AttributeOwnershipAcquisitionNotification(
                            objectInstance=payload.objectInstance,
                            securedAttributes=_attribute_set(tuple(attributes)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    ),
                    target_handles={owner_handle},
                )
            return rti_pb2.CallResponse(
                attributeOwnershipDivestitureIfWantedResponse=rti_pb2.AttributeOwnershipDivestitureIfWantedResponse(
                    result=_attribute_set(tuple(divested))
                )
            )
        if request_kind == "attributeOwnershipReleaseDeniedRequest":
            payload = request.attributeOwnershipReleaseDeniedRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            requester_handles: set[str] = set()
            for attribute in payload.attributes.attributeHandle:
                key = (object_instance, attribute.data.decode("ascii"))
                self.pending_attribute_acquisitions.pop(key, None)
                requester_handle = self.pending_attribute_requesters.pop(key, None)
                if requester_handle is not None:
                    requester_handles.add(requester_handle)
            for requester_handle in sorted(requester_handles, key=int):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        attributeOwnershipUnavailable=callback_pb2.AttributeOwnershipUnavailable(
                            objectInstance=payload.objectInstance,
                            attributes=payload.attributes,
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    ),
                    target_handles={requester_handle},
                )
            return rti_pb2.CallResponse(attributeOwnershipReleaseDeniedResponse=rti_pb2.AttributeOwnershipReleaseDeniedResponse())
        if request_kind == "cancelAttributeOwnershipAcquisitionRequest":
            payload = request.cancelAttributeOwnershipAcquisitionRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            requester_handles: set[str] = set()
            for attribute in payload.attributes.attributeHandle:
                key = (object_instance, attribute.data.decode("ascii"))
                self.pending_attribute_acquisitions.pop(key, None)
                requester_handle = self.pending_attribute_requesters.pop(key, None)
                if requester_handle is not None:
                    requester_handles.add(requester_handle)
            for requester_handle in sorted(requester_handles, key=int):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        confirmAttributeOwnershipAcquisitionCancellation=callback_pb2.ConfirmAttributeOwnershipAcquisitionCancellation(
                            objectInstance=payload.objectInstance,
                            attributes=payload.attributes,
                        )
                    ),
                    target_handles={requester_handle},
                )
            return rti_pb2.CallResponse(cancelAttributeOwnershipAcquisitionResponse=rti_pb2.CancelAttributeOwnershipAcquisitionResponse())
        if request_kind == "cancelNegotiatedAttributeOwnershipDivestitureRequest":
            payload = request.cancelNegotiatedAttributeOwnershipDivestitureRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.offered_attributes.discard((object_instance, attribute.data.decode("ascii")))
            return rti_pb2.CallResponse(
                cancelNegotiatedAttributeOwnershipDivestitureResponse=rti_pb2.CancelNegotiatedAttributeOwnershipDivestitureResponse()
            )
        if request_kind == "enableTimeRegulationRequest":
            handle = self._current_federate_handle(peer)
            self.handle_time_regulating[handle] = True
            self._set_handle_lookahead(handle, request.enableTimeRegulationRequest.lookahead)
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    timeRegulationEnabled=callback_pb2.TimeRegulationEnabled(
                        time=datatypes_pb2.LogicalTime(data=self._handle_current_time(handle).data)
                    )
                ),
                target_peers={peer},
            )
            self._process_time_advances()
            return rti_pb2.CallResponse(enableTimeRegulationResponse=rti_pb2.EnableTimeRegulationResponse())
        if request_kind == "enableTimeConstrainedRequest":
            handle = self._current_federate_handle(peer)
            self.handle_time_constrained[handle] = True
            self._sync_time_globals(handle)
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    timeConstrainedEnabled=callback_pb2.TimeConstrainedEnabled(
                        time=datatypes_pb2.LogicalTime(data=self._handle_current_time(handle).data)
                    )
                ),
                target_peers={peer},
            )
            self._process_time_advances()
            return rti_pb2.CallResponse(enableTimeConstrainedResponse=rti_pb2.EnableTimeConstrainedResponse())
        if request_kind == "disableTimeRegulationRequest":
            handle = self._current_federate_handle(peer)
            self.handle_time_regulating[handle] = False
            self._sync_time_globals(handle)
            self._process_time_advances()
            return rti_pb2.CallResponse(disableTimeRegulationResponse=rti_pb2.DisableTimeRegulationResponse())
        if request_kind == "disableTimeConstrainedRequest":
            handle = self._current_federate_handle(peer)
            self.handle_time_constrained[handle] = False
            self._sync_time_globals(handle)
            self._process_time_advances()
            return rti_pb2.CallResponse(disableTimeConstrainedResponse=rti_pb2.DisableTimeConstrainedResponse())
        if request_kind == "enableAsynchronousDeliveryRequest":
            handle = self._current_federate_handle(peer)
            self.handle_asynchronous_delivery_enabled[handle] = True
            self._sync_time_globals(handle)
            return rti_pb2.CallResponse(enableAsynchronousDeliveryResponse=rti_pb2.EnableAsynchronousDeliveryResponse())
        if request_kind == "disableAsynchronousDeliveryRequest":
            handle = self._current_federate_handle(peer)
            self.handle_asynchronous_delivery_enabled[handle] = False
            self._sync_time_globals(handle)
            return rti_pb2.CallResponse(disableAsynchronousDeliveryResponse=rti_pb2.DisableAsynchronousDeliveryResponse())
        if request_kind == "timeAdvanceRequestRequest":
            self._request_time_advance(self._current_federate_handle(peer), "timeAdvanceRequest", request.timeAdvanceRequestRequest.time)
            return rti_pb2.CallResponse(timeAdvanceRequestResponse=rti_pb2.TimeAdvanceRequestResponse())
        if request_kind == "timeAdvanceRequestAvailableRequest":
            self._request_time_advance(
                self._current_federate_handle(peer),
                "timeAdvanceRequestAvailable",
                request.timeAdvanceRequestAvailableRequest.time,
            )
            return rti_pb2.CallResponse(timeAdvanceRequestAvailableResponse=rti_pb2.TimeAdvanceRequestAvailableResponse())
        if request_kind == "nextMessageRequestRequest":
            self._request_time_advance(self._current_federate_handle(peer), "nextMessageRequest", request.nextMessageRequestRequest.time)
            return rti_pb2.CallResponse(nextMessageRequestResponse=rti_pb2.NextMessageRequestResponse())
        if request_kind == "nextMessageRequestAvailableRequest":
            self._request_time_advance(
                self._current_federate_handle(peer),
                "nextMessageRequestAvailable",
                request.nextMessageRequestAvailableRequest.time,
            )
            return rti_pb2.CallResponse(nextMessageRequestAvailableResponse=rti_pb2.NextMessageRequestAvailableResponse())
        if request_kind == "flushQueueRequestRequest":
            self._request_time_advance(self._current_federate_handle(peer), "flushQueueRequest", request.flushQueueRequestRequest.time)
            return rti_pb2.CallResponse(flushQueueRequestResponse=rti_pb2.FlushQueueRequestResponse())
        if request_kind == "queryLogicalTimeRequest":
            return rti_pb2.CallResponse(
                queryLogicalTimeResponse=rti_pb2.QueryLogicalTimeResponse(
                    result=self._handle_current_time(self._current_federate_handle(peer)),
                )
            )
        if request_kind == "enableCallbacksRequest":
            self.callback_delivery_enabled = True
            self.peer_callback_delivery_enabled[peer] = True
            return rti_pb2.CallResponse(enableCallbacksResponse=rti_pb2.EnableCallbacksResponse())
        if request_kind == "disableCallbacksRequest":
            self.callback_delivery_enabled = False
            self.peer_callback_delivery_enabled[peer] = False
            return rti_pb2.CallResponse(disableCallbacksResponse=rti_pb2.DisableCallbacksResponse())
        return self._error("RTIinternalError", f"Unsupported 2025 test call: {request_kind}")

    def EvokeCallback(self, request, context):  # noqa: N802 - grpc generated naming
        peer = self._context_peer(context)
        if not self.peer_callback_delivery_enabled.get(peer, True):
            return _callback_request()
        return self._pop_callback_for_peer(peer)

    def _route_mom_manager_action(
        self,
        interaction_name: str,
        parameter_values: datatypes_pb2.ParameterHandleValueMap,
        *,
        peer: str | None = None,
    ) -> None:
        params = self._mom_params(interaction_name, parameter_values)
        leaf = interaction_name.rsplit(".", 1)[-1]
        self.calls.append(f"mom:{leaf}")
        if ".HLAadjust." in interaction_name:
            self._route_mom_adjust(leaf, params)
            return
        self._route_mom_service(leaf, params, peer=peer)

    def _mom_params(
        self,
        interaction_name: str,
        parameter_values: datatypes_pb2.ParameterHandleValueMap,
    ) -> dict[str, bytes]:
        interaction_class = self.interactions[interaction_name]
        params: dict[str, bytes] = {}
        for item in parameter_values.parameterHandleValue:
            parameter_handle = item.parameterHandle.data.decode("ascii")
            parameter_name = self.parameter_names.get((interaction_class, parameter_handle))
            if parameter_name is not None:
                params[parameter_name] = bytes(item.value)
        return params

    @staticmethod
    def _mom_text(params: dict[str, bytes], name: str, default: str = "") -> str:
        value = params.get(name)
        return default if value is None else value.decode("ascii")

    @classmethod
    def _mom_int(cls, params: dict[str, bytes], name: str, default: str = "0") -> str:
        return cls._mom_text(params, name, default)

    @classmethod
    def _mom_attributes(cls, params: dict[str, bytes], name: str = "HLAattributeList") -> tuple[str, ...]:
        text = cls._mom_text(params, name)
        return tuple(item for item in text.replace(";", ",").split(",") if item)

    @classmethod
    def _mom_bool(cls, params: dict[str, bytes], name: str, default: bool = True) -> bool:
        text = cls._mom_text(params, name, "HLAtrue" if default else "HLAfalse").lower()
        if text in {"1", "true", "yes", "hlatrue", "on"}:
            return True
        if text in {"0", "false", "no", "hlafalse", "off"}:
            return False
        raise ValueError(f"Invalid MOM boolean value for {name}")

    @classmethod
    def _mom_time(cls, params: dict[str, bytes], name: str = "HLAtimeStamp") -> datatypes_pb2.LogicalTime:
        text = cls._mom_text(params, name, "0")
        return datatypes_pb2.LogicalTime(data=f"HLAinteger64Time:{text}".encode("ascii"))

    @classmethod
    def _mom_interval(cls, params: dict[str, bytes], name: str = "HLAlookahead") -> datatypes_pb2.LogicalTimeInterval:
        text = cls._mom_text(params, name, "0")
        return datatypes_pb2.LogicalTimeInterval(data=f"HLAinteger64Interval:{text}".encode("ascii"))

    @classmethod
    def _mom_resign_action(cls, params: dict[str, bytes], name: str = "HLAresignAction") -> int:
        text = cls._mom_text(params, name, "NO_ACTION")
        try:
            return int(text)
        except ValueError:
            normalized = text.removeprefix("HLA").replace("_", "").replace("-", "").upper()
            aliases = {
                "NOACTION": datatypes_pb2.NO_ACTION,
                "UNCONDITIONALLYDIVESTATTRIBUTES": datatypes_pb2.UNCONDITIONALLY_DIVEST_ATTRIBUTES,
                "DELETEOBJECTS": datatypes_pb2.DELETE_OBJECTS,
                "CANCELPENDINGOWNERSHIPACQUISITIONS": datatypes_pb2.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS,
                "DELETEOBJECTSTHENDIVEST": datatypes_pb2.DELETE_OBJECTS_THEN_DIVEST,
                "CANCELTHENDELETETHENDIVEST": datatypes_pb2.CANCEL_THEN_DELETE_THEN_DIVEST,
            }
            if normalized in aliases:
                return aliases[normalized]
            try:
                return datatypes_pb2.ResignAction.Value(text)
            except ValueError:
                raise ValueError(f"Invalid MOM resign action {text!r}")

    @staticmethod
    def _increment_counter(counter: dict[str, int], handle: str, amount: int = 1) -> None:
        counter[handle] = counter.get(handle, 0) + amount

    def _route_mom_adjust(self, leaf: str, params: dict[str, bytes]) -> None:
        if leaf in {"HLAsetServiceReporting", "HLAsetExceptionReporting"}:
            switch_name = "serviceReporting" if leaf == "HLAsetServiceReporting" else "exceptionReporting"
            if switch_name == "serviceReporting":
                target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
                self.handle_service_reporting[target_handle] = self._mom_bool(params, "HLAreportingState")
                self._recompute_service_reporting()
                self.switch_states[switch_name] = self.service_reporting
            else:
                target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
                self.handle_exception_reporting[target_handle] = self._mom_bool(params, "HLAreportingState")
                self._recompute_exception_reporting()
            return
        if leaf == "HLAsetSwitches":
            for parameter_name, raw_value in params.items():
                if parameter_name == "HLAfederate":
                    continue
                switch_name = parameter_name.removeprefix("HLA")
                switch_name = switch_name[:1].lower() + switch_name[1:]
                self.switch_states[switch_name] = self._mom_bool({parameter_name: raw_value}, parameter_name)
            return
        if leaf == "HLAsetTiming":
            self.mom_report_period = self._mom_text(params, "HLAreportPeriod", "0")
            return
        if leaf == "HLAmodifyAttributeState":
            object_instance = self._mom_int(params, "HLAobjectInstance")
            attribute = self._mom_int(params, "HLAattribute")
            state = self._mom_text(params, "HLAattributeState", "owned")
            normalized_state = state.removeprefix("HLA").replace("_", "").replace("-", "").lower()
            key = (object_instance, attribute)
            if normalized_state in {"0", "unowned", "notowned", "attributeisnotowned", "none"}:
                self.unowned_attributes.add(key)
                return
            if normalized_state in {"1", "owned", "owner", "ownedbyfederate", "attributeowned"}:
                self.unowned_attributes.discard(key)
                return
            raise ValueError("Invalid MOM ownership state for HLAattributeState")

    def _route_mom_service(self, leaf: str, params: dict[str, bytes], *, peer: str | None = None) -> None:
        if leaf == "HLAresignFederationExecution":
            handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
            self._apply_resign_action(self._mom_resign_action(params))
            self._remove_federate_handle(handle, peer=peer)
            return
        if leaf == "HLAsynchronizationPointAchieved":
            label = self._mom_text(params, "HLAlabel")
            record = self._synchronization_point_record(label)
            if self._mom_bool(params, "HLAsuccessIndicator", True):
                record["achieved"].add(self._mom_text(params, "HLAfederate", self._current_federate_handle()))
                self._queue_federation_synchronized_if_ready(label)
            return
        if leaf == "HLAfederateSaveBegun":
            if self.save_label is not None:
                self.save_status[self._mom_text(params, "HLAfederate", self._current_federate_handle())] = datatypes_pb2.FEDERATE_SAVING
            return
        if leaf == "HLAfederateSaveComplete":
            if self.save_label is not None and self._mom_bool(params, "HLAsuccessIndicator", True):
                target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
                self.save_status[target_handle] = datatypes_pb2.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE
                self.saved_snapshots[self.save_label] = self._snapshot()
                self.saved_labels.add(self.save_label)
                self.save_label = None
                self.save_status = {}
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(federationSaved=callback_pb2.FederationSaved()),
                    target_handles={target_handle},
                )
            return
        if leaf == "HLAfederateRestoreComplete":
            if self.restore_label is not None and self._mom_bool(params, "HLAsuccessIndicator", True):
                target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
                self.restore_status[target_handle] = datatypes_pb2.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE
                self._restore_snapshot(self.restore_label)
                self.restore_label = None
                self.restore_status = {}
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(federationRestored=callback_pb2.FederationRestored()),
                    target_handles={target_handle},
                )
            return
        if leaf == "HLApublishObjectClassAttributes":
            object_class = self._mom_int(params, "HLAobjectClass")
            handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_published_object_attributes.setdefault(handle, {}).setdefault(object_class, set()).update(self._mom_attributes(params))
            self._rebuild_published_object_aggregates()
            return
        if leaf == "HLAunpublishObjectClassAttributes":
            object_class = self._mom_int(params, "HLAobjectClass")
            handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_published_object_attributes.get(handle, {}).get(object_class, set()).difference_update(self._mom_attributes(params))
            if not self.handle_published_object_attributes.get(handle, {}).get(object_class, set()):
                self.handle_published_object_attributes.get(handle, {}).pop(object_class, None)
            self._rebuild_published_object_aggregates()
            return
        if leaf == "HLAsubscribeObjectClassAttributes":
            object_class = self._mom_int(params, "HLAobjectClass")
            handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_subscribed_object_attributes.setdefault(handle, {}).setdefault(object_class, set()).update(
                self._mom_attributes(params)
            )
            self._rebuild_subscribed_object_aggregates()
            return
        if leaf == "HLAunsubscribeObjectClassAttributes":
            object_class = self._mom_int(params, "HLAobjectClass")
            handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_subscribed_object_attributes.setdefault(handle, {}).setdefault(object_class, set()).difference_update(
                self._mom_attributes(params)
            )
            self._rebuild_subscribed_object_aggregates()
            return
        if leaf == "HLApublishInteractionClass":
            handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_published_interactions.setdefault(handle, set()).add(self._mom_int(params, "HLAinteractionClass"))
            self._rebuild_published_interaction_aggregates()
            return
        if leaf == "HLAunpublishInteractionClass":
            handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_published_interactions.setdefault(handle, set()).discard(self._mom_int(params, "HLAinteractionClass"))
            self._rebuild_published_interaction_aggregates()
            return
        if leaf == "HLAsubscribeInteractionClass":
            handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_subscribed_interactions.setdefault(handle, set()).add(self._mom_int(params, "HLAinteractionClass"))
            self._rebuild_subscribed_interaction_aggregates()
            return
        if leaf == "HLAunsubscribeInteractionClass":
            handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_subscribed_interactions.setdefault(handle, set()).discard(self._mom_int(params, "HLAinteractionClass"))
            self._rebuild_subscribed_interaction_aggregates()
            return
        if leaf == "HLAdeleteObjectInstance":
            object_instance = self._mom_required_text(params, "HLAobjectInstance")
            record = self._remove_object_instance(object_instance)
            if record is not None:
                target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
                remove_targets = self._discovery_target_handles(record["objectClass"], exclude_handle=target_handle)
                if remove_targets:
                    callback = callback_pb2.CallbackRequest(
                        removeObjectInstance=callback_pb2.RemoveObjectInstance(
                            objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                            userSuppliedTag=params.get("HLAtag", b"MOM"),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, target_handle),
                        )
                    )
                    if len(remove_targets) > 1:
                        self._enqueue_callback_per_handle(callback, target_handles=remove_targets)
                    else:
                        self._enqueue_callback(callback, target_handles=remove_targets)
            return
        if leaf == "HLAlocalDeleteObjectInstance":
            object_instance = self._mom_required_text(params, "HLAobjectInstance")
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
            if object_instance not in self.object_instances:
                raise ValueError(f"Unknown MOM local-delete object instance {object_instance}")
            self.handle_locally_deleted_objects.setdefault(target_handle, set()).add(object_instance)
            return
        if leaf == "HLArequestAttributeTransportationTypeChange":
            object_instance = self._mom_int(params, "HLAobjectInstance")
            transportation = self._mom_text(params, "HLAtransportation", "HLAreliable")
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
            attributes = self._mom_attributes(params)
            for attribute in attributes:
                self.default_attribute_transportation[(object_instance, attribute)] = transportation
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    confirmAttributeTransportationTypeChange=callback_pb2.ConfirmAttributeTransportationTypeChange(
                        objectInstance=datatypes_pb2.ObjectInstanceHandle(data=str(object_instance).encode("ascii")),
                        attributes=datatypes_pb2.AttributeHandleSet(
                            attributeHandle=[datatypes_pb2.AttributeHandle(data=str(attribute).encode("ascii")) for attribute in attributes]
                        ),
                        transportationType=datatypes_pb2.TransportationTypeHandle(
                            data=self.transportations[transportation].encode("ascii")
                        ),
                    )
                ),
                target_handles={target_handle},
            )
            return
        if leaf == "HLArequestInteractionTransportationTypeChange":
            interaction_class = self._mom_int(params, "HLAinteractionClass")
            transportation = self._mom_text(params, "HLAtransportation", "HLAreliable")
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle(peer))
            self.interaction_transportation = (
                interaction_class,
                transportation,
            )
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    confirmInteractionTransportationTypeChange=callback_pb2.ConfirmInteractionTransportationTypeChange(
                        interactionClass=datatypes_pb2.InteractionClassHandle(data=str(interaction_class).encode("ascii")),
                        transportationType=datatypes_pb2.TransportationTypeHandle(
                            data=self.transportations[transportation].encode("ascii")
                        ),
                    )
                ),
                target_handles={target_handle},
            )
            return
        if leaf == "HLAchangeAttributeOrderType":
            object_instance = self._mom_int(params, "HLAobjectInstance")
            order = self._mom_order(params)
            for attribute in self._mom_attributes(params):
                self.default_attribute_order[(object_instance, attribute)] = order
            return
        if leaf == "HLAchangeInteractionOrderType":
            self.interaction_order = (self._mom_int(params, "HLAinteractionClass"), self._mom_order(params))
            return
        if leaf == "HLAunconditionalAttributeOwnershipDivestiture":
            object_instance = self._mom_int(params, "HLAobjectInstance")
            for attribute in self._mom_attributes(params):
                self.unowned_attributes.add((object_instance, attribute))
            return
        if leaf == "HLAenableTimeRegulation":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_time_regulating[target_handle] = True
            self._set_handle_lookahead(target_handle, self._mom_interval(params))
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    timeRegulationEnabled=callback_pb2.TimeRegulationEnabled(time=self._handle_current_time(target_handle))
                ),
                target_handles={target_handle},
            )
            self._process_time_advances()
            return
        if leaf == "HLAdisableTimeRegulation":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_time_regulating[target_handle] = False
            self._sync_time_globals(target_handle)
            self._process_time_advances()
            return
        if leaf == "HLAenableTimeConstrained":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_time_constrained[target_handle] = True
            self._sync_time_globals(target_handle)
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    timeConstrainedEnabled=callback_pb2.TimeConstrainedEnabled(time=self._handle_current_time(target_handle))
                ),
                target_handles={target_handle},
            )
            self._process_time_advances()
            return
        if leaf == "HLAdisableTimeConstrained":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_time_constrained[target_handle] = False
            self._sync_time_globals(target_handle)
            self._process_time_advances()
            return
        if leaf == "HLAenableAsynchronousDelivery":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_asynchronous_delivery_enabled[target_handle] = True
            self._sync_time_globals(target_handle)
            return
        if leaf == "HLAdisableAsynchronousDelivery":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_asynchronous_delivery_enabled[target_handle] = False
            self._sync_time_globals(target_handle)
            return
        if leaf in {
            "HLAtimeAdvanceRequest",
            "HLAtimeAdvanceRequestAvailable",
            "HLAnextMessageRequest",
            "HLAnextMessageRequestAvailable",
        }:
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self._request_time_advance(target_handle, leaf.removeprefix("HLA"), self._mom_time(params))
            return
        if leaf == "HLAflushQueueRequest":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self._request_time_advance(target_handle, "flushQueueRequest", self._mom_time(params))
            return
        if leaf == "HLAmodifyLookahead":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self._set_handle_lookahead(target_handle, self._mom_interval(params))
            self._process_time_advances()

    @classmethod
    def _mom_order(cls, params: dict[str, bytes]) -> int:
        text = cls._mom_text(params, "HLAsendOrder", "0").strip()
        try:
            value = int(text)
        except ValueError:
            normalized = text.removeprefix("HLA").replace("_", "").replace("-", "").upper()
            if normalized in {"TIMESTAMP", "TSO"}:
                return datatypes_pb2.TIMESTAMP
            if normalized in {"RECEIVE", "RO"}:
                return datatypes_pb2.RECEIVE
            raise ValueError("Invalid MOM order type for HLAsendOrder")
        return datatypes_pb2.TIMESTAMP if value == 1 else datatypes_pb2.RECEIVE

    @classmethod
    def _mom_required_text(cls, params: dict[str, bytes], name: str) -> str:
        value = params.get(name)
        if value is None or not value:
            raise ValueError(f"Missing MOM parameter {name}")
        return value.decode("ascii")

    @staticmethod
    def _error(name: str, details: str) -> rti_pb2.CallResponse:
        return rti_pb2.CallResponse(
            exceptionData=datatypes_pb2.ExceptionData(
                exceptionName=name,
                details=details,
            )
        )

    def _queue_discovery(
        self,
        object_instance: str,
        object_class: str,
        object_name: str,
        *,
        target_handles: set[str] | None = None,
    ) -> None:
        callback = callback_pb2.CallbackRequest(
            discoverObjectInstance=callback_pb2.DiscoverObjectInstance(
                objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                objectClass=_handle(datatypes_pb2.ObjectClassHandle, object_class),
                objectInstanceName=object_name,
                producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
            )
        )
        if target_handles is not None and len(target_handles) > 1:
            self._enqueue_callback_per_handle(callback, target_handles=target_handles)
            return
        self._enqueue_callback(callback, target_handles=target_handles)

    def _queue_turn_updates_on(
        self,
        object_class: str,
        attributes: set[str],
        update_rate_designator: str = "",
        *,
        target_handles: set[str] | None = None,
    ) -> None:
        if not attributes:
            return
        published = self.published_object_attributes.get(object_class, set())
        relevant = sorted(attributes & published, key=int)
        if not relevant:
            return
        for object_instance, record in sorted(self.object_instances.items(), key=lambda item: int(item[0])):
            if record["objectClass"] != object_class:
                continue
            self._queue_turn_updates_on_for_object_instance(
                object_instance,
                set(relevant),
                update_rate_designator,
                target_handles=target_handles,
            )

    def _queue_turn_updates_on_for_object_instance(
        self,
        object_instance: str,
        attributes: set[str],
        update_rate_designator: str = "",
        *,
        target_handles: set[str] | None = None,
    ) -> None:
        relevant = tuple(sorted(attributes, key=int))
        if not relevant:
            return
        if update_rate_designator:
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    turnUpdatesOnForObjectInstanceWithRate=callback_pb2.TurnUpdatesOnForObjectInstanceWithRate(
                        objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                        attributes=_attribute_set(relevant),
                        updateRateDesignator=update_rate_designator,
                    )
                ),
                target_handles=target_handles,
            )
            return
        self._enqueue_callback(
            callback_pb2.CallbackRequest(
                turnUpdatesOnForObjectInstance=callback_pb2.TurnUpdatesOnForObjectInstance(
                    objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                    attributes=_attribute_set(relevant),
                )
            ),
            target_handles=target_handles,
        )

    def _queue_turn_updates_off(
        self,
        object_class: str,
        attributes: set[str],
        *,
        target_handles: set[str] | None = None,
    ) -> None:
        if not attributes:
            return
        for object_instance, record in sorted(self.object_instances.items(), key=lambda item: int(item[0])):
            if record["objectClass"] != object_class:
                continue
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    turnUpdatesOffForObjectInstance=callback_pb2.TurnUpdatesOffForObjectInstance(
                        objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                        attributes=_attribute_set(tuple(sorted(attributes, key=int))),
                    )
                ),
                target_handles=target_handles,
            )

    def _object_subscription_matches(self, published_class: str, subscribed_class: str) -> bool:
        published_name = self.object_class_names.get(published_class, "")
        subscribed_name = self.object_class_names.get(subscribed_class, "")
        return bool(
            published_name
            and subscribed_name
            and (published_name == subscribed_name or published_name.startswith(f"{subscribed_name}."))
        )

    def _interaction_subscription_matches(self, published_class: str, subscribed_class: str) -> bool:
        published_name = self.interaction_names.get(published_class, "")
        subscribed_name = self.interaction_names.get(subscribed_class, "")
        return bool(
            published_name
            and subscribed_name
            and (published_name == subscribed_name or published_name.startswith(f"{subscribed_name}."))
        )

    def _attribute_names_for_class(self, object_class: str, attributes: set[str]) -> set[str]:
        return {
            self.attribute_names[(object_class, attribute)]
            for attribute in attributes
            if (object_class, attribute) in self.attribute_names
        }

    def _registration_interest_snapshot(self) -> dict[str, set[str]]:
        snapshot: dict[str, set[str]] = {}
        for publisher_handle, object_class_map in self.handle_published_object_attributes.items():
            interested_classes: set[str] = set()
            for published_class, published_attributes in object_class_map.items():
                published_names = self._attribute_names_for_class(published_class, published_attributes)
                if not published_names:
                    continue
                for subscriber_handle, subscribed_map in self.handle_subscribed_object_attributes.items():
                    if subscriber_handle == publisher_handle:
                        continue
                    matched = False
                    for subscribed_class, subscribed_attributes in subscribed_map.items():
                        if not self._object_subscription_matches(published_class, subscribed_class):
                            continue
                        subscribed_names = self._attribute_names_for_class(subscribed_class, subscribed_attributes)
                        if published_names & subscribed_names:
                            interested_classes.add(published_class)
                            matched = True
                            break
                    if matched:
                        break
            snapshot[publisher_handle] = interested_classes
        return snapshot

    def _interaction_interest_snapshot(self) -> dict[str, set[str]]:
        snapshot: dict[str, set[str]] = {}
        for publisher_handle, published_classes in self.handle_published_interactions.items():
            interested_classes: set[str] = set()
            for published_class in published_classes:
                for subscriber_handle, subscribed_classes in self.handle_subscribed_interactions.items():
                    if subscriber_handle == publisher_handle:
                        continue
                    if any(
                        self._interaction_subscription_matches(published_class, subscribed_class)
                        for subscribed_class in subscribed_classes
                    ):
                        interested_classes.add(published_class)
                        break
            snapshot[publisher_handle] = interested_classes
        return snapshot

    def _emit_registration_interest_transitions(self, previous: dict[str, set[str]]) -> None:
        current = self._registration_interest_snapshot()
        for handle in sorted(set(previous) | set(current), key=int):
            prior_classes = previous.get(handle, set())
            current_classes = current.get(handle, set())
            for object_class in sorted(prior_classes - current_classes, key=int):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        stopRegistrationForObjectClass=callback_pb2.StopRegistrationForObjectClass(
                            objectClass=_handle(datatypes_pb2.ObjectClassHandle, object_class)
                        )
                    ),
                    target_handles={handle},
                )
            for object_class in sorted(current_classes - prior_classes, key=int):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        startRegistrationForObjectClass=callback_pb2.StartRegistrationForObjectClass(
                            objectClass=_handle(datatypes_pb2.ObjectClassHandle, object_class)
                        )
                    ),
                    target_handles={handle},
                )

    def _emit_interaction_interest_transitions(self, previous: dict[str, set[str]]) -> None:
        current = self._interaction_interest_snapshot()
        for handle in sorted(set(previous) | set(current), key=int):
            prior_classes = previous.get(handle, set())
            current_classes = current.get(handle, set())
            for interaction_class in sorted(prior_classes - current_classes, key=int):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        turnInteractionsOff=callback_pb2.TurnInteractionsOff(
                            interactionClass=_handle(datatypes_pb2.InteractionClassHandle, interaction_class)
                        )
                    ),
                    target_handles={handle},
                )
            for interaction_class in sorted(current_classes - prior_classes, key=int):
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        turnInteractionsOn=callback_pb2.TurnInteractionsOn(
                            interactionClass=_handle(datatypes_pb2.InteractionClassHandle, interaction_class)
                        )
                    ),
                    target_handles={handle},
                )

    def _rebuild_subscribed_object_aggregates(self) -> None:
        self.subscribed_object_attributes.clear()
        self.subscribed_object_regions.clear()
        for object_class_map in self.handle_subscribed_object_attributes.values():
            for object_class, attributes in object_class_map.items():
                if attributes:
                    self.subscribed_object_attributes.setdefault(object_class, set()).update(attributes)
        for object_class_regions in self.handle_subscribed_object_regions.values():
            for object_class, attribute_regions in object_class_regions.items():
                aggregate_regions = self.subscribed_object_regions.setdefault(object_class, {})
                for attribute, regions in attribute_regions.items():
                    if regions:
                        aggregate_regions.setdefault(attribute, set()).update(regions)

    def _rebuild_published_object_aggregates(self) -> None:
        self.published_object_attributes.clear()
        for object_class_map in self.handle_published_object_attributes.values():
            for object_class, attributes in object_class_map.items():
                if attributes:
                    self.published_object_attributes.setdefault(object_class, set()).update(attributes)

    def _rebuild_published_interaction_aggregates(self) -> None:
        self.published_interactions.clear()
        for interactions in self.handle_published_interactions.values():
            self.published_interactions.update(interactions)

    def _rebuild_published_directed_interactions(self) -> None:
        self.published_directed_interactions.clear()
        for object_class_map in self.handle_published_directed_interactions.values():
            for object_class, interactions in object_class_map.items():
                if interactions:
                    self.published_directed_interactions.setdefault(object_class, set()).update(interactions)

    def _rebuild_subscribed_interaction_aggregates(self) -> None:
        self.subscribed_interactions.clear()
        self.subscribed_interaction_regions.clear()
        for interactions in self.handle_subscribed_interactions.values():
            self.subscribed_interactions.update(interactions)
        for interaction_regions in self.handle_subscribed_interaction_regions.values():
            for interaction_class, regions in interaction_regions.items():
                if regions:
                    self.subscribed_interaction_regions.setdefault(interaction_class, set()).update(regions)

    def _rebuild_subscribed_directed_interactions(self) -> None:
        self.subscribed_directed_interactions.clear()
        for object_class_map in self.handle_subscribed_directed_interactions.values():
            for object_class, interactions in object_class_map.items():
                if interactions:
                    self.subscribed_directed_interactions.setdefault(object_class, set()).update(interactions)

    def _discovery_target_handles(self, object_class: str, *, exclude_handle: str | None = None) -> set[str]:
        targets = {
            handle
            for handle, object_class_map in self.handle_subscribed_object_attributes.items()
            if object_class_map.get(object_class)
        }
        if exclude_handle is not None and len(targets) > 1:
            targets.discard(exclude_handle)
        return targets

    def _recompute_service_reporting(self) -> None:
        self.service_reporting = any(
            self.handle_service_reporting.get(handle, False)
            for handle in self._joined_handle_values()
        )

    def _recompute_exception_reporting(self) -> None:
        self.switch_states["exceptionReporting"] = any(
            self.handle_exception_reporting.get(handle, False)
            for handle in self._joined_handle_values()
        )

    def _service_report_target_handles(self) -> set[str]:
        targets = {
            handle
            for handle in self._joined_handle_values()
            if self.handle_service_reporting.get(handle, self.service_reporting)
        }
        if not targets and self.service_reporting:
            return set(self._joined_handle_values())
        return targets

    def _queue_service_report(self, service_name: str, *, peer: str | None = None) -> None:
        target_handles = self._service_report_target_handles()
        if not target_handles:
            return
        source_handle = self._current_federate_handle(peer)
        interaction_class = self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"]
        values = datatypes_pb2.ParameterHandleValueMap()
        for parameter_name, payload in (
            ("HLAfederate", source_handle.encode("ascii")),
            ("HLAservice", service_name.encode("ascii")),
            ("HLAserialNumber", str(self.service_report_serial).encode("ascii")),
        ):
            row = values.parameterHandleValue.add()
            row.parameterHandle.data = self.parameters[(interaction_class, parameter_name)].encode("ascii")
            row.value = payload
        self.service_report_serial += 1
        callback = callback_pb2.CallbackRequest(
            receiveInteraction=callback_pb2.ReceiveInteraction(
                interactionClass=_handle(datatypes_pb2.InteractionClassHandle, interaction_class),
                parameterValues=values,
                userSuppliedTag=b"MOM",
                transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                producingFederate=_handle(datatypes_pb2.FederateHandle, source_handle),
            )
        )
        if len(target_handles) > 1:
            self._enqueue_callback_per_handle(callback, target_handles=target_handles)
        else:
            self._enqueue_callback(callback, target_handles=target_handles)

    def _queue_mom_exception_report(self, interaction_name: str, exception: Exception, *, parameter_error: bool) -> None:
        report_name = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
        report_class = self.interactions.get(report_name)
        target_handles = self._exception_report_target_handles(report_class) if report_class is not None else set()
        if report_class is None or not target_handles:
            return
        values = datatypes_pb2.ParameterHandleValueMap()
        for parameter_name, payload in (
            ("HLAservice", interaction_name.encode("utf-8")),
            ("HLAexception", f"{type(exception).__name__}: {exception}".encode("utf-8")),
            ("HLAparameterError", b"HLAtrue" if parameter_error else b"HLAfalse"),
        ):
            row = values.parameterHandleValue.add()
            row.parameterHandle.data = self.parameters[(report_class, parameter_name)].encode("ascii")
            row.value = payload
        self._enqueue_callback_per_handle(
            callback_pb2.CallbackRequest(
                receiveInteraction=callback_pb2.ReceiveInteraction(
                    interactionClass=_handle(datatypes_pb2.InteractionClassHandle, report_class),
                    parameterValues=values,
                    userSuppliedTag=b"MOM",
                    transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                    producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                )
            ),
            target_handles=target_handles,
        )

    def _queue_object_publication_report(self, parameters: datatypes_pb2.ParameterHandleValueMap) -> None:
        report_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication"
        ]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        request_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestPublications"
        ]
        requested_handle = "1"
        requested_parameter = self.parameters[(request_class, "HLAfederate")]
        for item in parameters.parameterHandleValue:
            if item.parameterHandle.data.decode("ascii") == requested_parameter:
                requested_handle = item.value.decode("ascii")
                break
        requested_publications = self.handle_published_object_attributes.get(requested_handle, {})
        publication_items = [
            (
                object_class,
                ",".join(sorted(attributes, key=int)),
                ",".join(f"{object_class}:{attribute}" for attribute in sorted(attributes, key=int)),
            )
            for object_class, attributes in sorted(requested_publications.items(), key=lambda item: int(item[0]))
            if attributes
        ]
        object_classes = ",".join(object_class for object_class, _attributes, _composite_attributes in publication_items)
        attribute_lists = ";".join(
            composite_attributes for _object_class, _attributes, composite_attributes in publication_items
        )
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": requested_handle.encode("ascii"),
                "HLAnumberOfClasses": str(len(publication_items)).encode("ascii"),
                "HLAobjectClass": object_classes.encode("ascii"),
                "HLAattributeList": attribute_lists.encode("ascii"),
            },
        )

    def _queue_object_subscription_report(self, parameters: datatypes_pb2.ParameterHandleValueMap) -> None:
        report_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription"
        ]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        request_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestSubscriptions"
        ]
        requested_handle = "1"
        requested_parameter = self.parameters[(request_class, "HLAfederate")]
        for item in parameters.parameterHandleValue:
            if item.parameterHandle.data.decode("ascii") == requested_parameter:
                requested_handle = item.value.decode("ascii")
                break
        requested_subscriptions = self.handle_subscribed_object_attributes.get(requested_handle, {})
        subscription_items = [
            (
                object_class,
                ",".join(sorted(attributes, key=int)),
                ",".join(f"{object_class}:{attribute}" for attribute in sorted(attributes, key=int)),
            )
            for object_class, attributes in sorted(requested_subscriptions.items(), key=lambda item: int(item[0]))
            if attributes
        ]
        object_classes = ",".join(object_class for object_class, _attributes, _composite_attributes in subscription_items)
        attribute_lists = ";".join(
            composite_attributes for _object_class, _attributes, composite_attributes in subscription_items
        )
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": requested_handle.encode("ascii"),
                "HLAnumberOfClasses": str(len(subscription_items)).encode("ascii"),
                "HLAobjectClass": object_classes.encode("ascii"),
                "HLAactive": b"HLAtrue" if subscription_items else b"HLAfalse",
                "HLAmaxUpdateRate": b"",
                "HLAattributeList": attribute_lists.encode("ascii"),
            },
        )

    def _queue_interaction_publication_report(self, parameters: datatypes_pb2.ParameterHandleValueMap) -> None:
        report_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionPublication"
        ]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        request_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestPublications"
        ]
        requested_handle = "1"
        requested_parameter = self.parameters[(request_class, "HLAfederate")]
        for item in parameters.parameterHandleValue:
            if item.parameterHandle.data.decode("ascii") == requested_parameter:
                requested_handle = item.value.decode("ascii")
                break
        requested_publications = sorted(self.handle_published_interactions.get(requested_handle, ()), key=int)
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": requested_handle.encode("ascii"),
                "HLAinteractionClassList": ",".join(requested_publications).encode("ascii"),
            },
        )

    def _queue_interaction_subscription_report(self, parameters: datatypes_pb2.ParameterHandleValueMap) -> None:
        report_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionSubscription"
        ]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        request_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestSubscriptions"
        ]
        requested_handle = "1"
        requested_parameter = self.parameters[(request_class, "HLAfederate")]
        for item in parameters.parameterHandleValue:
            if item.parameterHandle.data.decode("ascii") == requested_parameter:
                requested_handle = item.value.decode("ascii")
                break
        requested_subscriptions = sorted(self.handle_subscribed_interactions.get(requested_handle, ()), key=int)
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": requested_handle.encode("ascii"),
                "HLAinteractionClassList": ",".join(requested_subscriptions).encode("ascii"),
            },
        )

    def _queue_activity_count_report(self, report_name: str, count_parameter: str, count: int, federate_handle: str = "1") -> None:
        report_class = self.interactions[report_name]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": federate_handle.encode("ascii"),
                count_parameter: str(count).encode("ascii"),
            },
        )

    def _queue_object_instance_information_report(self, parameters: datatypes_pb2.ParameterHandleValueMap) -> None:
        report_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation"
        ]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        request_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstanceInformation"
        ]
        requested_handle = "1"
        requested_object = ""
        requested_federate_parameter = self.parameters[(request_class, "HLAfederate")]
        requested_parameter = self.parameters[(request_class, "HLAobjectInstance")]
        for item in parameters.parameterHandleValue:
            parameter_handle = item.parameterHandle.data.decode("ascii")
            if parameter_handle == requested_federate_parameter:
                requested_handle = item.value.decode("ascii")
            if parameter_handle == requested_parameter:
                requested_object = item.value.decode("ascii")
        rows = []
        for object_instance, record in sorted(self.object_instances.items(), key=lambda item: int(item[0])):
            if requested_object and object_instance != requested_object:
                continue
            object_class = record["objectClass"]
            attributes = sorted(
                attribute for (attribute_class, _name), attribute in self.attributes.items() if attribute_class == object_class
            )
            rows.append(
                {
                    "objectInstance": object_instance,
                    "objectClass": object_class,
                    "objectInstanceName": record["name"],
                    "attributeList": ",".join(attributes),
                    "ownedInstanceAttributeList": ",".join(
                        sorted(
                            (
                                attribute
                                for (owned_instance, attribute), owner_handle in self.attribute_owners.items()
                                if owned_instance == object_instance and owner_handle == requested_handle
                            ),
                            key=int,
                        )
                    ),
                }
            )
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": requested_handle.encode("ascii"),
                "HLAobjectInstance": ";".join(row["objectInstance"] for row in rows).encode("ascii"),
                "HLAobjectClass": ";".join(row["objectClass"] for row in rows).encode("ascii"),
                "HLAobjectInstanceName": ";".join(row["objectInstanceName"] for row in rows).encode("ascii"),
                "HLAattributeList": ";".join(row["attributeList"] for row in rows).encode("ascii"),
                "HLAregisteredClass": ";".join(row["objectClass"] for row in rows).encode("ascii"),
                "HLAknownClass": ";".join(row["objectClass"] for row in rows).encode("ascii"),
                "HLAownedInstanceAttributeList": ";".join(
                    row["ownedInstanceAttributeList"] for row in rows
                ).encode("ascii"),
            },
        )

    def _queue_fom_module_data_report(self, parameters: datatypes_pb2.ParameterHandleValueMap) -> None:
        report_class = self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFOMmoduleData"]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        request_class = self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestFOMmoduleData"]
        requested_handle = "1"
        indicator = 0
        requested_federate_parameter = self.parameters[(request_class, "HLAfederate")]
        indicator_parameter = self.parameters[(request_class, "HLAFOMmoduleIndicator")]
        for item in parameters.parameterHandleValue:
            parameter_handle = item.parameterHandle.data.decode("ascii")
            if parameter_handle == requested_federate_parameter:
                requested_handle = item.value.decode("ascii")
            if parameter_handle == indicator_parameter:
                try:
                    indicator = int(item.value.decode("ascii") or "0")
                except ValueError:
                    indicator = 0
        module_data = self.fom_modules[indicator] if 0 <= indicator < len(self.fom_modules) else ""
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": requested_handle.encode("ascii"),
                "HLAFOMmoduleIndicator": str(indicator).encode("ascii"),
                "HLAFOMmoduleData": module_data.encode("ascii"),
            },
        )

    def _queue_federation_fom_module_data_report(self, parameters: datatypes_pb2.ParameterHandleValueMap) -> None:
        report_class = self.interactions["HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportFOMmoduleData"]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        request_class = self.interactions["HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestFOMmoduleData"]
        indicator = 0
        indicator_parameter = self.parameters[(request_class, "HLAFOMmoduleIndicator")]
        for item in parameters.parameterHandleValue:
            if item.parameterHandle.data.decode("ascii") == indicator_parameter:
                try:
                    indicator = int(item.value.decode("ascii") or "0")
                except ValueError:
                    indicator = 0
                break
        federation_name = self.mom_federation_name or next(iter(self.federations), "")
        payloads = self.federation_fom_payloads.get(federation_name, ())
        if payloads:
            module_data = "\n".join(payloads)
        else:
            module_data = ""
        self._queue_mom_report(
            report_class,
            {
                "HLAFOMmoduleIndicator": str(indicator).encode("ascii"),
                "HLAFOMmoduleData": module_data.encode("utf-8"),
            },
        )

    def _queue_mim_report(self) -> None:
        report_class = self.interactions["HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata"]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        self._queue_mom_report(
            report_class,
            {"HLAMIMdata": b"HLAstandardMIM-2025 HLAmanager HLArequestMIMdata HLAreportMIMdata"},
        )

    def _queue_synchronization_points_report(self) -> None:
        report_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPoints"
        ]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        labels = ",".join(sorted(self.synchronization_points))
        self._queue_mom_report(report_class, {"HLAsynchronizationPoints": labels.encode("ascii")})

    def _queue_synchronization_point_status_report(self, parameters: datatypes_pb2.ParameterHandleValueMap) -> None:
        report_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPointStatus"
        ]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        request_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPointStatus"
        ]
        label_parameter = self.parameters[(request_class, "HLAlabel")]
        requested_label = ""
        for item in parameters.parameterHandleValue:
            if item.parameterHandle.data.decode("ascii") == label_parameter:
                requested_label = item.value.decode("ascii")
                break
        labels = [requested_label] if requested_label else sorted(self.synchronization_points)
        status_rows = []
        federates: set[str] = set()
        for label in labels:
            point_federates = sorted(self._synchronization_point_federates(label), key=int)
            if not point_federates:
                status_rows.append(f"{label}:")
                continue
            achieved = self._synchronization_point_achieved(label)
            federates.update(point_federates)
            status_bits = ",".join(
                f"{handle}:achieved" if handle in achieved else f"{handle}:pending" for handle in point_federates
            )
            status_rows.append(f"{label}:{status_bits}")
        self._queue_mom_report(
            report_class,
            {
                "HLAlabel": ",".join(labels).encode("ascii"),
                "HLAfederateList": ",".join(sorted(federates, key=int)).encode("ascii"),
                "HLAfederateSynchronizationStatusList": ";".join(status_rows).encode("ascii"),
            },
        )

    def _queue_mom_report(self, report_class: str, parameter_values: dict[str, bytes]) -> None:
        target_handles = self._interaction_target_handles(report_class, ())
        if not target_handles:
            return
        values = datatypes_pb2.ParameterHandleValueMap()
        for parameter_name, payload in parameter_values.items():
            row = values.parameterHandleValue.add()
            row.parameterHandle.data = self.parameters[(report_class, parameter_name)].encode("ascii")
            row.value = payload
        self._enqueue_callback_per_handle(
            callback_pb2.CallbackRequest(
                receiveInteraction=callback_pb2.ReceiveInteraction(
                    interactionClass=_handle(datatypes_pb2.InteractionClassHandle, report_class),
                    parameterValues=values,
                    userSuppliedTag=b"MOM",
                    transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                    producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                )
            ),
            target_handles=target_handles,
        )

    def _exception_report_target_handles(self, report_class: str) -> set[str]:
        target_handles = self._interaction_target_handles(report_class, ())
        return {
            handle
            for handle in target_handles
            if self.handle_exception_reporting.get(handle, self.switch_states.get("exceptionReporting", True))
        }

    def _next_retraction_handle(self) -> str:
        handle = str(self.next_retraction_handle)
        self.next_retraction_handle += 1
        return handle

    @staticmethod
    def _message_retraction_return(handle: str) -> datatypes_pb2.MessageRetractionReturn:
        return datatypes_pb2.MessageRetractionReturn(
            retractionHandleIsValid=True,
            messageRetractionHandle=_handle(datatypes_pb2.MessageRetractionHandle, handle),
        )

    def _queue_tso_callback(
        self,
        retraction_handle: str,
        time: datatypes_pb2.LogicalTime,
        callback: callback_pb2.CallbackRequest,
        *,
        target_handles: set[str] | None = None,
    ) -> None:
        if target_handles is not None:
            target_handles = self._active_target_handles(target_handles)
            if not target_handles:
                return
        time_value = _logical_time_value(time)
        queued_time, callbacks = self.queued_tso_callbacks.setdefault(retraction_handle, (time_value, []))
        callbacks.append(callback)
        self.queued_tso_callbacks[retraction_handle] = (queued_time, callbacks)
        if target_handles is not None:
            self.callback_targets[id(callback)] = (None, frozenset(target_handles))
        self._process_time_advances()

    def _request_time_advance(self, handle: str, mode: str, time: datatypes_pb2.LogicalTime) -> None:
        if _logical_time_value(time) < _logical_time_value(self._handle_current_time(handle)):
            raise ValueError("requested time is earlier than current logical time")
        self.handle_pending_time_advance[handle] = (mode, datatypes_pb2.LogicalTime(data=time.data))
        self._process_time_advances()

    def _process_time_advances(self) -> None:
        progressed = True
        while progressed:
            progressed = False
            for handle in self._joined_handle_values():
                if self._try_grant_pending_time_advance(handle):
                    progressed = True
            self._process_scheduled_save()

    def _try_grant_pending_time_advance(self, handle: str) -> bool:
        request = self._handle_pending_request(handle)
        if request is None:
            return False
        mode, requested_time = request
        requested_value = _logical_time_value(requested_time)
        current_value = _logical_time_value(self._handle_current_time(handle))
        if requested_value < current_value:
            self.handle_pending_time_advance.pop(handle, None)
            return False

        queued = [
            (time_value, int(retraction_handle), retraction_handle)
            for retraction_handle, (time_value, callbacks) in self.queued_tso_callbacks.items()
            if any(
                (target_handles is None or handle in target_handles)
                for callback in callbacks
                for _peers, target_handles in [self.callback_targets.get(id(callback), (None, None))]
            )
        ]
        queued.sort()
        queued_through_requested = [row for row in queued if row[0] <= requested_value]
        queued_before_requested = [row for row in queued if row[0] < requested_value]

        grant_time: datatypes_pb2.LogicalTime | None = None
        deliver_through: datatypes_pb2.LogicalTime | None = None
        optimistic_time: datatypes_pb2.LogicalTime | None = None
        peer_galt_candidates = self._peer_regulating_lower_bounds(handle)
        galt_value = min(peer_galt_candidates) if peer_galt_candidates else None
        constrained = self.handle_time_constrained.get(handle, False)

        if mode == "flushQueueRequest":
            candidates = [requested_value]
            if queued_through_requested:
                candidates.append(queued_through_requested[0][0])
            if constrained and galt_value is not None:
                candidates.append(galt_value)
            grant_time = self._logical_time_from_value(min(candidates))
            deliver_through = grant_time
            optimistic_time = self._logical_time_from_value(min([requested_value, queued_through_requested[0][0]]) if queued_through_requested else requested_value)
        else:
            if mode in {"nextMessageRequest", "nextMessageRequestAvailable"} and queued_through_requested:
                grant_time = self._logical_time_from_value(queued_through_requested[0][0])
                deliver_through = grant_time
            else:
                allowed = True
                if constrained and galt_value is not None:
                    if mode in {"timeAdvanceRequest", "nextMessageRequest"}:
                        allowed = requested_value < galt_value
                    else:
                        allowed = requested_value <= galt_value
                if allowed:
                    grant_time = datatypes_pb2.LogicalTime(data=requested_time.data)
                    deliver_through = grant_time
                elif galt_value is not None:
                    if mode == "timeAdvanceRequestAvailable" and queued_through_requested and queued_through_requested[0][0] <= galt_value:
                        grant_time = self._logical_time_from_value(queued_through_requested[0][0])
                        deliver_through = grant_time
                    elif mode == "nextMessageRequest" and queued_before_requested and queued_before_requested[0][0] < galt_value:
                        grant_time = self._logical_time_from_value(queued_before_requested[0][0])
                        deliver_through = grant_time
                    elif mode == "nextMessageRequestAvailable" and queued_through_requested and queued_through_requested[0][0] <= galt_value:
                        grant_time = self._logical_time_from_value(queued_through_requested[0][0])
                        deliver_through = grant_time

        if grant_time is None or deliver_through is None:
            return False

        self.handle_pending_time_advance.pop(handle, None)
        self._grant_time(handle, grant_time, flush_queue=(mode == "flushQueueRequest"), optimistic_time=optimistic_time, delivery_time=deliver_through)
        return True

    def _deliver_due_tso_callbacks(self, handle: str, time: datatypes_pb2.LogicalTime) -> None:
        requested = _logical_time_value(time)
        due = [
            (time_value, int(handle), handle, callbacks)
            for handle, (time_value, callbacks) in self.queued_tso_callbacks.items()
            if time_value <= requested
        ]
        retained_tso_callbacks = dict(self.queued_tso_callbacks)
        for _, _, retraction_handle, callbacks in sorted(due):
            delivered_targets = set(self.delivered_retraction_targets.get(retraction_handle, frozenset()))
            remaining_callbacks: list[callback_pb2.CallbackRequest] = []
            delivered_any = False
            for callback in callbacks:
                _peers, target_handles = self.callback_targets.get(id(callback), (None, None))
                if target_handles is not None and handle not in target_handles:
                    remaining_callbacks.append(callback)
                    continue
                delivered_any = True
                if callback.WhichOneof("callbackRequest") == "reflectAttributeValuesWithTime":
                    self.reflections_received += 1
                    self.object_instances_reflected += 1
                self.callback_queue.append(callback)
                if target_handles is not None:
                    delivered_targets.add(handle)
                    remaining = frozenset(candidate for candidate in target_handles if candidate != handle)
                    if remaining:
                        self.callback_targets[id(callback)] = (_peers, remaining)
                        remaining_callbacks.append(callback)
                    else:
                        # Once a TSO callback becomes due for a specific handle,
                        # keep that handle-level routing on the shared callback
                        # queue until the peer actually evokes it.
                        self.callback_targets[id(callback)] = (
                            _peers,
                            frozenset({handle}),
                        )
                else:
                    self.callback_targets.pop(id(callback), None)
            if delivered_any:
                self.delivered_retraction_targets[retraction_handle] = frozenset(delivered_targets)
            if remaining_callbacks:
                retained_tso_callbacks[retraction_handle] = (self.queued_tso_callbacks[retraction_handle][0], remaining_callbacks)
            else:
                retained_tso_callbacks.pop(retraction_handle, None)
                if delivered_any:
                    self.delivered_retractions.add(retraction_handle)
        self.queued_tso_callbacks = retained_tso_callbacks

    def _grant_time(
        self,
        handle: str,
        time: datatypes_pb2.LogicalTime,
        *,
        flush_queue: bool = False,
        optimistic_time: datatypes_pb2.LogicalTime | None = None,
        delivery_time: datatypes_pb2.LogicalTime | None = None,
    ) -> None:
        self._deliver_due_tso_callbacks(handle, delivery_time or time)
        self.handle_current_times[handle] = datatypes_pb2.LogicalTime(data=time.data)
        self._sync_time_globals(handle)
        if flush_queue:
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    flushQueueGrant=callback_pb2.FlushQueueGrant(time=time, optimisticTime=optimistic_time or time)
                ),
                target_handles={handle},
            )
            return
        self._enqueue_callback(
            callback_pb2.CallbackRequest(timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=time)),
            target_handles={handle},
        )

    def _start_federation_save(self, label: str, time: datatypes_pb2.LogicalTime | None) -> None:
        self.save_label = label
        self.next_save_name = None
        self.next_save_time = None
        self.save_status = {handle: datatypes_pb2.FEDERATE_INSTRUCTED_TO_SAVE for handle in self._joined_handle_values()}
        for handle in self._joined_handle_values():
            if time is None:
                callback = callback_pb2.CallbackRequest(
                    initiateFederateSave=callback_pb2.InitiateFederateSave(label=label)
                )
            else:
                callback = callback_pb2.CallbackRequest(
                    initiateFederateSaveWithTime=callback_pb2.InitiateFederateSaveWithTime(
                        label=label,
                        time=time,
                    )
                )
            self._enqueue_callback(callback, target_handles={handle})

    def _process_scheduled_save(self) -> None:
        if self.next_save_name is None or self.next_save_time is None or self.save_label is not None:
            return
        save_value = _logical_time_value(self.next_save_time)
        for handle in self._joined_handle_values():
            if not self.handle_time_constrained.get(handle, False):
                continue
            if _logical_time_value(self._handle_current_time(handle)) < save_value:
                return
            for retraction_handle, (time_value, callbacks) in self.queued_tso_callbacks.items():
                if time_value > save_value:
                    continue
                if any(
                    (target_handles is None or handle in target_handles)
                    for callback in callbacks
                    for _peers, target_handles in [self.callback_targets.get(id(callback), (None, None))]
                ):
                    return
        self._start_federation_save(self.next_save_name, self.next_save_time)

    def _queue_request_retraction(self, handle: str) -> None:
        delivered_targets = set(self.delivered_retraction_targets.get(handle, frozenset()))
        if not delivered_targets:
            return
        callback = callback_pb2.CallbackRequest(
            requestRetraction=callback_pb2.RequestRetraction(
                retraction=_handle(datatypes_pb2.MessageRetractionHandle, handle)
            )
        )
        if len(delivered_targets) > 1:
            self._enqueue_callback_per_handle(callback, target_handles=delivered_targets)
        else:
            self._enqueue_callback(callback, target_handles=delivered_targets)

    def _synchronization_point_record(self, label: str) -> dict[str, bytes | bool | set[str]]:
        return self.synchronization_points.setdefault(
            label,
            {
                "tag": b"",
                "achieved": set(),
                "failed": set(),
                "federates": set(),
                "synchronized": False,
                "dynamic_members": False,
            },
        )

    def _synchronization_point_achieved(self, label: str) -> set[str]:
        achieved = self.synchronization_points.get(label, {}).get("achieved", set())
        return achieved if isinstance(achieved, set) else set()

    def _synchronization_point_failed(self, label: str) -> set[str]:
        failed = self.synchronization_points.get(label, {}).get("failed", set())
        return failed if isinstance(failed, set) else set()

    def _synchronization_point_federates(self, label: str) -> set[str]:
        federates = self.synchronization_points.get(label, {}).get("federates", set())
        return federates if isinstance(federates, set) else set()

    def _queue_federation_synchronized_if_ready(self, label: str) -> None:
        record = self._synchronization_point_record(label)
        synchronized = record.get("synchronized", False)
        if isinstance(synchronized, bool) and synchronized:
            return
        target_federates = self._synchronization_point_federates(label)
        completed = self._synchronization_point_achieved(label) | self._synchronization_point_failed(label)
        if not target_federates or not target_federates.issubset(completed):
            return
        record["synchronized"] = True
        failed_handles = sorted(self._synchronization_point_failed(label), key=int)
        failed_set = datatypes_pb2.FederateHandleSet(
            federateHandle=[_handle(datatypes_pb2.FederateHandle, handle) for handle in failed_handles]
        )
        self._enqueue_callback_per_handle(
            callback_pb2.CallbackRequest(
                federationSynchronized=callback_pb2.FederationSynchronized(
                    synchronizationPointLabel=label,
                    failedToSyncSet=failed_set,
                )
            ),
            target_handles=target_federates,
        )

    def _joined_handle_values(self) -> tuple[str, ...]:
        if self.joined_federate_handles:
            return tuple(sorted(self.joined_federate_handles, key=int))
        return ("1",)

    def _active_target_handles(self, target_handles: set[str]) -> set[str]:
        return {handle for handle in target_handles if handle in self.joined_federate_handles}

    def _remove_peer_federate(self, peer: str, *, preserve_owned_attributes: bool = False) -> None:
        handle = self.peer_federate_handles.get(peer)
        if handle is None:
            return
        self._remove_federate_handle(handle, peer=peer, preserve_owned_attributes=preserve_owned_attributes)

    def _remove_federate_handle(
        self,
        handle: str,
        *,
        peer: str | None = None,
        preserve_owned_attributes: bool = False,
    ) -> None:
        if peer is not None:
            self.peer_federate_handles.pop(peer, None)
        else:
            for candidate_peer, candidate_handle in tuple(self.peer_federate_handles.items()):
                if candidate_handle == handle:
                    self.peer_federate_handles.pop(candidate_peer, None)
        mom_object_handle = self.mom_federate_object_handles.pop(handle, None)
        if mom_object_handle is not None:
            mom_record = self._remove_object_instance(mom_object_handle)
            if mom_record is not None:
                remove_targets = self._discovery_target_handles(mom_record["objectClass"], exclude_handle=handle)
                if remove_targets:
                    callback = callback_pb2.CallbackRequest(
                        removeObjectInstance=callback_pb2.RemoveObjectInstance(
                            objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, mom_object_handle),
                            userSuppliedTag=b"resign",
                            producingFederate=_handle(datatypes_pb2.FederateHandle, handle),
                        )
                    )
                    if len(remove_targets) > 1:
                        self._enqueue_callback_per_handle(callback, target_handles=remove_targets)
                    else:
                        self._enqueue_callback(callback, target_handles=remove_targets)
        name = self.joined_federate_handles.pop(handle, None)
        if name is not None:
            self.joined_federates.pop(name, None)
        self.joined_federate_types.pop(handle, None)
        self.handle_service_reporting.pop(handle, None)
        self.handle_exception_reporting.pop(handle, None)
        self.handle_published_object_attributes.pop(handle, None)
        self.handle_published_interactions.pop(handle, None)
        self.handle_published_directed_interactions.pop(handle, None)
        self.handle_current_times.pop(handle, None)
        self.handle_lookahead.pop(handle, None)
        self.handle_time_regulating.pop(handle, None)
        self.handle_time_constrained.pop(handle, None)
        self.handle_asynchronous_delivery_enabled.pop(handle, None)
        self.handle_pending_time_advance.pop(handle, None)
        self.handle_updates_sent.pop(handle, None)
        self.handle_reflections_received.pop(handle, None)
        self.handle_interactions_sent.pop(handle, None)
        self.handle_interactions_received.pop(handle, None)
        self.handle_object_instances_updated.pop(handle, None)
        self.handle_object_instances_reflected.pop(handle, None)
        self.save_status.pop(handle, None)
        self.restore_status.pop(handle, None)
        for record in self.synchronization_points.values():
            achieved = record.get("achieved")
            if isinstance(achieved, set):
                achieved.discard(handle)
            federates = record.get("federates")
            if isinstance(federates, set):
                federates.discard(handle)
        self._recompute_service_reporting()
        self._recompute_exception_reporting()
        self.handle_subscribed_object_attributes.pop(handle, None)
        self.handle_subscribed_object_regions.pop(handle, None)
        self.handle_subscribed_interactions.pop(handle, None)
        self.handle_subscribed_interaction_regions.pop(handle, None)
        self.handle_subscribed_directed_interactions.pop(handle, None)
        self.handle_locally_deleted_objects.pop(handle, None)
        if preserve_owned_attributes:
            owner_keys = {key for key, owner_handle in self.attribute_owners.items() if owner_handle == handle}
            self.offered_attributes.difference_update(owner_keys)
        for key, owner_handle in tuple(self.attribute_owners.items()):
            if owner_handle != handle:
                continue
            if preserve_owned_attributes:
                self.offered_attributes.discard(key)
                continue
            self.unowned_attributes.add(key)
            self.offered_attributes.discard(key)
            self.attribute_owners.pop(key, None)
        removed_pending_keys = {
            key for key, requester_handle in self.pending_attribute_requesters.items() if requester_handle == handle
        }
        self.pending_attribute_requesters = {
            key: requester_handle
            for key, requester_handle in self.pending_attribute_requesters.items()
            if requester_handle != handle
        }
        self.pending_attribute_acquisitions = {
            key: tag for key, tag in self.pending_attribute_acquisitions.items() if key not in removed_pending_keys
        }
        retained_callbacks: list[callback_pb2.CallbackRequest] = []
        retained_targets: dict[int, tuple[frozenset[str] | None, frozenset[str] | None]] = {}
        for callback in self.callback_queue:
            target_peers, target_handles = self.callback_targets.get(id(callback), (None, None))
            if target_handles is not None and handle in target_handles:
                remaining = frozenset(candidate for candidate in target_handles if candidate != handle)
                if not remaining:
                    self.callback_targets.pop(id(callback), None)
                    continue
                target_handles = remaining
            retained_callbacks.append(callback)
            retained_targets[id(callback)] = (target_peers, target_handles)
        self.callback_queue = retained_callbacks
        retained_tso_callbacks: dict[str, tuple[float, list[callback_pb2.CallbackRequest]]] = {}
        for retraction_handle, (time_value, callbacks) in self.queued_tso_callbacks.items():
            remaining_callbacks: list[callback_pb2.CallbackRequest] = []
            for callback in callbacks:
                target_peers, target_handles = self.callback_targets.get(id(callback), (None, None))
                if target_handles is not None and handle in target_handles:
                    remaining = frozenset(candidate for candidate in target_handles if candidate != handle)
                    if not remaining:
                        self.callback_targets.pop(id(callback), None)
                        continue
                    target_handles = remaining
                remaining_callbacks.append(callback)
                retained_targets[id(callback)] = (target_peers, target_handles)
            if remaining_callbacks:
                retained_tso_callbacks[retraction_handle] = (time_value, remaining_callbacks)
        self.callback_targets = retained_targets
        self.queued_tso_callbacks = retained_tso_callbacks
        retained_delivered_retraction_targets: dict[str, frozenset[str]] = {}
        for retraction_handle, delivered_targets in self.delivered_retraction_targets.items():
            remaining = frozenset(candidate for candidate in delivered_targets if candidate != handle)
            if remaining:
                retained_delivered_retraction_targets[retraction_handle] = remaining
        self.delivered_retraction_targets = retained_delivered_retraction_targets
        self._rebuild_published_object_aggregates()
        self._rebuild_published_interaction_aggregates()
        self._rebuild_published_directed_interactions()
        self._rebuild_subscribed_object_aggregates()
        self._rebuild_subscribed_interaction_aggregates()
        self._rebuild_subscribed_directed_interactions()
        remaining = self._joined_handle_values()
        if remaining:
            self._sync_time_globals(remaining[0])

    @staticmethod
    def _context_peer(context) -> str:
        if context is None:
            return "__direct__"
        try:
            for item in context.invocation_metadata():
                if item.key == "x-hla-session-id" and item.value:
                    return item.value
        except AttributeError:
            pass
        try:
            return context.peer()
        except AttributeError:
            return "__direct__"

    def _enqueue_callback(
        self,
        callback: callback_pb2.CallbackRequest,
        *,
        target_peers: set[str] | None = None,
        target_handles: set[str] | None = None,
    ) -> None:
        if target_handles is not None:
            target_handles = self._active_target_handles(target_handles)
            if not target_handles:
                return
        self.callback_queue.append(callback)
        self.callback_targets[id(callback)] = (
            None if target_peers is None else frozenset(target_peers),
            None if target_handles is None else frozenset(target_handles),
        )

    def _enqueue_callback_per_handle(
        self,
        callback: callback_pb2.CallbackRequest,
        *,
        target_handles: set[str],
    ) -> None:
        for handle in sorted(target_handles, key=int):
            clone = callback_pb2.CallbackRequest()
            clone.CopyFrom(callback)
            self._enqueue_callback(clone, target_handles={handle})

    def _pop_callback_for_peer(self, peer: str):
        handle = self.peer_federate_handles.get(peer)
        for index, callback in enumerate(self.callback_queue):
            target_peers, target_handles = self.callback_targets.get(id(callback), (None, None))
            if target_peers is not None and peer not in target_peers:
                continue
            if target_handles is not None and handle not in target_handles:
                continue
            self.callback_queue.pop(index)
            self.callback_targets.pop(id(callback), None)
            return callback
        return _callback_request()

    def _current_federate_handle(self, peer: str | None = None) -> str:
        if peer is not None and peer in self.peer_federate_handles:
            return self.peer_federate_handles[peer]
        return self._joined_handle_values()[0]

    def _handle_current_time(self, handle: str) -> datatypes_pb2.LogicalTime:
        return self.handle_current_times.setdefault(handle, datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:0"))

    def _handle_lookahead(self, handle: str) -> datatypes_pb2.LogicalTimeInterval:
        return self.handle_lookahead.setdefault(handle, datatypes_pb2.LogicalTimeInterval(data=b"HLAinteger64Interval:1"))

    def _attribute_transportation(self, object_instance: str, object_class: str, attribute: str) -> str:
        return self.default_attribute_transportation.get(
            (object_instance, attribute),
            self.default_attribute_transportation.get((object_class, attribute), "1"),
        )

    @staticmethod
    def _update_rate_hz(designator: str) -> float:
        normalized = designator.strip().lower()
        if normalized in {"", "hladefault", "hladefaultupdaterate", "default"}:
            return 0.0
        if normalized == "fast":
            return 2.0
        return 0.0

    def _update_rate_allows_delivery(
        self,
        handle: str,
        object_class: str,
        attribute: str,
        timestamp: float,
    ) -> bool:
        designator = self.handle_subscribed_object_update_rates.get(handle, {}).get((object_class, attribute), "")
        rate_hz = self._update_rate_hz(designator)
        if rate_hz <= 0.0:
            return True
        key = (object_class, attribute)
        last_delivered = self.handle_last_update_rate_delivery_time.setdefault(handle, {}).get(key)
        minimum_interval = 1.0 / rate_hz
        if last_delivered is not None and (timestamp - last_delivered) < minimum_interval:
            return False
        self.handle_last_update_rate_delivery_time[handle][key] = timestamp
        return True

    def _reflected_transportation_type(
        self,
        object_instance: str,
        object_class: str,
        reflected_items: list[datatypes_pb2.AttributeHandleValuePair],
    ):
        if not reflected_items:
            return _handle(datatypes_pb2.TransportationTypeHandle, "1")
        transportations = {
            self._attribute_transportation(
                object_instance,
                object_class,
                item.attributeHandle.data.decode("ascii"),
            )
            for item in reflected_items
        }
        transportation = sorted(transportations)[0] if len(transportations) == 1 else "1"
        return _handle(datatypes_pb2.TransportationTypeHandle, transportation)

    def _partition_reflected_items_by_transport(
        self,
        object_instance: str,
        object_class: str,
        reflected_items: list[datatypes_pb2.AttributeHandleValuePair],
    ) -> list[tuple[str, list[datatypes_pb2.AttributeHandleValuePair]]]:
        grouped: dict[str, list[datatypes_pb2.AttributeHandleValuePair]] = {}
        order: list[str] = []
        for item in reflected_items:
            transportation = self._attribute_transportation(
                object_instance,
                object_class,
                item.attributeHandle.data.decode("ascii"),
            )
            if transportation not in grouped:
                grouped[transportation] = []
                order.append(transportation)
            grouped[transportation].append(item)
        return [(transportation, grouped[transportation]) for transportation in order]

    def _interaction_transportation_type(self, interaction_class: str):
        transportation = (
            self.interaction_transportation[1]
            if self.interaction_transportation is not None and self.interaction_transportation[0] == interaction_class
            else "1"
        )
        return _handle(datatypes_pb2.TransportationTypeHandle, transportation)

    def _set_handle_lookahead(self, handle: str, lookahead: datatypes_pb2.LogicalTimeInterval) -> None:
        self.handle_lookahead[handle] = datatypes_pb2.LogicalTimeInterval(data=lookahead.data)
        self._sync_time_globals(handle)

    def _sync_time_globals(self, handle: str) -> None:
        self.current_time.CopyFrom(self._handle_current_time(handle))
        self.lookahead.CopyFrom(self._handle_lookahead(handle))
        self.time_regulating = self.handle_time_regulating.get(handle, False)
        self.time_constrained = self.handle_time_constrained.get(handle, False)
        self.asynchronous_delivery_enabled = self.handle_asynchronous_delivery_enabled.get(handle, False)

    @staticmethod
    def _logical_time_from_value(value: float) -> datatypes_pb2.LogicalTime:
        if float(value).is_integer():
            rendered = str(int(value))
        else:
            rendered = f"{value:g}"
        return datatypes_pb2.LogicalTime(data=f"HLAinteger64Time:{rendered}".encode("ascii"))

    def _handle_pending_request(self, handle: str) -> tuple[str, datatypes_pb2.LogicalTime] | None:
        return self.handle_pending_time_advance.get(handle)

    def _peer_regulating_lower_bounds(self, handle: str) -> list[float]:
        return [
            lower_bound
            for other_handle in self._joined_handle_values()
            if other_handle != handle
            for lower_bound in [self._regulating_lower_bound(other_handle)]
            if lower_bound is not None
        ]

    def _regulating_lower_bound(self, handle: str) -> float | None:
        if not self.handle_time_regulating.get(handle, False):
            return None
        request = self._handle_pending_request(handle)
        base = request[1] if request is not None else self._handle_current_time(handle)
        return _logical_time_value(base) + _logical_interval_value(self._handle_lookahead(handle))

    def _query_galt(self, handle: str) -> datatypes_pb2.TimeQueryReturn:
        candidates = self._peer_regulating_lower_bounds(handle)
        if not candidates:
            return datatypes_pb2.TimeQueryReturn(
                logicalTimeIsValid=True,
                logicalTime=datatypes_pb2.LogicalTime(data=self._handle_current_time(handle).data),
            )
        value = min(candidates)
        return datatypes_pb2.TimeQueryReturn(
            logicalTimeIsValid=True,
            logicalTime=self._logical_time_from_value(value),
        )

    def _query_lits(self, handle: str) -> datatypes_pb2.TimeQueryReturn:
        candidates: list[float] = []
        galt = self._query_galt(handle)
        if galt.logicalTimeIsValid:
            candidates.append(_logical_time_value(galt.logicalTime))
        for time_value, callbacks in self.queued_tso_callbacks.values():
            for callback in callbacks:
                _peers, target_handles = self.callback_targets.get(id(callback), (None, None))
                if target_handles is None or handle in target_handles:
                    candidates.append(time_value)
                    break
        if not candidates:
            return datatypes_pb2.TimeQueryReturn(logicalTimeIsValid=False)
        value = min(candidates)
        return datatypes_pb2.TimeQueryReturn(
            logicalTimeIsValid=True,
            logicalTime=self._logical_time_from_value(value),
        )

    def _validate_tso_send_time(self, handle: str, time: datatypes_pb2.LogicalTime) -> bool:
        if not self.handle_time_regulating.get(handle, False):
            return False
        timestamp = _logical_time_value(time)
        for other_handle in self._joined_handle_values():
            if other_handle == handle or not self.handle_time_constrained.get(other_handle, False):
                continue
            if _logical_time_value(self._handle_current_time(other_handle)) > timestamp:
                return False
        return True

    def _apply_resign_action(self, action: int) -> None:
        if action in {
            datatypes_pb2.UNCONDITIONALLY_DIVEST_ATTRIBUTES,
            datatypes_pb2.DELETE_OBJECTS_THEN_DIVEST,
            datatypes_pb2.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            for object_instance, record in self.object_instances.items():
                attributes = {
                    attribute
                    for (object_class, _name), attribute in self.attributes.items()
                    if object_class == record["objectClass"]
                }
                for attribute in attributes:
                    key = (object_instance, attribute)
                    self.unowned_attributes.add(key)
                    self.attribute_owners.pop(key, None)
        if action in {
            datatypes_pb2.DELETE_OBJECTS,
            datatypes_pb2.DELETE_OBJECTS_THEN_DIVEST,
            datatypes_pb2.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            self.object_instances.clear()
            self.object_update_regions.clear()
            self.attribute_owners.clear()
            self.unowned_attributes.clear()
            self.offered_attributes.clear()
        if action in {
            datatypes_pb2.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS,
            datatypes_pb2.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            self.pending_attribute_acquisitions.clear()
            self.pending_attribute_requesters.clear()

    def _cancel_pending_acquisitions_for_handle(self, handle: str) -> None:
        removed_keys = {
            key for key, requester_handle in self.pending_attribute_requesters.items() if requester_handle == handle
        }
        self.pending_attribute_requesters = {
            key: requester_handle
            for key, requester_handle in self.pending_attribute_requesters.items()
            if requester_handle != handle
        }
        self.pending_attribute_acquisitions = {
            key: tag for key, tag in self.pending_attribute_acquisitions.items() if key not in removed_keys
        }

    def _delete_objects_owned_by_handle(self, handle: str, *, user_supplied_tag: bytes) -> None:
        owned_instances = [
            object_instance
            for object_instance in tuple(self.object_instances)
            if any(
                owner_handle == handle and owned_instance == object_instance
                for (owned_instance, _attribute), owner_handle in self.attribute_owners.items()
            )
        ]
        for object_instance in owned_instances:
            record = self._remove_object_instance(object_instance)
            if record is None:
                continue
            remove_targets = self._discovery_target_handles(record["objectClass"], exclude_handle=handle)
            if not remove_targets:
                continue
            callback = callback_pb2.CallbackRequest(
                removeObjectInstance=callback_pb2.RemoveObjectInstance(
                    objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                    userSuppliedTag=user_supplied_tag,
                    producingFederate=_handle(datatypes_pb2.FederateHandle, handle),
                )
            )
            if len(remove_targets) > 1:
                self._enqueue_callback_per_handle(callback, target_handles=remove_targets)
            else:
                self._enqueue_callback(callback, target_handles=remove_targets)

    def _divest_attributes_owned_by_handle(self, handle: str) -> None:
        for key, owner_handle in tuple(self.attribute_owners.items()):
            if owner_handle != handle:
                continue
            self.unowned_attributes.add(key)
            self.offered_attributes.discard(key)
            self.attribute_owners.pop(key, None)

    def force_federate_loss(self, federate_handle: str, fault_description: str = "simulated federate fault") -> None:
        handle = str(federate_handle)
        lost_name = self.joined_federate_handles.get(handle)
        if lost_name is None:
            raise KeyError(f"Unknown federate handle {handle!r}")
        peer = next(
            (candidate_peer for candidate_peer, candidate_handle in self.peer_federate_handles.items() if candidate_handle == handle),
            None,
        )
        if peer is not None:
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    connectionLost=callback_pb2.ConnectionLost(faultDescription=fault_description)
                ),
                target_peers={peer},
            )

        report_name = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFederateLost"
        report_class = self.interactions.get(report_name)
        if report_class is not None:
            handle_module = import_module("hla.rti1516e.handles")
            mom_module = import_module("hla.fom.mom")
            time_module = import_module("hla.rti1516e.time")
            encoded_handle = handle_module.FederateHandle(int(handle)).encode()
            raw_time = self._handle_current_time(handle).data.decode("ascii")
            time_kind, time_value = raw_time.split(":", 1)
            if time_kind == "HLAfloat64Time":
                encoded_time = time_module.HLAfloat64Time(float(time_value)).encode()
            else:
                encoded_time = time_module.HLAinteger64Time(int(float(time_value))).encode()
            self._queue_mom_report(
                report_class,
                {
                    "HLAfederate": encoded_handle,
                    "HLAfederateName": mom_module.encode_text(lost_name),
                    "HLAtimeStamp": encoded_time,
                    "HLAfaultDescription": mom_module.encode_text(fault_description),
                },
            )

        action = self.automatic_resign_directive
        if action in {
            datatypes_pb2.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS,
            datatypes_pb2.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            self._cancel_pending_acquisitions_for_handle(handle)
        if action in {
            datatypes_pb2.DELETE_OBJECTS,
            datatypes_pb2.DELETE_OBJECTS_THEN_DIVEST,
            datatypes_pb2.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            self._delete_objects_owned_by_handle(handle, user_supplied_tag=b"lost")
        if action in {
            datatypes_pb2.UNCONDITIONALLY_DIVEST_ATTRIBUTES,
            datatypes_pb2.DELETE_OBJECTS_THEN_DIVEST,
            datatypes_pb2.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            self._divest_attributes_owned_by_handle(handle)

        if peer is not None:
            self.peer_callback_delivery_enabled.pop(peer, None)
        self._remove_federate_handle(handle, peer=peer, preserve_owned_attributes=False)

    def _snapshot(self) -> _FederationSnapshot:
        retained_queued_tso_callbacks = {
            retraction_handle: (
                time_value,
                [
                    callback
                    for callback in callbacks
                    if callback.WhichOneof("callbackRequest") != "receiveDirectedInteractionWithTime"
                ],
            )
            for retraction_handle, (time_value, callbacks) in self.queued_tso_callbacks.items()
        }
        retained_queued_tso_callbacks = {
            retraction_handle: (time_value, callbacks)
            for retraction_handle, (time_value, callbacks) in retained_queued_tso_callbacks.items()
            if callbacks
        }
        queued_tso_target_handles = {
            retraction_handle: [
                self.callback_targets.get(id(callback), (None, None))[1]
                for callback in callbacks
            ]
            for retraction_handle, (_time_value, callbacks) in retained_queued_tso_callbacks.items()
        }
        retained_retraction_handles = {
            int(handle)
            for handle in (
                set(retained_queued_tso_callbacks)
                | set(self.delivered_retractions)
                | set(self.requested_retractions)
                | set(self.delivered_retraction_targets)
            )
            if handle.isdigit()
        }
        next_retraction_handle = max(retained_retraction_handles, default=0) + 1
        return _FederationSnapshot(
            object_instances=deepcopy(self.object_instances),
            reserved_object_instance_names=dict(self.reserved_object_instance_names),
            attribute_owners=dict(self.attribute_owners),
            unowned_attributes=set(self.unowned_attributes),
            offered_attributes=set(self.offered_attributes),
            pending_attribute_acquisitions=dict(self.pending_attribute_acquisitions),
            pending_attribute_requesters=dict(self.pending_attribute_requesters),
            current_time=datatypes_pb2.LogicalTime(data=self.current_time.data),
            next_object_instance_handle=self.next_object_instance_handle,
            lookahead=datatypes_pb2.LogicalTimeInterval(data=self.lookahead.data),
            handle_current_times={handle: datatypes_pb2.LogicalTime(data=time.data) for handle, time in self.handle_current_times.items()},
            handle_lookahead={handle: datatypes_pb2.LogicalTimeInterval(data=interval.data) for handle, interval in self.handle_lookahead.items()},
            object_update_regions=deepcopy(self.object_update_regions),
            regions=deepcopy(self.regions),
            region_bounds=deepcopy(self.region_bounds),
            published_object_attributes=deepcopy(self.published_object_attributes),
            handle_published_object_attributes=deepcopy(self.handle_published_object_attributes),
            handle_subscribed_object_attributes=deepcopy(self.handle_subscribed_object_attributes),
            handle_subscribed_object_regions=deepcopy(self.handle_subscribed_object_regions),
            published_interactions=set(self.published_interactions),
            handle_published_interactions=deepcopy(self.handle_published_interactions),
            default_attribute_transportation=dict(self.default_attribute_transportation),
            default_attribute_order=dict(self.default_attribute_order),
            interaction_transportation=self.interaction_transportation,
            interaction_order=getattr(self, "interaction_order", None),
            switch_states=dict(self.switch_states),
            service_reporting=self.service_reporting,
            handle_service_reporting=dict(self.handle_service_reporting),
            handle_exception_reporting=dict(self.handle_exception_reporting),
            automatic_resign_directive=self.automatic_resign_directive,
            time_regulating=self.time_regulating,
            time_constrained=self.time_constrained,
            asynchronous_delivery_enabled=self.asynchronous_delivery_enabled,
            handle_time_regulating=dict(self.handle_time_regulating),
            handle_time_constrained=dict(self.handle_time_constrained),
            handle_asynchronous_delivery_enabled=dict(self.handle_asynchronous_delivery_enabled),
            handle_pending_time_advance={
                handle: (mode, datatypes_pb2.LogicalTime(data=time.data))
                for handle, (mode, time) in self.handle_pending_time_advance.items()
            },
            callback_delivery_enabled=self.callback_delivery_enabled,
            peer_callback_delivery_enabled=dict(self.peer_callback_delivery_enabled),
            handle_locally_deleted_objects=deepcopy(self.handle_locally_deleted_objects),
            directed_interaction_region_gates=set(self.directed_interaction_region_gates),
            published_directed_interactions=deepcopy(self.published_directed_interactions),
            handle_published_directed_interactions=deepcopy(self.handle_published_directed_interactions),
            handle_subscribed_directed_interactions=deepcopy(self.handle_subscribed_directed_interactions),
            handle_subscribed_interactions=deepcopy(self.handle_subscribed_interactions),
            handle_subscribed_interaction_regions=deepcopy(self.handle_subscribed_interaction_regions),
            queued_tso_callbacks=deepcopy(retained_queued_tso_callbacks),
            queued_tso_target_handles=deepcopy(queued_tso_target_handles),
            delivered_retractions=set(self.delivered_retractions),
            delivered_retraction_targets=dict(self.delivered_retraction_targets),
            requested_retractions=set(self.requested_retractions),
            next_retraction_handle=next_retraction_handle,
        )

    def _restore_snapshot(self, label: str | None) -> None:
        if label is None:
            return
        snapshot = self.saved_snapshots.get(label)
        if snapshot is None:
            return
        self.object_instances = deepcopy(snapshot.object_instances)
        self.reserved_object_instance_names = dict(snapshot.reserved_object_instance_names)
        self.attribute_owners = dict(snapshot.attribute_owners)
        self.unowned_attributes = set(snapshot.unowned_attributes)
        self.offered_attributes = set(snapshot.offered_attributes)
        self.pending_attribute_acquisitions = dict(snapshot.pending_attribute_acquisitions)
        self.pending_attribute_requesters = dict(snapshot.pending_attribute_requesters)
        self.current_time.CopyFrom(snapshot.current_time)
        self.next_object_instance_handle = snapshot.next_object_instance_handle
        self.lookahead.CopyFrom(snapshot.lookahead)
        self.handle_current_times = {handle: datatypes_pb2.LogicalTime(data=time.data) for handle, time in snapshot.handle_current_times.items()}
        self.handle_lookahead = {handle: datatypes_pb2.LogicalTimeInterval(data=interval.data) for handle, interval in snapshot.handle_lookahead.items()}
        self.object_update_regions = deepcopy(snapshot.object_update_regions)
        self.regions = deepcopy(snapshot.regions)
        self.region_bounds = deepcopy(snapshot.region_bounds)
        self.published_object_attributes = deepcopy(snapshot.published_object_attributes)
        self.handle_published_object_attributes = deepcopy(snapshot.handle_published_object_attributes)
        self.handle_subscribed_object_attributes = deepcopy(snapshot.handle_subscribed_object_attributes)
        self.handle_subscribed_object_regions = deepcopy(snapshot.handle_subscribed_object_regions)
        self.published_interactions = set(snapshot.published_interactions)
        self.handle_published_interactions = deepcopy(snapshot.handle_published_interactions)
        self.default_attribute_transportation = dict(snapshot.default_attribute_transportation)
        self.default_attribute_order = dict(snapshot.default_attribute_order)
        self.interaction_transportation = snapshot.interaction_transportation
        self.interaction_order = snapshot.interaction_order
        self.switch_states = dict(snapshot.switch_states)
        self.service_reporting = snapshot.service_reporting
        self.handle_service_reporting = dict(snapshot.handle_service_reporting)
        self.handle_exception_reporting = dict(snapshot.handle_exception_reporting)
        self.automatic_resign_directive = snapshot.automatic_resign_directive
        self.time_regulating = snapshot.time_regulating
        self.time_constrained = snapshot.time_constrained
        self.asynchronous_delivery_enabled = snapshot.asynchronous_delivery_enabled
        self.handle_time_regulating = dict(snapshot.handle_time_regulating)
        self.handle_time_constrained = dict(snapshot.handle_time_constrained)
        self.handle_asynchronous_delivery_enabled = dict(snapshot.handle_asynchronous_delivery_enabled)
        self.handle_pending_time_advance = {
            handle: (mode, datatypes_pb2.LogicalTime(data=time.data))
            for handle, (mode, time) in snapshot.handle_pending_time_advance.items()
        }
        # Callback enablement is a live per-peer runtime policy, not restored state.
        self.handle_locally_deleted_objects = deepcopy(snapshot.handle_locally_deleted_objects)
        self.directed_interaction_region_gates = set(snapshot.directed_interaction_region_gates)
        self.published_directed_interactions = deepcopy(snapshot.published_directed_interactions)
        self.handle_published_directed_interactions = deepcopy(snapshot.handle_published_directed_interactions)
        self.handle_subscribed_directed_interactions = deepcopy(snapshot.handle_subscribed_directed_interactions)
        self.handle_subscribed_interactions = deepcopy(snapshot.handle_subscribed_interactions)
        self.handle_subscribed_interaction_regions = deepcopy(snapshot.handle_subscribed_interaction_regions)
        self.queued_tso_callbacks = deepcopy(snapshot.queued_tso_callbacks)
        self.delivered_retractions = set(snapshot.delivered_retractions)
        self.delivered_retraction_targets = dict(snapshot.delivered_retraction_targets)
        self.requested_retractions = set(snapshot.requested_retractions)
        self.next_retraction_handle = snapshot.next_retraction_handle
        self._rebuild_published_object_aggregates()
        self._rebuild_published_interaction_aggregates()
        self._rebuild_published_directed_interactions()
        self._rebuild_subscribed_object_aggregates()
        self._rebuild_subscribed_interaction_aggregates()
        self._rebuild_subscribed_directed_interactions()
        self.callback_targets.clear()
        for retraction_handle, (_time_value, callbacks) in self.queued_tso_callbacks.items():
            saved_targets = snapshot.queued_tso_target_handles.get(retraction_handle, [])
            for index, callback in enumerate(callbacks):
                target_handles = saved_targets[index] if index < len(saved_targets) else None
                if target_handles is not None:
                    self.callback_targets[id(callback)] = (None, frozenset(target_handles))
        remaining = self._joined_handle_values()
        if remaining:
            self._sync_time_globals(remaining[0])
        self.callback_queue.clear()
        self.attribute_scope_state.clear()

    def _save_status_array(self) -> datatypes_pb2.FederateHandleSaveStatusPairArray:
        result = datatypes_pb2.FederateHandleSaveStatusPairArray()
        statuses = self.save_status or {handle: datatypes_pb2.NO_SAVE_IN_PROGRESS for handle in self._joined_handle_values()}
        for handle, status in sorted(statuses.items(), key=lambda item: int(item[0])):
            row = result.federateHandleSaveStatusPair.add()
            row.federateHandle.CopyFrom(_handle(datatypes_pb2.FederateHandle, handle))
            row.saveStatus = status
        return result

    def _restore_status_array(self) -> datatypes_pb2.FederateRestoreStatusArray:
        result = datatypes_pb2.FederateRestoreStatusArray()
        statuses = self.restore_status or {handle: datatypes_pb2.NO_RESTORE_IN_PROGRESS for handle in self._joined_handle_values()}
        for handle, status in sorted(statuses.items(), key=lambda item: int(item[0])):
            row = result.federateRestoreStatus.add()
            row.preRestoreHandle.CopyFrom(_handle(datatypes_pb2.FederateHandle, handle))
            row.postRestoreHandle.CopyFrom(_handle(datatypes_pb2.FederateHandle, handle))
            row.restoreStatus = status
        return result

    @staticmethod
    def _attribute_region_pairs(attributes_and_regions) -> tuple[tuple[str, set[str]], ...]:
        pairs: list[tuple[str, set[str]]] = []
        for pair in attributes_and_regions.AttributeSetRegionSetPair:
            regions = {region.data.decode("ascii") for region in pair.regionSet.regionHandle}
            for attribute in pair.attributeSet.attributeHandle:
                pairs.append((attribute.data.decode("ascii"), set(regions)))
        return tuple(pairs)

    @staticmethod
    def _ranges_overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
        return left[0] <= right[1] and right[0] <= left[1]

    def _regions_overlap(self, source_region: str, target_region: str) -> bool:
        common = self.regions.get(source_region, set()) & self.regions.get(target_region, set())
        if not common:
            return False
        for dimension in common:
            source_bounds = self.region_bounds.get(source_region, {}).get(dimension, (0, 1024))
            target_bounds = self.region_bounds.get(target_region, {}).get(dimension, (0, 1024))
            if not self._ranges_overlap(source_bounds, target_bounds):
                return False
        return True

    def _attribute_regions_overlap(self, object_instance: str, object_class: str, attribute: str) -> bool:
        target_regions = self.subscribed_object_regions.get(object_class, {}).get(attribute, set())
        if not target_regions:
            return attribute in self.subscribed_object_attributes.get(object_class, set())
        source_regions = self.object_update_regions.get(object_instance, {}).get(attribute, set())
        if not source_regions:
            return False
        return any(self._regions_overlap(source_region, target_region) for source_region in source_regions for target_region in target_regions)

    def _attribute_regions_overlap_for_handle(self, handle: str, object_instance: str, object_class: str, attribute: str) -> bool:
        target_regions = self.handle_subscribed_object_regions.get(handle, {}).get(object_class, {}).get(attribute, set())
        if not target_regions:
            return attribute in self.handle_subscribed_object_attributes.get(handle, {}).get(object_class, set())
        source_regions = self.object_update_regions.get(object_instance, {}).get(attribute, set())
        if not source_regions:
            return False
        return any(self._regions_overlap(source_region, target_region) for source_region in source_regions for target_region in target_regions)

    def _reflection_target_handles(self, object_instance: str, object_class: str, attributes: tuple[str, ...]) -> dict[str, list[str]]:
        targets: dict[str, list[str]] = {}
        for handle, object_class_map in self.handle_subscribed_object_attributes.items():
            subscribed_attributes = object_class_map.get(object_class, set())
            if not subscribed_attributes:
                continue
            for attribute in attributes:
                if attribute not in subscribed_attributes:
                    continue
                if self._attribute_regions_overlap_for_handle(handle, object_instance, object_class, attribute):
                    targets.setdefault(handle, []).append(attribute)
        return targets

    def _interaction_subscriber_matches(self, interaction_class: str, source_regions: tuple[str, ...]) -> bool:
        return any(
            self._interaction_subscriber_matches_for_handle(handle, interaction_class, source_regions)
            for handle in self.handle_subscribed_interactions
        )

    def _interaction_subscriber_matches_for_handle(self, handle: str, interaction_class: str, source_regions: tuple[str, ...]) -> bool:
        if interaction_class not in self.handle_subscribed_interactions.get(handle, set()):
            return False
        target_regions = self.handle_subscribed_interaction_regions.get(handle, {}).get(interaction_class, set())
        if not target_regions:
            return True
        if not source_regions:
            return False
        return any(self._regions_overlap(source_region, target_region) for source_region in source_regions for target_region in target_regions)

    def _interaction_target_handles(self, interaction_class: str, source_regions: tuple[str, ...]) -> set[str]:
        return {
            handle
            for handle in self.handle_subscribed_interactions
            if self._interaction_subscriber_matches_for_handle(handle, interaction_class, source_regions)
        }

    def _directed_interaction_target_handles(self, object_instance: str, object_class: str, interaction_class: str) -> set[str]:
        source_regions = self._object_instance_region_values(object_instance)
        targets: set[str] = set()
        for handle, object_class_map in self.handle_subscribed_directed_interactions.items():
            if interaction_class not in object_class_map.get(object_class, set()):
                continue
            if interaction_class not in self.directed_interaction_region_gates:
                targets.add(handle)
                continue
            target_regions = self.handle_subscribed_interaction_regions.get(handle, {}).get(interaction_class, set())
            if not target_regions or not source_regions:
                continue
            if any(self._regions_overlap(source_region, target_region) for source_region in source_regions for target_region in target_regions):
                targets.add(handle)
        return targets

    def _directed_interaction_subscriber_matches(self, object_instance: str, object_class: str, interaction_class: str) -> bool:
        if interaction_class not in self.subscribed_directed_interactions.get(object_class, set()):
            return False
        if interaction_class not in self.directed_interaction_region_gates:
            return True
        target_regions = self.subscribed_interaction_regions.get(interaction_class, set())
        if not target_regions:
            return False
        source_regions = self._object_instance_region_values(object_instance)
        if not source_regions:
            return False
        return any(self._regions_overlap(source_region, target_region) for source_region in source_regions for target_region in target_regions)

    def _object_instance_region_values(self, object_instance: str) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    region
                    for regions in self.object_update_regions.get(object_instance, {}).values()
                    for region in regions
                }
            )
        )

    def _reflectable_attribute_names(self, object_instance: str, object_class: str) -> set[str]:
        return {
            attribute
            for attribute in self.subscribed_object_attributes.get(object_class, set())
            if self._attribute_regions_overlap(object_instance, object_class, attribute)
        }

    def _reflectable_attribute_names_for_handle(self, handle: str, object_instance: str, object_class: str) -> set[str]:
        return {
            attribute
            for attribute in self.handle_subscribed_object_attributes.get(handle, {}).get(object_class, set())
            if self._attribute_regions_overlap_for_handle(handle, object_instance, object_class, attribute)
        }

    def _queue_attribute_scope_advisories(self) -> None:
        if not self.switch_states.get("attributeScopeAdvisory", False):
            self.attribute_scope_state.clear()
            return
        in_scope_callbacks: dict[str, dict[str, set[str]]] = {}
        reentered_in_scope_callbacks: dict[str, dict[str, set[str]]] = {}
        out_of_scope_callbacks: dict[str, dict[str, set[str]]] = {}
        active_keys: set[tuple[str, str, str]] = set()
        for handle, object_class_map in self.handle_subscribed_object_attributes.items():
            for object_instance, record in self.object_instances.items():
                object_class = record["objectClass"]
                for attribute in object_class_map.get(object_class, set()):
                    state_key = (handle, object_instance, attribute)
                    active_keys.add(state_key)
                    in_scope = self._attribute_regions_overlap_for_handle(handle, object_instance, object_class, attribute)
                    previous = self.attribute_scope_state.get(state_key)
                    self.attribute_scope_state[state_key] = in_scope
                    if previous is None and in_scope:
                        in_scope_callbacks.setdefault(handle, {}).setdefault(object_instance, set()).add(attribute)
                    elif previous is True and not in_scope:
                        out_of_scope_callbacks.setdefault(handle, {}).setdefault(object_instance, set()).add(attribute)
                    elif previous is False and in_scope:
                        in_scope_callbacks.setdefault(handle, {}).setdefault(object_instance, set()).add(attribute)
                        reentered_in_scope_callbacks.setdefault(handle, {}).setdefault(object_instance, set()).add(attribute)
        for state_key in tuple(self.attribute_scope_state):
            if state_key in active_keys:
                continue
            handle, object_instance, attribute = state_key
            if self.attribute_scope_state.pop(state_key, False):
                out_of_scope_callbacks.setdefault(handle, {}).setdefault(object_instance, set()).add(attribute)
        for handle, object_map in sorted(in_scope_callbacks.items(), key=lambda item: int(item[0])):
            for object_instance, attributes in sorted(object_map.items()):
                object_class = self.object_instances.get(object_instance, {}).get("objectClass")
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        attributesInScope=callback_pb2.AttributesInScope(
                            objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                            attributes=_attribute_set(tuple(sorted(attributes))),
                        )
                    ),
                    target_handles={handle},
                )
                attribute_set = reentered_in_scope_callbacks.get(handle, {}).get(object_instance)
                if object_class is not None and attribute_set:
                    self._queue_turn_updates_on_for_object_instance(
                        object_instance,
                        attribute_set & self.published_object_attributes.get(object_class, set()),
                        target_handles={handle},
                    )
        for handle, object_map in sorted(out_of_scope_callbacks.items(), key=lambda item: int(item[0])):
            for object_instance, attributes in sorted(object_map.items()):
                object_class = self.object_instances.get(object_instance, {}).get("objectClass")
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        attributesOutOfScope=callback_pb2.AttributesOutOfScope(
                            objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                            attributes=_attribute_set(tuple(sorted(attributes))),
                        )
                    ),
                    target_handles={handle},
                )
                if object_class is not None:
                    self._queue_turn_updates_off(
                        object_class,
                        attributes & self.published_object_attributes.get(object_class, set()),
                        target_handles={handle},
                    )

    def _conveyed_regions_for(self, object_instance: str, reflected) -> datatypes_pb2.ConveyedRegionSet:
        result = datatypes_pb2.ConveyedRegionSet()
        region_values = {
            region
            for item in reflected
            for region in self.object_update_regions.get(object_instance, {}).get(item.attributeHandle.data.decode("ascii"), set())
        }
        self._fill_conveyed_regions(result, region_values)
        return result

    def _conveyed_regions_from(self, region_values: tuple[str, ...]) -> datatypes_pb2.ConveyedRegionSet:
        result = datatypes_pb2.ConveyedRegionSet()
        self._fill_conveyed_regions(result, set(region_values))
        return result

    def _fill_conveyed_regions(self, result: datatypes_pb2.ConveyedRegionSet, region_values: set[str]) -> None:
        for region_value in sorted(region_values):
            conveyed = result.conveyedRegions.add()
            for dimension in sorted(self.regions.get(region_value, ())):
                row = conveyed.dimensionAndRange.add()
                row.dimensionHandle.data = dimension.encode("ascii")
                lower, upper = self.region_bounds.get(region_value, {}).get(dimension, (0, 1024))
                row.rangeBounds.lower = lower
                row.rangeBounds.upper = upper

    def _remove_object_instance(self, object_instance: str) -> dict[str, str] | None:
        record = self.object_instances.pop(object_instance, None)
        if record is None:
            return None
        for deleted_objects in self.handle_locally_deleted_objects.values():
            deleted_objects.discard(object_instance)
        self.object_update_regions.pop(object_instance, None)
        self.attribute_scope_state = {
            key: value for key, value in self.attribute_scope_state.items() if key[1] != object_instance
        }
        self.attribute_owners = {key: value for key, value in self.attribute_owners.items() if key[0] != object_instance}
        self.unowned_attributes = {key for key in self.unowned_attributes if key[0] != object_instance}
        self.offered_attributes = {key for key in self.offered_attributes if key[0] != object_instance}
        self.pending_attribute_acquisitions = {
            key: value for key, value in self.pending_attribute_acquisitions.items() if key[0][0] != object_instance
        }
        self.pending_attribute_requesters = {
            key: value for key, value in self.pending_attribute_requesters.items() if key[0][0] != object_instance
        }
        return record

    def _ensure_mom_federation_object(self, federation_name: str) -> None:
        self.mom_federation_name = federation_name
        if self.mom_federation_object_handle is None:
            self.mom_federation_object_handle = "900"
        self.object_instances.setdefault(
            self.mom_federation_object_handle,
            {
                "name": federation_name,
                "objectClass": self.object_classes["HLAobjectRoot.HLAmanager.HLAfederation"],
            },
        )

    def _ensure_mom_federate_object(self, federate_handle: str, federate_name: str) -> str:
        object_handle = self.mom_federate_object_handles.setdefault(federate_handle, str(900 + int(federate_handle)))
        self.object_instances.setdefault(
            object_handle,
            {
                "name": f"HLAfederate.{federate_name}",
                "objectClass": self.object_classes["HLAobjectRoot.HLAmanager.HLAfederate"],
            },
        )
        return object_handle

    def _mom_federates_in_federation_bytes(self) -> bytes:
        members = [self.joined_federate_handles[handle] for handle in sorted(self.joined_federate_handles, key=int)]
        return ",".join(members).encode("utf-8")

    def _mom_attribute_value(self, object_instance: str, attribute: str) -> bytes | None:
        federation_class = self.object_classes["HLAobjectRoot.HLAmanager.HLAfederation"]
        federate_class = self.object_classes["HLAobjectRoot.HLAmanager.HLAfederate"]
        if object_instance == self.mom_federation_object_handle:
            if attribute == self.attributes[(federation_class, "HLAfederationName")]:
                return (self.mom_federation_name or "").encode("utf-8")
            if attribute == self.attributes[(federation_class, "HLAfederatesInFederation")]:
                return self._mom_federates_in_federation_bytes()
            return None
        for federate_handle, mom_object_handle in self.mom_federate_object_handles.items():
            if mom_object_handle != object_instance:
                continue
            if attribute == self.attributes[(federate_class, "HLAfederateName")]:
                return self.joined_federate_handles.get(federate_handle, "").encode("utf-8")
            return None
        return None

    def _queue_rti_owned_attribute_reflection(
        self,
        target_handle: str,
        object_instance: str,
        attributes: list[str],
        user_supplied_tag: bytes,
    ) -> None:
        values = datatypes_pb2.AttributeHandleValueMap()
        for attribute in attributes:
            payload = self._mom_attribute_value(object_instance, attribute)
            if payload is None:
                continue
            row = values.attributeHandleValue.add()
            row.attributeHandle.data = attribute.encode("ascii")
            row.value = payload
        if not values.attributeHandleValue:
            return
        self._enqueue_callback(
            callback_pb2.CallbackRequest(
                reflectAttributeValues=callback_pb2.ReflectAttributeValues(
                    objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                    attributeValues=values,
                    userSuppliedTag=user_supplied_tag,
                    transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                    producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                )
            ),
            target_handles={target_handle},
        )

    def _is_rti_owned_attribute(self, object_instance: str, attribute: str) -> bool:
        if object_instance == self.mom_federation_object_handle:
            return attribute in {
                self.attributes.get((self.object_classes["HLAobjectRoot.HLAmanager.HLAfederation"], "HLAfederationName")),
                self.attributes.get((self.object_classes["HLAobjectRoot.HLAmanager.HLAfederation"], "HLAfederatesInFederation")),
            }
        return any(
            mom_object_handle == object_instance
            and attribute == self.attributes.get((self.object_classes["HLAobjectRoot.HLAmanager.HLAfederate"], "HLAfederateName"))
            for mom_object_handle in self.mom_federate_object_handles.values()
        )

    def _remove_region_references(self, region: str) -> None:
        for handle, object_class_regions in self.handle_subscribed_object_regions.items():
            for object_class, attribute_regions in object_class_regions.items():
                for attribute, regions in tuple(attribute_regions.items()):
                    regions.discard(region)
                    if not regions:
                        attribute_regions.pop(attribute, None)
                        self.handle_subscribed_object_attributes.get(handle, {}).get(object_class, set()).discard(attribute)
        self._rebuild_subscribed_object_aggregates()
        for update_regions in self.object_update_regions.values():
            for attribute, regions in tuple(update_regions.items()):
                regions.discard(region)
                if not regions:
                    update_regions.pop(attribute, None)
        for handle, interaction_regions in self.handle_subscribed_interaction_regions.items():
            for interaction_class, regions in tuple(interaction_regions.items()):
                regions.discard(region)
                if not regions:
                    interaction_regions.pop(interaction_class, None)
                    self.handle_subscribed_interactions.get(handle, set()).discard(interaction_class)
        self._rebuild_subscribed_interaction_aggregates()


class RTI2025GrpcServer:
    def __init__(self, config: RTI2025GrpcServerConfig = RTI2025GrpcServerConfig()) -> None:
        if grpc is None:  # pragma: no cover - optional dependency guard
            raise RuntimeError("gRPC server requested, but grpcio is not installed") from _GRPC_IMPORT_ERROR
        self.config = config
        self.runtime_provider = "python2025"
        self.implementation_lane = "hla-backend-python2025"
        self.counts_as_python_2025_rti = True
        self.wrapper_only = False
        self.spec = "rti1516_2025"
        self.transport_kind = "grpc"
        self.servicer = _FedPro2025GatewayServicer()
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=config.max_workers))
        pb2_grpc.add_HLA2025FedProGatewayServicer_to_server(self.servicer, self.server)
        self.port = self.server.add_insecure_port(f"{config.host}:{config.port}")
        self.target = f"{config.host}:{self.port}"
        self._started = False

    def start(self) -> "RTI2025GrpcServer":
        if not self._started:
            self.server.start()
            self._started = True
        return self

    def close(self) -> None:
        if self._started:
            self.server.stop(0).wait()
            self._started = False

    def capability_report(self) -> dict[str, object]:
        return {
            "runtime_provider": self.runtime_provider,
            "implementation_lane": self.implementation_lane,
            "counts_as_python_2025_rti": self.counts_as_python_2025_rti,
            "wrapper_only": self.wrapper_only,
            "spec": self.spec,
            "transport_kind": self.transport_kind,
            "target": self.target,
        }


def start_2025_grpc_server(
    *,
    host: str = "127.0.0.1",
    port: int = 0,
) -> RTI2025GrpcServer:
    return RTI2025GrpcServer(RTI2025GrpcServerConfig(host=host, port=port)).start()


__all__ = [
    "RTI2025GrpcServer",
    "RTI2025GrpcServerConfig",
    "start_2025_grpc_server",
]
