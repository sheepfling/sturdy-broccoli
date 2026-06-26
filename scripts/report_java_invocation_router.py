#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import tomllib


ROOT = Path(__file__).resolve().parents[1]


def _bootstrap_source_checkout() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
    for root in reversed(source_roots):
        source_path = str(ROOT / root)
        if source_path not in sys.path:
            sys.path.insert(0, source_path)


def _route_payload(route: object) -> dict[str, object]:
    return {
        "method_name": getattr(route, "method_name"),
        "arity": getattr(route, "arity"),
        "params": list(getattr(route, "params")),
        "rationale": getattr(route, "rationale"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report the configured Java invocation resolver and deterministic route coverage.")
    parser.add_argument("--router", choices=("weighted", "deterministic"), default="weighted")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    _bootstrap_source_checkout()

    from hla.backends.common import (
        get_deterministic_java_invocation_router,
        java_invocation_resolver,
        java_invocation_resolver_name,
    )

    deterministic_router = get_deterministic_java_invocation_router()
    payload = {
        "active_resolver": args.router,
        "active_resolver_callable": java_invocation_resolver_name(java_invocation_resolver(args.router)),
        "available_resolvers": ["weighted", "deterministic"],
        "deterministic_route_count": len(deterministic_router.routes),
        "deterministic_routes": [_route_payload(route) for route in deterministic_router.routes],
    }

    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print(f"Java invocation resolver: {payload['active_resolver']}")
    print(f"Callable: {payload['active_resolver_callable']}")
    print("Available resolvers: weighted, deterministic")
    print("")
    print("Deterministic route coverage")
    print("")
    print("method | arity | params | rationale")
    print("--- | --- | --- | ---")
    for route in payload["deterministic_routes"]:
        params = ", ".join(route["params"])
        print(f"{route['method_name']} | {route['arity']} | {params} | {route['rationale']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
