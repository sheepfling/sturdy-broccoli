from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "plans" / "2010_python_rti_bounded_family_execution_worklist.md"


def test_2010_bounded_family_execution_worklist_lists_current_bounded_buckets() -> None:
    text = DOC.read_text(encoding="utf-8")

    for token in (
        "`931` matrix rows",
        "`865` `pass`",
        "`25` `partial`",
        "`0` `planned`",
        "`40` `implemented-slice`",
        "mixed_backend_priority_boundaries.md",
        "`CAP-FM`",
        "`CAP-DM`",
        "`CAP-SUP`",
        "`CAP-OM`",
        "`CAP-OWN`",
        "`CAP-TM`",
        "`CAP-DDM`",
        "`CAP-XML` plus `CAP-OMT` tail",
    ):
        assert token in text

    assert "`CAP-XML`: `364 partial`" in text
    assert "`CAP-SUP`: `129 partial`" in text
    assert "`CAP-OM`: `102 partial`" in text
    assert "`CAP-FM`: `79 partial`" in text
    assert "`CAP-OMT`: `2 partial`" in text
    assert "`20` `pass` OMT/XML area rows" in text
    assert "`3` `implemented-slice` OMT/XML execution witnesses" in text
    assert "`0` remaining OMT/XML area partial placeholders" in text

    for token in (
        "`REQ-OMT-4_1-object_model_identification`",
        "`REQ-OMT-Annex_E-schema`",
        "`REQ-OMT-SCHEMA-001`",
    ):
        assert token in text


def test_2010_bounded_family_execution_worklist_keeps_owner_and_tightening_rules_explicit() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "## Execution Rule" in text
    assert "## Latest Investigated Decision" in text
    assert "### Keep-Bounded Rule" in text
    assert "### Tighten-To-Direct Rule" in text
    assert "Primary companion" in text
    assert "Primary shard now" in text
    assert "Stay bounded when" in text
    assert "Tighten only if" in text
    assert "keep these rows as canonical `partial`" in text
    assert "keep the `CAP-SUP` family as canonical `partial`" in text
    assert "uniform bounded tail of" in text
    assert "`43 PRE`, `43 EXC`, and `43 EXC_API` rows" in text
    assert "`REQ-RTI-SS-10_44-getMessageRetractionHandleFactory`" in text
    assert "`REQ-RTI-SS-10_44-getRegionHandleFactory`" in text
    assert "`status=pass` with `python_runtime_disposition=verified`" in text
    assert "keep the `CAP-DM` family as canonical `partial`" in text
    assert "`12 PRE`, `12 EXC`, and `14 EXC_API` rows" in text
    assert "isolated per-row precondition or" in text
    assert "negative-path proof" in text
    assert "keep the `CAP-TM` family as canonical `partial`" in text
    assert "stable bounded tail of" in text
    assert "`19 PRE`, `19 EXC`, `19 EXC_API`, and `1 OVW` row" in text
    assert "keep the `CAP-FM` family as canonical `partial`" in text
    assert "`43 ARG`, `17 CB_ORD`, and a much smaller residual tail of bounded effect," in text
    assert "runtime connection-loss callback proof" in text
    assert "keep the `CAP-OM` family as canonical `partial`" in text
    assert "`25 CB_ORD`, `17 CB_ORDER`, and the remaining bounded effect and exception" in text
    assert "`updateAttributeValues` exception rows" in text
    assert "`requestAttributeValueUpdate`" in text
    assert "`InvalidObjectClassHandle`" in text
    assert "`ObjectClassNotDefined`" in text
    assert "keep the `CAP-OWN` family as canonical `partial`" in text
    assert "`8 PRE`, `11 EXC`, and `11 EXC_API` rows" in text
    assert "isolated per-row negative-path" in text
    assert "keep the `CAP-DDM` family as canonical `partial`" in text
    assert "`6 EXC` and `10 EXC_API` rows" in text
    assert "keep the `CAP-XML / CAP-OMT` family as canonical `partial`" in text
    assert "`274 XML_ELEM`, `89 XML_TYPE`, and `1 CLAUSE12_13_DETAIL` row" in text
    assert "Annex B normalization rows" in text
    assert "there is no remaining hidden `planned` inventory in the `2010` packet" in text
    assert "do not describe the `2010` lane as if every remaining non-`pass` row were" in text
    assert "the remaining OMT/XML rows are no longer planned inventory" in text
    assert "hosted transport connect overload bug" in text
    assert "verification/shard_registry.md" in text
