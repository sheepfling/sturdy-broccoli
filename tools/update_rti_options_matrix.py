#!/usr/bin/env python3
from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RTI_PY = ROOT / "hla2010" / "rti.py"
DOC = ROOT / "docs" / "rti_options_and_test_matrix.md"

START = "<!-- GENERATED_BACKEND_ALIASES_START -->"
END = "<!-- GENERATED_BACKEND_ALIASES_END -->"


def _extract_alias_sets() -> list[tuple[str, list[str]]]:
    source = RTI_PY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    create_backend = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "create_backend"
    )
    groups: list[tuple[str, list[str]]] = []
    for node in create_backend.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "normalized"
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.In)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Set)
        ):
            continue
        alias_values: list[str] = []
        valid = True
        for elt in test.comparators[0].elts:
            if not isinstance(elt, ast.Constant) or not isinstance(elt.value, str):
                valid = False
                break
            alias_values.append(elt.value)
        if not valid:
            continue
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
