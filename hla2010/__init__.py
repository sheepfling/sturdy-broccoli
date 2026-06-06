"""Unofficial Python scaffold for IEEE 1516.1-2010 HLA APIs.

This package is an API surface and utility scaffold, not a complete RTI.
Attribution: "Reprinted with permission from IEEE 1516.1(TM)-2010".
"""
from .enums import *
from .exceptions import *
from .handles import *
from .time import *
from .types import *
from .fom import *
from .spec_refs import *
from .ambassadors import CallbackRecord, FederateAmbassadorMultiplexer, RecordingFederateAmbassador, NullFederateAmbassador
from .api import RTIambassador, RTIAmbassador, FederateAmbassador
from .backends import (
    BackendInfo,
    DelegatingRTIAmbassador,
    InMemoryRTIEngine,
    PythonRTIBackend,
    PythonRTIConfig,
    RTIBackend,
    CERTITransportRequest,
    CERTITransportResponse,
    RestTransport,
    RestTransportConfig,
    RecordingBackend,
    TransportCodec,
    TransportRequest,
    TransportResponse,
    create_python_backend,
    create_rest_transport,
    make_rti_ambassador,
)
from .rti import (
    RTIBackendSpec,
    RTITransportSpec,
    create_backend,
    create_python_rti_pair,
    create_rti_ambassador,
    register_transport_factory,
)
from .real_rti import (
    CERTIRuntime,
    PitchRuntime,
    RuntimeProcess,
    discover_certi_smoke_fom,
    discover_certi_runtime,
    discover_pitch_runtime,
    launch_certi_rtig,
    launch_pitch_py4j_gateway,
    launch_pitch_runtime,
)
from .verification import VerificationAsset, VerificationPlan, build_verification_plan, write_verification_assets
from .startup import (
    FederateStartupConfig,
    FederateStartupResult,
    FederationStartupConfig,
    StartupResult,
    achieve_startup_sync_point,
    connect_create_join,
    drain_callbacks,
    evoke_all_callbacks,
    register_startup_sync_point,
    synchronize_ready_to_run,
)

__version__ = '0.12.0'
