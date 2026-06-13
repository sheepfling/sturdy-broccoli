# Two-Federate Quick Start

Use this when you want the fastest path to the repo's two-federate example.

This quick start assumes the default `python` / `in-memory` RTI factory path is
already the intended route. If you want to verify that selection first, run:

```bash
source .venv/bin/activate
./tools/rti-factories show in-memory --probe
```

## Run It

```bash
source .venv/bin/activate
./tools/two-federate
```

That command:

- runs the composite two-federate suite
- writes artifacts under `analysis/two_federate_suite/`
- uses the pure Python RTI factory path for the default local route
- exercises the pair-based scenario flow used by the verification packet
- delegates into the shared runner at
  `src/hla2010_repo_internal/verification/two_federate_suite_runner.py`

If you want a smaller or custom artifact set, the script also accepts:

```bash
source .venv/bin/activate
./tools/two-federate --output-dir analysis/my_two_federate_suite
source .venv/bin/activate
./tools/two-federate --target-radar-steps 6
```

## What To Read Next

If you are helping someone understand the example, start here:

- [`./tools/rti-factories show in-memory --probe`](../tools/rti-factories)
- [`./tools/two-federate`](../tools/two-federate)
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
3. [`rti_factory_reading_map.md`](rti_factory_reading_map.md)
4. [`../README.md`](../README.md)

## Historical / Provenance

The operator wrapper is implemented by
[`scripts/run_two_federate_suite.py`](../scripts/run_two_federate_suite.py),
which in turn uses the shared repo-internal runner at
[`src/hla2010_repo_internal/verification/two_federate_suite_runner.py`](../src/hla2010_repo_internal/verification/two_federate_suite_runner.py).
