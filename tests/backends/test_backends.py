from hla2010.runtime_api import FederateAmbassador
from hla2010.backends import RecordingBackend, make_rti_ambassador
from hla2010.backends.base import DelegatingRTIAmbassador, lower_camel_to_snake, snake_to_lower_camel
from hla2010_rti_java_common import java_parameter_names, resolve_java_arguments
from hla2010.enums import CallbackModel
from hla2010.raw_api import API_METADATA


def test_delegating_ambassador_is_concrete():
    backend = RecordingBackend(results={"getFederateName": "fed"})
    rti = make_rti_ambassador(backend)
    assert isinstance(rti, DelegatingRTIAmbassador)
    assert rti.getFederateName() == "fed"
    assert backend.calls[-1].method_name == "getFederateName"


def test_snake_case_alias_forwards_to_source_method():
    backend = RecordingBackend(results={"createRegion": "region"})
    rti = make_rti_ambassador(backend)
    assert rti.create_region("space", {"dimension"}) == "region"
    call = backend.calls[-1]
    assert call.method_name == "createRegion"
    assert call.args == ("space", {"dimension"})


def test_connect_adapts_python_federate_ambassador():
    class Backend(RecordingBackend):
        def adapt_federate_ambassador(self, ambassador):
            return ("adapted", ambassador)

    federate = FederateAmbassador()
    backend = Backend()
    rti = make_rti_ambassador(backend)
    rti.connect(federate, CallbackModel.HLA_EVOKED)
    assert backend.calls[-1].method_name == "connect"
    assert backend.calls[-1].args[0] == ("adapted", federate)


def test_keyword_resolution_uses_java_overload_metadata():
    overloads = tuple(API_METADATA["RTIambassador"]["destroyFederationExecution"])
    from hla2010.backends.base import Invocation

    invocation = Invocation(
        method_name="destroyFederationExecution",
        args=(),
        kwargs={"federation_execution_name": "demo"},
        overloads=overloads,
    )
    assert resolve_java_arguments(invocation) == ("demo",)


def test_java_parameter_names_parser():
    overload = {
        "params": "String federationExecutionName, URL[] fomModules, byte[] userSuppliedTag"
    }
    assert java_parameter_names(overload) == (
        "federationExecutionName",
        "fomModules",
        "userSuppliedTag",
    )


def test_case_conversion_helpers():
    assert lower_camel_to_snake("getObjectClassHandle") == "get_object_class_handle"
    assert lower_camel_to_snake("getHLAversion") == "get_hla_version"
    assert snake_to_lower_camel("get_object_class_handle") == "getObjectClassHandle"


def test_native_handle_registry_uses_java_hash_semantics():
    from hla2010_rti_backend_common import NativeHandleRegistry
    from hla2010.handles import ObjectClassHandle

    class JavaLikeHandle:
        def __init__(self, value):
            self.value = value
        def hashCode(self):
            return self.value
        def getClass(self):
            class C:
                def getName(self):
                    return "hla.rti1516e.ObjectClassHandle"
            return C()

    registry = NativeHandleRegistry()
    a = registry.to_python(ObjectClassHandle, JavaLikeHandle(42))
    b = registry.to_python(ObjectClassHandle, JavaLikeHandle(42))
    assert a == b
