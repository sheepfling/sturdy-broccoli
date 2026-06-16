from pathlib import Path

from hla.rti1516e.runtime_api import FederateAmbassador
from hla.rti1516e.backends.java_common import JavaBridge, JavaValueConverter, resolve_java_invocation
from hla.rti1516e.backends.base import Invocation
from hla.rti1516e.enums import CallbackModel, ResignAction
from hla.rti1516e.handles import AttributeHandle, AttributeHandleSet, AttributeHandleValueMap, DimensionHandleSet
from hla.rti1516e.raw_api import API_METADATA
from hla.rti1516e.rti import create_rti_ambassador
from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_RADAR_FOM = PROJECT_ROOT / "examples" / "target_radar" / "TargetRadarFOMmodule.xml"


def test_python_rti_resolves_fom_path_and_uses_requested_time_factory():
    rti = create_rti_ambassador("python")
    rti.connect(FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.create_federation_execution("fom-time-fed", TARGET_RADAR_FOM, "HLAfloat64Time")
    rti.join_federation_execution("tester", "test", "fom-time-fed")

    target_class = rti.get_object_class_handle("HLAobjectRoot.Target")
    assert rti.get_object_class_name(target_class) == "HLAobjectRoot.Target"
    rcs = rti.get_attribute_handle(target_class, "RCS")
    assert rti.get_attribute_name(target_class, rcs) == "RCS"

    track_report = rti.get_interaction_class_handle("HLAinteractionRoot.TrackReport")
    time_param = rti.get_parameter_handle(track_report, "Time")
    assert rti.get_parameter_name(track_report, time_param) == "Time"

    factory = rti.get_time_factory()
    assert factory.get_name() == "HLAfloat64Time"
    assert isinstance(rti.query_logical_time(), HLAfloat64Time)

    rti.enable_time_regulation(factory.make_interval(0.25))
    rti.evoke_multiple_callbacks(0.0, 0.0)
    assert rti.query_lookahead() == HLAfloat64Interval(0.25)

    rti.time_advance_request(factory.make_time(1.5))
    rti.evoke_multiple_callbacks(0.0, 0.0)
    assert rti.query_logical_time() == HLAfloat64Time(1.5)

    rti.resign_federation_execution(ResignAction.NO_ACTION)
    rti.destroy_federation_execution("fom-time-fed")
    rti.disconnect()


def test_python_rti_exposes_handle_set_and_map_factories():
    rti = create_rti_ambassador("python")
    rti.connect(FederateAmbassador(), CallbackModel.HLA_EVOKED)
    rti.create_federation_execution("factory-fed", "TargetRadarFOMmodule.xml")
    rti.join_federation_execution("tester", "test", "factory-fed")

    cls = rti.get_object_class_handle("HLAobjectRoot.Target")
    attr = rti.get_attribute_handle(cls, "RCS")

    attrs = rti.get_attribute_handle_set_factory().create()
    attrs.add(attr)
    assert isinstance(attrs, AttributeHandleSet)
    rti.publish_object_class_attributes(cls, attrs)

    values = rti.get_attribute_handle_value_map_factory().create(1)
    values[attr] = b"rcs"
    assert isinstance(values, AttributeHandleValueMap)
    obj = rti.register_object_instance(cls, "Target-Factory")
    rti.update_attribute_values(obj, values, b"tag")

    dim = rti.get_dimension_handle("HLAdefaultRoutingSpace")
    dims = rti.get_dimension_handle_set_factory().create()
    dims.add(dim)
    region = rti.create_region(dims)
    roundtrip_dims = rti.get_dimension_handle_set(region)
    assert isinstance(roundtrip_dims, DimensionHandleSet)
    assert dim in roundtrip_dims

    rti.resign_federation_execution(ResignAction.NO_ACTION)
    rti.destroy_federation_execution("factory-fed")
    rti.disconnect()


class RecordingBridge(JavaBridge):
    name = "recording-java"

    def __init__(self):
        self.calls = []

    def call(self, obj, method_name, *args):
        return None

    def create_federate_proxy(self, dispatcher):
        return dispatcher

    def enum_constant(self, enum_class_name, member_name):
        return (enum_class_name, member_name)

    def fom_url(self, value):
        self.calls.append(("url", value))
        return f"url:{value}"

    def fom_url_array(self, values):
        self.calls.append(("url_array", tuple(values)))
        return tuple(f"url:{value}" for value in values)

    def new_handle_set(self, type_name, values, *, rti_ambassador=None):
        self.calls.append(("handle_set", type_name, tuple(values), rti_ambassador is not None))
        return ("handle_set", type_name, tuple(values))

    def new_handle_value_map(self, type_name, items, *, rti_ambassador=None):
        self.calls.append(("handle_map", type_name, tuple(items), rti_ambassador is not None))
        return ("handle_map", type_name, tuple(items))


def test_java_overload_resolution_and_converter_prepare_vendor_owned_collections():
    overloads = tuple(API_METADATA["RTIambassador"]["createFederationExecution"])
    invocation = Invocation(
        method_name="createFederationExecution",
        args=("fed", [TARGET_RADAR_FOM], "HLAfloat64Time"),
        overloads=overloads,
    )
    resolved = resolve_java_invocation(invocation)
    assert resolved.param_types == ("String", "URL[]", "String")

    bridge = RecordingBridge()
    converter = JavaValueConverter(bridge, rti_ambassador=object())
    assert converter.to_backend([TARGET_RADAR_FOM], expected_type_name="URL[]") == (f"url:{TARGET_RADAR_FOM}",)

    native_attr = ("native-attribute", 7)
    py_attr = converter.handle_registry.to_python(AttributeHandle, native_attr)

    converted_set = converter.to_backend({py_attr}, expected_type_name="AttributeHandleSet")
    assert converted_set[0] == "handle_set"
    assert bridge.calls[-1][1] == "AttributeHandleSet"

    converted_map = converter.to_backend({py_attr: b"abc"}, expected_type_name="AttributeHandleValueMap")
    assert converted_map[0] == "handle_map"
    assert bridge.calls[-1][1] == "AttributeHandleValueMap"
