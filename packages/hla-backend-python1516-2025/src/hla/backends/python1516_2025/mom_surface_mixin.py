"""MOM and service-report helper surface for the Python 2025 RTI ambassador."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Mapping, Protocol

from hla.rti1516_2025.enums import OrderType, ResignAction
from hla.rti1516_2025.handles import (
    AttributeHandle,
    FederateHandle,
    ObjectInstanceHandle,
    ParameterHandle,
    TransportationTypeHandle,
)

from .federation_state_runtime import (
    ensure_mom_federate_object,
    ensure_mom_federation_object,
    ensure_mom_objects,
    is_mom_object_class_name,
    mom_runtime_federate_handle,
    refresh_mom_federate_object,
    refresh_mom_federation_object,
    register_internal_object_instance,
    remove_current_federate_mom_object,
)
from .mom_codec import (
    mom_attribute_handles,
    mom_bool,
    mom_handle_list_payload,
    mom_index,
    mom_int,
    mom_module_data,
    mom_number,
    mom_order_type,
    mom_ownership_state,
    mom_request_params_by_name,
    mom_resign_action,
    mom_single_module_data,
    mom_target_rti,
    mom_text,
)
from .mom_runtime import (
    handle_mom_adjust_interaction,
    handle_mom_federate_request_interaction,
    handle_mom_interaction,
    handle_mom_service_interaction,
    modify_mom_attribute_state,
    mom_counts_for_federate,
    mom_deletable_object_counts,
    mom_request_report_values,
    mom_transport_counts_for_federate,
    send_mom_exception_interaction,
    send_mom_object_class_count_report,
    send_mom_object_instance_information_report,
    send_mom_publication_reports,
    send_mom_report_interaction,
    send_mom_subscription_reports,
    send_mom_transport_count_report,
)
from .object_instance_runtime import set_internal_object_attribute_values

if TYPE_CHECKING:
    class _MomSurfaceContext(Protocol):
        def _transportation_handle_by_name(self, name: str) -> TransportationTypeHandle: ...

        def _coerce_time(self, value: Any) -> Any: ...

        def _coerce_interval(self, value: Any) -> Any: ...

        def _object_class_handles(self) -> dict[str, int]: ...

        def _interaction_class_handles(self) -> dict[str, int]: ...


if TYPE_CHECKING:
    class _MomSurfaceMixinBase(_MomSurfaceContext):
        pass
else:
    class _MomSurfaceMixinBase:
        pass

class MomSurfaceMixin(_MomSurfaceMixinBase):
    """Move MOM helpers out of the primary ambassador class body."""

    @staticmethod
    def _is_mom_object_class_name(object_class_name: str) -> bool:
        return is_mom_object_class_name(object_class_name)

    @staticmethod
    def _mom_runtime_federate_handle() -> FederateHandle:
        return mom_runtime_federate_handle()

    def _ensure_mom_objects(self) -> None:
        ensure_mom_objects(self)

    def _ensure_mom_federation_object(self, federation: Any) -> None:
        ensure_mom_federation_object(self, federation)

    def _ensure_mom_federate_object(
        self,
        federation: Any,
        federate_name: str,
        federate_type: str,
        federate_handle: FederateHandle,
    ) -> None:
        ensure_mom_federate_object(self, federation, federate_name, federate_type, federate_handle)

    def _register_internal_object_instance(
        self,
        object_class_name: str,
        object_instance_name: str,
        *,
        producing_federate: FederateHandle,
        owner_by_attribute: dict[str, FederateHandle | None],
    ) -> ObjectInstanceHandle:
        return register_internal_object_instance(
            self,
            object_class_name,
            object_instance_name,
            producing_federate=producing_federate,
            owner_by_attribute=owner_by_attribute,
        )

    def _refresh_mom_federation_object(self) -> None:
        refresh_mom_federation_object(self)

    def _refresh_mom_federate_object(
        self,
        federate_name: str,
        federate_type: str,
        federate_handle: FederateHandle,
    ) -> None:
        refresh_mom_federate_object(self, federate_name, federate_type, federate_handle)

    def _set_internal_object_attribute_values(
        self,
        object_instance: ObjectInstanceHandle,
        attribute_values: Mapping[str, str | bytes],
    ) -> None:
        set_internal_object_attribute_values(self, object_instance, attribute_values)

    def _remove_current_federate_mom_object(self) -> None:
        remove_current_federate_mom_object(self)

    def _handle_mom_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        return handle_mom_interaction(self, interaction_class_name, values_by_handle)

    def _handle_mom_federate_request_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        return handle_mom_federate_request_interaction(self, interaction_class_name, values_by_handle)

    def _send_mom_publication_reports(self, target_federate: FederateHandle) -> None:
        send_mom_publication_reports(self, target_federate)

    def _send_mom_subscription_reports(self, target_federate: FederateHandle) -> None:
        send_mom_subscription_reports(self, target_federate)

    def _send_mom_object_instance_information_report(
        self,
        target_federate: FederateHandle,
        object_instance: ObjectInstanceHandle,
    ) -> None:
        send_mom_object_instance_information_report(self, target_federate, object_instance)

    def _send_mom_object_class_count_report(
        self,
        report_name: str,
        target_federate: FederateHandle,
        counts_by_class: Mapping[str, int],
        count_parameter_name: str,
    ) -> None:
        send_mom_object_class_count_report(self, report_name, target_federate, counts_by_class, count_parameter_name)

    def _send_mom_transport_count_report(
        self,
        report_name: str,
        target_federate: FederateHandle,
        counts_by_transport: Mapping[str, Mapping[str, int]],
        count_parameter_name: str,
    ) -> None:
        send_mom_transport_count_report(self, report_name, target_federate, counts_by_transport, count_parameter_name)

    def _mom_deletable_object_counts(self, target_federate: FederateHandle) -> dict[str, int]:
        return mom_deletable_object_counts(self, target_federate)

    @staticmethod
    def _mom_counts_for_federate(counts: Mapping[tuple[int, str], int], target_federate: FederateHandle) -> dict[str, int]:
        return mom_counts_for_federate(counts, target_federate)

    @staticmethod
    def _mom_transport_counts_for_federate(
        counts: Mapping[tuple[int, str, str], int],
        target_federate: FederateHandle,
    ) -> dict[str, dict[str, int]]:
        return mom_transport_counts_for_federate(counts, target_federate)

    def _handle_mom_service_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        return handle_mom_service_interaction(self, interaction_class_name, values_by_handle)

    def _handle_mom_adjust_interaction(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> bool:
        return handle_mom_adjust_interaction(self, interaction_class_name, values_by_handle)

    def _modify_mom_attribute_state(
        self,
        object_instance: ObjectInstanceHandle,
        attribute: AttributeHandle,
        ownership_state: str,
    ) -> None:
        modify_mom_attribute_state(self, object_instance, attribute, ownership_state)

    def _mom_request_params_by_name(
        self,
        interaction_class_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> dict[str, bytes]:
        return mom_request_params_by_name(self, interaction_class_name, values_by_handle)

    def _mom_target_rti(self, params: Mapping[str, bytes]) -> Any:
        return mom_target_rti(self, params)

    @staticmethod
    def _mom_bool(value: bytes | None, default: bool) -> bool:
        return mom_bool(value, default)

    @staticmethod
    def _mom_int(value: bytes | None, field_name: str) -> int:
        return mom_int(value, field_name)

    @staticmethod
    def _mom_attribute_handles(value: bytes | None) -> set[AttributeHandle]:
        return mom_attribute_handles(value)

    @staticmethod
    def _mom_text(value: bytes | None, field_name: str) -> str:
        return mom_text(value, field_name)

    def _mom_transportation_handle(self, value: bytes | None, field_name: str) -> TransportationTypeHandle:
        return self._transportation_handle_by_name(self._mom_text(value, field_name))

    def _mom_time(self, value: bytes | None, field_name: str) -> Any:
        return self._coerce_time(self._mom_number(value, field_name))

    def _mom_interval(self, value: bytes | None, field_name: str) -> Any:
        return self._coerce_interval(self._mom_number(value, field_name))

    @staticmethod
    def _mom_number(value: bytes | None, field_name: str) -> int | float:
        return mom_number(value, field_name)

    @staticmethod
    def _mom_handle_list_payload(values: Iterable[int]) -> bytes:
        return mom_handle_list_payload(values)

    @staticmethod
    def _increment_mom_count(counts: dict[Any, int], key: Any) -> None:
        counts[key] = counts.get(key, 0) + 1

    def _mom_object_class_counts_payload(self, counts_by_class: Mapping[str, int]) -> bytes:
        handle_pairs: list[tuple[int, int]] = []
        object_class_handles = self._object_class_handles()
        interaction_class_handles = self._interaction_class_handles()
        for class_name, count in counts_by_class.items():
            handle = object_class_handles.get(class_name, interaction_class_handles.get(class_name))
            if handle is not None:
                handle_pairs.append((handle, count))
        return ",".join(f"{handle}:{count}" for handle, count in sorted(handle_pairs)).encode("ascii")

    @staticmethod
    def _mom_ownership_state(value: bytes | None, field_name: str) -> str:
        return mom_ownership_state(value, field_name)

    @staticmethod
    def _mom_order_type(value: bytes | None, field_name: str) -> OrderType:
        return mom_order_type(value, field_name)

    @classmethod
    def _mom_resign_action(cls, value: bytes | None) -> ResignAction:
        return mom_resign_action(value)

    def _mom_request_report_values(
        self,
        request_name: str,
        report_name: str,
        values_by_handle: Mapping[ParameterHandle, bytes],
    ) -> dict[str, bytes]:
        return mom_request_report_values(self, request_name, report_name, values_by_handle)

    @staticmethod
    def _mom_index(value: bytes | None) -> int:
        return mom_index(value)

    def _mom_module_data(self, modules: tuple[Any, ...], indicator: int) -> str:
        return mom_module_data(modules, indicator)

    @staticmethod
    def _mom_single_module_data(module: Any | None) -> str:
        return mom_single_module_data(module)

    def _send_mom_report_interaction(self, report_name: str, values: Mapping[str, bytes]) -> None:
        send_mom_report_interaction(self, report_name, values)

    def _send_mom_exception_interaction(
        self,
        interaction_class_name: str,
        exception: Exception,
        *,
        parameter_error: bool,
    ) -> None:
        send_mom_exception_interaction(
            self,
            interaction_class_name,
            exception,
            parameter_error=parameter_error,
        )
