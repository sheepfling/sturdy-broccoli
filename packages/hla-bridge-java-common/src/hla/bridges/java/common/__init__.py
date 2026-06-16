"""Shared Java RTI support package."""
from __future__ import annotations

from hla.backends.common import (
    BACKEND_ENTRY_POINT_GROUP,
    BackendInfo,
    BackendUnavailableError,
    CALLBACK_METHOD_NAMES,
    Invocation,
    RTIBackend,
    RTIBackendPlugin,
    RTIBackendSpec,
    RTITransportSpec,
    UnsupportedBackendService,
    make_rti_ambassador,
)
from .java_common import (
    JavaBridge,
    JavaRTIBackend,
    JavaValueConverter,
    PythonFederateAmbassadorDispatcher,
    ResolvedJavaInvocation,
    java_parameter_names,
    java_parameter_types,
    resolve_java_arguments,
    resolve_java_invocation,
)
from .java_runtime import discover_java_home, discover_java_tool, ensure_java_home
from .py4j_support import reset_py4j_callback_client
from .java_shim_backend import InProcessJavaRTIShim, ShimJavaBridge
from .java_shim_factory import create_java_shim_backend, create_shared_java_shim_backend
from .java_factory_selection import JavaRTIDiscoveryReport, JavaRTIFactorySelection, create_java_backend, create_java_rti_ambassador, discover_java_rti
from .java_shim_kernel import SharedJavaShimKernel
from .java_shim_runtime import SharedInProcessJavaRTIShim
from .java_shim_types import JavaByteArray, JavaLikeException, JavaLikeObject

__all__ = [
    "BACKEND_ENTRY_POINT_GROUP",
    "BackendInfo",
    "BackendUnavailableError",
    "CALLBACK_METHOD_NAMES",
    "Invocation",
    "JavaBridge",
    "JavaByteArray",
    "JavaLikeException",
    "JavaLikeObject",
    "RTIBackend",
    "RTIBackendPlugin",
    "RTIBackendSpec",
    "JavaRTIBackend",
    "RTITransportSpec",
    "JavaValueConverter",
    "InProcessJavaRTIShim",
    "PythonFederateAmbassadorDispatcher",
    "ResolvedJavaInvocation",
    "SharedInProcessJavaRTIShim",
    "SharedJavaShimKernel",
    "ShimJavaBridge",
    "UnsupportedBackendService",
    "JavaRTIDiscoveryReport",
    "JavaRTIFactorySelection",
    "create_java_shim_backend",
    "create_java_backend",
    "create_java_rti_ambassador",
    "create_shared_java_shim_backend",
    "discover_java_rti",
    "discover_java_home",
    "discover_java_tool",
    "ensure_java_home",
    "java_parameter_names",
    "java_parameter_types",
    "make_rti_ambassador",
    "resolve_java_arguments",
    "resolve_java_invocation",
    "reset_py4j_callback_client",
]
