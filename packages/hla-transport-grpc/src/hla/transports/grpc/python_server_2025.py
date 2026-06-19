"""Transport-hosted IEEE 1516.1-2025 RTI server for the gRPC wire path."""

from __future__ import annotations

from concurrent import futures
from copy import deepcopy
from dataclasses import dataclass, field

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
    automatic_resign_directive: int = datatypes_pb2.NO_ACTION
    time_regulating: bool = False
    time_constrained: bool = False
    asynchronous_delivery_enabled: bool = False
    handle_time_regulating: dict[str, bool] = field(default_factory=dict)
    handle_time_constrained: dict[str, bool] = field(default_factory=dict)
    handle_asynchronous_delivery_enabled: dict[str, bool] = field(default_factory=dict)
    callback_delivery_enabled: bool = True
    peer_callback_delivery_enabled: dict[str, bool] = field(default_factory=dict)
    directed_interaction_region_gates: set[str] = field(default_factory=set)
    published_directed_interactions: dict[str, set[str]] = field(default_factory=dict)
    handle_published_directed_interactions: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    handle_subscribed_directed_interactions: dict[str, dict[str, set[str]]] = field(default_factory=dict)
    handle_subscribed_interactions: dict[str, set[str]] = field(default_factory=dict)
    handle_subscribed_interaction_regions: dict[str, dict[str, set[str]]] = field(default_factory=dict)


