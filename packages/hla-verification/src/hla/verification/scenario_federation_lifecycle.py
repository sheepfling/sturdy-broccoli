"""Federation lifecycle verification scenario."""
from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hla.rti1516e import mom
from hla.rti1516e.enums import CallbackModel, ResignAction
from hla.rti1516e.exceptions import (
    AlreadyConnected,
    CouldNotOpenFDD,
    ErrorReadingFDD,
    FederateIsExecutionMember,
    FederatesCurrentlyJoined,
    FederationExecutionAlreadyExists,
    FederationExecutionDoesNotExist,
    InconsistentFDD,
)
from hla.rti1516_2025.exceptions import (
    AlreadyConnected as AlreadyConnected2025,
    CouldNotOpenFOM as CouldNotOpenFOM2025,
    ErrorReadingFOM as ErrorReadingFOM2025,
    FederateIsExecutionMember as FederateIsExecutionMember2025,
    FederatesCurrentlyJoined as FederatesCurrentlyJoined2025,
    FederationExecutionAlreadyExists as FederationExecutionAlreadyExists2025,
    FederationExecutionDoesNotExist as FederationExecutionDoesNotExist2025,
    InconsistentFOM as InconsistentFOM2025,
)
from .scenario_support import drain_callbacks, wait_for_callback, wait_for_callback_count


@dataclass(frozen=True)
class FederationLifecycleScenarioConfig:
    federation_name: str = "LifecycleFederation"
    secondary_federation_name: str | None = None
    fom_modules: tuple[Any, ...] = field(default_factory=tuple)
    logical_time_implementation_name: str | None = None
    use_mim_create: bool = False
    federate_name: str = "LifecycleFederate"
    second_federate_name: str = "LifecycleWing"
    secondary_federate_name: str = "LifecycleShadow"
    federate_type: str = "LifecycleType"
    resign_action: ResignAction = ResignAction.NO_ACTION


def run_federation_lifecycle_scenario(
    rti: Any,
    *,
    config: FederationLifecycleScenarioConfig,
    federate: Any,
) -> dict[str, Any]:
    rti.connect(federate, CallbackModel.HLA_EVOKED)
    create_args = (config.federation_name, list(config.fom_modules), config.logical_time_implementation_name)
    if config.use_mim_create:
        rti.create_federation_execution_with_mim(*create_args)
    else:
        rti.create_federation_execution(*create_args)
    federate_handle = rti.join_federation_execution(
        config.federate_name,
        config.federate_type,
        config.federation_name,
    )
    rti.resign_federation_execution(config.resign_action)
    rti.destroy_federation_execution(config.federation_name)
    rti.disconnect()
    return {
        "federation_name": config.federation_name,
        "federate_handle": federate_handle,
        "resign_action": config.resign_action,
        "use_mim_create": config.use_mim_create,
    }


def _federation_execution_name(info: Any) -> str | None:
    for attribute_name in ("federation_execution_name", "federationExecutionName"):
        try:
            value = getattr(info, attribute_name)
        except AttributeError:
            continue
        if value is not None:
            return str(value)
    if isinstance(info, dict):
        value = info.get("federation_execution_name") or info.get("federationExecutionName")
        return str(value) if value is not None else None
    return None


def run_federation_listing_scenario(
    rti: Any,
    *,
    config: FederationLifecycleScenarioConfig,
    federate: Any,
) -> dict[str, Any]:
    rti.connect(federate, CallbackModel.HLA_EVOKED)
    destroyed = False
    try:
        rti.create_federation_execution(
            config.federation_name,
            list(config.fom_modules),
            config.logical_time_implementation_name,
        )
        rti.list_federation_executions()
        drain_callbacks(rti)
        report = wait_for_callback(rti, federate, "reportFederationExecutions", loops=120)
        assert report is not None
        reported_names = {_federation_execution_name(item) for item in report.args[0]}
        assert config.federation_name in reported_names

        rti.destroy_federation_execution(config.federation_name)
        destroyed = True
        rti.list_federation_executions()
        drain_callbacks(rti)
        post_destroy_report = wait_for_callback(rti, federate, "reportFederationExecutions", loops=120)
        assert post_destroy_report is not None
        post_destroy_reported_names = {_federation_execution_name(item) for item in post_destroy_report.args[0]}
        assert config.federation_name not in post_destroy_reported_names
        return {
            "federation_name": config.federation_name,
            "report": report,
            "reported_names": reported_names,
            "post_destroy_report": post_destroy_report,
            "post_destroy_reported_names": post_destroy_reported_names,
        }
    finally:
        try:
            if not destroyed:
                rti.destroy_federation_execution(config.federation_name)
        finally:
            rti.disconnect()


