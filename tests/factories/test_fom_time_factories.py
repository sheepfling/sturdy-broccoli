import pytest

from hla.rti1516e import NullFederateAmbassador
from hla.backends.common import (
    BackendConversionError,
    Invocation,
    ResolvedJavaInvocation,
    install_deterministic_java_invocation_router,
    reset_java_invocation_resolver,
    resolve_java_invocation_deterministic,
    set_java_invocation_resolver,
)
from hla.bridges.java.common import HLAJavaValueAdapter, JavaBridge, JavaRTIBackend, resolve_java_invocation
from hla.foms.target_radar._internal import target_radar_fom_path
from hla.rti1516e.enums import CallbackModel, ResignAction
from hla.rti1516e.handles import (
    AttributeHandle,
    AttributeHandleSet,
    AttributeHandleValueMap,
    DimensionHandleSet,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    RegionHandle,
    RegionHandleSet,
)
from hla.rti1516_2025.encoding import HLAfixedArray as HLA2025FixedArray, HLAoctet as HLA2025Octet, HLAvariantRecord as HLA2025VariantRecord
from hla.rti1516_2025.handles import ObjectInstanceHandle as ObjectInstanceHandle2025
from hla.rti1516e.encoding import HLAASCIIstring, HLAfixedRecord, HLAunicodeString
from hla.rti1516e.api_metadata import API_METADATA
from hla.runtime.factory import create_rti_ambassador
from hla.rti1516e.datatypes import AttributeRegionAssociation
from hla.rti1516e.time import HLAfloat64Interval, HLAfloat64Time
from hla.rti1516_2025 import AdditionalSettingsResultCode, ConfigurationResult, RtiConfiguration
from hla.backends.common import make_rti_ambassador

TARGET_RADAR_FOM = target_radar_fom_path()


def _same_arity_java_overload_groups(interface: str) -> dict[tuple[str, int], list[dict[str, object]]]:
    groups: dict[tuple[str, int], list[dict[str, object]]] = {}
    for method_name, overloads in API_METADATA.get(interface, {}).items():
        java_overloads = [overload for overload in overloads if overload.get("language") == "java"]
        by_arity: dict[int, list[dict[str, object]]] = {}
        for overload in java_overloads:
            params = [part.strip() for part in str(overload.get("params", "")).split(",") if part.strip()]
            by_arity.setdefault(len(params), []).append(overload)
        for arity, arity_overloads in by_arity.items():
            if len(arity_overloads) > 1:
                groups[(method_name, arity)] = arity_overloads
    return groups


def _sample_value_for_java_type(java_type: str, param_name: str):
    if java_type == "String":
        if param_name == "logicalTimeImplementationName":
            return "HLAfloat64Time"
        return f"{param_name}-value"
    if java_type == "URL":
        return TARGET_RADAR_FOM
    if java_type == "URL[]":
        return [TARGET_RADAR_FOM]
    if java_type == "byte[]":
        return b"tag"
    if java_type == "LogicalTime":
        return HLAfloat64Time(1.0)
    if java_type == "boolean":
        return True
    if java_type == "ObjectInstanceHandle":
        return ObjectInstanceHandle(101)
    if java_type == "ObjectClassHandle":
        return ObjectClassHandle(202)
    if java_type == "AttributeHandleSet":
        return {AttributeHandle(303)}
    if java_type == "AttributeHandleValueMap":
        return {AttributeHandle(404): b"value"}
    if java_type == "ParameterHandleValueMap":
        return {ParameterHandle(505): b"value"}
    if java_type == "RegionHandleSet":
        return {RegionHandle(606)}
    if java_type == "AttributeSetRegionSetPairList":
        return [AttributeRegionAssociation({AttributeHandle(707)}, {RegionHandle(808)})]
    raise AssertionError(f"Unhandled synthetic Java sample type {java_type!r} for {param_name!r}")


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
        self.fake_factory = _FakeJavaFactory()

    def call(self, obj, method_name, *args):
        return getattr(obj, method_name)(*args)

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

    def encoder_factory(self, java_factory):
        self.calls.append(("encoder_factory", java_factory))
        return java_factory.getEncoderFactory()


