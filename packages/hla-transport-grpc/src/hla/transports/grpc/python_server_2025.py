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
    unowned_attributes: set[tuple[str, str]]
    current_time: datatypes_pb2.LogicalTime
    next_object_instance_handle: int
    object_update_regions: dict[str, dict[str, set[str]]] = field(default_factory=dict)


def _callback_request() -> callback_pb2.CallbackRequest:
    return callback_pb2.CallbackRequest(timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:7")))


def _logical_time_value(time: datatypes_pb2.LogicalTime) -> float:
    raw = time.data.decode("ascii") if time.data else "HLAinteger64Time:0"
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


def _dimension_set(values: list[str] | tuple[str, ...] | str) -> datatypes_pb2.DimensionHandleSet:
    result = datatypes_pb2.DimensionHandleSet()
    items = values.split(",") if isinstance(values, str) else values
    for item in items:
        if item:
            result.dimensionHandle.add(data=str(item).encode("ascii"))
    return result


class _FedPro2025GatewayServicer(pb2_grpc.HLA2025FedProGatewayServicer):
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.federations: set[str] = set()
        self.joined_federates: dict[str, str] = {}
        self.joined_federate_handles: dict[str, str] = {}
        self.next_federate_handle = 1
        self.next_object_instance_handle = 1000
        self.next_region_handle = 700
        self.object_classes = {"HLAobjectRoot.RouteTarget": "100", "HLAobjectRoot.Target": "101"}
        self.object_class_names = {value: key for key, value in self.object_classes.items()}
        self.attributes = {("100", "Position"): "200", ("101", "Position"): "201"}
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
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstanceInformation": "416",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation": "417",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesThatCanBeDeleted": "418",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesThatCanBeDeleted": "419",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesUpdated": "420",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesUpdated": "421",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesReflected": "422",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesReflected": "423",
        }
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
            ("416", "HLAfederate"): "529",
            ("416", "HLAobjectInstance"): "530",
            ("417", "HLAfederate"): "531",
            ("417", "HLAobjectInstance"): "532",
            ("417", "HLAobjectClass"): "533",
            ("417", "HLAobjectInstanceName"): "534",
            ("417", "HLAattributeList"): "535",
            ("418", "HLAfederate"): "536",
            ("419", "HLAfederate"): "537",
            ("419", "HLAobjectInstanceCounts"): "538",
            ("420", "HLAfederate"): "539",
            ("421", "HLAfederate"): "540",
            ("421", "HLAobjectInstanceCounts"): "541",
            ("422", "HLAfederate"): "542",
            ("423", "HLAfederate"): "543",
            ("423", "HLAobjectInstanceCounts"): "544",
        }
        self.parameter_names = {(interaction_class, value): name for (interaction_class, name), value in self.parameters.items()}
        self.dimensions = {"RoutingSpace": "300"}
        self.dimension_names = {value: key for key, value in self.dimensions.items()}
        self.transportations = {"HLAreliable": "1", "HLAbestEffort": "2"}
        self.transportation_names = {value: key for key, value in self.transportations.items()}
        self.object_instances: dict[str, dict[str, str]] = {}
        self.published_object_attributes: dict[str, set[str]] = {}
        self.subscribed_object_attributes: dict[str, set[str]] = {}
        self.subscribed_object_regions: dict[str, dict[str, set[str]]] = {}
        self.object_update_regions: dict[str, dict[str, set[str]]] = {}
        self.regions: dict[str, set[str]] = {}
        self.region_bounds: dict[str, dict[str, tuple[int, int]]] = {}
        self.published_interactions: set[str] = set()
        self.subscribed_interactions: set[str] = set()
        self.subscribed_interaction_regions: dict[str, set[str]] = {}
        self.unowned_attributes: set[tuple[str, str]] = set()
        self.offered_attributes: set[tuple[str, str]] = set()
        self.pending_attribute_acquisitions: dict[tuple[str, str], bytes] = {}
        self.default_attribute_transportation: dict[tuple[str, str], str] = {}
        self.default_attribute_order: dict[tuple[str, str], int] = {}
        self.service_reporting = False
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
        self.updates_sent = 0
        self.reflections_received = 0
        self.interactions_sent = 0
        self.interactions_received = 0
        self.object_instances_updated = 0
        self.object_instances_reflected = 0
        self.queued_tso_callbacks: dict[str, tuple[float, callback_pb2.CallbackRequest]] = {}
        self.delivered_retractions: set[str] = set()
        self.saved_labels: set[str] = set()
        self.saved_snapshots: dict[str, _FederationSnapshot] = {}
        self.save_label: str | None = None
        self.save_status: dict[str, int] = {}
        self.restore_label: str | None = None
        self.restore_status: dict[str, int] = {}
        self.callback_queue: list[callback_pb2.CallbackRequest] = []

    def Call(self, request, context):  # noqa: N802 - grpc generated naming
        request_kind = request.WhichOneof("callRequest")
        if request_kind is not None:
            self.calls.append(request_kind)
        if request_kind in {
            "connectRequest",
            "connectWithCredentialsRequest",
            "connectWithConfigurationRequest",
            "connectWithConfigurationAndCredentialsRequest",
        }:
            return rti_pb2.CallResponse(connectResponse=rti_pb2.ConnectResponse())
        if request_kind == "disconnectRequest":
            self.joined_federates.clear()
            return rti_pb2.CallResponse(disconnectResponse=rti_pb2.DisconnectResponse())
        if request_kind in {
            "createFederationExecutionWithModulesRequest",
            "createFederationExecutionWithModulesAndTimeRequest",
        }:
            payload = getattr(request, request_kind)
            self.federations.add(payload.federationName)
            if request_kind == "createFederationExecutionWithModulesAndTimeRequest":
                return rti_pb2.CallResponse(createFederationExecutionWithModulesAndTimeResponse=rti_pb2.CreateFederationExecutionWithModulesAndTimeResponse())
            return rti_pb2.CallResponse(createFederationExecutionWithModulesResponse=rti_pb2.CreateFederationExecutionWithModulesResponse())
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
            result = datatypes_pb2.JoinResult(
                federateHandle=datatypes_pb2.FederateHandle(data=str(handle).encode("ascii")),
                logicalTimeImplementationName="HLAinteger64Time",
            )
            if request_kind in {"joinFederationExecutionWithNameRequest", "joinFederationExecutionWithNameAndModulesRequest"}:
                return rti_pb2.CallResponse(joinFederationExecutionWithNameResponse=rti_pb2.JoinFederationExecutionWithNameResponse(result=result))
            return rti_pb2.CallResponse(joinFederationExecutionResponse=rti_pb2.JoinFederationExecutionResponse(result=result))
        if request_kind == "resignFederationExecutionRequest":
            action = request.resignFederationExecutionRequest.resignAction
            self._apply_resign_action(action)
            self.joined_federates.clear()
            self.joined_federate_handles.clear()
            return rti_pb2.CallResponse(resignFederationExecutionResponse=rti_pb2.ResignFederationExecutionResponse())
        if request_kind == "destroyFederationExecutionRequest":
            payload = request.destroyFederationExecutionRequest
            if self.joined_federates:
                return self._error("FederatesCurrentlyJoined", payload.federationName)
            self.federations.discard(payload.federationName)
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
            self._queue_service_report("getObjectClassHandle")
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
                return self._error("NameNotFound", payload.parameterName)
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
            return rti_pb2.CallResponse(commitRegionModificationsResponse=rti_pb2.CommitRegionModificationsResponse())
        if request_kind == "deleteRegionRequest":
            region = request.deleteRegionRequest.region.data.decode("ascii")
            self.regions.pop(region, None)
            self.region_bounds.pop(region, None)
            self._remove_region_references(region)
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
            self.lookahead.CopyFrom(request.modifyLookaheadRequest.lookahead)
            return rti_pb2.CallResponse(modifyLookaheadResponse=rti_pb2.ModifyLookaheadResponse())
        if request_kind == "queryLookaheadRequest":
            return rti_pb2.CallResponse(queryLookaheadResponse=rti_pb2.QueryLookaheadResponse(result=self.lookahead))
        if request_kind == "queryGALTRequest":
            return rti_pb2.CallResponse(
                queryGALTResponse=rti_pb2.QueryGALTResponse(
                    result=datatypes_pb2.TimeQueryReturn(logicalTimeIsValid=True, logicalTime=self.current_time)
                )
            )
        if request_kind == "queryLITSRequest":
            return rti_pb2.CallResponse(
                queryLITSResponse=rti_pb2.QueryLITSResponse(
                    result=datatypes_pb2.TimeQueryReturn(logicalTimeIsValid=True, logicalTime=self.current_time)
                )
            )
        if request_kind == "getServiceReportingSwitchRequest":
            return rti_pb2.CallResponse(
                getServiceReportingSwitchResponse=rti_pb2.GetServiceReportingSwitchResponse(
                    result=self.service_reporting
                )
            )
        if request_kind == "setServiceReportingSwitchRequest":
            self.service_reporting = request.setServiceReportingSwitchRequest.value
            self.switch_states["serviceReporting"] = self.service_reporting
            return rti_pb2.CallResponse(setServiceReportingSwitchResponse=rti_pb2.SetServiceReportingSwitchResponse())
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
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        initiateFederateSaveWithTime=callback_pb2.InitiateFederateSaveWithTime(
                            label=payload.label,
                            time=payload.time,
                        )
                    )
                )
            else:
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(initiateFederateSave=callback_pb2.InitiateFederateSave(label=payload.label))
                )
            return rti_pb2.CallResponse(requestFederationSaveWithTimeResponse=rti_pb2.RequestFederationSaveWithTimeResponse())
        if request_kind == "federateSaveBegunRequest":
            if self.save_label is None:
                return self._error("SaveNotInitiated", "No federation save is in progress")
            self.save_status[self._current_federate_handle()] = datatypes_pb2.FEDERATE_SAVING
            return rti_pb2.CallResponse(federateSaveBegunResponse=rti_pb2.FederateSaveBegunResponse())
        if request_kind == "queryFederationSaveStatusRequest":
            self.callback_queue.append(
                callback_pb2.CallbackRequest(federationSaveStatusResponse=callback_pb2.FederationSaveStatusResponse(response=self._save_status_array()))
            )
            return rti_pb2.CallResponse(queryFederationSaveStatusResponse=rti_pb2.QueryFederationSaveStatusResponse())
        if request_kind == "federateSaveCompleteRequest":
            if self.save_label is None:
                return self._error("SaveNotInitiated", "No federation save is in progress")
            self.save_status[self._current_federate_handle()] = datatypes_pb2.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE
            if self.save_status and all(status == datatypes_pb2.FEDERATE_WAITING_FOR_FEDERATION_TO_SAVE for status in self.save_status.values()):
                self.saved_snapshots[self.save_label] = self._snapshot()
                self.saved_labels.add(self.save_label)
                self.save_label = None
                self.save_status = {}
                self.callback_queue.append(callback_pb2.CallbackRequest(federationSaved=callback_pb2.FederationSaved()))
            return rti_pb2.CallResponse(federateSaveCompleteResponse=rti_pb2.FederateSaveCompleteResponse())
        if request_kind == "federateSaveNotCompleteRequest":
            self.save_label = None
            self.save_status = {}
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    federationNotSaved=callback_pb2.FederationNotSaved(reason=datatypes_pb2.FEDERATE_REPORTED_FAILURE_DURING_SAVE)
                )
            )
            return rti_pb2.CallResponse(federateSaveNotCompleteResponse=rti_pb2.FederateSaveNotCompleteResponse())
        if request_kind == "abortFederationSaveRequest":
            self.save_label = None
            self.save_status = {}
            self.callback_queue.append(callback_pb2.CallbackRequest(federationNotSaved=callback_pb2.FederationNotSaved(reason=datatypes_pb2.SAVE_ABORTED)))
            return rti_pb2.CallResponse(abortFederationSaveResponse=rti_pb2.AbortFederationSaveResponse())
        if request_kind == "requestFederationRestoreRequest":
            label = request.requestFederationRestoreRequest.label
            if label not in self.saved_labels:
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        requestFederationRestoreFailed=callback_pb2.RequestFederationRestoreFailed(label=label)
                    )
                )
                return rti_pb2.CallResponse(requestFederationRestoreResponse=rti_pb2.RequestFederationRestoreResponse())
            self.restore_label = label
            self.restore_status = {handle: datatypes_pb2.FEDERATE_RESTORE_REQUEST_PENDING for handle in self._joined_handle_values()}
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    requestFederationRestoreSucceeded=callback_pb2.RequestFederationRestoreSucceeded(label=label)
                )
            )
            self.callback_queue.append(callback_pb2.CallbackRequest(federationRestoreBegun=callback_pb2.FederationRestoreBegun()))
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    initiateFederateRestore=callback_pb2.InitiateFederateRestore(
                        label=label,
                        federateName=self.joined_federate_handles.get(self._current_federate_handle(), "fedpro-federate"),
                        postRestoreFederateHandle=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle()),
                    )
                )
            )
            return rti_pb2.CallResponse(requestFederationRestoreResponse=rti_pb2.RequestFederationRestoreResponse())
        if request_kind == "queryFederationRestoreStatusRequest":
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    federationRestoreStatusResponse=callback_pb2.FederationRestoreStatusResponse(response=self._restore_status_array())
                )
            )
            return rti_pb2.CallResponse(queryFederationRestoreStatusResponse=rti_pb2.QueryFederationRestoreStatusResponse())
        if request_kind == "federateRestoreCompleteRequest":
            if self.restore_label is None:
                return self._error("RestoreNotRequested", "No federation restore is in progress")
            self.restore_status[self._current_federate_handle()] = datatypes_pb2.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE
            if self.restore_status and all(status == datatypes_pb2.FEDERATE_WAITING_FOR_FEDERATION_TO_RESTORE for status in self.restore_status.values()):
                self._restore_snapshot(self.restore_label)
                self.restore_label = None
                self.restore_status = {}
                self.callback_queue.append(callback_pb2.CallbackRequest(federationRestored=callback_pb2.FederationRestored()))
            return rti_pb2.CallResponse(federateRestoreCompleteResponse=rti_pb2.FederateRestoreCompleteResponse())
        if request_kind == "federateRestoreNotCompleteRequest":
            self.restore_label = None
            self.restore_status = {}
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    federationNotRestored=callback_pb2.FederationNotRestored(reason=datatypes_pb2.FEDERATE_REPORTED_FAILURE_DURING_RESTORE)
                )
            )
            return rti_pb2.CallResponse(federateRestoreNotCompleteResponse=rti_pb2.FederateRestoreNotCompleteResponse())
        if request_kind == "abortFederationRestoreRequest":
            self.restore_label = None
            self.restore_status = {}
            self.callback_queue.append(
                callback_pb2.CallbackRequest(federationNotRestored=callback_pb2.FederationNotRestored(reason=datatypes_pb2.RESTORE_ABORTED))
            )
            return rti_pb2.CallResponse(abortFederationRestoreResponse=rti_pb2.AbortFederationRestoreResponse())
        if request_kind == "changeDefaultAttributeTransportationTypeRequest":
            payload = request.changeDefaultAttributeTransportationTypeRequest
            object_class = payload.objectClass.data.decode("ascii")
            transportation = payload.transportationType.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.default_attribute_transportation[(object_class, attribute.data.decode("ascii"))] = transportation
            return rti_pb2.CallResponse(changeDefaultAttributeTransportationTypeResponse=rti_pb2.ChangeDefaultAttributeTransportationTypeResponse())
        if request_kind == "changeDefaultAttributeOrderTypeRequest":
            payload = request.changeDefaultAttributeOrderTypeRequest
            object_class = payload.theObjectClass.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.default_attribute_order[(object_class, attribute.data.decode("ascii"))] = payload.orderType
            return rti_pb2.CallResponse(changeDefaultAttributeOrderTypeResponse=rti_pb2.ChangeDefaultAttributeOrderTypeResponse())
        if request_kind == "publishObjectClassAttributesRequest":
            payload = request.publishObjectClassAttributesRequest
            object_class = payload.objectClass.data.decode("ascii")
            self.published_object_attributes.setdefault(object_class, set()).update(
                attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle
            )
            return rti_pb2.CallResponse(publishObjectClassAttributesResponse=rti_pb2.PublishObjectClassAttributesResponse())
        if request_kind == "subscribeObjectClassAttributesRequest":
            payload = request.subscribeObjectClassAttributesRequest
            object_class = payload.objectClass.data.decode("ascii")
            self.subscribed_object_attributes.setdefault(object_class, set()).update(
                attribute.data.decode("ascii") for attribute in payload.attributes.attributeHandle
            )
            for object_instance, record in self.object_instances.items():
                if record["objectClass"] == object_class:
                    self._queue_discovery(object_instance, object_class, record["name"])
            return rti_pb2.CallResponse(subscribeObjectClassAttributesResponse=rti_pb2.SubscribeObjectClassAttributesResponse())
        if request_kind == "subscribeObjectClassAttributesWithRegionsRequest":
            payload = request.subscribeObjectClassAttributesWithRegionsRequest
            object_class = payload.objectClass.data.decode("ascii")
            region_map = self.subscribed_object_regions.setdefault(object_class, {})
            for attribute, regions in self._attribute_region_pairs(payload.attributesAndRegions):
                self.subscribed_object_attributes.setdefault(object_class, set()).add(attribute)
                region_map.setdefault(attribute, set()).update(regions)
            for object_instance, record in self.object_instances.items():
                if record["objectClass"] == object_class and self._reflectable_attribute_names(object_instance, object_class):
                    self._queue_discovery(object_instance, object_class, record["name"])
            return rti_pb2.CallResponse(
                subscribeObjectClassAttributesWithRegionsResponse=rti_pb2.SubscribeObjectClassAttributesWithRegionsResponse()
            )
        if request_kind == "unsubscribeObjectClassAttributesWithRegionsRequest":
            payload = request.unsubscribeObjectClassAttributesWithRegionsRequest
            object_class = payload.objectClass.data.decode("ascii")
            region_map = self.subscribed_object_regions.setdefault(object_class, {})
            for attribute, regions in self._attribute_region_pairs(payload.attributesAndRegions):
                current = region_map.setdefault(attribute, set())
                current.difference_update(regions)
                if not current:
                    region_map.pop(attribute, None)
                    self.subscribed_object_attributes.get(object_class, set()).discard(attribute)
            return rti_pb2.CallResponse(
                unsubscribeObjectClassAttributesWithRegionsResponse=rti_pb2.UnsubscribeObjectClassAttributesWithRegionsResponse()
            )
        if request_kind == "publishInteractionClassRequest":
            interaction_class = request.publishInteractionClassRequest.interactionClass.data.decode("ascii")
            self.published_interactions.add(interaction_class)
            return rti_pb2.CallResponse(publishInteractionClassResponse=rti_pb2.PublishInteractionClassResponse())
        if request_kind == "subscribeInteractionClassRequest":
            interaction_class = request.subscribeInteractionClassRequest.interactionClass.data.decode("ascii")
            self.subscribed_interactions.add(interaction_class)
            return rti_pb2.CallResponse(subscribeInteractionClassResponse=rti_pb2.SubscribeInteractionClassResponse())
        if request_kind == "subscribeInteractionClassWithRegionsRequest":
            payload = request.subscribeInteractionClassWithRegionsRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            self.subscribed_interactions.add(interaction_class)
            self.subscribed_interaction_regions.setdefault(interaction_class, set()).update(
                region.data.decode("ascii") for region in payload.regions.regionHandle
            )
            return rti_pb2.CallResponse(subscribeInteractionClassWithRegionsResponse=rti_pb2.SubscribeInteractionClassWithRegionsResponse())
        if request_kind == "unsubscribeInteractionClassWithRegionsRequest":
            payload = request.unsubscribeInteractionClassWithRegionsRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            regions = self.subscribed_interaction_regions.setdefault(interaction_class, set())
            regions.difference_update(region.data.decode("ascii") for region in payload.regions.regionHandle)
            if not regions:
                self.subscribed_interaction_regions.pop(interaction_class, None)
                self.subscribed_interactions.discard(interaction_class)
            return rti_pb2.CallResponse(unsubscribeInteractionClassWithRegionsResponse=rti_pb2.UnsubscribeInteractionClassWithRegionsResponse())
        if request_kind in {"registerObjectInstanceRequest", "registerObjectInstanceWithNameRequest"}:
            payload = getattr(request, request_kind)
            object_class = payload.objectClass.data.decode("ascii")
            handle = str(self.next_object_instance_handle)
            self.next_object_instance_handle += 1
            object_name = getattr(payload, "objectInstanceName", "") or f"fedpro-object-{handle}"
            self.object_instances[handle] = {"name": object_name, "objectClass": object_class}
            if object_class in self.subscribed_object_attributes:
                self._queue_discovery(handle, object_class, object_name)
            response_kind = (
                "registerObjectInstanceWithNameResponse"
                if request_kind == "registerObjectInstanceWithNameRequest"
                else "registerObjectInstanceResponse"
            )
            response_type = getattr(rti_pb2, response_kind[0].upper() + response_kind[1:])
            return rti_pb2.CallResponse(**{response_kind: response_type(result=_handle(datatypes_pb2.ObjectInstanceHandle, handle))})
        if request_kind == "associateRegionsForUpdatesRequest":
            payload = request.associateRegionsForUpdatesRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            update_regions = self.object_update_regions.setdefault(object_instance, {})
            for attribute, regions in self._attribute_region_pairs(payload.attributesAndRegions):
                update_regions.setdefault(attribute, set()).update(regions)
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
            return rti_pb2.CallResponse(unassociateRegionsForUpdatesResponse=rti_pb2.UnassociateRegionsForUpdatesResponse())
        if request_kind == "updateAttributeValuesRequest":
            payload = request.updateAttributeValuesRequest
            self.updates_sent += 1
            self.object_instances_updated += 1
            object_instance = payload.objectInstance.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            object_class = record["objectClass"]
            subscribed = self.subscribed_object_attributes.get(object_class, set())
            reflected = [
                item
                for item in payload.attributeValues.attributeHandleValue
                if item.attributeHandle.data.decode("ascii") in subscribed
                and self._attribute_regions_overlap(object_instance, object_class, item.attributeHandle.data.decode("ascii"))
            ]
            if reflected:
                values = datatypes_pb2.AttributeHandleValueMap()
                for item in reflected:
                    row = values.attributeHandleValue.add()
                    row.attributeHandle.CopyFrom(item.attributeHandle)
                    row.value = item.value
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        reflectAttributeValues=callback_pb2.ReflectAttributeValues(
                            objectInstance=payload.objectInstance,
                            attributeValues=values,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                            optionalSentRegions=self._conveyed_regions_for(object_instance, reflected),
                        )
                    )
                )
                self.reflections_received += 1
                self.object_instances_reflected += 1
            return rti_pb2.CallResponse(updateAttributeValuesResponse=rti_pb2.UpdateAttributeValuesResponse())
        if request_kind == "updateAttributeValuesWithTimeRequest":
            payload = request.updateAttributeValuesWithTimeRequest
            self.updates_sent += 1
            self.object_instances_updated += 1
            object_instance = payload.objectInstance.data.decode("ascii")
            record = self.object_instances.get(object_instance)
            if record is None:
                return self._error("ObjectInstanceNotKnown", object_instance)
            object_class = record["objectClass"]
            subscribed = self.subscribed_object_attributes.get(object_class, set())
            reflected = [
                item
                for item in payload.attributeValues.attributeHandleValue
                if item.attributeHandle.data.decode("ascii") in subscribed
                and self._attribute_regions_overlap(object_instance, object_class, item.attributeHandle.data.decode("ascii"))
            ]
            retraction_handle = self._next_retraction_handle()
            if reflected:
                values = datatypes_pb2.AttributeHandleValueMap()
                for item in reflected:
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
                            producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                            optionalSentRegions=self._conveyed_regions_for(object_instance, reflected),
                            time=payload.time,
                            sentOrderType=datatypes_pb2.TIMESTAMP,
                            receivedOrderType=datatypes_pb2.TIMESTAMP,
                            optionalRetraction=_handle(datatypes_pb2.MessageRetractionHandle, retraction_handle),
                        )
                    ),
                )
            return rti_pb2.CallResponse(
                updateAttributeValuesWithTimeResponse=rti_pb2.UpdateAttributeValuesWithTimeResponse(
                    result=self._message_retraction_return(retraction_handle)
                )
            )
        if request_kind == "sendInteractionRequest":
            payload = request.sendInteractionRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata"]:
                self._queue_mim_report()
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestPublications"]:
                self._queue_object_publication_report()
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestSubscriptions"]:
                self._queue_object_subscription_report()
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestInteractionsSent"]:
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsSent",
                    "HLAinteractionsSent",
                    self.interactions_sent,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestInteractionsReceived"]:
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsReceived",
                    "HLAinteractionsReceived",
                    self.interactions_received,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestUpdatesSent"]:
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportUpdatesSent",
                    "HLAupdatesSent",
                    self.updates_sent,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestReflectionsReceived"]:
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportReflectionsReceived",
                    "HLAreflectionsReceived",
                    self.reflections_received,
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
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesUpdated",
                    "HLAobjectInstanceCounts",
                    self.object_instances_updated,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstancesReflected"]:
                self._queue_activity_count_report(
                    "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesReflected",
                    "HLAobjectInstanceCounts",
                    self.object_instances_reflected,
                )
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if interaction_class == self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLArequest.HLArequestObjectInstanceInformation"]:
                self._queue_object_instance_information_report(payload.parameterValues)
                return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
            if self._interaction_subscriber_matches(interaction_class, ()):
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        receiveInteraction=callback_pb2.ReceiveInteraction(
                            interactionClass=payload.interactionClass,
                            parameterValues=payload.parameterValues,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                        )
                    )
                )
                self.interactions_received += 1
            self.interactions_sent += 1
            return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
        if request_kind == "sendInteractionWithRegionsRequest":
            payload = request.sendInteractionWithRegionsRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            source_regions = tuple(region.data.decode("ascii") for region in payload.regions.regionHandle)
            if self._interaction_subscriber_matches(interaction_class, source_regions):
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        receiveInteraction=callback_pb2.ReceiveInteraction(
                            interactionClass=payload.interactionClass,
                            parameterValues=payload.parameterValues,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                            optionalSentRegions=self._conveyed_regions_from(source_regions),
                        )
                    )
                )
                self.interactions_received += 1
            self.interactions_sent += 1
            return rti_pb2.CallResponse(sendInteractionWithRegionsResponse=rti_pb2.SendInteractionWithRegionsResponse())
        if request_kind == "sendInteractionWithTimeRequest":
            payload = request.sendInteractionWithTimeRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            retraction_handle = self._next_retraction_handle()
            if self._interaction_subscriber_matches(interaction_class, ()):
                self._queue_tso_callback(
                    retraction_handle,
                    payload.time,
                    callback_pb2.CallbackRequest(
                        receiveInteractionWithTime=callback_pb2.ReceiveInteractionWithTime(
                            interactionClass=payload.interactionClass,
                            parameterValues=payload.parameterValues,
                            userSuppliedTag=payload.userSuppliedTag,
                            transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                            producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                            time=payload.time,
                            sentOrderType=datatypes_pb2.TIMESTAMP,
                            receivedOrderType=datatypes_pb2.TIMESTAMP,
                            optionalRetraction=_handle(datatypes_pb2.MessageRetractionHandle, retraction_handle),
                        )
                    ),
                )
                self.interactions_received += 1
            self.interactions_sent += 1
            return rti_pb2.CallResponse(
                sendInteractionWithTimeResponse=rti_pb2.SendInteractionWithTimeResponse(
                    result=self._message_retraction_return(retraction_handle)
                )
            )
        if request_kind == "retractRequest":
            handle = request.retractRequest.retraction.data.decode("ascii")
            if handle in self.queued_tso_callbacks:
                del self.queued_tso_callbacks[handle]
                return rti_pb2.CallResponse(retractResponse=rti_pb2.RetractResponse())
            if handle in self.delivered_retractions:
                return self._error("MessageCanNoLongerBeRetracted", handle)
            return self._error("InvalidMessageRetractionHandle", handle)
        if request_kind == "isAttributeOwnedByFederateRequest":
            payload = request.isAttributeOwnedByFederateRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            attribute = payload.attribute.data.decode("ascii")
            return rti_pb2.CallResponse(
                isAttributeOwnedByFederateResponse=rti_pb2.IsAttributeOwnedByFederateResponse(
                    result=(object_instance, attribute) not in self.unowned_attributes
                )
            )
        if request_kind == "unconditionalAttributeOwnershipDivestitureRequest":
            payload = request.unconditionalAttributeOwnershipDivestitureRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.unowned_attributes.add((object_instance, attribute.data.decode("ascii")))
            return rti_pb2.CallResponse(unconditionalAttributeOwnershipDivestitureResponse=rti_pb2.UnconditionalAttributeOwnershipDivestitureResponse())
        if request_kind == "queryAttributeOwnershipRequest":
            payload = request.queryAttributeOwnershipRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            unowned = []
            owned = []
            for attribute in payload.attributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                if (object_instance, attribute_value) in self.unowned_attributes:
                    unowned.append(attribute_value)
                else:
                    owned.append(attribute_value)
            if unowned:
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        attributeIsNotOwned=callback_pb2.AttributeIsNotOwned(
                            objectInstance=payload.objectInstance,
                            attributes=_attribute_set(tuple(unowned)),
                        )
                    )
                )
            if owned:
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        informAttributeOwnership=callback_pb2.InformAttributeOwnership(
                            objectInstance=payload.objectInstance,
                            attributes=_attribute_set(tuple(owned)),
                            federate=_handle(datatypes_pb2.FederateHandle, self._current_federate_handle()),
                        )
                    )
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
                    available.append(attribute_value)
                else:
                    unavailable.append(attribute_value)
            if available:
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        attributeOwnershipAcquisitionNotification=callback_pb2.AttributeOwnershipAcquisitionNotification(
                            objectInstance=payload.objectInstance,
                            securedAttributes=_attribute_set(tuple(available)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    )
                )
            if unavailable:
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        attributeOwnershipUnavailable=callback_pb2.AttributeOwnershipUnavailable(
                            objectInstance=payload.objectInstance,
                            attributes=_attribute_set(tuple(unavailable)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    )
                )
            return rti_pb2.CallResponse(attributeOwnershipAcquisitionIfAvailableResponse=rti_pb2.AttributeOwnershipAcquisitionIfAvailableResponse())
        if request_kind == "negotiatedAttributeOwnershipDivestitureRequest":
            payload = request.negotiatedAttributeOwnershipDivestitureRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.offered_attributes.add((object_instance, attribute.data.decode("ascii")))
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    requestAttributeOwnershipAssumption=callback_pb2.RequestAttributeOwnershipAssumption(
                        objectInstance=payload.objectInstance,
                        offeredAttributes=payload.attributes,
                        userSuppliedTag=payload.userSuppliedTag,
                    )
                )
            )
            return rti_pb2.CallResponse(negotiatedAttributeOwnershipDivestitureResponse=rti_pb2.NegotiatedAttributeOwnershipDivestitureResponse())
        if request_kind == "attributeOwnershipAcquisitionRequest":
            payload = request.attributeOwnershipAcquisitionRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            offered = []
            requested = []
            for attribute in payload.desiredAttributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                key = (object_instance, attribute_value)
                self.pending_attribute_acquisitions[key] = payload.userSuppliedTag
                if key in self.offered_attributes:
                    offered.append(attribute_value)
                else:
                    requested.append(attribute_value)
            if offered:
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        requestDivestitureConfirmation=callback_pb2.RequestDivestitureConfirmation(
                            objectInstance=payload.objectInstance,
                            releasedAttributes=_attribute_set(tuple(offered)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    )
                )
            if requested:
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        requestAttributeOwnershipRelease=callback_pb2.RequestAttributeOwnershipRelease(
                            objectInstance=payload.objectInstance,
                            candidateAttributes=_attribute_set(tuple(requested)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    )
                )
            return rti_pb2.CallResponse(attributeOwnershipAcquisitionResponse=rti_pb2.AttributeOwnershipAcquisitionResponse())
        if request_kind == "confirmDivestitureRequest":
            payload = request.confirmDivestitureRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            confirmed = []
            for attribute in payload.confirmedAttributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                key = (object_instance, attribute_value)
                self.offered_attributes.discard(key)
                self.unowned_attributes.discard(key)
                self.pending_attribute_acquisitions.pop(key, None)
                confirmed.append(attribute_value)
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    attributeOwnershipAcquisitionNotification=callback_pb2.AttributeOwnershipAcquisitionNotification(
                        objectInstance=payload.objectInstance,
                        securedAttributes=_attribute_set(tuple(confirmed)),
                        userSuppliedTag=payload.userSuppliedTag,
                    )
                )
            )
            return rti_pb2.CallResponse(confirmDivestitureResponse=rti_pb2.ConfirmDivestitureResponse())
        if request_kind == "attributeOwnershipDivestitureIfWantedRequest":
            payload = request.attributeOwnershipDivestitureIfWantedRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            divested = []
            for attribute in payload.attributes.attributeHandle:
                attribute_value = attribute.data.decode("ascii")
                key = (object_instance, attribute_value)
                if key in self.pending_attribute_acquisitions:
                    self.pending_attribute_acquisitions.pop(key, None)
                    self.unowned_attributes.discard(key)
                    divested.append(attribute_value)
            if divested:
                self.callback_queue.append(
                    callback_pb2.CallbackRequest(
                        attributeOwnershipAcquisitionNotification=callback_pb2.AttributeOwnershipAcquisitionNotification(
                            objectInstance=payload.objectInstance,
                            securedAttributes=_attribute_set(tuple(divested)),
                            userSuppliedTag=payload.userSuppliedTag,
                        )
                    )
                )
            return rti_pb2.CallResponse(
                attributeOwnershipDivestitureIfWantedResponse=rti_pb2.AttributeOwnershipDivestitureIfWantedResponse(
                    result=_attribute_set(tuple(divested))
                )
            )
        if request_kind == "attributeOwnershipReleaseDeniedRequest":
            payload = request.attributeOwnershipReleaseDeniedRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.pending_attribute_acquisitions.pop((object_instance, attribute.data.decode("ascii")), None)
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    attributeOwnershipUnavailable=callback_pb2.AttributeOwnershipUnavailable(
                        objectInstance=payload.objectInstance,
                        attributes=payload.attributes,
                        userSuppliedTag=payload.userSuppliedTag,
                    )
                )
            )
            return rti_pb2.CallResponse(attributeOwnershipReleaseDeniedResponse=rti_pb2.AttributeOwnershipReleaseDeniedResponse())
        if request_kind == "cancelAttributeOwnershipAcquisitionRequest":
            payload = request.cancelAttributeOwnershipAcquisitionRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            for attribute in payload.attributes.attributeHandle:
                self.pending_attribute_acquisitions.pop((object_instance, attribute.data.decode("ascii")), None)
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    confirmAttributeOwnershipAcquisitionCancellation=callback_pb2.ConfirmAttributeOwnershipAcquisitionCancellation(
                        objectInstance=payload.objectInstance,
                        attributes=payload.attributes,
                    )
                )
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
            self.time_regulating = True
            self.lookahead.CopyFrom(request.enableTimeRegulationRequest.lookahead)
            self.callback_queue.append(callback_pb2.CallbackRequest(timeRegulationEnabled=callback_pb2.TimeRegulationEnabled(time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:0"))))
            return rti_pb2.CallResponse(enableTimeRegulationResponse=rti_pb2.EnableTimeRegulationResponse())
        if request_kind == "enableTimeConstrainedRequest":
            self.time_constrained = True
            self.callback_queue.append(callback_pb2.CallbackRequest(timeConstrainedEnabled=callback_pb2.TimeConstrainedEnabled(time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:0"))))
            return rti_pb2.CallResponse(enableTimeConstrainedResponse=rti_pb2.EnableTimeConstrainedResponse())
        if request_kind == "disableTimeRegulationRequest":
            self.time_regulating = False
            return rti_pb2.CallResponse(disableTimeRegulationResponse=rti_pb2.DisableTimeRegulationResponse())
        if request_kind == "disableTimeConstrainedRequest":
            self.time_constrained = False
            return rti_pb2.CallResponse(disableTimeConstrainedResponse=rti_pb2.DisableTimeConstrainedResponse())
        if request_kind == "enableAsynchronousDeliveryRequest":
            self.asynchronous_delivery_enabled = True
            return rti_pb2.CallResponse(enableAsynchronousDeliveryResponse=rti_pb2.EnableAsynchronousDeliveryResponse())
        if request_kind == "disableAsynchronousDeliveryRequest":
            self.asynchronous_delivery_enabled = False
            return rti_pb2.CallResponse(disableAsynchronousDeliveryResponse=rti_pb2.DisableAsynchronousDeliveryResponse())
        if request_kind == "timeAdvanceRequestRequest":
            self._grant_time(request.timeAdvanceRequestRequest.time)
            return rti_pb2.CallResponse(timeAdvanceRequestResponse=rti_pb2.TimeAdvanceRequestResponse())
        if request_kind == "timeAdvanceRequestAvailableRequest":
            self._grant_time(request.timeAdvanceRequestAvailableRequest.time)
            return rti_pb2.CallResponse(timeAdvanceRequestAvailableResponse=rti_pb2.TimeAdvanceRequestAvailableResponse())
        if request_kind == "nextMessageRequestRequest":
            self._grant_time(request.nextMessageRequestRequest.time)
            return rti_pb2.CallResponse(nextMessageRequestResponse=rti_pb2.NextMessageRequestResponse())
        if request_kind == "nextMessageRequestAvailableRequest":
            self._grant_time(request.nextMessageRequestAvailableRequest.time)
            return rti_pb2.CallResponse(nextMessageRequestAvailableResponse=rti_pb2.NextMessageRequestAvailableResponse())
        if request_kind == "flushQueueRequestRequest":
            self._grant_time(request.flushQueueRequestRequest.time)
            return rti_pb2.CallResponse(flushQueueRequestResponse=rti_pb2.FlushQueueRequestResponse())
        if request_kind == "queryLogicalTimeRequest":
            return rti_pb2.CallResponse(
                queryLogicalTimeResponse=rti_pb2.QueryLogicalTimeResponse(
                    result=self.current_time,
                )
            )
        return self._error("RTIinternalError", f"Unsupported 2025 test call: {request_kind}")

    def EvokeCallback(self, request, context):  # noqa: N802 - grpc generated naming
        if self.callback_queue:
            return self.callback_queue.pop(0)
        return _callback_request()

    @staticmethod
    def _error(name: str, details: str) -> rti_pb2.CallResponse:
        return rti_pb2.CallResponse(
            exceptionData=datatypes_pb2.ExceptionData(
                exceptionName=name,
                details=details,
            )
        )

    def _queue_discovery(self, object_instance: str, object_class: str, object_name: str) -> None:
        self.callback_queue.append(
            callback_pb2.CallbackRequest(
                discoverObjectInstance=callback_pb2.DiscoverObjectInstance(
                    objectInstance=_handle(datatypes_pb2.ObjectInstanceHandle, object_instance),
                    objectClass=_handle(datatypes_pb2.ObjectClassHandle, object_class),
                    objectInstanceName=object_name,
                    producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                )
            )
        )

    def _queue_service_report(self, service_name: str) -> None:
        if not self.service_reporting:
            return
        interaction_class = self.interactions["HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation"]
        values = datatypes_pb2.ParameterHandleValueMap()
        for parameter_name, payload in (
            ("HLAfederate", b"1"),
            ("HLAservice", service_name.encode("ascii")),
            ("HLAserialNumber", str(self.service_report_serial).encode("ascii")),
        ):
            row = values.parameterHandleValue.add()
            row.parameterHandle.data = self.parameters[(interaction_class, parameter_name)].encode("ascii")
            row.value = payload
        self.service_report_serial += 1
        self.callback_queue.append(
            callback_pb2.CallbackRequest(
                receiveInteraction=callback_pb2.ReceiveInteraction(
                    interactionClass=_handle(datatypes_pb2.InteractionClassHandle, interaction_class),
                    parameterValues=values,
                    userSuppliedTag=b"MOM",
                    transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                    producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                )
            )
        )

    def _queue_object_publication_report(self) -> None:
        report_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication"
        ]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        publication_rows = [
            f"{object_class}:{','.join(sorted(attributes, key=int))}"
            for object_class, attributes in sorted(self.published_object_attributes.items(), key=lambda item: int(item[0]))
            if attributes
        ]
        object_classes = ",".join(row.split(":", 1)[0] for row in publication_rows)
        attribute_lists = ";".join(publication_rows)
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": b"1",
                "HLAnumberOfClasses": str(len(publication_rows)).encode("ascii"),
                "HLAobjectClass": object_classes.encode("ascii"),
                "HLAattributeList": attribute_lists.encode("ascii"),
            },
        )

    def _queue_object_subscription_report(self) -> None:
        report_class = self.interactions[
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription"
        ]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        subscription_rows = [
            f"{object_class}:{','.join(sorted(attributes, key=int))}"
            for object_class, attributes in sorted(self.subscribed_object_attributes.items(), key=lambda item: int(item[0]))
            if attributes
        ]
        object_classes = ",".join(row.split(":", 1)[0] for row in subscription_rows)
        attribute_lists = ";".join(subscription_rows)
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": b"1",
                "HLAnumberOfClasses": str(len(subscription_rows)).encode("ascii"),
                "HLAobjectClass": object_classes.encode("ascii"),
                "HLAactive": b"HLAtrue",
                "HLAmaxUpdateRate": b"",
                "HLAattributeList": attribute_lists.encode("ascii"),
            },
        )

    def _queue_activity_count_report(self, report_name: str, count_parameter: str, count: int) -> None:
        report_class = self.interactions[report_name]
        if not self._interaction_subscriber_matches(report_class, ()):
            return
        self._queue_mom_report(
            report_class,
            {
                "HLAfederate": b"1",
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
        requested_object = ""
        requested_parameter = self.parameters[(request_class, "HLAobjectInstance")]
        for item in parameters.parameterHandleValue:
            if item.parameterHandle.data.decode("ascii") == requested_parameter:
                requested_object = item.value.decode("ascii")
                break
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
                "HLAfederate": b"1",
                "HLAobjectInstance": ";".join(row["objectInstance"] for row in rows).encode("ascii"),
                "HLAobjectClass": ";".join(row["objectClass"] for row in rows).encode("ascii"),
                "HLAobjectInstanceName": ";".join(row["objectInstanceName"] for row in rows).encode("ascii"),
                "HLAattributeList": ";".join(row["attributeList"] for row in rows).encode("ascii"),
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

    def _queue_mom_report(self, report_class: str, parameter_values: dict[str, bytes]) -> None:
        values = datatypes_pb2.ParameterHandleValueMap()
        for parameter_name, payload in parameter_values.items():
            row = values.parameterHandleValue.add()
            row.parameterHandle.data = self.parameters[(report_class, parameter_name)].encode("ascii")
            row.value = payload
        self.callback_queue.append(
            callback_pb2.CallbackRequest(
                receiveInteraction=callback_pb2.ReceiveInteraction(
                    interactionClass=_handle(datatypes_pb2.InteractionClassHandle, report_class),
                    parameterValues=values,
                    userSuppliedTag=b"MOM",
                    transportationType=_handle(datatypes_pb2.TransportationTypeHandle, "1"),
                    producingFederate=_handle(datatypes_pb2.FederateHandle, "1"),
                )
            )
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
    ) -> None:
        self.queued_tso_callbacks[retraction_handle] = (_logical_time_value(time), callback)

    def _deliver_due_tso_callbacks(self, time: datatypes_pb2.LogicalTime) -> None:
        requested = _logical_time_value(time)
        due = [
            (time_value, int(handle), handle, callback)
            for handle, (time_value, callback) in self.queued_tso_callbacks.items()
            if time_value <= requested
        ]
        for _, _, handle, callback in sorted(due):
            if callback.WhichOneof("callbackRequest") == "reflectAttributeValuesWithTime":
                self.reflections_received += 1
                self.object_instances_reflected += 1
            self.callback_queue.append(callback)
            self.delivered_retractions.add(handle)
            del self.queued_tso_callbacks[handle]

    def _grant_time(self, time: datatypes_pb2.LogicalTime) -> None:
        self._deliver_due_tso_callbacks(time)
        self.current_time.CopyFrom(time)
        self.callback_queue.append(callback_pb2.CallbackRequest(timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=time)))

    def _joined_handle_values(self) -> tuple[str, ...]:
        if self.joined_federate_handles:
            return tuple(sorted(self.joined_federate_handles, key=int))
        return ("1",)

    def _current_federate_handle(self) -> str:
        return self._joined_handle_values()[0]

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
                    self.unowned_attributes.add((object_instance, attribute))
        if action in {
            datatypes_pb2.DELETE_OBJECTS,
            datatypes_pb2.DELETE_OBJECTS_THEN_DIVEST,
            datatypes_pb2.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            self.object_instances.clear()
            self.object_update_regions.clear()
            self.unowned_attributes.clear()
            self.offered_attributes.clear()
        if action in {
            datatypes_pb2.CANCEL_PENDING_OWNERSHIP_ACQUISITIONS,
            datatypes_pb2.CANCEL_THEN_DELETE_THEN_DIVEST,
        }:
            self.pending_attribute_acquisitions.clear()

    def _snapshot(self) -> _FederationSnapshot:
        return _FederationSnapshot(
            object_instances=deepcopy(self.object_instances),
            unowned_attributes=set(self.unowned_attributes),
            current_time=datatypes_pb2.LogicalTime(data=self.current_time.data),
            next_object_instance_handle=self.next_object_instance_handle,
            object_update_regions=deepcopy(self.object_update_regions),
        )

    def _restore_snapshot(self, label: str | None) -> None:
        if label is None:
            return
        snapshot = self.saved_snapshots.get(label)
        if snapshot is None:
            return
        self.object_instances = deepcopy(snapshot.object_instances)
        self.unowned_attributes = set(snapshot.unowned_attributes)
        self.current_time.CopyFrom(snapshot.current_time)
        self.next_object_instance_handle = snapshot.next_object_instance_handle
        self.object_update_regions = deepcopy(snapshot.object_update_regions)
        self.queued_tso_callbacks.clear()
        self.delivered_retractions.clear()

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

    def _interaction_subscriber_matches(self, interaction_class: str, source_regions: tuple[str, ...]) -> bool:
        if interaction_class not in self.subscribed_interactions:
            return False
        target_regions = self.subscribed_interaction_regions.get(interaction_class, set())
        if not target_regions:
            return True
        if not source_regions:
            return False
        return any(self._regions_overlap(source_region, target_region) for source_region in source_regions for target_region in target_regions)

    def _reflectable_attribute_names(self, object_instance: str, object_class: str) -> set[str]:
        return {
            attribute
            for attribute in self.subscribed_object_attributes.get(object_class, set())
            if self._attribute_regions_overlap(object_instance, object_class, attribute)
        }

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

    def _remove_region_references(self, region: str) -> None:
        for object_class, attribute_regions in self.subscribed_object_regions.items():
            for attribute, regions in tuple(attribute_regions.items()):
                regions.discard(region)
                if not regions:
                    attribute_regions.pop(attribute, None)
                    self.subscribed_object_attributes.get(object_class, set()).discard(attribute)
        for update_regions in self.object_update_regions.values():
            for attribute, regions in tuple(update_regions.items()):
                regions.discard(region)
                if not regions:
                    update_regions.pop(attribute, None)
        for interaction_class, regions in tuple(self.subscribed_interaction_regions.items()):
            regions.discard(region)
            if not regions:
                self.subscribed_interaction_regions.pop(interaction_class, None)
                self.subscribed_interactions.discard(interaction_class)


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
