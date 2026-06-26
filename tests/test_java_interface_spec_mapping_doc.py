from __future__ import annotations

from pathlib import Path

import scripts.generate_java_interface_spec_mapping as mapping_script


ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "reference" / "java_interface_spec_mapping.md"


def test_java_interface_spec_mapping_doc_is_in_sync_with_generator() -> None:
    mapping_script._bootstrap_source_checkout()
    expected = mapping_script.render()
    actual = DOC_PATH.read_text(encoding="utf-8")
    assert actual == expected


def test_java_interface_spec_mapping_doc_exposes_route_policy_legend_and_key_rows() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Java Interface Spec Mapping" in text
    assert "## Route Policy Legend" in text
    assert "`explicit-deterministic`" in text
    assert "`weighted-or-shape-selected`" in text
    assert "| `createFederationExecution` | `Federation Management` | `4.5` | `String federationExecutionName, URL[] fomModules` | `explicit-deterministic` | `yes` |" in text
    assert "| `requestAttributeValueUpdate` | `Object Management` | `6.19` | `ObjectInstanceHandle theObject, AttributeHandleSet theAttributes, byte[] userSuppliedTag` | `explicit-deterministic` | `yes` |" in text
    assert "| `timeAdvanceGrant` |" in text
