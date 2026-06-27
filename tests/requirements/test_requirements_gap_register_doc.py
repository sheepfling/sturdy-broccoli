from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GAP_DOC = ROOT / "docs/plans/requirements_gap_register.md"
QUEUE_DOC = ROOT / "docs/plans/requirements_execution_queue.md"


def test_gap_register_and_queue_keep_owner_companion_split_explicit() -> None:
    gap_text = GAP_DOC.read_text(encoding="utf-8")
    queue_text = QUEUE_DOC.read_text(encoding="utf-8")
    normalized_gap_text = " ".join(gap_text.split())

    assert "`Owner companion`" in gap_text
    assert "use the owner doc to explain the bounded or still-open claim honestly" in gap_text
    assert "use the owner companion to carry canonical row state or backend-resolution" in gap_text
    assert "hla1516_1_priority_backend_resolution.csv" in gap_text
    assert "hla_2025_pitch_202x_group_resolution.csv" in gap_text
    assert "hla_2025_pitch_202x_row_resolution.csv" in gap_text

    assert "use this queue for ordering" in queue_text
    assert "use `requirements_gap_register.md` for the exact owner doc, owner companion" in queue_text
    assert "There are no active `2010` open buckets in this register." in gap_text
    assert "The `2010` backend-compliance packet no longer carries any `planned`" in gap_text
    assert "`20` `pass` OMT/XML area rows" in gap_text
    assert "`3` `implemented-slice` OMT/XML execution witnesses" in gap_text
    assert "`0` remaining OMT/XML area partial placeholders" in gap_text
    assert "Use that worklist when the question is whether to tighten those bounded rows" in gap_text
    assert "There are no active `2025` open buckets in this register." in gap_text
    assert "Maintained optional scope-expansion candidates under the current honest-`100%`" in gap_text
    assert "2010 mixed-backend priority rows" in gap_text
    assert "2010 CAP-SUP bounded family" in gap_text
    assert "uniform bounded `43 PRE`, `43 EXC`, and" in gap_text
    assert "`43 EXC_API` negative-envelope family" in gap_text
    assert "2010 CAP-DM bounded family" in gap_text
    assert "stable bounded `12 PRE`, `12 EXC`, and" in gap_text
    assert "`14 EXC_API` Clause 5 family envelope" in gap_text
    assert "2010 CAP-TM bounded family" in gap_text
    assert "stable bounded `19 PRE`, `19 EXC`, `19 EXC_API`," in gap_text
    assert "and `1 OVW` Clause 8 family envelope" in gap_text
    assert "2010 CAP-FM bounded family" in gap_text
    assert "stable bounded `43 ARG`, `23 EFF`, `17 CB_ORD`," in gap_text
    assert "`15 EXC`, and `11` residual Clause 4 family envelope" in gap_text
    assert "2010 CAP-OM bounded family" in gap_text
    assert "stable bounded `25 EFF`, `25 CB_ORD`," in gap_text
    assert "`17 CB_ORDER`, `16 EXC_API`, `13 EXC`, `6 FED_CB`, and" in gap_text
    assert "`reserveObjectInstanceName` precondition row is also no longer part of that bounded tail" in normalized_gap_text
    assert "`registerObjectInstance` precondition row is also no longer part of that bounded tail" in normalized_gap_text
    assert "`releaseObjectInstanceName` precondition row is also no longer part of that bounded tail" in normalized_gap_text
    assert "`deleteObjectInstance` precondition row is also no longer part of that bounded tail" in normalized_gap_text
    assert "`sendInteraction` precondition row is also no longer part of that bounded tail" in normalized_gap_text
    assert "`updateAttributeValues` precondition row is also no longer part of that bounded tail" in normalized_gap_text
    assert "`localDeleteObjectInstance` precondition row is also no longer part of that bounded tail" in normalized_gap_text
    assert "multiple-name reservation and release precondition rows are also no longer part of that bounded tail" in normalized_gap_text
    assert "`requestAttributeValueUpdate` precondition row is also no longer part of that bounded tail" in normalized_gap_text
    assert "`1 OVW` Clause 6 family envelope" in gap_text
    assert "`updateAttributeValues` exception rows" in gap_text
    assert "`requestAttributeValueUpdate`" in gap_text
    assert "`InvalidObjectClassHandle`" in gap_text
    assert "`ObjectClassNotDefined`" in gap_text
    assert "2010 CAP-OWN bounded family" in gap_text
    assert "stable bounded `8 PRE`, `11 EXC`, and" in gap_text
    assert "`11 EXC_API` Clause 7 family envelope" in gap_text
    assert "2010 CAP-DDM bounded family" in gap_text
    assert "stable bounded `6 EXC` and `10 EXC_API` Clause 9 family envelope" in normalized_gap_text
    assert "2010 CAP-XML / CAP-OMT bounded family" in gap_text
    assert "stable bounded `274 XML_ELEM`, `89 XML_TYPE`," in gap_text
    assert "`1 CLAUSE12_13_DETAIL` envelope" in gap_text
    assert "stable bounded `2` Annex B normalization-row" in gap_text
    assert "kept as an explicit bounded/backend-resolution surface" in gap_text
    assert "2025 framework umbrella rows" in gap_text
    assert "2025 callback-control umbrella slice" in gap_text
    assert "2025 retired/legacy-only rows" in gap_text
    assert "2025 directed-interaction callback umbrella slice" in gap_text
    assert "2025 configuration/auth umbrella slice" in gap_text
    assert "2025 Java/C++ binding umbrella slice" in gap_text
    assert "2025 FedPro protocol umbrella slice" in gap_text
    assert "kept as an explicit bounded hosted-route boundary" in gap_text
    assert "Latest investigated decision" in gap_text
    assert "kept as an explicit umbrella boundary" in gap_text
    assert "2010 CAP-XML / CAP-OMT bounded family" in queue_text
    assert "2025 OMT `xs:any` extension-tolerance boundary" in queue_text
    assert "2010 CAP-XML / CAP-OMT partial families" not in queue_text
    assert "2025 Pitch proto HLA 4 / `202X` backend-resolution lane" in queue_text
    assert "2025 callback-control umbrella slice" in queue_text
    assert "Latest Investigated No-Convert Result" in queue_text
    assert "2025 framework umbrella slice" in queue_text
    assert "do not spend the next closeout slice trying to relabel it as direct `covered`" in queue_text
    assert "2010 mixed-backend priority rows" in queue_text
    assert "keep the canonical rows `pass`" in queue_text
    assert "2010 CAP-SUP bounded family" in queue_text
    assert "2010 CAP-DM bounded family" in queue_text
    assert "2010 CAP-TM bounded family" in queue_text
    assert "2010 CAP-FM bounded family" in queue_text
    assert "2010 CAP-OM bounded family" in queue_text
    assert "2010 CAP-OWN bounded family" in queue_text
    assert "2010 CAP-DDM bounded family" in queue_text
    assert "2010 CAP-XML / CAP-OMT bounded family" in queue_text
    assert "There are no active queue entries at this phase." in queue_text
    assert "do not spend the next closeout slice trying to relabel it as direct support" in queue_text
    assert "support-services owner docs as maintained bounded documentation" in queue_text
    assert "time-management owner docs as maintained bounded documentation" in queue_text
    assert "federation-management owner docs as maintained bounded documentation" in queue_text
    assert "ownership-management owner docs as maintained bounded documentation" in queue_text
    assert "data-distribution owner docs as maintained bounded documentation" in queue_text
    assert "OMT/XML owner docs as maintained bounded documentation" in queue_text
    assert "no narrower direct claim was identified" in queue_text
    assert "bounded hosted-route child proof" in queue_text
