from hla.rti1516e import NullFederateAmbassador
from hla.backends.common import Invocation
from hla.bridges.java.common import JavaBridge, JavaValueConverter, resolve_java_invocation
from hla.foms.target_radar._internal import target_radar_fom_path
from hla.rti1516e.enums import CallbackModel, ResignAction
from hla.rti1516e.handles import (
    AttributeHandle,
    AttributeHandleSet,
    AttributeHandleValueMap,
    DimensionHandleSet,
    RegionHandle,
    RegionHandleSet,
)
from hla.rti1516e.raw_api import API_METADATA
from hla.runtime.factory import create_rti_ambassador
from hla.rti1516e.datatypes import AttributeRegionAssociation
from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time
from hla.rti1516_2025 import AdditionalSettingsResultCode, ConfigurationResult, RtiConfiguration

TARGET_RADAR_FOM = target_radar_fom_path()


def test_python_rti_resolves_fom_path_and_uses_requested_time_factory():
    rti = create_rti_ambassador("python1516e")
    rti.connect(NullFederateAmbassador(), CallbackModel.HLA_EVOKED)
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
    assert factory.getName() == "HLAfloat64Time"
    assert isinstance(rti.queryLogicalTime(), HLAfloat64Time)

    rti.enableTimeRegulation(factory.makeInterval(0.25))
    rti.evokeMultipleCallbacks(0.0, 0.0)
    assert rti.queryLookahead() == HLAfloat64Interval(0.25)

    rti.timeAdvanceRequest(factory.makeTime(1.5))
    rti.evokeMultipleCallbacks(0.0, 0.0)
    assert rti.queryLogicalTime() == HLAfloat64Time(1.5)

    rti.resignFederationExecution(ResignAction.NO_ACTION)
    rti.destroyFederationExecution("fom-time-fed")
    rti.disconnect()


def test_python_rti_exposes_handle_set_and_map_factories():
    rti = create_rti_ambassador("python1516e")
    rti.connect(NullFederateAmbassador(), CallbackModel.HLA_EVOKED)
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

    def __init__(self, api_profile="2010"):
        super().__init__(api_profile=api_profile)
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

    def new_attribute_set_region_set_pair_list(self, values, *, rti_ambassador=None):
        self.calls.append(("pair_list", tuple(values), rti_ambassador is not None))
        return ("pair_list", tuple(values))

    def rti_configuration(self, value):
        self.calls.append(("rti_configuration", value))
        return ("rti_configuration", value.configuration_name, value.rti_address, value.additional_settings)


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


def test_java_converter_prepares_attribute_region_association_pair_lists():
    bridge = RecordingBridge()
    converter = JavaValueConverter(bridge, rti_ambassador=object())

    native_attr = ("native-attribute", 7)
    native_region = ("native-region", 9)
    py_attr = converter.handle_registry.to_python(AttributeHandle, native_attr)
    py_region = converter.handle_registry.to_python(RegionHandle, native_region)

    pairs = [
        AttributeRegionAssociation(
            AttributeHandleSet({py_attr}),
            RegionHandleSet({py_region}),
        )
    ]

    converted = converter.to_backend(pairs, expected_type_name="AttributeSetRegionSetPairList")
    assert converted[0] == "pair_list"


class _ConfigurationResultLike:
    configurationUsed = True
    addressUsed = False
    additionalSettingsResultCode = AdditionalSettingsResultCode.SETTINGS_APPLIED
    message = "ok"


def test_java_converter_converts_2025_rti_configuration_without_expected_type_metadata():
    bridge = RecordingBridge(api_profile="2025")
    converter = JavaValueConverter(bridge)

    configuration = (
        RtiConfiguration.createConfiguration()
        .withConfigurationName("native-hla4")
        .withRtiAddress("localhost")
        .withAdditionalSettings("mode=test")
    )
    converted = converter.to_backend(configuration)

    assert converted == ("rti_configuration", "native-hla4", "localhost", "mode=test")
    assert ("rti_configuration", configuration) in bridge.calls


def test_java_converter_converts_2025_configuration_result():
    converter = JavaValueConverter(RecordingBridge(api_profile="2025"))

    converted = converter.from_backend(_ConfigurationResultLike(), expected_type_name="ConfigurationResult")

    assert converted == ConfigurationResult(
        True,
        False,
        AdditionalSettingsResultCode.SETTINGS_APPLIED,
        "ok",
    )
