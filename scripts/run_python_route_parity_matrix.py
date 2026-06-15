#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path.cwd()


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla2010_repo_internal.verification.python_route_parity_matrix import write_python_route_parity_matrix


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the Python direct-vs-gRPC route parity matrix artifacts.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "analysis" / "traceability"),
        help="Directory for generated parity matrix artifacts",
    )
    args = parser.parse_args(argv)
    csv_path, md_path = write_python_route_parity_matrix(args.output_dir)
    print(csv_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
{"argv": [], "pythonpath": "/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-spec/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-python/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-certi/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-backend-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-java-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-runtime-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-java-jpype/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-java-py4j/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-pitch-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-pitch-jpype/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-pitch-py4j/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-portico/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-transport-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-transport-grpc/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-transport-rest/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-fom-target-radar/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-fom-minimal-demo/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-verification-harness/src"}
{"argv": [], "pythonpath": "/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-spec/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-python/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-certi/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-backend-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-java-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-runtime-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-java-jpype/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-java-py4j/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-pitch-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-pitch-jpype/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-pitch-py4j/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-portico/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-transport-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-transport-grpc/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-transport-rest/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-fom-target-radar/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-fom-minimal-demo/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-verification-harness/src"}
{"argv": [], "pythonpath": "/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-spec/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-python/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-certi/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-backend-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-java-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-runtime-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-java-jpype/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-java-py4j/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-pitch-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-pitch-jpype/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-pitch-py4j/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-portico/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-transport-common/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-transport-grpc/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-rti-transport-rest/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-fom-target-radar/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-fom-minimal-demo/src:/Users/rick/Library/Mobile Documents/com~apple~CloudDocs/GIT/hla-2010/packages/hla2010-verification-harness/src"}
