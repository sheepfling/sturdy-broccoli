from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

SCRIPT_REPO_ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((SCRIPT_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(SCRIPT_REPO_ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


_bootstrap_source_checkout()

from hla.verification.repo_internal.verification.federate_service_fastapi import build_federate_service_fastapi_app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the FastAPI federate service contract and bounded RTI proxy.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8788)
    args = parser.parse_args(argv)

    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - operator runtime guard
        raise SystemExit("uvicorn is required for `run_federate_service_api.py`; install repo Python dependencies first.") from exc

    app = build_federate_service_fastapi_app()
    print(f"http://{args.host}:{args.port}/")
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
