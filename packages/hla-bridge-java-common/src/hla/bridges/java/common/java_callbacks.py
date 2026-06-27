"""Java FederateAmbassador callback dispatch helpers."""
from __future__ import annotations

from typing import Any

from hla.backends.common import CALLBACK_METHOD_NAMES, Invocation, clean_java_type_name
from .java_binding_profile import load_python_java_binding_profile

_DEFAULT_BINDING = load_python_java_binding_profile("2010")
hla_exceptions = _DEFAULT_BINDING.exceptions_module
FederateInternalError = hla_exceptions.FederateInternalError

_CALLBACK_TYPE_FALLBACKS: dict[str, tuple[str | None, ...]] = {
    "federationSynchronized": ("String", "FederateHandleSet"),
}


def _clean_java_type(type_name: str | None) -> str | None:
    return clean_java_type_name(type_name)


def expected_java_return_type(invocation: Invocation) -> str | None:
    return_types = {
        _clean_java_type(str(o.get("return_type", "")).strip()) or ""
        for o in invocation.overloads
        if o.get("language") == "java" and str(o.get("return_type", "")).strip() not in {"", "void"}
    }
    return_types.discard("")
    if len(return_types) == 1:
        return next(iter(return_types))
    return None


def expected_java_callback_parameter_types(
    method_name: str,
    arg_count: int | None = None,
    *,
    binding: Any | None = None,
) -> tuple[str | None, ...]:
    resolved = (binding or _DEFAULT_BINDING).callback_parameter_types(method_name, arg_count)
    if resolved:
        return resolved
    fallback = _CALLBACK_TYPE_FALLBACKS.get(method_name)
    if fallback is None:
        return ()
    if arg_count is None:
        return fallback
    return fallback[:arg_count]


class PythonFederateAmbassadorDispatcher:
    """Dispatch Java FederateAmbassador callbacks to a Python ambassador."""

    def __init__(self, ambassador: Any, converter: Any):
        self.ambassador = ambassador
        self.converter = converter

    def _invoke_callback(self, method_name: str, *backend_args: Any) -> Any:
        try:
            expected = expected_java_callback_parameter_types(method_name, len(backend_args), binding=self.converter.python_binding)
            py_args = tuple(
                self.converter.from_backend(arg, expected_type_name=expected[idx] if idx < len(expected) else None)
                for idx, arg in enumerate(backend_args)
            )
            result = getattr(self.ambassador, method_name)(*py_args)
            return self.converter.to_backend(result) if result is not None else None
        except FederateInternalError:
            raise
        except BaseException as exc:
            raise FederateInternalError(f"Python FederateAmbassador.{method_name} failed: {exc}", cause=exc) from exc


for _callback_name in CALLBACK_METHOD_NAMES:
    if not hasattr(PythonFederateAmbassadorDispatcher, _callback_name):
        setattr(
            PythonFederateAmbassadorDispatcher,
            _callback_name,
            lambda self, *args, _method_name=_callback_name: self._invoke_callback(_method_name, *args),
        )


__all__ = [
    "PythonFederateAmbassadorDispatcher",
    "expected_java_callback_parameter_types",
    "expected_java_return_type",
]
