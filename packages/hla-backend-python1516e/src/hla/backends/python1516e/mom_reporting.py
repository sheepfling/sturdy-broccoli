"""Service-report and MOM-report emission helpers for the Python RTI backend."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping, Protocol, Sequence

import hla.fom.mom as hla_mom
from hla.rti1516e.enums import OrderType
from hla.spec.refs import method_reference

from .service_reporting import ServiceReportRecord
from .state import CallbackEvent, FederateState, FederationState, SupplementalReceiveInfo

if TYPE_CHECKING:
    from .engine import InMemoryRTIEngine
    from .state import PythonRTIConfig


class _MomReportingContext(Protocol):
    engine: "InMemoryRTIEngine"
    config: "PythonRTIConfig"
    state: FederateState
    service_report_files: Any
    service_report_sink: Any

    def _refresh_mom_attribute_values(self, federation: FederationState) -> None: ...

    def _mom_exposure_model(self, federation: FederationState) -> Any: ...

    def _mom_interaction_rule(self, federation: FederationState, interaction_name: str) -> Any: ...

    def _mom_parameter_handle(self, interaction_name: str, parameter_name: str) -> Any: ...

    def _queue_or_deliver_message(
        self,
        target: FederateState,
        callback: CallbackEvent,
        *,
        sent_order: OrderType,
        timestamp: Any | None,
        sender: Any,
        service_name: str,
        retraction_handle: Any | None = None,
        post_deliver_cleanup: Any | None = None,
    ) -> None: ...

    def _target_federate_from_mom_params(self, federation: FederationState, params: Mapping[str, bytes]) -> FederateState: ...

    def _all_fom_module_data(self, federation: FederationState) -> Sequence[Any]: ...

    def _module_xml_or_uri(self, module: Any) -> bytes: ...

    def _decode_mom_object_instance_handle(self, value: bytes | None) -> Any: ...

    def _is_subscribed_to_service_invocation_report(self, federate: FederateState) -> bool: ...

    def _send_mom_exception(self, federation: FederationState, interaction_name: str, exception_name: str, parameter_error: str = "", *, federate: Any | None = None) -> None: ...


if TYPE_CHECKING:
    class _MomReportingMixinBase(_MomReportingContext):
        pass
else:
    class _MomReportingMixinBase:
        pass


class PythonRTIMomReportingMixin(_MomReportingMixinBase):
    """Service-report file and MOM report emission helpers."""

    def _reporting_context(self) -> tuple[FederationState | None, Any, str | None]:
        federation = self.state.federation or self.state.last_reporting_federation
        handle = self.state.handle or self.state.last_reporting_handle
        name = self.state.name or self.state.last_reporting_name
        return federation, handle, name

    def _service_report_directory(self) -> Path:
        return self.service_report_files.report_directory()

    def _ensure_service_report_file(self, federation: FederationState, federate: FederateState) -> str:
        self.service_report_files.ensure_file(federation, federate)
        if not federate.service_report_initial_record_written:
            self._write_service_report_initial_record(federation, federate)
        return federate.service_report_file or ""

    def _json_safe(self, value: Any) -> Any:
        return self.service_report_files.json_safe(value)

    def _write_service_report_record(self, federation: FederationState, federate: FederateState, record: Mapping[str, Any]) -> None:
        self.service_report_files.write_record(federation, federate, record)

    def _write_service_report_initial_record(self, federation: FederationState, federate: FederateState) -> None:
        self.service_report_files.write_initial_record(federation, federate)

    def _append_service_report_record(
        self,
        service_name: str,
        *,
        success: bool,
        exception_name: str | None = None,
        args: Sequence[Any] | None = None,
        result: Any = None,
        section: str | None = None,
    ) -> None:
        federation, handle, name = self._reporting_context()
        if federation is None or handle is None:
            return
        if not (self.state.service_reporting and self.state.service_reports_to_file):
            return
        self._ensure_service_report_file(federation, self.state)
        self.state.service_report_serial_number += 1
        record = {
            "recordType": "ServiceReportRecord",
            "specSection": f"1516.1-2010 §{section}" if section else "1516.1-2010 §11.5.2",
            "timestampUTC": datetime.now(timezone.utc).isoformat(),
            "serialNumber": self.state.service_report_serial_number,
            "federate": getattr(handle, "value", handle),
            "federateName": name or "",
            "service": service_name,
            "success": bool(success),
            "exception": exception_name or "",
            "arguments": {str(i): self._safe_report_arg(arg) for i, arg in enumerate(args or ())},
            "returned": {"value": self._safe_report_arg(result)} if result is not None else {},
        }
        self.state.service_report_records.append(record)
        self._write_service_report_record(federation, self.state, record)
        self._refresh_mom_attribute_values(federation)

    def _send_mom_report(self, federation: FederationState, report_name: str, values: Mapping[str, Any]) -> None:
        model = self._mom_exposure_model(federation)
        report_name = model.canonical_interaction_name(report_name) or report_name
        report_handle = self.engine.get_or_create_interaction_class(report_name).handle
        rule = self._mom_interaction_rule(federation, report_name)
        normalized_values: dict[str, Any] = {}
        for name, value in values.items():
            normalized_values[mom_table.canonical_parameter_name(rule, str(name))] = value
        expected_names = tuple(rule.parameters) if rule is not None else tuple(normalized_values)
        params: dict[ParameterHandle, bytes] = {}
        for name in expected_names:
            value = normalized_values.get(name, "")
            param = self._mom_parameter_handle(report_name, name)
            if report_name.endswith("HLAreportMOMexception"):
                params[param] = hla_mom.encode_text(value)
            elif isinstance(value, bytes):
                params[param] = value
            elif hasattr(value, "encode") and not isinstance(value, str):
                params[param] = value.encode()
            elif isinstance(value, bool):
                params[param] = hla_mom.encode_bool(value)
            elif isinstance(value, int):
                params[param] = hla_mom.encode_count(value)
            else:
                params[param] = hla_mom.encode_text(value)
        for federate in list(federation.federates.values()):
            if report_handle in federate.subscribed_interactions or report_name.endswith("HLAreportMOMexception"):
                self._queue_or_deliver_message(
                    federate,
                    CallbackEvent(
                        "receiveInteraction",
                        (
                            report_handle,
                            params,
                            b"MOM",
                            OrderType.RECEIVE,
                            self.engine.transportation_reliable,
                            SupplementalReceiveInfo(producing_federate=None),
                        ),
                    ),
                    sent_order=OrderType.RECEIVE,
                    timestamp=None,
                    sender=None,
                    service_name=report_name,
                )

    def _service_report_serial(self) -> int:
        return self.engine._next_sequence()

    def _safe_report_arg(self, value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, bytes):
            return value.hex()
        if isinstance(value, Mapping):
            return {str(k): self._safe_report_arg(v) for k, v in value.items()}
        if isinstance(value, (set, frozenset, list, tuple)):
            return [self._safe_report_arg(v) for v in value]
        return repr(value)

    def _report_service_invocation(
        self,
        service_name: str,
        *,
        success: bool,
        exception_name: str | None = None,
        args: Sequence[Any] | None = None,
        result: Any = None,
    ) -> None:
        try:
            serial = self._service_report_serial()
            ref = method_reference(service_name)
            federation, handle, name = self._reporting_context()
            if self.service_report_sink is not None:
                self.service_report_sink.write(
                    ServiceReportRecord(
                        serial_number=serial,
                        service_name=service_name,
                        federate_handle=repr(handle) if handle is not None else None,
                        federate_name=name,
                        success=success,
                        exception_name=exception_name or None,
                        section=ref.section if ref is not None else None,
                        arguments={str(i): self._safe_report_arg(arg) for i, arg in enumerate(args or ())},
                        returned={"value": self._safe_report_arg(result)} if result is not None else {},
                    )
                )

            self._append_service_report_record(
                service_name,
                success=success,
                exception_name=exception_name or None,
                args=args or (),
                result=result,
                section=ref.section if ref is not None else None,
            )

            if not self.config.enable_mom or federation is None or handle is None or not self.state.service_reporting:
                return
            report_name = f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportServiceInvocation"
            self._send_mom_report(
                federation,
                report_name,
                {
                    "HLAfederate": handle,
                    "HLAservice": service_name,
                    "HLAinitiator": handle,
                    "HLAsuccessIndicator": success,
                    "HLAsuppliedArguments": json.dumps({str(i): self._safe_report_arg(arg) for i, arg in enumerate(args or ())}, sort_keys=True),
                    "HLAreturnedArguments": json.dumps({"value": self._safe_report_arg(result)} if result is not None else {}, sort_keys=True),
                    "HLAexception": exception_name or "",
                    "HLAserialNumber": serial,
                },
            )
            if exception_name and self.state.exception_reporting:
                exception_report = f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportException"
                self._send_mom_report(
                    federation,
                    exception_report,
                    {
                        "HLAfederate": handle,
                        "HLAservice": service_name,
                        "HLAexception": exception_name,
                        "HLAserialNumber": serial,
                    },
                )
        except Exception:
            return

    def _mom_request_report_values(self, federation: FederationState, request_name: str, report_name: str, params: Mapping[str, bytes]) -> dict[str, Any]:
        summary = federation.fom_catalog.as_summary()
        lower_report = report_name.lower()
        target = self._target_federate_from_mom_params(federation, params)
        base: dict[str, Any] = {
            "HLAfederate": target.handle or self.state.handle or "",
            "HLAservice": request_name,
            "HLAsuccessIndicator": True,
        }
        if report_name.endswith("HLAreportFOMmoduleData"):
            base.update(
                {
                    "HLAFOMmoduleIndicator": 0,
                    "HLAFOMmoduleData": hla_mom.encode_opaque(self._all_fom_module_data(federation) or str(summary)),
                }
            )
            return base
        if lower_report.endswith("hlareportmimdata"):
            mim_payload = self._module_xml_or_uri(federation.mim_module)
            base.update({"HLAMIMdata": hla_mom.encode_opaque(mim_payload), "HLAMIMData": hla_mom.encode_opaque(mim_payload)})
            return base
        if report_name.endswith("HLAreportSynchronizationPoints"):
            labels = ",".join(sorted(federation.synchronization_points))
            base.update({"HLAsyncPoints": labels, "HLAsynchronizationPoints": labels})
            return base
        if report_name.endswith("HLAreportSynchronizationPointStatus"):
            status = ";".join(
                f"{label}:{','.join(str(h.value) for h in sorted(point.reported(), key=lambda x: x.value))}"
                for label, point in sorted(federation.synchronization_points.items())
            )
            base.update(
                {
                    "HLAsyncPointName": ",".join(sorted(federation.synchronization_points)),
                    "HLAsyncPointFederates": status,
                    "HLAlabel": ",".join(sorted(federation.synchronization_points)),
                    "HLAfederateSynchronizationStatusList": status,
                }
            )
            return base
        if report_name.endswith("HLAreportObjectClassPublication"):
            base.update(
                {
                    "HLAnumberOfClasses": len(target.published_objects),
                    "HLAobjectClass": str(list(target.published_objects)),
                    "HLAattributeList": str({str(k): list(v) for k, v in target.published_objects.items()}),
                }
            )
            return base
        if report_name.endswith("HLAreportObjectClassSubscription"):
            base.update(
                {
                    "HLAnumberOfClasses": len(target.subscribed_objects),
                    "HLAobjectClass": str(list(target.subscribed_objects)),
                    "HLAactive": True,
                    "HLAmaxUpdateRate": "",
                    "HLAattributeList": str({str(k): list(v) for k, v in target.subscribed_objects.items()}),
                }
            )
            return base
        if report_name.endswith("HLAreportInteractionPublication"):
            base.update({"HLAinteractionClassList": str(list(target.published_interactions)), "HLAnumberOfClasses": len(target.published_interactions)})
            return base
        if report_name.endswith("HLAreportInteractionSubscription"):
            base.update({"HLAinteractionClassList": str(list(target.subscribed_interactions)), "HLAnumberOfClasses": len(target.subscribed_interactions)})
            return base
        if report_name.endswith("HLAreportUpdatesSent"):
            base.update({"HLAtransportation": "", "HLAtransportationType": "", "HLAupdateCounts": target.updates_sent, "HLAupdatesSent": target.updates_sent})
            return base
        if report_name.endswith("HLAreportReflectionsReceived"):
            base.update(
                {
                    "HLAtransportation": "",
                    "HLAtransportationType": "",
                    "HLAreflectCounts": target.reflections_received,
                    "HLAreflectionsReceived": target.reflections_received,
                }
            )
            return base
        if report_name.endswith("HLAreportInteractionsSent"):
            base.update(
                {
                    "HLAtransportation": "",
                    "HLAtransportationType": "",
                    "HLAinteractionCounts": target.interactions_sent,
                    "HLAinteractionsSent": target.interactions_sent,
                }
            )
            return base
        if report_name.endswith("HLAreportInteractionsReceived"):
            base.update(
                {
                    "HLAtransportation": "",
                    "HLAtransportationType": "",
                    "HLAinteractionCounts": target.interactions_received,
                    "HLAinteractionsReceived": target.interactions_received,
                }
            )
            return base
        if report_name.endswith("HLAreportObjectInstancesUpdated"):
            base.update({"HLAobjectInstanceCounts": target.object_instances_updated})
            return base
        if report_name.endswith("HLAreportObjectInstancesReflected"):
            base.update({"HLAobjectInstanceCounts": target.object_instances_reflected})
            return base
        if report_name.endswith("HLAreportObjectInstancesThatCanBeDeleted"):
            deletable = sum(1 for obj in federation.objects.values() if obj.owner == target.handle)
            base.update({"HLAobjectInstanceCounts": deletable})
            return base
        if report_name.endswith("HLAreportObjectInstanceInformation"):
            requested = self._decode_mom_object_instance_handle(params.get("HLAobjectInstance")) if params.get("HLAobjectInstance") is not None else None
            objects = [f"{obj.handle.value}:{obj.name}" for obj in federation.objects.values() if requested is None or obj.handle == requested]
            object_text = ";".join(objects)
            base.update({"HLAobjectInstance": object_text, "HLAobjectClass": "", "HLAobjectInstanceName": object_text, "HLAattributeList": ""})
            return base

        rule = self._mom_interaction_rule(federation, report_name)
        if rule is not None:
            for name in rule.parameters:
                base.setdefault(name, "")
        return base

    def _apply_mom_set_service_reporting(
        self,
        federation: FederationState,
        target: FederateState,
        enabled: bool,
        interaction_name: str,
        parameter_name: str = "HLAreportingState",
    ) -> None:
        if enabled and not target.service_reporting and self._is_subscribed_to_service_invocation_report(target):
            self._send_mom_exception(
                federation,
                interaction_name,
                "FederateServiceInvocationsAreBeingReportedViaMOM",
                parameter_name,
                federate=target.handle,
            )
            return
        target.service_reporting = bool(enabled)


from hla.rti1516e.handles import ParameterHandle  # noqa: E402

from . import mom_catalog as mom_table  # noqa: E402
