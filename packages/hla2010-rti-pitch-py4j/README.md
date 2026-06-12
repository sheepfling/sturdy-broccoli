# hla2010-rti-pitch-py4j

Pitch Java RTI adapter through Py4J.

This package owns the `pitch-py4j` backend plugin descriptor and Pitch-specific
runtime wiring. Generic Py4J Java bridge mechanics live in
`hla2010-rti-java-py4j`.

The old `hla2010_rti_pitch_py4j.{runtime,adapter,factory}` modules remain as
package-local compatibility facades. The removed root
`hla2010.backends.py4j` modules do not remain available.
Verification and preflight policy for this backend is intentionally shared
through `hla2010_rti_pitch_common.testing_policy`.
Split-package guard coverage lives in `tests/test_rti_pitch_split_packages.py`,
and the shared real-runtime wrapper matrix lives in
`tests/vendors/test_pitch_real_backend_matrix.py`.
Import the canonical implementation from `hla2010_rti_pitch_py4j`.

The human operator surface for Pitch stays `./tools/pitch`; this package does
not add a package-local command.
