"""MOM parameter validation and decoding helpers for the Python RTI backend."""

from __future__ import annotations

from typing import Any, Mapping

from hla.rti1516e import mom as hla_mom
from hla.rti1516e.enums import OrderType, ResignAction
from hla.rti1516e.exceptions import (
    FederateHandleNotKnown,
    InteractionParameterNotDefined,
    InvalidParameterHandle,
    RTIexception,
)
from hla.rti1516e.handles import (
    AttributeHandle,
    DimensionHandle,
    FederateHandle,
    InteractionClassHandle,
    ObjectClassHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    TransportationTypeHandle,
)

from . import mom_catalog as mom_table


class PythonRTIMomParameterDecodingMixin:
    """MOM exception reporting plus parameter decoding and validation helpers."""

    def _send_mom_exception(
        self,
        federation,
        interaction_name: str,
        exception_name: str,
        parameter_error: str = "",
        *,
        federate: FederateHandle | None = None,
    ) -> None:
        model = self._mom_exposure_model(federation)
        report_name = f"{hla_mom.MOM_FEDERATE_INTERACTION_ROOT}.HLAreport.HLAreportMOMexception"
        report_name = model.canonical_interaction_name(report_name) or report_name
        self._send_mom_report(
            federation,
            report_name,
            {
                "HLAfederate": federate or self.state.handle or "",
                "HLAservice": interaction_name,
                "HLAexception": exception_name,
                "HLAparameterError": parameter_error,
            },
        )

    def _mom_parameter_failure(
        self,
        federation,
        interaction_name: str,
        exception: RTIexception,
        parameter_error: str,
        *,
        mom_exception_name: str | None = None,
    ) -> dict[str, bytes]:
        self._send_mom_exception(
            federation,
            interaction_name,
            mom_exception_name or exception.__class__.__name__,
            parameter_error,
        )
        if self.config.strict_mom_parameter_decoding:
            raise exception
        return {}

    def _mom_bool_payload_is_valid(self, value: bytes) -> bool:
        data = bytes(value)
        if len(data) == 1:
            return data in {b"\x00", b"\x01"}
        text = ""
        try:
            text = hla_mom.decode_text(data).strip().lower()
        except Exception:
            try:
                text = data.decode("utf-8").strip().lower()
            except Exception:
                return False
        return text in {
            "0",
            "1",
            "true",
            "false",
            "t",
            "f",
            "yes",
            "no",
            "y",
            "n",
            "enabled",
            "disabled",
            "enable",
            "disable",
        }

    def _mom_parameter_payload_issue(
        self,
        federation,
        rule: mom_table.MOMInteractionRule,
        name: str,
        value: bytes,
    ) -> str | None:
        data_type = (rule.parameter_datatypes.get(name, "") or "").lower()
        lower_name = name.lower()
        if (
            data_type in {"hlaswitch", "hlaboolean"}
            or lower_name
            in {"hlareportingstate", "hlasuccessindicator", "hlaactive", "hlaautoprovide"}
            or lower_name.startswith("hlaconvey")
        ):
            return None if self._mom_bool_payload_is_valid(value) else "InvalidMOMParameterEncoding"
        if (
            name in mom_table.MOM_FLOAT_PARAMETERS
            or data_type in {"hlafloat64be", "hlafloat64le", "hlafloat32be", "hlafloat32le"}
        ):
            try:
                float(self._decode_mom_text(value, ""))
                return None
            except Exception:
                return "InvalidMOMParameterEncoding"
        if name in mom_table.MOM_HANDLE_PARAMETERS or data_type == "hlahandle":
            handle_types = {
                "HLAfederate": FederateHandle,
                "HLAobjectClass": ObjectClassHandle,
                "HLAobjectClassName": ObjectClassHandle,
                "HLAinteractionClass": InteractionClassHandle,
                "HLAinteractionClassName": InteractionClassHandle,
                "HLAobjectInstance": ObjectInstanceHandle,
                "HLAtransportation": TransportationTypeHandle,
                "HLAtransportationType": TransportationTypeHandle,
            }
            handle_type = handle_types.get(name, FederateHandle)
            try:
                handle = self._decode_mom_handle(value, handle_type, name)
            except Exception:
                return "InvalidMOMParameterEncoding"
            if name == "HLAfederate" and handle not in federation.federates:
                return "FederateHandleNotKnown"
            return None
        if name in mom_table.MOM_HANDLE_SET_PARAMETERS or data_type == "hlahandlelist":
            handle_set_types = {
                "HLAattributeList": AttributeHandle,
                "HLAattribute": AttributeHandle,
                "HLAfederateList": FederateHandle,
                "HLAdimensionHandleSet": DimensionHandle,
            }
            handle_type = handle_set_types.get(name, FederateHandle)
            try:
                values = self._decode_mom_handle_set(value, handle_type, name)
            except Exception:
                return "InvalidMOMParameterEncoding"
            if handle_type is FederateHandle and any(item not in federation.federates for item in values):
                return "FederateHandleNotKnown"
            return None
        if lower_name in {"hlatimestamp", "hlatimeadvancingtime", "hlatimegrantedtime"}:
            return None if self._decode_mom_time(value) is not None else "InvalidMOMParameterEncoding"
        if lower_name == "hlalookahead":
            return None if self._decode_mom_interval(value) is not None else "InvalidMOMParameterEncoding"
        if (
            data_type in {"hlacount", "hlainteger32be", "hlainteger32le"}
            or lower_name.endswith("count")
            or lower_name in {"hlanumberofclasses", "hlaserialnumber"}
        ):
            try:
                hla_mom.decode_count(value)
                return None
            except Exception:
                try:
                    int(self._decode_mom_text(value, ""))
                    return None
                except Exception:
                    return "InvalidMOMParameterEncoding"
        return None

    def _validate_mom_parameter_payloads(
        self,
        federation,
        rule: mom_table.MOMInteractionRule | None,
        params: Mapping[str, bytes],
    ):
        if rule is None:
            return ()
        issues: list[mom_table.MOMValidationIssue] = []
        for name, value in params.items():
            if name not in rule.allowed_parameters:
                continue
            kind = self._mom_parameter_payload_issue(federation, rule, name, bytes(value))
            if kind:
                issues.append(mom_table.MOMValidationIssue(kind, rule.name, name))
        return tuple(issues)

    def _mom_params_by_name(
        self,
        interaction_name: str,
        parameters: Mapping[ParameterHandle, bytes],
    ) -> dict[str, bytes]:
        federation = self._require_joined()
        model = self._mom_exposure_model(federation)
        canonical_interaction = model.canonical_interaction_name(interaction_name) or interaction_name
        definition = self.engine.get_or_create_interaction_class(canonical_interaction)
        rule = self._mom_interaction_rule(federation, canonical_interaction)
        params: dict[str, bytes] = {}
        for handle, value in dict(parameters).items():
            try:
                raw_name = definition.parameter_names[handle]
            except KeyError:
                return self._mom_parameter_failure(
                    federation,
                    canonical_interaction,
                    InvalidParameterHandle(
                        f"Parameter handle {handle!r} is not defined for {canonical_interaction}"
                    ),
                    repr(handle),
                    mom_exception_name="InvalidMOMParameterHandle",
                )
            name = mom_table.canonical_parameter_name(rule, raw_name)
            if rule is not None and name not in rule.allowed_parameters:
                if self.config.strict_mom_parameter_decoding:
                    return self._mom_parameter_failure(
                        federation,
                        canonical_interaction,
                        InteractionParameterNotDefined(
                            f"Parameter {raw_name!r} is not allowed for {canonical_interaction}"
                        ),
                        raw_name,
                        mom_exception_name="UnexpectedMOMParameter",
                    )
                name = raw_name
            if name in params:
                return self._mom_parameter_failure(
                    federation,
                    canonical_interaction,
                    InteractionParameterNotDefined(
                        f"Duplicate MOM parameter {name!r} for {canonical_interaction}"
                    ),
                    name,
                    mom_exception_name="DuplicateMOMParameter",
                )
            params[name] = bytes(value)

        if rule is not None and self.config.strict_mom_parameter_decoding:
            for issue in model.validate_incoming_parameters(canonical_interaction, params, strict=True):
                return self._mom_parameter_failure(
                    federation,
                    canonical_interaction,
                    InteractionParameterNotDefined(issue.detail or issue.kind),
                    issue.parameter_name,
                    mom_exception_name=issue.kind,
                )
            for issue in self._validate_mom_parameter_payloads(federation, rule, params):
                exc = (
                    FederateHandleNotKnown(issue.parameter_name)
                    if issue.kind == "FederateHandleNotKnown"
                    else InteractionParameterNotDefined(issue.kind)
                )
                return self._mom_parameter_failure(
                    federation,
                    canonical_interaction,
                    exc,
                    issue.parameter_name,
                    mom_exception_name=issue.kind,
                )
        return params

    def _decode_mom_text(self, value: bytes | None, default: str = "") -> str:
        if value is None:
            return default
        try:
            return hla_mom.decode_text(value)
        except Exception:
            try:
                return bytes(value).decode("utf-8")
            except Exception:
                return default

    def _decode_mom_bool(self, value: bytes | None, default: bool = True) -> bool:
        if value is None:
            return default
        try:
            return hla_mom.decode_bool(value)
        except Exception:
            text = self._decode_mom_text(value, "").strip().lower()
            if text in {"1", "true", "t", "yes", "y", "enabled", "enable"}:
                return True
            if text in {"0", "false", "f", "no", "n", "disabled", "disable"}:
                return False
            return default

    def _decode_mom_float(self, value: bytes | None, default: float | None = None) -> float | None:
        if value is None:
            return default
        try:
            return float(self._decode_mom_text(value, ""))
        except Exception:
            try:
                return float(int.from_bytes(value[-4:], "big", signed=True))
            except Exception:
                return default

    def _decode_mom_time(self, value: bytes | None) -> Any:
        if value is None:
            return None
        federation = self._require_joined()
        data = bytes(value)
        try:
            return federation.time_factory.decode_time(data)
        except Exception:
            text = self._decode_mom_text(data, "")
            try:
                return federation.time_factory.make_time(float(text))
            except Exception:
                return None

    def _decode_mom_interval(self, value: bytes | None) -> Any:
        if value is None:
            return None
        federation = self._require_joined()
        data = bytes(value)
        try:
            return federation.time_factory.decode_interval(data)
        except Exception:
            text = self._decode_mom_text(data, "")
            try:
                return federation.time_factory.make_interval(float(text))
            except Exception:
                return None

    def _decode_mom_federate_handle(self, value: bytes | None) -> FederateHandle | None:
        if value is None:
            return None
        data = bytes(value)
        try:
            return FederateHandle.decode(data)
        except Exception:
            text = self._decode_mom_text(data, "").strip()
            if text:
                try:
                    return FederateHandle(int(text))
                except Exception:
                    return None
        return None

    def _decode_mom_handle(
        self,
        value: bytes | None,
        handle_type: type[Any],
        parameter_name: str,
    ) -> Any:
        if value is None:
            raise InteractionParameterNotDefined(
                f"Missing required MOM parameter {parameter_name}"
            )
        data = bytes(value)
        try:
            return handle_type.decode(data)
        except Exception:
            text = self._decode_mom_text(data, "").strip()
            if text:
                try:
                    return handle_type(int(text))
                except Exception as exc:
                    raise InteractionParameterNotDefined(
                        f"Could not decode {parameter_name} as {handle_type.__name__}: {text!r}"
                    ) from exc
        raise InteractionParameterNotDefined(
            f"Could not decode {parameter_name} as {handle_type.__name__}"
        )

    def _decode_mom_object_class_handle(self, value: bytes | None) -> ObjectClassHandle:
        return self._decode_mom_handle(value, ObjectClassHandle, "HLAobjectClass")

    def _decode_mom_interaction_class_handle(self, value: bytes | None) -> InteractionClassHandle:
        return self._decode_mom_handle(value, InteractionClassHandle, "HLAinteractionClass")

    def _decode_mom_object_instance_handle(self, value: bytes | None) -> ObjectInstanceHandle:
        return self._decode_mom_handle(value, ObjectInstanceHandle, "HLAobjectInstance")

    def _decode_mom_transportation_handle(
        self,
        value: bytes | None,
    ) -> TransportationTypeHandle:
        if value is None:
            return self.engine.transportation_reliable
        try:
            return self._decode_mom_handle(
                value, TransportationTypeHandle, "HLAtransportation"
            )
        except InteractionParameterNotDefined:
            text = self._decode_mom_text(value, "").strip().lower()
            if text in {"", "hlareliable", "reliable"}:
                return self.engine.transportation_reliable
            raise

    def _decode_mom_handle_set(
        self,
        value: bytes | None,
        handle_type: type[Any],
        parameter_name: str,
    ) -> set[Any]:
        if value is None:
            raise InteractionParameterNotDefined(
                f"Missing required MOM parameter {parameter_name}"
            )
        data = bytes(value)
        if data and len(data) % 8 == 0 and any(b < 32 or b > 126 for b in data):
            try:
                return {
                    handle_type.decode(data[offset : offset + 8])
                    for offset in range(0, len(data), 8)
                }
            except Exception:
                pass
        text = self._decode_mom_text(data, "")
        if not text:
            try:
                text = data.decode("utf-8")
            except Exception:
                text = ""
        tokens = [
            token.strip()
            for token in text.replace("[", "").replace("]", "").replace(";", ",").split(",")
            if token.strip()
        ]
        result: set[Any] = set()
        for token in tokens:
            if token.startswith(f"{handle_type.__name__}(") and token.endswith(")"):
                token = token[token.find("(") + 1 : -1]
            if "value=" in token:
                token = token.split("value=", 1)[1].strip(" )")
            try:
                result.add(handle_type(int(token)))
            except Exception as exc:
                raise InteractionParameterNotDefined(
                    f"Could not decode {parameter_name} element {token!r} as {handle_type.__name__}"
                ) from exc
        return result

    def _decode_mom_attribute_set(self, value: bytes | None) -> set[AttributeHandle]:
        return self._decode_mom_handle_set(value, AttributeHandle, "HLAattributeList")

    def _decode_mom_order_type(
        self,
        value: bytes | None,
        default: OrderType = OrderType.RECEIVE,
    ) -> OrderType:
        if value is None:
            return default
        text = self._decode_mom_text(value, "").strip().upper()
        if "TIMESTAMP" in text or text.endswith("TSO"):
            return OrderType.TIMESTAMP
        if "RECEIVE" in text or text.endswith("RO"):
            return OrderType.RECEIVE
        return default

    def _decode_mom_resign_action(
        self,
        value: bytes | None,
        default: ResignAction = ResignAction.NO_ACTION,
    ) -> ResignAction:
        if value is None:
            return default
        text = self._decode_mom_text(value, "").strip().upper()
        for action in ResignAction:
            if text in {action.name.upper(), str(action.value).upper(), str(action).upper()}:
                return action
        return default

    def _target_federate_from_mom_params(self, federation, params: Mapping[str, bytes]):
        target_handle = self._decode_mom_federate_handle(params.get("HLAfederate"))
        if target_handle is None:
            return self.state
        try:
            return federation.federates[target_handle]
        except KeyError as exc:
            raise FederateHandleNotKnown(repr(target_handle)) from exc
