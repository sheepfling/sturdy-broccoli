from __future__ import annotations

from collections.abc import Iterable, Mapping

DISALLOWED_CLOSEOUT_TRUTH_SOURCES = (
    "docs/plans/",
    "analysis/compliance/presentation_packets",
    "analysis/compliance/python_final_requirements_report.md",
    "analysis/compliance/python_boss_capability_brief.md",
)


def assert_rows_do_not_use_closeout_truth_sources(
    rows: Iterable[Mapping[str, str]],
    *,
    reference_field: str = "current_test_id",
    requirement_field: str = "packet_requirement_id",
) -> None:
    for row in rows:
        for forbidden in DISALLOWED_CLOSEOUT_TRUTH_SOURCES:
            assert forbidden not in row[reference_field], (
                f"{row[requirement_field]} should not use {forbidden} as a truth source"
            )
