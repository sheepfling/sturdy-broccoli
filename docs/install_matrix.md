# Install Matrix

This page answers two questions:

1. what do I install first?
2. which extras or external runtimes map to which backend family?

Start with the base Python environment first. Then add only what you need.

## Install Order

1. `./scripts/bootstrap_profile.sh python`
2. `source .venv/bin/activate`
3. run a pure-Python smoke path
4. add bridge extras if needed
5. add vendor runtimes only after that

You can prepend `./scripts/bootstrap_profile.sh doctor` before that sequence when you want a
machine/workspace readiness check.

## Base Paths

| Goal | Command | Notes |
| --- | --- | --- |
| Lean local setup | `./scripts/bootstrap_profile.sh python` | Default operator path. Installs the workspace with lean `test` extras. |
| Broader local QA | `HLA2010_BOOTSTRAP_EXTRAS=qa ./scripts/bootstrap_python.sh` | Adds Ruff and Pyright. |
| Manual combined install after activation | `python -m pip install --no-build-isolation -e ".[qa,java]"` | Use when you need both QA and Java bridge extras together. |

## Backend Family Matrix

| Backend family | What you need | How to install or enable it | Start here |
| --- | --- | --- | --- |
| Pure Python | Python only | `./scripts/bootstrap_profile.sh python` | `python examples/target_radar_simulation.py --backend python --steps 5` |
| Java shim | Python only for local shim tests | `./scripts/bootstrap_profile.sh python` | `python examples/java_shim_federate.py` |
| JPype bridge | `jpype1` | `HLA2010_BOOTSTRAP_EXTRAS=jpype ./scripts/bootstrap_python.sh` | `python examples/jpype_java_rti.py` |
| Py4J bridge | `py4j` | `HLA2010_BOOTSTRAP_EXTRAS=py4j ./scripts/bootstrap_python.sh` | `python examples/py4j_java_rti.py` |
| JPype + Py4J | both bridge deps | `HLA2010_BOOTSTRAP_EXTRAS=java ./scripts/bootstrap_python.sh` | bridge-specific examples or tests |
| CERTI | working base Python plus local CERTI runtime | bootstrap Python first, then `./scripts/certi_easy.sh preflight` | `./scripts/certi_easy.sh smoke compare` |
| Pitch | working base Python plus local Pitch runtime or Docker flow | bootstrap Python first, then `./scripts/pitch_docker_easy.sh preflight` | `./scripts/pitch_docker_easy.sh smoke` |
| Portico | working base Python plus a Portico runtime and a Java bridge path | bootstrap Python first, then add `jpype` or `py4j` extras | route-specific tests |
| REST / gRPC transport | working base Python | bootstrap Python first | transport tests and discovery scripts |

## Rules Of Thumb

- If you are unsure, start with the pure-Python backend.
- If you only need to read or modify the API surface, do not install vendor runtimes.
- If you need Java-backed routes, install bridge extras before touching vendor runtimes.
- If you need CERTI or Pitch, treat them as a second phase after Python setup, not as the starting point.

## Related Docs

- [`python_environment.md`](python_environment.md)
- [`first_run.md`](first_run.md)
- [`rti_options_and_test_matrix.md`](rti_options_and_test_matrix.md)
- [`../packages/hla2010-rti-certi/docs/certi_section8_runbook.md`](../packages/hla2010-rti-certi/docs/certi_section8_runbook.md)
- [`../packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md`](../packages/hla2010-rti-pitch-common/docs/pitch_decision_tree.md)
