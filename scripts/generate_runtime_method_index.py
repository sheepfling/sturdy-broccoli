from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "specs" / "hla2010_api.json"
OUTPUT_PATH = ROOT / "analysis" / "traceability" / "runtime_method_index.md"


def lower_camel_to_snake(name: str) -> str:
    name = name.replace("HLAversion", "HLAVersion")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def build_markdown() -> str:
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    interfaces = payload["interfaces"]
    rows: list[tuple[str, str, str, str, str, str]] = []
    for method_name in sorted(interfaces["RTIambassador"]):
        rows.append(
            (
                method_name,
                lower_camel_to_snake(method_name),
                "RTIambassador",
                "DelegatingRTIAmbassador",
                "_invoke",
                "specs/hla2010_api.json",
            )
        )
    for method_name in sorted(interfaces["FederateAmbassador"]):
        rows.append(
            (
                method_name,
                lower_camel_to_snake(method_name),
                "FederateAmbassador",
                "RecordingFederateAmbassador",
                "record_callback",
                "specs/hla2010_api.json",
            )
        )

    lines = [
        "# Runtime Method Index",
        "",
        "Generated from `specs/hla2010_api.json`.",
        "",
        "| hla_method | python_name | interface | runtime_class | backend_invocation_name | generated_from |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    OUTPUT_PATH.write_text(build_markdown(), encoding="utf-8")
    print(OUTPUT_PATH.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
