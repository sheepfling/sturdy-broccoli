"""Factory helpers for Java-profile CERTI backends."""
from __future__ import annotations

from hla2010_rti_java_common import BackendInfo
from hla2010_rti_certi.certi import CERTIConfig
from hla2010_rti_java_common.java_common import JavaRTIBackend
from hla2010_rti_java_common.java_shim_backend import ShimJavaBridge
from .adapter import CERTIJavaRTIShim
from .runtime import CERTIJavaValueConverter


def create_certi_java_backend(profile: str, config: CERTIConfig = CERTIConfig()) -> JavaRTIBackend:
    bridge = ShimJavaBridge(profile)
    info = BackendInfo(
        name="CERTI",
        kind=f"java/{profile}/certi-shim",
        version=None,
        details={"profile": profile, "transport": "native-certi"},
    )
    return JavaRTIBackend(
        java_rti_ambassador=CERTIJavaRTIShim(profile=profile, config=config),
        bridge=bridge,
        converter=CERTIJavaValueConverter(bridge),
        info=info,
    )


__all__ = ["create_certi_java_backend"]
