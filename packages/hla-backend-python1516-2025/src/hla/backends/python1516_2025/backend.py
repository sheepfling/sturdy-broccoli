"""Live IEEE 1516.1-2025 Python RTI backend implementation."""

from __future__ import annotations

from .ambassador_core_surface_mixin import AmbassadorCoreSurfaceMixin
from .backend_factory_runtime import (
    HostedPython2025Backend,
    Python2025Backend,
    Python2025BackendInfo,
)
from .backend_factory_runtime import (
    create_python2025_backend as _create_python2025_backend,
)
from .declaration_ddm_surface_mixin import DeclarationDdmSurfaceMixin
from .federation_time_surface_mixin import FederationTimeSurfaceMixin
from .mom_surface_mixin import MomSurfaceMixin
from .object_ownership_surface_mixin import ObjectOwnershipSurfaceMixin
from .runtime_helper_surface_mixin import RuntimeHelperSurfaceMixin
from .runtime_state import FEDERATION_REGISTRY as _FEDERATION_REGISTRY
from .runtime_state import FederationRecord as _FederationRecord
from .runtime_state import SynchronizationPointRecord as _SynchronizationPointRecord
from .support_surface_mixin import SupportSurfaceMixin

_DEFAULT_LOGICAL_TIME_IMPLEMENTATION = "HLAinteger64Time"
_SUPPORTED_LOGICAL_TIME_IMPLEMENTATIONS = frozenset(
    {
        "HLAinteger64Time",
        "HLAfloat64Time",
    }
)
_SWITCH_DEFAULTS = {
    "object_class_relevance_advisory": False,
    "attribute_relevance_advisory": False,
    "attribute_scope_advisory": False,
    "interaction_relevance_advisory": False,
    "convey_region_designator_sets": True,
    "service_reporting": False,
    "exception_reporting": True,
    "send_service_reports_to_file": False,
    "auto_provide": True,
    "delay_subscription_evaluation": False,
    "advisories_use_known_class": True,
    "allow_relaxed_ddm": False,
    "non_regulated_grant": False,
}
MOM_2025_FEDERATE_ADJUST_LEAVES = frozenset(
    {
        "HLAsetTiming",
        "HLAmodifyAttributeState",
        "HLAsetServiceReporting",
        "HLAsetExceptionReporting",
        "HLAsetSwitches",
    }
)
MOM_2025_FEDERATION_ADJUST_LEAVES = frozenset({"HLAsetSwitches"})
MOM_2025_FEDERATE_REQUEST_LEAVES = frozenset(
    {
        "HLArequestPublications",
        "HLArequestSubscriptions",
        "HLArequestObjectInstancesThatCanBeDeleted",
        "HLArequestObjectInstancesUpdated",
        "HLArequestObjectInstancesReflected",
        "HLArequestUpdatesSent",
        "HLArequestInteractionsSent",
        "HLArequestReflectionsReceived",
        "HLArequestInteractionsReceived",
        "HLArequestObjectInstanceInformation",
        "HLArequestFOMmoduleData",
    }
)
MOM_2025_FEDERATION_REQUEST_LEAVES = frozenset(
    {
        "HLArequestSynchronizationPoints",
        "HLArequestSynchronizationPointStatus",
        "HLArequestFOMmoduleData",
        "HLArequestMIMdata",
    }
)
MOM_2025_FEDERATE_SERVICE_LEAVES = frozenset(
    {
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
    }
)
MOM_2025_INPROCESS_ROUTED_MANAGER_LEAVES = frozenset(
    MOM_2025_FEDERATE_ADJUST_LEAVES
    | MOM_2025_FEDERATION_ADJUST_LEAVES
    | MOM_2025_FEDERATE_REQUEST_LEAVES
    | MOM_2025_FEDERATION_REQUEST_LEAVES
    | MOM_2025_FEDERATE_SERVICE_LEAVES
)

class Python2025RTIAmbassador(
    AmbassadorCoreSurfaceMixin,
    RuntimeHelperSurfaceMixin,
    MomSurfaceMixin,
    DeclarationDdmSurfaceMixin,
    ObjectOwnershipSurfaceMixin,
    FederationTimeSurfaceMixin,
    SupportSurfaceMixin,
):
    """Minimal 2025 RTI ambassador for factory and adapter development."""

    backend_info = Python2025BackendInfo()
    _DEFAULT_LOGICAL_TIME_IMPLEMENTATION = _DEFAULT_LOGICAL_TIME_IMPLEMENTATION
    _SUPPORTED_LOGICAL_TIME_IMPLEMENTATIONS = _SUPPORTED_LOGICAL_TIME_IMPLEMENTATIONS
    _SWITCH_DEFAULTS = _SWITCH_DEFAULTS
    _FEDERATION_REGISTRY = _FEDERATION_REGISTRY
    _FederationRecord = _FederationRecord
    _SynchronizationPointRecord = _SynchronizationPointRecord

Python2025BackendScaffold = Python2025Backend
Python2025BackendInfo.__module__ = __name__
Python2025Backend.__module__ = __name__
HostedPython2025Backend.__module__ = __name__


def create_python2025_backend(request):  # noqa: ANN001, ANN201
    return _create_python2025_backend(request)

__all__ = [
    "Python2025Backend",
    "Python2025BackendInfo",
    "Python2025BackendScaffold",
    "Python2025RTIAmbassador",
    "create_python2025_backend",
]