def _callback_request() -> callback_pb2.CallbackRequest:
    return callback_pb2.CallbackRequest(timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:7")))


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
        }
        self.object_class_names = {value: key for key, value in self.object_classes.items()}
        self.attributes = {
            ("100", "Position"): "200",
            ("101", "Position"): "201",
            ("102", "HLAfederationName"): "202",
        }
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
        }
        self.next_parameter_handle = 800
        self.parameter_names = {(interaction_class, value): name for (interaction_class, name), value in self.parameters.items()}
        self.dimensions = {"RoutingSpace": "300"}
        self.dimension_names = {value: key for key, value in self.dimensions.items()}
        self.transportations = {"HLAreliable": "1", "HLAbestEffort": "2"}
        self.transportation_names = {value: key for key, value in self.transportations.items()}
        self.object_instances: dict[str, dict[str, str]] = {}
        self.mom_federation_object_handle: str | None = None
        self.mom_federation_name: str | None = None
        self.reserved_object_instance_names: dict[str, str] = {}
        self.attribute_owners: dict[tuple[str, str], str] = {}
        self.published_object_attributes: dict[str, set[str]] = {}
        self.handle_published_object_attributes: dict[str, dict[str, set[str]]] = {}
        self.subscribed_object_attributes: dict[str, set[str]] = {}
        self.subscribed_object_regions: dict[str, dict[str, set[str]]] = {}
        self.handle_subscribed_object_attributes: dict[str, dict[str, set[str]]] = {}
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
        self.automatic_resign_directive = datatypes_pb2.NO_ACTION
        self.switch_states: dict[str, bool] = {
            "advisoriesUseKnownClass": False,
            "allowRelaxedDDM": False,
            "attributeRelevanceAdvisory": False,
            "attributeScopeAdvisory": False,
            "autoProvide": False,
            "conveyRegionDesignatorSets": False,
            "delaySubscriptionEvaluation": False,
            "exceptionReporting": False,
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
        self.callback_delivery_enabled = True
        self.peer_callback_delivery_enabled: dict[str, bool] = {}
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
        self.save_label: str | None = None
        self.save_status: dict[str, int] = {}
        self.restore_label: str | None = None
        self.restore_status: dict[str, int] = {}
        self.synchronization_points: dict[str, dict[str, bytes | bool | set[str]]] = {}
        self.attribute_scope_state: dict[tuple[str, str, str], bool] = {}
        self.callback_queue: list[callback_pb2.CallbackRequest] = []
        self.callback_targets: dict[int, tuple[frozenset[str] | None, frozenset[str] | None]] = {}

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
            self.peer_callback_delivery_enabled[peer] = True
            return rti_pb2.CallResponse(connectResponse=rti_pb2.ConnectResponse())
        if request_kind == "disconnectRequest":
            self.peer_callback_delivery_enabled.pop(peer, None)
            self._remove_peer_federate(peer)
            return rti_pb2.CallResponse(disconnectResponse=rti_pb2.DisconnectResponse())
        if request_kind in {
            "createFederationExecutionWithModulesRequest",
            "createFederationExecutionWithModulesAndTimeRequest",
        }:
            payload = getattr(request, request_kind)
            self.federations.add(payload.federationName)
            self.federation_logical_time_implementations[payload.federationName] = getattr(
                payload,
                "logicalTimeImplementationName",
                "",
            ) or "HLAinteger64Time"
            self.fom_modules = _fom_module_designators(payload.fomModules)
            self._ensure_mom_federation_object(payload.federationName)
            if request_kind == "createFederationExecutionWithModulesAndTimeRequest":
                return rti_pb2.CallResponse(createFederationExecutionWithModulesAndTimeResponse=rti_pb2.CreateFederationExecutionWithModulesAndTimeResponse())
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
            payload = getattr(request, request_kind)
            federation_name = payload.federationName
            if federation_name not in self.federations:
                return self._error("FederationExecutionDoesNotExist", federation_name)
            federate_name = getattr(payload, "federateName", "") or f"fedpro-federate-{self.next_federate_handle}"
            handle = self.next_federate_handle
            self.next_federate_handle += 1
            self.joined_federates[federate_name] = federation_name
            self.joined_federate_handles[str(handle)] = federate_name
            self.joined_federate_types[str(handle)] = payload.federateType
            self.peer_federate_handles[peer] = str(handle)
            self.handle_service_reporting.setdefault(str(handle), False)
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
            result = datatypes_pb2.JoinResult(
                federateHandle=datatypes_pb2.FederateHandle(data=str(handle).encode("ascii")),
                logicalTimeImplementationName="HLAinteger64Time",
            )
            if request_kind in {"joinFederationExecutionWithNameRequest", "joinFederationExecutionWithNameAndModulesRequest"}:
                return rti_pb2.CallResponse(joinFederationExecutionWithNameResponse=rti_pb2.JoinFederationExecutionWithNameResponse(result=result))
            return rti_pb2.CallResponse(joinFederationExecutionResponse=rti_pb2.JoinFederationExecutionResponse(result=result))
        if request_kind == "resignFederationExecutionRequest":
            action = request.resignFederationExecutionRequest.resignAction
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
            if self.joined_federates:
                return self._error("FederatesCurrentlyJoined", payload.federationName)
            self.federations.discard(payload.federationName)
            self.federation_logical_time_implementations.pop(payload.federationName, None)
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
            if name == self.mom_federation_name and self.mom_federation_object_handle is not None:
                return rti_pb2.CallResponse(
                    getObjectInstanceHandleResponse=rti_pb2.GetObjectInstanceHandleResponse(
                        result=_handle(datatypes_pb2.ObjectInstanceHandle, self.mom_federation_object_handle)
                    )
                )
            for handle, record in self.object_instances.items():
                if record["name"] == name:
                    return rti_pb2.CallResponse(
                        getObjectInstanceHandleResponse=rti_pb2.GetObjectInstanceHandleResponse(
                            result=_handle(datatypes_pb2.ObjectInstanceHandle, handle)
                        )
                    )
            return self._error("ObjectInstanceNotKnown", name)
        if request_kind == "getObjectInstanceNameRequest":
            handle = request.getObjectInstanceNameRequest.objectInstance.data.decode("ascii")
            if handle == self.mom_federation_object_handle and self.mom_federation_name is not None:
                return rti_pb2.CallResponse(getObjectInstanceNameResponse=rti_pb2.GetObjectInstanceNameResponse(result=self.mom_federation_name))
            record = self.object_instances.get(handle)
            if record is None:
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
            name = request.getInteractionClassHandleRequest.interactionClassName
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
            try:
                handle = self.parameters[(interaction_class, payload.parameterName)]
            except KeyError:
                interaction_name = self.interaction_names.get(interaction_class, "")
                if ".HLAmanager." not in interaction_name:
                    return self._error("NameNotFound", payload.parameterName)
                handle = str(self.next_parameter_handle)
                self.next_parameter_handle += 1
                self.parameters[(interaction_class, payload.parameterName)] = handle
                self.parameter_names[(interaction_class, handle)] = payload.parameterName
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
            target_federates = set(self._joined_handle_values())
            if request_kind == "registerFederationSynchronizationPointWithSetRequest":
                target_federates = {
                    item.data.decode("ascii") for item in payload.synchronizationSet.federateHandle if item.data
                }
                if not target_federates:
                    target_federates = set(self._joined_handle_values())
            record = self._synchronization_point_record(payload.synchronizationPointLabel)
            record["tag"] = bytes(payload.userSuppliedTag)
            record["federates"] = target_federates
            record["achieved"].clear()
            record["synchronized"] = False
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
                self._queue_federation_synchronized_if_ready(payload.synchronizationPointLabel)
            return rti_pb2.CallResponse(synchronizationPointAchievedResponse=rti_pb2.SynchronizationPointAchievedResponse())
        if request_kind == "getDimensionHandleRequest":
            name = request.getDimensionHandleRequest.dimensionName
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
                return self._error("NameNotFound", name)
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
                return self._error("InvalidTransportationType", handle)
        if request_kind == "getOrderTypeRequest":
            name = request.getOrderTypeRequest.orderTypeName
            if name == "HLAreceive":
                return rti_pb2.CallResponse(getOrderTypeResponse=rti_pb2.GetOrderTypeResponse(result=datatypes_pb2.RECEIVE))
            if name == "HLAtimestamp":
                return rti_pb2.CallResponse(getOrderTypeResponse=rti_pb2.GetOrderTypeResponse(result=datatypes_pb2.TIMESTAMP))
            return self._error("InvalidOrderName", name)
        if request_kind == "getOrderNameRequest":
            order = request.getOrderNameRequest.orderType
            name = "HLAtimestamp" if order == datatypes_pb2.TIMESTAMP else "HLAreceive"
            return rti_pb2.CallResponse(getOrderNameResponse=rti_pb2.GetOrderNameResponse(result=name))
        if request_kind == "getUpdateRateValueRequest":
            value = 1.0 if request.getUpdateRateValueRequest.updateRateDesignator == "HLAdefaultUpdateRate" else 0.0
            return rti_pb2.CallResponse(getUpdateRateValueResponse=rti_pb2.GetUpdateRateValueResponse(result=value))
        if request_kind == "getUpdateRateValueForAttributeRequest":
            return rti_pb2.CallResponse(getUpdateRateValueForAttributeResponse=rti_pb2.GetUpdateRateValueForAttributeResponse(result=1.0))
        if request_kind == "getKnownObjectClassHandleRequest":
            object_instance = request.getKnownObjectClassHandleRequest.objectInstance.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            if record is None:
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
            self._set_handle_lookahead(self._current_federate_handle(peer), request.modifyLookaheadRequest.lookahead)
            return rti_pb2.CallResponse(modifyLookaheadResponse=rti_pb2.ModifyLookaheadResponse())
        if request_kind == "queryLookaheadRequest":
            return rti_pb2.CallResponse(
                queryLookaheadResponse=rti_pb2.QueryLookaheadResponse(
                    result=self._handle_lookahead(self._current_federate_handle(peer))
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
            payload = request.requestFederationSaveWithTimeRequest
            if self.save_label is not None:
                return self._error("SaveInProgress", payload.label)
            self.save_label = payload.label
            self.save_status = {handle: datatypes_pb2.FEDERATE_INSTRUCTED_TO_SAVE for handle in self._joined_handle_values()}
            if payload.time.data:
                for handle in self._joined_handle_values():
                    self._enqueue_callback(
                        callback_pb2.CallbackRequest(
                            initiateFederateSaveWithTime=callback_pb2.InitiateFederateSaveWithTime(
                                label=payload.label,
                                time=payload.time,
                            )
                        ),
                        target_handles={handle},
                    )
            else:
                for handle in self._joined_handle_values():
                    self._enqueue_callback(
                        callback_pb2.CallbackRequest(initiateFederateSave=callback_pb2.InitiateFederateSave(label=payload.label)),
                        target_handles={handle},
                    )
            return rti_pb2.CallResponse(requestFederationSaveWithTimeResponse=rti_pb2.RequestFederationSaveWithTimeResponse())
        if request_kind == "federateSaveBegunRequest":
            if self.save_label is None:
                return self._error("SaveNotInitiated", "No federation save is in progress")
            self.save_status[self._current_federate_handle(peer)] = datatypes_pb2.FEDERATE_SAVING
            return rti_pb2.CallResponse(federateSaveBegunResponse=rti_pb2.FederateSaveBegunResponse())
        if request_kind == "queryFederationSaveStatusRequest":
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    federationSaveStatusResponse=callback_pb2.FederationSaveStatusResponse(response=self._save_status_array())
                ),
                target_peers={peer},
            )
            return rti_pb2.CallResponse(queryFederationSaveStatusResponse=rti_pb2.QueryFederationSaveStatusResponse())
        if request_kind == "federateSaveCompleteRequest":
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
            self.save_label = None
            self.save_status = {}
            for handle in self._joined_handle_values():
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(federationNotSaved=callback_pb2.FederationNotSaved(reason=datatypes_pb2.SAVE_ABORTED)),
                    target_handles={handle},
                )
            return rti_pb2.CallResponse(abortFederationSaveResponse=rti_pb2.AbortFederationSaveResponse())
        if request_kind == "requestFederationRestoreRequest":
            label = request.requestFederationRestoreRequest.label
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
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    federationRestoreStatusResponse=callback_pb2.FederationRestoreStatusResponse(response=self._restore_status_array())
                ),
                target_peers={peer},
            )
            return rti_pb2.CallResponse(queryFederationRestoreStatusResponse=rti_pb2.QueryFederationRestoreStatusResponse())
        if request_kind == "federateRestoreCompleteRequest":
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
            transportation = payload.transportationType.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.default_attribute_transportation[(object_instance, attribute.data.decode("ascii"))] = transportation
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
            attribute = payload.attribute.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            object_class = record["objectClass"] if record is not None else ""
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
            transportation = payload.transportationType.data.decode("ascii")
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
            handle = self._current_federate_handle(peer)
            self.handle_published_object_attributes.setdefault(handle, {}).setdefault(object_class, set()).update(
                attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle
            )
            self._rebuild_published_object_aggregates()
            return rti_pb2.CallResponse(publishObjectClassAttributesResponse=rti_pb2.PublishObjectClassAttributesResponse())
        if request_kind == "unpublishObjectClassAttributesRequest":
            payload = request.unpublishObjectClassAttributesRequest
            object_class = payload.objectClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            published = self.handle_published_object_attributes.setdefault(handle, {}).setdefault(object_class, set())
            published.difference_update(attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle)
            if not published:
                self.handle_published_object_attributes.get(handle, {}).pop(object_class, None)
            self._rebuild_published_object_aggregates()
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
            self.handle_subscribed_object_attributes.setdefault(self._current_federate_handle(peer), {}).setdefault(
                object_class,
                set(),
            ).update(attributes)
            self._rebuild_subscribed_object_aggregates()
            for object_instance, record in self.object_instances.items():
                if record["objectClass"] == object_class:
                    self._queue_discovery(
                        object_instance,
                        object_class,
                        record["name"],
                        target_handles={self._current_federate_handle(peer)},
                    )
            self._queue_turn_updates_on(
                object_class,
                attributes,
                getattr(payload, "updateRateDesignator", ""),
                target_handles={self._current_federate_handle(peer)},
            )
            response_kind = request_kind.replace("Request", "Response")
            response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
            return rti_pb2.CallResponse(**{response_kind: response_type()})
        if request_kind == "subscribeObjectClassAttributesWithRegionsRequest":
            payload = request.subscribeObjectClassAttributesWithRegionsRequest
            object_class = payload.objectClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            prior_scope_state = dict(self.attribute_scope_state)
            region_map = self.handle_subscribed_object_regions.setdefault(handle, {}).setdefault(object_class, {})
            for attribute, regions in self._attribute_region_pairs(payload.attributesAndRegions):
                self.handle_subscribed_object_attributes.setdefault(handle, {}).setdefault(object_class, set()).add(attribute)
                region_map.setdefault(attribute, set()).update(regions)
            self._rebuild_subscribed_object_aggregates()
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
            self._queue_turn_updates_off(object_class, removed_attributes, target_handles={handle})
            self._queue_attribute_scope_advisories()
            return rti_pb2.CallResponse(
                unsubscribeObjectClassAttributesWithRegionsResponse=rti_pb2.UnsubscribeObjectClassAttributesWithRegionsResponse()
            )
        if request_kind == "unsubscribeObjectClassAttributesRequest":
            payload = request.unsubscribeObjectClassAttributesRequest
            object_class = payload.objectClass.data.decode("ascii")
            removed_attributes = {attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle}
            current = self.handle_subscribed_object_attributes.setdefault(self._current_federate_handle(peer), {}).setdefault(
                object_class,
                set(),
            )
            current.difference_update(removed_attributes)
            self._rebuild_subscribed_object_aggregates()
            self._queue_turn_updates_off(
                object_class,
                removed_attributes,
                target_handles={self._current_federate_handle(peer)},
            )
            return rti_pb2.CallResponse(
                unsubscribeObjectClassAttributesResponse=rti_pb2.UnsubscribeObjectClassAttributesResponse()
            )
        if request_kind == "publishInteractionClassRequest":
            interaction_class = request.publishInteractionClassRequest.interactionClass.data.decode("ascii")
            self.handle_published_interactions.setdefault(self._current_federate_handle(peer), set()).add(interaction_class)
            self._rebuild_published_interaction_aggregates()
            return rti_pb2.CallResponse(publishInteractionClassResponse=rti_pb2.PublishInteractionClassResponse())
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
            self.handle_subscribed_interactions.setdefault(self._current_federate_handle(peer), set()).add(interaction_class)
            self._rebuild_subscribed_interaction_aggregates()
            response_kind = request_kind.replace("Request", "Response")
            response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
            return rti_pb2.CallResponse(**{response_kind: response_type()})
        if request_kind == "subscribeInteractionClassWithRegionsRequest":
            payload = request.subscribeInteractionClassWithRegionsRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            self.handle_subscribed_interactions.setdefault(handle, set()).add(interaction_class)
            self.directed_interaction_region_gates.add(interaction_class)
            self.handle_subscribed_interaction_regions.setdefault(handle, {}).setdefault(interaction_class, set()).update(
                region.data.decode("ascii") for region in payload.regions.regionHandle
            )
            self._rebuild_subscribed_interaction_aggregates()
            return rti_pb2.CallResponse(subscribeInteractionClassWithRegionsResponse=rti_pb2.SubscribeInteractionClassWithRegionsResponse())
        if request_kind == "unsubscribeInteractionClassWithRegionsRequest":
            payload = request.unsubscribeInteractionClassWithRegionsRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            handle = self._current_federate_handle(peer)
            regions = self.handle_subscribed_interaction_regions.setdefault(handle, {}).setdefault(interaction_class, set())
            regions.difference_update(region.data.decode("ascii") for region in payload.regions.regionHandle)
            if not regions:
                self.handle_subscribed_interaction_regions.get(handle, {}).pop(interaction_class, None)
                self.handle_subscribed_interactions.setdefault(handle, set()).discard(interaction_class)
            self._rebuild_subscribed_interaction_aggregates()
            return rti_pb2.CallResponse(unsubscribeInteractionClassWithRegionsResponse=rti_pb2.UnsubscribeInteractionClassWithRegionsResponse())
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
        if request_kind in {"registerObjectInstanceRequest", "registerObjectInstanceWithNameRequest"}:
            payload = getattr(request, request_kind)
            object_class = payload.objectClass.data.decode("ascii")
            object_name = getattr(payload, "objectInstanceName", "") or f"fedpro-object-{self.next_object_instance_handle}"
            if request_kind == "registerObjectInstanceWithNameRequest":
                if any(record["name"] == object_name for record in self.object_instances.values()):
                    return self._error("ObjectInstanceNameInUse", object_name)
                reserved_by = self.reserved_object_instance_names.get(object_name)
                if reserved_by is not None and reserved_by != self._current_federate_handle():
                    return self._error("ObjectInstanceNameInUse", object_name)
            handle = str(self.next_object_instance_handle)
            self.next_object_instance_handle += 1
            self.object_instances[handle] = {"name": object_name, "objectClass": object_class}
            owner_handle = self._current_federate_handle(peer)
            for (declared_object_class, _name), attribute_handle in self.attributes.items():
                if declared_object_class == object_class:
                    self.attribute_owners[(handle, attribute_handle)] = owner_handle
            self.reserved_object_instance_names.pop(object_name, None)
            discovery_targets = self._discovery_target_handles(object_class, exclude_handle=owner_handle)
            if discovery_targets:
                self._queue_discovery(handle, object_class, object_name, target_handles=discovery_targets)
            response_kind = (
                "registerObjectInstanceWithNameResponse"
                if request_kind == "registerObjectInstanceWithNameRequest"
                else "registerObjectInstanceResponse"
            )
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
            if self.reserved_object_instance_names.get(name) != self._current_federate_handle():
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
            owner = self._current_federate_handle()
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
            published = self.published_object_attributes.get(object_class, set())
            if any(item.attributeHandle.data.decode("ascii") not in published for item in payload.attributeValues.attributeHandleValue):
                return self._error("ObjectClassNotPublished", object_class)
            reflected_by_handle = self._reflection_target_handles(
                object_instance,
                object_class,
                tuple(item.attributeHandle.data.decode("ascii") for item in payload.attributeValues.attributeHandleValue),
            )
            for target_handle, attribute_values in reflected_by_handle.items():
                values = datatypes_pb2.AttributeHandleValueMap()
                reflected_items = [
                    item
                    for item in payload.attributeValues.attributeHandleValue
                    if item.attributeHandle.data.decode("ascii") in set(attribute_values)
                ]
                for item in reflected_items:
                    row = values.attributeHandleValue.add()
                    row.attributeHandle.CopyFrom(item.attributeHandle)
                    row.value = item.value
                self._enqueue_callback(
                    callback_pb2.CallbackRequest(
                        reflectAttributeValues=callback_pb2.ReflectAttributeValues(
                            objectInstance=payload.objectInstance,
                            attributeValues=values,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle(peer)),
                            optionalSentRegions=self._conveyed_regions_for(object_instance, reflected_items),
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
            self.updates_sent += 1
            self.object_instances_updated += 1
            self._increment_counter(self.handle_updates_sent, source_handle)
            self._increment_counter(self.handle_object_instances_updated, source_handle)
            object_instance = payload.objectInstance.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            object_class = record["objectClass"]
            published = self.published_object_attributes.get(object_class, set())
            if any(item.attributeHandle.data.decode("ascii") not in published for item in payload.attributeValues.attributeHandleValue):
                return self._error("ObjectClassNotPublished", object_class)
            retraction_handle = self._next_retraction_handle()
            reflected_by_handle = self._reflection_target_handles(
                object_instance,
                object_class,
                tuple(item.attributeHandle.data.decode("ascii") for item in payload.attributeValues.attributeHandleValue),
            )
            for target_handle, attribute_values in reflected_by_handle.items():
                values = datatypes_pb2.AttributeHandleValueMap()
                reflected_items = [
                    item
                    for item in payload.attributeValues.attributeHandleValue
                    if item.attributeHandle.data.decode("ascii") in set(attribute_values)
                ]
                for item in reflected_items:
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
                            transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle(peer)),
                            optionalSentRegions=self._conveyed_regions_for(object_instance, reflected_items),
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
            return rti_pb2.CallResponse(localDeleteObjectInstanceResponse=rti_pb2.LocalDeleteObjectInstanceResponse())
        if request_kind == "requestInstanceAttributeValueUpdateRequest":
            payload = request.requestInstanceAttributeValueUpdateRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            requested_attributes = [attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle]
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
            for object_instance, record in self.object_instances.items():
                if record["objectClass"] != object_class:
                    continue
                requested_attributes = [attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle]
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
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestSubscriptions"]:
                self._queue_object_subscription_report(payload.parameterValues)
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
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesThatCanBeDeleted",
                    "HLAobjectInstanceCounts",
                    len(self.object_instances),
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
                            transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
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
                sendInteractionWithTimeResponse=rti_pb2.SendInteractionWithTimeResponse(
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
            return rti_pb2.CallResponse(
                isAttributeOwnedByFederateResponse=rti_pb2.IsAttributeOwnedByFederateResponse(
                    result=not self._is_rti_owned_attribute(object_instance, attribute)
                    and (object_instance, attribute) not in self.unowned_attributes
                )
            )
        if request_kind == "unconditionalAttributeOwnershipDivestitureRequest":
            payload = request.unconditionalAttributeOwnershipDivestitureRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                key = (object_instance, attribute.data.decode("ascii"))
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
            available = []
            unavailable = []
            for attribute in payload.desiredAttributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                key = (object_instance, attribute_value)
                if key in self.unowned_attributes:
                    self.unowned_attributes.discard(key)
                    self.attribute_owners[key] = self._current_federate_handle(peer)
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
            return rti_pb2.CallResponse(enableTimeConstrainedResponse=rti_pb2.EnableTimeConstrainedResponse())
        if request_kind == "disableTimeRegulationRequest":
            handle = self._current_federate_handle(peer)
            self.handle_time_regulating[handle] = False
            self._sync_time_globals(handle)
            return rti_pb2.CallResponse(disableTimeRegulationResponse=rti_pb2.DisableTimeRegulationResponse())
        if request_kind == "disableTimeConstrainedRequest":
            handle = self._current_federate_handle(peer)
            self.handle_time_constrained[handle] = False
            self._sync_time_globals(handle)
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
            self._grant_time(self._current_federate_handle(peer), request.timeAdvanceRequestRequest.time)
            return rti_pb2.CallResponse(timeAdvanceRequestResponse=rti_pb2.TimeAdvanceRequestResponse())
        if request_kind == "timeAdvanceRequestAvailableRequest":
            self._grant_time(self._current_federate_handle(peer), request.timeAdvanceRequestAvailableRequest.time)
            return rti_pb2.CallResponse(timeAdvanceRequestAvailableResponse=rti_pb2.TimeAdvanceRequestAvailableResponse())
        if request_kind == "nextMessageRequestRequest":
            self._grant_time(self._current_federate_handle(peer), request.nextMessageRequestRequest.time)
            return rti_pb2.CallResponse(nextMessageRequestResponse=rti_pb2.NextMessageRequestResponse())
        if request_kind == "nextMessageRequestAvailableRequest":
            self._grant_time(self._current_federate_handle(peer), request.nextMessageRequestAvailableRequest.time)
            return rti_pb2.CallResponse(nextMessageRequestAvailableResponse=rti_pb2.NextMessageRequestAvailableResponse())
        if request_kind == "flushQueueRequestRequest":
            self._grant_time(self._current_federate_handle(peer), request.flushQueueRequestRequest.time, flush_queue=True)
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
        return text in {"1", "true", "yes", "hlatrue", "on"}

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
            try:
                return datatypes_pb2.ResignAction.Value(text)
            except ValueError:
                return datatypes_pb2.NO_ACTION

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
                self.switch_states[switch_name] = self._mom_bool(params, "HLAreportingState")
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
            state = self._mom_text(params, "HLAattributeState", "owned").lower()
            key = (object_instance, attribute)
            if state in {"unowned", "hlaunowned", "0"}:
                self.unowned_attributes.add(key)
            else:
                self.unowned_attributes.discard(key)

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
            return
        if leaf == "HLArequestAttributeTransportationTypeChange":
            object_instance = self._mom_int(params, "HLAobjectInstance")
            transportation = self._mom_text(params, "HLAtransportation", "HLAreliable")
            for attribute in self._mom_attributes(params):
                self.default_attribute_transportation[(object_instance, attribute)] = transportation
            return
        if leaf == "HLArequestInteractionTransportationTypeChange":
            self.interaction_transportation = (
                self._mom_int(params, "HLAinteractionClass"),
                self._mom_text(params, "HLAtransportation", "HLAreliable"),
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
            return
        if leaf == "HLAdisableTimeRegulation":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_time_regulating[target_handle] = False
            self._sync_time_globals(target_handle)
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
            return
        if leaf == "HLAdisableTimeConstrained":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self.handle_time_constrained[target_handle] = False
            self._sync_time_globals(target_handle)
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
            self._grant_time(target_handle, self._mom_time(params))
            return
        if leaf == "HLAflushQueueRequest":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self._grant_time(target_handle, self._mom_time(params), flush_queue=True)
            return
        if leaf == "HLAmodifyLookahead":
            target_handle = self._mom_text(params, "HLAfederate", self._current_federate_handle())
            self._set_handle_lookahead(target_handle, self._mom_interval(params))

    @classmethod
    def _mom_order(cls, params: dict[str, bytes]) -> int:
        return datatypes_pb2.TIMESTAMP if cls._mom_text(params, "HLAsendOrder", "0") in {"1", "TIMESTAMP", "TimeStamp"} else datatypes_pb2.RECEIVE

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
        if report_class is None or not self._interaction_subscriber_matches(report_class, ()):
            return
        self._queue_mom_report(
            report_class,
            {
                "HLAservice": interaction_name.encode("utf-8"),
                "HLAexception": f"{type(exception).__name__}: {exception}".encode("utf-8"),
                "HLAparameterError": b"HLAtrue" if parameter_error else b"HLAfalse",
            },
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
        publication_rows = [
            f"{object_class}:{','.join(sorted(attributes, key=int))}"
            for object_class, attributes in sorted(requested_publications.items(), key=lambda item: int(item[0]))
            if attributes
        ]
        object_classes = ",".join(row.split(":", 1)[0] for row in publication_rows)
        attribute_lists = ";".join(publication_rows)
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": requested_handle.encode("ascii"),
                "HLAnumberOfClasses": str(len(publication_rows)).encode("ascii"),
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
        subscription_rows = [
            f"{object_class}:{','.join(sorted(attributes, key=int))}"
            for object_class, attributes in sorted(requested_subscriptions.items(), key=lambda item: int(item[0]))
            if attributes
        ]
        object_classes = ",".join(row.split(":", 1)[0] for row in subscription_rows)
        attribute_lists = ";".join(subscription_rows)
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": requested_handle.encode("ascii"),
                "HLAnumberOfClasses": str(len(subscription_rows)).encode("ascii"),
                "HLAobjectClass": object_classes.encode("ascii"),
                "HLAactive": b"HLAtrue" if subscription_rows else b"HLAfalse",
                "HLAmaxUpdateRate": b"",
                "HLAattributeList": attribute_lists.encode("ascii"),
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
                        self.callback_targets.pop(id(callback), None)
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

    def _grant_time(self, handle: str, time: datatypes_pb2.LogicalTime, *, flush_queue: bool = False) -> None:
        self._deliver_due_tso_callbacks(handle, time)
        self.handle_current_times[handle] = datatypes_pb2.LogicalTime(data=time.data)
        self._sync_time_globals(handle)
        if flush_queue:
            self._enqueue_callback(
                callback_pb2.CallbackRequest(
                    flushQueueGrant=callback_pb2.FlushQueueGrant(time=time, optimisticTime=time)
                ),
                target_handles={handle},
            )
            return
        self._enqueue_callback(
            callback_pb2.CallbackRequest(timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=time)),
            target_handles={handle},
        )

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
        return self.synchronization_points.setdefault(label, {"tag": b"", "achieved": set(), "federates": set(), "synchronized": False})

    def _synchronization_point_achieved(self, label: str) -> set[str]:
        achieved = self.synchronization_points.get(label, {}).get("achieved", set())
        return achieved if isinstance(achieved, set) else set()

    def _synchronization_point_federates(self, label: str) -> set[str]:
        federates = self.synchronization_points.get(label, {}).get("federates", set())
        return federates if isinstance(federates, set) else set()

    def _queue_federation_synchronized_if_ready(self, label: str) -> None:
        record = self._synchronization_point_record(label)
        synchronized = record.get("synchronized", False)
        if isinstance(synchronized, bool) and synchronized:
            return
        target_federates = self._synchronization_point_federates(label)
        if not target_federates or not target_federates.issubset(self._synchronization_point_achieved(label)):
            return
        record["synchronized"] = True
        self._enqueue_callback_per_handle(
            callback_pb2.CallbackRequest(
                federationSynchronized=callback_pb2.FederationSynchronized(
                    synchronizationPointLabel=label,
                    failedToSyncSet=datatypes_pb2.FederateHandleSet(),
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
        name = self.joined_federate_handles.pop(handle, None)
        if name is not None:
            self.joined_federates.pop(name, None)
        self.joined_federate_types.pop(handle, None)
        self.handle_service_reporting.pop(handle, None)
        self.handle_published_object_attributes.pop(handle, None)
        self.handle_published_interactions.pop(handle, None)
        self.handle_published_directed_interactions.pop(handle, None)
        self.handle_current_times.pop(handle, None)
        self.handle_lookahead.pop(handle, None)
        self.handle_time_regulating.pop(handle, None)
        self.handle_time_constrained.pop(handle, None)
        self.handle_asynchronous_delivery_enabled.pop(handle, None)
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
        self.handle_subscribed_object_attributes.pop(handle, None)
        self.handle_subscribed_object_regions.pop(handle, None)
        self.handle_subscribed_interactions.pop(handle, None)
        self.handle_subscribed_interaction_regions.pop(handle, None)
        self.handle_subscribed_directed_interactions.pop(handle, None)
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

    def _set_handle_lookahead(self, handle: str, lookahead: datatypes_pb2.LogicalTimeInterval) -> None:
        self.handle_lookahead[handle] = datatypes_pb2.LogicalTimeInterval(data=lookahead.data)
        self._sync_time_globals(handle)

    def _sync_time_globals(self, handle: str) -> None:
        self.current_time.CopyFrom(self._handle_current_time(handle))
        self.lookahead.CopyFrom(self._handle_lookahead(handle))
        self.time_regulating = self.handle_time_regulating.get(handle, False)
        self.time_constrained = self.handle_time_constrained.get(handle, False)
        self.asynchronous_delivery_enabled = self.handle_asynchronous_delivery_enabled.get(handle, False)

    def _query_galt(self, handle: str) -> datatypes_pb2.TimeQueryReturn:
        candidates: list[float] = [_logical_time_value(self._handle_current_time(handle))]
        candidates.extend(
            _logical_time_value(self._handle_current_time(other_handle))
            + _logical_interval_value(self._handle_lookahead(other_handle))
            for other_handle in self._joined_handle_values()
            if other_handle != handle and self.handle_time_regulating.get(other_handle, False)
        )
        if not candidates:
            return datatypes_pb2.TimeQueryReturn(logicalTimeIsValid=False)
        value = min(candidates)
        return datatypes_pb2.TimeQueryReturn(
            logicalTimeIsValid=True,
            logicalTime=datatypes_pb2.LogicalTime(data=f"HLAinteger64Time:{value:g}".encode("ascii")),
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
            logicalTime=datatypes_pb2.LogicalTime(data=f"HLAinteger64Time:{value:g}".encode("ascii")),
        )

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

    def _snapshot(self) -> _FederationSnapshot:
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
            automatic_resign_directive=self.automatic_resign_directive,
            time_regulating=self.time_regulating,
            time_constrained=self.time_constrained,
            asynchronous_delivery_enabled=self.asynchronous_delivery_enabled,
            handle_time_regulating=dict(self.handle_time_regulating),
            handle_time_constrained=dict(self.handle_time_constrained),
            handle_asynchronous_delivery_enabled=dict(self.handle_asynchronous_delivery_enabled),
            callback_delivery_enabled=self.callback_delivery_enabled,
            peer_callback_delivery_enabled=dict(self.peer_callback_delivery_enabled),
            directed_interaction_region_gates=set(self.directed_interaction_region_gates),
            published_directed_interactions=deepcopy(self.published_directed_interactions),
            handle_published_directed_interactions=deepcopy(self.handle_published_directed_interactions),
            handle_subscribed_directed_interactions=deepcopy(self.handle_subscribed_directed_interactions),
            handle_subscribed_interactions=deepcopy(self.handle_subscribed_interactions),
            handle_subscribed_interaction_regions=deepcopy(self.handle_subscribed_interaction_regions),
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
        self.automatic_resign_directive = snapshot.automatic_resign_directive
        self.time_regulating = snapshot.time_regulating
        self.time_constrained = snapshot.time_constrained
        self.asynchronous_delivery_enabled = snapshot.asynchronous_delivery_enabled
        self.handle_time_regulating = dict(snapshot.handle_time_regulating)
        self.handle_time_constrained = dict(snapshot.handle_time_constrained)
        self.handle_asynchronous_delivery_enabled = dict(snapshot.handle_asynchronous_delivery_enabled)
        self.callback_delivery_enabled = snapshot.callback_delivery_enabled
        self.peer_callback_delivery_enabled = dict(snapshot.peer_callback_delivery_enabled)
        self.directed_interaction_region_gates = set(snapshot.directed_interaction_region_gates)
        self.published_directed_interactions = deepcopy(snapshot.published_directed_interactions)
        self.handle_published_directed_interactions = deepcopy(snapshot.handle_published_directed_interactions)
        self.handle_subscribed_directed_interactions = deepcopy(snapshot.handle_subscribed_directed_interactions)
        self.handle_subscribed_interactions = deepcopy(snapshot.handle_subscribed_interactions)
        self.handle_subscribed_interaction_regions = deepcopy(snapshot.handle_subscribed_interaction_regions)
        self._rebuild_published_object_aggregates()
        self._rebuild_published_interaction_aggregates()
        self._rebuild_published_directed_interactions()
        self._rebuild_subscribed_object_aggregates()
        self._rebuild_subscribed_interaction_aggregates()
        self._rebuild_subscribed_directed_interactions()
        remaining = self._joined_handle_values()
        if remaining:
            self._sync_time_globals(remaining[0])
        self.callback_queue.clear()
        self.callback_targets.clear()
        self.queued_tso_callbacks.clear()
        self.delivered_retractions.clear()
        self.delivered_retraction_targets.clear()
        self.requested_retractions.clear()
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

    def _is_rti_owned_attribute(self, object_instance: str, attribute: str) -> bool:
        return (
            object_instance == self.mom_federation_object_handle
            and attribute == self.attributes.get((self.object_classes["HLAobjectRoot.HLAmanager.HLAfederation"], "HLAfederationName"))
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
