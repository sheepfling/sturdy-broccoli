#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hla2010.backends.base import BackendUnavailableError
from hla2010.real_rti import discover_certi_smoke_fom
from hla2010.real_rti_certi import discover_certi_runtime
from hla2010.real_rti_process import reserve_tcp_port


def _check(name: str, func):
    try:
        value = func()
        return True, f"{name}: ok: {value}"
    except BackendUnavailableError as exc:
        return False, f"{name}: blocked: {exc}"
    except Exception as exc:
        return False, f"{name}: error: {exc.__class__.__name__}: {exc}"


def main() -> int:
    argparse.ArgumentParser(
        description="Check whether the local CERTI runtime is runnable."
    ).parse_args()

    checks: list[tuple[bool, str]] = [
        _check("certi_runtime", lambda: discover_certi_runtime().prefix),
        _check("certi_smoke_fom", discover_certi_smoke_fom),
        _check("loopback_bind", lambda: f"reserved tcp port {reserve_tcp_port('127.0.0.1')}"),
    ]

    for _ok, message in checks:
        print(message)

    if all(ok for ok, _message in checks):
        print("result: real CERTI runnable")
        print("easy: ./certi-easy smoke compare")
        print(
            "next: HLA2010_ENABLE_REAL_RTI_SMOKE=1 python3 -m pytest -q "
            "tests/vendors/test_certi_real_backend_exchange_matrix.py "
            "tests/vendors/test_certi_real_backend_time_matrix.py "
            "tests/vendors/test_certi_real_backend_ownership_matrix.py"
        )
        return 0

    print("result: real CERTI will skip")
    print("easy: ./certi-easy doctor")
    print("next: fix the blocked prerequisite above, then rerun this preflight")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
