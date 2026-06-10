# Two-Federate Quick Start

Use this when you want the fastest path to the repo's two-federate example.

## Run It

```bash
python3 scripts/run_two_federate_suite.py
```

That command:

- runs the composite two-federate suite
- writes artifacts under `analysis/two_federate_suite/`
- exercises the pair-based scenario flow used by the verification packet

If you want a smaller or custom artifact set, the script also accepts:

```bash
python3 scripts/run_two_federate_suite.py --output-dir analysis/my_two_federate_suite
python3 scripts/run_two_federate_suite.py --target-radar-steps 6
```

## What To Read Next

If you are helping someone understand the example, start here:

- [`scripts/run_two_federate_suite.py`](../scripts/run_two_federate_suite.py)
- [`src/hla2010_repo_internal/verification/two_federate_suite_runner.py`](../src/hla2010_repo_internal/verification/two_federate_suite_runner.py)

If you want the broader verification context, use:

- [`docs/verification/run_sequence.md`](verification/run_sequence.md)
- [`docs/local_verification_commands.md`](local_verification_commands.md)

## When To Use It

This is the best entry point when you want to:

- explain how the repo exercises two federates together
- point someone at the first runnable artifact-producing example
- show where the generated report and CSV/SVG artifacts land

## Read Next

1. [`verification/run_sequence.md`](verification/run_sequence.md)
2. [`local_verification_commands.md`](local_verification_commands.md)
3. [`../README.md`](../README.md)
