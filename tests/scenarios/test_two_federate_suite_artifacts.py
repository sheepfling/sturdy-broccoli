from __future__ import annotations

import csv
import json

from hla2010.testing.two_federate_suite import write_two_federate_suite_artifacts


def test_two_federate_suite_artifacts_are_generated(tmp_path):
    paths = write_two_federate_suite_artifacts(tmp_path, target_radar_steps=3)

    summary = json.loads(paths.summary_json.read_text())
    assert summary["suite_name"] == "two-federate-suite"
    assert summary["primary_profile"] == "python"
    assert len(summary["scenario_rows"]) == 7
    assert len(summary["profiles"]) >= 4
    assert summary["profiles"][0]["profile"] == "python"
    assert len(summary["target_radar"]["track_reports"]) == 3
    assert summary["exchange"]["history"]["timestamp_interaction"]["method_name"] == "receiveInteraction"

    with paths.track_reports_csv.open() as handle:
        track_rows = list(csv.DictReader(handle))
    assert len(track_rows) == 3
    assert track_rows[0]["track_id"] == "TRK-001"

    with paths.callbacks_csv.open() as handle:
        callback_rows = list(csv.DictReader(handle))
    assert callback_rows
    assert any(row["method_name"] == "federationSynchronized" for row in callback_rows)
    assert "profile" in callback_rows[0]
    assert "scenario" in callback_rows[0]

    report_text = paths.report_markdown.read_text()
    assert "Two-Federate Suite" in report_text
    assert "## Profiles" in report_text
    assert "target_radar" in report_text

    svg_text = paths.summary_svg.read_text()
    assert "<svg" in svg_text
    assert "Target/radar range growth" in svg_text

    timeline_text = paths.timeline_svg.read_text()
    assert "<svg" in timeline_text
    assert "Callback Timeline" in timeline_text
