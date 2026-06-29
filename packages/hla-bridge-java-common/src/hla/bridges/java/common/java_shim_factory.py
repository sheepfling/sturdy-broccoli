"""Factory helpers for Java-shaped shim backends."""
# pyright: reportMissingImports=false
from __future__ import annotations

from hla.backends.common import BackendInfo, make_rti_ambassador

from .java_common import JavaRTIBackend
from .java_shim_backend import InProcessJavaRTIShim, ShimJavaBridge
from .java_shim_kernel import SharedJavaShimKernel
from .java_shim_runtime import SharedInProcessJavaRTIShim


def create_java_shim_backend(profile: str = "jpype") -> JavaRTIBackend:
    bridge = ShimJavaBridge(profile)
    info = BackendInfo(
        name=f"inprocess-{profile}-java-shim",
        kind=f"java/{profile}/shim",
        version="0.5",
        details={"profile": profile, "implementation": "Python Java-shaped RTI shim"},
    )
    return JavaRTIBackend(java_rti_ambassador=InProcessJavaRTIShim(), bridge=bridge, info=info)


def create_java_shim_rti_ambassador(profile: str = "jpype"):
    return make_rti_ambassador(create_java_shim_backend(profile))


def create_shared_java_shim_backend(profile: str = "jpype", kernel: SharedJavaShimKernel | None = None) -> JavaRTIBackend:
    bridge = ShimJavaBridge(profile)
    info = BackendInfo(
        name=f"shared-inprocess-{profile}-java-shim",
        kind=f"java/{profile}/shared-shim",
        version="0.6",
        details={"profile": profile, "implementation": "shared Python Java-shaped RTI shim"},
    )
    return JavaRTIBackend(java_rti_ambassador=SharedInProcessJavaRTIShim(kernel), bridge=bridge, info=info)


def create_shared_java_shim_rti_ambassador(profile: str = "jpype", kernel: SharedJavaShimKernel | None = None):
    return make_rti_ambassador(create_shared_java_shim_backend(profile, kernel))


__all__ = [
    "create_java_shim_backend",
    "create_java_shim_rti_ambassador",
    "create_shared_java_shim_backend",
    "create_shared_java_shim_rti_ambassador",
]
