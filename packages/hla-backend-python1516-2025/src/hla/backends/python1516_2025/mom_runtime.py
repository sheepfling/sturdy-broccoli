"""MOM manager routing helpers for the current Python 2025 RTI runtime."""

from __future__ import annotations

from typing import Any, Mapping

from hla.rti1516_2025.enums import OrderType
from hla.rti1516_2025.exceptions import AttributeNotOwned, ObjectClassNotPublished
from hla.rti1516_2025.handles import (
    AttributeHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
)

MOM_REQUEST_TO_REPORT = {
    "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPoints":
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPoints",
    "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestSynchronizationPointStatus":
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportSynchronizationPointStatus",
    "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestFOMmoduleData":
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportFOMmoduleData",
    "HLAinteractionRoot.HLAmanager.HLAfederation.HLArequest.HLArequestMIMdata":
        "HLAinteractionRoot.HLAmanager.HLAfederation.HLAreport.HLAreportMIMdata",
}


def handle_mom_interaction(
    rti: Any,
    interaction_class_name: str,
    values_by_handle: Mapping[ParameterHandle, bytes],
) -> bool:
    if ".HLAmanager." not in interaction_class_name:
        return False
    try:
        if ".HLAadjust." in interaction_class_name:
            return handle_mom_adjust_interaction(rti, interaction_class_name, values_by_handle)
        if ".HLAservice." in interaction_class_name:
            return handle_mom_service_interaction(rti, interaction_class_name, values_by_handle)
    except Exception as exc:
        send_mom_exception_interaction(rti, interaction_class_name, exc, parameter_error=False)
        raise
    if ".HLArequest." not in interaction_class_name:
        return False
    if ".HLAfederate.HLArequest." in interaction_class_name:
        try:
            return handle_mom_federate_request_interaction(rti, interaction_class_name, values_by_handle)
        except Exception as exc:
            send_mom_exception_interaction(rti, interaction_class_name, exc, parameter_error=True)
            raise
    report_name = MOM_REQUEST_TO_REPORT.get(interaction_class_name)
    if report_name is None:
        return False
    try:
        send_mom_report_interaction(
            rti,
            report_name,
            mom_request_report_values(rti, interaction_class_name, report_name, values_by_handle),
        )
    except Exception as exc:
        send_mom_exception_interaction(rti, interaction_class_name, exc, parameter_error=True)
        raise
    return True


