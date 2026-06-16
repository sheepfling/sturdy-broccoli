"""Startup and synchronization helpers for small HLA federations.

The helpers in this module are intentionally thin wrappers around standard
RTIambassador services. They keep examples clean while preserving the normal HLA
startup sequence and section anchors:

* IEEE 1516.1-2010 §4.2 ``Connect``
* IEEE 1516.1-2010 §4.5 ``Create Federation Execution``
* IEEE 1516.1-2010 §4.9 ``Join Federation Execution``
* IEEE 1516.1-2010 §4.11-§4.15 federation synchronization services

They work with the pure Python RTI and the Java JPype/Py4J adapters because they
only call the backend-neutral Python RTIambassador façade.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from hla.rti1516e.enums import CallbackModel
from hla.rti1516e.exceptions import FederationExecutionAlreadyExists, RTIexception
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.handles import FederateHandle


@dataclass(frozen=True)
class FederationStartupConfig:
    """Configuration for the usual connect/create/join startup sequence."""

    federation_name: str
    federate_name: str = ""
    federate_type: str = "PythonFederate"
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    mim_module: Any | None = None
    logical_time_implementation_name: str | None = None
    callback_model: CallbackModel = CallbackModel.HLA_EVOKED
    local_settings_designator: str | None = None
    auto_create: bool = True
    ready_to_run_sync_point: str | None = "ReadyToRun"

    @classmethod
    def target_radar(
        cls,
        *,
        federation_name: str = "TargetRadarFederation",
        federate_name: str = "",
        federate_type: str = "PythonFederate",
    ) -> "FederationStartupConfig":
        """Return a config using the bundled Target/Radar FOM resource."""

        return cls(
            federation_name=federation_name,
            federate_name=federate_name,
            federate_type=federate_type,
            fom_modules=("resource:TargetRadarFOMmodule.xml",),
            logical_time_implementation_name="HLAfloat64Time",
        )

    def create_federation_args(self) -> tuple[Any, ...]:
        args: list[Any] = [list(self.fom_modules)]
        if self.mim_module is not None:
            args.append(self.mim_module)
        if self.logical_time_implementation_name is not None:
            args.append(self.logical_time_implementation_name)
        return tuple(args)

    def join_args(self) -> tuple[Any, ...]:
        if self.federate_name:
            return (self.federate_name, self.federate_type, self.federation_name)
        return (self.federate_type, self.federation_name)


@dataclass(frozen=True)
class StartupResult:
    """Result of :func:`connect_create_join`."""

    federate_handle: FederateHandle
    created_federation: bool
    synchronization_label: str | None = None


# Backwards-compatible v0.8 names.
FederateStartupConfig = FederationStartupConfig
FederateStartupResult = StartupResult


def _as_rti_list(rtis: Any) -> list[Any]:
    if isinstance(rtis, (str, bytes, bytearray)):
        return [rtis]
    if hasattr(rtis, "evokeMultipleCallbacks") or hasattr(rtis, "evoke_multiple_callbacks"):
        return [rtis]
    try:
        return list(rtis)
    except TypeError:
        return [rtis]


def _call_service(rti: Any, snake_name: str, camel_name: str, *args: Any) -> Any:
    method = getattr(rti, snake_name, None) or getattr(rti, camel_name)
    return method(*args)


def connect_create_join(
    rti: Any,
    ambassador: NullFederateAmbassador,
    config: FederationStartupConfig,
    *,
    create_federation: bool | None = None,
) -> StartupResult:
    """Connect, create if needed, then join a federation execution.

    Existing federations are treated as a normal startup race: if creation raises
    ``FederationExecutionAlreadyExists``, joining continues.
    """

    connect_args = [ambassador, config.callback_model]
    if config.local_settings_designator is not None:
        connect_args.append(config.local_settings_designator)
    _call_service(rti, "connect", "connect", *connect_args)

    should_create = config.auto_create if create_federation is None else create_federation
    created = False
    if should_create:
        try:
            if config.mim_module is not None and hasattr(rti, "createFederationExecutionWithMIM"):
                _call_service(
                    rti,
                    "create_federation_execution_with_mim",
                    "createFederationExecutionWithMIM",
                    config.federation_name,
                    *config.create_federation_args(),
                )
            else:
                _call_service(
                    rti,
                    "create_federation_execution",
                    "createFederationExecution",
                    config.federation_name,
                    *config.create_federation_args(),
                )
            created = True
        except FederationExecutionAlreadyExists:
            created = False

    handle = _call_service(rti, "join_federation_execution", "joinFederationExecution", *config.join_args())
    return StartupResult(handle, created, config.ready_to_run_sync_point)


def evoke_all_callbacks(rtis: Iterable[Any] | Any) -> bool:
    """Drain currently queued callbacks once for each ambassador."""

    delivered = False
    for rti in _as_rti_list(rtis):
        try:
            delivered = bool(_call_service(rti, "evoke_multiple_callbacks", "evokeMultipleCallbacks", 0.0, 0.0)) or delivered
        except RTIexception:
            raise
        except AttributeError:
            continue
    return delivered


def drain_callbacks(rtis: Iterable[Any] | Any, *, max_cycles: int = 16, max_passes: int | None = None) -> int:
    """Drain callback queues with a bounded deterministic loop.

    Returns the number of passes that delivered at least one callback.
    """

    passes = 0
    limit = max_passes if max_passes is not None else max_cycles
    rti_list = _as_rti_list(rtis)
    for _ in range(limit):
        if not evoke_all_callbacks(rti_list):
            return passes
        passes += 1
    return passes


def register_startup_sync_point(
    rti: Any,
    label: str = "ReadyToRun",
    tag: bytes = b"startup",
    synchronization_set: Iterable[Any] | None = None,
) -> None:
    """Register the usual startup synchronization point."""

    if synchronization_set is None:
        _call_service(rti, "register_federation_synchronization_point", "registerFederationSynchronizationPoint", label, tag)
    else:
        _call_service(
            rti,
            "register_federation_synchronization_point",
            "registerFederationSynchronizationPoint",
            label,
            tag,
            set(synchronization_set),
        )


def achieve_startup_sync_point(rti: Any, label: str = "ReadyToRun", *, success: bool = True) -> None:
    """Report achievement for the usual startup synchronization point."""

    _call_service(rti, "synchronization_point_achieved", "synchronizationPointAchieved", label, bool(success))


def synchronize_ready_to_run(
    rtis: Sequence[Any],
    *,
    label: str = "ReadyToRun",
    tag: bytes = b"startup",
    max_passes: int = 16,
) -> None:
    """Register and achieve a whole-federation startup synchronization point."""

    if not rtis:
        return
    register_startup_sync_point(rtis[0], label, tag)
    drain_callbacks(rtis, max_passes=max_passes)
    for rti in rtis:
        achieve_startup_sync_point(rti, label)
    drain_callbacks(rtis, max_passes=max_passes)


__all__ = [
    "FederateStartupConfig",
    "FederateStartupResult",
    "FederationStartupConfig",
    "StartupResult",
    "achieve_startup_sync_point",
    "connect_create_join",
    "drain_callbacks",
    "evoke_all_callbacks",
    "register_startup_sync_point",
    "synchronize_ready_to_run",
]
