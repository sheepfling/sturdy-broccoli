# Two-Federate Quick Start

Use this when you want the fastest path to the repo's two-federate example.

This page is scenario-first, not edition-neutral architecture guidance. For the
current 2025 runtime-lane ownership and wrapper boundary, use
[`python_rti_backend.md`](python_rti_backend.md).

## Run It

```bash
source .venv/bin/activate
./tools/two-federate
```

That command:

- runs the composite two-federate suite
- writes artifacts under `analysis/two_federate_suite/`
- exercises the pair-based scenario flow used by the verification packet
- includes the trial-safe two-federate 2025 time-window `future-exclusion`
  and `restore-state` proofs alongside the exchange, ownership,
  save/restore, DDM, and Target/Radar paths
- delegates into the shared runner at
  `packages/hla-verification/src/hla/verification/repo_internal/verification/two_federate_suite_runner.py`

If you want a smaller or custom artifact set, the script also accepts:

```bash
source .venv/bin/activate
./tools/two-federate --output-dir analysis/my_two_federate_suite
source .venv/bin/activate
./tools/two-federate --target-radar-steps 6
```

## What To Read Next

If you are helping someone understand the example, start here:

- [`./tools/two-federate`](../tools/two-federate)
- [`packages/hla-verification/src/hla/verification/repo_internal/verification/two_federate_suite_runner.py`](../packages/hla-verification/src/hla/verification/repo_internal/verification/two_federate_suite_runner.py)

If you want the broader verification context, use:

- [`docs/verification/run_sequence.md`](verification/run_sequence.md)
- [`docs/local_verification_commands.md`](local_verification_commands.md)

If you want the 2025 RTI-specific runtime path behind these scenarios, use:

- [`python_rti_backend.md`](python_rti_backend.md)
- [`python_rti_reading_map.md`](python_rti_reading_map.md)
- [`verification/time_model_compliance.md`](verification/time_model_compliance.md)

## When To Use It

This is the best entry point when you want to:

- explain how the repo exercises two federates together
- point someone at the first runnable artifact-producing example
- show where the generated report and CSV/SVG artifacts land
- exercise the smallest reusable time-window proofs that can also be replayed
  against constrained vendor routes such as the current Pitch two-federate lane

For IEEE 1516.1-2025 work, remember that the scenario may run over the main full
`python2025` lane or bounded hosted route variants, but `hla-backend-python2025`
remains the main runtime and `shim` does not count as a separate RTI family.

## Read Next

1. [`verification/run_sequence.md`](verification/run_sequence.md)
2. [`local_verification_commands.md`](local_verification_commands.md)
3. [`../README.md`](../README.md)

## Historical / Provenance

The operator wrapper is implemented by
[`scripts/run_two_federate_suite.py`](../scripts/run_two_federate_suite.py),
which in turn uses the shared repo-internal runner at
[`packages/hla-verification/src/hla/verification/repo_internal/verification/two_federate_suite_runner.py`](../packages/hla-verification/src/hla/verification/repo_internal/verification/two_federate_suite_runner.py).