def handle_mom_federate_request_interaction(
    rti: Any,
    interaction_class_name: str,
    values_by_handle: Mapping[ParameterHandle, bytes],
) -> bool:
    params = rti._mom_request_params_by_name(interaction_class_name, values_by_handle)
    target = rti._mom_target_rti(params)
    target_federate = target._current_federate_handle()
    if interaction_class_name.endswith("HLArequestPublications"):
        send_mom_publication_reports(target, target_federate)
        return True
    if interaction_class_name.endswith("HLArequestSubscriptions"):
        send_mom_subscription_reports(target, target_federate)
        return True
    if interaction_class_name.endswith("HLArequestObjectInstanceInformation"):
        object_instance = ObjectInstanceHandle(rti._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance"))
        send_mom_object_instance_information_report(target, target_federate, object_instance)
        return True
    if interaction_class_name.endswith("HLArequestFOMmoduleData"):
        report_name = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportFOMmoduleData"
        values = mom_request_report_values(target, interaction_class_name, report_name, values_by_handle)
        values["HLAfederate"] = str(target_federate.value).encode("ascii")
        send_mom_report_interaction(target, report_name, values)
        return True
    if interaction_class_name.endswith("HLArequestObjectInstancesThatCanBeDeleted"):
        send_mom_object_class_count_report(
            target,
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesThatCanBeDeleted",
            target_federate,
            mom_deletable_object_counts(target, target_federate),
            "HLAobjectInstanceCounts",
        )
        return True
    if interaction_class_name.endswith("HLArequestObjectInstancesUpdated"):
        send_mom_object_class_count_report(
            target,
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesUpdated",
            target_federate,
            mom_counts_for_federate(target._federation_record().mom_object_instances_updated, target_federate),
            "HLAobjectInstanceCounts",
        )
        return True
    if interaction_class_name.endswith("HLArequestObjectInstancesReflected"):
        send_mom_object_class_count_report(
            target,
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstancesReflected",
            target_federate,
            mom_counts_for_federate(target._federation_record().mom_object_instances_reflected, target_federate),
            "HLAobjectInstanceCounts",
        )
        return True
    if interaction_class_name.endswith("HLArequestUpdatesSent"):
        send_mom_transport_count_report(
            target,
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportUpdatesSent",
            target_federate,
            mom_transport_counts_for_federate(target._federation_record().mom_updates_sent, target_federate),
            "HLAupdateCounts",
        )
        return True
    if interaction_class_name.endswith("HLArequestReflectionsReceived"):
        send_mom_transport_count_report(
            target,
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportReflectionsReceived",
            target_federate,
            mom_transport_counts_for_federate(target._federation_record().mom_reflections_received, target_federate),
            "HLAreflectCounts",
        )
        return True
    if interaction_class_name.endswith("HLArequestInteractionsSent"):
        send_mom_transport_count_report(
            target,
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsSent",
            target_federate,
            mom_transport_counts_for_federate(target._federation_record().mom_interactions_sent, target_federate),
            "HLAinteractionCounts",
        )
        return True
    if interaction_class_name.endswith("HLArequestInteractionsReceived"):
        send_mom_transport_count_report(
            target,
            "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionsReceived",
            target_federate,
            mom_transport_counts_for_federate(target._federation_record().mom_interactions_received, target_federate),
            "HLAinteractionCounts",
        )
        return True
    return False


def send_mom_publication_reports(rti: Any, target_federate: FederateHandle) -> None:
    federation = rti._federation_record()
    object_publications = federation.published_object_attributes.get(target_federate.value, {})
    object_report = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassPublication"
    if not object_publications:
        send_mom_report_interaction(
            rti,
            object_report,
            {
                "HLAfederate": str(target_federate.value).encode("ascii"),
                "HLAnumberOfClasses": b"0",
            },
        )
    else:
        for object_class_name, attribute_names in sorted(object_publications.items()):
            send_mom_report_interaction(
                rti,
                object_report,
                {
                    "HLAfederate": str(target_federate.value).encode("ascii"),
                    "HLAnumberOfClasses": str(len(object_publications)).encode("ascii"),
                    "HLAobjectClass": str(rti._object_class_handles()[object_class_name]).encode("ascii"),
                    "HLAattributeList": rti._mom_handle_list_payload(
                        rti._attribute_handles(object_class_name)[attribute_name]
                        for attribute_name in sorted(attribute_names)
                    ),
                },
            )
    send_mom_report_interaction(
        rti,
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionPublication",
        {
            "HLAfederate": str(target_federate.value).encode("ascii"),
            "HLAinteractionClassList": rti._mom_handle_list_payload(
                rti._interaction_class_handles()[interaction_class_name]
                for interaction_class_name in sorted(federation.published_interactions.get(target_federate.value, set()))
            ),
        },
    )


def send_mom_subscription_reports(rti: Any, target_federate: FederateHandle) -> None:
    federation = rti._federation_record()
    object_subscriptions = federation.subscribed_object_attributes.get(target_federate.value, {})
    object_report = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectClassSubscription"
    if not object_subscriptions:
        send_mom_report_interaction(
            rti,
            object_report,
            {
                "HLAfederate": str(target_federate.value).encode("ascii"),
                "HLAnumberOfClasses": b"0",
            },
        )
    else:
        for object_class_name, attribute_names in sorted(object_subscriptions.items()):
            send_mom_report_interaction(
                rti,
                object_report,
                {
                    "HLAfederate": str(target_federate.value).encode("ascii"),
                    "HLAnumberOfClasses": str(len(object_subscriptions)).encode("ascii"),
                    "HLAobjectClass": str(rti._object_class_handles()[object_class_name]).encode("ascii"),
                    "HLAactive": b"HLAtrue",
                    "HLAmaxUpdateRate": b"",
                    "HLAattributeList": rti._mom_handle_list_payload(
                        rti._attribute_handles(object_class_name)[attribute_name]
                        for attribute_name in sorted(attribute_names)
                    ),
                },
            )
    send_mom_report_interaction(
        rti,
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportInteractionSubscription",
        {
            "HLAfederate": str(target_federate.value).encode("ascii"),
            "HLAinteractionClassList": rti._mom_handle_list_payload(
                rti._interaction_class_handles()[interaction_class_name]
                for interaction_class_name in sorted(federation.subscribed_interactions.get(target_federate.value, set()))
            ),
        },
    )


def send_mom_object_instance_information_report(
    rti: Any,
    target_federate: FederateHandle,
    object_instance: ObjectInstanceHandle,
) -> None:
    record = rti._object_instance_record_known(object_instance)
    owned_attribute_handles = [
        rti._attribute_handles(record.object_class_name)[attribute_name]
        for attribute_name, owner in sorted(record.attribute_owners.items())
        if owner == target_federate
    ]
    object_class_handle = rti._object_class_handles()[record.object_class_name]
    send_mom_report_interaction(
        rti,
        "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportObjectInstanceInformation",
        {
            "HLAfederate": str(target_federate.value).encode("ascii"),
            "HLAobjectInstance": str(object_instance.value).encode("ascii"),
            "HLAownedInstanceAttributeList": rti._mom_handle_list_payload(owned_attribute_handles),
            "HLAregisteredClass": str(object_class_handle).encode("ascii"),
            "HLAknownClass": str(object_class_handle).encode("ascii"),
        },
    )


def send_mom_object_class_count_report(
    rti: Any,
    report_name: str,
    target_federate: FederateHandle,
    counts_by_class: Mapping[str, int],
    count_parameter_name: str,
) -> None:
    send_mom_report_interaction(
        rti,
        report_name,
        {
            "HLAfederate": str(target_federate.value).encode("ascii"),
            count_parameter_name: rti._mom_object_class_counts_payload(counts_by_class),
        },
    )


def send_mom_transport_count_report(
    rti: Any,
    report_name: str,
    target_federate: FederateHandle,
    counts_by_transport: Mapping[str, Mapping[str, int]],
    count_parameter_name: str,
) -> None:
    if not counts_by_transport:
        counts_by_transport = {"HLAreliable": {}}
    for transportation_name, counts_by_name in sorted(counts_by_transport.items()):
        send_mom_report_interaction(
            rti,
            report_name,
            {
                "HLAfederate": str(target_federate.value).encode("ascii"),
                "HLAtransportation": transportation_name.encode("ascii"),
                count_parameter_name: rti._mom_object_class_counts_payload(counts_by_name),
            },
        )


def mom_deletable_object_counts(rti: Any, target_federate: FederateHandle) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in rti._federation_record().object_instances.values():
        if target_federate not in set(record.attribute_owners.values()):
            continue
        if ".HLAmanager." in record.object_class_name:
            continue
        counts[record.object_class_name] = counts.get(record.object_class_name, 0) + 1
    return counts


def mom_counts_for_federate(counts: Mapping[tuple[int, str], int], target_federate: FederateHandle) -> dict[str, int]:
    result: dict[str, int] = {}
    for (federate_key, class_name), count in counts.items():
        if federate_key == target_federate.value:
            if ".HLAmanager." in class_name:
                continue
            result[class_name] = count
    return result


def mom_transport_counts_for_federate(
    counts: Mapping[tuple[int, str, str], int],
    target_federate: FederateHandle,
) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for (federate_key, class_name, transportation_name), count in counts.items():
        if federate_key == target_federate.value:
            result.setdefault(transportation_name, {})[class_name] = count
    return result


def handle_mom_service_interaction(
    rti: Any,
    interaction_class_name: str,
    values_by_handle: Mapping[ParameterHandle, bytes],
) -> bool:
    params = rti._mom_request_params_by_name(interaction_class_name, values_by_handle)
    target = rti._mom_target_rti(params)
    leaf = interaction_class_name.rsplit(".", 1)[-1]
    if leaf == "HLAresignFederationExecution":
        target.resignFederationExecution(rti._mom_resign_action(params.get("HLAresignAction")))
        return True
    if leaf == "HLAsynchronizationPointAchieved":
        target.synchronizationPointAchieved(
            rti._mom_text(params.get("HLAlabel"), "HLAlabel"),
            rti._mom_bool(params.get("HLAsuccessIndicator"), True),
        )
        return True
    if leaf == "HLAfederateSaveBegun":
        target.federateSaveBegun()
        return True
    if leaf == "HLAfederateSaveComplete":
        if rti._mom_bool(params.get("HLAsuccessIndicator"), True):
            target.federateSaveComplete()
        else:
            target.federateSaveNotComplete()
        return True
    if leaf == "HLAfederateRestoreComplete":
        if rti._mom_bool(params.get("HLAsuccessIndicator"), True):
            target.federateRestoreComplete()
        else:
            target.federateRestoreNotComplete()
        return True
    if leaf == "HLAenableTimeRegulation":
        target.enableTimeRegulation(target._mom_interval(params.get("HLAlookahead"), "HLAlookahead"))
        return True
    if leaf == "HLAdisableTimeRegulation":
        target.disableTimeRegulation()
        return True
    if leaf == "HLAenableTimeConstrained":
        target.enableTimeConstrained()
        return True
    if leaf == "HLAdisableTimeConstrained":
        target.disableTimeConstrained()
        return True
    if leaf == "HLAenableAsynchronousDelivery":
        target.enableAsynchronousDelivery()
        return True
    if leaf == "HLAdisableAsynchronousDelivery":
        target.disableAsynchronousDelivery()
        return True
    if leaf == "HLAtimeAdvanceRequest":
        target.timeAdvanceRequest(target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp"))
        return True
    if leaf == "HLAtimeAdvanceRequestAvailable":
        target.timeAdvanceRequestAvailable(target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp"))
        return True
    if leaf == "HLAnextMessageRequest":
        target.nextMessageRequest(target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp"))
        return True
    if leaf == "HLAnextMessageRequestAvailable":
        target.nextMessageRequestAvailable(target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp"))
        return True
    if leaf == "HLAflushQueueRequest":
        target.flushQueueRequest(target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp"))
        return True
    if leaf == "HLAmodifyLookahead":
        target.modifyLookahead(target._mom_interval(params.get("HLAlookahead"), "HLAlookahead"))
        return True
    if leaf == "HLAdeleteObjectInstance":
        time = target._mom_time(params.get("HLAtimeStamp"), "HLAtimeStamp") if params.get("HLAtimeStamp") else None
        target.deleteObjectInstance(
            ObjectInstanceHandle(rti._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance")),
            bytes(params.get("HLAtag", b"MOM")),
            time,
        )
        return True
    if leaf == "HLAlocalDeleteObjectInstance":
        target.localDeleteObjectInstance(
            ObjectInstanceHandle(rti._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance"))
        )
        return True
    if leaf == "HLArequestAttributeTransportationTypeChange":
        target.requestAttributeTransportationTypeChange(
            ObjectInstanceHandle(rti._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance")),
            rti._mom_attribute_handles(params.get("HLAattributeList")),
            target._mom_transportation_handle(params.get("HLAtransportation"), "HLAtransportation"),
        )
        return True
    if leaf == "HLArequestInteractionTransportationTypeChange":
        target.requestInteractionTransportationTypeChange(
            InteractionClassHandle(rti._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass")),
            target._mom_transportation_handle(params.get("HLAtransportation"), "HLAtransportation"),
        )
        return True
    if leaf == "HLAchangeAttributeOrderType":
        target.changeAttributeOrderType(
            ObjectInstanceHandle(rti._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance")),
            rti._mom_attribute_handles(params.get("HLAattributeList")),
            rti._mom_order_type(params.get("HLAsendOrder"), "HLAsendOrder"),
        )
        return True
    if leaf == "HLAchangeInteractionOrderType":
        target.changeInteractionOrderType(
            InteractionClassHandle(rti._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass")),
            rti._mom_order_type(params.get("HLAsendOrder"), "HLAsendOrder"),
        )
        return True
    if leaf == "HLAunconditionalAttributeOwnershipDivestiture":
        target.unconditionalAttributeOwnershipDivestiture(
            ObjectInstanceHandle(rti._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance")),
            rti._mom_attribute_handles(params.get("HLAattributeList")),
            b"MOM",
        )
        return True
    if leaf == "HLApublishObjectClassAttributes":
        target.publishObjectClassAttributes(
            ObjectClassHandle(rti._mom_int(params.get("HLAobjectClass"), "HLAobjectClass")),
            rti._mom_attribute_handles(params.get("HLAattributeList")),
        )
        return True
    if leaf == "HLAunpublishObjectClassAttributes":
        target.unpublishObjectClassAttributes(
            ObjectClassHandle(rti._mom_int(params.get("HLAobjectClass"), "HLAobjectClass")),
            rti._mom_attribute_handles(params.get("HLAattributeList")),
        )
        return True
    if leaf == "HLApublishInteractionClass":
        target.publishInteractionClass(
            InteractionClassHandle(rti._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass"))
        )
        return True
    if leaf == "HLAunpublishInteractionClass":
        target.unpublishInteractionClass(
            InteractionClassHandle(rti._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass"))
        )
        return True
    if leaf == "HLAsubscribeObjectClassAttributes":
        service = (
            target.subscribeObjectClassAttributes
            if rti._mom_bool(params.get("HLAactive"), True)
            else target.subscribeObjectClassAttributesPassively
        )
        service(
            ObjectClassHandle(rti._mom_int(params.get("HLAobjectClass"), "HLAobjectClass")),
            rti._mom_attribute_handles(params.get("HLAattributeList")),
        )
        return True
    if leaf == "HLAunsubscribeObjectClassAttributes":
        target.unsubscribeObjectClassAttributes(
            ObjectClassHandle(rti._mom_int(params.get("HLAobjectClass"), "HLAobjectClass")),
            rti._mom_attribute_handles(params.get("HLAattributeList")),
        )
        return True
    if leaf == "HLAsubscribeInteractionClass":
        service = (
            target.subscribeInteractionClass
            if rti._mom_bool(params.get("HLAactive"), True)
            else target.subscribeInteractionClassPassively
        )
        service(
            InteractionClassHandle(rti._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass"))
        )
        return True
    if leaf == "HLAunsubscribeInteractionClass":
        target.unsubscribeInteractionClass(
            InteractionClassHandle(rti._mom_int(params.get("HLAinteractionClass"), "HLAinteractionClass"))
        )
        return True
    return False


def handle_mom_adjust_interaction(
    rti: Any,
    interaction_class_name: str,
    values_by_handle: Mapping[ParameterHandle, bytes],
) -> bool:
    params = rti._mom_request_params_by_name(interaction_class_name, values_by_handle)
    target = rti._mom_target_rti(params)
    if interaction_class_name.endswith("HLAsetServiceReporting"):
        target._switches["service_reporting"] = rti._mom_bool(params.get("HLAreportingState"), False)
        return True
    if interaction_class_name.endswith("HLAsetExceptionReporting"):
        target._switches["exception_reporting"] = rti._mom_bool(params.get("HLAreportingState"), False)
        return True
    if interaction_class_name.endswith("HLAsetTiming"):
        target._mom_report_period_seconds = float(rti._mom_number(params.get("HLAreportPeriod"), "HLAreportPeriod"))
        return True
    if interaction_class_name.endswith("HLAmodifyAttributeState"):
        object_instance = ObjectInstanceHandle(rti._mom_int(params.get("HLAobjectInstance"), "HLAobjectInstance"))
        attribute = AttributeHandle(rti._mom_int(params.get("HLAattribute"), "HLAattribute"))
        ownership_state = rti._mom_ownership_state(params.get("HLAattributeState"), "HLAattributeState")
        modify_mom_attribute_state(target, object_instance, attribute, ownership_state)
        return True
    if interaction_class_name.endswith("HLAsetSwitches") and ".HLAfederate." in interaction_class_name:
        if "HLAconveyRegionDesignatorSets" in params:
            target._switches["convey_region_designator_sets"] = rti._mom_bool(
                params.get("HLAconveyRegionDesignatorSets"),
                target._switches["convey_region_designator_sets"],
            )
        return True
    if interaction_class_name.endswith("HLAsetSwitches") and ".HLAfederation." in interaction_class_name:
        if "HLAautoProvide" in params:
            auto_provide = rti._mom_bool(params.get("HLAautoProvide"), target._switches["auto_provide"])
            for member_rti in rti._federation_record().member_rtis.values():
                member_rti._switches["auto_provide"] = auto_provide
        return True
    return False


def modify_mom_attribute_state(
    rti: Any,
    object_instance: ObjectInstanceHandle,
    attribute: AttributeHandle,
    ownership_state: str,
) -> None:
    record = rti._object_instance_record(object_instance)
    attribute_name = rti._attribute_names_from_handles(record.object_class_name, {attribute})[0]
    if ownership_state == "owned":
        if attribute_name not in rti._published_attributes_for_current_federate(record.object_class_name):
            raise ObjectClassNotPublished(record.object_class_name)
        record.attribute_owners[attribute_name] = rti._current_federate_handle()
        record.attribute_divesting.discard(attribute_name)
        record.attribute_candidates.pop(attribute_name, None)
        return
    if record.attribute_owners.get(attribute_name) != rti._current_federate_handle():
        raise AttributeNotOwned(attribute_name)
    record.attribute_owners[attribute_name] = None
    record.attribute_divesting.discard(attribute_name)
    record.attribute_candidates.pop(attribute_name, None)


def mom_request_report_values(
    rti: Any,
    request_name: str,
    report_name: str,
    values_by_handle: Mapping[ParameterHandle, bytes],
) -> dict[str, bytes]:
    federation = rti._federation_record()
    params = rti._mom_request_params_by_name(request_name, values_by_handle)
    if report_name.endswith("HLAreportFOMmoduleData"):
        indicator = rti._mom_index(params.get("HLAFOMmoduleIndicator"))
        module_data = rti._mom_module_data(federation.fom_modules, indicator)
        return {
            "HLAFOMmoduleIndicator": str(indicator).encode("ascii"),
            "HLAFOMmoduleData": module_data.encode("utf-8"),
        }
    if report_name.endswith("HLAreportMIMdata"):
        return {
            "HLAMIMdata": rti._mom_single_module_data(federation.mim_module).encode("utf-8"),
        }
    if report_name.endswith("HLAreportSynchronizationPoints"):
        labels = ",".join(sorted(federation.synchronization_points)).encode("ascii")
        return {
            "HLAsyncPoints": labels,
            "HLAsynchronizationPoints": labels,
        }
    if report_name.endswith("HLAreportSynchronizationPointStatus"):
        requested_label = (params.get("HLAlabel") or params.get("HLAsyncPointName") or b"").decode("ascii")
        labels = [requested_label] if requested_label else sorted(federation.synchronization_points)
        federates: set[int] = set()
        statuses = []
        for label in labels:
            point = federation.synchronization_points.get(label)
            if point is None:
                statuses.append(f"{label}:")
                continue
            reported = sorted(point.achieved_federates | point.failed_federates)
            federates.update(reported)
            status_bits = ",".join(
                f"{handle}:failed" if handle in point.failed_federates else f"{handle}:achieved"
                for handle in reported
            )
            statuses.append(f"{label}:{status_bits}")
        label_payload = ",".join(labels).encode("ascii")
        federates_payload = ",".join(str(handle) for handle in sorted(federates)).encode("ascii")
        statuses_payload = ";".join(statuses).encode("ascii")
        return {
            "HLAsyncPointName": label_payload,
            "HLAsyncPointFederates": statuses_payload,
            "HLAlabel": label_payload,
            "HLAfederateList": federates_payload,
            "HLAfederateSynchronizationStatusList": statuses_payload,
        }
    return {}


def send_mom_report_interaction(rti: Any, report_name: str, values: Mapping[str, bytes]) -> None:
    report_class = InteractionClassHandle(rti._interaction_class_handles()[report_name])
    report_parameters = rti._parameter_handles(report_name)
    parameter_values: dict[ParameterHandle, bytes] = {
        ParameterHandle(report_parameters[name]): bytes(value)
        for name, value in values.items()
        if name in report_parameters
    }
    transportation = rti._transportation_handle_by_name("HLAreliable")
    federation = rti._federation_record()
    for federate_key, subscriptions in federation.subscribed_interactions.items():
        if report_name not in subscriptions:
            continue
        rti._deliver_to_federate_handle(
            FederateHandle(federate_key),
            "receiveInteraction",
            report_class,
            parameter_values,
            b"MOM",
            transportation,
            rti._current_federate_handle(),
            set(),
            None,
            OrderType.RECEIVE,
            OrderType.RECEIVE,
            None,
        )


def send_mom_exception_interaction(
    rti: Any,
    interaction_class_name: str,
    exception: Exception,
    *,
    parameter_error: bool,
) -> None:
    report_name = "HLAinteractionRoot.HLAmanager.HLAfederate.HLAreport.HLAreportMOMexception"
    try:
        report_class = InteractionClassHandle(rti._interaction_class_handles()[report_name])
        report_parameters = rti._parameter_handles(report_name)
    except Exception:
        return
    values = {
        "HLAservice": interaction_class_name.encode("utf-8"),
        "HLAexception": f"{type(exception).__name__}: {exception}".encode("utf-8"),
        "HLAparameterError": b"HLAtrue" if parameter_error else b"HLAfalse",
    }
    parameter_values = {
        ParameterHandle(report_parameters[name]): value
        for name, value in values.items()
        if name in report_parameters
    }
    transportation = rti._transportation_handle_by_name("HLAreliable")
    federation = rti._federation_record()
    for federate_key in sorted(federation.member_ambassadors):
        member_rti = federation.member_rtis.get(federate_key)
        if member_rti is not None and not member_rti._switches.get("exception_reporting", True):
            continue
        rti._deliver_to_federate_handle(
            FederateHandle(federate_key),
            "receiveInteraction",
            report_class,
            parameter_values,
            b"MOM",
            transportation,
            rti._current_federate_handle(),
            set(),
            None,
            OrderType.RECEIVE,
            OrderType.RECEIVE,
            None,
        )
