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
    RecordingBackend,
    create_python_backend,
    make_rti_ambassador,
)
from .rti import RTIBackendSpec, create_backend, create_python_rti_pair, create_rti_ambassador
from .real_rti import CERTIRuntime, PitchRuntime, discover_certi_runtime, discover_pitch_runtime, launch_pitch_py4j_gateway
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
