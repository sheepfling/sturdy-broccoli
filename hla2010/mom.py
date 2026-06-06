"""Management Object Model (MOM) / MIM catalog helpers for the Python RTI.

The symbols in this module are intentionally name-based.  The pure Python RTI
installs them into its handle tables, while Java adapters may use the same names
to normalize handles and report interactions crossing JPype/Py4J.

Section anchors:
* IEEE 1516.1-2010 Clause 11, especially 11.2-11.4 and Tables 4-7.
* IEEE 1516.1-2010 Annex G for the standard MOM and Initialization Module
  (MIM); if Annex G and Clause 11 differ, Clause 11 takes precedence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Any

from .encoding import HLAboolean, HLAinteger32BE, HLAunicodeString, HLAopaqueData
from .fom import FOMModule, ObjectClassSpec, InteractionClassSpec

MOM_OBJECT_ROOT = "HLAobjectRoot.HLAmanager"
MOM_INTERACTION_ROOT = "HLAinteractionRoot.HLAmanager"
MOM_FEDERATE_OBJECT_CLASS = f"{MOM_OBJECT_ROOT}.HLAfederate"
MOM_FEDERATION_OBJECT_CLASS = f"{MOM_OBJECT_ROOT}.HLAfederation"
MOM_FEDERATE_INTERACTION_ROOT = f"{MOM_INTERACTION_ROOT}.HLAfederate"
MOM_FEDERATION_INTERACTION_ROOT = f"{MOM_INTERACTION_ROOT}.HLAfederation"
STANDARD_MIM_NAME = "HLAstandardMIM"
RTI_FEDERATE_OBJECT_NAME_PREFIX = "HLAmanager.HLAfederate"
RTI_FEDERATION_OBJECT_NAME_PREFIX = "HLAmanager.HLAfederation"

MOM_FEDERATE_ATTRIBUTES: tuple[str, ...] = (
    "HLAfederateHandle",
    "HLAfederateName",
    "HLAfederateType",
    "HLAfederateHost",
    "HLARTIversion",
    "HLAFOMmoduleDesignatorList",
    "HLAtimeConstrained",
    "HLAtimeRegulating",
    "HLAasynchronousDelivery",
    "HLAfederateState",
    "HLAtimeManagerState",
    "HLAlogicalTime",
    "HLAlookahead",
    "HLAGALT",
    "HLALITS",
    "HLAROlength",
    "HLATSOlength",
    "HLAreflectionsReceived",
    "HLAupdatesSent",
    "HLAinteractionsReceived",
    "HLAinteractionsSent",
    "HLAobjectInstancesThatCanBeDeleted",
    "HLAobjectInstancesUpdated",
    "HLAobjectInstancesReflected",
    "HLAobjectInstancesDeleted",
    "HLAobjectInstancesRemoved",
    "HLAobjectInstancesRegistered",
    "HLAobjectInstancesDiscovered",
    "HLAtimeGrantedTime",
    "HLAtimeAdvancingTime",
    "HLAconveyRegionDesignatorSets",
    "HLAconveyProducingFederate",
    "HLAserviceReporting",
    "HLAexceptionReporting",
)

MOM_FEDERATION_ATTRIBUTES: tuple[str, ...] = (
    "HLAfederationName",
    "HLAfederatesInFederation",
    "HLARTIversion",
    "HLAMIMDesignator",
    "HLAFOMmoduleDesignatorList",
    "HLAcurrentFDD",
    "HLAtimeImplementationName",
    "HLAlastSaveName",
    "HLAlastSaveTime",
    "HLAnextSaveName",
    "HLAnextSaveTime",
    "HLAautoProvide",
)

# Leaf interaction class -> predefined parameter names.  Non-leaf classes are
# also installed with no parameters so getInteractionClassHandle can resolve the
# full MOM hierarchy.
MOM_INTERACTION_PARAMETERS: dict[str, tuple[str, ...]] = {
    # Federate adjust/request/report/service hierarchy
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAadjust.HLAsetTiming": ("HLAfederate", "HLAreportPeriod"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAadjust.HLAmodifyAttributeState": ("HLAfederate", "HLAobjectInstance", "HLAattribute", "HLAattributeState"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAadjust.HLAsetSwitches": (
        "HLAfederate",
        "HLAconveyRegionDesignatorSets",
        "HLAconveyProducingFederate",
        "HLAserviceReporting",
        "HLAexceptionReporting",
    ),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestPublications": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestSubscriptions": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestObjectInstancesThatCanBeDeleted": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestObjectInstancesUpdated": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestObjectInstancesReflected": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestUpdatesSent": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestInteractionsSent": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestReflectionsReceived": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestInteractionsReceived": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestObjectInstanceInformation": ("HLAfederate", "HLAobjectInstance"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest.HLArequestFOMmoduleData": ("HLAfederate", "HLAFOMmoduleIndicator"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportObjectClassPublication": ("HLAfederate", "HLAnumberOfClasses", "HLAobjectClass", "HLAattributeList"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportObjectClassSubscription": ("HLAfederate", "HLAnumberOfClasses", "HLAobjectClass", "HLAactive", "HLAmaxUpdateRate", "HLAattributeList"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportInteractionPublication": ("HLAfederate", "HLAinteractionClassList"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportInteractionSubscription": ("HLAfederate", "HLAinteractionClassList"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportObjectInstancesThatCanBeDeleted": ("HLAfederate", "HLAobjectInstanceCounts"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportObjectInstancesUpdated": ("HLAfederate", "HLAobjectInstanceCounts"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportObjectInstancesReflected": ("HLAfederate", "HLAobjectInstanceCounts"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportUpdatesSent": ("HLAfederate", "HLAupdatesSent"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportReflectionsReceived": ("HLAfederate", "HLAreflectionsReceived"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportInteractionsSent": ("HLAfederate", "HLAinteractionsSent"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportInteractionsReceived": ("HLAfederate", "HLAinteractionsReceived"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportObjectInstanceInformation": ("HLAfederate", "HLAobjectInstance", "HLAobjectClass", "HLAobjectInstanceName", "HLAattributeList"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportException": ("HLAfederate", "HLAservice", "HLAexception", "HLAparameterError"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportServiceInvocation": ("HLAfederate", "HLAservice", "HLAinitiator", "HLAsuccessIndicator", "HLAexception", "HLAserialNumber"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportMOMexception": ("HLAfederate", "HLAservice", "HLAexception", "HLAparameterError"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportFederateLost": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportFOMmoduleData": ("HLAfederate", "HLAFOMmoduleIndicator", "HLAFOMmoduleData"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAresignFederationExecution": ("HLAfederate", "HLAresignAction"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAsynchronizationPointAchieved": ("HLAfederate", "HLAlabel", "HLAsuccessIndicator"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAfederateSaveBegun": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAfederateSaveComplete": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAfederateRestoreComplete": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLApublishObjectClassAttributes": ("HLAfederate", "HLAobjectClass", "HLAattributeList"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAunpublishObjectClassAttributes": ("HLAfederate", "HLAobjectClass", "HLAattributeList"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLApublishInteractionClass": ("HLAfederate", "HLAinteractionClass"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAunpublishInteractionClass": ("HLAfederate", "HLAinteractionClass"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAsubscribeObjectClassAttributes": ("HLAfederate", "HLAobjectClass", "HLAattributeList", "HLAactive"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAunsubscribeObjectClassAttributes": ("HLAfederate", "HLAobjectClass", "HLAattributeList"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAsubscribeInteractionClass": ("HLAfederate", "HLAinteractionClass", "HLAactive"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAunsubscribeInteractionClass": ("HLAfederate", "HLAinteractionClass"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAdeleteObjectInstance": ("HLAfederate", "HLAobjectInstance", "HLAtag", "HLAtimeStamp"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAlocalDeleteObjectInstance": ("HLAfederate", "HLAobjectInstance"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLArequestAttributeTransportationypeChange": ("HLAfederate", "HLAobjectInstance", "HLAattributeList", "HLAtransportationType"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLArequestInteractionTransportationypeChange": ("HLAfederate", "HLAinteractionClass", "HLAtransportationType"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAunconditionalAttributeOwnershipDivestiture": ("HLAfederate", "HLAobjectInstance", "HLAattributeList"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAenableTimeRegulation": ("HLAfederate", "HLAlookahead"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAdisableTimeRegulation": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAenableTimeConstrained": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAdisableTimeConstrained": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAtimeAdvanceRequest": ("HLAfederate", "HLAtimeStamp"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAtimeAdvanceRequestAvailable": ("HLAfederate", "HLAtimeStamp"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAnextMessageRequest": ("HLAfederate", "HLAtimeStamp"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAnextMessageRequestAvailable": ("HLAfederate", "HLAtimeStamp"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAflushQueueRequest": ("HLAfederate", "HLAtimeStamp"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAenableAsynchronousDelivery": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAdisableAsynchronousDelivery": ("HLAfederate",),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAmodifyLookahead": ("HLAfederate", "HLAlookahead"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAchangeAttributeOrderType": ("HLAfederate", "HLAobjectInstance", "HLAattributeList", "HLAorderType"),
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice.HLAchangeInteractionOrderType": ("HLAfederate", "HLAinteractionClass", "HLAorderType"),
    # Federation adjust/request/report hierarchy
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLAadjust.HLAsetSwitches": ("HLAautoProvide",),
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestSynchronizationPoints": (),
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestSynchronizationPointStatus": ("HLAlabel",),
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestFOMmoduleData": ("HLAFOMmoduleIndicator",),
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestMIMData": (),
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportSynchronizationPoints": ("HLAsynchronizationPoints",),
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportSynchronizationPointStatus": ("HLAlabel", "HLAfederateList", "HLAfederateSynchronizationStatusList"),
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportFOMmoduleData": ("HLAFOMmoduleIndicator", "HLAFOMmoduleData"),
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportMIMData": ("HLAMIMData",),
}

MOM_INTERACTION_NON_LEAF_CLASSES: tuple[str, ...] = (
    "HLAinteractionRoot",
    MOM_INTERACTION_ROOT,
    MOM_FEDERATE_INTERACTION_ROOT,
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAadjust",
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLArequest",
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAreport",
    f"{MOM_FEDERATE_INTERACTION_ROOT}.HLAservice",
    MOM_FEDERATION_INTERACTION_ROOT,
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLAadjust",
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLArequest",
    f"{MOM_FEDERATION_INTERACTION_ROOT}.HLAreport",
)


def parent_name(full_name: str) -> str | None:
    return full_name.rsplit(".", 1)[0] if "." in full_name else None


def _fallback_standard_mim_module() -> FOMModule:
    """Build a local standard-MIM/MOM catalog module.

    This is still a practical development MIM rather than a byte-for-byte copy of
    Annex G XML, but it exposes the normative MOM object/interaction names used
    by Clause 11 so the Python RTI can publish, subscribe, report, and process
    the management surface.
    """

    object_classes = (
        ObjectClassSpec("HLAobjectRoot", ()),
        ObjectClassSpec(MOM_OBJECT_ROOT, (), parent_name="HLAobjectRoot"),
        ObjectClassSpec(MOM_FEDERATE_OBJECT_CLASS, MOM_FEDERATE_ATTRIBUTES, parent_name=MOM_OBJECT_ROOT, declared_attributes=MOM_FEDERATE_ATTRIBUTES),
        ObjectClassSpec(MOM_FEDERATION_OBJECT_CLASS, MOM_FEDERATION_ATTRIBUTES, parent_name=MOM_OBJECT_ROOT, declared_attributes=MOM_FEDERATION_ATTRIBUTES),
    )
    interaction_classes = [
        InteractionClassSpec(name, (), parent_name=parent_name(name)) for name in MOM_INTERACTION_NON_LEAF_CLASSES
    ]
    interaction_classes.extend(
        InteractionClassSpec(name, params, parent_name=parent_name(name), declared_parameters=params)
        for name, params in sorted(MOM_INTERACTION_PARAMETERS.items())
    )
    return FOMModule(
        source=STANDARD_MIM_NAME,
        uri="builtin:HLAstandardMIM",
        name=STANDARD_MIM_NAME,
        model_type="MIM",
        is_mim=True,
        object_classes=object_classes,
        interaction_classes=tuple(interaction_classes),
        dimensions=("HLAdefaultRoutingSpace", "HLAfederate", "HLAserviceGroup"),
        inferred_time_implementation="HLAfloat64Time",
        notes=(
            "MOM/MIM development catalog derived from IEEE 1516.1-2010 Clause 11 names; "
            "replace with a full Annex G MIM XML for external conformance campaigns.",
        ),
    )


def create_standard_mim_module() -> FOMModule:
    """Return the bundled standard MOM/MIM catalog.

    Section anchors: IEEE 1516.1-2010 §11 and Annex G.  The preferred path is
    the HLAstandardMIM.xml file shipped with the uploaded 1516.1-2010 downloads.
    A generated fallback is retained for environments where package resources are
    unavailable.
    """

    try:
        from importlib import resources
        from pathlib import Path
        from .fom import parse_fom_xml, _path_to_file_uri

        resource = resources.files("hla2010").joinpath("resources", "foms", "HLAstandardMIM.xml")
        path = Path(str(resource))
        parsed = parse_fom_xml(path, source=STANDARD_MIM_NAME, uri=_path_to_file_uri(path))
        return FOMModule(
            source=STANDARD_MIM_NAME,
            uri=parsed.uri,
            path=parsed.path,
            name=STANDARD_MIM_NAME,
            model_type="MIM",
            object_classes=parsed.object_classes,
            interaction_classes=parsed.interaction_classes,
            dimensions=parsed.dimensions,
            inferred_time_implementation=parsed.inferred_time_implementation,
            notes=("Parsed bundled HLAstandardMIM.xml from IEEE 1516.1-2010 downloads; section anchors: §11 and Annex G.",),
            is_mim=True,
        )
    except Exception:
        return _fallback_standard_mim_module()


def is_mom_object_class_name(name: str) -> bool:
    return name == MOM_OBJECT_ROOT or name.startswith(MOM_OBJECT_ROOT + ".")


def is_mom_interaction_class_name(name: str) -> bool:
    return name == MOM_INTERACTION_ROOT or name.startswith(MOM_INTERACTION_ROOT + ".")


def mom_report_name_for_request(request_name: str) -> str | None:
    """Return the standard MOM report interaction class for a request class."""

    if ".HLArequest." not in request_name:
        return None
    candidate = request_name.replace(".HLArequest.HLArequest", ".HLAreport.HLAreport", 1)
    return candidate if candidate in MOM_INTERACTION_PARAMETERS else None


def encode_text(value: Any) -> bytes:
    return HLAunicodeString(str(value)).encode()


def encode_bool(value: Any) -> bytes:
    return HLAboolean(bool(value)).encode()


def encode_count(value: int) -> bytes:
    return HLAinteger32BE(int(value)).encode()


def encode_opaque(value: Any) -> bytes:
    if isinstance(value, bytes):
        data = value
    elif isinstance(value, bytearray):
        data = bytes(value)
    else:
        data = str(value).encode("utf-8")
    return HLAopaqueData(data).encode()


def decode_text(data: bytes | bytearray | memoryview) -> str:
    element = HLAunicodeString()
    element.decode(bytes(data))
    return element.value


def decode_bool(data: bytes | bytearray | memoryview) -> bool:
    element = HLAboolean(False)
    element.decode(bytes(data))
    return bool(element.value)


def decode_count(data: bytes | bytearray | memoryview) -> int:
    element = HLAinteger32BE(0)
    element.decode(bytes(data))
    return int(element.value)


def decode_opaque(data: bytes | bytearray | memoryview) -> bytes:
    element = HLAopaqueData()
    element.decode(bytes(data))
    return bytes(element.value)


def encode_handle_list(handles: Iterable[Any]) -> bytes:
    payload = b"".join(handle.encode() if hasattr(handle, "encode") else encode_text(handle) for handle in handles)
    return HLAopaqueData(payload).encode()


__all__ = [
    "MOM_OBJECT_ROOT",
    "MOM_INTERACTION_ROOT",
    "MOM_FEDERATE_OBJECT_CLASS",
    "MOM_FEDERATION_OBJECT_CLASS",
    "MOM_FEDERATE_INTERACTION_ROOT",
    "MOM_FEDERATION_INTERACTION_ROOT",
    "MOM_FEDERATE_ATTRIBUTES",
    "MOM_FEDERATION_ATTRIBUTES",
    "MOM_INTERACTION_PARAMETERS",
    "STANDARD_MIM_NAME",
    "create_standard_mim_module",
    "is_mom_object_class_name",
    "is_mom_interaction_class_name",
    "mom_report_name_for_request",
    "encode_text",
    "encode_bool",
    "encode_count",
    "encode_opaque",
    "encode_handle_list",
    "decode_text",
    "decode_bool",
    "decode_count",
    "decode_opaque",
]
