"""MOM service dispatch and interaction routing for the Python RTI backend."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Protocol, cast

import hla.fom.mom as hla_mom
from hla.backends.common import UnsupportedBackendService
from hla.rti1516e.enums import ResignAction
from hla.rti1516e.exceptions import (
    InteractionClassNotDefined,
    InteractionClassNotPublished,
)
from hla.rti1516e.handles import ParameterHandle

from .mom_parameter_decoding import PythonRTIMomParameterDecodingMixin

if TYPE_CHECKING:
    from .state import FederateState, FederationState, PythonRTIConfig


class _MomActionRoutingContext(Protocol):
    config: "PythonRTIConfig"
    state: "FederateState"

    def _require_joined(self) -> "FederationState": ...

    def _target_federate_from_mom_params(self, federation: "FederationState", params: Mapping[str, bytes]) -> "FederateState": ...

    def _mom_exposure_model(self, federation: "FederationState") -> Any: ...

    def _mom_request_report_values(
        self,
        federation: "FederationState",
        request_name: str,
        report_name: str,
        params: Mapping[str, bytes],
    ) -> dict[str, Any]: ...

    def _send_mom_report(self, federation: "FederationState", report_name: str, values: Mapping[str, Any]) -> None: ...

    def _apply_mom_set_service_reporting(
        self,
        federation: "FederationState",
        target: "FederateState",
        enabled: bool,
        interaction_name: str = "",
        parameter_name: str = "HLAreportingState",
    ) -> None: ...

    def _ensure_service_report_file(self, federation: "FederationState", federate: "FederateState") -> str: ...

    def _refresh_mom_attribute_values(self, federation: "FederationState") -> None: ...

    def _svc_resignFederationExecution(self, resignAction: ResignAction) -> None: ...

    def _svc_synchronizationPointAchieved(
        self,
        synchronizationPointLabel: str,
        successIndicator: bool = True,
    ) -> Any: ...

    def _svc_federateSaveBegun(self) -> Any: ...

    def _svc_federateSaveComplete(self) -> Any: ...

    def _svc_federateSaveNotComplete(self) -> Any: ...

    def _svc_federateRestoreComplete(self) -> Any: ...

    def _svc_federateRestoreNotComplete(self) -> Any: ...

    def _svc_publishObjectClassAttributes(self, theClass: Any, attributeList: Any) -> Any: ...

    def _svc_unpublishObjectClassAttributes(self, theClass: Any, attributeList: Any) -> Any: ...

    def _svc_publishInteractionClass(self, theInteraction: Any) -> Any: ...

    def _svc_unpublishInteractionClass(self, theInteraction: Any) -> Any: ...

    def _svc_subscribeObjectClassAttributes(
        self,
        theClass: Any,
        attributeList: Any,
        *unused: Any,
    ) -> Any: ...

    def _svc_subscribeObjectClassAttributesPassively(
        self,
        theClass: Any,
        attributeList: Any,
        *unused: Any,
    ) -> Any: ...

    def _svc_unsubscribeObjectClassAttributes(self, theClass: Any, attributeList: Any) -> Any: ...

    def _svc_subscribeInteractionClass(self, theClass: Any, *unused: Any) -> Any: ...

    def _svc_subscribeInteractionClassPassively(self, theClass: Any, *unused: Any) -> Any: ...

    def _svc_unsubscribeInteractionClass(self, theClass: Any) -> Any: ...

    def _svc_deleteObjectInstance(self, theObject: Any, userSuppliedTag: bytes, *unused: Any) -> Any: ...

    def _svc_localDeleteObjectInstance(self, theObject: Any) -> Any: ...

    def _svc_requestAttributeTransportationTypeChange(
        self,
        theObject: Any,
        theAttributes: Any,
        theType: Any,
    ) -> Any: ...

    def _svc_requestInteractionTransportationTypeChange(self, theClass: Any, theType: Any) -> Any: ...

    def _svc_unconditionalAttributeOwnershipDivestiture(self, theObject: Any, theAttributes: Any) -> Any: ...

    def _svc_enableTimeRegulation(self, theLookahead: Any) -> Any: ...

    def _svc_disableTimeRegulation(self) -> Any: ...

    def _svc_enableTimeConstrained(self) -> Any: ...

    def _svc_disableTimeConstrained(self) -> Any: ...

    def _svc_timeAdvanceRequest(self, theTime: Any) -> Any: ...

    def _svc_timeAdvanceRequestAvailable(self, theTime: Any) -> Any: ...

    def _svc_nextMessageRequest(self, theTime: Any) -> Any: ...

    def _svc_nextMessageRequestAvailable(self, theTime: Any) -> Any: ...

    def _svc_flushQueueRequest(self, theTime: Any) -> Any: ...

    def _svc_enableAsynchronousDelivery(self) -> Any: ...

    def _svc_disableAsynchronousDelivery(self) -> Any: ...

    def _svc_modifyLookahead(self, theLookahead: Any) -> Any: ...

    def _svc_changeAttributeOrderType(self, theObject: Any, theAttributes: Any, theType: Any) -> Any: ...

    def _svc_changeInteractionOrderType(self, theClass: Any, theType: Any) -> Any: ...


class _MomActionRoutingMixinBase(PythonRTIMomParameterDecodingMixin):
    pass


class PythonRTIMomActionRoutingMixin(_MomActionRoutingMixinBase):
    """MOM interaction routing plus service and adjust action dispatch."""

    def _run_mom_service_action(self, interaction_name: str, params: Mapping[str, bytes]) -> None:
        ctx = cast(_MomActionRoutingContext, self)
        federation = ctx._require_joined()
        target = ctx._target_federate_from_mom_params(federation, params)
        old_state = ctx.state
        ctx.state = target
        try:
            leaf = interaction_name.rsplit(".", 1)[-1]
            if leaf == "HLAresignFederationExecution":
                ctx._svc_resignFederationExecution(
                    self._decode_mom_resign_action(params.get("HLAresignAction"))
                )
            elif leaf == "HLAsynchronizationPointAchieved":
                label = self._decode_mom_text(params.get("HLAlabel"), "")
                ctx._svc_synchronizationPointAchieved(
                    label,
                    self._decode_mom_bool(params.get("HLAsuccessIndicator"), True),
                )
            elif leaf == "HLAfederateSaveBegun":
                ctx._svc_federateSaveBegun()
            elif leaf == "HLAfederateSaveComplete":
                if self._decode_mom_bool(params.get("HLAsuccessIndicator"), True):
                    ctx._svc_federateSaveComplete()
                else:
                    ctx._svc_federateSaveNotComplete()
            elif leaf == "HLAfederateRestoreComplete":
                if self._decode_mom_bool(params.get("HLAsuccessIndicator"), True):
                    ctx._svc_federateRestoreComplete()
                else:
                    ctx._svc_federateRestoreNotComplete()
            elif leaf == "HLApublishObjectClassAttributes":
                ctx._svc_publishObjectClassAttributes(
                    self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                )
            elif leaf == "HLAunpublishObjectClassAttributes":
                ctx._svc_unpublishObjectClassAttributes(
                    self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                )
            elif leaf == "HLApublishInteractionClass":
                ctx._svc_publishInteractionClass(
                    self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass"))
                )
            elif leaf == "HLAunpublishInteractionClass":
                ctx._svc_unpublishInteractionClass(
                    self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass"))
                )
            elif leaf == "HLAsubscribeObjectClassAttributes":
                service = (
                    ctx._svc_subscribeObjectClassAttributes
                    if self._decode_mom_bool(params.get("HLAactive"), True)
                    else ctx._svc_subscribeObjectClassAttributesPassively
                )
                service(
                    self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                )
            elif leaf == "HLAunsubscribeObjectClassAttributes":
                ctx._svc_unsubscribeObjectClassAttributes(
                    self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                )
            elif leaf == "HLAsubscribeInteractionClass":
                service = (
                    ctx._svc_subscribeInteractionClass
                    if self._decode_mom_bool(params.get("HLAactive"), True)
                    else ctx._svc_subscribeInteractionClassPassively
                )
                service(
                    self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass"))
                )
            elif leaf == "HLAunsubscribeInteractionClass":
                ctx._svc_unsubscribeInteractionClass(
                    self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass"))
                )
            elif leaf == "HLAdeleteObjectInstance":
                obj = self._decode_mom_object_instance_handle(params.get("HLAobjectInstance"))
                tag = bytes(params.get("HLAtag", b"MOM"))
                timestamp = self._decode_mom_time(params.get("HLAtimeStamp"))
                if timestamp is not None:
                    ctx._svc_deleteObjectInstance(obj, tag, timestamp)
                else:
                    ctx._svc_deleteObjectInstance(obj, tag)
            elif leaf == "HLAlocalDeleteObjectInstance":
                ctx._svc_localDeleteObjectInstance(
                    self._decode_mom_object_instance_handle(params.get("HLAobjectInstance"))
                )
            elif leaf == "HLArequestAttributeTransportationTypeChange":
                ctx._svc_requestAttributeTransportationTypeChange(
                    self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                    self._decode_mom_transportation_handle(params.get("HLAtransportation")),
                )
            elif leaf == "HLArequestInteractionTransportationTypeChange":
                ctx._svc_requestInteractionTransportationTypeChange(
                    self._decode_mom_interaction_class_handle(
                        params.get("HLAinteractionClass")
                    ),
                    self._decode_mom_transportation_handle(params.get("HLAtransportation")),
                )
            elif leaf == "HLAunconditionalAttributeOwnershipDivestiture":
                ctx._svc_unconditionalAttributeOwnershipDivestiture(
                    self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                )
            elif leaf == "HLAenableTimeRegulation":
                lookahead = (
                    self._decode_mom_interval(params.get("HLAlookahead"))
                    or federation.time_factory.make_zero()
                )
                ctx._svc_enableTimeRegulation(lookahead)
            elif leaf == "HLAdisableTimeRegulation":
                ctx._svc_disableTimeRegulation()
            elif leaf == "HLAenableTimeConstrained":
                ctx._svc_enableTimeConstrained()
            elif leaf == "HLAdisableTimeConstrained":
                ctx._svc_disableTimeConstrained()
            elif leaf == "HLAtimeAdvanceRequest":
                ctx._svc_timeAdvanceRequest(
                    self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time
                )
            elif leaf == "HLAtimeAdvanceRequestAvailable":
                ctx._svc_timeAdvanceRequestAvailable(
                    self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time
                )
            elif leaf == "HLAnextMessageRequest":
                ctx._svc_nextMessageRequest(
                    self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time
                )
            elif leaf == "HLAnextMessageRequestAvailable":
                ctx._svc_nextMessageRequestAvailable(
                    self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time
                )
            elif leaf == "HLAflushQueueRequest":
                ctx._svc_flushQueueRequest(
                    self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time
                )
            elif leaf == "HLAenableAsynchronousDelivery":
                ctx._svc_enableAsynchronousDelivery()
            elif leaf == "HLAdisableAsynchronousDelivery":
                ctx._svc_disableAsynchronousDelivery()
            elif leaf == "HLAmodifyLookahead":
                lookahead = self._decode_mom_interval(params.get("HLAlookahead")) or target.lookahead
                ctx._svc_modifyLookahead(lookahead)
            elif leaf == "HLAchangeAttributeOrderType":
                ctx._svc_changeAttributeOrderType(
                    self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                    self._decode_mom_order_type(params.get("HLAsendOrder")),
                )
            elif leaf == "HLAchangeInteractionOrderType":
                ctx._svc_changeInteractionOrderType(
                    self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")),
                    self._decode_mom_order_type(params.get("HLAsendOrder")),
                )
            else:
                raise UnsupportedBackendService(
                    f"Unsupported MOM service action {leaf}"
                )
        finally:
            ctx.state = old_state

    def _handle_mom_interaction(
        self,
        interaction_name: str,
        parameters: Mapping[ParameterHandle, bytes],
        tag: bytes,
    ) -> bool:
        ctx = cast(_MomActionRoutingContext, self)
        if not (ctx.config.enable_mom and hla_mom.is_mom_interaction_class_name(interaction_name)):
            return False
        federation = ctx._require_joined()
        model = ctx._mom_exposure_model(federation)
        rule = model.interaction_rule(interaction_name)
        if rule is None:
            self._send_mom_exception(
                federation,
                interaction_name,
                "MOMInteractionClassNotDefined",
                interaction_name,
            )
            if ctx.config.strict_mom_parameter_decoding:
                raise InteractionClassNotDefined(interaction_name)
            return True
        if rule.rti_direction == "rti-sends":
            self._send_mom_exception(
                federation, rule.name, "MOMInteractionNotReceivableByRTI", rule.name
            )
            if ctx.config.strict_mom_parameter_decoding:
                raise InteractionClassNotPublished(
                    f"MOM report interaction {rule.name!r} is RTI-sent only"
                )
            return True
        if rule.rti_direction == "neither":
            if ctx.config.strict_mom_parameter_decoding:
                self._send_mom_exception(
                    federation, rule.name, "MOMInteractionNotReceivableByRTI", rule.name
                )
                raise InteractionClassNotDefined(
                    f"MOM non-leaf interaction {rule.name!r} is not RTI-receivable"
                )
            return True

        params = self._mom_params_by_name(rule.name, parameters)
        if not params and parameters:
            return True

        if rule.role == "HLArequest":
            report_name = rule.report_name or ""
            if report_name:
                report_values = ctx._mom_request_report_values(
                    federation, rule.name, report_name, params
                )
                ctx._send_mom_report(federation, report_name, report_values)
            return True
        if rule.role == "HLAservice":
            self._run_mom_service_action(rule.name, params)
            return True
        if rule.role == "HLAadjust":
            target = ctx._target_federate_from_mom_params(federation, params)
            leaf = rule.name.rsplit(".", 1)[-1]
            if leaf == "HLAsetTiming":
                target.convey_producing_federate = self._decode_mom_bool(
                    params.get("HLAreportingState"), target.convey_producing_federate
                )
            elif leaf == "HLAsetSwitches":
                if "HLAconveyProducingFederate" in params:
                    target.convey_producing_federate = self._decode_mom_bool(
                        params.get("HLAconveyProducingFederate"),
                        target.convey_producing_federate,
                    )
                if "HLAconveyRegionDesignatorSets" in params:
                    target.convey_region_designator_sets = self._decode_mom_bool(
                        params.get("HLAconveyRegionDesignatorSets"),
                        target.convey_region_designator_sets,
                    )
                if "HLAserviceReporting" in params:
                    ctx._apply_mom_set_service_reporting(
                        federation,
                        target,
                        self._decode_mom_bool(
                            params.get("HLAserviceReporting"),
                            target.service_reporting,
                        ),
                        rule.name,
                        "HLAserviceReporting",
                    )
                if "HLAexceptionReporting" in params:
                    target.exception_reporting = self._decode_mom_bool(
                        params.get("HLAexceptionReporting"),
                        target.exception_reporting,
                    )
                if "HLAsendServiceReportsToFile" in params:
                    target.service_reports_to_file = self._decode_mom_bool(
                        params.get("HLAsendServiceReportsToFile"),
                        target.service_reports_to_file,
                    )
                    if target.service_reports_to_file:
                        ctx._ensure_service_report_file(federation, target)
                if "HLAreportServiceFile" in params:
                    target.service_report_file = self._decode_mom_text(
                        params.get("HLAreportServiceFile"),
                        target.service_report_file or "",
                    )
            elif leaf in {"HLAsetServiceReporting", "HLAsetReportServiceInvocationReporting"}:
                enabled = self._decode_mom_bool(params.get("HLAreportingState"), True)
                ctx._apply_mom_set_service_reporting(federation, target, enabled, rule.name)
            elif leaf == "HLAsetExceptionReporting":
                target.exception_reporting = self._decode_mom_bool(
                    params.get("HLAreportingState"), target.exception_reporting
                )
            elif leaf == "HLAsetState":
                target.convey_region_designator_sets = self._decode_mom_bool(
                    params.get("HLAconveyRegionDesignatorSets"),
                    target.convey_region_designator_sets,
                )
                target.convey_producing_federate = self._decode_mom_bool(
                    params.get("HLAconveyProducingFederate"),
                    target.convey_producing_federate,
                )
            else:
                self._send_mom_exception(
                    federation, rule.name, "UnsupportedMOMAdjustInteraction", leaf
                )
                if ctx.config.strict_mom_parameter_decoding:
                    raise InteractionClassNotDefined(rule.name)
            ctx._refresh_mom_attribute_values(federation)
            return True
        return True
