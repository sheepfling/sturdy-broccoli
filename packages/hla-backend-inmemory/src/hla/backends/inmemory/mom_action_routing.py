"""MOM service dispatch and interaction routing for the Python RTI backend."""

from __future__ import annotations

from typing import Mapping

from hla.rti1516e import mom as hla_mom
from hla.rti1516e.exceptions import (
    InteractionClassNotDefined,
    InteractionClassNotPublished,
)
from hla.rti1516e.handles import ParameterHandle
from hla.backends.common import UnsupportedBackendService

from .mom_parameter_decoding import PythonRTIMomParameterDecodingMixin


class PythonRTIMomActionRoutingMixin(PythonRTIMomParameterDecodingMixin):
    """MOM interaction routing plus service and adjust action dispatch."""

    def _run_mom_service_action(self, interaction_name: str, params: Mapping[str, bytes]) -> None:
        federation = self._require_joined()
        target = self._target_federate_from_mom_params(federation, params)
        old_state = self.state
        self.state = target
        try:
            leaf = interaction_name.rsplit(".", 1)[-1]
            if leaf == "HLAresignFederationExecution":
                self._svc_resignFederationExecution(
                    self._decode_mom_resign_action(params.get("HLAresignAction"))
                )
            elif leaf == "HLAsynchronizationPointAchieved":
                label = self._decode_mom_text(params.get("HLAlabel"), "")
                self._svc_synchronizationPointAchieved(
                    label,
                    self._decode_mom_bool(params.get("HLAsuccessIndicator"), True),
                )
            elif leaf == "HLAfederateSaveBegun":
                self._svc_federateSaveBegun()
            elif leaf == "HLAfederateSaveComplete":
                if self._decode_mom_bool(params.get("HLAsuccessIndicator"), True):
                    self._svc_federateSaveComplete()
                else:
                    self._svc_federateSaveNotComplete()
            elif leaf == "HLAfederateRestoreComplete":
                if self._decode_mom_bool(params.get("HLAsuccessIndicator"), True):
                    self._svc_federateRestoreComplete()
                else:
                    self._svc_federateRestoreNotComplete()
            elif leaf == "HLApublishObjectClassAttributes":
                self._svc_publishObjectClassAttributes(
                    self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                )
            elif leaf == "HLAunpublishObjectClassAttributes":
                self._svc_unpublishObjectClassAttributes(
                    self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                )
            elif leaf == "HLApublishInteractionClass":
                self._svc_publishInteractionClass(
                    self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass"))
                )
            elif leaf == "HLAunpublishInteractionClass":
                self._svc_unpublishInteractionClass(
                    self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass"))
                )
            elif leaf == "HLAsubscribeObjectClassAttributes":
                service = (
                    self._svc_subscribeObjectClassAttributes
                    if self._decode_mom_bool(params.get("HLAactive"), True)
                    else self._svc_subscribeObjectClassAttributesPassively
                )
                service(
                    self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                )
            elif leaf == "HLAunsubscribeObjectClassAttributes":
                self._svc_unsubscribeObjectClassAttributes(
                    self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                )
            elif leaf == "HLAsubscribeInteractionClass":
                service = (
                    self._svc_subscribeInteractionClass
                    if self._decode_mom_bool(params.get("HLAactive"), True)
                    else self._svc_subscribeInteractionClassPassively
                )
                service(
                    self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass"))
                )
            elif leaf == "HLAunsubscribeInteractionClass":
                self._svc_unsubscribeInteractionClass(
                    self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass"))
                )
            elif leaf == "HLAdeleteObjectInstance":
                obj = self._decode_mom_object_instance_handle(params.get("HLAobjectInstance"))
                tag = bytes(params.get("HLAtag", b"MOM"))
                timestamp = self._decode_mom_time(params.get("HLAtimeStamp"))
                if timestamp is not None:
                    self._svc_deleteObjectInstance(obj, tag, timestamp)
                else:
                    self._svc_deleteObjectInstance(obj, tag)
            elif leaf == "HLAlocalDeleteObjectInstance":
                self._svc_localDeleteObjectInstance(
                    self._decode_mom_object_instance_handle(params.get("HLAobjectInstance"))
                )
            elif leaf == "HLArequestAttributeTransportationTypeChange":
                self._svc_requestAttributeTransportationTypeChange(
                    self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                    self._decode_mom_transportation_handle(params.get("HLAtransportation")),
                )
            elif leaf == "HLArequestInteractionTransportationTypeChange":
                self._svc_requestInteractionTransportationTypeChange(
                    self._decode_mom_interaction_class_handle(
                        params.get("HLAinteractionClass")
                    ),
                    self._decode_mom_transportation_handle(params.get("HLAtransportation")),
                )
            elif leaf == "HLAunconditionalAttributeOwnershipDivestiture":
                self._svc_unconditionalAttributeOwnershipDivestiture(
                    self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                )
            elif leaf == "HLAenableTimeRegulation":
                lookahead = (
                    self._decode_mom_interval(params.get("HLAlookahead"))
                    or federation.time_factory.make_zero()
                )
                self._svc_enableTimeRegulation(lookahead)
            elif leaf == "HLAdisableTimeRegulation":
                self._svc_disableTimeRegulation()
            elif leaf == "HLAenableTimeConstrained":
                self._svc_enableTimeConstrained()
            elif leaf == "HLAdisableTimeConstrained":
                self._svc_disableTimeConstrained()
            elif leaf == "HLAtimeAdvanceRequest":
                self._svc_timeAdvanceRequest(
                    self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time
                )
            elif leaf == "HLAtimeAdvanceRequestAvailable":
                self._svc_timeAdvanceRequestAvailable(
                    self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time
                )
            elif leaf == "HLAnextMessageRequest":
                self._svc_nextMessageRequest(
                    self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time
                )
            elif leaf == "HLAnextMessageRequestAvailable":
                self._svc_nextMessageRequestAvailable(
                    self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time
                )
            elif leaf == "HLAflushQueueRequest":
                self._svc_flushQueueRequest(
                    self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time
                )
            elif leaf == "HLAenableAsynchronousDelivery":
                self._svc_enableAsynchronousDelivery()
            elif leaf == "HLAdisableAsynchronousDelivery":
                self._svc_disableAsynchronousDelivery()
            elif leaf == "HLAmodifyLookahead":
                lookahead = self._decode_mom_interval(params.get("HLAlookahead")) or target.lookahead
                self._svc_modifyLookahead(lookahead)
            elif leaf == "HLAchangeAttributeOrderType":
                self._svc_changeAttributeOrderType(
                    self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")),
                    self._decode_mom_attribute_set(params.get("HLAattributeList")),
                    self._decode_mom_order_type(params.get("HLAsendOrder")),
                )
            elif leaf == "HLAchangeInteractionOrderType":
                self._svc_changeInteractionOrderType(
                    self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")),
                    self._decode_mom_order_type(params.get("HLAsendOrder")),
                )
            else:
                raise UnsupportedBackendService(
                    f"Unsupported MOM service action {leaf}"
                )
        finally:
            self.state = old_state

    def _handle_mom_interaction(
        self,
        interaction_name: str,
        parameters: Mapping[ParameterHandle, bytes],
        tag: bytes,
    ) -> bool:
        if not (self.config.enable_mom and hla_mom.is_mom_interaction_class_name(interaction_name)):
            return False
        federation = self._require_joined()
        model = self._mom_exposure_model(federation)
        rule = model.interaction_rule(interaction_name)
        if rule is None:
            self._send_mom_exception(
                federation,
                interaction_name,
                "MOMInteractionClassNotDefined",
                interaction_name,
            )
            if self.config.strict_mom_parameter_decoding:
                raise InteractionClassNotDefined(interaction_name)
            return True
        if rule.rti_direction == "rti-sends":
            self._send_mom_exception(
                federation, rule.name, "MOMInteractionNotReceivableByRTI", rule.name
            )
            if self.config.strict_mom_parameter_decoding:
                raise InteractionClassNotPublished(
                    f"MOM report interaction {rule.name!r} is RTI-sent only"
                )
            return True
        if rule.rti_direction == "neither":
            if self.config.strict_mom_parameter_decoding:
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
                report_values = self._mom_request_report_values(
                    federation, rule.name, report_name, params
                )
                self._send_mom_report(federation, report_name, report_values)
            return True
        if rule.role == "HLAservice":
            self._run_mom_service_action(rule.name, params)
            return True
        if rule.role == "HLAadjust":
            target = self._target_federate_from_mom_params(federation, params)
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
                    self._apply_mom_set_service_reporting(
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
                        self._ensure_service_report_file(federation, target)
                if "HLAreportServiceFile" in params:
                    target.service_report_file = self._decode_mom_text(
                        params.get("HLAreportServiceFile"),
                        target.service_report_file or "",
                    )
            elif leaf in {"HLAsetServiceReporting", "HLAsetReportServiceInvocationReporting"}:
                enabled = self._decode_mom_bool(params.get("HLAreportingState"), True)
                self._apply_mom_set_service_reporting(federation, target, enabled, rule.name)
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
                if self.config.strict_mom_parameter_decoding:
                    raise InteractionClassNotDefined(rule.name)
            self._refresh_mom_attribute_values(federation)
            return True
        return True
