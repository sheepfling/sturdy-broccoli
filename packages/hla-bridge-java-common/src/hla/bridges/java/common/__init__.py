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
from .java_toolchain import (
    JAVA_2010_JAR,
    JAVA_2025_JAR,
    JavaToolchainArtifact,
    JavaToolchainInventory,
    discover_java_toolchain,
    render_java_toolchain_markdown,
    write_java_toolchain_reports,
)
from .py4j_support import reset_py4j_callback_client
from .java_shim_backend import InProcessJavaRTIShim, ShimJavaBridge
from .java_shim_factory import create_java_shim_backend, create_shared_java_shim_backend
from .java_factory_selection import JavaRTIDiscoveryReport, JavaRTIFactorySelection, create_java_backend, create_java_rti_ambassador, discover_java_rti
from .java_intake import (
    JAVA_2010,
    JAVA_2025,
    JavaApiProfile,
    JavaRtiIntakeReport,
    JavaRtiIntakeRequest,
    discover_java_rti_jar,
    java_api_profile,
    split_classpath,
    validate_classpath,
    write_intake_reports,
)
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
    "JavaToolchainArtifact",
    "JavaToolchainInventory",
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
    "JAVA_2010",
    "JAVA_2025",
    "JavaApiProfile",
    "JavaRtiIntakeReport",
    "JavaRtiIntakeRequest",
    "create_java_shim_backend",
    "create_java_backend",
    "create_java_rti_ambassador",
    "create_shared_java_shim_backend",
    "discover_java_rti_jar",
    "discover_java_rti",
    "discover_java_home",
    "discover_java_tool",
    "discover_java_toolchain",
    "ensure_java_home",
    "JAVA_2010_JAR",
    "JAVA_2025_JAR",
    "java_api_profile",
    "java_parameter_names",
    "java_parameter_types",
    "make_rti_ambassador",
    "resolve_java_arguments",
    "resolve_java_invocation",
    "reset_py4j_callback_client",
    "split_classpath",
    "validate_classpath",
    "render_java_toolchain_markdown",
    "write_intake_reports",
    "write_java_toolchain_reports",
]
