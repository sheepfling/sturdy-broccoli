#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "rti_options_and_test_matrix.md"

START = "<!-- GENERATED_BACKEND_ALIASES_START -->"
END = "<!-- GENERATED_BACKEND_ALIASES_END -->"


def _extract_alias_sets() -> list[tuple[str, list[str]]]:
    from hla2010 import rti

    groups: list[tuple[str, list[str]]] = []
    for plugin in rti.iter_rti_backend_plugins():
        aliases = sorted({plugin.name, *plugin.aliases})
        alias_values = sorted(aliases)
        key = _classify(alias_values)
        if key is None:
            continue
        groups.append((key, alias_values))
    return groups


def _classify(aliases: list[str]) -> str | None:
    alias_set = set(aliases)
    if "python" in alias_set:
        return "Pure Python"
    if any("pitch" in alias for alias in aliases):
        return "Pitch"
    if any("portico" in alias for alias in aliases):
        return "Portico"
    if any(alias.startswith("certi") or alias.endswith("certi") for alias in aliases):
        return "CERTI"
    if any("shim" in alias for alias in aliases):
        return "Java Shim"
    if "jpype" in alias_set or "java-jpype" in alias_set:
        return "Generic Java Adapter Paths"
    if "py4j" in alias_set or "java-py4j" in alias_set:
        return "Generic Java Adapter Paths"
    return None


def _render_generated_section() -> str:
    ordered_sections = [
        "Pure Python",
        "Generic Java Adapter Paths",
        "Pitch",
        "Portico",
        "CERTI",
        "Java Shim",
    ]
    buckets: dict[str, list[list[str]]] = {key: [] for key in ordered_sections}
    for key, aliases in _extract_alias_sets():
        buckets[key].append(aliases)

    lines: list[str] = []
    for section in ordered_sections:
        alias_groups = buckets[section]
        if not alias_groups:
            continue
        lines.append(f"### {section}")
        lines.append("")
        for aliases in alias_groups:
            for alias in aliases:
                lines.append(f"- `{alias}`")
            lines.append("")
        if section == "Generic Java Adapter Paths":
            lines.append("These are only useful when you provide a Java RTI configuration explicitly.")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    original = DOC.read_text(encoding="utf-8")
    start = original.index(START) + len(START)
    end = original.index(END)
    generated = "\n\n" + _render_generated_section() + "\n"
    updated = original[:start] + generated + original[end:]
    DOC.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
