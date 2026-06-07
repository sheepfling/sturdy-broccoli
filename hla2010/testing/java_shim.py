"""In-process Java-shaped RTI shim used by tests and examples."""
from __future__ import annotations

from .java_shim_backend import InProcessJavaRTIShim, ShimJavaBridge
from .java_shim_factory import (
    create_java_shim_backend,
    create_java_shim_rti_ambassador,
    create_shared_java_shim_backend,
    create_shared_java_shim_rti_ambassador,
)
from .java_shim_kernel import (
    SharedInProcessJavaRTIShim,
    SharedJavaFederationRecord,
    SharedJavaObjectRecord,
    SharedJavaShimKernel,
)
from .java_shim_types import (
    JavaAttributeHandle,
    JavaByteArray,
    JavaClassInfo,
    JavaDimensionHandle,
    JavaEnumConstant,
    JavaFederateHandle,
    JavaHLAfloat64Interval,
    JavaHLAfloat64Time,
    JavaHLAinteger64Interval,
    JavaHLAinteger64Time,
    JavaInteractionClassHandle,
    JavaLikeException,
    JavaLikeObject,
    JavaObjectClassHandle,
    JavaObjectInstanceHandle,
    JavaParameterHandle,
    JavaRegionHandle,
    JavaTransportationTypeHandle,
)

__all__ = [
    "InProcessJavaRTIShim",
    "JavaAttributeHandle",
    "JavaByteArray",
    "JavaClassInfo",
    "JavaDimensionHandle",
    "JavaEnumConstant",
    "JavaFederateHandle",
    "JavaHLAfloat64Interval",
    "JavaHLAfloat64Time",
    "JavaHLAinteger64Interval",
    "JavaHLAinteger64Time",
    "JavaInteractionClassHandle",
    "JavaLikeException",
    "JavaLikeObject",
    "JavaObjectClassHandle",
    "JavaObjectInstanceHandle",
    "JavaParameterHandle",
    "JavaRegionHandle",
    "JavaTransportationTypeHandle",
    "SharedInProcessJavaRTIShim",
    "SharedJavaFederationRecord",
    "SharedJavaObjectRecord",
    "SharedJavaShimKernel",
    "ShimJavaBridge",
    "create_java_shim_backend",
    "create_java_shim_rti_ambassador",
    "create_shared_java_shim_backend",
    "create_shared_java_shim_rti_ambassador",
]
