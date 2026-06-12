# hla2010-fom-target-radar docs

This package owns the concrete Target/Radar example FOM, scenario helpers, and
related example-specific verification support.

Key owned surfaces:
- `hla2010_fom_target_radar.resources.foms`: packaged Target/Radar FOM assets.
- `hla2010_fom_target_radar.scenarios`: canonical Target/Radar scenario and
  factory helpers.
- package-owned example/FOM support reused by repo-internal proof and backend
  matrix layers.
- `tests/test_fom_target_radar_split_package.py`: split-package guard coverage
  for the installable Target/Radar example package.

This package does not own RTI backend implementations or generic shared
verification-harness scenarios.

If you want the package entrypoint and usage story, read
[`../README.md`](../README.md).
