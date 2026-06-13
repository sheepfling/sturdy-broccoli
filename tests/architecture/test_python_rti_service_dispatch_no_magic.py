from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/backend.py"
MOM_ACTION_ROUTING_PATH = ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/mom_action_routing.py"
OBJECT_DELIVERY_ATTRIBUTES_PATH = (
    ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/object_delivery_attributes.py"
)
MOM_PATH = ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/mom.py"
INTERNAL_SERVICE_REUSE_FILES = [
    ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/federation_creation.py",
    ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/declaration.py",
    ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/ddm_services.py",
    ROOT / "packages/hla2010-rti-python/src/hla2010_rti_python/support_control.py",
]


def test_python_rti_backend_does_not_lookup_service_handlers_by_name_convention() -> None:
    text = BACKEND_PATH.read_text(encoding="utf-8")
    assert 'getattr(self, f"_svc_{invocation.method_name}"' not in text
    assert '"_svc_{invocation.method_name}"' not in text


def test_python_rti_mom_service_dispatch_does_not_call_svc_methods_directly() -> None:
    text = MOM_ACTION_ROUTING_PATH.read_text(encoding="utf-8")
    assert "self._svc_" not in text
    assert "self.call_service(" in text


def test_python_rti_mom_service_dispatch_uses_explicit_handler_table() -> None:
    text = MOM_ACTION_ROUTING_PATH.read_text(encoding="utf-8")
    assert "def _mom_service_action_handlers" in text
    assert 'handler = self._mom_service_action_handlers().get(leaf)' in text
    assert 'if leaf == "HLAresignFederationExecution"' not in text


def test_python_rti_mom_adjust_dispatch_uses_explicit_handler_table() -> None:
    text = MOM_ACTION_ROUTING_PATH.read_text(encoding="utf-8")
    assert "def _mom_adjust_action_handlers" in text
    assert 'handler = self._mom_adjust_action_handlers().get(leaf)' in text
    assert 'if leaf == "HLAsetTiming"' not in text


def test_python_rti_internal_helpers_use_explicit_backend_methods() -> None:
    object_delivery_text = OBJECT_DELIVERY_ATTRIBUTES_PATH.read_text(encoding="utf-8")
    mom_text = MOM_PATH.read_text(encoding="utf-8")
    assert "owner_backend._svc_provideAttributeValueUpdate" not in object_delivery_text
    assert "owner_backend.provide_attribute_value_update" in object_delivery_text
    assert "self._svc_getHLAversion()" not in mom_text
    assert "self.get_hla_version()" in mom_text


def test_python_rti_backend_explicit_helpers_do_not_delegate_back_to_svc_names() -> None:
    text = BACKEND_PATH.read_text(encoding="utf-8")
    assert "return self._svc_getHLAversion()" not in text
    assert "self._svc_provideAttributeValueUpdate(" not in text
    assert "self._svc_turnUpdatesOnForObjectInstance(" not in text
    assert "self._svc_turnUpdatesOffForObjectInstance(" not in text
    assert "super().get_hla_version()" in text
    assert "super().provide_attribute_value_update(" in text
    assert "super().turn_updates_on_for_object_instance(" in text
    assert "super().turn_updates_off_for_object_instance(" in text


def test_python_rti_internal_mixins_do_not_reenter_services_via_call_service() -> None:
    violations: list[str] = []
    for path in INTERNAL_SERVICE_REUSE_FILES:
        text = path.read_text(encoding="utf-8")
        if "call_service(" in text:
            violations.append(path.relative_to(ROOT).as_posix())
    assert not violations, "\n".join(violations)