class _RecordingJavaRTI:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def connect(self, *args):  # noqa: ANN002
        self.calls.append(("connect", args))
        return None

    def createFederationExecution(self, *args):  # noqa: N802, ANN002
        self.calls.append(("createFederationExecution", args))
        return None

    def joinFederationExecution(self, *args):  # noqa: N802, ANN002
        self.calls.append(("joinFederationExecution", args))
        return "joined"

    def requestAttributeValueUpdate(self, *args):  # noqa: N802, ANN002
        self.calls.append(("requestAttributeValueUpdate", args))
        return None


class _FakeEncodedElement:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def toByteArray(self) -> bytes:  # noqa: N802
        return self.payload


class _FakeEncoderFactory:
    def createHLAoctet(self, value: int):  # noqa: N802
        return _FakeEncodedElement(bytes([value]))

    def createHLAASCIIstring(self, value: str):  # noqa: N802
        return _FakeEncodedElement(b"java-ascii:" + value.encode("ascii"))

    def createHLAunicodeString(self, value: str):  # noqa: N802
        return _FakeEncodedElement(b"java-unicode:" + value.encode("utf-8"))

    def createHLAfixedRecord(self):  # noqa: N802
        return _FakeJavaFixedRecord()

    def createHLAfixedArray(self, *elements):  # noqa: N802
        return _FakeJavaFixedArray(elements)

    def createHLAvariantRecord(self, discriminant):  # noqa: N802
        return _FakeJavaVariantRecord(discriminant)


class _FakeJavaFixedRecord:
    def __init__(self) -> None:
        self.elements: list[_FakeEncodedElement] = []

    def add(self, element) -> None:
        self.elements.append(element)

    def toByteArray(self) -> bytes:  # noqa: N802
        return b"".join(element.toByteArray() for element in self.elements)


class _FakeJavaFixedArray:
    def __init__(self, elements) -> None:
        self.elements = list(elements)

    def toByteArray(self) -> bytes:  # noqa: N802
        return b"".join(element.toByteArray() for element in self.elements)


class _FakeJavaVariantRecord:
    def __init__(self, discriminant) -> None:
        self.discriminant = discriminant
        self.value = None

    def setVariant(self, discriminant, value) -> None:  # noqa: N802
        self.discriminant = discriminant
        self.value = value

    def setDiscriminant(self, discriminant) -> None:  # noqa: N802
        self.discriminant = discriminant

    def toByteArray(self) -> bytes:  # noqa: N802
        assert self.value is not None
        return self.discriminant.toByteArray() + self.value.toByteArray()


class _FakeJavaFactory:
    def getEncoderFactory(self):  # noqa: N802
        return _FakeEncoderFactory()


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
    converter = HLAJavaValueAdapter(bridge, rti_ambassador=object())
    assert converter.to_backend([TARGET_RADAR_FOM], expected_type_name="URL[]") == (f"url:{TARGET_RADAR_FOM}",)

    native_attr = ("native-attribute", 7)
    py_attr = converter.handle_registry.to_python(AttributeHandle, native_attr)

    converted_set = converter.to_backend({py_attr}, expected_type_name="AttributeHandleSet")
    assert converted_set[0] == "handle_set"
    assert bridge.calls[-1][1] == "AttributeHandleSet"

    converted_map = converter.to_backend({py_attr: b"abc"}, expected_type_name="AttributeHandleValueMap")
    assert converted_map[0] == "handle_map"
    assert bridge.calls[-1][1] == "AttributeHandleValueMap"


def test_api_designator_metadata_preserves_standard_designator_types_across_java_and_cpp_bindings():
    connect_overloads = tuple(API_METADATA["RTIambassador"]["connect"])
    assert any(
        overload.get("language") == "java"
        and "String localSettingsDesignator" in str(overload.get("params", ""))
        for overload in connect_overloads
    )
    assert any(
        overload.get("language") == "cpp"
        and "std::wstring const & localSettingsDesignator" in str(overload.get("params", ""))
        for overload in connect_overloads
    )

    create_overloads = tuple(API_METADATA["RTIambassador"]["createFederationExecution"])
    assert any(
        overload.get("language") == "java"
        and "String logicalTimeImplementationName" in str(overload.get("params", ""))
        for overload in create_overloads
    )
    assert any(
        overload.get("language") == "cpp"
        and "std::wstring const & logicalTimeImplementationName" in str(overload.get("params", ""))
        for overload in create_overloads
    )

    turn_updates_overloads = tuple(
        API_METADATA["FederateAmbassador"]["turnUpdatesOnForObjectInstance"]
    )
    assert any(
        overload.get("language") == "java"
        and "String updateRateDesignator" in str(overload.get("params", ""))
        for overload in turn_updates_overloads
    )
    assert any(
        overload.get("language") == "cpp"
        and "std::wstring const & updateRateDesignator" in str(overload.get("params", ""))
        for overload in turn_updates_overloads
    )


