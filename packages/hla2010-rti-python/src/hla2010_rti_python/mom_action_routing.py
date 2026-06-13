"""MOM service dispatch and interaction routing for the Python RTI backend."""

from __future__ import annotations

from typing import Mapping

from hla2010 import mom as hla_mom
from hla2010.exceptions import (
    InteractionClassNotDefined,
    InteractionClassNotPublished,
)
from hla2010.handles import ParameterHandle
from hla2010_rti_backend_common import UnsupportedBackendService

from .mom_parameter_decoding import PythonRTIMomParameterDecodingMixin


class PythonRTIMomActionRoutingMixin(PythonRTIMomParameterDecodingMixin):
    """MOM interaction routing plus service and adjust action dispatch."""

    def _mom_service_action_resign(self, federation, target, params: Mapping[str, bytes]) -> None:
        del federation, target
        self.call_service(
            "resignFederationExecution",
            self._decode_mom_resign_action(params.get("HLAresignAction")),
        )

    def _mom_service_action_synchronization_point_achieved(
        self,
        federation,
        target,
        params: Mapping[str, bytes],
    ) -> None:
        del federation, target
        label = self._decode_mom_text(params.get("HLAlabel"), "")
        self.call_service(
            "synchronizationPointAchieved",
            label,
            self._decode_mom_bool(params.get("HLAsuccessIndicator"), True),
        )

    def _mom_service_action_federate_save_begun(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target, params
        self.call_service("federateSaveBegun")

    def _mom_service_action_federate_save_complete(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "federateSaveComplete"
            if self._decode_mom_bool(params.get("HLAsuccessIndicator"), True)
            else "federateSaveNotComplete"
        )

    def _mom_service_action_federate_restore_complete(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "federateRestoreComplete"
            if self._decode_mom_bool(params.get("HLAsuccessIndicator"), True)
            else "federateRestoreNotComplete"
        )

    def _mom_service_action_publish_object_class_attributes(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "publishObjectClassAttributes",
            self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
            self._decode_mom_attribute_set(params.get("HLAattributeList")),
        )

    def _mom_service_action_unpublish_object_class_attributes(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "unpublishObjectClassAttributes",
            self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
            self._decode_mom_attribute_set(params.get("HLAattributeList")),
        )

    def _mom_service_action_publish_interaction_class(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "publishInteractionClass",
            self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")),
        )

    def _mom_service_action_unpublish_interaction_class(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "unpublishInteractionClass",
            self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")),
        )

    def _mom_service_action_subscribe_object_class_attributes(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            (
                "subscribeObjectClassAttributes"
                if self._decode_mom_bool(params.get("HLAactive"), True)
                else "subscribeObjectClassAttributesPassively"
            ),
            self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
            self._decode_mom_attribute_set(params.get("HLAattributeList")),
        )

    def _mom_service_action_unsubscribe_object_class_attributes(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "unsubscribeObjectClassAttributes",
            self._decode_mom_object_class_handle(params.get("HLAobjectClass")),
            self._decode_mom_attribute_set(params.get("HLAattributeList")),
        )

    def _mom_service_action_subscribe_interaction_class(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            (
                "subscribeInteractionClass"
                if self._decode_mom_bool(params.get("HLAactive"), True)
                else "subscribeInteractionClassPassively"
            ),
            self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")),
        )

    def _mom_service_action_unsubscribe_interaction_class(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "unsubscribeInteractionClass",
            self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")),
        )

    def _mom_service_action_delete_object_instance(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del target
        obj = self._decode_mom_object_instance_handle(params.get("HLAobjectInstance"))
        tag = bytes(params.get("HLAtag", b"MOM"))
        timestamp = self._decode_mom_time(params.get("HLAtimeStamp"))
        if timestamp is not None:
            self.call_service("deleteObjectInstance", obj, tag, timestamp)
            return
        self.call_service("deleteObjectInstance", obj, tag)

    def _mom_service_action_local_delete_object_instance(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "localDeleteObjectInstance",
            self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")),
        )

    def _mom_service_action_request_attribute_transportation_type_change(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "requestAttributeTransportationTypeChange",
            self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")),
            self._decode_mom_attribute_set(params.get("HLAattributeList")),
            self._decode_mom_transportation_handle(params.get("HLAtransportation")),
        )

    def _mom_service_action_request_interaction_transportation_type_change(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "requestInteractionTransportationTypeChange",
            self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")),
            self._decode_mom_transportation_handle(params.get("HLAtransportation")),
        )

    def _mom_service_action_unconditional_attribute_ownership_divestiture(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "unconditionalAttributeOwnershipDivestiture",
            self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")),
            self._decode_mom_attribute_set(params.get("HLAattributeList")),
        )

    def _mom_service_action_enable_time_regulation(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del target
        lookahead = (
            self._decode_mom_interval(params.get("HLAlookahead"))
            or federation.time_factory.make_zero()
        )
        self.call_service("enableTimeRegulation", lookahead)

    def _mom_service_action_disable_time_regulation(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target, params
        self.call_service("disableTimeRegulation")

    def _mom_service_action_enable_time_constrained(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target, params
        self.call_service("enableTimeConstrained")

    def _mom_service_action_disable_time_constrained(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target, params
        self.call_service("disableTimeConstrained")

    def _mom_service_action_time_advance_request(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation
        self.call_service(
            "timeAdvanceRequest",
            self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time,
        )

    def _mom_service_action_time_advance_request_available(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation
        self.call_service(
            "timeAdvanceRequestAvailable",
            self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time,
        )

    def _mom_service_action_next_message_request(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation
        self.call_service(
            "nextMessageRequest",
            self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time,
        )

    def _mom_service_action_next_message_request_available(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation
        self.call_service(
            "nextMessageRequestAvailable",
            self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time,
        )

    def _mom_service_action_flush_queue_request(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation
        self.call_service(
            "flushQueueRequest",
            self._decode_mom_time(params.get("HLAtimeStamp")) or target.current_time,
        )

    def _mom_service_action_enable_asynchronous_delivery(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target, params
        self.call_service("enableAsynchronousDelivery")

    def _mom_service_action_disable_asynchronous_delivery(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target, params
        self.call_service("disableAsynchronousDelivery")

    def _mom_service_action_modify_lookahead(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation
        lookahead = self._decode_mom_interval(params.get("HLAlookahead")) or target.lookahead
        self.call_service("modifyLookahead", lookahead)

    def _mom_service_action_change_attribute_order_type(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "changeAttributeOrderType",
            self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")),
            self._decode_mom_attribute_set(params.get("HLAattributeList")),
            self._decode_mom_order_type(params.get("HLAsendOrder")),
        )

    def _mom_service_action_change_interaction_order_type(
        self, federation, target, params: Mapping[str, bytes]
    ) -> None:
        del federation, target
        self.call_service(
            "changeInteractionOrderType",
            self._decode_mom_interaction_class_handle(params.get("HLAinteractionClass")),
            self._decode_mom_order_type(params.get("HLAsendOrder")),
        )

    def _mom_service_action_handlers(self) -> dict[str, object]:
        return {
            "HLAresignFederationExecution": self._mom_service_action_resign,
            "HLAsynchronizationPointAchieved": self._mom_service_action_synchronization_point_achieved,
            "HLAfederateSaveBegun": self._mom_service_action_federate_save_begun,
            "HLAfederateSaveComplete": self._mom_service_action_federate_save_complete,
            "HLAfederateRestoreComplete": self._mom_service_action_federate_restore_complete,
            "HLApublishObjectClassAttributes": self._mom_service_action_publish_object_class_attributes,
            "HLAunpublishObjectClassAttributes": self._mom_service_action_unpublish_object_class_attributes,
            "HLApublishInteractionClass": self._mom_service_action_publish_interaction_class,
            "HLAunpublishInteractionClass": self._mom_service_action_unpublish_interaction_class,
            "HLAsubscribeObjectClassAttributes": self._mom_service_action_subscribe_object_class_attributes,
            "HLAunsubscribeObjectClassAttributes": self._mom_service_action_unsubscribe_object_class_attributes,
            "HLAsubscribeInteractionClass": self._mom_service_action_subscribe_interaction_class,
            "HLAunsubscribeInteractionClass": self._mom_service_action_unsubscribe_interaction_class,
            "HLAdeleteObjectInstance": self._mom_service_action_delete_object_instance,
            "HLAlocalDeleteObjectInstance": self._mom_service_action_local_delete_object_instance,
            "HLArequestAttributeTransportationTypeChange": self._mom_service_action_request_attribute_transportation_type_change,
            "HLArequestInteractionTransportationTypeChange": self._mom_service_action_request_interaction_transportation_type_change,
            "HLAunconditionalAttributeOwnershipDivestiture": self._mom_service_action_unconditional_attribute_ownership_divestiture,
            "HLAenableTimeRegulation": self._mom_service_action_enable_time_regulation,
            "HLAdisableTimeRegulation": self._mom_service_action_disable_time_regulation,
            "HLAenableTimeConstrained": self._mom_service_action_enable_time_constrained,
            "HLAdisableTimeConstrained": self._mom_service_action_disable_time_constrained,
            "HLAtimeAdvanceRequest": self._mom_service_action_time_advance_request,
            "HLAtimeAdvanceRequestAvailable": self._mom_service_action_time_advance_request_available,
            "HLAnextMessageRequest": self._mom_service_action_next_message_request,
            "HLAnextMessageRequestAvailable": self._mom_service_action_next_message_request_available,
            "HLAflushQueueRequest": self._mom_service_action_flush_queue_request,
            "HLAenableAsynchronousDelivery": self._mom_service_action_enable_asynchronous_delivery,
            "HLAdisableAsynchronousDelivery": self._mom_service_action_disable_asynchronous_delivery,
            "HLAmodifyLookahead": self._mom_service_action_modify_lookahead,
            "HLAchangeAttributeOrderType": self._mom_service_action_change_attribute_order_type,
            "HLAchangeInteractionOrderType": self._mom_service_action_change_interaction_order_type,
        }

    def _mom_adjust_action_set_timing(self, federation, target, rule_name: str, params: Mapping[str, bytes]) -> None:
        del federation, rule_name
        target.convey_producing_federate = self._decode_mom_bool(
            params.get("HLAreportingState"),
            target.convey_producing_federate,
        )

    def _mom_adjust_action_set_switches(
        self, federation, target, rule_name: str, params: Mapping[str, bytes]
    ) -> None:
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
                rule_name,
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

    def _mom_adjust_action_set_service_reporting(
        self, federation, target, rule_name: str, params: Mapping[str, bytes]
    ) -> None:
        enabled = self._decode_mom_bool(params.get("HLAreportingState"), True)
        self._apply_mom_set_service_reporting(federation, target, enabled, rule_name)

    def _mom_adjust_action_set_exception_reporting(
        self, federation, target, rule_name: str, params: Mapping[str, bytes]
    ) -> None:
        del federation, rule_name
        target.exception_reporting = self._decode_mom_bool(
            params.get("HLAreportingState"),
            target.exception_reporting,
        )

    def _mom_adjust_action_set_state(
        self, federation, target, rule_name: str, params: Mapping[str, bytes]
    ) -> None:
        del federation, rule_name
        target.convey_region_designator_sets = self._decode_mom_bool(
            params.get("HLAconveyRegionDesignatorSets"),
            target.convey_region_designator_sets,
        )
        target.convey_producing_federate = self._decode_mom_bool(
            params.get("HLAconveyProducingFederate"),
            target.convey_producing_federate,
        )

    def _mom_adjust_action_handlers(self) -> dict[str, object]:
        return {
            "HLAsetTiming": self._mom_adjust_action_set_timing,
            "HLAsetSwitches": self._mom_adjust_action_set_switches,
            "HLAsetServiceReporting": self._mom_adjust_action_set_service_reporting,
            "HLAsetReportServiceInvocationReporting": self._mom_adjust_action_set_service_reporting,
            "HLAsetExceptionReporting": self._mom_adjust_action_set_exception_reporting,
            "HLAsetState": self._mom_adjust_action_set_state,
        }

    def _run_mom_service_action(self, interaction_name: str, params: Mapping[str, bytes]) -> None:
        federation = self._require_joined()
        target = self._target_federate_from_mom_params(federation, params)
        old_state = self.state
        self.state = target
        try:
            leaf = interaction_name.rsplit(".", 1)[-1]
            handler = self._mom_service_action_handlers().get(leaf)
            if handler is None:
                raise UnsupportedBackendService(
                    f"Unsupported MOM service action {leaf}"
                )
            handler(federation, target, params)
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
            handler = self._mom_adjust_action_handlers().get(leaf)
            if handler is None:
                self._send_mom_exception(
                    federation, rule.name, "UnsupportedMOMAdjustInteraction", leaf
                )
                if self.config.strict_mom_parameter_decoding:
                    raise InteractionClassNotDefined(rule.name)
            else:
                handler(federation, target, rule.name, params)
            self._refresh_mom_attribute_values(federation)
            return True
        return True
