# hla-verification

Shared verification harness package for repo-internal test packets and suite
helpers.

This package now owns generic two-federate packet mechanics such as:

- suite pair construction helpers
- callback timeline recording
- JSON normalization and callback-row shaping
- suite packet path types
- generic markdown/SVG/CSV writer helpers
- reusable two-federate time-window future-exclusion and restore-state proof
  routing for the composite suite

It intentionally does not own concrete backend runtime policy or example/FOM
logic. Target/Radar-specific artifact wording and vendor profile policy remain
with `hla-fom-target-radar`.

Use this package when you need:

- reusable two-federate scenario mechanics
- callback timeline capture and normalized summary shaping
- shared artifact writer helpers that are not specific to one backend or one
  example package

Import the canonical implementation from `hla.verification`.
It does not own human operator entrypoints; those live under `./tools/`.
Guard coverage for the shared harness boundary and thin-wrapper contract lives
in `tests/test_verification_harness_split_package.py` and
`tests/test_backend_wrapper_policy.py`.