def test_java_overload_resolution_rejects_equal_score_ambiguity():
    invocation = Invocation(
        method_name="ambiguousCall",
        args=("alpha",),
        overloads=(
            {"language": "java", "params": "String federationExecutionName"},
            {"language": "java", "params": "String federateType"},
        ),
    )

    with pytest.raises(BackendConversionError, match="Ambiguous Java overload resolution"):
        resolve_java_invocation(invocation)


def test_java_overload_resolution_prefers_better_scored_candidate():
    invocation = Invocation(
        method_name="createFederationExecution",
        args=("fed", TARGET_RADAR_FOM, "HLAfloat64Time"),
        overloads=(
            {"language": "java", "params": "String federationExecutionName, URL fomModule, String logicalTimeImplementationName"},
            {"language": "java", "params": "String federationExecutionName, String fomModule, String logicalTimeImplementationName"},
        ),
    )

    resolved = resolve_java_invocation(invocation)

    assert resolved.param_types == ("String", "URL", "String")


def test_java_overload_resolution_matches_handle_shape_across_edition_classes():
    invocation = Invocation(
        method_name="requestAttributeValueUpdate",
        args=(ObjectInstanceHandle2025(4), {AttributeHandle(51)}, b"radar-rcs-query"),
        overloads=(
            {"language": "java", "params": "ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag"},
            {"language": "java", "params": "ObjectClassHandle theClass, AttributeHandleSet theAttributes, byte[] userSuppliedTag"},
        ),
    )

    resolved = resolve_java_invocation(invocation)

    assert resolved.param_types == ("ObjectInstanceHandle", "AttributeHandleSet", "byte[]")


def test_same_arity_java_rti_overloads_have_unique_exact_shape_resolution():
    groups = _same_arity_java_overload_groups("RTIambassador")
    assert set(groups) == {
        ("createFederationExecution", 2),
        ("createFederationExecution", 3),
        ("joinFederationExecution", 3),
        ("requestAttributeValueUpdate", 3),
    }

    for (method_name, _arity), overloads in groups.items():
        for overload in overloads:
            param_names = [part.rsplit(" ", 1)[-1].replace("...", "") for part in str(overload["params"]).split(",") if part.strip()]
            param_types = [
                " ".join(part.strip().split()[:-1]).replace("...", "").strip()
                for part in str(overload["params"]).split(",")
                if part.strip()
            ]
            args = tuple(_sample_value_for_java_type(java_type, param_name) for java_type, param_name in zip(param_types, param_names))
            resolved = resolve_java_invocation(
                Invocation(
                    method_name=method_name,
                    args=args,
                    overloads=tuple(overloads),
                )
            )
            assert resolved.overload == overload


def test_java_backend_connect_inserts_local_settings_designator_on_two_arg_path():
    java_rti = _RecordingJavaRTI()
    rti = make_rti_ambassador(
        JavaRTIBackend(
            java_rti_ambassador=java_rti,
            bridge=RecordingBridge(),
            connect_local_settings_designator="crc=127.0.0.1:8989",
        )
    )

    rti.connect(NullFederateAmbassador(), CallbackModel.HLA_EVOKED)

    method_name, args = java_rti.calls[-1]
    assert method_name == "connect"
    assert len(args) == 3
    assert args[-1] == "crc=127.0.0.1:8989"


def test_java_backend_create_federation_execution_prefers_single_url_overload():
    java_rti = _RecordingJavaRTI()
    rti = make_rti_ambassador(JavaRTIBackend(java_rti_ambassador=java_rti, bridge=RecordingBridge()))

    rti.createFederationExecution("fed", TARGET_RADAR_FOM)

    method_name, args = java_rti.calls[-1]
    assert method_name == "createFederationExecution"
    assert args == ("fed", f"url:{TARGET_RADAR_FOM}")


