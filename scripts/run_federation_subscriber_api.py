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

from hla.verification.repo_internal.verification.runtime_observer_fastapi import build_runtime_observer_fastapi_app


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the FastAPI federation subscriber and control service.")
    parser.add_argument("--provider", default=None, choices=("siso-runtime", "two-federate", "target-radar"))
    parser.add_argument("--scenario", default=None, help="Optional initial scenario id to auto-start.")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd() / "artifacts" / "federation_studio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--backend", default=None, help="Optional backend override.")
    args = parser.parse_args(argv)

    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - operator runtime guard
        raise SystemExit("uvicorn is required for `run_federation_subscriber_api.py`; install repo Python dependencies first.") from exc

    app = build_runtime_observer_fastapi_app(
        output_dir=args.output_dir,
        backend=args.backend,
        provider=args.provider,
        scenario=args.scenario,
    )
    print(f"http://{args.host}:{args.port}/")
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