def _resolve_interaction_handle(rti: Any, *names: str) -> Any:
    last_error: Exception | None = None
    for name in names:
        try:
            return rti.get_interaction_class_handle(name)
        except Exception as exc:  # pragma: no cover - backend-specific naming fallback
            last_error = exc
    assert last_error is not None
    raise last_error


def _resolve_parameter_handle(rti: Any, interaction: Any, *names: str) -> Any:
    last_error: Exception | None = None
    for name in names:
        try:
            return rti.get_parameter_handle(interaction, name)
        except Exception as exc:  # pragma: no cover - backend-specific naming fallback
            last_error = exc
    assert last_error is not None
    raise last_error


def _write_minimal_fom(
    path: Path,
    *,
    name: str,
    time_type: str,
    object_name: str,
    dimension_name: str | None = None,
    simple_datatype_name: str | None = None,
) -> None:
    dimensions = ""
    if dimension_name:
        dimensions = f"""
  <dimensions>
    <dimension><name>{dimension_name}</name></dimension>
  </dimensions>"""

    data_types = ""
    if simple_datatype_name:
        data_types = f"""
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>{simple_datatype_name}</name><representation>HLAinteger32BE</representation></simpleData>
    </simpleDataTypes>
  </dataTypes>"""

    path.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<objectModel>
  <modelIdentification><name>{name}</name><type>FOM</type></modelIdentification>
{dimensions}
  <objects>
    <objectClass>
      <name>HLAobjectRoot</name>
      <objectClass>
        <name>{object_name}</name>
      </objectClass>
    </objectClass>
  </objects>
  <time>
    <timeStamp><dataType>{time_type}</dataType></timeStamp>
  </time>
{data_types}
</objectModel>
""",
        encoding="utf-8",
    )


def run_fom_module_visibility_scenario(
    rti: Any,
    *,
    config: FederationLifecycleScenarioConfig,
    federate: Any,
) -> dict[str, Any]:
    rti.connect(federate, CallbackModel.HLA_EVOKED)
    try:
        rti.create_federation_execution(
            config.federation_name,
            list(config.fom_modules),
            config.logical_time_implementation_name,
        )
        federate_handle = rti.join_federation_execution(
            config.federate_name,
            config.federate_type,
            config.federation_name,
        )

        federation_class = rti.get_object_class_handle(mom.MOM_FEDERATION_OBJECT_CLASS)
        federate_class = rti.get_object_class_handle(mom.MOM_FEDERATE_OBJECT_CLASS)
        federation_name_attr = rti.get_attribute_handle(federation_class, "HLAfederationName")
        federate_name_attr = rti.get_attribute_handle(federate_class, "HLAfederateName")

        fom_request = _resolve_interaction_handle(
            rti,
            f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestFOMmoduleData",
        )
        fom_report = _resolve_interaction_handle(
            rti,
            f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportFOMmoduleData",
        )
        fom_indicator = _resolve_parameter_handle(rti, fom_request, "HLAFOMmoduleIndicator")
        fom_data = _resolve_parameter_handle(rti, fom_report, "HLAFOMmoduleData")

        mim_request = _resolve_interaction_handle(
            rti,
            f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestMIMData",
            f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestMIMdata",
        )
        mim_report = _resolve_interaction_handle(
            rti,
            f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportMIMData",
            f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportMIMdata",
        )
        mim_data = _resolve_parameter_handle(rti, mim_report, "HLAMIMData", "HLAMIMdata")

        rti.subscribe_interaction_class(fom_report)
        rti.send_interaction(fom_request, {fom_indicator: b"0"}, b"fom-request")
        fom_reports = wait_for_callback_count(rti, federate, "receiveInteraction", 1, loops=120)
        matching_fom_reports = [record for record in fom_reports if record.args[0] == fom_report]
        assert matching_fom_reports, "Expected a MOM FOM-module report interaction"
        fom_report_record = matching_fom_reports[-1]
        assert fom_data in fom_report_record.args[1]

        rti.subscribe_interaction_class(mim_report)
        rti.send_interaction(mim_request, {}, b"mim-request")
        mim_reports = wait_for_callback_count(rti, federate, "receiveInteraction", 2, loops=120)
        matching_mim_reports = [record for record in mim_reports if record.args[0] == mim_report]
        assert matching_mim_reports, "Expected a MOM MIM-data report interaction"
        mim_report_record = matching_mim_reports[-1]
        assert mim_data in mim_report_record.args[1]

        return {
            "federation_name": config.federation_name,
            "federate_handle": federate_handle,
            "federation_class": federation_class,
            "federate_class": federate_class,
            "federation_name_attr": federation_name_attr,
            "federate_name_attr": federate_name_attr,
            "fom_report_record": fom_report_record,
            "mim_report_record": mim_report_record,
        }
    finally:
        try:
            rti.resign_federation_execution(config.resign_action)
        except Exception:
            pass
        try:
            rti.destroy_federation_execution(config.federation_name)
        except Exception:
            pass
        rti.disconnect()


def run_multi_module_fom_visibility_scenario(
    rti: Any,
    *,
    config: FederationLifecycleScenarioConfig,
    federate: Any,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="hla2010-fom-visibility-") as temp_dir:
        root = Path(temp_dir)
        first_fom = root / "FirstFloatFOM.xml"
        second_fom = root / "SecondFloatFOM.xml"
        _write_minimal_fom(
            first_fom,
            name="FirstFloatFOM",
            time_type="HLAfloat64BE",
            object_name="FirstObject",
            dimension_name="DimA",
            simple_datatype_name="TypeA",
        )
        _write_minimal_fom(
            second_fom,
            name="SecondFloatFOM",
            time_type="HLAfloat64BE",
            object_name="SecondObject",
            dimension_name="DimB",
            simple_datatype_name="TypeB",
        )

        rti.connect(federate, CallbackModel.HLA_EVOKED)
        try:
            rti.create_federation_execution(
                config.federation_name,
                [first_fom, second_fom],
                config.logical_time_implementation_name,
            )
            federate_handle = rti.join_federation_execution(
                config.federate_name,
                config.federate_type,
                config.federation_name,
            )

            fom_request = _resolve_interaction_handle(
                rti,
                f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLArequest.HLArequestFOMmoduleData",
            )
            fom_report = _resolve_interaction_handle(
                rti,
                f"{mom.MOM_FEDERATION_INTERACTION_ROOT}.HLAreport.HLAreportFOMmoduleData",
            )
            fom_indicator = _resolve_parameter_handle(rti, fom_request, "HLAFOMmoduleIndicator")
            fom_data = _resolve_parameter_handle(rti, fom_report, "HLAFOMmoduleData")

            rti.subscribe_interaction_class(fom_report)
            rti.send_interaction(fom_request, {fom_indicator: b"0"}, b"fom-multi-request")
            reports = wait_for_callback_count(rti, federate, "receiveInteraction", 1, loops=120)
            matching_reports = [record for record in reports if record.args[0] == fom_report]
            assert matching_reports, "Expected a MOM FOM-module report interaction"
            fom_report_record = matching_reports[-1]
            payload = bytes(fom_report_record.args[1][fom_data])
            assert (b"FirstFloatFOM" in payload or b"FirstObject" in payload), payload
            assert (b"SecondFloatFOM" in payload or b"SecondObject" in payload), payload
            assert b"DimA" in payload and b"DimB" in payload, payload
            assert b"TypeA" in payload and b"TypeB" in payload, payload
            return {
                "federation_name": config.federation_name,
                "federate_handle": federate_handle,
                "fom_report_record": fom_report_record,
                "payload": payload,
            }
        finally:
            try:
                rti.resign_federation_execution(config.resign_action)
            except Exception:
                pass
            try:
                rti.destroy_federation_execution(config.federation_name)
            except Exception:
                pass
            rti.disconnect()


def run_fom_integrity_negative_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: FederationLifecycleScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    with tempfile.TemporaryDirectory(prefix="hla2010-fom-negative-") as temp_dir:
        root = Path(temp_dir)
        primary_fom = root / "PrimaryFloatFOM.xml"
        conflicting_fom = root / "ConflictingIntegerFOM.xml"
        bad_fom = root / "BadFOM.xml"
        missing_fom = root / "MissingFOM.xml"

        _write_minimal_fom(
            primary_fom,
            name="PrimaryFloatFOM",
            time_type="HLAfloat64BE",
            object_name="PrimaryObject",
        )
        _write_minimal_fom(
            conflicting_fom,
            name="ConflictingIntegerFOM",
            time_type="HLAinteger64BE",
            object_name="ConflictingObject",
        )
        bad_fom.write_text("<not-an-object-model/>", encoding="utf-8")

        try:
            leader_rti.create_federation_execution(f"{config.federation_name}-missing", [missing_fom])
        except (CouldNotOpenFDD, CouldNotOpenFOM2025) as exc:
            create_missing = exc
        else:  # pragma: no cover - scenario contract
            raise AssertionError("Expected missing create FOM to raise CouldNotOpenFDD/CouldNotOpenFOM")

        try:
            leader_rti.create_federation_execution(f"{config.federation_name}-bad", [bad_fom])
        except (ErrorReadingFDD, ErrorReadingFOM2025) as exc:
            create_bad = exc
        else:  # pragma: no cover - scenario contract
            raise AssertionError("Expected malformed create FOM to raise ErrorReadingFDD/ErrorReadingFOM")

        transactional_federation_name = f"{config.federation_name}-transactional"
        try:
            leader_rti.create_federation_execution(transactional_federation_name, [primary_fom, conflicting_fom])
        except (InconsistentFDD, InconsistentFOM2025) as exc:
            create_inconsistent = exc
        else:  # pragma: no cover - scenario contract
            raise AssertionError("Expected conflicting create FOM set to raise InconsistentFDD/InconsistentFOM")

        leader_rti.create_federation_execution(transactional_federation_name, [primary_fom])
        leader_rti.destroy_federation_execution(transactional_federation_name)

        leader_rti.create_federation_execution(config.federation_name, [primary_fom])
        leader_handle = leader_rti.join_federation_execution(
            config.federate_name,
            config.federate_type,
            config.federation_name,
        )

        try:
            wing_rti.join_federation_execution(
                config.second_federate_name,
                config.federate_type,
                config.federation_name,
                [missing_fom],
            )
        except (CouldNotOpenFDD, CouldNotOpenFOM2025) as exc:
            join_missing = exc
        else:  # pragma: no cover - scenario contract
            raise AssertionError("Expected missing join FOM to raise CouldNotOpenFDD/CouldNotOpenFOM")

        try:
            wing_rti.join_federation_execution(
                config.second_federate_name,
                config.federate_type,
                config.federation_name,
                [bad_fom],
            )
        except (ErrorReadingFDD, ErrorReadingFOM2025) as exc:
            join_bad = exc
        else:  # pragma: no cover - scenario contract
            raise AssertionError("Expected malformed join FOM to raise ErrorReadingFDD/ErrorReadingFOM")

        try:
            wing_rti.join_federation_execution(
                config.second_federate_name,
                config.federate_type,
                config.federation_name,
                [conflicting_fom],
            )
        except (InconsistentFDD, InconsistentFOM2025) as exc:
            join_inconsistent = exc
        else:  # pragma: no cover - scenario contract
            raise AssertionError("Expected conflicting join FOM set to raise InconsistentFDD/InconsistentFOM")

        wing_handle = wing_rti.join_federation_execution(
            config.second_federate_name,
            config.federate_type,
            config.federation_name,
        )

        try:
            wing_rti.resign_federation_execution(config.resign_action)
        except Exception:
            pass
        try:
            leader_rti.resign_federation_execution(config.resign_action)
        except Exception:
            pass
        try:
            leader_rti.destroy_federation_execution(config.federation_name)
        except Exception:
            pass
        leader_rti.disconnect()
        wing_rti.disconnect()
        return {
            "leader_handle": leader_handle,
            "wing_handle": wing_handle,
            "create_missing": create_missing,
            "create_bad": create_bad,
            "create_inconsistent": create_inconsistent,
            "join_missing": join_missing,
            "join_bad": join_bad,
            "join_inconsistent": join_inconsistent,
        }


def run_federation_lifecycle_negative_scenario(
    leader_rti: Any,
    wing_rti: Any,
    *,
    config: FederationLifecycleScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
) -> dict[str, Any]:
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    try:
        leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    except (AlreadyConnected, AlreadyConnected2025) as exc:
        already_connected = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected a repeated connect attempt to raise AlreadyConnected")

    leader_rti.create_federation_execution(
        config.federation_name,
        list(config.fom_modules),
        config.logical_time_implementation_name,
    )
    try:
        leader_rti.create_federation_execution(
            config.federation_name,
            list(config.fom_modules),
            config.logical_time_implementation_name,
        )
    except (FederationExecutionAlreadyExists, FederationExecutionAlreadyExists2025) as exc:
        duplicate_create = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected a duplicate create attempt to raise FederationExecutionAlreadyExists")

    leader_handle = leader_rti.join_federation_execution(
        config.federate_name,
        config.federate_type,
        config.federation_name,
    )
    try:
        leader_rti.disconnect()
    except (FederateIsExecutionMember, FederateIsExecutionMember2025) as exc:
        disconnect_while_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected disconnect while joined to raise FederateIsExecutionMember")

    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    wing_handle = wing_rti.join_federation_execution(
        f"{config.federate_name}-wing",
        config.federate_type,
        config.federation_name,
    )
    try:
        leader_rti.destroy_federation_execution(config.federation_name)
    except (FederatesCurrentlyJoined, FederatesCurrentlyJoined2025) as exc:
        destroy_with_joined = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected destroy with joined members to raise FederatesCurrentlyJoined")

    leader_rti.resign_federation_execution(config.resign_action)
    wing_rti.resign_federation_execution(config.resign_action)
    leader_rti.destroy_federation_execution(config.federation_name)
    try:
        leader_rti.destroy_federation_execution(config.federation_name)
    except (FederationExecutionDoesNotExist, FederationExecutionDoesNotExist2025) as exc:
        destroy_missing = exc
    else:  # pragma: no cover - scenario contract
        raise AssertionError("Expected destroy of missing federation to raise FederationExecutionDoesNotExist")
    finally:
        wing_rti.disconnect()
        leader_rti.disconnect()

    return {
        "federation_name": config.federation_name,
        "leader_handle": leader_handle,
        "wing_handle": wing_handle,
        "already_connected": already_connected,
        "duplicate_create": duplicate_create,
        "disconnect_while_joined": disconnect_while_joined,
        "destroy_with_joined": destroy_with_joined,
        "destroy_missing": destroy_missing,
    }


def run_multi_participation_scenario(
    leader_rti: Any,
    wing_rti: Any,
    shadow_rti: Any,
    *,
    config: FederationLifecycleScenarioConfig,
    leader_federate: Any,
    wing_federate: Any,
    shadow_federate: Any,
) -> dict[str, Any]:
    secondary_federation_name = config.secondary_federation_name or f"{config.federation_name}-Secondary"
    leader_rti.connect(leader_federate, CallbackModel.HLA_EVOKED)
    wing_rti.connect(wing_federate, CallbackModel.HLA_EVOKED)
    shadow_rti.connect(shadow_federate, CallbackModel.HLA_EVOKED)

    try:
        leader_rti.create_federation_execution(
            config.federation_name,
            list(config.fom_modules),
            config.logical_time_implementation_name,
        )
        shadow_rti.create_federation_execution(
            secondary_federation_name,
            list(config.fom_modules),
            config.logical_time_implementation_name,
        )

        leader_handle = leader_rti.join_federation_execution(
            config.federate_name,
            config.federate_type,
            config.federation_name,
        )
        wing_handle = wing_rti.join_federation_execution(
            config.second_federate_name,
            config.federate_type,
            config.federation_name,
        )
        shadow_handle = shadow_rti.join_federation_execution(
            config.secondary_federate_name,
            config.federate_type,
            secondary_federation_name,
        )

        return {
            "primary_federation_name": config.federation_name,
            "secondary_federation_name": secondary_federation_name,
            "leader_handle": leader_handle,
            "wing_handle": wing_handle,
            "shadow_handle": shadow_handle,
        }
    finally:
        try:
            leader_rti.resign_federation_execution(config.resign_action)
        except Exception:
            pass
        try:
            wing_rti.resign_federation_execution(config.resign_action)
        except Exception:
            pass
        try:
            shadow_rti.resign_federation_execution(config.resign_action)
        except Exception:
            pass
        try:
            leader_rti.destroy_federation_execution(config.federation_name)
        except Exception:
            pass
        try:
            shadow_rti.destroy_federation_execution(secondary_federation_name)
        except Exception:
            pass
        try:
            shadow_rti.disconnect()
        except Exception:
            pass
        try:
            wing_rti.disconnect()
        except Exception:
            pass
        try:
            leader_rti.disconnect()
        except Exception:
            pass


__all__ = [
    "FederationLifecycleScenarioConfig",
    "run_fom_module_visibility_scenario",
    "run_fom_integrity_negative_scenario",
    "run_multi_module_fom_visibility_scenario",
    "run_federation_lifecycle_scenario",
    "run_federation_lifecycle_negative_scenario",
    "run_federation_listing_scenario",
    "run_multi_participation_scenario",
]
