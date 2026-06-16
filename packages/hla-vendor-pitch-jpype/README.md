# hla-vendor-pitch-jpype

Pitch Java RTI adapter through JPype.

This package owns the `pitch-jpype` backend plugin descriptor and Pitch-specific
runtime wiring. Generic JPype Java bridge mechanics live in
`hla-bridge-java-jpype`.

The old `hla.vendors.pitch.jpype.{runtime,adapter,factory}` modules remain as
package-local compatibility facades. The removed root
`hla.rti1516e.backends.jpype` modules do not remain available.
Verification and preflight policy for this backend is intentionally shared
through `hla.vendors.pitch.testing_policy`.
Split-package guard coverage lives in `tests/test_rti_pitch_split_packages.py`,
and the shared real-runtime wrapper matrix lives in
`tests/vendors/test_pitch_real_backend_matrix.py`.
Import the canonical implementation from `hla.vendors.pitch.jpype`.

The human operator surface for Pitch stays `./tools/pitch`; this package does
not add a package-local command.
