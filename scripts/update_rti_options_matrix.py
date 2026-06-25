#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]

START = "<!-- GENERATED_BACKEND_ALIASES_START -->"
END = "<!-- GENERATED_BACKEND_ALIASES_END -->"


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()


def _extract_alias_sets() -> list[tuple[str, list[str]]]:
    from hla.rti.factory import iter_rti_backend_plugins

    groups: list[tuple[str, list[str]]] = []
    for plugin in iter_rti_backend_plugins():
        aliases = sorted({plugin.name, *plugin.aliases})
        key = _classify(aliases)
        if key is None:
            continue
        alias_values = sorted(aliases, key=lambda alias: _alias_sort_key(key, alias))
        groups.append((key, alias_values))
    return groups


def _alias_sort_key(section: str, alias: str) -> tuple[int, str]:
    if section == "Pure Python":
        preferred_order = {
            "python1516e": 0,
            "python-1516e": 1,
            "python": 2,
            "in-memory": 3,
            "python-in-memory": 4,
        }
        return (preferred_order.get(alias, 100), alias)
    return (0, alias)


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
    if any("cpp-shim" in alias or "native-cpp-shim" in alias for alias in aliases):
        return "C++ Shim"
    if any(alias.startswith("java-standard-") for alias in aliases):
        return "Standard Java Shim"
    if any("java-shim" in alias or alias.startswith("shim-") for alias in aliases):
        return "Java Shim"
    if any("shim" in alias for alias in aliases):
        return "Spec Shim"
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
        "Standard Java Shim",
        "C++ Shim",
        "Java Shim",
        "Spec Shim",
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


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Refresh the generated backend alias inventory in the RTI options matrix.")
    parser.add_argument(
        "--project-root",
        default=str(SCRIPT_REPO_ROOT),
        help="Repository root containing docs/rti_options_and_test_matrix.md",
    )
    args = parser.parse_args(argv)
    root = Path(args.project_root).resolve()
    doc = root / "docs" / "rti_options_and_test_matrix.md"

    original = doc.read_text(encoding="utf-8")
    start = original.index(START) + len(START)
    end = original.index(END)
    generated = "\n\n" + _render_generated_section() + "\n"
    updated = original[:start] + generated + original[end:]
    doc.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
