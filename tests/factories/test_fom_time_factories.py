from hla2010.spec import FederateAmbassadorSpec
from hla2010_rti_backend_common import Invocation
from hla2010_rti_java_common import JavaBridge, JavaValueConverter, resolve_java_invocation
from hla2010_fom_target_radar.scenarios import target_radar_fom_path
from hla2010.enums import CallbackModel, ResignAction
from hla2010.handles import AttributeHandle, AttributeHandleSet, AttributeHandleValueMap, DimensionHandleSet
from hla2010.raw_api import API_METADATA
from hla2010_rti_runtime_common import create_rti_ambassador
from hla2010.time import HLAfloat64Interval, HLAfloat64Time

TARGET_RADAR_FOM = target_radar_fom_path()


def test_python_rti_resolves_fom_path_and_uses_requested_time_factory():
    rti = create_rti_ambassador("python")
    rti.connect(FederateAmbassadorSpec(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution("fom-time-fed", TARGET_RADAR_FOM, "HLAfloat64Time")
    rti.joinFederationExecution("tester", "test", "fom-time-fed")

    target_class = rti.getObjectClassHandle("HLAobjectRoot.Target")
    assert rti.getObjectClassName(target_class) == "HLAobjectRoot.Target"
    rcs = rti.getAttributeHandle(target_class, "RCS")
    assert rti.getAttributeName(target_class, rcs) == "RCS"

    track_report = rti.getInteractionClassHandle("HLAinteractionRoot.TrackReport")
    time_param = rti.getParameterHandle(track_report, "Time")
    assert rti.getParameterName(track_report, time_param) == "Time"

    factory = rti.getTimeFactory()
    assert factory.get_name() == "HLAfloat64Time"
    assert isinstance(rti.queryLogicalTime(), HLAfloat64Time)

    rti.enableTimeRegulation(factory.make_interval(0.25))
    rti.evokeMultipleCallbacks(0.0, 0.0)
    assert rti.queryLookahead() == HLAfloat64Interval(0.25)

    rti.timeAdvanceRequest(factory.make_time(1.5))
    rti.evokeMultipleCallbacks(0.0, 0.0)
    assert rti.queryLogicalTime() == HLAfloat64Time(1.5)

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution("fom-time-fed")
    rti.disconnect()


def test_python_rti_exposes_handle_set_and_map_factories():
    rti = create_rti_ambassador("python")
    rti.connect(FederateAmbassadorSpec(), CallbackModel.HLA_EVOKED)
    rti.createFederationExecution("factory-fed", "TargetRadarFOMmodule.xml")
    rti.joinFederationExecution("tester", "test", "factory-fed")

    cls = rti.getObjectClassHandle("HLAobjectRoot.Target")
    attr = rti.getAttributeHandle(cls, "RCS")

    attrs = rti.getAttributeHandleSetFactory().create()
    attrs.add(attr)
    assert isinstance(attrs, AttributeHandleSet)
    rti.publishObjectClassAttributes(cls, attrs)

    values = rti.getAttributeHandleValueMapFactory().create(1)
    values[attr] = b"rcs"
    assert isinstance(values, AttributeHandleValueMap)
    obj = rti.registerObjectInstance(cls, "Target-Factory")
    rti.updateAttributeValues(obj, values, b"tag")

    dim = rti.getDimensionHandle("HLAdefaultRoutingSpace")
    dims = rti.getDimensionHandleSetFactory().create()
    dims.add(dim)
    region = rti.createRegion(dims)
    roundtrip_dims = rti.getDimensionHandleSet(region)
    assert isinstance(roundtrip_dims, DimensionHandleSet)
    assert dim in roundtrip_dims

    rti.resignFederationExecution(ResignAction.DELETE_OBJECTS)
    rti.destroyFederationExecution("factory-fed")
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
