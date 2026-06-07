"""Unofficial Python scaffold for IEEE 1516.1-2010 HLA APIs.

This package is an API surface and utility scaffold, not a complete RTI.
Attribution: "Reprinted with permission from IEEE 1516.1(TM)-2010".
"""
from . import enums as _enums
from . import exceptions as _exceptions
from . import fom as _fom
from . import handles as _handles
from . import spec_refs as _spec_refs
from . import time as _time
from . import types as _types
from .ambassadors import (
    CallbackRecord as CallbackRecord,
)
from .ambassadors import (
    FederateAmbassadorMultiplexer as FederateAmbassadorMultiplexer,
)
from .ambassadors import (
    NullFederateAmbassador as NullFederateAmbassador,
)
from .ambassadors import (
    RecordingFederateAmbassador as RecordingFederateAmbassador,
)
from .api import (
    FederateAmbassador as FederateAmbassador,
)
from .api import (
    RTIAmbassador as RTIAmbassador,
)
from .api import (
    RTIambassador as RTIambassador,
)
from .backends import (
    BackendInfo as BackendInfo,
)
from .backends import (
    CERTITransportRequest as CERTITransportRequest,
)
from .backends import (
    CERTITransportResponse as CERTITransportResponse,
)
from .backends import (
    DelegatingRTIAmbassador as DelegatingRTIAmbassador,
)
from .backends import (
    InMemoryRTIEngine as InMemoryRTIEngine,
)
from .backends import (
    PythonRTIBackend as PythonRTIBackend,
)
from .backends import (
    PythonRTIConfig as PythonRTIConfig,
)
from .backends import (
    RecordingBackend as RecordingBackend,
)
from .backends import (
    RestTransport as RestTransport,
)
from .backends import (
    RestTransportConfig as RestTransportConfig,
)
from .backends import (
    RTIBackend as RTIBackend,
)
from .backends import (
    TransportRequest as TransportRequest,
)
from .backends import (
    TransportResponse as TransportResponse,
)
from .backends import (
    create_python_ambassador as create_python_ambassador,
)
from .backends import (
    create_python_backend as create_python_backend,
)
from .backends import (
    create_rest_transport as create_rest_transport,
)
from .backends import (
    make_rti_ambassador as make_rti_ambassador,
)
from .real_rti import (
    CERTIRuntime as CERTIRuntime,
)
from .real_rti import (
    PitchRuntime as PitchRuntime,
)
from .real_rti import (
    PorticoRuntime as PorticoRuntime,
)
from .real_rti import (
    RuntimeProcess as RuntimeProcess,
)
from .real_rti import (
    discover_certi_runtime as discover_certi_runtime,
)
from .real_rti import (
    discover_certi_smoke_fom as discover_certi_smoke_fom,
)
from .real_rti import (
    discover_pitch_runtime as discover_pitch_runtime,
)
from .real_rti import (
    launch_certi_rtig as launch_certi_rtig,
)
from .real_rti import (
    launch_pitch_py4j_gateway as launch_pitch_py4j_gateway,
)
from .real_rti import (
    launch_pitch_runtime as launch_pitch_runtime,
)
from .rti import (
    RTIBackendSpec as RTIBackendSpec,
)
from .rti import (
    RTITransportSpec as RTITransportSpec,
)
from .rti import (
    create_backend as create_backend,
)
from .rti import (
    create_python_pair as create_python_pair,
)
from .rti import (
    create_rti_ambassador as create_rti_ambassador,
)
from .rti import (
    register_transport_factory as register_transport_factory,
)
from .startup import (
    FederateStartupConfig as FederateStartupConfig,
)
from .startup import (
    FederateStartupResult as FederateStartupResult,
)
from .startup import (
    FederationStartupConfig as FederationStartupConfig,
)
from .startup import (
    StartupResult as StartupResult,
)
from .startup import (
    achieve_startup_sync_point as achieve_startup_sync_point,
)
from .startup import (
    connect_create_join as connect_create_join,
)
from .startup import (
    drain_callbacks as drain_callbacks,
)
from .startup import (
    evoke_all_callbacks as evoke_all_callbacks,
)
from .startup import (
    register_startup_sync_point as register_startup_sync_point,
)
from .startup import (
    synchronize_ready_to_run as synchronize_ready_to_run,
)
from .verification import (
    VerificationAsset as VerificationAsset,
)
from .verification import (
    VerificationPlan as VerificationPlan,
)
from .verification import (
    build_verification_plan as build_verification_plan,
)
from .verification import (
    write_verification_assets as write_verification_assets,
)

for _module in (_enums, _exceptions, _fom, _handles, _spec_refs, _time, _types):
    globals().update({name: getattr(_module, name) for name in _module.__all__})

__version__ = '0.12.0'
