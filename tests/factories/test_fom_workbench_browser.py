from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from hla.verification.repo_internal.fom_workbench import write_fom_workbench_html
from hla.verification.repo_internal.fom_inventory import FOMInventoryRecord, inventory_records


CONFLICTING_2010_LOAD_SET_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<objectModel xmlns="http://standards.ieee.org/IEEE1516-2010">
  <modelIdentification><name>{name}</name><type>FOM</type></modelIdentification>
  <dataTypes>
    <simpleDataTypes>
      <simpleData><name>SharedType</name><representation>{representation}</representation></simpleData>
    </simpleDataTypes>
  </dataTypes>
</objectModel>
"""


def _launch_browser():
    errors: list[str] = []
    manager = playwright.sync_playwright()
    pw = manager.start()
    for browser_type_name in ("chromium", "webkit", "firefox"):
        browser_type = getattr(pw, browser_type_name)
        try:
            browser = browser_type.launch(headless=True)
            return pw, browser, browser_type_name
        except Exception as exc:  # pragma: no cover - only exercised in blocked envs
            errors.append(f"{browser_type_name}: {exc}")
    pw.stop()
    pytest.skip("Playwright browser launch failed: " + " | ".join(errors))


def test_fom_workbench_browser_saved_custom_load_set_flow(tmp_path: Path) -> None:
    output_dir = tmp_path / "workbench-browser"
    html_path = write_fom_workbench_html(
        output_dir=output_dir,
        custom_load_sets={
            "custom-target-plus-demo": ("repo-cross-target-radar", "repo-2010-demo"),
        },
        diff_specs=(("target-radar", "custom-target-plus-demo"),),
    )

    pw, browser, _browser_name = _launch_browser()
    try:
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri())

        storage_key = "hla2010-fom-workbench-custom-load-sets"
        page.evaluate("window.localStorage.clear()")
        page.reload()

        page.fill("#builder-name", "browser-demo")
        page.check('input[data-entry-id="repo-cross-target-radar"]')
        page.check('input[data-entry-id="repo-2010-demo"]')
        builder_health = page.locator("#builder-health").inner_text()
        assert "known warning" in builder_health
        assert "mixes multiple edition classes or edition scopes" in builder_health
        page.click("#builder-save")

        page.select_option("#catalog-mode", "custom-load-set")
        page.locator("#family-list .family-card", has_text="browser-demo").click()
        assert page.locator('.workspace-tab.active[data-workspace="overview"]').count() == 1
        summary_text = page.locator("#selection-summary").inner_text()
        assert "browser-demo" in summary_text
        assert "NEXT ACTION" in summary_text
        assert "BROWSER-SAVED LOAD SET" in summary_text
        assert "ownership: repo-owned" in summary_text
        assert "browser-demo" in page.locator("#recent-selections").inner_text()
        inspect_text = page.locator("#inspect-panel").inner_text()
        assert "browser-demo" in inspect_text
        assert "browser-pending" in inspect_text
        page.locator("#inspect-panel summary", has_text="Operator commands").click()
        inspect_text = page.locator("#inspect-panel").inner_text()
        assert "./tools/fom-workbench --html --custom-load-set browser-demo=repo-cross-target-radar,repo-2010-demo" in inspect_text
        conflict_text = page.locator("#conflict-panel").inner_text()
        assert "browser pending" in conflict_text.lower()
        validation_text = page.locator("#validation-panel").inner_text()
        assert "Validation state" in validation_text
        assert "Verdict" in validation_text
        assert "Issues" in validation_text
        page.click('.workspace-tab[data-workspace="validation"]')
        assert page.locator('button:has-text("Copy Validation Command")').count() >= 1
        page.locator("#family-list .family-card", has_text="custom-target-plus-demo").click()
        assert "custom-target-plus-demo" in page.locator("#selection-summary").inner_text()
        assert "browser-demo" in page.locator("#recent-selections").inner_text()
        assert "custom-target-plus-demo" in page.locator("#recent-selections").inner_text()
        page.locator("#recent-selections button", has_text="browser-demo").click()
        assert "browser-demo" in page.locator("#selection-summary").inner_text()

        stored = page.evaluate(f"window.localStorage.getItem({storage_key!r})")
        assert stored is not None
        stored_payload = json.loads(stored)
        assert stored_payload == [{"name": "browser-demo", "member_ids": ["repo-cross-target-radar", "repo-2010-demo"]}]

        page.click("#builder-export")
        exported = page.input_value("#builder-transfer")
        exported_payload = json.loads(exported)
        assert exported_payload == stored_payload

        page.evaluate(
            f"""
            window.localStorage.removeItem({storage_key!r});
            """
        )
        page.fill("#builder-transfer", exported)
        page.click("#builder-import")
        restored = page.evaluate(f"window.localStorage.getItem({storage_key!r})")
        assert restored is not None
        restored_payload = json.loads(restored)
        assert restored_payload == stored_payload

        page.select_option("#catalog-mode", "custom-load-set")
        page.select_option("#status-filter", "browser-pending")
        cards_text = page.locator("#family-list").inner_text()
        assert "browser-demo" in cards_text
        page.locator("#family-list .family-card", has_text="browser-demo").click()
        inspect_text = page.locator("#inspect-panel").inner_text()
        assert "browser-demo" in inspect_text
        assert page.locator("#left-family").input_value() == "browser-demo"

        page.click('.workspace-tab[data-workspace="diff"]')
        assert page.locator('.workspace-tab.active[data-workspace="diff"]').count() == 1
        page.select_option("#left-family", "browser-demo")
        page.select_option("#right-family", "target-radar")
        diff_text = page.locator("#diff-panel").inner_text()
        assert "This snapshot does not contain a precomputed diff for the selected pair." in diff_text
        assert "Copy Regenerate Diff Command" in diff_text
        assert "browser-demo" in page.locator("#recent-comparisons").inner_text()
        assert "target-radar" in page.locator("#recent-comparisons").inner_text()
        page.locator("#diff-panel summary", has_text="Operator commands").click()
        diff_text = page.locator("#diff-panel").inner_text()
        assert "./tools/fom-workbench --html --custom-load-set browser-demo=repo-cross-target-radar,repo-2010-demo --diff browser-demo:target-radar" in diff_text
    finally:
        browser.close()
        pw.stop()


def test_fom_workbench_browser_symbol_jump_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    suffix = uuid.uuid4().hex[:8]
    first_name = f"merge-conflict-a-{suffix}.xml"
    second_name = f"merge-conflict-b-{suffix}.xml"
    first = repo_root / first_name
    second = repo_root / second_name
    first.write_text(CONFLICTING_2010_LOAD_SET_TEMPLATE.format(name="A", representation="HLAinteger32BE"), encoding="utf-8")
    second.write_text(CONFLICTING_2010_LOAD_SET_TEMPLATE.format(name="B", representation="HLAinteger64BE"), encoding="utf-8")
    try:
        base_records = inventory_records()
        monkeypatch.setattr(
            "hla.verification.repo_internal.fom_workbench.inventory_records",
            lambda: base_records
            + (
                FOMInventoryRecord(
                    id="merge-conflict-a",
                    path=first_name,
                    edition_class="2010",
                    load_mode="standalone",
                    baseline_kind="repo-owned",
                    scenario_family="merge-conflict",
                    notes="synthetic conflict fixture a",
                ),
                FOMInventoryRecord(
                    id="merge-conflict-b",
                    path=second_name,
                    edition_class="2010",
                    load_mode="standalone",
                    baseline_kind="repo-owned",
                    scenario_family="merge-conflict",
                    notes="synthetic conflict fixture b",
                ),
            ),
        )
        html_path = write_fom_workbench_html(
            output_dir=tmp_path / "workbench-symbol-jumps",
            custom_load_sets={"conflict-set": ("merge-conflict-a", "merge-conflict-b")},
            diff_specs=(("target-radar", "proto2025-message-test"), ("conflict-set", "target-radar")),
        )

        pw, browser, _browser_name = _launch_browser()
        try:
            page = browser.new_page()
            page.goto(html_path.resolve().as_uri())

            page.select_option("#catalog-mode", "custom-load-set")
            page.locator("#family-list .family-card", has_text="conflict-set").click()
            assert page.locator('.workspace-tab.active[data-workspace="conflict"]').count() == 1
            assert "conflict-set" in page.locator("#selection-summary").inner_text()
            assert "Ownership mix" in page.locator("#conflict-panel").inner_text()
            page.click('button:has-text("Prepare Repair")')
            assert page.locator('.workspace-tab.active[data-workspace="repair"]').count() == 1
            page.click('.workspace-tab[data-workspace="conflict"]')
            page.click("#conflict-copy-symbol")
            assert page.input_value("#search-filter") == "SharedType"
            assert page.locator("#active-symbol-summary").inner_text() == "Pinned symbol: SharedType"
            assert page.locator("#search-results tr").count() >= 1
            assert "No merged names match the current search scope." in page.locator("#search-results").inner_text()
            repair_text = page.locator("#edit-command").inner_text()
            assert "Align merge-conflict-a to merge-conflict-b" in repair_text
            assert "--set-simple-datatype-representation" in repair_text
            assert "Target file:" in repair_text
            assert first_name in repair_text
            assert "./tools/fom-workbench --html --custom-load-set conflict-set=merge-conflict-a,merge-conflict-b" in repair_text

            page.select_option("#catalog-mode", "family")
            page.locator("#family-list .family-card", has_text="target-radar").click()
            page.evaluate(
                """
                const family = snapshot.families.find((item) => item.scenario_family === "target-radar");
                family.validation_verdict = "warning";
                family.validation_issue_count = 1;
                family.validation_issue_layers = ["semantic"];
                family.validation_issue_groups = [{
                  layer: "semantic",
                  count: 1,
                  messages: ["Symbol HLAobjectRoot.Target has inconsistent semantics."]
                }];
                renderValidationWorkspace();
                """
            )
            assert page.locator('.workspace-tab.active[data-workspace="overview"]').count() == 1
            page.click('.workspace-tab[data-workspace="validation"]')
            assert page.locator('.workspace-tab.active[data-workspace="validation"]').count() == 1
            assert "Verdict" in page.locator("#validation-panel").inner_text()
            page.click('button:has-text("Investigate First Issue")')
            assert page.input_value("#search-filter") == "HLAobjectRoot.Target"
            page.locator("#validation-panel .symbol-link", has_text="HLAobjectRoot.Target").click()
            assert page.input_value("#search-filter") == "HLAobjectRoot.Target"
            assert page.locator("#tree-kind").input_value() == "object"
            assert "HLAobjectRoot.Target" in page.locator("#node-panel").inner_text()
            assert page.locator("#active-symbol-summary").inner_text() == "Pinned symbol: HLAobjectRoot.Target"
            page.fill("#workspace-focus-filter", "symbol:NoSuchSymbol")
            assert "No validation issues match the workspace focus." in page.locator("#validation-panel").inner_text()
            page.fill("#workspace-focus-filter", "symbol:HLAobjectRoot.Target")
            assert "Symbol HLAobjectRoot.Target has inconsistent semantics." in page.locator("#validation-panel").inner_text()
            assert page.locator("#workspace-focus-status").inner_text() == "Focus: symbol:HLAobjectRoot.Target"
            page.fill("#workspace-focus-filter", "")
            page.fill("#search-filter", "")
            page.keyboard.press("ArrowDown")
            assert page.locator("#search-results .search-row.active").count() == 1
            assert page.locator("#active-symbol-summary").inner_text().startswith("Pinned symbol: HLAobjectRoot.")

            page.click('.workspace-tab[data-workspace="diff"]')
            assert page.locator('.workspace-tab.active[data-workspace="diff"]').count() == 1
            assert page.locator("#active-symbol-summary").inner_text().startswith("Pinned symbol: HLAobjectRoot.")
            assert "target-radar" in page.locator("#selection-summary").inner_text()

            page.select_option("#left-family", "target-radar")
            page.select_option("#right-family", "proto2025-message-test")
            assert "Object deltas" in page.locator("#diff-panel").inner_text()
            page.click('button[data-focus-kind="object"]')
            assert page.locator("#workspace-focus-status").inner_text() == "Focus: object"
            assert "Only Left Objects" in page.locator("#diff-panel").inner_text()
            assert "Only Left Interactions" not in page.locator("#diff-panel").inner_text()
            page.fill("#workspace-focus-filter", "Target")
            assert "HLAobjectRoot.Target" in page.locator("#diff-panel").inner_text()
            page.fill("#workspace-focus-filter", "Track")
            assert "HLAobjectRoot.Track" in page.locator("#search-results").inner_text()
            page.click('button[data-focus-kind="all"]')
            page.fill("#workspace-focus-filter", "")
            page.locator("#diff-panel .symbol-link", has_text="HLAobjectRoot.Target").first.click()
            assert page.input_value("#search-filter") == "HLAobjectRoot.Target"
            assert "HLAobjectRoot.Target" in page.locator("#node-panel").inner_text()
        finally:
            browser.close()
            pw.stop()
    finally:
        first.unlink(missing_ok=True)
        second.unlink(missing_ok=True)
