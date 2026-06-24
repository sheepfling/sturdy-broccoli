from __future__ import annotations

import pytest

from hla.backends.common import RecordingFederateAmbassador
from hla.bridges.java.common import JavaValueConverter
from hla.backends.inmemory import InMemoryRTIEngine, PythonRTIConfig
from hla.rti1516e.enums import CallbackModel, RestoreStatus, SaveStatus
from hla.rti1516e.exceptions import NameNotFound
from hla.rti1516e.handles import (
    AttributeHandle,
    AttributeHandleValueMap,
    FederateHandleSet,
    MessageRetractionHandle,
    ObjectInstanceHandle,
    RegionHandleSet,
)
from hla.runtime.factory import create_rti_ambassador
from hla.rti1516e.datatypes import (
    FederateHandleSaveStatusPair,
    FederateRestoreStatus,
    FederationExecutionInformation,
    MessageRetractionReturn,
    RangeBounds,
    SupplementalReceiveInfo,
    SupplementalReflectInfo,
    SupplementalRemoveInfo,
    TimeQueryReturn,
)
from hla.verification import (
    SynchronizationScenarioConfig,
    run_failed_federate_synchronization_scenario,
    run_late_join_synchronization_scenario,
)
from hla.verification.startup import (
    FederationStartupConfig,
    connect_create_join,
    drain_callbacks,
    synchronize_ready_to_run,
)
from hla.bridges.java.common.java_shim_backend import ShimJavaBridge
from hla.bridges.java.common.java_shim_types import JavaByteArray, JavaEnumConstant, JavaLikeObject, JavaRangeBounds


def _python_rti(engine: InMemoryRTIEngine, *, config: PythonRTIConfig | None = None):
    return create_rti_ambassador("python", engine=engine, config=config)


def test_whole_federation_synchronization_announces_late_joiner_before_completion():
    engine = InMemoryRTIEngine()
    r1, r2, r3 = (_python_rti(engine) for _ in range(3))
    summary = run_late_join_synchronization_scenario(
        r1,
        r2,
        r3,
        config=SynchronizationScenarioConfig(
            federation_name="late-sync-fed",
            fom_modules=("TargetRadarFOMmodule.xml",),
            leader_name="Leader",
            wing_name="Wing",
            late_name="Late",
            federate_type="Participant",
            label="ReadyToRun",
            tag=b"startup",
        ),
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
        late_federate=RecordingFederateAmbassador(),
    )

    assert summary["late_announce"].args[:2] == ("ReadyToRun", b"startup")
    assert summary["leader_sync"].args[0] == "ReadyToRun"
    assert summary["wing_sync"].args[0] == "ReadyToRun"
    assert summary["late_sync"].args[0] == "ReadyToRun"


def test_strict_fom_loading_discovers_bundled_fom_and_rejects_unknown_names():
    engine = InMemoryRTIEngine()
    config = PythonRTIConfig(strict_fom_loading=True, strict_fom_lookup=True)
    rti = _python_rti(engine, config=config)
    fed = RecordingFederateAmbassador()

    rti.connect(fed, CallbackModel.HLA_EVOKED)
    rti.create_federation_execution("strict-fom-fed", ["TargetRadarFOMmodule.xml"])
    rti.join_federation_execution("FomUser", "Radar", "strict-fom-fed")

    summary = rti.backend.current_fom_summary()
    assert "HLAobjectRoot.Target" in summary["object_classes"]
    assert "HLAinteractionRoot.TrackReport" in summary["interaction_classes"]
    assert summary["logical_time_implementation"] == "HLAfloat64Time"
    assert summary["module_uris"][0].startswith("file:")

    target = rti.get_object_class_handle("HLAobjectRoot.Target")
    rcs = rti.get_attribute_handle(target, "RCS")
    assert isinstance(rcs, AttributeHandle)
    with pytest.raises(NameNotFound):
        rti.get_object_class_handle("HLAobjectRoot.NotInFOM")


def test_startup_helper_connects_joins_and_completes_ready_to_run_sync_point():
    engine = InMemoryRTIEngine()
    r1, r2 = _python_rti(engine), _python_rti(engine)
    f1, f2 = RecordingFederateAmbassador(), RecordingFederateAmbassador()
    config1 = FederationStartupConfig(
        federation_name="startup-fed",
        federate_name="Target",
        federate_type="TargetFederate",
        fom_modules=("TargetRadarFOMmodule.xml",),
    )
    config2 = FederationStartupConfig(
        federation_name="startup-fed",
        federate_name="Radar",
        federate_type="RadarFederate",
        fom_modules=("TargetRadarFOMmodule.xml",),
    )

    result1 = connect_create_join(r1, f1, config1)
    result2 = connect_create_join(r2, f2, config2)
    assert result1.created_federation is True
    assert result2.created_federation is False

    synchronize_ready_to_run([r1, r2], label="ReadyToRun")
    assert f1.callbacks_named("federationSynchronized")
    assert f2.callbacks_named("federationSynchronized")


