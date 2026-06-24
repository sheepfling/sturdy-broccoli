"""FOM resolution and catalog helpers for the Python RTI backend."""
from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable

from hla.rti1516e.exceptions import (
    CouldNotCreateLogicalTimeFactory,
    CouldNotOpenFDD,
    CouldNotOpenMIM,
    ErrorReadingFDD,
    ErrorReadingMIM,
    InconsistentFDD,
    InvalidLogicalTime,
    InvalidLookahead,
)
from hla.fom import FOMCatalog, FOMMergeError, FOMModule, FOMResolutionError, merge_fom_modules, standard_mim_module
from hla.rti1516e.time import LogicalTimeFactory
from .state import FederationState


class PythonRTIFomMixin:
    """FOM resolution, merge, and summary helpers."""

    def _resolve_fom_modules(
        self,
        sources: Iterable[Any] | Any | None,
        *,
        require_non_empty: bool = False,
        mim: bool = False,
    ) -> tuple[FOMModule, ...]:
        try:
            modules = self.fom_resolver.resolve_many(sources)
            if mim:
                modules = tuple(replace(module, is_mim=True) for module in modules)
            if require_non_empty and not modules:
                raise FOMResolutionError("At least one FOM module designator is required")
            if self.config.require_fom_parse or self.config.strict_fom_loading:
                for module in modules:
                    if module.uri.startswith("builtin:"):
                        continue
                    if not module.parsed:
                        raise FOMResolutionError(
                            f"FOM module could not be parsed locally by the Python RTI: {module.uri}",
                            kind="read",
                        )
            return modules
        except FOMResolutionError as exc:
            kind = getattr(exc, "kind", "open")
            if mim:
                if kind == "read":
                    raise ErrorReadingMIM(str(exc)) from exc
                raise CouldNotOpenMIM(str(exc)) from exc
            if kind == "read":
                raise ErrorReadingFDD(str(exc)) from exc
            raise CouldNotOpenFDD(str(exc)) from exc

    def _combine_fom_catalog(
        self,
        modules: Iterable[FOMModule],
        *,
        mim_module: FOMModule | None = None,
        base_catalog: FOMCatalog | None = None,
    ) -> FOMCatalog:
        try:
            base_modules = tuple(base_catalog.modules) if base_catalog is not None else ()
            effective_mim = mim_module if mim_module is not None else (base_catalog.mim_module if base_catalog is not None else standard_mim_module())
            return merge_fom_modules((*base_modules, *tuple(modules)), mim_module=effective_mim)
        except FOMMergeError as exc:
            raise InconsistentFDD(str(exc)) from exc

    def _current_fom_summary(self, federation: FederationState | None = None) -> dict[str, Any]:
        federation = federation or self._require_joined()
        return federation.fom_catalog.as_summary()

    def _choose_time_factory(self, requested_name: str | None, modules: Iterable[FOMModule]) -> LogicalTimeFactory[Any, Any]:
        name = requested_name or self.config.default_logical_time_implementation_name
        if self.config.infer_time_factory_from_fom and not requested_name:
            for module in modules:
                if module.inferred_time_implementation:
                    name = module.inferred_time_implementation
                    break
        try:
            return self.engine.time_factories.get(name)
        except KeyError as exc:
            raise CouldNotCreateLogicalTimeFactory(str(exc)) from exc

    def _coerce_time(self, value: Any) -> Any:
        try:
            return self._time_factory().coerce_time(value)
        except Exception as exc:
            raise InvalidLogicalTime(repr(value)) from exc

    def _coerce_interval(self, value: Any) -> Any:
        try:
            return self._time_factory().coerce_interval(value)
        except Exception as exc:
            raise InvalidLookahead(repr(value)) from exc


__all__ = ["PythonRTIFomMixin"]
