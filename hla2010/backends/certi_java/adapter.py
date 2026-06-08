"""Adapter classes for Java-profile CERTI backends."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ...runtime_api import FederateAmbassador
from ..base import CALLBACK_METHOD_NAMES, lower_camel_to_snake, make_rti_ambassador
from ..certi import CERTIConfig, create_certi_backend
from .runtime import from_java_like, to_java_like


class _CERTIJavaFederateAdapter(FederateAmbassador):
    """Adapter that forwards native CERTI callbacks into a Java-style proxy."""

    def __init__(self, java_proxy: Any) -> None:
        self._java_proxy = java_proxy

    def _forward_callback(self, method_name: str, *args: Any) -> Any:
        callback = getattr(self._java_proxy, method_name)
        return callback(*(to_java_like(arg) for arg in args))


def _make_adapter_callback(method_name: str):
    def _callback(self: _CERTIJavaFederateAdapter, *args: Any) -> Any:
        return self._forward_callback(method_name, *args)

    _callback.__name__ = method_name
    _callback.__qualname__ = f"_CERTIJavaFederateAdapter.{method_name}"
    return _callback


for _callback_name in CALLBACK_METHOD_NAMES:
    setattr(_CERTIJavaFederateAdapter, _callback_name, _make_adapter_callback(_callback_name))
    setattr(_CERTIJavaFederateAdapter, lower_camel_to_snake(_callback_name), _make_adapter_callback(_callback_name))


@dataclass
class CERTIJavaRTIShim:
    """Java-shaped facade for a real CERTI-backed RTI ambassador."""

    profile: str
    config: CERTIConfig = CERTIConfig()

    def __post_init__(self) -> None:
        self._rti = make_rti_ambassador(create_certi_backend(self.config))
        self._java_proxy = None

    def __getattr__(self, name: str):
        target = getattr(self._rti, name, None)
        if target is None:
            raise AttributeError(name)

        def _invoke(*args: Any) -> Any:
            py_args = tuple(from_java_like(arg) for arg in args)
            result = target(*py_args)
            return to_java_like(result)

        return _invoke

    def connect(self, federateReference: Any, callbackModel: Any, localSettingsDesignator: str | None = None) -> None:
        self._java_proxy = federateReference
        python_ambassador = _CERTIJavaFederateAdapter(federateReference)
        callback_model = from_java_like(callbackModel)
        if localSettingsDesignator is None:
            self._rti.connect(python_ambassador, callback_model)
        else:
            self._rti.connect(python_ambassador, callback_model, localSettingsDesignator)

    def close(self) -> None:
        self._rti.close()

    def getHLAversion(self) -> str:
        return self._rti.getHLAversion()


__all__ = ["CERTIJavaRTIShim", "_CERTIJavaFederateAdapter"]
