from __future__ import annotations

import pytest

from hla.rti1516e.ambassadors import RecordingFederateAmbassador
from hla.rti1516e.backends.python_rti import InMemoryRTIEngine, PythonRTIConfig
from hla.rti1516e.enums import CallbackModel
from hla.rti1516e.exceptions import NameNotFound
from hla.rti1516e.handles import AttributeHandle, AttributeHandleValueMap, FederateHandleSet, ObjectInstanceHandle
from hla.rti1516e.rti import create_rti_ambassador
from hla.rti1516e.startup import FederationStartupConfig, connect_create_join, drain_callbacks, synchronize_ready_to_run
from hla.rti1516e.backends.java_common import JavaValueConverter
from hla.rti1516e.testing.java_shim_backend import ShimJavaBridge
from hla.rti1516e.testing.java_shim_types import JavaByteArray, JavaLikeObject


def _python_rti(engine: InMemoryRTIEngine, *, config: PythonRTIConfig | None = None):
    return create_rti_ambassador("python", engine=engine, config=config)


def test_whole_federation_synchronization_announces_late_joiner_before_completion():
    engine = InMemoryRTIEngine()
    r1, r2, r3 = (_python_rti(engine) for _ in range(3))
    f1, f2, f3 = RecordingFederateAmbassador(), RecordingFederateAmbassador(), RecordingFederateAmbassador()

    r1.connect(f1, CallbackModel.HLA_EVOKED)
    r2.connect(f2, CallbackModel.HLA_EVOKED)
    r3.connect(f3, CallbackModel.HLA_EVOKED)
    r1.create_federation_execution("late-sync-fed", "TargetRadarFOMmodule.xml")
    r1.join_federation_execution("Leader", "Control", "late-sync-fed")
    r2.join_federation_execution("Wing", "Participant", "late-sync-fed")

    r1.register_federation_synchronization_point("ReadyToRun", b"startup")
    drain_callbacks([r1, r2])
    assert f1.callbacks_named("announceSynchronizationPoint")
    assert f2.callbacks_named("announceSynchronizationPoint")

    # Join before the original synchronization set has completed.  For a whole-
    # federation synchronization point, the RTI must announce it to the late
    # joiner and include that federate in the completion condition.
    r3.join_federation_execution("Late", "Participant", "late-sync-fed")
    drain_callbacks([r1, r2, r3])
    assert f3.callbacks_named("announceSynchronizationPoint")

    r1.synchronization_point_achieved("ReadyToRun")
    r2.synchronization_point_achieved("ReadyToRun")
    drain_callbacks([r1, r2, r3])
    assert not f1.callbacks_named("federationSynchronized")

    r3.synchronization_point_achieved("ReadyToRun")
    drain_callbacks([r1, r2, r3])
    assert f1.callbacks_named("federationSynchronized")
    assert f2.callbacks_named("federationSynchronized")
    assert f3.callbacks_named("federationSynchronized")


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
    f1, f2 = RecordingFederateAmbassador(), RecordingFederateAmbassador()

    r1.connect(f1, CallbackModel.HLA_EVOKED)
    r2.connect(f2, CallbackModel.HLA_EVOKED)
    r1.create_federation_execution("failed-sync-fed", "TargetRadarFOMmodule.xml")
    h1 = r1.join_federation_execution("One", "Participant", "failed-sync-fed")
    h2 = r2.join_federation_execution("Two", "Participant", "failed-sync-fed")

    r1.register_federation_synchronization_point("PreRun", b"startup")
    drain_callbacks([r1, r2])
    r1.synchronization_point_achieved("PreRun", True)
    r2.synchronization_point_achieved("PreRun", False)
    drain_callbacks([r1, r2])

    sync1 = f1.last_callback("federationSynchronized")
    sync2 = f2.last_callback("federationSynchronized")
    assert sync1 is not None and sync2 is not None
    assert sync1.args[0] == "PreRun"
    assert isinstance(sync1.args[1], FederateHandleSet)
    assert h2 in sync1.args[1]
    assert h1 not in sync1.args[1]
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
    from hla.rti1516e.backends.java_common import PythonFederateAmbassadorDispatcher

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