def test_java_converter_recognizes_vendor_handle_impl_names_and_typed_maps_sets():
    converter = JavaValueConverter(ShimJavaBridge("jpype"))

    native_obj = JavaLikeObject("VendorObjectInstanceHandleImpl", 101)
    obj = converter.from_backend(native_obj)
    same_obj_from_fresh_proxy = converter.from_backend(JavaLikeObject("VendorObjectInstanceHandleImpl", 101))
    assert isinstance(obj, ObjectInstanceHandle)
    assert same_obj_from_fresh_proxy == obj
    assert converter.to_backend(obj) is native_obj

    attribute_map = converter.from_backend(
        {JavaLikeObject("VendorAttributeHandleImpl", 5): JavaByteArray(b"abc")},
        expected_type_name="AttributeHandleValueMap",
    )
    assert isinstance(attribute_map, AttributeHandleValueMap)
    assert next(iter(attribute_map.values())) == b"abc"
    assert isinstance(next(iter(attribute_map.keys())), AttributeHandle)

    failed_set = converter.from_backend(
        {JavaLikeObject("VendorFederateHandleImpl", 1), JavaLikeObject("VendorFederateHandleImpl", 2)},
        expected_type_name="FederateHandleSet",
    )
    assert isinstance(failed_set, FederateHandleSet)
    assert len(failed_set) == 2


def test_synchronization_reports_failed_federates_and_removes_completed_point():
    engine = InMemoryRTIEngine()
    r1, r2 = _python_rti(engine), _python_rti(engine)
    summary = run_failed_federate_synchronization_scenario(
        r1,
        r2,
        config=SynchronizationScenarioConfig(
            federation_name="failed-sync-fed",
            fom_modules=("TargetRadarFOMmodule.xml",),
            leader_name="One",
            wing_name="Two",
            federate_type="Participant",
            label="PreRun",
            tag=b"startup",
        ),
        leader_federate=RecordingFederateAmbassador(),
        wing_federate=RecordingFederateAmbassador(),
        leader_success=True,
        wing_success=False,
    )

    sync1 = summary["leader_sync"]
    assert isinstance(sync1.args[1], FederateHandleSet)
    assert summary["wing_handle"] in sync1.args[1]
    assert summary["leader_handle"] not in sync1.args[1]
    assert "PreRun" not in engine.federations["failed-sync-fed"].synchronization_points


def test_join_fom_time_conflict_is_transactional(tmp_path):
    first = tmp_path / "FloatTimeFOM.xml"
    second = tmp_path / "IntegerTimeFOM.xml"
    first.write_text(
        """<?xml version='1.0'?>
<objectModel>
  <modelIdentification><name>FloatTimeFOM</name><type>FOM</type></modelIdentification>
  <objects><objectClass><name>HLAobjectRoot</name></objectClass></objects>
  <time><timeStamp><dataType>HLAfloat64BE</dataType></timeStamp></time>
</objectModel>
""",
        encoding="utf-8",
    )
    second.write_text(
        """<?xml version='1.0'?>
<objectModel>
  <modelIdentification><name>IntegerTimeFOM</name><type>FOM</type></modelIdentification>
  <objects><objectClass><name>HLAobjectRoot</name></objectClass></objects>
  <time><timeStamp><dataType>HLAinteger64BE</dataType></timeStamp></time>
</objectModel>
""",
        encoding="utf-8",
    )

    from hla.rti1516e.exceptions import InconsistentFDD

    engine = InMemoryRTIEngine()
    r1, r2 = _python_rti(engine), _python_rti(engine)
    f1, f2 = RecordingFederateAmbassador(), RecordingFederateAmbassador()
    r1.connect(f1, CallbackModel.HLA_EVOKED)
    r2.connect(f2, CallbackModel.HLA_EVOKED)
    r1.create_federation_execution("time-conflict-fed", [first])
    r1.join_federation_execution("Creator", "Participant", "time-conflict-fed")
    before = r1.backend.current_fom_summary()

    with pytest.raises(InconsistentFDD):
        r2.join_federation_execution("Joiner", "Participant", "time-conflict-fed", [second])

    after = r1.backend.current_fom_summary()
    assert before == after
    assert after["logical_time_implementation"] == "HLAfloat64Time"


def test_java_callback_dispatcher_uses_callback_metadata_for_typed_failed_set():
    from hla.bridges.java.common import PythonFederateAmbassadorDispatcher

    fed = RecordingFederateAmbassador()
    converter = JavaValueConverter(ShimJavaBridge("py4j"))
    dispatcher = PythonFederateAmbassadorDispatcher(fed, converter)

    dispatcher.federationSynchronized(
        "ReadyToRun",
        {JavaLikeObject("VendorFederateHandleImpl", 17)},
    )

    record = fed.last_callback("federationSynchronized")
    assert record is not None
    assert record.args[0] == "ReadyToRun"
    assert isinstance(record.args[1], FederateHandleSet)
    assert len(record.args[1]) == 1


