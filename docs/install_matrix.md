# Install Matrix

This page answers two questions:

1. what do I install first?
2. which extras or external runtimes map to which backend family?

Start with the base Python environment first. Then add only what you need.

For IEEE 1516.1-2025 specifically, treat `hla-backend-python1516-2025` as the main
runtime lane after bootstrap. `hla-backend-shim` remains only as a
compatibility-wrapper/import-compatibility package, and the hosted FedPro
route remains a bounded route variant rather than a separate RTI family.

## Install Order

1. `./tools/bootstrap python`
2. `source .venv/bin/activate`
3. run a pure-Python smoke path or `./tools/python verify`
4. add bridge extras if needed
5. add vendor runtimes only after that

If you need to inspect the local Java toolchain before bridge or language-shim work,
run `./tools/java`.

You can prepend `./tools/bootstrap doctor` before that sequence when you want a
machine/workspace readiness check.

## Base Paths

| Goal | Command | Notes |
| --- | --- | --- |
| Lean local setup | `./tools/bootstrap python` | Default bootstrap path. Installs the core split workspace with lean `test` extras. |
| Broader local QA | `HLA2010_BOOTSTRAP_EXTRAS=qa ./tools/bootstrap python` | Adds Ruff, Pyright, and the bridge package set used by repo-green verification. |
| Manual combined install after activation | `python -m pip install --no-build-isolation ruff pyright jpype1 py4j` | Use when you need both QA and Java bridge helper dependencies together without installing the repo root. |

## Backend Family Matrix

| Backend family | What you need | How to install or enable it | Start here |
| --- | --- | --- | --- |
| Pure Python | Python only | `./tools/bootstrap python` | `./tools/python verify` |
| Java shim | Python only for local shim tests | `./tools/bootstrap python` | `python examples/java_shim_federate.py` |
| JPype bridge | `jpype1` | `HLA2010_BOOTSTRAP_EXTRAS=jpype ./tools/bootstrap python` | `python examples/jpype_java_rti.py` |
| Py4J bridge | `py4j` | `HLA2010_BOOTSTRAP_EXTRAS=py4j ./tools/bootstrap python` | `python examples/py4j_java_rti.py` |
| JPype + Py4J | both bridge deps | `HLA2010_BOOTSTRAP_EXTRAS=java ./tools/bootstrap python` | bridge-specific examples or tests |
| CERTI | working base Python plus local CERTI runtime | bootstrap Python first, then `./tools/certi-easy preflight` | `./tools/certi-easy verify-best-effort` |
| Pitch | working base Python plus local Pitch runtime or Docker flow | bootstrap Python first, then `./tools/pitch preflight` | `./tools/pitch verify-best-effort` |
| Portico | working base Python plus a Portico runtime and a Java bridge path | bootstrap Python first, then add `jpype` or `py4j` extras | route-specific tests |
| REST / gRPC transport | working base Python | bootstrap Python first | transport tests and discovery scripts |

## Rules Of Thumb

- If you are unsure, start with the pure-Python backend.
- If you want the smallest direct 2010/2025 Python comparison first, use `./tools/python smoke-examples --all`.
- For the primary 2025 Python RTI lane, read [`python_rti_backend.md`](python_rti_backend.md)
  after bootstrap rather than inferring runtime ownership from bridge or shim tooling.
- If you want the easiest isolated Java bridge run, use `./tools/java smoke --all` before touching a vendor RTI.
- If you want the real JPype or Py4J path without a vendor RTI, use `./tools/java smoke --bridge jpype --edition 2010 --real-shim` or the Py4J equivalent after installing the bridge extra.
- If you only need to read or modify the API surface, do not install vendor runtimes.
- If you need Java-backed routes, install bridge extras before touching vendor runtimes.
- If you need CERTI or Pitch, treat them as a second phase after Python setup, not as the starting point.
- When you need the strict real-runtime matrix lane after vendor preflight, use `./tools/vendor-green ...`.
- When you need local or sandbox-friendly vendor diagnostics first, use the `*-best-effort` top-level routes before moving on to the strict vendor-green lane.

## Related Docs

- [`python_environment.md`](python_environment.md)
- [`first_run.md`](first_run.md)
- [`python_rti_backend.md`](python_rti_backend.md)
- [`python_rti_reading_map.md`](python_rti_reading_map.md)
- [`rti_options_and_test_matrix.md`](rti_options_and_test_matrix.md)
- [`../packages/hla-backend-certi/docs/certi_section8_runbook.md`](../packages/hla-backend-certi/docs/certi_section8_runbook.md)
- [`../packages/hla-vendor-pitch/docs/pitch_decision_tree.md`](../packages/hla-vendor-pitch/docs/pitch_decision_tree.md)
