"""Transport-hosted IEEE 1516.1-2025 RTI server for the gRPC wire path."""

from __future__ import annotations

from concurrent import futures
from dataclasses import dataclass

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
        self.next_federate_handle = 1
        self.next_object_instance_handle = 1000
        self.next_region_handle = 700
        self.object_classes = {"HLAobjectRoot.RouteTarget": "100", "HLAobjectRoot.Target": "101"}
        self.object_class_names = {value: key for key, value in self.object_classes.items()}
        self.attributes = {("100", "Position"): "200", ("101", "Position"): "201"}
        self.interactions = {
            "HLAinteractionRoot.TrackReport": "400",
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportServiceInvocation": "401",
        }
        self.interaction_names = {value: key for key, value in self.interactions.items()}
        self.parameters = {
            ("400", "TrackId"): "500",
            ("401", "HLAfederate"): "501",
            ("401", "HLAservice"): "502",
            ("401", "HLAserialNumber"): "503",
        }
        self.dimensions = {"RoutingSpace": "300"}
        self.transportations = {"HLAreliable": "1", "HLAbestEffort": "2"}
        self.object_instances: dict[str, dict[str, str]] = {}
        self.published_object_attributes: dict[str, set[str]] = {}
        self.subscribed_object_attributes: dict[str, set[str]] = {}
        self.subscribed_object_regions: dict[str, dict[str, set[str]]] = {}
        self.object_update_regions: dict[str, dict[str, set[str]]] = {}
        self.regions: dict[str, set[str]] = {}
        self.region_bounds: dict[str, dict[str, tuple[int, int]]] = {}
        self.published_interactions: set[str] = set()
        self.subscribed_interactions: set[str] = set()
        self.unowned_attributes: set[tuple[str, str]] = set()
        self.default_attribute_transportation: dict[tuple[str, str], str] = {}
        self.default_attribute_order: dict[tuple[str, str], int] = {}
        self.service_reporting = False
        self.service_report_serial = 1
        self.next_retraction_handle = 1
        self.queued_tso_callbacks: dict[str, tuple[float, callback_pb2.CallbackRequest]] = {}
        self.delivered_retractions: set[str] = set()
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
            result = datatypes_pb2.JoinResult(
                federateHandle=datatypes_pb2.FederateHandle(data=str(handle).encode("ascii")),
                logicalTimeImplementationName="HLAinteger64Time",
            )
            if request_kind in {"joinFederationExecutionWithNameRequest", "joinFederationExecutionWithNameAndModulesRequest"}:
                return rti_pb2.CallResponse(joinFederationExecutionWithNameResponse=rti_pb2.JoinFederationExecutionWithNameResponse(result=result))
            return rti_pb2.CallResponse(joinFederationExecutionResponse=rti_pb2.JoinFederationExecutionResponse(result=result))
        if request_kind == "resignFederationExecutionRequest":
            self.joined_federates.clear()
            return rti_pb2.CallResponse(resignFederationExecutionResponse=rti_pb2.ResignFederationExecutionResponse())
        if request_kind == "destroyFederationExecutionRequest":
            payload = request.destroyFederationExecutionRequest
            if self.joined_federates:
                return self._error("FederatesCurrentlyJoined", payload.federationName)
            self.federations.discard(payload.federationName)
            return rti_pb2.CallResponse(destroyFederationExecutionResponse=rti_pb2.DestroyFederationExecutionResponse())
        if request_kind == "getFederateHandleRequest":
            return rti_pb2.CallResponse(getFederateHandleResponse=rti_pb2.GetFederateHandleResponse(result=datatypes_pb2.FederateHandle(data=b"42")))
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
            names = {value: key for (class_handle, key), value in self.parameters.items() if class_handle == interaction_class}
            return rti_pb2.CallResponse(getParameterNameResponse=rti_pb2.GetParameterNameResponse(result=names.get(parameter, "")))
        if request_kind == "getDimensionHandleRequest":
            name = request.getDimensionHandleRequest.dimensionName
            try:
                handle = self.dimensions[name]
            except KeyError:
                return self._error("NameNotFound", name)
            return rti_pb2.CallResponse(getDimensionHandleResponse=rti_pb2.GetDimensionHandleResponse(result=_handle(datatypes_pb2.DimensionHandle, handle)))
        if request_kind == "getAvailableDimensionsForObjectClassRequest":
            return rti_pb2.CallResponse(
                getAvailableDimensionsForObjectClassResponse=rti_pb2.GetAvailableDimensionsForObjectClassResponse(
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
        if request_kind == "getServiceReportingSwitchRequest":
            return rti_pb2.CallResponse(
                getServiceReportingSwitchResponse=rti_pb2.GetServiceReportingSwitchResponse(
                    result=self.service_reporting
                )
            )
        if request_kind == "setServiceReportingSwitchRequest":
            self.service_reporting = request.setServiceReportingSwitchRequest.value
            return rti_pb2.CallResponse(setServiceReportingSwitchResponse=rti_pb2.SetServiceReportingSwitchResponse())
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
        if request_kind == "publishInteractionClassRequest":
            interaction_class = request.publishInteractionClassRequest.interactionClass.data.decode("ascii")
            self.published_interactions.add(interaction_class)
            return rti_pb2.CallResponse(publishInteractionClassResponse=rti_pb2.PublishInteractionClassResponse())
        if request_kind == "subscribeInteractionClassRequest":
            interaction_class = request.subscribeInteractionClassRequest.interactionClass.data.decode("ascii")
            self.subscribed_interactions.add(interaction_class)
            return rti_pb2.CallResponse(subscribeInteractionClassResponse=rti_pb2.SubscribeInteractionClassResponse())
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
        if request_kind == "updateAttributeValuesRequest":
            payload = request.updateAttributeValuesRequest
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
            return rti_pb2.CallResponse(updateAttributeValuesResponse=rti_pb2.UpdateAttributeValuesResponse())
        if request_kind == "updateAttributeValuesWithTimeRequest":
            payload = request.updateAttributeValuesWithTimeRequest
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
            if interaction_class in self.subscribed_interactions:
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
            return rti_pb2.CallResponse(sendInteractionResponse=rti_pb2.SendInteractionResponse())
        if request_kind == "sendInteractionWithTimeRequest":
            payload = request.sendInteractionWithTimeRequest
            interaction_class = payload.interactionClass.data.decode("ascii")
            retraction_handle = self._next_retraction_handle()
            if interaction_class in self.subscribed_interactions:
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
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    attributeIsNotOwned=callback_pb2.AttributeIsNotOwned(
                        objectInstance=payload.objectInstance,
                        attributes=payload.attributes,
                    )
                )
            )
            return rti_pb2.CallResponse(queryAttributeOwnershipResponse=rti_pb2.QueryAttributeOwnershipResponse())
        if request_kind == "attributeOwnershipAcquisitionIfAvailableRequest":
            payload = request.attributeOwnershipAcquisitionIfAvailableRequest
            object_instance = payload.objectInstance.data.decode("ascii")
            for attribute in payload.desiredAttributes.attributeHandle:
                self.unowned_attributes.discard((object_instance, attribute.data.decode("ascii")))
            self.callback_queue.append(
                callback_pb2.CallbackRequest(
                    attributeOwnershipAcquisitionNotification=callback_pb2.AttributeOwnershipAcquisitionNotification(
                        objectInstance=payload.objectInstance,
                        securedAttributes=payload.desiredAttributes,
                        userSuppliedTag=payload.userSuppliedTag,
                    )
                )
            )
            return rti_pb2.CallResponse(attributeOwnershipAcquisitionIfAvailableResponse=rti_pb2.AttributeOwnershipAcquisitionIfAvailableResponse())
        if request_kind == "enableTimeRegulationRequest":
            self.callback_queue.append(callback_pb2.CallbackRequest(timeRegulationEnabled=callback_pb2.TimeRegulationEnabled(time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:0"))))
            return rti_pb2.CallResponse(enableTimeRegulationResponse=rti_pb2.EnableTimeRegulationResponse())
        if request_kind == "enableTimeConstrainedRequest":
            self.callback_queue.append(callback_pb2.CallbackRequest(timeConstrainedEnabled=callback_pb2.TimeConstrainedEnabled(time=datatypes_pb2.LogicalTime(data=b"HLAinteger64Time:0"))))
            return rti_pb2.CallResponse(enableTimeConstrainedResponse=rti_pb2.EnableTimeConstrainedResponse())
        if request_kind == "timeAdvanceRequestRequest":
            self._deliver_due_tso_callbacks(request.timeAdvanceRequestRequest.time)
            self.callback_queue.append(callback_pb2.CallbackRequest(timeAdvanceGrant=callback_pb2.TimeAdvanceGrant(time=request.timeAdvanceRequestRequest.time)))
            return rti_pb2.CallResponse(timeAdvanceRequestResponse=rti_pb2.TimeAdvanceRequestResponse())
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
            self.callback_queue.append(callback)
            self.delivered_retractions.add(handle)
            del self.queued_tso_callbacks[handle]

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
            return True
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
        for region_value in sorted(region_values):
            conveyed = result.conveyedRegions.add()
            for dimension in sorted(self.regions.get(region_value, ())):
                row = conveyed.dimensionAndRange.add()
                row.dimensionHandle.data = dimension.encode("ascii")
                lower, upper = self.region_bounds.get(region_value, {}).get(dimension, (0, 1024))
                row.rangeBounds.lower = lower
                row.rangeBounds.upper = upper
        return result


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
