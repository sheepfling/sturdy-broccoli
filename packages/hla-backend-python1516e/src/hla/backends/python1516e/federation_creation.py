"""Connection and federation create/destroy services."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Protocol

from hla.rti1516e.enums import CallbackModel
from hla.rti1516e.exceptions import (
    AlreadyConnected,
    DesignatorIsHLAstandardMIM,
    FederateIsExecutionMember,
    FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist,
    FederatesCurrentlyJoined,
)
from hla.fom import standard_mim_module
from hla.rti1516e import NullFederateAmbassador
from hla.rti1516e.time import TimeFactoryRegistry
from hla.rti1516e.datatypes import FederationExecutionInformation

from . import mom_catalog as mom_table
from .state import FederationState

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine
    from .state import FederateState, PythonRTIConfig


class _FederationCreationContext(Protocol):
    engine: "InMemoryRTIEngine"
    state: "FederateState"
    config: "PythonRTIConfig"

    def _require_connected(self) -> None: ...

    def _deliver(self, target: "FederateState", method_name: str, *args: Any) -> None: ...

    def _resolve_fom_modules(
        self,
        sources: Iterable[Any],
        *,
        require_non_empty: bool = False,
        mim: bool = False,
    ) -> tuple[Any, ...]: ...

    def _combine_fom_catalog(self, modules: Iterable[Any], *, mim_module: Any | None = None, base_catalog: Any | None = None) -> Any: ...

    def _choose_time_factory(self, requested_name: str | None, modules: Iterable[Any]) -> Any: ...

    def _ensure_mom_federation_object(self, federation: FederationState) -> None: ...


if TYPE_CHECKING:
    class _FederationCreationMixinBase(_FederationCreationContext):
        pass
else:
    class _FederationCreationMixinBase:
        pass


def _is_non_string_sequence(value: Any) -> bool:
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return False
    return isinstance(value, Iterable)


def _as_tuple(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if _is_non_string_sequence(value):
        return tuple(value)
    return (value,)


def _looks_like_time_factory_name(value: Any, registry: TimeFactoryRegistry) -> bool:
    return isinstance(value, str) and value in registry


def _parse_create_federation_args(
    raw_args: tuple[Any, ...],
    *,
    registry: TimeFactoryRegistry,
    default_time_name: str,
) -> tuple[tuple[Any, ...], Any | None, str | None]:
    del default_time_name
    foms: tuple[Any, ...] = ()
    mim: Any | None = None
    time_name: str | None = None
    args = tuple(raw_args)

    if not args:
        return foms, mim, time_name
    if len(args) == 1:
        if _looks_like_time_factory_name(args[0], registry):
            return (), None, str(args[0])
        return _as_tuple(args[0]), None, time_name
    if len(args) == 2:
        first, second = args
        if _looks_like_time_factory_name(second, registry):
            return _as_tuple(first), None, str(second)
        return _as_tuple(first), second, time_name
    if len(args) == 3:
        first, second, third = args
        if _looks_like_time_factory_name(third, registry):
            return _as_tuple(first), second, str(third)
        return args, None, time_name
    if _looks_like_time_factory_name(args[-1], registry):
        return tuple(args[:-1]), None, str(args[-1])
    return args, None, time_name


class PythonRTIFederationCreationMixin(_FederationCreationMixinBase):
    """Connection and federation creation/destruction services."""

    def _svc_connect(
        self,
        federateReference: NullFederateAmbassador,
        callbackModel: CallbackModel,
        localSettingsDesignator: str | None = None,
    ) -> None:
        if self.state.connected:
            raise AlreadyConnected("RTI ambassador is already connected")
        self.state.ambassador = federateReference
        self.state.callback_model = callbackModel
        self.state.local_settings_designator = localSettingsDesignator
        self.state.connected = True

    def _svc_disconnect(self) -> None:
        self._require_connected()
        if self.state.handle is not None:
            raise FederateIsExecutionMember("Resign before disconnecting")
        self.state.connected = False
        self.state.ambassador = None
        self.state.queue.clear()

    def _svc_createFederationExecution(
        self,
        federationExecutionName: str,
        *fomModules: Any,
    ) -> None:
        self._require_connected()
        fom_sources, mim_source, time_name = _parse_create_federation_args(
            tuple(fomModules),
            registry=self.engine.time_factories,
            default_time_name=self.config.default_logical_time_implementation_name,
        )
        if str(mim_source) == "HLAstandardMIM":
            raise DesignatorIsHLAstandardMIM(
                "Explicit MIM designator shall not be HLAstandardMIM"
            )
        require_foms = self.config.require_fom_modules or bool(fom_sources)
        resolved_foms = self._resolve_fom_modules(
            fom_sources,
            require_non_empty=require_foms,
        )
        resolved_mim = (
            self._resolve_fom_modules((mim_source,), mim=True)[0]
            if mim_source is not None
            else standard_mim_module()
        )
        catalog = self._combine_fom_catalog(resolved_foms, mim_module=resolved_mim)
        time_modules = tuple(
            module
            for module in ((resolved_mim,) if resolved_mim is not None else ()) + tuple(resolved_foms)
            if module is not None
        )
        time_factory = self._choose_time_factory(time_name, time_modules)
        with self.engine._lock:
            if federationExecutionName in self.engine.federations:
                raise FederationExecutionAlreadyExists(str(federationExecutionName))
            self.engine.install_fom_modules(
                [
                    module
                    for module in ((resolved_mim,) if resolved_mim is not None else ())
                    + tuple(resolved_foms)
                    if module is not None
                ]
            )
            federation = FederationState(
                name=str(federationExecutionName),
                fom_modules=tuple(resolved_foms),
                mim_module=resolved_mim,
                fom_catalog=catalog,
                mom_model=mom_table.build_mom_exposure_model(catalog),
                time_factory=time_factory,
            )
            self.engine.federations[str(federationExecutionName)] = federation
            self._ensure_mom_federation_object(federation)

    def _svc_createFederationExecutionWithMIM(
        self,
        federationExecutionName: str,
        *fomModules: Any,
    ) -> None:
        self._svc_createFederationExecution(federationExecutionName, *fomModules)

    def _svc_destroyFederationExecution(self, federationExecutionName: str) -> None:
        self._require_connected()
        with self.engine._lock:
            federation = self.engine.federations.get(str(federationExecutionName))
            if federation is None:
                raise FederationExecutionDoesNotExist(str(federationExecutionName))
            if federation.federates:
                raise FederatesCurrentlyJoined(str(federationExecutionName))
            del self.engine.federations[str(federationExecutionName)]

    def _svc_listFederationExecutions(self) -> None:
        self._require_connected()
        infos = {
            FederationExecutionInformation(
                federation.name,
                federation.time_factory.get_name(),
            )
            for federation in self.engine.federations.values()
        }
        self._deliver(self.state, "reportFederationExecutions", infos)