def test_java_backend_join_federation_execution_prefers_additional_modules_overload_for_list_third_arg():
    java_rti = _RecordingJavaRTI()
    rti = make_rti_ambassador(JavaRTIBackend(java_rti_ambassador=java_rti, bridge=RecordingBridge()))

    rti.joinFederationExecution("observer", "demo-fed", [TARGET_RADAR_FOM])

    method_name, args = java_rti.calls[-1]
    assert method_name == "joinFederationExecution"
    assert args == ("observer", "demo-fed", (f"url:{TARGET_RADAR_FOM}",))


def test_java_backend_request_attribute_value_update_prefers_exact_handle_type():
    java_rti = _RecordingJavaRTI()
    backend = JavaRTIBackend(java_rti_ambassador=java_rti, bridge=RecordingBridge())
    object_handle = backend.converter.handle_registry.to_python(ObjectInstanceHandle, ("native-object", 17))
    attribute_handle = backend.converter.handle_registry.to_python(AttributeHandle, ("native-attribute", 3))
    rti = make_rti_ambassador(backend)

    rti.requestAttributeValueUpdate(object_handle, {attribute_handle}, b"tag")

    method_name, args = java_rti.calls[-1]
    assert method_name == "requestAttributeValueUpdate"
    assert args[0] == ("native-object", 17)
    assert args[1][0] == "handle_set"
    assert args[2] == b"tag"


def test_java_backend_can_run_through_deterministic_invocation_router():
    java_rti = _RecordingJavaRTI()
    backend = JavaRTIBackend(java_rti_ambassador=java_rti, bridge=RecordingBridge())
    object_handle = backend.converter.handle_registry.to_python(ObjectInstanceHandle, ("native-object", 17))
    attribute_handle = backend.converter.handle_registry.to_python(AttributeHandle, ("native-attribute", 3))
    rti = make_rti_ambassador(backend)

    previous = install_deterministic_java_invocation_router()
    try:
        rti.requestAttributeValueUpdate(object_handle, {attribute_handle}, b"tag")
    finally:
        set_java_invocation_resolver(previous)
        reset_java_invocation_resolver()

    method_name, args = java_rti.calls[-1]
    assert method_name == "requestAttributeValueUpdate"
    assert args[0] == ("native-object", 17)
    assert args[1][0] == "handle_set"
    assert args[2] == b"tag"


def test_deterministic_java_router_marks_explicit_routes_as_strict_for_container_shapes():
    invocation = Invocation(
        method_name="createFederationExecution",
        args=("fed", [TARGET_RADAR_FOM], TARGET_RADAR_FOM),
        overloads=tuple(API_METADATA["RTIambassador"]["createFederationExecution"]),
    )

    resolved = resolve_java_invocation_deterministic(invocation)

    assert resolved.param_types == ("String", "URL[]", "String")
    assert resolved.strict_container_shapes is True


def test_java_backend_prefers_backend_local_resolver_over_global_swap():
    java_rti = _RecordingJavaRTI()
    backend = JavaRTIBackend(
        java_rti_ambassador=java_rti,
        bridge=RecordingBridge(),
        invocation_resolver=resolve_java_invocation_deterministic,
    )
    object_handle = backend.converter.handle_registry.to_python(ObjectInstanceHandle, ("native-object", 23))
    attribute_handle = backend.converter.handle_registry.to_python(AttributeHandle, ("native-attribute", 5))
    rti = make_rti_ambassador(backend)

    def _alternate_resolver(invocation: Invocation) -> ResolvedJavaInvocation:
        return ResolvedJavaInvocation(args=("wrong-route",), param_types=("String",), overload=None)

    previous = set_java_invocation_resolver(_alternate_resolver)
    try:
        rti.requestAttributeValueUpdate(object_handle, {attribute_handle}, b"tag")
    finally:
        set_java_invocation_resolver(previous)
        reset_java_invocation_resolver()

    method_name, args = java_rti.calls[-1]
    assert method_name == "requestAttributeValueUpdate"
    assert args[0] == ("native-object", 23)
    assert args[1][0] == "handle_set"
    assert args[2] == b"tag"


