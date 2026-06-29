#!/usr/bin/env python3
"""Generate the HLA 1516e-2010 FedPro-style gRPC Python stubs."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
PACKAGE_ROOT = ROOT / "packages" / "hla-transport-grpc"
PROTO_DIR = PACKAGE_ROOT / "proto" / "rti1516e" / "fedpro"
OUT_DIR = PACKAGE_ROOT / "src" / "hla" / "transports" / "grpc" / "fedpro2010"
PROTO_FILES = (
    "datatypes.proto",
    "RTIambassador.proto",
    "FederateAmbassador.proto",
    "HLA2010RTITransport.proto",
)
IMPORT_REWRITES = {
    r"^import datatypes_pb2 as datatypes__pb2$": (
        "from hla.transports.grpc.fedpro2010 import datatypes_pb2 as datatypes__pb2"
    ),
    r"^import FederateAmbassador_pb2 as FederateAmbassador__pb2$": (
        "from hla.transports.grpc.fedpro2010 import FederateAmbassador_pb2 as FederateAmbassador__pb2"
    ),
    r"^import RTIambassador_pb2 as RTIambassador__pb2$": (
        "from hla.transports.grpc.fedpro2010 import RTIambassador_pb2 as RTIambassador__pb2"
    ),
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        "-I",
        str(PROTO_DIR),
        f"--python_out={OUT_DIR}",
        f"--grpc_python_out={OUT_DIR}",
        *(str(PROTO_DIR / item) for item in PROTO_FILES),
    ]
    subprocess.run(command, check=True)
    for path in OUT_DIR.glob("*_pb2*.py"):
        text = path.read_text()
        for pattern, replacement in IMPORT_REWRITES.items():
            text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
        path.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