def test_java_converter_round_trips_range_bounds():
    converter = JavaValueConverter(ShimJavaBridge("jpype"))

    native = converter.to_backend(RangeBounds(10, 20))
    assert isinstance(native, JavaRangeBounds)
    assert native.getLowerBound() == 10
    assert native.getUpperBound() == 20

    assert converter.from_backend(native, expected_type_name="RangeBounds") == RangeBounds(10, 20)


def test_java_converter_normalizes_public_datatype_return_shapes():
    converter = JavaValueConverter(ShimJavaBridge("jpype"))

    time_query = JavaLikeObject("TimeQueryReturn")
    time_query.timeIsValid = True
    time_query.time = JavaLikeObject("HLAinteger64Time", 12)
    converted_time_query = converter.from_backend(time_query, expected_type_name="TimeQueryReturn")
    assert converted_time_query == TimeQueryReturn(True, converted_time_query.time)
    assert converted_time_query.time_is_valid is True

    retraction = JavaLikeObject("MessageRetractionReturn")
    retraction.retractionHandleIsValid = True
    retraction.messageRetractionHandle = JavaLikeObject("MessageRetractionHandle", 44)
    converted_retraction = converter.from_backend(retraction, expected_type_name="MessageRetractionReturn")
    assert isinstance(converted_retraction, MessageRetractionReturn)
    assert converted_retraction.retraction_handle_is_valid is True
    assert isinstance(converted_retraction.handle, MessageRetractionHandle)

    federation_info = JavaLikeObject("FederationExecutionInformation")
    federation_info.federationExecutionName = "fed-a"
    federation_info.logicalTimeImplementationName = "HLAinteger64Time"
    converted_federation_info = converter.from_backend(
        federation_info,
        expected_type_name="FederationExecutionInformation",
    )
    assert converted_federation_info == FederationExecutionInformation("fed-a", "HLAinteger64Time")
    assert converted_federation_info.federation_execution_name == "fed-a"

    save_pair = JavaLikeObject("FederateHandleSaveStatusPair")
    save_pair.federateHandle = JavaLikeObject("FederateHandle", 7)
    save_pair.saveStatus = JavaEnumConstant("SaveStatus", "FEDERATE_SAVING")
    converted_save_pair = converter.from_backend(save_pair, expected_type_name="FederateHandleSaveStatusPair")
    assert converted_save_pair == FederateHandleSaveStatusPair(converted_save_pair.handle, SaveStatus.FEDERATE_SAVING)
    assert converted_save_pair.federate_handle == converted_save_pair.handle

    restore_status = JavaLikeObject("FederateRestoreStatus")
    restore_status.preRestoreHandle = JavaLikeObject("FederateHandle", 8)
    restore_status.postRestoreHandle = JavaLikeObject("FederateHandle", 9)
    restore_status.restoreStatus = JavaEnumConstant("RestoreStatus", "FEDERATE_RESTORING")
    converted_restore_status = converter.from_backend(
        restore_status,
        expected_type_name="FederateRestoreStatus",
    )
    assert isinstance(converted_restore_status, FederateRestoreStatus)
    assert converted_restore_status.restore_status is RestoreStatus.FEDERATE_RESTORING

    sent_regions = {JavaLikeObject("RegionHandle", 3), JavaLikeObject("RegionHandle", 4)}
    reflect = JavaLikeObject("SupplementalReflectInfo")
    reflect.hasProducingFederate = lambda: True
    reflect.hasSentRegions = lambda: True
    reflect.getProducingFederate = lambda: JavaLikeObject("FederateHandle", 12)
    reflect.getSentRegions = lambda: sent_regions
    converted_reflect = converter.from_backend(reflect, expected_type_name="SupplementalReflectInfo")
    assert isinstance(converted_reflect, SupplementalReflectInfo)
    assert converted_reflect.hasProducingFederate() is True
    assert isinstance(converted_reflect.getSentRegions(), RegionHandleSet)

    receive = JavaLikeObject("SupplementalReceiveInfo")
    receive.hasProducingFederate = lambda: True
    receive.hasSentRegions = lambda: True
    receive.getProducingFederate = lambda: JavaLikeObject("FederateHandle", 13)
    receive.getSentRegions = lambda: sent_regions
    converted_receive = converter.from_backend(receive, expected_type_name="SupplementalReceiveInfo")
    assert isinstance(converted_receive, SupplementalReceiveInfo)
    assert converted_receive.hasSentRegions() is True

    remove = JavaLikeObject("SupplementalRemoveInfo")
    remove.hasProducingFederate = lambda: True
    remove.getProducingFederate = lambda: JavaLikeObject("FederateHandle", 14)
    converted_remove = converter.from_backend(remove, expected_type_name="SupplementalRemoveInfo")
    assert isinstance(converted_remove, SupplementalRemoveInfo)
    assert converted_remove.hasProducingFederate() is True
