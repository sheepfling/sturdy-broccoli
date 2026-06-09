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
