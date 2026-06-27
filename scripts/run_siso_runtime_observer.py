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

from hla.verification.repo_internal.verification.runtime_observer_server import serve_runtime_observer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local runtime observer control server with JSON/SSE endpoints and browser UI.")
    parser.add_argument("--provider", default="siso-runtime", choices=("siso-runtime", "two-federate", "target-radar", "live-federation"))
    parser.add_argument("--scenario", default=None, help="Optional initial scenario id to auto-start.")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd() / "artifacts" / "runtime_observer")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--backend", default=None, help="Optional backend override.")
    args = parser.parse_args(argv)
    print(f"http://{args.host}:{args.port}/")
    serve_runtime_observer(
        provider=args.provider,
        scenario=args.scenario,
        output_dir=args.output_dir,
        host=args.host,
        port=args.port,
        backend=args.backend,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