def test_java_backend_invoke_uses_swapped_java_resolver_result():
    java_rti = _RecordingJavaRTI()
    backend = JavaRTIBackend(java_rti_ambassador=java_rti, bridge=RecordingBridge())
    rti = make_rti_ambassador(backend)

    def _alternate_resolver(invocation: Invocation) -> ResolvedJavaInvocation:
        assert invocation.method_name == "createFederationExecution"
        return ResolvedJavaInvocation(
            args=("forced-fed", [TARGET_RADAR_FOM], "HLAfloat64Time"),
            param_types=("String", "URL[]", "String"),
            overload={"language": "java", "params": "String federationExecutionName, URL[] fomModules, String logicalTimeImplementationName"},
        )

    previous = set_java_invocation_resolver(_alternate_resolver)
    try:
        rti.createFederationExecution("ignored-fed", "not-a-real-fom")
    finally:
        set_java_invocation_resolver(previous)
        reset_java_invocation_resolver()

    method_name, args = java_rti.calls[-1]
    assert method_name == "createFederationExecution"
    assert args == ("forced-fed", (f"url:{TARGET_RADAR_FOM}",), "HLAfloat64Time")


def test_java_backend_fails_closed_on_strict_generic_container_fallback():
    java_rti = _RecordingJavaRTI()
    backend = JavaRTIBackend(java_rti_ambassador=java_rti, bridge=RecordingBridge())
    rti = make_rti_ambassador(backend)

    def _strict_generic_container_resolver(invocation: Invocation) -> ResolvedJavaInvocation:
        assert invocation.method_name == "createFederationExecution"
        return ResolvedJavaInvocation(
            args=("forced-fed", [TARGET_RADAR_FOM]),
            param_types=("String", "java.util.List"),
            overload={"language": "java", "params": "String federationExecutionName, java.util.List fomModules"},
            strict_container_shapes=True,
        )

    previous = set_java_invocation_resolver(_strict_generic_container_resolver)
    try:
        with pytest.raises(BackendConversionError, match="forbids generic container fallback"):
            rti.createFederationExecution("ignored-fed", [TARGET_RADAR_FOM])
    finally:
        set_java_invocation_resolver(previous)
        reset_java_invocation_resolver()


def test_java_converter_uses_encoder_oracle_for_data_element_payload_slots():
    bridge = RecordingBridge()
    converter = HLAJavaValueAdapter(
        bridge,
        rti_ambassador=object(),
        java_encoder_oracle=JavaRTIBackend(
            java_rti_ambassador=object(),
            java_factory=bridge.fake_factory,
            bridge=bridge,
            info=None,
        ).java_encoder_oracle,
    )

    native_attr = ("native-attribute", 7)
    py_attr = converter.handle_registry.to_python(AttributeHandle, native_attr)

    converted_map = converter.to_backend(
        {py_attr: HLAunicodeString("lambda-\u03bb")},
        expected_type_name="AttributeHandleValueMap",
    )
    assert converted_map == (
        "handle_map",
        "AttributeHandleValueMap",
        ((native_attr, b"java-unicode:lambda-\xce\xbb"),),
    )

    converted_tag = converter.to_backend(HLAASCIIstring("tagged"), expected_type_name="byte[]")
    assert converted_tag == b"java-ascii:tagged"

    record = HLAfixedRecord([HLAASCIIstring("left"), HLAunicodeString("right-\u03bb")])
    converted_record = converter.to_backend(record, expected_type_name="byte[]")
    assert converted_record == b"java-ascii:leftjava-unicode:right-\xce\xbb"

    fixed_array = HLA2025FixedArray([HLA2025Octet(1), HLA2025Octet(2), HLA2025Octet(3)])
    converted_array = converter.to_backend(fixed_array, expected_type_name="byte[]")
    assert converted_array == b"\x01\x02\x03"

    discriminant = HLA2025Octet(7)
    variant = HLA2025VariantRecord(discriminant)
    variant.setVariant(HLA2025Octet(7), HLAASCIIstring("armed"))
    converted_variant = converter.to_backend(variant, expected_type_name="byte[]")
    assert converted_variant == b"\x07java-ascii:armed"


def test_java_converter_prepares_attribute_region_association_pair_lists():
    bridge = RecordingBridge()
    converter = HLAJavaValueAdapter(bridge, rti_ambassador=object())

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
    converter = HLAJavaValueAdapter(bridge)

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
    converter = HLAJavaValueAdapter(RecordingBridge(api_profile="2025"))

    converted = converter.from_backend(_ConfigurationResultLike(), expected_type_name="ConfigurationResult")

    assert converted == ConfigurationResult(
        True,
        False,
        AdditionalSettingsResultCode.SETTINGS_APPLIED,
        "ok",
    )
