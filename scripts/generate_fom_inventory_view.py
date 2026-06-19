from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "docs" / "fom-examples" / "fom_inventory.json"
MD_PATH = REPO_ROOT / "docs" / "fom-examples" / "fom_inventory.md"


def render_inventory_markdown() -> str:
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    entries = payload["entries"]

    lines = [
        "# FOM Inventory",
        "",
        "Generated from `docs/fom-examples/fom_inventory.json`.",
        "",
        "This inventory is the human-readable edition and load-classification view",
        "for repo-owned and third-party FOM XML modules.",
        "",
        "| ID | Edition | Load Mode | Baseline | Scenario Family | Path |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        lines.append(
            f"| `{entry['id']}` | `{entry['edition_class']}` | `{entry['load_mode']}` | "
            f"`{entry['baseline_kind']}` | `{entry['scenario_family']}` | `{entry['path']}` |"
        )

    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for entry in entries:
        groups[entry["scenario_family"]].append(entry)

    lines.extend(["", "## Notes By Scenario Family", ""])
    for family in sorted(groups):
        lines.append(f"### {family}")
        lines.append("")
        for entry in groups[family]:
            lines.append(f"- `{entry['id']}`: {entry['notes']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    MD_PATH.write_text(render_inventory_markdown(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
