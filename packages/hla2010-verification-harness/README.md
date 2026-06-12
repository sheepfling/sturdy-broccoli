# hla2010-verification-harness

Shared verification harness package for repo-internal test packets and suite
helpers.

This package now owns generic two-federate packet mechanics such as:

- suite pair construction helpers
- callback timeline recording
- JSON normalization and callback-row shaping
- suite packet path types
- generic markdown/SVG/CSV writer helpers

It intentionally does not own concrete backend runtime policy or example/FOM
logic. Target/Radar-specific artifact wording and vendor profile policy remain
with `hla2010-fom-target-radar`.
Import the canonical implementation from `hla2010_verification_harness`.
Guard coverage for the shared harness boundary and thin-wrapper contract lives
in `tests/test_verification_harness_split_package.py` and
`tests/test_backend_wrapper_policy.py`.

This package does not own human operator entrypoints; repo-local operator flows
stay under `./tools/`.
