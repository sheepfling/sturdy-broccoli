"""Backend adapters for the HLA 1516.1-2010 Python API scaffold.

The base adapter has no optional dependencies. JPype and Py4J adapters are
imported explicitly from their modules so importing ``hla2010.backends`` does not
require a Java bridge package.
"""
from .base import (
    BackendConversionError,
    BackendInfo,
    BackendUnavailableError,
    CALLBACK_METHOD_NAMES,
    DelegatingRTIAmbassador,
    Invocation,
    RTIBackend,
    RTI_METHOD_NAMES,
    RecordingBackend,
    UnsupportedBackendService,
    lower_camel_to_snake,
    make_rti_ambassador,
    snake_to_lower_camel,
)
from .conversion import NativeHandleRegistry, NativeObjectRef, ValueConverter
from .java_common import JavaBridge, JavaRTIBackend, JavaValueConverter, PythonFederateAmbassadorDispatcher
from ..real_rti import CERTIRuntime, PitchRuntime, discover_certi_runtime, discover_pitch_runtime, launch_pitch_py4j_gateway
from .python_rti import (
    InMemoryRTIEngine,
    PythonRTIBackend,
    PythonRTIConfig,
    SupplementalReflectInfo,
    SupplementalReceiveInfo,
    SupplementalRemoveInfo,
    create_python_backend,
    rti_ambassador as python_rti_ambassador,
)

__all__ = [
    "BackendConversionError",
    "BackendInfo",
    "BackendUnavailableError",
    "CALLBACK_METHOD_NAMES",
    "DelegatingRTIAmbassador",
    "InMemoryRTIEngine",
    "Invocation",
    "JavaBridge",
    "JavaRTIBackend",
    "JavaValueConverter",
    "CERTIRuntime",
    "NativeHandleRegistry",
    "NativeObjectRef",
    "PitchRuntime",
    "PythonFederateAmbassadorDispatcher",
    "PythonRTIBackend",
    "PythonRTIConfig",
    "RTIBackend",
    "RTI_METHOD_NAMES",
    "RecordingBackend",
    "discover_certi_runtime",
    "discover_pitch_runtime",
    "launch_pitch_py4j_gateway",
    "SupplementalReflectInfo",
    "SupplementalReceiveInfo",
    "SupplementalRemoveInfo",
    "UnsupportedBackendService",
    "ValueConverter",
    "create_python_backend",
    "lower_camel_to_snake",
    "make_rti_ambassador",
    "python_rti_ambassador",
    "snake_to_lower_camel",
]
