from __future__ import annotations

import json
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from hla.verification.repo_internal.fom_workbench import write_fom_workbench_html


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
        page.click("#builder-save")

        page.select_option("#catalog-mode", "custom-load-set")
        page.locator("#family-list .family-card", has_text="browser-demo").click()
        inspect_text = page.locator("#inspect-panel").inner_text()
        assert "browser-demo" in inspect_text
        assert "browser-pending" in inspect_text
        assert "./tools/fom-workbench --html --custom-load-set browser-demo=repo-2010-demo,repo-cross-target-radar" in inspect_text

        stored = page.evaluate(f"window.localStorage.getItem({storage_key!r})")
        assert stored is not None
        stored_payload = json.loads(stored)
        assert stored_payload == [{"name": "browser-demo", "member_ids": ["repo-2010-demo", "repo-cross-target-radar"]}]

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
        cards_text = page.locator("#family-list").inner_text()
        assert "browser-demo" in cards_text
        page.locator("#family-list .family-card", has_text="browser-demo").click()
        inspect_text = page.locator("#inspect-panel").inner_text()
        assert "browser-demo" in inspect_text

        page.select_option("#left-family", "browser-demo")
        page.select_option("#right-family", "target-radar")
        diff_text = page.locator("#diff-panel").inner_text()
        assert "No precomputed diff row is available for this pair" in diff_text
        assert "./tools/fom-workbench --html --custom-load-set browser-demo=repo-2010-demo,repo-cross-target-radar --diff browser-demo:target-radar" in diff_text
    finally:
        browser.close()
        pw.stop()
